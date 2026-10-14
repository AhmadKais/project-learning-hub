# LanGame — hints, checks and traps, stage by stage

Use this file when you are **stuck** on a function of your skeleton. For each hard function:

- **Learn it in** — the theory section, notebook and exercise that teach the idea.
- **Hints** — hidden. Open one at a time: 💡 a nudge, 🔧 the steps.
- **Check yourself** — values to compare against before you run the tests.
- **Traps** — the mistakes that make a test fail (or pass while the game is broken).

`CHECKLIST.md` (next to this file) lists **every** function you have to write. The docstrings and
`04_build/10_build_part1.md` / `14_build_part2.md` give the step-by-step; this file is for when those are not enough.

> **The working loop.** One function → run **its** test (`pytest tests/test_protocol.py -v`) → green → commit →
> next. Network bugs are hard to see, so test without sockets first (the tests do) and only then with two windows.

---

## Stage 1 — Protocol and infrastructure

**Learn it in:** theory `02_networks` §2.5 (TCP is a stream), `03_sockets_protocol` §3.3–3.4 · notebook
`01_tcp_stream_and_framing` · exercises **ex01–ex03**

### `Message.to_wire` / `from_wire`

<details><summary>🔧 Hint — <code>from_wire</code> never lets a raw exception out</summary>

```
try:
    data = json.loads(line)
except json.JSONDecodeError:
    raise ProtocolError("bad_json", "...")
if not isinstance(data, dict) or "type" not in data:   raise ProtocolError("bad_message", ...)
try:
    kind = MessageType(data["type"])                   # "DANCE" -> ValueError
except ValueError:
    raise ProtocolError("unknown_type", ...)
if not isinstance(data.get("payload"), dict):          raise ProtocolError("bad_payload", ...)
return cls(kind, data["payload"])
```
</details>

**Check yourself:** `join("liraz").to_wire()` →
`b'{"type": "JOIN", "payload": {"name": "liraz"}}\n'` — one line, ending in `\n`. With `ensure_ascii=False`, Hebrew
goes out as UTF-8 bytes, not as `ל...`.

### `MessageBuffer.feed` — framing

<details><summary>💡 Hint</summary>

`bytes.split(b"\n")` on `b'A\nB\nC'` gives `[b'A', b'B', b'C']`: every piece except the **last** is a complete
message, and the last one is either `b''` (the data ended exactly on a newline) or the start of the next message.
`*complete, self._pending = data.split(delimiter)` says exactly that in one line.
</details>

**Check yourself:** feed `join("a")` + the first 4 bytes of `join("b")` → returns `[{"name": "a"}]`, and
`_pending` is `b'{"ty'`. Feed the rest → returns `[{"name": "b"}]`.

**Traps:** decoding the bytes **before** splitting — a Hebrew letter is 2 bytes and a `recv` can cut it in half ·
forgetting the size check (`MAX_MESSAGE_BYTES`): one client that never sends `\n` would grow the buffer forever.

---

## Stage 2 — Server and lobby

**Learn it in:** theory `03_sockets_protocol` §3.1–3.2, `04_threads` §4.1–4.6 · notebooks `02_threads_and_locks`,
`04_mini_server` · exercises **ex04, ex06**

### `GameServer.serve_forever` and `ClientHandler.run`

The docstrings contain both loops line by line. The `settimeout(1.0)` is what lets `accept()` and `recv()` wake up
every second and notice that the server is shutting down.

### `GameServer.broadcast` — never send while holding the lock

<details><summary>🔧 Hint</summary>

```
with self._lock:
    targets = list(self._handlers)            # a copy, taken under the lock
for handler in targets:                        # sending happens OUTSIDE the lock
    if handler.player_name == exclude_name:
        continue
    if not handler.send(message):
        self.engine.player_left(handler.player_name)
```
</details>

### `GameEngine.execute` and the commands

Every command runs **inside** `with self._lock:` — that one lock is why eight answers arriving in the same
millisecond are all recorded (`test_concurrent_answers_are_all_recorded`, theory §4.5). A command returns an
`ERROR` message or `None`; `execute` sends the reply.

**Check yourself:** `JoinCommand` with a taken name → the second handler gets `ERROR` with code `"name_taken"` and
its `player_name` stays `None`. The first player to join becomes the host.

**Traps:** the `ERROR` codes are part of the contract — the tests check `"name_taken"`, `"not_accepting"`,
`"already_answered"`, `"bad_choice"` exactly · `close()` must be safe to call twice (it is called from `run`'s
`finally` and from `shutdown`).

---

## Stage 3 — Database and questions

**Learn it in:** theory `06_database` §6.2–6.5 · the docstring at the top of `repositories.py`

- `created_at` is `NOT NULL` — put `datetime.now().isoformat()` in every `INSERT INTO questions`.
- `difficulty` is a plain `int` (1–3) in `Question` and in the table — no conversion.
- `import_csv`: open with `encoding="utf-8-sig"` (Excel adds a BOM), collect the good rows, skip a row whose
  `correct_index` is not 0–3, and insert everything with **one** `executemany` inside **one**
  `with self.db.connection()`.
