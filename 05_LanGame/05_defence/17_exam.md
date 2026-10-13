# Part C — Pass the exam

# Chapter 17 — Question and answer bank

Go over the questions **after** the code works. Every answer is 2–4 sentences, at the level
expected from you. When you answer — point at the file and the line in your code. "This happens
in `game_engine.py`, in `record_answer`, the second check" is worth more than a definition.

## 17.1 The problem and the design

**1. What does the system do, in one sentence?** A multiplayer trivia game on the local network:
one server runs the game and computes scores, every player runs a client, and the fastest correct
answer wins the most points.

**2. What is an authoritative server and why did you choose it?** The server is the only one
that holds the game state and decides: who joined, which question, whose answer counts, how many
points. Clients only display and report clicks. It prevents disagreement between clients and makes
cheating by a modified client useless — the client never even receives the correct answer.

**3. Why three programs?** The server has no UI and runs once; the client runs on every player's
machine; the admin is for the teacher and touches only the database. Separate programs = separate
responsibilities, and the shared `common` package keeps them speaking the same protocol.

**4. What are the two hard parts of the project?** Networking (a byte stream with no message
boundaries, clients that disappear) and concurrency (8 threads touching one game state).

## 17.2 Networks

**5. What is an IP address and what is a port?** IP identifies a computer on the network; a port
(0–65535) identifies a program on that computer. `192.168.1.20:5050` = LanGame's server on that machine.

**6. TCP vs. UDP — and why TCP here?** TCP: connection, guaranteed and ordered delivery, a bit
slower. UDP: no connection, no guarantees, faster. Every trivia message must arrive, so TCP. Fast
action games use UDP because a late position update is worthless.

**7. What is the three-way handshake?** SYN, SYN-ACK, ACK — the client and server agree to
connect before any data. Happens inside `connect()` / `accept()`. Visible in Wireshark.

**8. What does "TCP is a stream" mean for your code?** `recv()` returns bytes with no message
boundaries: messages can arrive glued or cut. So the protocol adds a `\n` after every message and
`MessageBuffer` reassembles them.

**9. What is framing and which method did you use?** Marking message boundaries in a stream.
A delimiter (`\n`) after every JSON message. The alternative is a length prefix.

**10. Why is the newline a safe delimiter?** JSON encodes newlines inside strings as `\n` (two
characters), so a raw newline byte never appears inside a message.

**11. What happens if a client sends 1 MB of garbage?** `MessageBuffer` raises
`ProtocolError("too_large")` once `_pending` passes `MAX_MESSAGE_BYTES`; the handler replies ERROR
and (for this case) closes the connection. The server keeps running.

**12. What is latency and how do you keep scoring fair?** The travel time of a message. The server
measures response time on its own clock from broadcast to arrival, never trusting the client's
clock. On a LAN the 1–5 ms differences are negligible.

**13. Why `time.monotonic()` and not `time.time()`?** `time()` is the wall clock and can jump
(clock changes, NTP). `monotonic()` only moves forward at a steady rate — correct for durations.

**14. `0.0.0.0` vs `127.0.0.1`?** `0.0.0.0` when listening = all network interfaces.
`127.0.0.1` = this machine only; used by clients testing on the server's own computer.

**15. Why does the server print its IP addresses at start?** Players must type the server's LAN
address; `gethostbyname_ex` lists them.

**16. What blocked you from another machine, and how did you fix it?** [Usually: Windows Firewall.
An inbound rule for TCP 5050.]

## 17.3 Sockets

**17. Order of the server's socket calls?** `socket()`, `setsockopt(SO_REUSEADDR)`, `bind()`,
`listen()`, then `accept()` in a loop. `accept()` returns a new socket per client.

**18. What does `recv()` returning `b""` mean?** The peer closed the connection. Break the loop
and clean up.

**19. What does `settimeout` do and why do you use it?** Makes blocking calls raise
`socket.timeout` after N seconds. On the listening socket so Ctrl+C works; on client sockets so
threads can notice shutdown.

**20. Why `sendall` and not `send`?** `send` may write only part of the bytes and return how
many; `sendall` loops until everything is written.

**21. Why do you need a lock around `sendall` per client?** The client's own handler and the
broadcaster may send at the same time; interleaved writes corrupt both messages.

**22. Why is the payload JSON?** Text: readable in logs and Wireshark, parsers everywhere,
extensible. Size is irrelevant at our message rate.

## 17.4 Threads

**23. Why a thread per client?** `recv()` blocks; one thread waiting on player A must not delay
player B. Each thread waits on its own socket.

**24. What is a race condition? Give your example.** Two threads read-modify-write the same
variable and one update is lost. `score += 800` and `score += 500` interleaving → 500 instead of 1300.

**25. What is a lock?** A token one thread holds at a time; others wait. Code between acquire and
release runs exclusively.

**26. Why one lock for the whole engine?** A command touches several fields together; one lock
makes each command atomic. Multiple locks would need a locking order to avoid deadlock.

**27. `Lock` vs. `RLock`?** `RLock` may be re-acquired by the thread that holds it.
`record_answer` → `close_question` both lock; with a plain `Lock` that deadlocks.

