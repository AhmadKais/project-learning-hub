# 25 · PhishGuard — start here

**Student:** Dani Faris  ·  **Field:** machine learning  ·  **Core algorithms:** URL feature engineering, logistic regression and a random forest, threshold selection

> **Your current mission:** [Mission 1](MISSION_01.md) - study, homework and a 10-minute talk in class (two weeks).

## The problem in one paragraph

Someone pastes a link; your program says **phishing or not — and why**, without ever opening the page.
The hard, interesting part is turning a URL into 20 numbers that capture how attackers work: the real
owner is read from the *right* of the host (`paypal.com.secure-login.xyz` belongs to `secure-login.xyz`),
`@` hides the real host, cheap TLDs, urgency words, random-looking paths (entropy). Then two models —
logistic regression (simple, its weights *are* the explanation) and a random forest (stronger) — are
compared fairly, and the decision threshold is chosen on validation data so that at least 95% of phishing
is caught.

## What is in this folder

| Folder | What it is | How to use it |
|---|---|---|
| `01_theory/` | The ideas and the math, with examples done by hand | Read one chapter before each notebook |
| `02_examples/` | Runnable notebooks on 11,430 real URLs; `url_features.py` = the extractor from notebook 01 | Run every cell, then change things and run again. **Run 02 before 03** (it saves the trained models) |
| `03_exercises/` | 12 short functions to write yourself + automatic tests + `solutions.py` | Write, run `pytest`, only then look at the solution |
| `04_build/` | Architecture, code map, and the stage-by-stage build chapter for your skeleton | Use it next to `TASKS.md` in your project |
| `05_defence/` | Exam-style questions, answers, resources | Before the defence — and test yourself every few weeks |
| `06_solve/` | `CHECKLIST.md`: all 59 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones · `WALKTHROUGH.md`: every function explained - the problem, the finished code and its test - and the finished project with screenshots | Tick the checklist as you go; open a hint only after you tried |
| `data/phishing_urls.csv` | 11,430 URLs, half phishing (Hannousse & Yahiouche 2021, Mendeley Data, CC BY 4.0), in the same `URL,Label` format as your project | Your project trains on the Kaggle file (see its `data/README.md`); this one is a second, harder test set |

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
| 1 | [Lesson 01 — What is "machine learning"?](../lessons/01_what_is_learning/LESSON.md) | instead of writing the rules yourself, you show the computer many examples **with the right answers**, and it finds the rules by itself. | 4 animations, 4 videos | before you start |
| 2 | [Lesson 18 — A URL as numbers: feature engineering and Shannon entropy](../lessons/18_url_features_entropy/LESSON.md) | a model can't "look" at a link, so we turn each clue a person would notice — who really owns the address, strange endings, suspicious words, random-looking characters — into a number. | 2 animations, 3 videos | stages 1-2 |
| 3 | [Lesson 02 — Feature scaling: putting all numbers on the same ruler](../lessons/02_feature_scaling/LESSON.md) | before comparing examples, change every feature so that "1 step" means the same thing for all of them — otherwise the feature with the biggest numbers wins every comparison. | 3 animations, 2 videos | stage 3 |
| 4 | [Lesson 12 — Logistic regression: a points system that learns its own points](../lessons/12_logistic_regression/LESSON.md) | give every warning sign some points, add them up, squash the total into a probability with the sigmoid — and let the computer find the best points by walking downhill on its mistakes. | 3 animations, 3 videos | stage 3 |
| 5 | [Lesson 13 — Decision trees and random forests: a flow chart that writes itself](../lessons/13_trees_forests/LESSON.md) | a decision tree is a flow chart of yes/no questions that the computer builds by always asking the question that separates the classes best; a random forest asks a hundred slightly different trees and lets them vote. | 3 animations, 2 videos | stage 4 |
| 6 | [Lesson 05 — Honest testing: cross-validation, nested CV and leakage](../lessons/05_cross_validation_leakage/LESSON.md) | test many times on different slices so that luck averages out, and make sure the test data never — not even a little — helps build the model. | 2 animations, 1 video | stage 4 |
| 7 | [Lesson 03 — Is the model good? Counting its right and wrong answers](../lessons/03_confusion_matrix_metrics/LESSON.md) | sort every answer into four boxes (caught, false alarm, missed, correct "no"), and from those four counts compute numbers that answer different questions: *can I trust it when it says yes?* and *does it catch everything?* | 2 animations, 2 videos | stage 4 |
| 8 | [Lesson 04 — Where do we draw the line? Thresholds and the ROC curve](../lessons/04_threshold_roc/LESSON.md) | a model gives each example a **score** from 0 to 1; **people** choose the line (threshold) above which we say "yes" — and the right line depends on which mistake costs more. | 2 animations, 2 videos | stage 4 |
| 9 | [Lesson 33 — The database: constraints, transactions, indexes, parameters](../lessons/33_databases/LESSON.md) | let the database itself refuse bad rows (constraints), group changes so they happen all-or-nothing (transactions), find rows without reading them all (indexes), and never paste user text into SQL (parameters). | 1 animation, 1 video | stage 6 |

## Where to start — the learning path

Do the rows **in order**. Each row ends with something you can show your supervisor.

| # | Read (`01_theory/`) | Run (`02_examples/`) | Solve (`03_exercises/`) | Then in your project |
|---|---|---|---|---|
| 0 | `00_intro`, `01_python`, `02_ml_basics` | — | — | install, open the skeleton, run `pytest` (red — normal) |
| 1 | `03_features` — fill the §3.3 table by hand first | `01_url_features` | ex01 – ex04 | stage 1 (parser + extractor), stage 2 (data) |
| 2 | `04_models` | `02_models` | ex05 – ex09 | stages 3–4 (logistic, forest, grid search) |
| 3 | `05_evaluation` | `03_threshold_roc_mistakes` | ex10 – ex12 | stages 4–5 (threshold, ROC, explanation) |
| 4 | `04_build/*` | — | — | stages 6–7 (database, UI, drift test, the book) |
| 5 | `05_defence/*` | re-run the notebooks and explain every number aloud | — | the defence |

## How to work with the exercises

```bash
cd 25_PhishGuard/03_exercises
pytest test_exercises.py -k ex07 -v      # one exercise
pytest test_exercises.py -v              # everything
```

ex07 checks your gradient against a numerical derivative — if it passes, your "error × input" formula is
right. ex12 must give exactly scikit-learn's AUC, including ties.

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

## The numbers you should be able to explain (this dataset)

| | |
|---|---|
| strongest single features (before any model) | digit_ratio, entropy, suspicious_word_count, url_length |
| logistic regression (from scratch), validation accuracy | 0.78 — same predictions as scikit-learn |
| random forest (grid-searched), validation accuracy | 0.87, AUC 0.94 on test |
| threshold for recall ≥ 0.95 (chosen on validation) | ≈ 0.21 → test recall 0.96, precision 0.75 |

This dataset is harder than the Kaggle file — expect higher numbers in your project.
