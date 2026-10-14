# Lesson 14 — The SVM, calibration, and comparing two models honestly

> **For:** Laith (SpamClassifier stage 5) &nbsp;·&nbsp; **Time:** 45 min
> **Before:** Lessons 02, 04, 05, 11 &nbsp;·&nbsp; **After this:** the comparison chapter of Laith's book

## 🎯 By the end, the student can

1. Explain the SVM as "the widest street between the classes", and what support vectors are.
2. Explain the `C` parameter with the animation.
3. Explain why a raw SVM output is not a probability, and what Platt calibration does.
4. Compare NB and the SVM **fairly** (same split, same threshold rule) and explain why NB stays the primary model.

---

## 1. The widest street

![maximum margin](figs/margin.png)

Many lines separate the training data. The SVM chooses the one with the **largest margin** — the widest "street" with no
points inside. Intuition: a line far from both classes is the safest bet for new points.

Only the points on the edge of the street — the **support vectors** — decide where the line is. All the others could
move (without crossing the street) and nothing would change.

## 2. Real data is not separable — the C parameter

![C sweep](figs/C_sweep.gif)

Real classes overlap, so some points must be inside the street or on the wrong side. `C` is the price of each mistake:

| C | street | training mistakes | risk |
|---|---|---|---|
| small | wide | many allowed | underfitting, very stable |
| large | narrow | few allowed | overfitting to noise |

Choose `C` by **grid search inside cross-validation** (Lesson 05) — never on the test set.

## 3. Generative vs discriminative

| | Naive Bayes | SVM |
|---|---|---|
| learns | how each class **generates** words (P(w \| c)) | only **where the boundary is** |
| training | counting, one pass | optimisation |
| needs scaling | no (counts) | **yes** — `StandardScaler` first (the 7 handcrafted features would otherwise dominate) |
| explanation | exact: each word's log-odds | approximate after calibration |

## 4. Calibration — from distance to probability

![calibration](figs/calibration.png)

`LinearSVC` returns a **signed distance** from the line ("2.3 = well inside the spam side") — not a probability, and not
comparable to NB's 0.94. **Platt scaling** fits a sigmoid (a 1-feature logistic regression, Lesson 12) from distance to
label, on held-out folds:

```python
base = make_pipeline(StandardScaler(), LinearSVC(C=self.c, random_state=config.RANDOM_SEED))
self._model = CalibratedClassifierCV(base, method="sigmoid", cv=5)
```

Right panel: Naive Bayes' probabilities are almost only 0 or 1 (the naive assumption multiplies evidence as if it were
independent → overconfident). The calibrated SVM uses the whole range. **Both rank well; only calibrated numbers can share
a threshold.**

## 5. The fair comparison

![precision-recall comparison](figs/pr_compare.png)

Same validation split, same rule (precision ≥ 0.98, best recall — Lesson 04). In this quick run the two are almost equal
(recall ≈ 0.89 vs 0.88). **Fair** means: same data split, same preprocessing, the scaler and `C` chosen inside CV, both
calibrated, one threshold rule. Report the numbers on the test set once.

**Why NB stays primary** even if the SVM were a little better: the project requires an exact reason for every verdict.
NB's explanation *is* the model; the SVM's, after calibration, is an approximation.

## 6. Misconceptions

| Student says | Truth |
|---|---|
| "The SVM gives a probability" | It gives a distance. Calibration makes a probability. |
| "Higher C is always better — fewer training errors" | Fewer *training* errors; often more test errors. |
| "Calibration changes which messages are spam" | It is monotonic: the ranking is unchanged. It changes the numbers, so a shared threshold makes sense. |
| "Comparing on different splits is fine" | Then you compare luck, not models. |

## 7. Activities

1. **The street (10 min).** Coloured counters on a table (two colours). Students lay a ruler as the "line" and two pencils
   as the street edges; widest street wins. Which counters touch the pencils? (support vectors)
2. **Predict-then-run (5 min).** "What happens to the street when C grows?" — then play the GIF.
3. **Weather forecaster (5 min).** "70 % rain" — on how many of those days should it rain? That's calibration.

## 8. Check yourself

<details><summary>1. Remove a point that is NOT a support vector and retrain. What changes?</summary>

Nothing. The solution depends only on the support vectors.
</details>

<details><summary>2. Why does the SVM need StandardScaler but Naive Bayes doesn't?</summary>

The SVM measures distances/margins in feature space, so a feature with large numbers (`message_length` in the thousands)
would dominate. NB multiplies per-word probabilities from counts — no distances.
</details>

<details><summary>3. Why `CalibratedClassifierCV(..., cv=5)` and not calibrate on the training predictions?</summary>

On its own training data the SVM is overconfident; the sigmoid would learn that. Held-out folds give honest distances.
</details>

## 9. In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/ml/svm_classifier.py` → `SVMClassifier.fit`, `predict_proba`, `predict`, `explain` · `ml/comparator.py` → `ModelComparator.cross_validate`, `compare` · views `compare_view.py` (`draw_curves`) · theory `08_SpamClassifier/01_theory/05_svm_comparison.md` · notebook `03_compare_and_threshold.ipynb` |

## 🎬 Watch & explore

* StatQuest — *Support Vector Machines Part 1 (of 3): Main Ideas* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+support+vector+machines+main+ideas)
* MIT 6.034 (Patrick Winston) — *Learning: Support Vector Machines* — [search on YouTube](https://www.youtube.com/results?search_query=MIT+6.034+support+vector+machines+Winston)
* scikit-learn — [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html)