**28. What is a deadlock? How could it happen here?** Threads waiting on each other forever.
E.g. holding the engine lock while `sendall` blocks on a client that is itself waiting for the
lock through its handler. Prevention: never do I/O while holding the lock.

**29. Does the GIL make `score += 800` safe?** No. The GIL serializes bytecode instructions, and
`+=` is several instructions; a switch can happen between them.

**30. Why is the timer a separate thread and what must `close_question` guarantee?**
`threading.Timer` runs its function in a new thread after the delay. `close_question` must be
idempotent (state check + `cancel()`) because the timer and the last answer may both call it.

**31. Why can't the reader thread update the Tkinter window?** Tk is single-threaded; widgets
must be touched only from the Tk thread. The reader puts messages in a `queue.Queue`; the Tk
thread polls it with `after(50)`.

**32. What is `daemon=True`?** A daemon thread dies with the main thread; without it the process
hangs on exit waiting for blocked `recv` calls.

**33. How did you test thread safety?** `test_concurrent_answers_are_all_recorded`: 8 threads
answer simultaneously; all 8 must be recorded. Plus the 8-player classroom test.

## 17.5 State machine and scoring

**34. What are the states and transitions?** LOBBY → (start) → QUESTION → (time up / all
answered) → SCORING → (more) → QUESTION or → (last) → GAME_OVER → (reset) → LOBBY.

**35. What does an ANSWER in LOBBY do?** Rejected with `not_accepting`; state unchanged.

**36. What are the checks in `record_answer`, in order?** state is QUESTION → question id is
current → choice in 0–3 → not already answered → store; close early if everyone answered.

**37. What is a stale answer?** An ANSWER for the previous question, delayed by the network or a
slow client. Rejected by the question id check.

**38. The scoring formula?** `round(1000 · (limit − t) / limit)`, minimum 100 for correct, 0 for
wrong; `t` clamped to `[0, limit]`. 3 s → 800; 7.5 s → 500.

**39. Why a minimum of 100?** A slow correct answer must still beat a wrong one.

**40. How do you avoid repeating questions?** Load all matching ids once, shuffle in Python, pop
one per round, fetch by primary key. Also avoids `ORDER BY RANDOM()` scanning the table each time.

**41. What happens to a player who disconnects mid-question?** Marked disconnected, handler
dropped, stays on the leaderboard; if everyone still connected has answered the round closes.

**42. What if the host disconnects in the lobby?** The next player becomes host
(`next(iter(players))`); a new WELCOME/LOBBY_UPDATE tells them.

## 17.6 Database

**43. Describe the schema.** `questions`; `games` 1→* `players` and `answers`; `answers` also →
`questions`. Cascade on game delete. Index on `(category, difficulty)`.

**44. Why `PRAGMA foreign_keys = ON`?** Off by default in SQLite; without it FK constraints and
CASCADE are ignored.

**45. What is a transaction and where do you rely on one?** All-or-nothing group of writes.
`save_game`: game + players + answers in one `with db.connection()`; a failure rolls back everything.

**46. How do you prevent SQL injection?** `?` placeholders always; never f-strings in SQL.

**47. Why one connection per operation?** SQLite connections are not thread-safe across threads;
opening a short-lived connection per operation avoids sharing. Cost is negligible here.

**48. What does the index on `(category, difficulty)` speed up?** `list_ids(category)` — a tree
lookup instead of scanning every row.

**49. Give a query you use for the results chapter.** Hardest questions: `AVG(is_correct)` per
question via `LEFT JOIN answers`, ordered ascending (chapter 6.6).

## 17.7 Architecture and code

**50. Which design patterns and where?** Command (`commands.py`), State machine (`GameEngine`),
MVC (client), Repository (`repositories.py`), Singleton (`Database`), Factory (`build_command`),
Producer/Consumer (`NetworkClient.inbox`).

**51. Why the Command pattern?** Parsing and rules separated; new action = new class; the executed
command list is a replay of the game.

**52. Where is the MVC boundary in the client?** Views import no socket/protocol code;
`NetworkClient` imports no tkinter; `ClientController` is the only class that knows both.

**53. What is `build_command` and what pattern is it?** Message → Command object; a Factory. It is
the only place that maps message types to classes.

**54. What is `@abstractmethod` doing on `Command.execute`?** Forbids instantiating a command
without `execute`; a missing implementation fails at creation, not at runtime.

**55. What does `Database.__new__` do?** Returns the single instance (Singleton).
`Database() is Database()` → True.

**56. What is `@contextmanager` and why here?** Turns a `yield` function into a `with` block:
commit after the body, rollback on exception, close always.

**57. What did you unit-test and why that?** Protocol (framing, malformed input), scoring
(exact numbers), the engine (state rules, concurrency) with fake handlers, repositories on a temp
DB. No sockets/GUI in tests — they are tested by hand.

**58. How would you add a "SKIP" action?** `SkipCommand` in `commands.py`, one line in
`build_command`, `MessageType.SKIP`, `engine.skip_question()` (host only, QUESTION state), a button
in the client. Nothing else changes.

