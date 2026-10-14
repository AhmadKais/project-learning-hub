# 00 · Getting started — for everyone (about 30 minutes)

Do this once. At the end you will have the repo on your computer, a working Python environment, one notebook
running, and one exercise tested.

## 1. Install the tools

| Tool | Where | Notes |
|---|---|---|
| Python 3.10 or newer | https://www.python.org/downloads/ | Windows: tick **"Add Python to PATH"** in the installer |
| Git | https://git-scm.com/download/win | keep the defaults |
| VS Code | https://code.visualstudio.com | then install the extensions **Python** and **Jupyter** (Ctrl+Shift+X) |

## 2. Get the repo

You were invited to this private repository on GitHub — accept the invitation in the e-mail first. Then, in a
terminal (in VS Code: Terminal → New Terminal):

```bash
cd C:\Projects                       # or any folder you like
git clone <the repo URL from GitHub>
cd project-learning-hub
```

When the teacher adds material later, get it with:

```bash
git pull
```

⚠️ Do your exercises in your own copy. If `git pull` complains that your `exercises.py` changed, run
`git stash`, then `git pull`, then `git stash pop` — your work comes back on top of the update.

## 3. Create the environment (once)

```bash
python -m venv .venv
.venv\Scripts\activate               # Windows      (Linux / macOS: source .venv/bin/activate)
pip install -r requirements.txt
```

You will see `(.venv)` at the start of the prompt. Every time you open a new terminal, run the `activate` line again.

**FaceEmotion only:** also install PyTorch for your graphics card — see `13_FaceEmotion/START_HERE.md`.

## 4. Run a notebook

1. In VS Code open your project folder's `02_examples/` and click the first `.ipynb`.
2. Top right: **Select Kernel** → **Python Environments** → `.venv`.
3. **Run All** (or Shift+Enter cell by cell).

The notebooks are saved **with** their outputs, so you can read them on GitHub before you run anything. Running
them yourself is the point, though: change a number, run again, see what changes.

## 5. Test an exercise

```bash
cd NN_YourProject/03_exercises
pytest test_exercises.py -k ex01 -v
```

At first every test is red with `NotImplementedError` — that is the starting point. Open `exercises.py`, write
the body of `ex01_...`, run the command again until it is green, then go on to `ex02`.

How to read a red test:

```
>       assert ex.ex05_minkowski(a, b, p=1) == pytest.approx(7.0)
E       assert 5.0 == 7.0 ± 7.0e-06
```

= with `p=1` your function returned 5.0, the test expected 7.0. The test is the fastest teacher you have.

## 6. When you are stuck

1. Re-read the theory section named in the exercise's docstring.
2. Find the same idea in the notebook and run that cell with your own numbers.
3. Print! `print(x.shape, x[:5])` solves half of all bugs.
4. Only after 20 honest minutes: open `solutions.py`, read **one** function, close it, and write yours again
   from memory.

Stuck on your **project** rather than an exercise? Your folder's `06_solve/HINTS.md` has hints, numbers to check
against and the common traps for every hard function of your skeleton — in the order of `TASKS.md`.
5. Bring the question to the lesson — with the red test output copied.

## Useful references

- Python tutorial: https://docs.python.org/3/tutorial/
- NumPy for absolute beginners: https://numpy.org/doc/stable/user/absolute_beginners.html
- pytest — getting started: https://docs.pytest.org/en/stable/getting-started.html
- Git — the basics in 15 minutes: https://rogerdudler.github.io/git-guide/
