# 08 · SpamClassifier — start here

**Student:** Laith Halabi  ·  **Field:** machine learning  ·  **Core algorithm:** Multinomial Naive Bayes, written from scratch

> **Next week:** a talk in class - [Spam: why it exists and how computers learned to catch it](PRESENTATION_01.md).
>
> **Your current mission:** [Mission 1](MISSION_01.md) - study, homework and a 10-minute talk in class (two weeks).

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
| `06_solve/` | `CHECKLIST.md`: all 99 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones · `WALKTHROUGH.md`: every function explained - the problem, the finished code and its test - and the finished project with screenshots | Tick the checklist as you go; open a hint only after you tried |
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

Illustrated lessons, each built around a **story**, **real-world examples**, pictures and animations from your own
data, diagrams, a **runnable worked example**, checked **videos** and exercises with answers (all lessons:
[`lessons/`](../lessons/README.md), or open `lessons/LESSONS.html` in a browser). Study each one **before** the stage it
belongs to. Studying alone? Follow the 8-step route in the
[lessons README](../lessons/README.md#learning-alone-follow-this-route-for-every-lesson).

| # | Lesson | In one sentence | Inside | Before your skeleton's … |
|---|---|---|---|---|
| 0 | [Lesson 00 — The maths toolkit: all the maths you need, from zero](../lessons/00_math_toolkit/LESSON.md) and the [glossary](../lessons/GLOSSARY.md) | the projects only use about twelve small pieces of maths — this lesson shows each one with a story, a picture, an everyday example, and a calculation you can do on paper. | 4 animations, 3 videos | before everything — and whenever a word or a formula is new |
| 1 | [Lesson 01 — What is "machine learning"?](../lessons/01_what_is_learning/LESSON.md) | instead of writing the rules yourself, you show the computer many examples **with the right answers**, and it finds the rules by itself. | 4 animations, 4 videos | before you start |
| 2 | [Lesson 06 — Cleaning text: from a message to a list of words the computer can count](../lessons/06_text_preprocessing/LESSON.md) | before a computer can compare texts it must cut them into words and make "the same word" really look the same — and every small choice in that cleaning decides what the computer is allowed to see. | 3 animations, 3 videos | stage 2 |
| 3 | [Lesson 07 — TF-IDF: turning text into numbers that mean something](../lessons/07_tfidf/LESSON.md) | a word is important for a document if it is **frequent in it** and **rare in the others** — TF-IDF is that sentence turned into arithmetic. | 2 animations, 2 videos | stage 3 |
| 4 | [Lesson 11 — Naive Bayes from scratch: counting your way to a spam filter](../lessons/11_naive_bayes/LESSON.md) | every word in a message is a clue; Naive Bayes counts how often each clue appeared in spam and in normal messages, and combines the clues into one verdict — and can tell you which clues convinced it. | 3 animations, 2 videos | stage 4 |
| 5 | [Lesson 02 — Feature scaling: putting all numbers on the same ruler](../lessons/02_feature_scaling/LESSON.md) | before comparing examples, change every feature so that "1 step" means the same thing for all of them — otherwise the feature with the biggest numbers wins every comparison. | 3 animations, 2 videos | stage 5 |
| 6 | [Lesson 05 — Honest testing: cross-validation, nested CV and leakage](../lessons/05_cross_validation_leakage/LESSON.md) | test many times on different slices so that luck averages out, and make sure the test data never — not even a little — helps build the model. | 2 animations, 1 video | stage 5 |
| 7 | [Lesson 14 — The SVM: the widest street between two classes (and how to get a probability out of it)](../lessons/14_svm_calibration/LESSON.md) | the SVM draws the fence between two classes that stays as far as possible from both — and because its answer is a distance, not a probability, we "calibrate" it into an honest percentage. | 3 animations, 2 videos | stage 5 |
| 8 | [Lesson 03 — Is the model good? Counting its right and wrong answers](../lessons/03_confusion_matrix_metrics/LESSON.md) | sort every answer into four boxes (caught, false alarm, missed, correct "no"), and from those four counts compute numbers that answer different questions: *can I trust it when it says yes?* and *does it catch everything?* | 2 animations, 2 videos | stage 6 |
| 9 | [Lesson 04 — Where do we draw the line? Thresholds and the ROC curve](../lessons/04_threshold_roc/LESSON.md) | a model gives each example a **score** from 0 to 1; **people** choose the line (threshold) above which we say "yes" — and the right line depends on which mistake costs more. | 2 animations, 2 videos | stage 6 |
| 10 | [Lesson 33 — The database: constraints, transactions, indexes, parameters](../lessons/33_databases/LESSON.md) | let the database itself refuse bad rows (constraints), group changes so they happen all-or-nothing (transactions), find rows without reading them all (indexes), and never paste user text into SQL (parameters). | 1 animation, 1 video | stage 7 |

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
| spam share of the corpus | 13.4% |
| Naive Bayes, F1 on spam (5 folds) | 0.925 ± 0.010 |
| calibrated LinearSVC, F1 on spam | 0.936 ± 0.018 — the gap is inside the noise |
| from-scratch NB vs sklearn | identical to ~1e-14 |
| strongest spam words | claim, prize, won, guaranteed, URLTOKEN |

Why is NB the primary model even if the SVM scores a little higher? → `01_theory/04_naive_bayes.md` §4.8.
