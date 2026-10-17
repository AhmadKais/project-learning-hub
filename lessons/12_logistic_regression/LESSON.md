# Lesson 12 — Logistic regression: a points system that learns its own points

> **For:** Dani (PhishGuard — first model, explanations) · the gradient-descent part also for Ryan (Lesson 21)
> **Time:** 3 × 45 min &nbsp;·&nbsp; **Before:** Lesson 00 §5, §7, §8, §9; Lessons 02, 03, 18 &nbsp;·&nbsp; **After this:** Lessons 13, 21

**In one sentence:** give every warning sign some points, add them up, squash the total into a probability with the
sigmoid — and let the computer find the best points by walking downhill on its mistakes.

## 🗺️ The map of this lesson

```mermaid
flowchart LR
    X["features x<br/>(Lesson 18)"] --> Z["1 · points:<br/>z = Σ w·x + b"]
    Z --> S["2 · sigmoid:<br/>p = σ(z)"]
    S --> LO["3 · loss:<br/>how wrong?"]
    LO --> G["4 · gradient descent:<br/>fix the points"]
    G -->|repeat| Z
    G --> R["5 · brake (C)<br/>6 · scaling"]
```

## The story

> Rana at the bank (Lesson 04) used to judge links by experience: *"An @ in the address? Suspicious. The word 'paypal'
> before the real domain? Very suspicious. HTTPS? A bit more trustworthy."* Her manager asks her to write it down as a
> **points system**: each warning sign gets points, add them up, and decide. Rana writes one — but how many points should
> each sign get? She guesses. **Logistic regression is a points system that learns the best points from thousands of
> examples**, and then turns the total into a probability.

### 🌍 Points systems are everywhere

![points systems in everyday life](figs/points_world.png)

Banks, insurance companies, universities and doctors all use **points systems**: each fact about you gets some points, the
total decides. Many of them are, in fact, logistic regressions whose points were learned from past data. Dani's PhishGuard
is one more.

## Words you need

| word | meaning | Rana's version |
|---|---|---|
| **feature x** | one number about the link (Lesson 18) | has_at_symbol = 1 |
| **weight w** | the points that feature is worth; can be negative | @ is worth +0.8 |
| **bias b** | the starting points, before looking at any feature | everyone starts at −1.0 |
| **z** | the total: Σ wᵢ·xᵢ + b — any number | |
| **sigmoid σ(z)** | the S-curve that turns any number into a probability 0 … 1 | |
| **p** | the predicted probability of phishing | 0.76 |
| **y (truth)** | 1 = phishing, 0 = legitimate | |
| **loss** | a number that measures how wrong one prediction was | |
| **training** | finding the weights with the smallest total loss | |
| **gradient descent** | improving the weights by small steps "downhill" on the loss (Lesson 00 §9) | |
| **learning rate (lr)** | how big each step is | |

---

## 1. Step 1: add up the points

Rana's first guess of the points (invented weights — the real ones are learned in §4):

| feature | weight |
|---|---|
| has_at_symbol (an @ in the URL) | +0.8 |
| brand_in_subdomain ("paypal" before the real domain) | +1.2 |
| has_https | −1.5 (HTTPS lowers suspicion) |
| num_dots | +0.05 per dot |
| bias (start) | −1.0 |

$$z = w_1x_1 + w_2x_2 + w_3x_3 + w_4x_4 + b$$

**URL A: `http://paypal.com.secure-login.xyz/verify`** → has_at 0, brand 1, https 0, dots 3:

```
z = 0.8×0 + 1.2×1 + (−1.5)×0 + 0.05×3 + (−1.0)
  = 0     + 1.2   + 0        + 0.15   − 1.0
  = 0.35
```

**URL B: `https://www.google.com/`** → has_at 0, brand 0, https 1, dots 2:

```
z = 0 + 0 + (−1.5)×1 + 0.05×2 − 1.0 = −1.5 + 0.10 − 1.0 = −2.40
```

Positive z leans phishing, negative leans legitimate. But "0.35" isn't a probability yet.

