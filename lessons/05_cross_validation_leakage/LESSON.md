# Lesson 05 — Honest testing: cross-validation, nested CV and leakage

> **For:** Seif (nested CV is the heart of his evaluation) · Laith · Dani · everyone (leakage) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lessons 00 §2–3, 01, 03 &nbsp;·&nbsp; **After this:** the tuning stages of the ML projects

## The story

> Sami (the wine shop, Lesson 02) now has a program that grades a wine as low / medium / high. A company offers to buy
> it — **if it is really good**. Sami tested it once on 300 wines and got 0.61. He tests again on 300 *other* wines:
> 0.55. Which number is true? And the company's expert warns him: *"Half the programs we see score great at home and
> badly with us, because the programmer accidentally let the test wines help."* This lesson is how to get **one honest
> number**, and how to never fool yourself.

## 🎯 By the end, the student can

1. Explain why one test split is "one roll of the dice", and how k-fold cross-validation fixes it.
2. Compute a cross-validated score: mean ± standard deviation.
3. Explain **leakage** with two real demonstrations, and name the four common leaks.
4. Explain nested cross-validation: one loop to **choose**, one loop to **measure**.

## Words you need

| word | meaning |
|---|---|
| **fold** | one slice of the data (e.g. one fifth) |
| **k-fold cross-validation (CV)** | test k times, each time on a different fold, train on the rest; average the k scores |
| **mean ± std** | the average score and how much it jumps between folds (Lesson 00 §2–3) |
| **hyper-parameter** | a setting chosen by people, not learned: k in k-NN, C, the threshold (Lesson 01) |
| **tuning / grid search** | trying many settings and keeping the best |
| **leakage** | information from the test data sneaks into training or into a decision → a falsely good score |
| **nested CV** | an inner CV to choose settings, inside an outer CV that measures |

---

## 1. One split = one roll of the dice

300 test wines is not a lot. Whether a few hard wines land in the test pile or not changes the score by several
points. If Sami then chooses between `k = 15` and `k = 17` on such a noisy number, he's choosing by luck.

## 2. k-fold cross-validation — every wine is tested once

![k-fold animation](figs/kfold.gif)

1. Shuffle the wines and cut them into **5 folds** (slices).
2. **Round 1:** fold 1 is the test, folds 2–5 are training. Train, then score on fold 1.
3. **Round 2:** fold 2 is the test, the others train. … and so on, 5 rounds.
4. Report the **mean** of the 5 scores, and their **std** (how much they jump).

Every wine is tested **exactly once**, and every score comes from wines the model didn't train on.

### By hand

The 5 scores Sami gets (real wine data, 5,320 unique wines, a k-NN):

```
round:   1      2      3      4      5
score:  0.606  0.573  0.574  0.564  0.593

mean = (0.606 + 0.573 + 0.574 + 0.564 + 0.593) / 5 = 2.910 / 5 = 0.582
std:  differences from 0.582:  +0.024  −0.009  −0.008  −0.018  +0.011
      squares (× 1,000,000 to avoid tiny numbers): 576, 81, 64, 324, 121 → sum 1166 → /5 = 233.2 → back: 0.000233
      √0.000233 = 0.015
report:  0.582 ± 0.015
```

**How to read the ±:** if another setting scores 0.590, that's within the jumping range — a **tie**, not a win.

## 3. Stratified folds

![stratified vs random folds](figs/stratified.png)

"High" wines are only 19 %. Random folds (left) can get 5 % high wines in one fold and 30 % in another — every fold
tests a different problem. **Stratified** folds (right) deal the high wines out evenly, like dealing cards suit by suit.
Seif writes this himself in `stratified_kfold`.

## 4. Leakage — the test must know NOTHING

**Leakage** = something from the test data helped build the model or make a decision. Nothing crashes. The score just
becomes too good — and the program fails with the real customer.

**Analogy:** a teacher's assistant accidentally sees the exam on Sunday. On Wednesday she gets 100. Does she know the
material? We can't tell anymore.

### Demonstration 1 — 89 % on pure noise

![leakage demo](figs/leakage.png)

The experiment: 100 rows, 5,000 columns of **random numbers**, and labels that are **coin flips**. There is *nothing* to
learn — any honest method must score about 50 %.

* **The leak:** first choose the 20 columns "most related to the label" using **all 100 rows**, then cross-validate on
  those 20 columns → **89 %**. The choosing step already looked at the test rows' labels.
* **Honest:** do the choosing **inside** each training fold only → **55 %** (≈ a coin flip — the truth).

### Demonstration 2 — the duplicate trap (Seif's real data)

![duplicates](figs/duplicates.png)