- `QuestionManager.prepare`: `random.shuffle(ids)`, keep `ids[:count]`; fewer than `count` → `ValueError` with a
  message that says how many there are.

**Check yourself:** `test_import_csv` — 3 rows in, the one with `correct_index` 9 skipped → returns 2.

---

## Stage 4 — State machine and scoring

**Learn it in:** theory `05_state_machine_scoring` §5.1–5.5, `04_threads` §4.7 (timers) · notebook
`03_game_engine` · exercises **ex05, ex07–ex10**

### `ScoreEngine.points_for`

**Check yourself** (time limit 15 s):

| answered after | points |
|---|---|
| 0 s | 1000 |
| 3 s | 800 |
| 7.5 s | 500 |
| 14.9 s | 100 (7 raised to the minimum) |
| 99 s (clamped to 15) | 100 |
| wrong, any time | 0 |

### `record_answer` — the order of the checks

`state` → `question_id` → `0 <= choice <= 3` → "already answered" → store. The order matters: an answer in the
lobby must say `not_accepting`, not `stale_question`. Store `response_time = time.monotonic() - question_sent_at`
(`monotonic`, never `time.time()`: it cannot jump when the clock is adjusted). When every **connected** player
has answered, close the question early.

### `close_question` — safe to call twice

<details><summary>🔧 Hint</summary>

The timer and the last answer can both call it. The first line decides:

```
if self.state is not GameState.QUESTION:
    return                                   # already closed - the second caller does nothing
if self._question_timer is not None:
    self._question_timer.cancel()
self.state = GameState.SCORING
...
```

The `threading.Timer` runs in its **own** thread, so `close_question` and `next_question` must take
`with self._lock:` themselves. The lock is an `RLock`, so taking it again inside `execute` is fine.
</details>

### `build_leaderboard`

`sorted(players.values(), key=lambda p: (-p.score, p.name))` — minus for "highest score first", the name as a
stable tie-break; then number from 1. **Check yourself:** scores a 300, b 900, c 300 → `1 b, 2 a, 3 c`.

**Traps:** `public_payload` must not contain `correct_index` — a modified client could read it · a player who did
not answer gets no `AnswerRecord` and 0 points, and stays on the leaderboard.

---

## Stage 5 — Graphical client

**Learn it in:** theory `04_threads` §4.8 (threads and Tkinter: the queue)

The reader thread only ever does `self.inbox.put(message)`. `_poll_inbox` — on the Tkinter thread — drains the queue
with `get_nowait()` and re-schedules itself with `root.after(POLL_MS, ...)` (`POLL_MS = 50` is defined at the top of `client_controller.py`) **every** time. The docstring
explains why each of the three details matters.

**Check yourself:** run `python run_server.py` and two clients (`python run_client.py`) on one computer with host
`127.0.0.1`. Two names → the lobby lists both → the host starts → both see the same question and the same countdown.

**Traps:** touching a widget from the reader thread (random crashes, frozen windows) · `connect` with no timeout
hangs for a minute on a wrong IP — `settimeout(5)` for the connect, then `settimeout(None)` for the reader.

---

## Stage 6 — Admin tool and persistence

`save_game`: **one** `with self.db.connection()` block — insert the game, then each player (remember
`name → player_id` from `cur.lastrowid`), then the answers with `executemany`. If any insert fails, the whole game
is rolled back. `list_recent`: `LEFT JOIN players` + `GROUP BY g.id` + `COUNT(p.id) AS player_count`, then
`dict(row)`.

---

## Stage 7 — Load test, network analysis, documentation

- Load test: a script that opens 8 sockets, joins with 8 names and answers every question at once. Every answer must
  be in the database afterwards — that is the lock working.
- Wireshark (theory §3.5): filter `tcp.port == 5050`, find one `ANSWER` line in the bytes, and screenshot the
  three-way handshake for the book.

---

## When nothing works

| Symptom | Likely cause |
|---|---|
| `OSError: [Errno 98] Address already in use` | `SO_REUSEADDR` missing, or an old server still running |
| the client connects, then nothing happens | `_poll_inbox` does not re-schedule itself, or the server never sends `WELCOME` |
| two messages arrive as one / one arrives in two | that is TCP — your `MessageBuffer` must handle both (stage 1 tests) |
| the window freezes | a blocking call (`recv`, `queue.get()`, `time.sleep`) in the Tkinter thread |
| the game hangs after a question | `close_question` returned early, or the `Timer` for `next_question` was never started |
| another computer cannot connect | Windows firewall — allow Python on *private* networks; use the address `run_server.py` prints, not 127.0.0.1 |
| `sqlite3.ProgrammingError: ... created in a thread` | `check_same_thread=False` missing in `get_connection` |
