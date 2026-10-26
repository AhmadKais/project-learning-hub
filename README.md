# Project Learning Hub — Software Engineering, Grade 14, 2025–2026

Atid – Western Galilee · Ministry of Education final project (questionnaire 714918)

Everything you need to **understand** the algorithms of your final project: the theory and the math with
examples done by hand, runnable example implementations, exercises with automatic tests, and a clear
plan of where to start. Your project skeleton (the code you will hand in) is in your own package — this
repo is where you **learn** what goes into it.

**Next week:** every student teaches the class one algorithm from their project - the choices are in [`PRESENTATIONS.md`](PRESENTATIONS.md).

## Find your folder

| # | Project | Student | Field | Core algorithms |
|---|---|---|---|---|
| 05 | [LanGame](05_LanGame/START_HERE.md) | Liraz Dakseh | networks & concurrency | TCP framing, JSON protocol, threads & locks, game state machine, time-based scoring |
| 08 | [SpamClassifier](08_SpamClassifier/START_HERE.md) | Laith Halabi | machine learning | TF-IDF, **Multinomial Naive Bayes from scratch**, calibrated SVM, precision-floor threshold |
| 13 | [FaceEmotion](13_FaceEmotion/START_HERE.md) | Ryan Raed | deep learning & vision | CNN / ResNet (EmotionNet), training loop, Haar cascade, temporal smoothing |
| 18 | [HotelManager](18_HotelManager/START_HERE.md) | Eran Nijm | algorithmic business logic | interval overlap, Best-Fit allocation, rule-chain pricing, booking state machine |
| 25 | [PhishGuard](25_PhishGuard/START_HERE.md) | Dani Faris | machine learning | URL feature engineering, **logistic regression from scratch**, random forest, ROC / threshold |
| 31 | [ResumeMatch](31_ResumeMatch/START_HERE.md) | Kosai Badreih | information retrieval | **TF-IDF + cosine and BM25 from scratch**, inverted index, P@k / MRR |
| 32 | [WineGrader](32_WineGrader/START_HERE.md) | Seif Ferro | machine learning | **k-NN from scratch**, k-d tree, feature-weight learning, nested cross-validation |

**Start with [`00_common/`](00_common/README.md)** (30 minutes: clone, install, run a notebook, run the tests), then open your
folder's `START_HERE.md`.

**New: [`lessons/`](lessons/README.md)** — 34 illustrated lessons (a maths toolkit + one per algorithm of all seven
projects), written so you can **learn alone**: a story, real-world examples, animations and charts made from the projects'
own data, diagrams, runnable worked examples, checked videos, exercises with answers and a one-card summary. Open
[`lessons/LESSONS.html`](lessons/LESSONS.html) to see them all in one page. Your `START_HERE.md` lists your lessons in order.

## What every project folder contains

```
NN_Project/
├── START_HERE.md     the problem in one paragraph, setup, and the learning path - READ FIRST
├── 01_theory/        the ideas and the math, with worked examples you can redo on paper
├── 02_examples/      Jupyter notebooks: each algorithm implemented step by step on real data, already run
├── 03_exercises/     exercises.py (you fill it) + test_exercises.py (checks you) + solutions.py
├── 04_build/         architecture, code map, and the stage-by-stage chapters for your skeleton
├── 05_defence/       exam-style questions, answers, further reading
├── 06_solve/         CHECKLIST.md (every function, with its test) + HINTS.md (when stuck) + WALKTHROUGH.md (problem + solution + test of every function, screenshots)
└── data/             the data the notebooks use (where we are allowed to share it)
```

The learning loop, for every topic:

0. **See** it — the matching lesson in `lessons/` (pictures and animations first).
1. **Read** the theory chapter — do the hand examples on paper.
2. **Run** the notebook — every cell, top to bottom. Then change numbers and run again.
3. **Solve** the matching exercises until `pytest` is green. Only then look at `solutions.py`.
4. **Build** the matching stage of your project (`TASKS.md` in your skeleton). Tick each function in
   `06_solve/CHECKLIST.md`; when one will not go green, open its entry in `06_solve/HINTS.md`.

## The one rule

The notebooks and solutions show **one** way to write each algorithm, as plain functions. Your project has
its own structure — classes, layers, tests. **Type your project code yourself; do not paste.** In the defence
you will be asked to explain and change any line of your project, and you can only do that with code you
wrote and understood.

## For the teacher — maintaining this repo

| Tool | What it does |
|---|---|
| `tools/notebook_src/<project>/*.py` | the notebook sources (plain Python with `# %%` cells) — edit these, not the `.ipynb` |
| `python tools/build_notebooks.py [project]` | converts the sources to `.ipynb`, **runs** them and saves the outputs |
| `python tools/build_lessons.py` | redraws every lesson's pictures / animations / videos and rebuilds `lessons/LESSONS.html` |
| `python tools/sync_guides.py` | re-copies the theory / build / defence chapters from the students' study guides |
| `python tools/make_resume_data.py` | regenerates the synthetic CVs for ResumeMatch |
| `python tools/make_checklists.py` | regenerates every `06_solve/CHECKLIST.md` from the students' skeletons (run after a skeleton changes) |
| `python tools/make_walkthroughs.py` | regenerates every `06_solve/WALKTHROUGH.md` from the skeletons, the teacher solutions and `tools/walkthrough_problems/` (run after either changes) |
| `python tools/check_walkthroughs.py` | proves the walkthroughs are complete: pastes everything they show into a clean copy of each skeleton and runs its tests; also flags ready-made skeleton code that differs from the solution |
| `EXERCISES=solutions pytest <project>/03_exercises` | checks that the solutions pass their own tests |

Data sources and licences are listed in each project's `data/README.md`.
