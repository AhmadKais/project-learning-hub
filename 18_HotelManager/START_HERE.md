# 18 · HotelManager — start here

**Student:** Eran Nijm  ·  **Field:** software engineering — algorithmic business logic  ·  **Core algorithms:** interval overlap, room allocation strategies, a rule-chain pricing engine, a booking state machine

> **Next week:** a talk in class - [one algorithm from your project](PRESENTATION_01.md).
>
> **Your current mission:** [Mission 1](MISSION_01.md) - study, homework and a paper task at the board (two weeks).

## The problem in one paragraph

A hotel management system — but **not** a CRUD screen over a database. Four algorithms are the heart of it,
and the examiner will look for them: (1) **do two stays collide?** — half-open intervals and the rule
`a < d and c < b`; (2) **which free room to give?** — First-Fit, Best-Fit and preference scoring behind one
interface, with an experiment that measures which is best; (3) **what does the stay cost, and why?** — a
chain of independent pricing rules, each adding an explained line to the invoice; (4) **the booking's life
cycle** — a state machine where illegal moves are impossible and cancelling frees the room with no extra code.

## What is in this folder

| Folder | What it is | How to use it |
|---|---|---|
| `01_theory/` | The four algorithms, each with worked examples and the proof/derivation | Read one chapter before each notebook |
| `02_examples/` | Runnable notebooks — one per algorithm — that reproduce the guide's numbers exactly | Run every cell, then change things and run again |
| `03_exercises/` | 13 short functions to write yourself (21 tests) + `solutions.py` | Write, run `pytest`, only then look at the solution |
| `04_build/` | Architecture, the stage-by-stage build chapter, troubleshooting | Use it next to `TASKS.md` in your project |
| `05_defence/` | Exam-style questions, answers, resources | Before the defence — and test yourself every few weeks |
| `06_solve/` | `CHECKLIST.md`: all 113 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones · `WALKTHROUGH.md`: every function explained - the problem, the finished code and its test - and the finished project with screenshots | Tick the checklist as you go; open a hint only after you tried |
| `data/` | The 24 sample rooms and guests from your project | Notebook 02 uses the rooms |

## Setup (once)

From the repo's root folder:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

Open the repo in VS Code, open a notebook from `02_examples/`, choose the `.venv` kernel, **Run All**.

## Your lessons — see it before you build it

