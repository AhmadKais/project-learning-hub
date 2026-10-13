# Chapter 7 — The architecture: OOP, patterns and MVC

The Ministry requires OOP, a design pattern and a database. In this project they are not
decoration — they are what lets you test the game rules without a network and change one part
without breaking the others.

## 7.1 The three programs and the shared package

```text
run_server.py  ──▶  langame/server/     ──┐
run_client.py  ──▶  langame/client/     ──┼──▶  langame/common/  (protocol, models)
run_admin.py   ──▶  langame/admin/      ──┘          │
                                                     ▼
                              langame/database/  (server + admin only)
```

The client never imports `database`; the admin never imports `server`; nobody imports the views
except the client controller. If an import crosses these lines, something is in the wrong place.

## 7.2 Command pattern — `server/commands.py`

Every action a client can take is a **class** with an `execute(engine)` method: `JoinCommand`,
`AnswerCommand`, `LeaveCommand`, `StartGameCommand`. The handler thread *builds* the object from
the message (`build_command`, a small Factory); the engine *executes* it under the lock.

Why this and not a big `if message.type == ...` in the handler:

- the rules are in one place (the engine), the parsing in another (the factory);
- a new action = one new class, no existing code touched;
- the list of executed commands, with timestamps, is a complete **replay** of the game — put it
  in the log and you can reconstruct any dispute ("I answered first!").

📄 **The shape of a command**
```python
class AnswerCommand(Command):
    def __init__(self, handler, question_id, choice): ...
    def execute(self, engine):                       # called WITH the engine lock held
        return engine.record_answer(self.handler.player_name, self.question_id, self.choice)
        # returns None (accepted) or an ERROR Message to send back
```

## 7.3 State pattern (simplified) — `GameEngine`

Chapter 5. `GameState` is an enum, transitions are methods, every method checks the state first.
The full State pattern would make each state a class; for four states the enum form is clearer.
Say that in the defense — knowing *why* you simplified is worth more than the pattern itself.

## 7.4 MVC — the client

- **Model**: `NetworkClient` — the connection and the inbox queue. Knows the protocol, knows
  nothing about windows.
- **View**: `views/` — Tkinter screens. Know nothing about sockets, JSON or rules. They receive
  plain dicts/lists and call back plain functions (`on_answer(2)`).
- **Controller**: `ClientController` — the only class that knows both. Messages in → screen
  updates; button clicks → messages out.

📄 **Quick check that your MVC is real**
```bash
grep -rn "import socket\|protocol" langame/client/views/      # must be empty
grep -rn "tkinter" langame/client/network_client.py           # must be empty
```

## 7.5 Repository — `database/repositories.py`

All SQL in one file. The engine says `questions.get(id)` and gets a `Question`; the admin says
`questions.add(q)`. Nobody else knows what `INSERT` is. If you move to PostgreSQL, one file changes.

## 7.6 Singleton — `Database`

One object decides where the DB file is and how a connection is configured. `__new__` returns
the same instance every time. Downside: tests must reset it (`conftest.py` does).

## 7.7 Producer / consumer — `NetworkClient.inbox`

The reader thread produces messages; the Tkinter thread consumes them (chapter 4.8). The
`queue.Queue` between them is the whole synchronization — no lock needed in your code because
`Queue` is thread-safe by design.

## 7.8 The full flow — from a click to points on the screen

📄 **One answer, end to end**
```text
 1. player clicks option 2                       [Client View]     QuestionView -> on_answer(2)
 2. ClientController.on_answer(2)                [Client Controller] has_answered? no -> send
 3. NetworkClient.send(answer(17, 2))            [Client Model]    bytes -> TCP
 4. ClientHandler.run() receives bytes           [Server thread A]
 5. MessageBuffer.feed -> Message(ANSWER)        [common.protocol]
 6. build_command -> AnswerCommand               [Server commands]
 7. GameEngine.execute(cmd)  with lock           [Server engine]
 8.   record_answer: state ok? id ok? not yet answered? -> store, t = 2.31 s
 9. ... timer or last answer -> close_question   [Server engine / timer thread]
10.   ScoreEngine.score_round -> 800 points      [Server]
11.   server.broadcast(RESULT), broadcast(LEADERBOARD)   [Server, outside the lock]
12. NetworkClient reader thread -> inbox         [Client Model]
13. ClientController._poll_inbox -> handle_message [Client Controller, Tk thread]
14. QuestionView.show_result, LeaderboardView.update   [Client View]
```

The sequence diagram in the book is this list. Notice the views appear only at lines 1 and 14,
and the socket only at 3, 4 and 12.

## ✅ Check yourself — Chapter 7

1. A student puts `import socket` in `lobby_view.py` to show the player's own IP. Is that a
   problem? Where should that information come from instead?
2. What does `build_command` return for a message of type `LOBBY_UPDATE` sent *by a client*?
   Where is that decided?
3. Explain why the handler thread does not call `engine.record_answer` directly but goes through
   `AnswerCommand.execute`. Give one concrete benefit.
4. `a = Database(); b = Database(); print(a is b)` — what prints? And
   `QuestionRepository() is QuestionRepository()`?
5. Add a new action "SKIP" (the host skips the current question). List every file that changes.
6. Why does the reader thread put messages in a queue instead of calling the controller directly?

## 📚 Further reading — Chapter 7

- **Refactoring Guru** — Command https://refactoring.guru/design-patterns/command ·
  State https://refactoring.guru/design-patterns/state · Singleton https://refactoring.guru/design-patterns/singleton ·
  Factory Method https://refactoring.guru/design-patterns/factory-method
- **Python docs — abc** (abstract classes): https://docs.python.org/3/library/abc.html
- **Python docs — dataclasses**: https://docs.python.org/3/library/dataclasses.html
- **Real Python — MVC in Python**: https://realpython.com/lessons/mvc-summary/
- **pytest — Getting Started** and **fixtures**: https://docs.pytest.org/en/stable/getting-started.html ·
  https://docs.pytest.org/en/stable/how-to/fixtures.html
