# Lesson 14 — The SVM: the widest street between two classes (and how to get a probability out of it)

> **For:** Laith (SpamClassifier stage 5) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lessons 02, 04, 05, 11, 12 &nbsp;·&nbsp; **After this:** the comparison chapter of Laith's book

## The story

> A farmer has sheep on one side of a field and goats on the other, and wants to build a **straight fence** between them.
> Many fences would separate today's animals. But tomorrow the animals move a little. The wise farmer builds the fence
> **as far as possible from both flocks** — in the middle of the widest empty strip. That fence is the most likely to stay
> correct tomorrow. The **SVM** (support vector machine) builds exactly that fence between spam and ham — in thousands of
> dimensions instead of a field.

## 🎯 By the end, the student can

1. Explain the SVM as "the widest street", and what support vectors are.
2. Explain the C parameter with the animation.
3. Explain why the SVM's output is a distance, not a probability, and what calibration does.
4. Explain why Laith compares the SVM with Naive Bayes, and why NB stays the main model.

## Words you need

| word | meaning |
|---|---|
| **boundary / fence** | the line (in many dimensions: a flat sheet) that separates the classes |
| **margin / street** | the empty strip on both sides of the fence |
| **support vectors** | the examples standing right at the edge of the street — they alone decide where the fence goes |
| **C** | how expensive a mistake (an example inside the street or on the wrong side) is |
| **signed distance** | the SVM's output: how far an example is from the fence, + on the spam side, − on the ham side |
| **calibration** | turning a score into a probability you can trust: when it says 70 %, it's right 70 % of the time |
| **Platt scaling** | a calibration method: fit a sigmoid (Lesson 12) from distance to label |

---

## 1. Many fences — which one?

![maximum margin](figs/margin.png)

Left: four different lines all separate today's examples perfectly. Right: the SVM's choice — the line in the middle of
the **widest street** (yellow). Only the circled examples, the **support vectors**, touch the edges of the street. Move any
other example (without crossing the street) and the fence doesn't move at all.

The width of the street is 2 / |w| (|w| = the length of the weight vector, Lesson 00 §10) — so "widest street" =
"smallest weights", the same idea as the regularisation brake of Lesson 12.

## 2. Real data overlaps — the C knob

Real spam and ham are mixed near the middle: no fence separates them perfectly. So the SVM allows some examples inside
the street or on the wrong side, and charges a price **C** for each.

![C sweep](figs/C_sweep.gif)

| C | the SVM thinks | street | risk |
|---|---|---|---|
| small (0.003) | "mistakes are cheap, I want a wide street" | wide, many support vectors | underfitting |
| large (100) | "mistakes are expensive" | narrow, bends to every example | overfitting |

C is chosen by cross-validation (Lesson 05), never on the test set.

## 3. Naive Bayes vs SVM — two different ways of thinking

| | Naive Bayes (Lesson 11) | SVM |
|---|---|---|
| learns | how each class **writes**: which words, how often | only **where the fence is** |
| training | counting, one pass | an optimisation that searches for the widest street |
| needs scaling | no (it counts) | **yes** — `StandardScaler` first, or `message_length` (thousands) dominates every distance (Lesson 02) |
| explanation | exact: each word's log-odds | only approximate |

## 4. Distance is not a probability — calibration

`LinearSVC` returns a **signed distance**: +2.3 = "deep on the spam side", −1.1 = "on the ham side". That is not 2.3 %
or 2.3 anything — and it can't be compared with NB's "92 %". To use one shared threshold (Lesson 04), both models must speak
**probability**.

![calibration](figs/calibration.png)

**Platt scaling (left):** take many held-out messages; for each we know the distance and the truth (0 or 1). Fit an
S-curve (a sigmoid, Lesson 12) through them: p = σ(A × distance + B). On the SMS data: p = σ(6.7 × distance + 1.3).

```
a message at distance 0      → σ(1.3)  = 0.79
a message at distance −0.5   → σ(−2.05) = 0.11
a message at distance +0.5   → σ(4.65) = 0.99
```

In Laith's code:

```python
base = make_pipeline(StandardScaler(), LinearSVC(C=self.c, random_state=config.RANDOM_SEED))
self._model = CalibratedClassifierCV(base, method="sigmoid", cv=5)    # sigmoid = Platt scaling
```

`cv=5` means the S-curve is fitted on messages the SVM didn't train on — on its own training data the SVM is
over-confident.

**Right panel:** Naive Bayes' probabilities are almost only 0 or 1 (it multiplies the evidence of every word as if they
were independent → over-confident). The calibrated SVM uses the whole range. **Analogy:** a weather forecaster who says
"0 % or 100 %" every day vs. one who says "30 %" when unsure — the second can be trusted.

## 5. The fair comparison

![precision-recall comparison](figs/pr_compare.png)

Same validation SMS, same rule (precision ≥ 0.98, best recall — Lesson 04): NB catches 89 % of spam, the SVM 88 % — almost
the same. **Fair** means: the same split, the same cleaning, scaler and C chosen inside CV, both calibrated, one rule.

**Why NB stays Laith's main model** even if the SVM were a little better: the project requires an **exact reason** for
every verdict. In NB the reason *is* the model; after calibration, the SVM's reason is only an approximation.

## 6. Common mistakes

| student says | the truth |
|---|---|
| "The SVM gives a probability" | It gives a distance. Calibration makes a probability. |
| "Higher C is better — fewer training errors" | Fewer *training* errors, often more test errors. |
| "Calibration changes which messages are spam" | It keeps the order; it only changes the numbers, so one threshold works for both models. |

## 7. Activities

1. **The fence (10 min).** Two colours of counters on a table. Pairs lay a ruler (the fence) and two pencils (the street
   edges). Widest street wins. Which counters touch the pencils? (support vectors)
2. **Predict, then watch (5 min).** "What happens to the street as C grows?" — then play the GIF.
3. **The forecaster (5 min).** On which share of "70 % rain" days should it rain? That's calibration.

## 8. Do it yourself

<details><summary>1. Remove an example that is NOT a support vector and retrain. What changes?</summary>

Nothing. The fence depends only on the support vectors.
</details>

<details><summary>2. With p = σ(6.7 × d + 1.3), which distance gives exactly 50 %?</summary>

σ(z) = 0.5 when z = 0 → 6.7 d + 1.3 = 0 → d = −1.3 / 6.7 = **−0.19**.
</details>

<details><summary>3. Why does the SVM need scaling and Naive Bayes doesn't?</summary>

The SVM measures distances to the fence, so a feature in the thousands dominates. NB multiplies per-word probabilities
from counts — no distances.
</details>

## 9. In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/ml/svm_classifier.py` → `fit`, `predict_proba`, `predict`, `explain` · `ml/comparator.py` → `cross_validate`, `compare` · `views/compare_view.py` → `draw_curves` · theory `08_SpamClassifier/01_theory/05_svm_comparison.md` · notebook `03_compare_and_threshold.ipynb` |

## 🎬 Watch & explore

* StatQuest — *Support Vector Machines Part 1: Main Ideas* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+support+vector+machines+main+ideas)
* MIT 6.034 (Patrick Winston) — *Support Vector Machines* — [search on YouTube](https://www.youtube.com/results?search_query=MIT+6.034+support+vector+machines+Winston)
* scikit-learn — [Probability calibration](https://scikit-learn.org/stable/modules/calibration.html)
