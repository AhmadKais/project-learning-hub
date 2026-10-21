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
| `06_solve/` | `CHECKLIST.md`: all 107 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones · `WALKTHROUGH.md`: every function explained - the problem, the finished code and its test - and the finished project with screenshots | Tick the checklist as you go; open a hint only after you tried |
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

## Your lessons — see it before you build it

Illustrated lessons, each built around a **story**, **real-world examples**, pictures and animations from your own
data, diagrams, a **runnable worked example**, checked **videos** and exercises with answers (all lessons:
[`lessons/`](../lessons/README.md), or open `lessons/LESSONS.html` in a browser). Study each one **before** the stage it
belongs to. Studying alone? Follow the 8-step route in the
[lessons README](../lessons/README.md#learning-alone-follow-this-route-for-every-lesson).

| # | Lesson | In one sentence | Inside | Before your skeleton's … |
|---|---|---|---|---|
| 0 | [Lesson 00 — The maths toolkit: all the maths you need, from zero](../lessons/00_math_toolkit/LESSON.md) and the [glossary](../lessons/GLOSSARY.md) | the projects only use about twelve small pieces of maths — this lesson shows each one with a story, a picture, an everyday example, and a calculation you can do on paper. | 4 animations, 3 videos | before everything — and whenever a word or a formula is new |
| 1 | [Lesson 01 — What is "machine learning"?](../lessons/01_what_is_learning/LESSON.md) | instead of writing the rules yourself, you show the computer many examples **with the right answers**, and it finds the rules by itself. | 4 animations, 4 videos | before you start |
| 2 | [Lesson 02 — Feature scaling: putting all numbers on the same ruler](../lessons/02_feature_scaling/LESSON.md) | before comparing examples, change every feature so that "1 step" means the same thing for all of them — otherwise the feature with the biggest numbers wins every comparison. | 3 animations, 2 videos | stage 3 |
| 3 | [Lesson 03 — Is the model good? Counting its right and wrong answers](../lessons/03_confusion_matrix_metrics/LESSON.md) | sort every answer into four boxes (caught, false alarm, missed, correct "no"), and from those four counts compute numbers that answer different questions: *can I trust it when it says yes?* and *does it catch everything?* | 2 animations, 2 videos | stage 4 |
| 4 | [Lesson 15 — k-nearest neighbours: "tell me who your neighbours are, and I'll tell you who you are"](../lessons/15_knn/LESSON.md) | to grade a new wine, find the k most similar wines whose grades you already know, and let them vote — closer wines louder, and with a small correction so the common grade doesn't win just by being common. | 2 animations, 1 video | stage 4 |
| 5 | [Lesson 16 — The kd-tree: skipping work, and when skipping stops working](../lessons/16_kdtree/LESSON.md) | a kd-tree cuts the space into boxes inside boxes so a nearest-neighbour search can skip whole boxes that can't contain a closer wine — which works beautifully in 2–4 dimensions and hardly at all in 11. | 2 animations, 3 videos | stage 5 |
| 6 | [Lesson 05 — Honest testing: cross-validation, nested CV and leakage](../lessons/05_cross_validation_leakage/LESSON.md) | test many times on different slices so that luck averages out, and make sure the test data never — not even a little — helps build the model. | 2 animations, 1 video | stage 6 |
| 7 | [Lesson 17 — Learning how much each feature matters: coordinate search](../lessons/17_feature_weights/LESSON.md) | give each feature a "volume knob" in the distance, and let the computer turn one knob at a time, keeping a change only when the cross-validated score really improves. | 2 animations | stage 6 |
| 8 | [Lesson 33 — The database: constraints, transactions, indexes, parameters](../lessons/33_databases/LESSON.md) | let the database itself refuse bad rows (constraints), group changes so they happen all-or-nothing (transactions), find rows without reading them all (indexes), and never paste user text into SQL (parameters). | 1 animation, 1 video | stage 7 |

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
4. Still stuck, or finished and want to compare? `06_solve/WALKTHROUGH.md` has the problem and the full solution of every function.
5. Still red after 30 honest minutes? Send your supervisor the test name and the last 10 lines of the error.

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
