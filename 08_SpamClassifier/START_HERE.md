# 08 · SpamClassifier — start here

**Student:** Laith Halabi  ·  **Field:** machine learning  ·  **Core algorithm:** Multinomial Naive Bayes, written from scratch

## The problem in one paragraph

A desktop spam filter: a message comes in, your program says **spam or not — and why**. Text has to
become numbers first (cleaning, tokens, TF-IDF, a few hand-made signals like CAPS and `!!!`). Then Naive
Bayes — which you write yourself — counts how often each word appears in spam and in ham and combines the
evidence. Its big advantage: every verdict can be explained word by word, straight from the model. A
library SVM is the yardstick you compare against, fairly. Finally, because hiding a real message is much
worse than letting one spam through, the decision threshold is not 0.5 — it is chosen so precision stays
above 0.98.

## What is in this folder

| Folder | What it is | How to use it |
|---|---|---|
| `01_theory/` | The ideas and the math, with examples done by hand | Read one chapter before each notebook |
| `02_examples/` | Runnable notebooks on the real SMS Spam Collection (5,574 messages) | Run every cell, then change things and run again |
| `03_exercises/` | 13 short functions to write yourself + automatic tests + `solutions.py` | Write, run `pytest`, only then look at the solution |
| `04_build/` | Architecture, code map, and the stage-by-stage build chapter for your skeleton | Use it next to `TASKS.md` in your project |
| `05_defence/` | Exam-style questions, answers, resources | Before the defence — and test yourself every few weeks |
| `06_solve/` | `CHECKLIST.md`: all 99 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones | Tick the checklist as you go; open a hint only after you tried |
| `data/sms_spam.csv` | The corpus, as `text,label` — the same format your project's `data/corpus/messages.csv` expects | Copy it there to train your real model |

## Setup (once)

From the repo's root folder:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

Open the repo in VS Code, open a notebook from `02_examples/`, choose the `.venv` kernel, **Run All**.

## Your lessons — see it before you build it

Illustrated lessons with animations and pictures from your own data (all of them: [`lessons/`](../lessons/README.md),
or open `lessons/LESSONS.html` in a browser). Watch the lesson **before** the stage it belongs to.

| # | Lesson | Before your skeleton's … |
|---|---|---|
| 1 | [Lesson 01 — What "learning" means: data, splits and overfitting](../lessons/01_what_is_learning/LESSON.md) | before you start |
| 2 | [Lesson 06 — Cleaning text: from a message to a list of terms](../lessons/06_text_preprocessing/LESSON.md) | stage 2 |
| 3 | [Lesson 07 — TF-IDF: turning text into numbers that mean something](../lessons/07_tfidf/LESSON.md) | stage 3 |
| 4 | [Lesson 11 — Naive Bayes from scratch: counting your way to a spam filter](../lessons/11_naive_bayes/LESSON.md) | stage 4 |
| 5 | [Lesson 02 — Feature scaling: making every feature speak the same language](../lessons/02_feature_scaling/LESSON.md) | stage 5 |
| 6 | [Lesson 05 — Honest evaluation: cross-validation, nested CV and leakage](../lessons/05_cross_validation_leakage/LESSON.md) | stage 5 |
| 7 | [Lesson 14 — The SVM, calibration, and comparing two models honestly](../lessons/14_svm_calibration/LESSON.md) | stage 5 |
| 8 | [Lesson 03 — Measuring a classifier: confusion matrix, precision, recall, F1](../lessons/03_confusion_matrix_metrics/LESSON.md) | stage 6 |
| 9 | [Lesson 04 — The threshold is a decision: ROC, AUC and choosing where to cut](../lessons/04_threshold_roc/LESSON.md) | stage 6 |
| 10 | [Lesson 33 — The database: constraints, transactions, indexes, parameters](../lessons/33_databases/LESSON.md) | stage 7 |

## Where to start — the learning path

Do the rows **in order**. Each row ends with something you can show your supervisor.

| # | Read (`01_theory/`) | Run (`02_examples/`) | Solve (`03_exercises/`) | Then in your project |
|---|---|---|---|---|
| 0 | `00_intro`, `01_python`, `02_ml_basics` | — | — | install, open the skeleton, run `pytest` (all red — normal) |
| 1 | `03_features` | `01_text_to_numbers` | ex01 – ex07 | stages 1–3 of `TASKS.md` (cleaning, tokens, TF-IDF) |
| 2 | `04_naive_bayes` — work §4.10 on paper first! | `02_naive_bayes_from_scratch` | ex08 – ex11 | stage 4 — the heart of the project |
| 3 | `05_svm_comparison`, `06_evaluation` | `03_compare_and_threshold` | ex12 – ex13 | stages 5–6 |
| 4 | `04_build/*` | — | — | the database, the UI, the book |
| 5 | `05_defence/*` | re-run the notebooks and explain every number aloud | — | the defence |

## How to work with the exercises

```bash
cd 08_SpamClassifier/03_exercises
pytest test_exercises.py -k ex08 -v      # one exercise
pytest test_exercises.py -v              # everything
```

Exercises 8–10 together must agree with scikit-learn's `MultinomialNB` to 1e-9 — exactly the blocking
test of your project's stage 4. If it fails, the table in theory §4.9 tells you where to look.

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
| spam share of the corpus | 13.4% |
| Naive Bayes, F1 on spam (5 folds) | 0.925 ± 0.010 |
| calibrated LinearSVC, F1 on spam | 0.936 ± 0.018 — the gap is inside the noise |
| from-scratch NB vs sklearn | identical to ~1e-14 |
| strongest spam words | claim, prize, won, guaranteed, URLTOKEN |

Why is NB the primary model even if the SVM scores a little higher? → `01_theory/04_naive_bayes.md` §4.8.
