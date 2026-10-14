# LanGame — the full checklist

Every function you still have to write in your skeleton: **86**, in the order of `TASKS.md`.
Tick each box when its tests are green. The text after each name is the first line of its TODO —
the full instructions are in the docstring in your code. `HINTS.md` (next to this file) helps with the hard ones.

Generated from your skeleton by `tools/make_checklists.py` — do not edit by hand.

## Stage 1 — Protocol and infrastructure

**`langame/common/protocol.py`**

- [ ] `Message.to_wire()` — serialise to bytes ready for socket.sendall(): json.dumps({"type": self.type.value, "payload": self.payload}) + config.MESSAGE_DELIMITER, encoded with config.ENCODING. Use ensure_ascii=False so Hebrew question text st...  
  ✅ checked by `tests/test_protocol.py`
- [ ] `Message.from_wire(line)` — parse ONE line (without the trailing newline). Raise ProtocolError (below) - never a raw json/KeyError - when: * the JSON is invalid * "type" is missing or not a known MessageType * "payload" is missing or not a dict...  
  ✅ checked by `tests/test_protocol.py`
- [ ] `MessageBuffer.feed(chunk)` — 1. self._pending += chunk 2. if len(self._pending) > config.MAX_MESSAGE_BYTES: raise ProtocolError("too_large", ...) 3. split on the delimiter; the LAST piece is incomplete -> keep it in _pending 4. decode every compl...  
  ✅ checked by `tests/test_protocol.py`

> **Exit condition:** `pytest tests/test_protocol.py -v` green. You can explain, with a drawing, why the `\n` delimiter is needed (two messages glued / one message split).

## Stage 2 — Server and lobby

**`langame/server/client_handler.py`**

- [ ] `ClientHandler.run()` — conn.settimeout(config.SOCKET_TIMEOUT_SECONDS) while self._alive: try: chunk = conn.recv(config.RECV_BUFFER_SIZE) except socket.timeout: continue except OSError: break if not chunk: break # client closed the connectio...
- [ ] `ClientHandler._dispatch(message)` — command = build_command(message, self); self.engine.execute(command). Unknown/illegal commands come back from the engine as an ERROR message to send - the handler never decides rules by itself.
- [ ] `ClientHandler.send(message)` — conn.sendall(message.to_wire()) under _send_lock. Return False (and mark not alive) on any OSError instead of raising - the caller may be the broadcaster iterating over all clients.
- [ ] `ClientHandler.close()` — idempotent. Mark not alive, tell the engine the player left (only if player_name is set), close the socket, remove self from the server.

**`langame/server/commands.py`**

- [ ] `JoinCommand.execute(engine)` — validate (state must be LOBBY, name non-empty and unique, <= PLAYER_NAME_MAX_LENGTH, room for one more player); on success engine.add_player(self.name, self.handler) and return None; otherwise return an ERROR with cod...  
  ✅ checked by `tests/test_game_engine.py`
- [ ] `LeaveCommand.execute(engine)` — engine.player_left(self.handler.player_name).  
  ✅ checked by `tests/test_game_engine.py`
- [ ] `build_command(message, handler)` — Factory: message -> Command object.

**`langame/server/game_engine.py`**

- [ ] `GameEngine.execute(command)` — with self._lock: reply = command.execute(self); if reply is not None: command.handler.send(reply). Log every command with its player name and the current state.  
  ✅ checked by `tests/test_game_engine.py`
- [ ] `GameEngine.add_player(name, handler)` — create Player(name, handler.address), store player and handler, set handler.player_name, make the first player the host, send WELCOME to that handler and broadcast a LOBBY_UPDATE.
- [ ] `GameEngine.player_left(name)` — mark the player disconnected and drop its handler. In LOBBY: remove the player entirely and re-pick the host if needed. In QUESTION: if everyone still connected has answered, close the question. Always broadcast LOBBY...
- [ ] `GameEngine.lobby_payload()` — {"players": [names of connected players], "min_players": ...}.
- [ ] `GameEngine.connected_players()` — players with connected == True.

**`langame/server/game_server.py`**

- [ ] `GameServer.serve_forever()` — 1. create a TCP socket: socket.socket(AF_INET, SOCK_STREAM) 2. setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) -> restart without "address in use" 3. bind((config.SERVER_HOST, self.port)); listen(config.MAX_PLAYERS) 4. settim...
- [ ] `GameServer.broadcast(message, exclude_name)` — send `message` to every connected handler (skip exclude_name). Copy the handler list under the lock FIRST, then send outside the lock - a slow client must never block the others or hold the lock while writing. A handl...
- [ ] `GameServer.remove_handler(handler)` — remove a finished handler from the list (under the lock).
- [ ] `GameServer.shutdown()` — set _running False, close every handler socket, close the listen socket, and ask the engine to save an in-progress game.

