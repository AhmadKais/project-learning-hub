# 31 · ResumeMatch — start here

**Student:** Kosai Badreih  ·  **Field:** machine learning / information retrieval  ·  **Core algorithms:** TF-IDF + cosine similarity and BM25, both written from scratch

> **Next week:** a talk in class - [one algorithm from your project](PRESENTATION_01.md).
>
> **Your current mission:** [Mission 1](MISSION_01.md) - study, homework and a paper task at the board (two weeks).

## The problem in one paragraph

A recruiter has a pile of CVs and one job advert. Your program ranks the candidates — **and explains every
score**: which words made it, which required skills were found and which are missing. Two ranking methods,
both written by you: TF-IDF with cosine similarity (length is handled by geometry) and BM25 (repetition
saturates with `k1`, length is corrected explicitly with `b`). Your research question: **how does length
normalisation change who is ranked first?** — answered by comparing `b = 0` with `b = 0.75`. Everything
depends on preprocessing: if `C++` becomes `C`, no ranking method can save you.

## What is in this folder

| Folder | What it is | How to use it |
|---|---|---|
| `01_theory/` | The ideas and the math, with examples done by hand | Read one chapter before each notebook |
| `02_examples/` | Runnable notebooks on 200 synthetic CVs and 5 job adverts | Run every cell, then change things and run again |
| `03_exercises/` | 13 short functions to write yourself + automatic tests + `solutions.py` | Write, run `pytest`, only then look at the solution |
| `04_build/` | Code map and the stage-by-stage build chapters for your skeleton | Use it next to `TASKS.md` in your project |
| `05_defence/` | Exam-style questions and resources | Before the defence — and test yourself every few weeks |
| `06_solve/` | `CHECKLIST.md`: all 73 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones · `WALKTHROUGH.md`: every function explained - the problem, the finished code and its test - and the finished project with screenshots | Tick the checklist as you go; open a hint only after you tried |
| `data/` | `resumes.csv` (200 invented CVs), `jobs.csv` (5 adverts + which CVs are relevant) | Made by `tools/make_resume_data.py` — **no real person's CV**, on purpose |

The synthetic CVs contain traps on purpose: very long CVs that list every technology, "keyword stuffers"
that repeat one skill 15 times, and a few CVs that **copied a job advert** without having its skills. The
notebooks use them to show what `k1`, `b` and the reliability check are for.

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
| 1 | [Lesson 06 — Cleaning text: from a message to a list of words the computer can count](../lessons/06_text_preprocessing/LESSON.md) | before a computer can compare texts it must cut them into words and make "the same word" really look the same — and every small choice in that cleaning decides what the computer is allowed to see. | 3 animations, 3 videos | stage 2 |
| 2 | [Lesson 07 — TF-IDF: turning text into numbers that mean something](../lessons/07_tfidf/LESSON.md) | a word is important for a document if it is **frequent in it** and **rare in the others** — TF-IDF is that sentence turned into arithmetic. | 2 animations, 2 videos | stage 3 |
| 3 | [Lesson 08 — How similar are two texts? Arrows, the dot product and cosine similarity](../lessons/08_vectors_cosine/LESSON.md) | draw every text as an arrow; two texts are similar when their arrows **point the same way** — and the cosine of the angle between them is that similarity, as one number from 0 to 1. | 1 animation, 2 videos | stage 4 |
| 4 | [Lesson 09 — BM25 and the inverted index: how real search engines rank](../lessons/09_bm25_inverted_index/LESSON.md) | BM25 fixes two weaknesses of TF-IDF — repeating a word counts too much, and long documents match everything — and the inverted index lets a search engine skip every document that doesn't contain the query's words. | 2 animations, 3 videos | stage 5 |
| 5 | [Lesson 10 — Is the ranking good? Precision@k and MRR](../lessons/10_ranking_metrics/LESSON.md) | a ranking is judged at the top — **P@k** asks "how many of the first k are good?" and **MRR** asks "how high is the first good one?". | 2 animations, 1 video | stage 6 |
| 6 | [Lesson 33 — The database: constraints, transactions, indexes, parameters](../lessons/33_databases/LESSON.md) | let the database itself refuse bad rows (constraints), group changes so they happen all-or-nothing (transactions), find rows without reading them all (indexes), and never paste user text into SQL (parameters). | 1 animation, 1 video | stage 8 |

## Where to start — the learning path

Do the rows **in order**. Each row ends with something you can show your supervisor.

| # | Read (`01_theory/`) | Run (`02_examples/`) | Solve (`03_exercises/`) | Then in your project |
|---|---|---|---|---|
| 0 | `00_intro`, `00b_python` | — | — | install, open the skeleton, run `pytest` (all red — normal) |
| 1 | `04_pipeline` (twice!) | `01_preprocessing` | ex01 – ex03 | the preprocessing stages of `TASKS.md` |
| 2 | `01_vectors`, `02_cosine`, `05_explain` | `02_tfidf_cosine` | ex04 – ex08 | TF-IDF index, ranking, explanations |
| 3 | `03_bm25` | `03_bm25` | ex09 – ex11 | BM25 with the inverted index; the b = 0 experiment |
| 4 | `06_evaluate` | `04_evaluate` | ex12 – ex13 | metrics, ground truth (label **before** you look), the reliability check |
| 5 | `04_build/*` | — | — | the database, the UI, the book |
| 6 | `05_defence/*` | re-run the notebooks and explain every number aloud | — | the defence |

## How to work with the exercises

```bash
cd 31_ResumeMatch/03_exercises
pytest test_exercises.py -k ex08 -v      # one exercise
pytest test_exercises.py -v              # everything
```

ex08 checks that your explanation **sums exactly to the score** — the same promise your project makes in
`test_explanation_sums_to_the_score`.

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

| | P@5 | P@10 | MRR |
|---|---|---|---|
| TF-IDF + cosine | 0.80 | 0.88 | 0.57 |
| BM25, b = 0 | 0.76 | 0.86 | 0.55 |
| BM25, b = 0.75 | 0.80 | 0.86 | 0.57 |
| …after moving CVs flagged by the reliability check to the end: | | | |
| TF-IDF + cosine | 1.00 | 0.98 | 1.00 |
| BM25, b = 0 | 0.92 | 0.96 | 0.90 |
| BM25, b = 0.75 | 0.96 | 0.96 | 1.00 |

With `b = 0` up to 5 of the top 10 are very long CVs; with `b = 0.75` at most 2. Why? → `01_theory/03_bm25.md`,
"Problem 2 — length". (These are synthetic numbers that show the method; your book reports your real ones.)
