# Lesson 32 — Threads, race conditions and locks

> **For:** Liraz (LanGame — server and client) · Ryan (the camera thread, Lesson 26) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 31 &nbsp;·&nbsp; **After this:** Lesson 33

**In one sentence:** when several threads change the same data, their read–change–write steps can interleave and lose
work; a lock lets only one thread at a time into that critical section — use one lock, with `with`, and hold it briefly.

## 🗺️ The map of this lesson

```mermaid
flowchart LR
    A["1 · why threads"] --> B["2 · the race:<br/>read–add–write"]
    B --> C["3 · see it live"]
    C --> D["4 · the lock"]
    D --> E["5 · deadlock:<br/>one lock only"]
    E --> F["6 · hold it briefly"]
    F --> G["7 · threads &<br/>the window"]
```

## The story

> A small shop has **one notebook** with the day's total, and **two cashiers**. Cashier A sells for 800 ₪: she reads the
> total (0), takes out her calculator… Meanwhile cashier B sells for 500 ₪: she reads the total — still 0 — adds 500, writes
> **500**. Then A finishes: 0 + 800 = 800, and writes **800** over it. The evening total says 800. **500 ₪ disappeared**, and
> nobody did anything wrong individually. Liraz's game server has exactly this problem: one thread per player, all updating
> the same scores. This lesson shows the bug happening for real, and the fix: **only one cashier may hold the pen at a
> time** — a lock.

### 🌍 Real world

![races, locks and deadlocks outside computers](figs/locks_world.png)

Real railways solved this a century ago: on a single track, only the train driver **holding the token** may enter, so two
trains can never meet head-on. Online ticket shops must lock the last seat while someone pays, or two people buy it.

## Words you need

| word | meaning | shop |
|---|---|---|
| **thread** | a part of the program that runs at the same time as other parts | a cashier |
| **shared data** | a variable several threads read and write | the notebook |
| **race condition** | the result depends on which thread happens to be faster | the lost 500 ₪ |
| **lock (mutex)** | a token; only the thread holding it may enter | the one pen |
| **critical section** | the code that must be done by one thread at a time | read–add–write the total |
| **deadlock** | two threads each wait for something the other holds — forever | |
| **GIL** | Python runs one bytecode instruction at a time — but a switch can happen *between* instructions | |

---

## 1. Why threads at all

`conn.recv()` **waits** until bytes arrive (Lesson 31). With one loop for 4 players, the server would sit waiting for player 1
while player 2's answer piles up. So: **one thread per player** (`ClientHandler`), plus the thread that accepts new players,
plus **timer** threads that close a question after 15 seconds. They all share **one** game state — fast and convenient, and
dangerous.

