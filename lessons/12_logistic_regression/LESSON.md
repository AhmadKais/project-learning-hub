# Lesson 12 — Logistic regression and gradient descent: a weighted vote with a squash

> **For:** Dani (PhishGuard — first model, explanations) · the gradient-descent part is also for Ryan (Lesson 21)
> **Time:** 2 × 45 min &nbsp;·&nbsp; **Before:** Lessons 01, 02, 03 &nbsp;·&nbsp; **After this:** Lesson 13 (trees), Lesson 21 (backprop)

## 🎯 By the end, the student can

1. Compute z = w·x + b and p = sigmoid(z) by hand for a URL.
2. Explain the log-loss and why "confident and wrong" costs so much.
3. Explain gradient descent with the hill picture, and write the update rule `w ← w − lr·(p − y)·x`.
4. Read the weights as an explanation, and explain what `C` (regularisation) does.

---

## 1. The model in one line

$$p=\sigma(w_1x_1+w_2x_2+\dots+w_nx_n+b)\qquad\sigma(z)=\frac{1}{1+e^{-z}}$$

Every feature gets a weight. The model adds weight × value (a **vote**), adds a bias, and **squashes** the sum into a
probability.

![sigmoid](figs/sigmoid.png)

The guide's three URLs (invented weights, real mechanism): `has_at +0.8, brand_in_subdomain +1.2, has_https −1.5,
num_dots +0.05, bias −1.0`.

```
URL A   paypal.com.secure-login.xyz   z = 0 + 1.2 + 0 + 0.15 − 1.0 = 0.35   p = 0.59
URL A'  …same with an "@"             z = 0.8 + 1.2 + 0 + 0.15 − 1.0 = 1.15  p = 0.76
URL B   https://www.google.com/       z = 0 + 0 − 1.5 + 0.10 − 1.0 = −2.40  p = 0.083
```

## 2. The weights ARE the explanation

![contributions](figs/contributions.png)

Each bar is weight × value. PhishGuard's `Explainer.contributions` shows exactly these (on **scaled** features:
"url_length is 2.1 standard deviations above average"). The model is **linear**: it cannot learn "dots matter only
without HTTPS" — that's what the random forest is for (Lesson 13).

## 3. How wrong were we? The log-loss

![log-loss](figs/logloss.png)

| truth | p | loss |
|---|---|---|
| phishing | 0.76 | −ln 0.76 = 0.27 |
| phishing | 0.10 | −ln 0.10 = **2.30** |
| legitimate | 0.08 | −ln 0.92 = 0.09 |
| legitimate | 0.90 | −ln 0.10 = **2.30** |

Training = find the weights with the smallest **average** loss over all training URLs.

## 4. Gradient descent — walking downhill

![learning rate](figs/gd_1d.png)

Imagine standing on a hill in fog. You feel the slope under your feet and step downhill. Repeat.

$$w\leftarrow w-\text{lr}\cdot\frac{\partial\,\text{loss}}{\partial w}$$

For sigmoid + log-loss the slope is beautifully simple — **"error times input"**:

$$\frac{\partial\,\text{loss}}{\partial w_i}=(p-y)\,x_i\qquad\frac{\partial\,\text{loss}}{\partial b}=p-y$$

* URL A' (truth 1, p 0.76): error −0.24 → the weights of the features it has go **up**.
* URL B (truth 0, p 0.08): error +0.08 → its features' weights go **down a little**.

### Watch it learn (500 real PhishGuard URLs, two features)

![gradient descent learning the boundary](figs/gd_boundary.gif)

Left: the black line is p = 0.5; colour = the model's probability. It starts with bad weights and turns step by step;
right: the loss falls. Two features cannot separate the classes well (loss stays at 0.6) — the real model uses all 20.

```python
for epoch in range(2000):
    p = sigmoid(X @ w + b)
    grad_w = X.T @ (p - y) / len(y)     # average of "error × input"
    grad_b = (p - y).mean()
    w -= lr * grad_w
    b -= lr * grad_b
```

(Dani's exercises ex05–ex08 build exactly this; `ModelTrainer.build_logistic` then uses scikit-learn, which does the same
with a smarter optimiser.)

## 5. Regularisation — the `C` parameter

![regularisation path](figs/regularisation.png)

Without a brake the model can grow huge weights to fit noise. L2 regularisation adds $\sum w^2$ to the loss.
scikit-learn's `C` is the **inverse** strength: **small C = strong brake** = all weights pulled toward 0 = simpler model.
Dani tries `C ∈ {0.01, 0.1, 1, 10}` with cross-validation (Lesson 05).

## 6. Misconceptions

| Student says | Truth |
|---|---|
| "Logistic **regression** predicts a number, so it isn't a classifier" | It predicts a probability; the threshold makes it a class. The name is historical. |
| "A big weight = an important feature" | Only if features are on the same scale — that's why weights are compared on scaled features. |
| "A bigger learning rate learns faster" | Too big jumps over the minimum and diverges (third panel). |
| "Gradient descent finds the perfect model" | It finds the best **linear** model for the loss. If the truth isn't linear, it can't. |

## 7. Activities

1. **Human gradient descent (10 min).** Blindfolded student, a gentle slope in the room (or a drawn curve): "feel" the
   slope by taking tiny test steps; walk downhill. What if the steps are huge?
2. **Compute (10 min).** Weights above; compute p for `http://203.0.113.5@paypal.secure.xyz` (has_at = 1, brand = 1,
   https = 0, dots = 5).  → z = 0.8 + 1.2 + 0.25 − 1.0 = 1.25, p = 0.78.
3. **One update by hand (10 min).** x = (1, 0), y = 1, w = (0, 0), b = 0, lr = 0.5: p = 0.5, grad_w = (−0.5, 0),
   new w = (0.25, 0), new b = 0.25.
4. **Live:** run the notebook `25_PhishGuard/02_examples/02_models.ipynb` and change `lr` to 5.

## 8. Check yourself

<details><summary>1. sigmoid(0)? sigmoid(+∞)? sigmoid(−∞)?</summary>

0.5, 1, 0.
</details>

<details><summary>2. Why is the gradient "(p − y)·x" so convenient?</summary>

The sigmoid's derivative and the log's derivative cancel, leaving just "how wrong" × "how big the input". No
exponentials, no division — cheap and numerically stable.
</details>

<details><summary>3. The scaler must be saved with the model. Why?</summary>

The weights were learned on scaled features. A new URL must be scaled with the **training** mean and std — otherwise
`url_length = 91` is treated as 91 standard deviations. The `Pipeline` keeps them together.
</details>

## 9. In your project

| Project | Where |
|---|---|
| PhishGuard | exercises `ex05_sigmoid`, `ex06_log_loss`, `ex07_gradient`, `ex08_fit_logistic` · `phishguard/ml/trainer.py` → `ModelTrainer.build_logistic` (StandardScaler + LogisticRegression in a Pipeline) · `ml/explainer.py` → `Explainer.contributions`, `explain` · theory `25_PhishGuard/01_theory/04_models.md` §4.1–4.4 · notebook `02_models.ipynb` |

## 🎬 Watch & explore

* StatQuest — *Logistic Regression* (and *…Details Pt 2: Maximum Likelihood*) — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+logistic+regression)
* StatQuest — *Gradient Descent, Step-by-Step* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+gradient+descent+step+by+step)
* MLU-Explain — [Logistic Regression](https://mlu-explain.github.io/logistic-regression/) (interactive)
* TensorFlow Playground — [play with a linear classifier](https://playground.tensorflow.org/)
