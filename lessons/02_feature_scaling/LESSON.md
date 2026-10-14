# Lesson 02 — Feature scaling: making every feature speak the same language

> **For:** Seif (WineGrader — critical) · Dani (PhishGuard) · Laith (SVM) · Ryan (pixels) &nbsp;·&nbsp; **Time:** 45 – 60 min
> **Before:** Lesson 00 §2, §3, §10; Lesson 01 &nbsp;·&nbsp; **After this:** Lessons 12, 14, 15, 19

## The story

> **Sami owns a wine shop.** A customer loved a white wine with **10.4 % alcohol** and **140 mg/l of sulphur dioxide**
> (SO₂ — a preservative). It's sold out. Sami wants the computer to find **the most similar wines** in stock. "Similar"
> means "the numbers are close". But one number is around 10 and the other around 140 — and that turns out to ruin
> everything.

## 🎯 By the end, the student can

1. Explain with a picture why a feature with big numbers "wins" every distance.
2. Compute a z-score and a min-max score by hand, step by step.
3. State the rule: the scaler is learned on the training rows only, and the same numbers are used for every new example.

## Words you need

| word | meaning |
|---|---|
| **feature** | one measured number of an example (alcohol, SO₂) — Lesson 01 |
| **distance** | how far apart two examples are, using all their numbers — Pythagoras, Lesson 00 §10 |
| **scale (of a feature)** | the typical size of its numbers: alcohol ≈ 8–14, SO₂ ≈ 10–440 |
| **scaling** | changing every feature so they all have a similar size |
| **mean** | the average — Lesson 00 §2 |
| **standard deviation (std)** | the typical distance from the average — Lesson 00 §3 |
| **z-score** | (value − mean) / std: "how many typical steps above or below average" |
| **min-max scaling** | (value − min) / (max − min): squeeze everything into 0 … 1 |

---

## 1. Why the big numbers win

Two wines in Sami's shop, compared with the customer's wine (10.4 %, 140):

```
                 alcohol   SO₂
customer's wine    10.4    140
wine A             10.5    155        ← almost the same alcohol, SO₂ a bit higher
wine B             13.0    142        ← very different alcohol (much stronger), SO₂ almost the same
```

Distance = Pythagoras (Lesson 00 §10): square each difference, add, take the root.

```
to wine A:   alcohol difference 10.5 − 10.4 = 0.1   → squared 0.01
             SO₂ difference     155 − 140   = 15    → squared 225
             distance = √(0.01 + 225) = √225.01 = 15.0

to wine B:   alcohol difference 13.0 − 10.4 = 2.6   → squared 6.76
             SO₂ difference     142 − 140   = 2     → squared 4
             distance = √(6.76 + 4) = √10.76 = 3.3
```

The computer says **wine B is much closer** (3.3 < 15.0). But any wine expert says the opposite: 13 % vs 10.4 % alcohol
is a *huge* difference in taste, while 155 vs 140 SO₂ is nothing. The computer is fooled because **SO₂ numbers are
big**, so their differences are big, so they dominate the sum.

![feature ranges](figs/ranges.png)

The 11 wine features live on completely different scales: density changes by 0.001, SO₂ by hundreds.

![neighbours before and after scaling](figs/neighbours.png)

**Left:** the 7 "nearest" wines to the star using raw numbers form a flat **band**: all have SO₂ ≈ 140, and their
alcohol is anything from 8.8 to 11.7 — **alcohol is ignored**. **Right:** after scaling, the neighbours are close in
**both** features.

**Analogy:** compare people by "height in millimetres + age in years". Height (1,700 mm) drowns age (16 years): a
2-year-old and a 60-year-old of the same height look like twins.

## 2. The fix: z-score, step by step

The idea: measure every feature in **its own typical step**. "One step" of alcohol is its standard deviation; "one step"
of SO₂ is *its* standard deviation. Then 1 means the same thing for every feature: "one typical step away from average".

$$z = \frac{\text{value} - \text{mean}}{\text{std}}$$

**Example — alcohol of 3 training wines: 8, 10, 12.**

```
step 1  mean:                 (8 + 10 + 12) / 3 = 30 / 3 = 10
step 2  differences:          8 − 10 = −2      10 − 10 = 0      12 − 10 = +2
step 3  squares:              4                0                4
step 4  average of squares:   (4 + 0 + 4) / 3 = 8 / 3 = 2.667
step 5  std = √2.667 =        1.633
step 6  z-scores:             (8 − 10) / 1.633  = −1.22
                              (10 − 10) / 1.633 =  0
                              (12 − 10) / 1.633 = +1.22
```

Read them aloud: "wine 1 is 1.22 steps **below** average, wine 2 is exactly average, wine 3 is 1.22 steps **above**".

**A new wine arrives with 13 % alcohol.** We use the **training** mean and std (10 and 1.633), not new ones:
z = (13 − 10) / 1.633 = 3 / 1.633 = **1.84**.

![z-score in two steps](figs/zscore_steps.gif)

The animation shows what z-score does to the cloud of wines: first **slide** it so the centre is at 0 (subtract the
mean), then **squeeze or stretch** each direction so the spread is 1 (divide by the std). Who is close to whom *inside*
one feature does not change — only the units.

### Sami's wines again, scaled

Say for SO₂ the training mean is 138 and the std is 42; for alcohol mean 10.5, std 1.2.

