# Lesson 02 — Feature scaling: putting all numbers on the same ruler

> **For:** Seif (WineGrader) · Dani (PhishGuard) · Laith (SVM) · Ryan (pixels) &nbsp;·&nbsp; **Time:** 45 min
> **Before:** Lesson 00 §2, §3, §10; Lesson 01

**In one sentence:** before comparing examples, change every feature so that "1 step" means the same thing for all of
them — otherwise the feature with the biggest numbers wins every comparison.

## The story

> **Sami owns a wine shop.** A customer loved a wine with **10.4 % alcohol** and **140 mg/l of SO₂** (a preservative). It's
> sold out. *"Give me the most similar wine you have,"* she says. Sami asks his computer to find the wine with the closest
> numbers. The computer suggests a wine that tastes completely different. What went wrong?

## Words you need

| word | simple meaning |
|---|---|
| **feature** | one measured number (alcohol, SO₂) |
| **distance** | how different two wines are, using all their numbers (Lesson 00 §10) |
| **scale** | how big a feature's numbers usually are: alcohol ≈ 10, SO₂ ≈ 140 |
| **scaling** | changing the numbers so all features have a similar size |
| **z-score** | "how many typical steps above or below average" |

---

## Step 1 — See the problem

> 📖 Sami has two candidate wines.

```
                 alcohol   SO₂
customer's wine    10.4    140
wine A             10.5    155      ← almost the same alcohol, a bit more SO₂
wine B             13.0    142      ← MUCH stronger, almost the same SO₂
```

Any wine expert says **A** is similar. Let's compute the distance (Pythagoras: square the differences, add, square root):

```
to A:  alcohol 0.1 → 0.1² = 0.01      SO₂ 15 → 15² = 225       √(0.01 + 225) = 15.0
to B:  alcohol 2.6 → 2.6² = 6.76      SO₂ 2  → 2²  = 4         √(6.76 + 4)   =  3.3
```

The computer says **B is closer** (3.3 < 15). Why? SO₂ numbers are **big** (hundreds), so their differences are big and drown
the alcohol. A 15-point SO₂ difference is nothing for taste; a 2.6 % alcohol difference is huge.

![neighbours before and after scaling](figs/neighbours.png)

**Left:** the 7 "nearest" wines using raw numbers all have SO₂ ≈ 140 — and any alcohol at all. Alcohol is ignored.
**Right:** after scaling, the nearest wines are close in **both**.

**Like comparing people by "height in millimetres + age in years":** height (1,700) drowns age (16). A child and a grown-up
of the same height would look like twins.

## Step 2 — The fix: z-score

> 📖 Sami's idea: measure each feature in **its own** typical step. "One step of alcohol" and "one step of SO₂" should mean
> the same thing: "one typical difference".

**In words:** take the value, subtract the average, divide by the standard deviation (Lesson 00 §3).

$$z = \frac{\text{value} - \text{average}}{\text{std}}$$

**By hand — alcohol of 3 wines: 8, 10, 12.**

```
average:      (8 + 10 + 12) ÷ 3 = 10
std:          distances −2, 0, +2 → squares 4, 0, 4 → average 8 ÷ 3 = 2.67 → √2.67 = 1.63
z-scores:     (8 − 10) ÷ 1.63 = −1.22      (10 − 10) ÷ 1.63 = 0      (12 − 10) ÷ 1.63 = +1.22
```

Say it aloud: "wine 1 is 1.2 steps **below** average, wine 2 is average, wine 3 is 1.2 steps **above**".

![z-score in two steps](figs/zscore_steps.gif)

The animation: first **move** the cloud so its centre is 0, then **squeeze** each direction so its spread is 1.

> 📖 After scaling, Sami's computer suggests **wine A**. The customer is happy.

## Step 3 — One rule you must never break

> 📖 A new wine arrives at the shop with 13 % alcohol. Sami scales it with the **same** average (10) and std (1.63) he
> used before: (13 − 10) ÷ 1.63 = **1.84**.

The average and std are **learned from the training wines** and **saved with the model**. Every new wine is scaled with
those saved numbers — never with new ones. (Scaling one wine by itself would mean dividing by a std of 0!)

## Try it yourself

<details><summary>1. Average alcohol 10.5, std 1.2. A wine has 12.3. Its z-score?</summary>

(12.3 − 10.5) ÷ 1.2 = 1.8 ÷ 1.2 = **1.5** → "one and a half steps above average".
</details>

<details><summary>2. z-scores of 4, 6, 8, 10.</summary>

average 7 · distances −3, −1, 1, 3 · squares 9, 1, 1, 9 · average 5 · std √5 = 2.24 → **−1.34, −0.45, 0.45, 1.34**.
</details>

## Common mistakes

| student says | the truth |
|---|---|
| "Scaling changes my data" | It changes how features are compared — that's the point. The order of wines inside one feature stays the same. |
| "Fit the scaler on all the data" | Only on training data, then reuse (Lesson 05: leakage). |

## Class activities

1. **Human comparison (10 min).** 5 "people" on the board as (height cm, age). Who is closest to a new person? Convert to
   z-scores — the answer changes.
2. **Slider (5 min).** `python visualize.py --live`: a slider makes SO₂ count more or less.

## In your project

| Project | Where |
|---|---|
| WineGrader | `winegrader/ml/scaler.py` → `StandardScaler`, `MinMaxScaler` · scaled inside each fold in `tuning.prepare_folds` |
| PhishGuard | `ModelTrainer.build_logistic` — `StandardScaler` inside the `Pipeline` |
| Spam | `SVMClassifier.fit` — `StandardScaler` before the SVM |
| FaceEmotion | pixels: `/255`, then `(x − 0.5013) / 0.2916` (Lesson 19) |

<details><summary>🎓 <b>For the defence (advanced)</b></summary>

* **All 11 features live on different scales:**

  ![feature ranges](figs/ranges.png)

* **Min-max scaling** = (value − min) ÷ (max − min) → everything between 0 and 1. One extreme wine (an **outlier**) breaks
  it: one white wine has 440 SO₂, so every normal wine is squeezed near 0. z-score suffers much less:

  ![one outlier squeezes min-max](figs/outlier.png)

* **Scaling makes learning faster** for models trained by gradient descent (Lesson 12): unscaled → a narrow valley and
  zig-zag steps; scaled → straight to the bottom. That's the SVM's "failed to converge" warning.

  ![gradient descent with and without scaling](figs/gradient_descent.gif)

* **Which models need it?** k-NN, SVM, logistic regression, neural networks — yes. Naive Bayes, decision trees, random
  forests — no (they count or ask "is x > 3?").
* **A feature that is the same for every wine:** std = 0 → set std to 1 (the column becomes zeros and adds nothing).
* Test names: `test_one_outlier_squeezes_minmax_but_not_zscore`, `test_fit_uses_only_given_rows`.
</details>

## 🎬 Watch & explore

* *Feature scaling explained* — [search on YouTube](https://www.youtube.com/results?search_query=feature+scaling+standardization+normalization+machine+learning)
* scikit-learn — [Importance of feature scaling](https://scikit-learn.org/stable/auto_examples/preprocessing/plot_scaling_importance.html)