1,177 wines in the dataset are **exact copies** of other wines. If one copy lands in training and its twin in the test
fold, the 1-NN finds the twin at distance 0 and copies its grade: score 0.676. Without duplicates: 0.539. **Remove
duplicates before splitting** — after splitting is too late.

### The four leaks and their guards

| leak | guard |
|---|---|
| the same example (or its copy) in train and test | remove duplicates **before** splitting; `assert_no_leakage` |
| scaler / vocabulary / IDF / feature choice fitted on all rows | fit them on the training part only (a `Pipeline`) |
| settings or threshold chosen using the test set | a validation set, or **nested** CV |
| looking at the final test score and trying again | run the final evaluation **once** |

## 5. Nested cross-validation — choosing and measuring separately

If Sami uses the same 5 folds to **choose** the best k (trying 20 values) **and** to **report** the score, the reported
score is "the best of 20 tries" — lucky, so too high. Nested CV gives each job its own data:

![nested CV](figs/nested.png)

* **Outer loop (5 folds) — measures.** One fold is locked away as the outer test.
* **Inner loop (3 folds, inside the other 4 outer folds only) — chooses.** Try every setting, pick the best.
* Train with the chosen setting on the 4 outer folds, score **once** on the locked fold.
* Repeat for each outer fold; the average of the 5 outer scores is the honest number.

**Analogy:** to pick the best study method you do practice tests (inner loop). The real exam (outer fold) is written by
someone else and you never see it while practising.

```python
for train, test in outer_splits:                       # 5 times
    inner  = stratified_kfold(y[train], 3)
    tuned  = grid_search(X[train], y[train], inner)    # never sees X[test]
    w      = learn_weights(X[train], y[train], tuned.best, inner).weights
    result = evaluate_split(model_with(tuned.best, w), X, y, train, test, ...)
```

Seif's proof that nothing leaks: `test_nested_never_sees_outer_test` scrambles the outer test labels and runs again — the
chosen settings must stay **identical**, because the procedure never looked at them.

## 6. Common mistakes

| student says | the truth |
|---|---|
| "CV trains one model 5 times" | It trains 5 different models; CV measures the **procedure**. Afterwards you train one final model on all training data. |
| "With duplicates my score is higher — great" | It is better at looking up answers, not at grading wine. |
| "A small leak doesn't matter" | You can't know how big it is — that's the problem. |

## 7. Activities

1. **Deal the folds (10 min).** 20 cards: 12 red, 8 black. Deal 4 folds randomly; count colours. Then deal stratified.
2. **Spot the leak (15 min).** On the board: (a) scaler fitted before the split, (b) `TfidfVectorizer.fit` on all texts,
   (c) threshold chosen on `X_test`, (d) duplicates removed after `train_test_split`. Pairs find and fix each leak.
3. **Run the noise demo** (`python visualize.py --only leakage`) and change `k=20` to `k=200`.

## 8. Do it yourself

<details><summary>1. Fold scores 0.61, 0.55, 0.58, 0.60, 0.56. Mean ± std, step by step.</summary>

mean = 2.90 / 5 = 0.58 · differences +0.03, −0.03, 0, +0.02, −0.02 · squares 9, 9, 0, 4, 4 (× 0.0001) → mean 5.2 ×
0.0001 = 0.00052 → √ = **0.023** → "0.58 ± 0.02".
</details>

<details><summary>2. Why is the spam vocabulary part of "the model" for leakage?</summary>

It is learned from data (which words exist, how common they are → IDF). If test messages helped build it, the model
already knows their rare words. Fit it on the training split only.
</details>

<details><summary>3. Outer fold 2 chose k = 15, fold 4 chose k = 25. A bug?</summary>

No. Different training rows, and nearby k values score almost the same. The table of choices shows how stable tuning is.
</details>

## 9. In your project

| Project | Where |
|---|---|
| WineGrader | `winegrader/ml/folds.py` → `stratified_kfold` · `data/loader.py` → `drop_exact_duplicates` · `ml/evaluation.py` → `cross_validate`, `nested_cv` · `ml/tuning.py` → `prepare_folds`, `grid_search` · theory `32_WineGrader/01_theory/07_evaluation.md` |
| Spam | `ModelComparator.cross_validate`, `assert_no_leakage` |
| PhishGuard | `ModelTrainer.fit_with_search` (grid search with CV on train only) |

## 🎬 Watch & explore

* StatQuest — *Machine Learning Fundamentals: Cross Validation* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+cross+validation)
* MLU-Explain — [Cross-Validation](https://mlu-explain.github.io/cross-validation/) (interactive)
* scikit-learn — [Nested versus non-nested cross-validation](https://scikit-learn.org/stable/auto_examples/model_selection/plot_nested_cross_validation_iris.html)