![LanGame's threads in time](figs/thread_lanes.png)

## 2. The race condition, step by step

![race animation](figs/race.gif)

`score += 800` looks like one step, but the computer does **three**: **read** the value, **add**, **write** it back. If thread
B reads between A's read and A's write, A's work is overwritten:

```mermaid
sequenceDiagram
    participant A as thread A (+800)
    participant S as score
    participant B as thread B (+500)
    A->>S: read → 0
    B->>S: read → 0
    Note over A: 0 + 800 = 800
    Note over B: 0 + 500 = 500
    A->>S: write 800
    B->>S: write 500  ✗ A's 800 is lost
```

```
time   thread A                        thread B                          score
t1     read score → 0                                                      0
t2                                     read score → 0                      0
t3     add 800 → 800                                                       0
t4                                     add 500 → 500                       0
t5     write score = 800                                                 800
t6                                     write score = 500                 500   ← A's 800 is LOST
should be 1300
```

Python's GIL doesn't help: it runs one tiny instruction at a time, and `+=` is several instructions.

## 3. See it happen for real

```bash
cd lessons/32_threads_locks
python race_demo.py          # 4 threads × 10,000 points without a lock → many points lost
python race_demo.py --lock   # 40,000 every time
```

![race measured](figs/race_measured.png)

When the bad timing is **rare**, the bug is rare: your tests pass, and it shows up in front of the class. That's the worst
kind of bug. With the lock: **0 lost, always**.

## 4. The lock

```python
with self._lock:                      # take the pen (wait if another thread has it)
    player.score += points            # critical section: one thread at a time
                                      # the pen is released here — even if an error happened
```

With the lock, the same story:

```mermaid
sequenceDiagram
    participant A as thread A (+800)
    participant L as lock
    participant S as score
    participant B as thread B (+500)
    A->>L: take
    B->>L: take → must WAIT
    A->>S: read 0, write 800
    A->>L: release
    L-->>B: now yours
    B->>S: read 800, write 1300 ✓
    B->>L: release
```


```
t1  A takes the lock            t2  B tries → must WAIT
t3  A: read 0, add 800, write 800    t4  A releases the lock
t5  B takes the lock            t6  B: read 800, add 500, write 1300  ✓
```

Always use `with`: if you call `acquire()` and an error happens before `release()`, the lock is never released and every
other thread waits forever.

## 5. Deadlock — and LanGame's simple rule

![deadlock](figs/deadlock.png)

With **two** locks: thread A holds lock 1 and waits for lock 2; thread B holds lock 2 and waits for lock 1. Both wait forever —
the game freezes, no error message. LanGame uses **one lock** around the whole game state: nothing to get in the wrong
order.

## 6. Hold the lock briefly

![hold the lock briefly](figs/hold_short.png)

Sending a message to 10 players takes time (the network). If a thread does that **while holding the lock**, every other
thread waits. Do the update and **copy** what must be sent while holding the lock; release it; then send.

## 7. Threads and the window (Tkinter)

![thread + queue + Tkinter](figs/tk_queue.png)

Tkinter allows only its **main thread** to touch the window. The client's network thread puts incoming messages into a
`queue.Queue` (safe for threads); the window checks the queue every 50 ms with `root.after(50, poll)`. (The same idea as
Ryan's camera thread, Lesson 26.)

**SQLite and threads:** a database connection may only be used by the thread that created it → `Database.get_connection()`
gives each thread its own (Lesson 33).

## 🧪 Worked example: the race and the fix in 20 lines

```python
import threading, time

score = 0
lock = threading.Lock()

def add_points(n, use_lock):
    global score
    for _ in range(n):
        if use_lock:
            with lock:
                current = score
                time.sleep(0)            # invite a thread switch exactly in the dangerous place
                score = current + 1
        else:
            current = score              # read
            time.sleep(0)                # another thread may run here
            score = current + 1          # write - may overwrite someone else's work

for use_lock in (False, True):
    score = 0
    threads = [threading.Thread(target=add_points, args=(2_000, use_lock)) for _ in range(4)]
    for t in threads: t.start()
    for t in threads: t.join()
    print(f"lock={use_lock}: score {score:,} of 8,000")
```

Expect a large loss without the lock, and exactly 8,000 with it.

## 8. Common mistakes

| student says | the truth |
|---|---|
| "Python has the GIL, I don't need locks" | The GIL protects single instructions, not your read–add–write. |
| "The tests pass, so there's no race" | Races depend on timing — they hide from tests. Reason about them; run the demo. |
| "More locks = safer" | More locks = deadlock risk. One lock, held briefly. |
| "Send the broadcast inside the lock, to be safe" | Every other thread then waits for the network. Copy inside, send outside. |

## 📝 Summary

> * Threads let the server **wait** for many players at once; they **share** the game state.
> * `x += 1` is **read, add, write**; two threads can interleave → **lost updates** (a race), rare and hidden from tests.
> * A **lock** makes the **critical section** one-at-a-time; always `with lock:`.
> * Two locks taken in different orders → **deadlock**. LanGame: **one** lock, held **briefly** (copy inside, send outside).
> * Only Tkinter's main thread touches the window: other threads → `queue.Queue` → `root.after(50, poll)`.

## 9. Activities

1. **Two cashiers (10 min).** Two students both add their number to a total on the board: read it, walk to the calculator,
   come back, write. Start them together → a lost update. Then give the class **one** marker as the lock.
2. **Run both demos** and change `THREADS`, `ADDS`.
3. **Find the critical sections (10 min).** In `GameEngine`, list every method that touches `players` or `state` — each must
   be inside `with self._lock:`.

## 10. Do it yourself

<details><summary>1. Score 0. A adds 300, B adds 200, without a lock. Which final scores are possible?</summary>

**500** (no overlap), **300** (B's write lost), **200** (A's write lost).
</details>

<details><summary>2. Why is `with lock:` better than `lock.acquire()` … `lock.release()`?</summary>

If an error happens in between, `release()` never runs → deadlock. `with` always releases.
</details>

<details><summary>3. The timer thread closes the question while a player's thread records an answer. What keeps it correct?</summary>

Both change the state under the same lock, so one finishes before the other starts; and inside the lock the state check
(`state == QUESTION`, Lesson 30) decides whether the answer still counts.
</details>

## 11. In your project

| Project | Where |
|---|---|
| LanGame | `langame/server/game_engine.py` (one `self._lock`) · `server/client_handler.py` (one thread per player) · `server/game_server.py` → `serve_forever`, `broadcast` · `client/network_client.py` → `_reader_loop` · `client/controllers/client_controller.py` → `_poll_inbox` · `database/db.py` → `get_connection` · theory `05_LanGame/01_theory/04_threads.md` · notebook `02_threads_and_locks.ipynb` |
| FaceEmotion | `app/vision/camera.py` (Lock + copy) |

## 🎬 Watch & explore

* *Race conditions and mutexes* — [search on YouTube](https://www.youtube.com/results?search_query=race+condition+mutex+lock+explained)
* At home: `python race_demo.py` and `python race_demo.py --lock` in this folder.
* *The Deadlock Empire* — [deadlockempire.github.io](https://deadlockempire.github.io/) (a game: you are the scheduler)
* Python docs — [`threading.Lock`](https://docs.python.org/3/library/threading.html#lock-objects) · [`queue`](https://docs.python.org/3/library/queue.html)
