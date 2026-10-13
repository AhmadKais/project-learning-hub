# Appendix — Answers to "Check yourself"

For the supervisor: the questions require calculation or reasoning, not memorization. A student
who answers 80% of them correctly understands what he is building. For the student: do not peek
before you tried.

## Chapter 2

1. Another machine: `192.168.1.20`. The same machine: `127.0.0.1` (the LAN address works too).
   `0.0.0.0` is never typed by a client — it only means "all interfaces" when listening.
2. (a) recv 1 = `{"a":1}\n{"b":2}\n` → buffer returns [a, b]; recv 2 = (nothing yet).
   (b) recv 1 = `{"a":1}\n{"b"` → [a], pending `{"b"`; recv 2 = `:2}\n` → [b].
   (c) recv 1 = `{"a"` → []; recv 2 = `:1}\n{"b":2}\n` → [a, b]. In every case the buffer returns
   the same two messages — that is the whole point of `MessageBuffer`.
3. Commas appear *inside* JSON (`{"a":1,"b":2}`), so the receiver could not tell an internal comma
   from a message boundary. A raw newline byte never appears inside JSON (it is escaped as `\n`),
   so it is unambiguous.
4. The question reaches A after ~2 ms and B after ~40 ms; the answers travel back 2 ms and 40 ms.
   The server measures ≈ 3.004 s for A and ≈ 3.080 s for B. Not perfectly fair: B loses about
   80 ms ≈ 5 points (1000·0.08/15). Perfect fairness would need the server to estimate each
   client's round-trip time (a ping/pong message at join) and subtract it — but the estimate must
   be made by the server, never reported by the client. On a LAN the difference is negligible, and
   that is the honest thing to write in the book.
5. Trivia: every answer must arrive and be counted — reliability. Racing: only the newest position
   matters; a resent old packet is useless, so low latency beats reliability.

## Chapter 3

1. `socket` → `bind` → `listen` → `accept` → `recv`. `accept` returns the per-client socket
   (`conn`); `recv` is called on that, never on the listening socket.
2. The peer closed the connection (a proper close, not an error). The loop must `break`, and the
   handler must clean up (`close()` → engine learns the player left). Continuing to call `recv`
   returns `b""` forever and burns CPU.
3. A modified client could display the correct option and auto-answer in 1 ms — 1000 points every
   round. Never send the answer until the round is closed (RESULT).
4. `GameEngine`. `from_wire` only knows the *shape* of a message — an ANSWER is a perfectly
   well-formed message. Whether it is *legal now* depends on the game state, which only the engine
   knows. Shape checks in the protocol, rule checks in the engine.
5. `b'{"type": "LEAVE", "payload": {}}\n'` (JSON key order/spaces may differ; the trailing `\n` is required).
6. A TCP ACK: the client's operating system confirming it received the QUESTION bytes. It carries
   no data and your code never sees it — TCP handles it. In Wireshark it shows as `[ACK]`.

## Chapter 4

1. Between 2 and 2000. 2000 if no interleaving happens; as low as 2 in the worst pathological
   interleaving (each thread's reads overwrite the other's work). In practice you will see numbers
   like 1,400–1,900 — random, which is the signature of a race.
2. `with` releases the lock even when an exception is raised inside. With manual
   `acquire()/release()`, an exception between them (e.g. a `KeyError` on a missing player) skips
   `release()`; the lock stays taken; every other thread blocks forever — a deadlock caused by a
   typo somewhere else.
3. `Lock`: `close_question` tries to acquire a lock its own thread already holds → waits for itself
   forever → the server freezes. `RLock`: the same thread may re-acquire; it keeps a count and
   releases when the count returns to zero → works.
4. The lock is held for 3 s. During that time no handler can execute any command (all wait for the
   lock), the timer's `close_question` waits too, and every answer that arrives is recorded 3 s
   late — worse response times for everyone, possibly rejected as late. One slow Wi-Fi client
   punishes the whole room. Fix: build the payload under the lock, release, then send.
5. The second call must return immediately without scoring again or broadcasting twice. The first
   line `if self.state != GameState.QUESTION: return` guarantees it (the first call already moved
   the state to SCORING), and `self._question_timer.cancel()` in the early-close path prevents the
   timer from even firing.
