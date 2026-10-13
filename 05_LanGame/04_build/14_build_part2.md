# Chapter 14 — Stage 5: the graphical client

## 14.1 `NetworkClient`

`connect`: `settimeout(5)` for the connect itself (a wrong IP otherwise hangs for a minute),
then `settimeout(None)` — the reader may block forever, that is fine for a daemon thread.
`_reader_loop`: same shape as `ClientHandler.run`, but every message goes to `self.inbox.put(m)`.
On exit, put `error("disconnected", "connection lost")` so the controller can show a message and
return to the connect screen.

## 14.2 `ClientController`

- `handle_message`: a dict `{MessageType.WELCOME: self._on_welcome, ...}` is cleaner than a chain
  of `if`. Unknown types are logged and ignored.
- `on_answer`: the `has_answered` flag prevents double-clicks from sending twice (the server would
  reject the second anyway — but why send it).
- `_poll_inbox` from chapter 4.8. 50 ms is fast enough; 10 ms wastes CPU.
- Keep `player_name` — `RESULT` contains everyone's answers and the view needs to know which row is "me".

## 14.3 Views

- One container `Frame`, all screens `grid(row=0, column=0, sticky="nsew")`, `tkraise()` the active one.
- `QuestionView.show`: `wraplength=600` on the question label, or long questions run off the window.
  The local countdown: `after(100, tick)` updating a `Progressbar` — and **stop it** in `show_result`
  (keep the `after` id and `after_cancel` it), or the old countdown keeps running under the next question.
- Buttons: `state="disabled"` after answering; colours in `show_result` via `configure(style=...)`
  or plain `tk.Button` with `bg=`.
- `LeaderboardView`: a `ttk.Treeview` with `columns=("rank", "name", "score")`, `show="headings"`.
  `update`: `delete(*get_children())` then `insert` each entry.

💡 If the window freezes when the server sends a question: something in the reader thread touched
a widget. Search for `self.view` in `network_client.py` — it must not be there.

**Exit condition:** two GUI clients play a full game on one computer. Record it.

# Chapter 15 — Stage 6: admin tool and saving games

## 15.1 `GameRepository.save_game`

One transaction, three inserts in order (games → players → answers), because answers need
`player_id`. Keep `player_ids = {name: cursor.lastrowid}` after each player insert. `is_correct`
as `int(record.is_correct)` — SQLite has no boolean.

## 15.2 `GameEngine.end_game`

Build the leaderboard, `winner = board[0].name` (or `None` if nobody played), broadcast GAME_OVER,
then `GameRepository().save_game(...)` with `datetime` objects for `started_at/ended_at`
(convert from your `time.monotonic()` start by recording `datetime.now()` at game start as well —
`monotonic` cannot be turned into a date). Then reset: `state = LOBBY`, keep connected players
(they may want to play again), clear scores and history.

## 15.3 `AdminApp`

A `ttk.Notebook` with two tabs. Questions tab: `Treeview` on top, a form below, buttons in a row.
`on_add` validation: text non-empty, four non-empty options, a radio button selected, difficulty
in 1–3. `on_import_csv`: `filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])`, then show
`messagebox.showinfo("Imported", f"{n} questions")`. Games tab: `Treeview` of `list_recent()`.

**Exit condition:** `pytest -v` all green; a GUI game appears in the Games tab; a question added
in the admin appears in the next game.

# Chapter 16 — Stage 7: load test, Wireshark, documentation

- **Load test**: 8 clients (or 8 terminal scripts) on the classroom network. In the server log,
  note the time between "broadcast QUESTION" and each handler's "sent" line; the largest difference
  is your "question reaches all players" number. Also try 8 answers in the same second — the
  scores must add up.
- **Wireshark**: filter `tcp.port == 5050`; screenshots of the handshake, one QUESTION packet
  (bytes pane shows the JSON), and *Follow TCP Stream* of one round.
- **Question statistics**: `GameRepository.question_stats()` (the SQL is in chapter 6.6) → a table
  for the results chapter.
- Your own tests: `build_command` (good and bad payloads), `QuestionManager.prepare` (too few
  questions), `lobby_payload`.
- UML per `docs/UML.md`; the book per `docs/PROJECT_BOOK_MAP.md`.

💡 `git commit` at the end of every stage. The history is proof of your work over time.

# Chapter 16a — Troubleshooting: the error, the cause, the fix

## 16a.1 Sockets and network

