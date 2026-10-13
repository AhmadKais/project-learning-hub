# Part B — Build the code

The next chapters follow `TASKS.md`. For every stage: what to write, the pieces worth knowing,
and how to check. The skeleton code already has, in every function, the list of steps — here is
the **why**, and the details that are easy to trip on.

Working rule: open the file, read the docstring, write, run the stage's test, and only then
continue. Do not write five files and then run.

# Chapter 10 — Stage 1: the protocol

## 10.1 `Message.to_wire` / `Message.from_wire`

- `to_wire`: `json.dumps({...}, ensure_ascii=False) + "\n"`, then `.encode("utf-8")`. Without
  `ensure_ascii=False`, Hebrew becomes `מ...` — still correct, but unreadable in Wireshark and logs.
- `from_wire`: wrap `json.loads` in `try/except json.JSONDecodeError` → `ProtocolError("bad_json")`.
  Then check `isinstance(data, dict)`, `"type" in data`, `data["type"] in MessageType.__members__`,
  `isinstance(data.get("payload"), dict)`. Each failure → its own code. Never let a `KeyError` or
  `ValueError` escape — the handler only catches `ProtocolError`.

💡 `MessageType("DANCE")` raises `ValueError`, not `ProtocolError`. Catch it, or check membership first.

## 10.2 `MessageBuffer.feed`

📄 **The split, exactly**
```python
self._pending += chunk
if len(self._pending) > config.MAX_MESSAGE_BYTES:
    raise ProtocolError("too_large", "message exceeds limit")
*complete, self._pending = self._pending.split(b"\n")   # the LAST piece is always incomplete
return [Message.from_wire(line.decode("utf-8")) for line in complete if line.strip()]
```

Why the last piece is "always incomplete": if the chunk ended exactly with `\n`, the last piece is
`b""` — an empty, incomplete message — which is correct. If it ended mid-message, the last piece is
the start of the next message — also correct. `split` does the right thing in both cases.

## 10.3 The throw-away echo test

Write two 15-line scripts (not in the project): a server that accepts one connection and prints
every message it gets through a `MessageBuffer`, and a client that sends `join("test")` twice
without a pause. Run them on one machine. You will very likely see both messages arrive in one
`recv()` — your first "glued" case, live.

**Exit condition:** `pytest tests/test_protocol.py -v` green.

# Chapter 11 — Stage 2: server and lobby

## 11.1 `GameServer.serve_forever`

- `SO_REUSEADDR` before `bind` — otherwise, after Ctrl+C, the port stays "in use" for a minute and
  the next start fails.
- `settimeout(1.0)` on the listening socket — `accept()` then raises `socket.timeout` every second,
  which lets the loop check `self._running`. Without it, Ctrl+C is ignored until the next client connects.
- After `accept`, the new `conn` has **no** timeout of its own until `ClientHandler.run` sets one.

## 11.2 `ClientHandler.run`

The loop from the docstring. Three exits: `recv` returns `b""` (client closed), `OSError`
(connection reset), or `_alive` becomes False (shutdown). All three end in `finally: self.close()`
so the engine always hears that the player left — even if the client's laptop was closed mid-game.

💡 `except socket.timeout: continue` must come **before** `except OSError`, because `socket.timeout`
is a subclass of `OSError`. In the wrong order every timeout kills the thread.

## 11.3 `send` and the send lock

Two threads can send to the same client at once: its own handler (an ERROR reply) and the broadcaster
(a LOBBY_UPDATE). Two `sendall` calls interleaving = two JSON strings mixed byte by byte = garbage.
`_send_lock` around `sendall` prevents it. Return `False` on `OSError` — the broadcaster iterates
over everyone and must not stop at one dead client.

## 11.4 `JoinCommand` and `GameEngine.add_player`

Validation order: state is LOBBY → name is a non-empty string ≤ 16 chars → name not taken →
fewer than MAX_PLAYERS. Each failure returns `error(code, message)` and changes nothing. On success:
create `Player`, store handler, set `handler.player_name` (this is how the handler learns its
name — before that it is anonymous), first player becomes host, send WELCOME to *this* handler,
broadcast LOBBY_UPDATE to *everyone*.

## 11.5 `player_left`

