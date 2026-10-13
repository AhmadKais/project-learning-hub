# Chapter 0 — How to use this guide

💡 **In short:** this guide takes you from "I have an empty project" to "I can defend it". Read a chapter, write the code it describes, run the tests, move on. Do not read the whole thing first.

## 0.1 What you are building

WineGrader takes eleven numbers from a wine laboratory — acidity, sugar, sulphur dioxide, alcohol and so on — plus the wine's colour, and answers two questions:

1. Is this wine **low**, **medium** or **high** quality?
2. **Why?**

The answer to the second question is the five wines from the database that are most similar to this one, with their grades. "It is graded high because four of the five most similar wines we know were graded high" is an explanation a wine maker can check with their own eyes. That is the whole idea of k-nearest neighbours, and it is why the project uses it.

## 0.2 What makes it a project and not an exercise

Calling `KNeighborsClassifier().fit(X, y)` from scikit-learn takes one line. Your project is everything that line hides, written by you and measured honestly:

- **What does "similar" mean** when one measurement is around 0.05 and another around 140? (Chapter 3 — scaling.)
- **How should the neighbours vote** when only one wine in five is high quality? (Chapter 4 — the imbalance correction.)
- **How can the search be fast?** A kd-tree — and the surprising measured answer that in 12 dimensions it barely helps. (Chapter 5.)
- **Can k-NN learn anything?** Yes: a weight for every feature. (Chapter 6.)
- **How do you measure without fooling yourself?** Nested cross-validation, and the duplicates trap. (Chapter 7.)

## 0.3 The shape of the work

There are eight stages in `TASKS.md`. Each stage is tested by its own test file, and each one is built on the ones before it.

| Stage | What you build | Tests that must go green |
|---|---|---|
| 1 | Loading, validating, duplicates | `test_loader.py` |
| 2 | Looking at the data | `test_analysis.py` |
| 3 | Scaling, distance, linear search | `test_scaler_metrics.py`, linear part of `test_index.py` |
| 4 | **k-NN, baselines, scoring, folds** | `test_classifiers.py` |
| 5 | The kd-tree | `test_index.py` |
| 6 | Tuning, weight learning, nested CV | `test_tuning_weights.py` |
| 7 | Bundle, database, the lab station | `test_app.py`, `test_evaluation_bundle.py` |
| 8 | The final measurement and the book | everything |

Stage 4 is the heart. Everything before it is preparation, everything after it is making it better, faster, honest and usable.

## 0.4 The tests are the specification

Open the project and run:

```bash
pytest -v
```

About 150 tests fail with `NotImplementedError`. That is correct. The tests were written before you write the code, and each one describes exactly what a function has to do. When you are not sure what `class_priors` should return for a class that never appears, do not guess — read `test_class_priors`. The answer is there.

💡 This is the most useful habit you can build this year: when stuck, read the test, not just the docstring.

## 0.5 How to read a chapter

Each chapter has the same shape:

- a **💡 In short** box — the whole chapter in two or three lines
- the explanation, with code
- **❓ question boxes** — the kind of thing an examiner asks, with the answer underneath

Chapter 17 collects the questions into a mock exam, and chapter 20 has short answers. If you can answer every box without looking, you are ready.

## 0.6 What you need to know already

Python: functions, classes, lists, dictionaries, `for` loops. Chapter 1 covers the numpy you need — read it even if you know Python well, because numpy thinks differently.

Maths: the distance between two points (Pythagoras), averages, and what a standard deviation is. Nothing else. You do **not** need linear algebra or statistics beyond that.

## 0.7 A warning about shortcuts

scikit-learn is installed. It is there for one purpose: the tests compare your code against it. `test_knn_matches_sklearn` demands that your k-NN gives exactly the same answers as scikit-learn's on 200 wines. That test is your proof of correctness.

If you import scikit-learn's k-NN inside `winegrader/`, the project is over — the whole claim of this work is "I understand this algorithm, and here is my implementation to prove it". In the defence you will be asked to explain every line.
