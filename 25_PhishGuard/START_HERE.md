# 25 · PhishGuard — start here

**Student:** Dani Faris  ·  **Field:** machine learning  ·  **Core algorithms:** URL feature engineering, logistic regression and a random forest, threshold selection

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
| `data/phishing_urls.csv` | 11,430 URLs, half phishing (Hannousse & Yahiouche 2021, Mendeley Data, CC BY 4.0), in the same `URL,Label` format as your project | Your project trains on the Kaggle file (see its `data/README.md`); this one is a second, harder test set |

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
