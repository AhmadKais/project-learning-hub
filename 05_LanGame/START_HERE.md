# 05 · LanGame — start here

**Student:** Liraz Dakseh  ·  **Field:** networks and concurrency  ·  **Core topics:** TCP sockets, message framing, a JSON protocol, threads and locks, a game state machine, time-based scoring

## The problem in one paragraph

A multiplayer trivia game for the classroom network: one computer runs the server, every player runs a
client, the teacher has an admin tool. Simple to describe, and full of real computer-science problems:
**TCP is a stream, not messages** — so you must frame them yourself; **the server talks to 8 players at
once** — so it needs one thread per player, and threads that share data need a lock or points silently
disappear; **the other side cannot be trusted** — garbage must never crash the server; and **the game has
rules in time** — a state machine decides what is legal when, and a timer closes each question.

## What is in this folder

| Folder | What it is | How to use it |
|---|---|---|
| `01_theory/` | Networks, sockets, the protocol, threads, the state machine, the database | Read one chapter before each notebook |
| `02_examples/` | Runnable notebooks — real sockets and threads on your own computer (`127.0.0.1`) | Run every cell, then change things and run again |
| `03_exercises/` | 12 exercises (34 tests) + `solutions.py` | Write, run `pytest`, only then look at the solution |
| `04_build/` | Architecture and the two build chapters for your skeleton | Use it next to `TASKS.md` in your project |
| `05_defence/` | Exam-style questions, answers, resources | Before the defence — and test yourself every few weeks |
| `06_solve/` | `CHECKLIST.md`: all 86 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones · `WALKTHROUGH.md`: every function explained - the problem, the finished code and its test - and the finished project with screenshots | Tick the checklist as you go; open a hint only after you tried |

No dataset needed — everything uses the standard library.

## Setup (once)

From the repo's root folder:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

Open the repo in VS Code, open a notebook from `02_examples/`, choose the `.venv` kernel, **Run All**.
If Windows Firewall asks about Python the first time a notebook opens a socket, allow it (private networks).

## Your lessons — see it before you build it

Illustrated lessons, each built around a **story**, **real-world examples**, pictures and animations from your own
data, diagrams, a **runnable worked example**, checked **videos** and exercises with answers (all lessons:
[`lessons/`](../lessons/README.md), or open `lessons/LESSONS.html` in a browser). Study each one **before** the stage it
belongs to. Studying alone? Follow the 8-step route in the
[lessons README](../lessons/README.md#learning-alone-follow-this-route-for-every-lesson).

| # | Lesson | In one sentence | Inside | Before your skeleton's … |
|---|---|---|---|---|
| 0 | [Lesson 00 — The maths toolkit: all the maths you need, from zero](../lessons/00_math_toolkit/LESSON.md) and the [glossary](../lessons/GLOSSARY.md) | the projects only use about twelve small pieces of maths — this lesson shows each one with a story, a picture, an everyday example, and a calculation you can do on paper. | 4 animations, 3 videos | before everything — and whenever a word or a formula is new |
| 1 | [Lesson 31 — TCP is a stream: sockets, the protocol and message framing](../lessons/31_tcp_framing/LESSON.md) | TCP delivers a reliable stream of bytes with no message boundaries, so every message must end with a marker (a newline) and the receiver must collect bytes in a buffer until a full message has arrived. | 2 animations, 1 video | stages 1-2 |
| 2 | [Lesson 32 — Threads, race conditions and locks](../lessons/32_threads_locks/LESSON.md) | when several threads change the same data, their read–change–write steps can interleave and lose work; a lock lets only one thread at a time into that critical section — use one lock, with `with`, and hold it briefly. | 1 animation | stage 2 |
| 3 | [Lesson 33 — The database: constraints, transactions, indexes, parameters](../lessons/33_databases/LESSON.md) | let the database itself refuse bad rows (constraints), group changes so they happen all-or-nothing (transactions), find rows without reading them all (indexes), and never paste user text into SQL (parameters). | 1 animation, 1 video | stage 3 |
| 4 | [Lesson 30 — Finite state machines: making illegal moves impossible](../lessons/30_state_machines/LESSON.md) | keep the program in exactly one named state at a time and allow only the arrows you drew — then illegal actions (cancel after check-in, a late answer) are not "forgotten checks" but simply impossible. | 2 animations, 1 video | stage 4 |

## Where to start — the learning path

Do the rows **in order**. Each row ends with something you can show your supervisor.

| # | Read (`01_theory/`) | Run (`02_examples/`) | Solve (`03_exercises/`) | Then in your project |
|---|---|---|---|---|
| 0 | `00_intro` | — | — | install, open the skeleton, run `pytest` (red — normal) |
| 1 | `02_networks` (§2.5!), `03_sockets_protocol` | `01_tcp_stream_and_framing` | ex01 – ex03 | stage 1 — protocol and the echo test |
| 2 | `04_threads` | `02_threads_and_locks` | ex04 – ex06 | stage 2 — server, handlers, lobby |
| 3 | `05_state_machine_scoring`, `06_database` | `03_game_engine` | ex07 – ex10 | stages 3–4 — questions, state machine, scoring |
| 4 | `04_build/07_architecture` | `04_mini_server` | ex11 – ex12 | stages 5–6 — the GUI client, the admin tool |
| 5 | `04_build/*` | Wireshark on the mini server | — | stage 7 — load test, capture, the book |
| 6 | `05_defence/*` | re-run the notebooks and explain every output aloud | — | the defence |

## How to work with the exercises

```bash
cd 05_LanGame/03_exercises
pytest test_exercises.py -k ex03 -v      # one exercise (framing, cut at every possible byte)
pytest test_exercises.py -v              # everything
```

ex05 starts 6 threads that close the same round at the same instant, 20 times — it only passes if exactly one
of them scores the round.

## When you are stuck on your project

1. Find the function in `06_solve/CHECKLIST.md` — it names the stage and the test that checks it.
2. Read its docstring in your code again, slowly, and the matching step in `04_build/`.
3. Open `06_solve/HINTS.md` at that function: the 💡 hint first, the 🔧 steps only if you need them.
   Compare your output with the "check yourself" numbers.
4. Still stuck, or finished and want to compare? `06_solve/WALKTHROUGH.md` has the problem and the full solution of every function.
5. Still red after 30 honest minutes? Send your supervisor the test name and the last 10 lines of the error.

## The rule

The notebooks show **one** way to write each piece, as plain functions and small classes. Your project has
its own structure (server, handler, engine, client, views) — **type your project code yourself, do not paste
from the notebooks.** In the defence you will be asked to explain and change any line, and you can only do
that with code you wrote.

## What you should be able to show and explain

| | |
|---|---|
| 3 separate `sendall` calls | arrive in **1** `recv` — framing with `\n` fixes it at any cut |
| 8 threads × 200 unsafe `score += 10` | ~2,000 instead of 16,000 — with a lock, always 16,000 |
| `Lock` vs `RLock` | `record_answer` → `close_question` deadlocks with `Lock` |
| broadcast holding the lock with one slow client | a JOIN waits ~0.5 s; copy-under-lock → 0 ms |
| scoring | 0 s → 1000 · 3 s → 800 · 7.5 s → 500 · 14.9 s → 100 · wrong → 0 |