![contributions](figs/contributions.png)

Each bar is weight × value — the explanation PhishGuard shows: "this URL was flagged mostly because of a brand name in
the subdomain".

## 2. Step 2: squash into a probability — the sigmoid

$$p = \sigma(z) = \frac{1}{1+e^{-z}}$$

(e ≈ 2.718 — Lesson 00 §8. The calculator has an eˣ button.)

```
URL A:  z = 0.35   →  e^(−0.35) = 0.705   →  1 / (1 + 0.705) = 1 / 1.705 = 0.59    → 59 % phishing
URL B:  z = −2.40  →  e^(2.40)  = 11.02   →  1 / (1 + 11.02) = 1 / 12.02 = 0.083   → 8 % phishing
```

![sigmoid](figs/sigmoid.png)

What the sigmoid does: very negative z → close to 0; z = 0 → exactly 0.5; very positive z → close to 1. It never goes
below 0 or above 1 — exactly what a probability needs. Watch a total travel along the curve:

![the sigmoid as a machine](figs/sigmoid_walk.gif)

Think of it as a **dimmer switch**: far to the left the light is off (0), far to the right fully on (1), and in the middle
it changes smoothly. Doubling the points near 0 changes p a lot; doubling 10 into 20 changes almost nothing (already sure).

## 3. How wrong was it? The log-loss

To learn good weights, the computer needs a number for "how wrong". For one example:

```
if the truth is phishing (y = 1):    loss = −ln(p)          ← p should be close to 1
if the truth is legitimate (y = 0):  loss = −ln(1 − p)      ← p should be close to 0
```

```
phishing, model said p = 0.76:   −ln(0.76) = 0.27     (fairly right → small loss)
phishing, model said p = 0.10:   −ln(0.10) = 2.30     (confident and WRONG → big loss)
legitimate, model said p = 0.08: −ln(0.92) = 0.08     (right)
```

![log-loss](figs/logloss.png)

The curve shoots up near the wrong end: **confident mistakes are punished hard**. The total loss = the average over all
training URLs. **Training = finding the weights that make this average as small as possible.**

## 4. How the weights are learned — gradient descent

Imagine the loss as a landscape: every possible set of weights is a place, its height is the loss. We start somewhere
random and **walk downhill** (Lesson 00 §9):

$$w_{\text{new}} = w - \text{lr}\times\text{slope}$$

![learning rate](figs/gd_1d.png)

The step size (lr) matters: too small → crawls; good → arrives; too big → jumps over the bottom and gets worse. Watch three
marbles race from the same place:

![three learning rates race downhill](figs/lr_race.gif)

For logistic regression, the slope for each weight has a beautifully simple form — **error × input**:

$$\text{slope for } w_i = (p - y)\times x_i \qquad\text{slope for } b = p - y$$

### One step by hand

One training URL: x = (has_at = 1, brand = 0). Truth y = 1 (phishing). Start: w = (0, 0), b = 0, lr = 0.5.

```
1. z = 0×1 + 0×0 + 0 = 0
2. p = σ(0) = 0.5                       (no idea yet)
3. error = p − y = 0.5 − 1 = −0.5        (it said too little)
4. slopes:  w₁: −0.5 × 1 = −0.5    w₂: −0.5 × 0 = 0    b: −0.5
5. update:  w₁ = 0 − 0.5 × (−0.5) = +0.25
            w₂ = 0 − 0.5 × 0      = 0          (feature was 0: not involved, not changed)
            b  = 0 − 0.5 × (−0.5) = +0.25
6. check:   z = 0.25 × 1 + 0.25 = 0.5  →  p = σ(0.5) = 0.62    (closer to the truth 1 ✓)
```

Read step 5 in words: *"the model said too little for a phishing URL, so the weights of the features this URL has go
**up**"*. Repeat for thousands of URLs, hundreds of times.

### Watch it learn, on 500 real PhishGuard URLs

![gradient descent learning the boundary](figs/gd_boundary.gif)

