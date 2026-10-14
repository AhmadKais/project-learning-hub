# Lesson 02 — Feature scaling: making every feature speak the same language

> **For:** Seif (WineGrader — critical) · Dani (PhishGuard) · Laith (SVM) · Ryan (pixel normalisation) &nbsp;·&nbsp; **Time:** 45 min
> **Before:** Lesson 01 &nbsp;·&nbsp; **After this:** Lessons 12 (logistic regression), 14 (SVM), 15 (k-NN), 19 (images)

## 🎯 By the end, the student can

1. Explain with a picture why an unscaled feature with big numbers "wins" every distance.
2. Compute a z-score and a min-max score by hand, and say which one an outlier breaks.
3. State **the rule**: fit the scaler on the training rows only, then use the same numbers for everything else.

---

## 1. The problem in one picture

![feature ranges](figs/ranges.png)

Wine features: alcohol is 8 – 14, density is 0.99 – 1.04, total SO₂ is 9 – 440. A distance just adds the
differences up, so a difference of 50 in SO₂ (ordinary) completely drowns a difference of 3 % alcohol (huge).

![nearest neighbours before and after scaling](figs/neighbours.png)

**Left:** the 7 "nearest" wines to the blue star, using raw numbers. They are all at SO₂ ≈ 140, and their
alcohol is anything from 8.8 to 11.7 — **alcohol is ignored**. **Right:** after scaling, the neighbours are close
in *both* features.

**Analogy:** comparing two people by "height in millimetres + age in years". Height decides everything; a
2-year-old and a 60-year-old of the same height look like twins.

## 2. Definitions

| Name | Formula | After it | Breaks when |
|---|---|---|---|
| **z-score** (standardisation) | $z = \dfrac{x - \text{mean}}{\text{std}}$ | mean 0, std 1 — "how many typical steps away from average" | std = 0 (constant feature → set std to 1) |
| **min-max** | $z = \dfrac{x - \min}{\max - \min}$ | everything in [0, 1] | one outlier squeezes everyone else |

## 3. Watch z-score happen

![z-score in two steps](figs/zscore_steps.gif)

Two moves, nothing else: **slide** the cloud so its centre is at 0 (subtract the mean), then **squeeze/stretch**
each axis so its spread is 1 (divide by the std). The shape of the cloud — who is close to whom *inside each
feature* — does not change.

## 4. By hand (do it on the board)

Alcohol of three training wines: **8, 10, 12**.

```
mean = (8 + 10 + 12) / 3 = 10
std  = sqrt( ((8-10)² + (10-10)² + (12-10)²) / 3 ) = sqrt(8/3) = 1.633     (numpy's np.std, ddof = 0)

z(8)  = (8 - 10) / 1.633  = -1.22
z(10) = 0
z(12) = +1.22

min-max:  (8-8)/(12-8) = 0     (10-8)/4 = 0.5     (12-8)/4 = 1
```

A **new** wine with alcohol 13 arrives → z = (13 − 10) / 1.633 = **1.84** using the **training** mean and std.
Min-max gives (13 − 8) / 4 = 1.25 — outside [0, 1], and that is fine.

## 5. Outliers: why WineGrader prefers z-score

![one outlier squeezes min-max](figs/outlier.png)

One white wine has 440 mg/l SO₂. With min-max that wine is 1.0 and the other 4,897 wines are pressed into
the bottom part of the range, so their differences become tiny. z-score is hurt much less. (Both are in Seif's
hyper-parameter search; the tuning table decides — `test_one_outlier_squeezes_minmax_but_not_zscore`.)

## 6. Scaling also makes learning faster

![gradient descent with and without scaling](figs/gradient_descent.gif)

For models trained with **gradient descent** (logistic regression, SVM, neural networks): unscaled features make
the error surface a long narrow valley. The step that is safe for the steep direction is far too small for the flat
one, so the optimiser zig-zags and crawls. Scaled features make the valley round — it walks straight down.
That is what `LinearSVC` means when it warns *"failed to converge"* (Laith, `StandardScaler` before the SVM).

## 7. THE rule (the one examiners ask about)

```python
# RIGHT                                         # WRONG - leaks the test rows into the model
scaler = StandardScaler().fit(X_train)          Z = StandardScaler().fit_transform(X_all)
Xtr = scaler.transform(X_train)                 Xtr, Xte = Z[train], Z[test]
Xte = scaler.transform(X_test)   # TRAIN numbers
```

The mean and std are **learned** → they are part of the model → they come from the training rows only → they
are **saved with the model** and used again for every new example in the app.

## 8. Misconceptions

| Student says | Truth |
|---|---|
| "Scaling changes my data, so it changes the answer" | It changes *distances between features*, which is exactly the point. Inside one feature the order of the wines is unchanged. |
| "Naive Bayes / random forest also need scaling" | No. NB counts words; a tree asks "is x > 3?" — scaling moves the threshold, not the split. Only distance- and gradient-based models need it. |
| "Fit the scaler on everything, it's just a mean" | Leakage. Small, but real — and there are tests that catch it. |
| "At prediction time I'll scale the one new example by itself" | The std of one value is 0. Use the saved training numbers. |

## 9. Activities

1. **Human k-NN (10 min).** Write 5 "people" on the board as (height cm, age years). Ask who is closest to a new
   person. Then convert to z-scores together and ask again — the answer changes.
2. **Slider (5 min).** `python visualize.py --live` — the slider multiplies SO₂ by a weight. At 0 SO₂ is
   ignored; at 3 it dominates again. This is also the idea behind Seif's **feature weights** (Lesson 17).

## 10. Check yourself

<details><summary>1. Training alcohol: mean 10.5, std 1.2. A new wine has 12.3. Its z-score?</summary>

(12.3 − 10.5) / 1.2 = **1.5** — one and a half typical steps above average.
</details>

<details><summary>2. Why does a random forest not care about scaling?</summary>

Every split is a question "feature ≤ threshold?". Scaling is a monotonic change of the axis, so the same
examples go left and right — only the threshold number changes.
</details>

<details><summary>3. A feature is the same for every training wine. What does the z-score do, and what should it do?</summary>

std = 0 → division by zero. Set std to 1: the column becomes all zeros and adds nothing to any distance — right,
because it carries no information.
</details>

## 11. In your project

| Project | Where |
|---|---|
| WineGrader | `winegrader/ml/scaler.py` → `StandardScaler.fit/transform/inverse_transform`, `MinMaxScaler`, `scaler_from_dict` · `tuning.prepare_folds` scales inside every fold · theory `32_WineGrader/01_theory/03_data_scaling.md` |
| PhishGuard | `ModelTrainer.build_logistic` — `StandardScaler` inside the `Pipeline`, so it is fitted on train only and saved in the bundle |
| Spam | `SVMClassifier.fit` — `make_pipeline(StandardScaler(), LinearSVC(...))` |
| FaceEmotion | pixels: `/255`, then `(x − 0.5013) / 0.2916` (the dataset's mean/std, Lesson 19) |

## 🎬 Watch & explore

* StatQuest — *Standardization vs Normalization* — [search on YouTube](https://www.youtube.com/results?search_query=feature+scaling+standardization+normalization+machine+learning)
* Andrew Ng — *Feature scaling (gradient descent in practice)* — [search on YouTube](https://www.youtube.com/results?search_query=Andrew+Ng+feature+scaling+gradient+descent)
* scikit-learn — [Importance of feature scaling](https://scikit-learn.org/stable/auto_examples/preprocessing/plot_scaling_importance.html)
