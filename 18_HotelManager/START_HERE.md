# 18 · HotelManager — start here

**Student:** Eran Nijm  ·  **Field:** software engineering — algorithmic business logic  ·  **Core algorithms:** interval overlap, room allocation strategies, a rule-chain pricing engine, a booking state machine

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
| `06_solve/` | `CHECKLIST.md`: all 113 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones | Tick the checklist as you go; open a hint only after you tried |
| `data/` | The 24 sample rooms and guests from your project | Notebook 02 uses the rooms |

## Setup (once)

From the repo's root folder:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

Open the repo in VS Code, open a notebook from `02_examples/`, choose the `.venv` kernel, **Run All**.

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
4. Still red after 30 honest minutes? Send your supervisor the test name and the last 10 lines of the error.

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
