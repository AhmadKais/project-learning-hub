# 32 · WineGrader — start here

**Student:** Seif Ferro  ·  **Field:** machine learning  ·  **Core algorithm:** k-nearest neighbours, written from scratch

## The problem in one paragraph

A wine laboratory measures 11 things about a wine (acidity, sugar, sulphur dioxide, alcohol…) and
knows its colour. Your program answers: **is this wine low, medium or high quality — and why?** The
"why" is the five most similar wines we already know, with their grades. That is k-NN: find the k most
similar examples and let them vote. The hard parts are what "similar" means (scaling), how the votes
count (weights, rare grades), how to search fast (k-d tree), and how to measure honestly (duplicates,
nested cross-validation).

## What is in this folder

| Folder | What it is | How to use it |
|---|---|---|
| `01_theory/` | The math and the ideas, with small examples done by hand | Read one chapter before each notebook |
| `02_examples/` | Runnable notebooks: every algorithm implemented step by step **on the real wine data** | Run every cell, then change things and run again |
| `03_exercises/` | 13 short functions to write yourself + automatic tests + `solutions.py` | Write, run `pytest`, only then look at the solution |
| `04_build/` | Architecture, code map, and the stage-by-stage build chapter for your project skeleton | Use it next to `TASKS.md` in your project |
| `05_defence/` | Exam-style questions, answers, resources | Before the defence — and test yourself every few weeks |
| `06_solve/` | `CHECKLIST.md`: all 107 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones | Tick the checklist as you go; open a hint only after you tried |
| `data/` | The UCI Wine Quality dataset (6,497 wines) | The notebooks read it from here |

## Setup (once)

From the repo's root folder:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

Open the repo in VS Code, open a notebook from `02_examples/`, choose the `.venv` kernel when asked,
and press **Run All**.

## Where to start — the learning path

Do the rows **in order**. Each row ends with something you can show your supervisor.

| # | Read (`01_theory/`) | Run (`02_examples/`) | Solve (`03_exercises/`) | Then in your project |
|---|---|---|---|---|
| 0 | `00_intro`, `01_python`, `02_ml_basics` | — | — | install, open the skeleton, run `pytest` (all red — normal) |
| 1 | `03_data_scaling` | `01_data_and_scaling` | ex01 – ex04 | stages 1–3 of `TASKS.md` |
| 2 | `04_knn` | `02_knn_from_scratch` | ex05 – ex08 | stage 4 — the heart of the project |
| 3 | `05_kdtree` | `03_kdtree` | ex09 | stage 5 |
| 4 | `07_evaluation` | `04_honest_evaluation` | ex10 – ex12 | stage 6 (folds, nested CV) |
| 5 | `06_tuning_weights` | `05_feature_weights` | ex13 | stage 6 (weight learning) |
| 6 | `04_build/*` | — | — | stages 7–8, the book |
| 7 | `05_defence/*` | re-run all notebooks and explain every number aloud | — | the defence |

## How to work with the exercises

```bash
cd 32_WineGrader/03_exercises
pytest test_exercises.py -k ex01 -v      # one exercise
pytest test_exercises.py -v              # everything
```

A red test tells you exactly what was expected and what you returned. Read it — it is the fastest
teacher you have. Stuck for more than 20 minutes? Re-read the theory section named in the docstring,
look at the notebook, and only then open `solutions.py`.

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

| | macro-F1 |
|---|---|
| always "medium" | 0.20 |
| nearest centroid | 0.49 |
| k-NN without scaling | 0.45 |
| k-NN, z-score, k ≈ 15–21 | 0.58 |

k-d tree in 12 dimensions: computes ~55% of the distances and is slower than the linear search in
Python — in 2 dimensions it computes ~2%. Why? → `01_theory/05_kdtree.md` §5.7.