| Message / symptom | Cause | Fix |
|---|---|---|
| `OSError: [Errno 98] Address already in use` / `WinError 10048` | The previous server is still running, or the port is in TIME_WAIT | Stop the old server; `SO_REUSEADDR` before `bind` |
| `ConnectionRefusedError` / `WinError 10061` on the client | No server on that host:port, or wrong IP | Start the server first; check the IP it printed; same port |
| The client hangs on `connect()` for a long time | Wrong IP (a machine that does not exist) or a firewall dropping packets | `settimeout(5)` before connect; check the firewall (below) |
| Works on the same machine, not from another one | **Windows Firewall** blocks port 5050 | Windows Defender Firewall → Advanced → Inbound Rules → New rule → Port 5050 TCP → Allow. Or allow "python.exe" |
| `ConnectionResetError` / `WinError 10054` in a handler | The client process died or closed the laptop | Normal — catch `OSError`, call `close()`, the engine handles the leave |
| `recv` returns `b""` again and again, CPU at 100% | You did not `break` on empty recv | `if not chunk: break` |
| `json.JSONDecodeError: Extra data` | Two messages glued in one `recv` | Use `MessageBuffer` — never `json.loads(chunk)` directly |
| `json.JSONDecodeError: Unterminated string` | One message cut in two | Same — the buffer keeps the partial tail |
| `TypeError: a bytes-like object is required, not 'str'` | `sendall("...")` with a str | `.encode("utf-8")` — `to_wire()` does it |
| Hebrew shows as `מה` in the log | `json.dumps` default | `ensure_ascii=False` |
| Ctrl+C does not stop the server | `accept()` blocks forever | `settimeout(1.0)` on the listening socket |
| Broadcast reaches 7 players, the 8th gets garbage | Two threads called `sendall` on the same socket at once | `_send_lock` in `ClientHandler.send` |

## 16a.2 Threads

| Symptom | Cause | Fix |
|---|---|---|
| Scores sometimes wrong by one answer | Race condition on the answers dict / scores | Every engine method under `with self._lock:` |
| The server freezes completely | Deadlock: `Lock` taken twice by the same thread, or a lock never released | `RLock`; always `with`; never hold the lock while sending |
| `close_question` runs twice, results broadcast twice | Timer and last-answer both call it | `if state != QUESTION: return` + `timer.cancel()` |
| Closing the server leaves the process alive | Non-daemon threads | `daemon=True` on every thread |
| `RuntimeError: main thread is not in main loop` (client) | The reader thread touched a widget | Queue + `after()` polling |
| The client window freezes when a question arrives | `time.sleep` or a loop in the Tk thread, or `inbox.get()` without `_nowait` | `get_nowait()` in `_poll_inbox`; never sleep in Tk |
| Exception in a handler thread, nobody notices | Threads swallow exceptions silently | `try/except Exception: log.exception(...)` around `run()` body; read `logs/server.log` |

## 16a.3 Database and tests

| Message | Cause | Fix |
|---|---|---|
| `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread` | A connection shared across threads | One connection per operation via `connection()`; `check_same_thread=False` |
| `database is locked` | A connection left open, or two long transactions | Always `with db.connection()`; keep transactions short |
| `FOREIGN KEY constraint failed` | Inserting an answer before its player / game | Insert in order games → players → answers, same transaction |
| Deleting a game leaves players | `PRAGMA foreign_keys` not set on that connection | In `get_connection()`, every time |
| `sqlite3.IntegrityError: CHECK constraint failed` | `correct_index` outside 0–3 or `difficulty` outside 1–3 | Validate in the admin form / CSV import — the DB is the last line, not the first |
| A test passes alone and fails with the others | `Database` singleton leaks | `Database._instance = None` in the fixture (already in `conftest.py`) |
| `ModuleNotFoundError: langame` | pytest run from the wrong folder | Run from the project root |
| `test_concurrent_answers_are_all_recorded` fails sometimes | The lock is missing or not around the whole `record_answer` | Lock the whole method, not just the dict write |

## 16a.4 A general debugging method

1. **Read the log first.** `logs/server.log` shows every thread by name. Most "mysteries" are visible there.
2. **Reproduce with terminal clients**, not the GUI — a 10-line script that sends one message is
   easier to reason about than a window.
3. **One player, then two, then eight.** Most bugs appear at two.
4. **Add the thread name to every print**: `threading.current_thread().name`. If a widget update is
   printed from `client-reader`, you found the bug.
5. **Write down every bug that took more than half an hour** in `TASKS.md` — it is the "challenges"
   chapter, and the answer to "what was hardest".