Illustrated lessons, each built around a **story**, **real-world examples**, pictures and animations from your own
data, diagrams, a **runnable worked example**, checked **videos** and exercises with answers (all lessons:
[`lessons/`](../lessons/README.md), or open `lessons/LESSONS.html` in a browser). Study each one **before** the stage it
belongs to. Studying alone? Follow the 8-step route in the
[lessons README](../lessons/README.md#learning-alone-follow-this-route-for-every-lesson).

| # | Lesson | In one sentence | Inside | Before your skeleton's … |
|---|---|---|---|---|
| 0 | [Lesson 00 — The maths toolkit: all the maths you need, from zero](../lessons/00_math_toolkit/LESSON.md) and the [glossary](../lessons/GLOSSARY.md) | the projects only use about twelve small pieces of maths — this lesson shows each one with a story, a picture, an everyday example, and a calculation you can do on paper. | 4 animations, 3 videos | before everything — and whenever a word or a formula is new |
| 1 | [Lesson 27 — Do two stays collide? Half-open intervals and a two-comparison rule](../lessons/27_intervals_overlap/LESSON.md) | write a stay as [check-in, check-out) — nights, not days — and two stays collide exactly when `a < d and c < b`: two comparisons that cover every possible case. | 1 animation | stage 1 |
| 2 | [Lesson 33 — The database: constraints, transactions, indexes, parameters](../lessons/33_databases/LESSON.md) | let the database itself refuse bad rows (constraints), group changes so they happen all-or-nothing (transactions), find rows without reading them all (indexes), and never paste user text into SQL (parameters). | 1 animation, 1 video | stage 2 |
| 3 | [Lesson 28 — Which free room to give? First-Fit, Best-Fit, Preference — and the Strategy pattern](../lessons/28_allocation_strategies/LESSON.md) | when several rooms are free, the rule for choosing one decides who gets turned away later — so we write three rules, measure them on 200 simulated months, and program them so the hotel can swap the rule with one line. | 2 animations | stage 3 |
| 4 | [Lesson 29 — What does the stay cost, and why? A chain of pricing rules](../lessons/29_rule_chain_pricing/LESSON.md) | build the price as a chain of small rules — base, weekend, long stay, extras, VAT — each adding visible invoice lines, and remember that the order of the rules changes the total. | 1 animation | stage 4 |
| 5 | [Lesson 30 — Finite state machines: making illegal moves impossible](../lessons/30_state_machines/LESSON.md) | keep the program in exactly one named state at a time and allow only the arrows you drew — then illegal actions (cancel after check-in, a late answer) are not "forgotten checks" but simply impossible. | 2 animations, 1 video | stage 5 |

## Where to start — the learning path

Do the rows **in order**. Each row ends with something you can show your supervisor.

| # | Read (`01_theory/`) | Run (`02_examples/`) | Solve (`03_exercises/`) | Then in your project |
|---|---|---|---|---|
| 0 | `00_intro`, `01_python` | — | — | install, open the skeleton, run `pytest` (red — normal) |
| 1 | `03_intervals` — prove the rule with De Morgan on paper | `01_intervals` | ex01 – ex04 | `DateRange`, availability, `BookingRepository.in_period` |
| 2 | `04_allocation` | `02_allocation` | ex05 – ex07 | the three strategies + the factory |
| 3 | `05_pricing` — do the 4,445.06 invoice by hand first | `03_pricing` | ex08 – ex10 | the pricing engine and its rules |
| 4 | `06_fsm`, `07_database` | `04_state_machine` | ex11 – ex13 | `HotelService` transitions, invoices in one transaction |
| 5 | `04_build/*` | — | — | the UI, the experiment table, the book |
| 6 | `05_defence/*` | re-run the notebooks and explain every number aloud | — | the defence |

## How to work with the exercises

```bash
cd 18_HotelManager/03_exercises
pytest test_exercises.py -k ex02 -v      # one exercise (all eight interval cases)
pytest test_exercises.py -v              # everything
```

ex10 must reproduce both invoices of the theory chapter to the agora: **4,445.06** and **2,442.60**.

## When you are stuck on your project

1. Find the function in `06_solve/CHECKLIST.md` — it names the stage and the test that checks it.
2. Read its docstring in your code again, slowly, and the matching step in `04_build/`.
3. Open `06_solve/HINTS.md` at that function: the 💡 hint first, the 🔧 steps only if you need them.
   Compare your output with the "check yourself" numbers.
4. Still stuck, or finished and want to compare? `06_solve/WALKTHROUGH.md` has the problem and the full solution of every function.
5. Still red after 30 honest minutes? Send your supervisor the test name and the last 10 lines of the error.

## The rule

The notebooks show **one** way to write each algorithm, as plain functions. Your project has its own
structure (classes, layers, tests) — **type your project code yourself, do not paste from the notebooks.**
In the defence you will be asked to explain and change any line, and you can only do that with code you
wrote.

## The numbers you should be able to explain

| | |
|---|---|
| overlap rule checked against "share a night" | 4,356 pairs, 0 mismatches; with `<=` case F wrongly collides |
| availability, 20,000 bookings | SQL + index uses `SEARCH ... USING INDEX` instead of reading every row |
| allocation, 200 simulated months | Best-Fit serves the most and wastes the fewest beds; **First-Fit earns the most** (price is per room) |
| pricing | 4,445.06 · 2,442.60 · wrong rule order → 4,466.30 |