**`run_server.py`**

- [ ] `print_local_addresses(port)` — print every IPv4 address of this machine so players know what to type. Hint: socket.gethostbyname_ex(socket.gethostname())[2], plus 127.0.0.1 for players on the same computer.

> **Exit condition:** three terminal clients (a 10-line script that connects, sends JOIN and prints what arrives) all receive the same LOBBY_UPDATE; closing one of them does not crash the server; sending garbage returns an ERROR message. `pytest tests/test_game_engine.py -k "join or duplicate or lobby"` green.

## Stage 3 — Database and questions

**`langame/common/models.py`**

- [ ] `Question.public_payload()` — the dict that goes inside a QUESTION message: {"question_id", "text", "options"} - and nothing else. If correct_index leaks here, a modified client can cheat. Write a test for it.  
  ✅ checked by `tests/test_game_engine.py`

**`langame/database/db.py`**

- [ ] `Database.get_connection()` — conn = sqlite3.connect(self.db_path, check_same_thread=False) conn.row_factory = sqlite3.Row conn.execute("PRAGMA foreign_keys = ON") # off by default in SQLite! return conn check_same_thread=False: the server writes...
- [ ] `Database.connection()` — commit on success, rollback on any exception, always close.
- [ ] `Database.initialize_schema()` — conn.executescript(SCHEMA).

**`langame/database/repositories.py`**

- [ ] `QuestionRepository.add(question)` — INSERT and return the new id. created_at = now().isoformat().  
  ✅ checked by `tests/test_repositories.py`
- [ ] `QuestionRepository.get(question_id)` — SELECT one row and map it to a Question (options as a list of 4).  
  ✅ checked by `tests/test_repositories.py`
- [ ] `QuestionRepository.list_ids(category)` — SELECT id ... optionally WHERE category=?. Only ids - this is what QuestionManager shuffles.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `QuestionRepository.count(category)` — SELECT COUNT(*) ...  
  ✅ checked by `tests/test_repositories.py`
- [ ] `QuestionRepository.import_csv(path)` — read data/questions_seed.csv (columns: text, option_a, option_b, option_c, option_d, correct_index, category, difficulty) and insert every row in ONE transaction with executemany. Return how many were imported. Skip r...  
  ✅ checked by `tests/test_repositories.py`

**`langame/server/question_manager.py`**

- [ ] `QuestionManager.prepare(count)` — ids = repository.list_ids(category); shuffle; keep the first `count`. Raise ValueError with a clear message if there are fewer than `count` questions - better than crashing mid-game.
- [ ] `QuestionManager.next()` — pop the next id and return repository.get(id).

> **Exit condition:** `pytest tests/test_repositories.py -k "question or import" tests/test_game_engine.py::test_public_payload_never_leaks_the_answer -v` green. `QuestionManager.prepare(10)` on the seed data gives 10 different ids; `prepare(100)` raises a clear error.

## Stage 4 — State machine and scoring

**`langame/common/models.py`**

- [ ] `build_leaderboard(players)` — sort players by score (highest first), then by name for a stable order, and number them from 1. Disconnected players stay on the board - they still played.  
  ✅ checked by `tests/test_score_engine.py`

**`langame/server/commands.py`**

- [ ] `StartGameCommand.execute(engine)` — only the host may start, and only with >= MIN_PLAYERS.  
  ✅ checked by `tests/test_game_engine.py`
- [ ] `AnswerCommand.execute(engine)` — engine.record_answer(self.handler.player_name, self.question_id, self.choice). The engine itself checks state, question id, 0 <= choice <= 3 and "already answered".  
  ✅ checked by `tests/test_game_engine.py`

**`langame/server/game_engine.py`**

- [ ] `GameEngine.start_game()` — state -> QUESTION path: load the question pool (self.questions.prepare(self.questions_per_game)), reset scores, record started_at, broadcast COUNTDOWN and schedule next_question() with a threading.Timer of LOBBY_COUNT...
- [ ] `GameEngine.next_question()` — if question_number == questions_per_game: return self.end_game() question = self.questions.next(); question_number += 1 answers = {}; state = QUESTION; question_sent_at = time.monotonic() broadcast QUESTION with quest...
- [ ] `GameEngine.record_answer(name, question_id, choice)` — the most important validation in the project. reject (return ERROR) when: state != QUESTION ("not_accepting"), question_id != current ("stale_question"), choice not in 0..3 ("bad_choice"), name already in self.answers...
- [ ] `GameEngine.close_question()` — called by the timer OR by record_answer. Must be safe to call twice (cancel the timer; ignore if state != QUESTION). state = SCORING self.scores.score_round(self.current_question, self.answers, self.players) history.e...  
  ✅ checked by `tests/test_game_engine.py`