6. A widget is updated from the reader thread → Tkinter is not thread-safe → random crashes
   (`main thread is not in main loop`) or a frozen window. Fix: the reader only does
   `inbox.put(message)`; the controller's `_poll_inbox`, running in the Tk thread via `after(50)`,
   calls `show`.

## Chapter 5

1. 6.0 s → 1000·9/15 = **600**. 12.0 s → 1000·3/15 = **200**. 15.0 s → 1000·0/15 = 0 → raised to **100**.
2. Still **LOBBY**. The host receives `ERROR` (e.g. `not_enough_players`) and nothing else changes;
   the other side of the same rule is `MIN_PLAYERS` in `config.py`.
3. C's `Player.connected = False`, C's handler removed from the engine and the server. Other players
   see nothing immediately (in-game there is no LOBBY_UPDATE; C simply shows "no answer" in the
   next RESULT and stays on the leaderboard). The round closes early only if every *still connected*
   player has already answered — `player_left` must check that, or the round waits the full limit.
4. LOBBY —JOIN→ LOBBY —JOIN→ LOBBY —START_GAME→ (COUNTDOWN) → QUESTION 1 —close→ SCORING —timer→
   QUESTION 2 —close→ SCORING —last→ GAME_OVER —reset→ LOBBY.
5. `sleep(15)` would block the thread that called `next_question` — a handler or timer thread — and
   if it holds the engine lock, the *whole engine* for 15 s: no answers recorded, nothing. A `Timer`
   returns immediately and fires `close_question` in its own thread; meanwhile handlers record
   answers normally.
6. Raise `ValueError("need 10 questions in 'networks', have 6")` inside `prepare()`, which
   `start_game` turns into an ERROR to the host — the host can pick another category or fewer
   questions, before anyone has scored. Discovering it at question 7 would abort a game in progress
   with scores already earned and nothing to save.

## Chapter 6

1. Its `players` and `answers` rows are deleted automatically. Two conditions: `ON DELETE CASCADE`
   in the schema **and** `PRAGMA foreign_keys = ON` executed on the connection doing the delete.
2. **Zero.** All inserts ran inside one transaction; the exception triggers `rollback()` in
   `connection()`. No game row, no players, no answers.
3. With `?`: the whole string is a category value; no such category exists; the query returns
   nothing. Without: the SQL becomes `... WHERE category = 'networks'; DROP TABLE questions; --'`
   and the table is gone.
4. `list_ids` returns a few thousand integers — a few KB — enough to shuffle and pick. `list_all`
   would load every question's text and options, most of which are never used in this game. Then
   each round fetches one row by primary key — the cheapest query there is.
5. `SELECT winner_name, COUNT(*) AS wins FROM games WHERE winner_name IS NOT NULL GROUP BY winner_name ORDER BY wins DESC;`
6. Any path that bypasses your Python validation: someone editing the file in DB Browser, a bug in
   a future import script, a new tool. The constraint lives in the database, so it holds no matter
   which program writes.

## Chapter 7

1. Yes — the view now knows about networking. The information should arrive as data: the
   controller (or the server's WELCOME payload, which can echo the client's address) hands the
   view a string to display. Views display; they do not discover.
2. `build_command` raises `ProtocolError("unexpected_type")` — a client may not send server-only
   types. Decided in the factory, because it is the single place that knows which types map to
   which commands; the handler turns the exception into an ERROR reply.
3. The handler stays "dumb" (bytes → object), the rules stay in the engine, and every command runs
   under the engine lock in exactly one way (`execute`). Concrete benefits: tests drive the engine
   with `FakeHandler` and no sockets; the executed-command log is a replay of the game; adding an
   action does not touch the handler.
4. `True` — `Database` is a Singleton. `False` — `QuestionRepository` is an ordinary class; each
   call creates a new object (both wrap the same `Database`).
5. `commands.py` (a `SkipCommand` + one line in `build_command`), `protocol.py`
   (`MessageType.SKIP`), `game_engine.py` (`skip_question`: host only, QUESTION state → close the
   round with no scoring), the client controller (`on_skip`) and one button in `QuestionView`.
   **Not**: `client_handler.py`, `game_server.py`, the database, `MessageBuffer`.
6. The controller updates Tkinter widgets, and only the Tk thread may do that. The queue moves the
   message from the reader thread to the Tk thread, which takes it in `_poll_inbox` via `after()`.
   Calling the controller directly from the reader would update widgets from the wrong thread.