```
customer:  alcohol (10.4 − 10.5)/1.2 = −0.08     SO₂ (140 − 138)/42 = 0.05
wine A:    alcohol (10.5 − 10.5)/1.2 =  0.00     SO₂ (155 − 138)/42 = 0.40
wine B:    alcohol (13.0 − 10.5)/1.2 =  2.08     SO₂ (142 − 138)/42 = 0.10

distance to A = √((0.00+0.08)² + (0.40−0.05)²) = √(0.0064 + 0.1225) = √0.129 = 0.36
distance to B = √((2.08+0.08)² + (0.10−0.05)²) = √(4.67 + 0.0025)   = √4.67  = 2.16
```

Now wine A is the nearest — the right answer.

## 3. The other way: min-max, and why one outlier breaks it

$$\text{minmax} = \frac{\text{value} - \min}{\max - \min}$$

Alcohol 8, 10, 12 → (8−8)/(12−8) = 0, (10−8)/4 = 0.5, (12−8)/4 = 1. Simple: everything between 0 and 1.

![one outlier squeezes min-max](figs/outlier.png)

But one white wine has 440 mg/l SO₂ (most have 50–200). The maximum is now 440, so every *normal* wine is squeezed into
the bottom part of 0 … 1 and their differences become tiny. An unusual value like this is called an **outlier**. z-score
is hurt much less. Seif's project tries both; the tuning table decides (`test_one_outlier_squeezes_minmax_but_not_zscore`).

## 4. Scaling also makes learning faster

![gradient descent with and without scaling](figs/gradient_descent.gif)

Some models learn by taking small steps **downhill** (gradient descent — Lesson 00 §9, Lesson 12). With unscaled
features the "valley" is long and narrow: steps that are safe in the steep direction are tiny in the flat one, so the
model zig-zags and crawls (left). Scaled features make the valley round: it walks straight to the bottom (right). That's
why Laith's SVM needs `StandardScaler` and otherwise warns "failed to converge".

## 5. THE rule

The mean and std are **learned from data** → they are part of the model → they come from the **training rows only** →
they are **saved with the model** and used again for every new wine at the shop.

```python
# RIGHT                                         # WRONG - the test rows helped build the scaler
scaler = StandardScaler().fit(X_train)          Z = StandardScaler().fit_transform(X_all)
Xtr = scaler.transform(X_train)                 Xtr, Xte = Z[train], Z[test]
Xte = scaler.transform(X_test)   # TRAINING numbers
```

## 6. Which models need it?

| needs scaling | doesn't |
|---|---|
| k-NN (distances) · SVM (distances/margins) · logistic regression and neural networks (gradient descent) | Naive Bayes (counts words) · decision trees / random forest (only ask "is x > 3?") |

## 7. Common mistakes

| student says | the truth |
|---|---|
| "Scaling changes my data, so it changes the answer" | It changes how features are **compared** — exactly the point. Inside one feature the order of the wines stays the same. |
| "Fit the scaler on everything, it's just an average" | Leakage. Small, but real — and tests catch it. |
| "At the shop I'll scale the one new wine by itself" | The std of one number is 0 → division by zero. Use the saved training numbers. |

## 8. Activities

1. **Human k-NN (10 min).** Write 5 "people" as (height in cm, age in years). Who is closest to a new person? Convert to
   z-scores together and ask again — the answer changes.
2. **Slider (5 min).** `python visualize.py --live`: a slider multiplies SO₂'s importance. At 0 SO₂ is ignored; at 3 it
   dominates again. (This is Seif's "feature weights", Lesson 17.)

## 9. Do it yourself

<details><summary>1. Training alcohol: mean 10.5, std 1.2. A new wine has 12.3. Its z-score? Say it in words.</summary>

(12.3 − 10.5) / 1.2 = 1.8 / 1.2 = **1.5** → "one and a half typical steps above average".
</details>

<details><summary>2. z-score of 4, 6, 8, 10 (compute mean and std first).</summary>

mean 7 · differences −3, −1, 1, 3 · squares 9, 1, 1, 9 · average 5 · std √5 = 2.236 → z = −1.34, −0.45, 0.45, 1.34.
</details>

<details><summary>3. Min-max of 20, 50, 80, 200.</summary>

min 20, max 200, range 180 → 0, 0.17, 0.33, 1. (See how 200 squeezes the others.)
</details>

<details><summary>4. A feature is the same for every training wine. What breaks, and what is the fix?</summary>

std = 0 → division by zero. Set std to 1: the column becomes zeros and adds nothing to any distance — correct, it carries
no information.
</details>

## 10. In your project

| Project | Where |
|---|---|
| WineGrader | `winegrader/ml/scaler.py` → `StandardScaler.fit/transform/inverse_transform`, `MinMaxScaler`, `scaler_from_dict` · `tuning.prepare_folds` scales inside every fold · theory `32_WineGrader/01_theory/03_data_scaling.md` |
| PhishGuard | `ModelTrainer.build_logistic` — `StandardScaler` inside the `Pipeline`, fitted on train only, saved in the bundle |
| Spam | `SVMClassifier.fit` — `make_pipeline(StandardScaler(), LinearSVC(...))` |
| FaceEmotion | pixels: `/255`, then `(x − 0.5013) / 0.2916` (Lesson 19) |

## 🎬 Watch & explore

* *Feature scaling: standardization vs normalization* — [search on YouTube](https://www.youtube.com/results?search_query=feature+scaling+standardization+normalization+machine+learning)
* scikit-learn — [Importance of feature scaling](https://scikit-learn.org/stable/auto_examples/preprocessing/plot_scaling_importance.html)