Two features only (digit ratio, URL length), so we can draw it. Left: the black line is where p = 0.5; it turns step by
step. Right: the average loss falls. (Two features can't separate the classes well — the real model uses all 20.)

```python
for epoch in range(2000):
    p = sigmoid(X @ w + b)
    w -= lr * X.T @ (p - y) / len(y)      # average of "error × input"
    b -= lr * (p - y).mean()
```

### The points it really learned

On all 20 PhishGuard features (scaled first, Part 6), trained on 70 % of the real URLs:

![the real learned weights](figs/real_weights.png)

Long URLs, an "@", suspicious words and many digits push towards phishing; HTTPS pushes (a little) towards legitimate. Some
weights look surprising (many hyphens → legitimate?). That happens when features are **correlated**: url_length already
counts the hyphens, so the hyphen weight "corrects" it. Read single weights carefully — and say so in the defence.

The accuracy, 77 %, is honest: telling phishing from real URLs by the text of the URL alone is **hard**. Lesson 13's trees
do better.

## 5. Regularisation — a brake on big weights

![regularisation path](figs/regularisation.png)

Without a brake, the model can make some weights huge to fit noise in the training URLs (overfitting, Lesson 01).
Regularisation adds a penalty for big weights. In scikit-learn the knob is **C**, and it works **backwards**: **small C =
strong brake** → all weights pulled toward 0. Dani tries C ∈ {0.01, 0.1, 1, 10} with cross-validation (Lesson 05).

## 6. Why the features must be scaled

`url_length` is around 50; `has_https` is 0 or 1. Gradient descent then zig-zags (Lesson 02 §4), and the weights can't be
compared. So a `StandardScaler` comes first, inside the `Pipeline` — fitted on training URLs only and saved with the
model.

## 🧪 Worked example: logistic regression from scratch

```python
import numpy as np

def sigmoid(z):
    return 1 / (1 + np.exp(-z))

# 6 tiny URLs, 2 features: has_at_symbol, brand_in_subdomain.  y = 1 phishing
X = np.array([[1, 1], [1, 0], [0, 1], [0, 0], [0, 0], [0, 0]], float)
y = np.array([1, 1, 1, 0, 0, 0], float)

w, b, lr = np.zeros(2), 0.0, 0.5
for epoch in range(500):
    p = sigmoid(X @ w + b)                       # 1. points → probability
    w -= lr * X.T @ (p - y) / len(y)             # 2. step downhill: average of error × input
    b -= lr * (p - y).mean()

loss = -np.mean(y * np.log(p) + (1 - y) * np.log(1 - p))
print("weights", w.round(2), "bias", round(b, 2), "loss", round(loss, 3))
print("P(phishing) for '@ only':", sigmoid(np.array([1, 0]) @ w + b).round(2))
print("P(phishing) for nothing :", sigmoid(b).round(2))
```

Both weights come out positive (both signs mean phishing) and the bias negative (a URL with no warning sign is probably fine).

## 7. Common mistakes

| student says | the truth |
|---|---|
| "Logistic *regression* predicts a number, so it's not a classifier" | It predicts a probability; the threshold makes a class. The name is historical. |
| "Bigger weight = more important feature" | Only if the features are scaled the same. |
| "A bigger learning rate learns faster" | Too big jumps over the minimum. |
| "It can learn any pattern" | It draws a straight line (a flat boundary). For curves: trees (Lesson 13) or networks (Lesson 20). |
| "A negative weight is a bug" | It means "this feature points towards legitimate" — or it's correcting a correlated feature. |

## 📝 Summary

> * **z = Σ wᵢ·xᵢ + b** — add up the points.
> * **p = σ(z) = 1 ÷ (1 + e⁻ᶻ)** — squash to 0…1; z = 0 → 0.5.
> * **log-loss**: −ln(p) if phishing, −ln(1 − p) if not — confident mistakes cost a lot.
> * **Gradient descent**: w ← w − lr × (p − y) × x — "said too little → raise the weights of the features it has".
> * **C** is a brake on big weights (small C = strong brake). **Scale** the features first.
> * The weights **are** the explanation.

## 8. Activities

1. **Human points system (10 min).** The class invents points for 4 warning signs, then scores 5 printed URLs. Compare
   with the real model's weights.
2. **Blindfolded hill (5 min).** A tilted table and a marble — gradient descent. What happens if the marble jumps?
3. **One step (15 min).** Pairs repeat §4 "one step by hand" with lr = 1.0. Is p closer to 1 than with lr = 0.5?

## 9. Do it yourself

<details><summary>1. Rana's points: URL with has_at 1, brand 1, https 0, dots 5. z and p.</summary>

z = 0.8 + 1.2 + 0 + 0.25 − 1.0 = **1.25** · e^(−1.25) = 0.287 · p = 1 / 1.287 = **0.78**.
</details>

<details><summary>2. σ(0)? σ(+10)? σ(−10)?</summary>

0.5 · 0.99995 · 0.00005.
</details>

<details><summary>3. One step: x = (1, 1), y = 0, w = (0, 0), b = 0, lr = 0.5.</summary>

p = 0.5, error = +0.5, slopes 0.5, 0.5, 0.5 → w = (−0.25, −0.25), b = −0.25 → z = −0.75 → p = 0.32 (closer to 0 ✓).
</details>

<details><summary>4. 🟢 Log-loss when the truth is legitimate and p = 0.9?</summary>

−ln(1 − 0.9) = −ln(0.1) = **2.30** — confident and wrong.
</details>

<details><summary>5. 🟡 What z gives p = 0.5? p = 0.73? p = 0.27?</summary>

**0**; **+1** (σ(1) = 1 ÷ 1.368 = 0.73); **−1** (the sigmoid is symmetric: σ(−z) = 1 − σ(z)).
</details>

<details><summary>6. 🟡 After training, the weight of has_https is −0.18. A URL changes from http to https. What happens to z? To p?</summary>

z goes down by 0.18 (if the features are scaled, by 0.18 × one scaled step). p goes down a little — https makes it look a
bit less like phishing.
</details>

<details><summary>7. 🔴 Why is the update "error × input" and not just "error"?</summary>

A feature that was 0 in this example played no part in the mistake, so its weight shouldn't change (× 0). A feature with a
big value contributed a lot, so it changes more. That is exactly what the slope (derivative) of the log-loss says.
</details>

## 10. In your project

| Project | Where |
|---|---|
| PhishGuard | exercises `ex05_sigmoid`, `ex06_log_loss`, `ex07_gradient`, `ex08_fit_logistic` · `phishguard/ml/trainer.py` → `ModelTrainer.build_logistic` · `ml/explainer.py` → `Explainer.contributions`, `explain` · theory `25_PhishGuard/01_theory/04_models.md` §4.1–4.4 · notebook `02_models.ipynb` |

## 🎬 Watch & explore

| | |
|---|---|
| <a href="https://www.youtube.com/watch?v=yIYKR4sgzI8"><img src="https://img.youtube.com/vi/yIYKR4sgzI8/mqdefault.jpg" width="240" alt="video"></a> | **StatQuest — Logistic Regression** (9 min). The S-curve and what the weights mean. |
| <a href="https://www.youtube.com/watch?v=sDv4f4s2SB8"><img src="https://img.youtube.com/vi/sDv4f4s2SB8/mqdefault.jpg" width="240" alt="video"></a> | **StatQuest — Gradient Descent, Step-by-Step** (23 min). Part 4, slowly, with every number. |
| <a href="https://www.youtube.com/watch?v=IHZwWFHWa-w"><img src="https://img.youtube.com/vi/IHZwWFHWa-w/mqdefault.jpg" width="240" alt="video"></a> | **3Blue1Brown — Gradient descent, how neural networks learn**. The same "walk downhill" idea for networks (Ryan, Lesson 21). |

**Play with it:**
* MLU-Explain — [Logistic Regression](https://mlu-explain.github.io/logistic-regression/) (interactive)
* At home: in the worked example change lr to 5 and to 0.01 — what happens to the loss after 500 steps?
