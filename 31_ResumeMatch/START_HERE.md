# 31 · ResumeMatch — start here

**Student:** Kosai Badreih  ·  **Field:** machine learning / information retrieval  ·  **Core algorithms:** TF-IDF + cosine similarity and BM25, both written from scratch

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