- [ ] `GameEngine.result_payload()` — correct_index + one entry per player (choice, is_correct, points).
- [ ] `GameEngine.leaderboard_payload()` — {"entries": [asdict(e) for e in build_leaderboard(self.players)]}.

**`langame/server/score_engine.py`**

- [ ] `ScoreEngine.points_for(is_correct, response_time)` — the formula above. Clamp response_time to [0, time_limit].  
  ✅ checked by `tests/test_score_engine.py`
- [ ] `ScoreEngine.score_round(question, answers, players)` — for every answer: set is_correct and points, and add the points to players[name].score. Players who did not answer get 0 and no AnswerRecord (the result payload shows them as "no answer").  
  ✅ checked by `tests/test_score_engine.py`

> **Exit condition:** `pytest tests/test_score_engine.py tests/test_game_engine.py -v` all green — including `test_concurrent_answers_are_all_recorded` (8 threads at once). A full game runs with terminal clients: questions arrive, answers score, results and leaderboard are broadcast, the game ends after N questions.

## Stage 5 — Graphical client

**`langame/client/controllers/client_controller.py`**

- [ ] `ClientController.__init__(root, default_host, default_port)` — build the MainWindow and give it the callbacks: self.view = MainWindow(root, on_connect=self.on_connect, on_answer=self.on_answer, on_start=self.on_start, default_host=..., default_port=...) root.protocol("WM_DELETE_W...
- [ ] `ClientController.start()` — two lines: self.view.show_connect() self.root.after(POLL_MS, self._poll_inbox)
- [ ] `ClientController.on_connect(host, port, name)` — validate the name locally (non-empty, length), then net.connect(host, port) inside try/except -> view.show_error on failure; on success send join(name) and show the lobby screen (waiting state).
- [ ] `ClientController.on_start()` — host only - send START_GAME.
- [ ] `ClientController.on_answer(choice)` — ignore if has_answered; send answer(current_question_id, choice); has_answered = True; view.question.lock_buttons(choice).
- [ ] `ClientController.on_close()` — leave tidily when the window is closed: try: self.net.send(leave_message()) except Exception: pass # already disconnected - do not block exit self.net.close() self.root.destroy()
- [ ] `ClientController._poll_inbox()` — THE BRIDGE BETWEEN THE NETWORK THREAD AND THE SCREEN. Read this carefully; it is the piece students get wrong most often.
- [ ] `ClientController.handle_message(message)` — one branch per MessageType (a dict of handlers is cleaner than if/elif): WELCOME -> remember name/is_host; lobby.set_host_controls(is_host) LOBBY_UPDATE -> lobby.set_players(names, min_players) COUNTDOWN -> lobby.show...

**`langame/client/network_client.py`**

- [ ] `NetworkClient.connect(host, port)` — create the socket, connect((host, port)) with a timeout of a few seconds, then remove the timeout (settimeout(None)) for the reader, set connected=True and start _reader_loop in a daemon thread. Let socket errors prop...
- [ ] `NetworkClient._reader_loop()` — recv loop like ClientHandler.run(), but every decoded message goes to self.inbox.put(message). On disconnect put a special Message(MessageType.ERROR, {"code": "disconnected", ...}) so the UI can react, and set connect...
- [ ] `NetworkClient.send(message)` — sendall(message.to_wire()); on OSError mark disconnected.
- [ ] `NetworkClient.close()` — idempotent; shutdown + close the socket.

**`langame/client/views/connect_view.py`**

- [ ] `ConnectView.__init__(parent, on_connect, default_host, default_port)` — three labelled Entries (host, port, name) + a button that reads them and calls on_connect(host, int(port), name.strip()). Bind <Return> to the same action.

**`langame/client/views/game_over_view.py`**

- [ ] `GameOverView.__init__(parent, on_back)` — winner label, a Treeview of final scores, a Back button.
- [ ] `GameOverView.show(winner, entries)` — .

**`langame/client/views/leaderboard_view.py`**

- [ ] `LeaderboardView.__init__(parent)` — a ttk.Treeview with columns rank / name / score.
- [ ] `LeaderboardView.update(entries)` — clear and refill from [{"rank", "name", "score"}, ...].
- [ ] `LeaderboardView.highlight(my_name)` — (optional): bold / coloured row for the local player.

**`langame/client/views/lobby_view.py`**

- [ ] `LobbyView.__init__(parent, on_start)` — a Listbox of player names, a status label ("3 / 2 players - waiting for host"), a Start button (hidden unless host), and a big countdown label.
- [ ] `LobbyView.set_players(names, min_players)` — refresh the list and the status label.
- [ ] `LobbyView.set_host_controls(is_host)` — show/enable the Start button only for the host.
- [ ] `LobbyView.show_countdown(seconds)` — "Game starts in 5..." counting down locally with after().

**`langame/client/views/main_window.py`**

- [ ] `MainWindow.__init__(root, on_connect, on_answer, on_start, default_host, default_port)` — create ConnectView, LobbyView, QuestionView, LeaderboardView, GameOverView in a shared container with grid(row=0, column=0, sticky="nsew"), keep them as attributes (self.connect, self.lobby, self.question, ...), and p...
- [ ] `MainWindow.show(name)` — tkraise() the screen called `name`.
- [ ] `MainWindow.show_error(text)` — messagebox.showerror - the only place tkinter.messagebox is imported.

**`langame/client/views/question_view.py`**

- [ ] `QuestionView.__init__(parent, on_answer)` — THE WORKED EXAMPLE SCREEN. Build this one first; the lobby and game-over screens are simpler versions of the same shape.
- [ ] `QuestionView.show(payload)` — a new question arrived from the server: self.counter.config(text=f"Question {payload['index']} / {payload['total']}") self.question.config(text=payload["text"]) for btn, option in zip(self.buttons, payload["options"])...
- [ ] `QuestionView.lock_buttons(chosen)` — the player has answered; stop them answering twice: for i, btn in enumerate(self.buttons): btn.config(state="disabled") if i == chosen: btn.config(text="> " + btn.cget("text"))
- [ ] `QuestionView.show_result(payload, my_name)` — the round is over, show what happened: if self._countdown_job: # stop the timer first self.after_cancel(self._countdown_job) self._countdown_job = None self.timer["value"] = 0

> **Exit condition:** two clients on one computer play a full game through the GUI: connect, lobby with names, host presses Start, countdown, questions with a time bar, colours on the result, live leaderboard, game-over screen. The window never freezes. Record a short video.

## Stage 6 — Admin tool and persistence

**`langame/admin/admin_app.py`**

- [ ] `AdminApp.__init__(root)` — a ttk.Notebook with two tabs: "Questions": Treeview (id, text, category, difficulty) + a form (text, 4 options, correct radio, category, difficulty) + buttons Add / Update / Delete / Import CSV / Refresh "Games": Tree...
- [ ] `AdminApp.refresh_questions()` — re-read from the database and redraw the table: rows = self.questions.list_all() for item in self.tree.get_children(): # clear first! self.tree.delete(item) for q in rows: self.tree.insert("", "end", iid=str(q.id), va...
- [ ] `AdminApp.on_add()` — read the form, validate (4 non-empty options, a correct one), questions.add().
- [ ] `AdminApp.on_update()` — questions.update() for the selected row.
- [ ] `AdminApp.on_delete()` — confirm with messagebox.askyesno, then questions.delete().
- [ ] `AdminApp.on_import_csv()` — filedialog.askopenfilename -> questions.import_csv(path) -> show the count.
- [ ] `AdminApp.refresh_games()` — reload from games.list_recent().

**`langame/database/repositories.py`**

- [ ] `QuestionRepository.update(question)` — UPDATE every editable column WHERE id=?.
- [ ] `QuestionRepository.delete(question_id)` — DELETE WHERE id=?.
- [ ] `QuestionRepository.list_all(category)` — for the admin table.
- [ ] `QuestionRepository.categories()` — SELECT DISTINCT category ORDER BY category.
- [ ] `GameRepository.save_game(started_at, ended_at, questions_count, time_limit, category, winner_name, players, answers)` — ONE transaction that inserts the game, then every player (remember the new player ids in a dict name -> id), then every answer with the right player_id. Return the game id. If anything fails nothing is written - that...  
  ✅ checked by `tests/test_repositories.py`
- [ ] `GameRepository.list_recent(limit)` — newest games first with winner and player count (a JOIN + GROUP BY).  
  ✅ checked by `tests/test_repositories.py`

**`langame/server/game_engine.py`**

- [ ] `GameEngine.end_game()` — state = GAME_OVER; build the leaderboard; broadcast GAME_OVER with the winner; save everything with GameRepository.save_game(...); then reset to a fresh LOBBY so players can play again.

> **Exit condition:** `pytest -v` all green. A game played through the GUI appears in the admin's "Games" tab with the right winner and players; a question added in the admin appears in the next game.

## Stage 7 — Load test, network analysis, documentation

**`langame/database/repositories.py`**

- [ ] `GameRepository.question_stats()` — (optional): per question: how many times asked, % correct, average response time. A great table for the project book: SELECT q.id, q.text, COUNT(a.id) AS asked, AVG(a.is_correct) AS pct_correct, AVG(a.response_time) A...

> **Exit condition:** a complete project book where every number comes from a log, a test run or a capture.