**59. What would change to move from Tkinter to a web client?** Only `client/` — the protocol and
server stay. That is the point of the shared `common` package.

**60. What is in `logs/server.log` and how did it help?** Every command with thread name, state
and player; broadcast timestamps for the latency metric. [Your story.]

## 17.8 Security, limits, ethics

**61. Can a player cheat?** Not by modifying the client: the correct answer is never sent, time
is measured on the server, the server validates everything. A player could spam JOINs — rate
limiting would be future work.

**62. What is not protected?** Traffic is plain text (readable on the LAN); the DB file is
readable by anyone with access to the server machine. Future work: TLS, DB encryption.

**63. Why LAN only?** No NAT traversal / public server; a future web version would fix it.

**64. What would you improve with another month?** [Pick 2 from the proposal's future work and
say why.]

**65. What was the hardest bug and how did you find it?** [Yours — write it in `TASKS.md` when it happens.]

## 17.9 Numbers you must know from your own runs

**66.** Question-to-all-clients latency you measured. **67.** Max players tested. **68.** Number
of questions in your DB. **69.** Response time of `list_ids` for your DB size. **70.** Test count
and coverage. **71.** Points formula examples (3 s, 7.5 s, 14.9 s). **72.** Size in bytes of one
QUESTION message (from Wireshark). **73.** Number of threads in the server with 8 players.
**74.** The port and why you chose it. **75.** Lines of code per package (`wc -l`).

# Chapter 17a — "Explain your code": line-by-line drills

In the defense they will open a random file and ask "explain". Practice on **your** code — for
every section below, explain out loud every line: what it does, why it is there, and what would
happen without it.

1. **`MessageBuffer.feed`** — why `split` keeps the last piece, why the size check, why empty lines are skipped.
2. **`Message.from_wire`** — every check and its error code; why `ProtocolError` and not `ValueError`.
3. **`GameServer.serve_forever`** — the five socket calls, `SO_REUSEADDR`, the timeout, why `ClientHandler` is imported inside.
4. **`ClientHandler.run`** — the three exits, the order of `except` clauses, the `finally`.
5. **`ClientHandler.send`** — the send lock and why it returns `False` instead of raising.
6. **`GameEngine.execute`** — the lock, the reply, the log line.
7. **`GameEngine.record_answer`** — the four checks in order, `monotonic`, the early close.
8. **`GameEngine.close_question`** — idempotence, `cancel()`, the order build-then-broadcast, the next timer.
9. **`ScoreEngine.points_for`** — clamp, formula, rounding, minimum.
10. **`Database.connection`** — `yield / commit / rollback / close` and the three scenarios.
11. **`GameRepository.save_game`** — the insert order and why one transaction.
12. **`ClientController._poll_inbox`** — `get_nowait`, `queue.Empty`, `after(50)`, why not the reader thread.

💡 Record yourself explaining three of them. If you hear "basically" more than twice per
sentence, you are not sure — go back to the chapter.

# Chapter 18 — Glossary

| Term | Short explanation |
|---|---|
| ACK | Acknowledgement packet in TCP |
| Authoritative server | The server alone decides the game state |
| Blocking call | A call that waits (accept, recv) until something happens |
| Broadcast | Sending one message to every connected client |
| Client / server | The program that connects / the program that waits for connections |
| Command pattern | An action as an object with `execute()` |
| Context manager | A `with` block with setup and teardown |
| Critical section | Code that only one thread may run at a time |
| Daemon thread | A thread that dies with the main thread |
| Deadlock | Threads waiting on each other forever |
| Delimiter | A character marking the end of a message (`\n`) |
| Foreign key | A column that must match a row in another table |
| Framing | Cutting a byte stream into messages |
| FSM (state machine) | A fixed set of states and transitions |
| GIL | Python's global interpreter lock — one bytecode at a time |
| Handshake | The three packets that open a TCP connection |
| Idempotent | Safe to call more than once |
| Index (DB) | A search tree on a column |
| IP address / port | Which computer / which program |
| JSON | Text format for structured data |
| Latency | Travel time of a message |
| Lock / RLock | Mutual exclusion; RLock is re-entrant |
| Loopback (127.0.0.1) | This computer |
| MVC | Model / View / Controller separation |
| Monotonic clock | A clock that only moves forward, for durations |
| Payload | The data part of a message |
| Producer / consumer | One thread produces into a queue, another consumes |
| Protocol | The agreed set of messages and rules |
| Race condition | A bug that depends on thread timing |
| Repository | A class that hides all SQL |
| Singleton | Exactly one instance |
| Socket | The endpoint object for network I/O |
| SQL injection | Malicious input executed as SQL — prevented with `?` |
| Stream | Bytes with no message boundaries (TCP) |
| TCP / UDP | Reliable ordered stream / fast unreliable datagrams |
| Thread | A second line of execution sharing memory |
| Timer | A thread that runs a function after a delay |
| Transaction | All-or-nothing group of DB writes |
| Wireshark | A tool that records and shows network packets |