Must be safe with `name is None` (a client that connected and closed without joining) and safe to
call twice (`close()` is idempotent and `LeaveCommand` may also run). In LOBBY remove the player
and re-pick the host (`next(iter(players))`); in-game just mark `connected = False`. Then, if in
QUESTION and every *connected* player has answered → `close_question()` — otherwise the round
would wait the full time limit for a player who is gone.

**Exit condition:** three terminal clients get the same LOBBY_UPDATE; kill one, the other two get an
updated list; send `hello\n` from one, it gets `ERROR bad_json` and stays connected.

# Chapter 12 — Stage 3: database and questions

## 12.1 `Database` methods

The code is in chapter 6.3. `check_same_thread=False` in `sqlite3.connect`. `row_factory = sqlite3.Row`
so you can write `row["text"]`.

## 12.2 `QuestionRepository`

- `add`: `INSERT ... VALUES (?,?,?,?,?,?,?,?,?)` with `datetime.now().isoformat()`; return `cursor.lastrowid`.
- `get`: map the row to `Question(id, text, [option_a, option_b, option_c, option_d], correct_index, category, difficulty)`.
  Write the row→Question mapping once (`_row_to_question`) — `list_all` needs it too.
- `list_ids`: build the SQL in two branches (with/without `WHERE category = ?`); return `[row["id"] for row in ...]`.
- `import_csv`: `csv.DictReader` with `encoding="utf-8-sig"` (Excel adds a BOM); validate
  `0 <= int(correct_index) <= 3`, collect valid rows, one `executemany` inside one transaction; return the count.

## 12.3 `Question.public_payload` and `QuestionManager`

`public_payload` returns exactly `{"question_id", "text", "options"}`. The test
`test_public_payload_never_leaks_the_answer` exists because this is the one place a careless
`asdict(question)` would leak the answer to every client.

`prepare(count)`: `ids = self.repository.list_ids(self.category)`; if `len(ids) < count` raise
`ValueError(f"need {count} questions in '{category}', have {len(ids)}")`; `random.shuffle(ids)`;
`self._queue = ids[:count]`. `next()`: `self.repository.get(self._queue.pop(0))`.

**Exit condition:** the stage-3 tests green; a tiny script imports `data/questions_seed.csv` and
prints `count()` = 25.

# Chapter 13 — Stage 4: the state machine and scoring

## 13.1 `ScoreEngine`

`points_for`: clamp, then the formula from chapter 5.4 with `round()`, then `max(MIN_POINTS_CORRECT, ...)`
for correct answers, `0` for wrong. `score_round`: for each record, `is_correct = chosen_index == question.correct_index`,
`points = points_for(...)`, `players[name].score += points`.

## 13.2 `build_leaderboard`

`sorted(players.values(), key=lambda p: (-p.score, p.name))`, then `enumerate(..., start=1)`.

## 13.3 `record_answer` — the checks, in order

1. `state != QUESTION` → `not_accepting`
2. `question_id != current_question.id` → `stale_question` (an answer to the previous question,
   delayed by the network)
3. `choice not in (0, 1, 2, 3)` → `bad_choice` (also catches non-integers — check `isinstance(choice, int)` first)
4. `name in self.answers` → `already_answered`
5. store `AnswerRecord(name, question_id, choice, time.monotonic() - self.question_sent_at)`
6. if `len(answers) >= number of connected players` → `close_question()`

Return `None` on success, `error(...)` otherwise. The engine's `execute` sends the reply.

## 13.4 `close_question` and the timers

```python
if self.state != GameState.QUESTION: return          # idempotent
if self._question_timer: self._question_timer.cancel()
self.state = GameState.SCORING
self.scores.score_round(...); self.history.extend(self.answers.values())
result, board = self.result_payload(), self.leaderboard_payload()   # build under the lock
self.server.broadcast(Message(MessageType.RESULT, result))          # (release the lock first if you can)
self.server.broadcast(Message(MessageType.LEADERBOARD, board))
threading.Timer(config.SECONDS_BETWEEN_QUESTIONS, self.next_question).start()
```

💡 `next_question` runs in the timer's thread — so it must take the lock like everything else.
The simplest way: make every public method start with `with self._lock:` and never think about
who called it.

**Exit condition:** all of `tests/test_score_engine.py` and `tests/test_game_engine.py` green,
including the 8-thread test; a full game with terminal clients.
