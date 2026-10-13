# Chapter 4 — Threads, locks and race conditions

## 4.1 What a thread is

A **thread** is a second line of execution inside the same program. Two threads run "at the same
time" and share the same memory (the same variables, the same objects). Starting one in Python:

📄 **Starting a thread**
```python
t = threading.Thread(target=handler.run, daemon=True, name="client-192.168.1.5")
t.start()          # from now on handler.run() runs alongside the main thread
```

`daemon=True` means: when the main thread ends, this thread is killed too. Without it, closing the
server would hang until every client thread ends by itself.

## 4.2 The threads in LanGame

| Program | Thread | What it does | Blocks on |
|---|---|---|---|
| Server | main | `accept()` loop | new connections |
| Server | one per client (`ClientHandler`) | `recv()` loop → commands | that client's socket |
| Server | timer (`threading.Timer`) | closes a question when time is up | a sleep |
| Client | main (Tkinter) | draws the window, handles clicks | the event loop |
| Client | reader (`NetworkClient`) | `recv()` loop → puts messages in a queue | the socket |

So the server with 8 players has 10 threads, and any two of them may run at the same moment.

## 4.3 The race condition — with a concrete example

Shared memory is convenient and dangerous. Two client threads both execute
`players["liraz"].score += 800` — which is really three steps: read, add, write.

📄 **Two threads, one variable, no lock**
```text
score = 0

time   thread A (player A's handler)          thread B (player B's handler)
t1     read  score        -> 0
t2                                            read  score        -> 0
t3     add 800            -> 800
t4                                            add 500            -> 500
t5     write score = 800
t6                                            write score = 500     <- A's 800 is LOST

final: score = 500   (should be 1300)
```

This is a **race condition**: the result depends on the exact timing of the threads. It happens
rarely — maybe once in a thousand games — which makes it the worst kind of bug: your tests pass,
and it fails in the classroom.

💡 Python's GIL (Global Interpreter Lock) does **not** protect you here. The GIL only guarantees
that one *bytecode instruction* runs at a time. `score += 800` is several instructions, and a
thread switch can happen between any two of them.

## 4.4 The lock

A **lock** (mutex) is a token only one thread can hold. A thread that wants the token while another
holds it — waits. Everything between "take the lock" and "release the lock" is a **critical
section**: only one thread is inside it at any moment.

📄 **The same example with a lock**
```python
with self._lock:                       # take the lock (wait if someone has it)
    players["liraz"].score += 800      # critical section
                                       # lock released automatically here
```

```text
t1     A: take lock
t2                                            B: try to take lock -> WAIT
t3     A: read 0, add 800, write 800
t4     A: release lock
t5                                            B: take lock
t6                                            B: read 800, add 500, write 1300   <- correct
```

The `with` statement is the right way: the lock is released even if an exception happens inside.
Forgetting to release a lock = every other thread waits forever (a **deadlock**).

## 4.5 One lock for the whole game state

`GameEngine` has **one** lock, and every public method takes it first. Why one and not one per
variable? Because an answer touches several things at once — the answer dict, the state, maybe
the score — and they must change *together*. With one lock, "execute a command" is atomic: it
either fully happens or has not started yet, from any other thread's point of view.

We use an `RLock` (re-entrant lock): the same thread may take it again while already holding it.
`record_answer()` holds the lock and may call `close_question()`, which takes the lock again. With
a plain `Lock` that would deadlock against itself.

📄 **The rule in one line**
```text
Any code that reads or writes engine state runs inside `with self._lock:` — no exceptions.
```

`tests/test_game_engine.py::test_concurrent_answers_are_all_recorded` starts 8 threads that answer
at the same instant. Without the lock it fails sometimes; with it, always passes.

## 4.6 Do not hold the lock while doing slow things

Sending to a socket can take a while (a slow Wi-Fi client). If `broadcast()` held the engine lock
while sending to 8 clients, a slow client would freeze the whole game for everyone. The pattern:

📄 **Copy under the lock, work outside it**
```python
with self._handlers_lock:
    targets = list(self._handlers)      # fast: just copy the list
for handler in targets:                 # slow: network I/O, no lock held
    handler.send(message)
```

Same idea in the engine: compute the payload under the lock, release, then broadcast.

## 4.7 Timers

`threading.Timer(15.0, self.close_question)` runs `close_question` after 15 seconds — in a new
thread. So `close_question` can be entered from the timer thread **and** from a handler thread
(when the last player answers early). Two rules follow:

- it takes the lock like everything else;
- it must be **idempotent** — safe to call twice. Check `if self.state != QUESTION: return` first,
  and `timer.cancel()` when closing early.

## 4.8 Threads and Tkinter: the queue

On the client there are two threads: the reader (socket) and Tkinter (window). **Tkinter widgets
may be touched only from the Tkinter thread.** If the reader thread calls `label.config(...)`, you
get crashes or a frozen window — sometimes.

The safe pattern is **producer/consumer with a queue**: the reader thread *puts* decoded messages
into a `queue.Queue` (thread-safe by design), and the Tkinter thread *takes* them every 50 ms with
`root.after(50, poll)`. The reader never touches the window; the window never touches the socket.

📄 **The client's polling loop**
```python
def _poll_inbox(self):
    while True:
        try:
            message = self.net.inbox.get_nowait()
        except queue.Empty:
            break
        self.handle_message(message)          # updates widgets - we ARE the Tk thread here
    self.root.after(50, self._poll_inbox)
```

## ✅ Check yourself — Chapter 4

1. Two threads each run `counter += 1` 1,000 times, no lock. What is the range of possible final
   values? (Smallest and largest.)
2. Why is `with lock:` better than `lock.acquire()` ... `lock.release()`? Describe a case where the
   second form leaves the lock taken forever.
3. `record_answer` (holding the lock) calls `close_question` (which takes the lock). With
   `threading.Lock` — what happens? With `threading.RLock`?
4. `broadcast()` holds the engine lock while calling `sendall()` to every client. Client 5 is on
   bad Wi-Fi and `sendall` takes 3 seconds. Describe what every other player experiences.
5. The question timer fires at the same moment the last player answers. Both call
   `close_question`. Write what the second call must do and which line guarantees it.
6. The client's reader thread calls `self.view.question.show(payload)` directly. What is wrong,
   and what is the fix?

## 📚 Further reading — Chapter 4

- **Python docs — threading**: https://docs.python.org/3/library/threading.html — `Thread`, `Lock`, `RLock`, `Timer`.
- **Real Python — An Intro to Threading in Python**: https://realpython.com/intro-to-python-threading/ —
  race conditions with a runnable example; read "Race Conditions" and "Basic Synchronization Using Lock".
- **Real Python — What Is the Python GIL?**: https://realpython.com/python-gil/
- **Python docs — queue**: https://docs.python.org/3/library/queue.html
- **TkDocs — The Event Loop** (why `after`, never `sleep`): https://tkdocs.com/tutorial/eventloop.html
