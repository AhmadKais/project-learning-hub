# Chapter 4 — The two models

💡 **In short:** logistic regression gives every feature a weight, adds them up and squashes the sum into a probability — simple and explainable. A random forest is 300 decision trees that vote — stronger, less explainable. We train both, compare, and keep the better one.


## 4.1 Logistic regression — a weighted vote with a squash

The simplest useful classifier. Every feature gets a **weight**; the model adds up
weight × value, adds a bias, and squashes the sum into a probability with the **sigmoid** function.

📄 **Sigmoid**
```text
sigmoid(z) = 1 / (1 + e^(-z))

z = -5  ->  0.007       z = 0  ->  0.5       z = +5  ->  0.993
```

📄 **A tiny model with 4 features (invented weights, real mechanism)**
```text
weights:  has_at_symbol +0.8    brand_in_subdomain +1.2    has_https -1.5    num_dots +0.05    bias -1.0

URL A  http://paypal.com.secure-login.xyz/verify   (at=0, brand=1, https=0, dots=3)
   z = 0.8*0 + 1.2*1 + (-1.5)*0 + 0.05*3 + (-1.0) = 1.2 + 0.15 - 1.0 = 0.35
   p = 1 / (1 + e^-0.35) = 1 / (1 + 0.705) = 0.59        -> phishing, but only 59%

URL A' http://paypal.com@secure-login.xyz/verify   (same, plus an "@": at=1)
   z = 0.8 + 1.2 + 0 + 0.15 - 1.0 = 1.15
   p = 1 / (1 + e^-1.15) = 1 / (1 + 0.317) = 0.76        -> phishing (76%) - one more trick, more confidence

URL B  https://www.google.com/                     (at=0, brand=0, https=1, dots=2)
   z = 0 + 0 - 1.5 + 0.10 - 1.0 = -2.40
   p = 1 / (1 + e^2.40) = 1 / (1 + 11.02) = 0.083        -> legitimate (8%)
```

Two things to notice:

- **The weights are the explanation.** `has_https = -1.5` means "HTTPS pushes strongly toward
  legitimate". `Explainer` shows exactly `weight × value` per feature — that is where the sentences
  on screen come from.
- **The model is linear**: it cannot learn "dots matter only when there is no HTTPS". The random
  forest can. That is why we train both and compare.

## 4.2 How the weights are learned

Start with random weights. For every training URL, compare the predicted probability with the truth
using the **log-loss**:

📄 **Log-loss**
```text
truth = 1 (phishing):   loss = -ln(p)         p = 0.76 -> 0.27      p = 0.10 -> 2.30
truth = 0 (good):       loss = -ln(1 - p)     p = 0.08 -> 0.09      p = 0.90 -> 2.30
```

Confident and wrong is punished hard. Then **gradient descent**: for every weight, compute in which
direction a small change lowers the average loss, and step that way. Repeat a few hundred times
(scikit-learn does this inside `fit()`). The step direction turns out to be beautifully simple:

📄 **The gradient of log-loss + sigmoid**
```text
for weight i:   d(loss)/d(w_i) = (p - truth) * x_i

URL A' (truth 1, p 0.76):  (0.76 - 1) * x = -0.24 * x   -> weights of the features present go UP (w = w - lr * gradient)
URL B  (truth 0, p 0.08):  (0.08 - 0) * x = +0.08 * x   -> weights of the features present go DOWN a little
```

"Error times input" — every weight moves in proportion to how wrong we were and how big its feature was.

## 4.3 Why features must be scaled

`url_length` is ~50; `has_https` is 0 or 1. Without scaling, the length's weight would have to be
tiny and the boolean's huge for them to matter equally, and gradient descent crawls. **StandardScaler**
turns every feature into "how many standard deviations from the training mean":
`x_scaled = (x - mean) / std`. Two consequences you must remember:

- the scaler is fitted on the **training** split only (its mean/std are learned parameters — using
  test data would be leakage), and it must be saved **with** the model — hence the `Pipeline`;
- the weights you show in explanations are on the *scaled* features: "url_length is 2.1 std above
  average" — which is actually a better sentence than "length is 91".

## 4.4 Regularization — the `C` parameter

Without a brake, the model can grow huge weights to fit noise in the training data. **L2
regularization** adds a penalty `sum(w²)` to the loss; `C` in scikit-learn is the *inverse* strength:
small `C` = strong brake = simpler model. We try `C ∈ {0.01, 0.1, 1, 10}` with cross-validation
(section 4.7) and keep the best.

## 4.5 Decision trees — a flow chart learned from data

A tree asks yes/no questions on features and reaches a leaf with a verdict:

📄 **A small tree**
```text
                 has_https == 0 ?
                /                \
             yes                  no
       num_subdomains >= 2 ?    suspicious_word_count >= 2 ?
        /          \              /            \
   phishing      good        phishing         good
```

How does it choose the question? By **Gini impurity**: how "mixed" a group is.
`Gini = 1 - sum(p_class²)`. Pure group (all phishing) → 0; 50/50 → 0.5.

📄 **Choosing the first split — 10 URLs, 5 good, 5 bad**
```text
root: Gini = 1 - (0.5² + 0.5²) = 0.5

candidate A: split on has_https
   https=1 group: 4 good, 1 bad  -> Gini = 1 - (0.8² + 0.2²) = 0.32
   https=0 group: 1 good, 4 bad  -> Gini = 0.32
   weighted = (5/10)*0.32 + (5/10)*0.32 = 0.32      gain = 0.5 - 0.32 = 0.18

candidate B: split on num_dots > 2
   dots>2 group:  3 good, 3 bad  -> Gini = 0.5
   dots<=2 group: 2 good, 2 bad  -> Gini = 0.5
   weighted = 0.5                                     gain = 0

-> the tree asks about has_https first.
```

It repeats inside each group until the groups are pure or a limit is reached (`max_depth`,
`min_samples_leaf`). A single tree grown to purity **memorizes** the training data — 100% on train,
much worse on test.

## 4.6 Random forest — many weak trees, one strong vote

Breiman's fix (2001): train **300 trees**, each on a random sample of the rows (with replacement —
"bootstrap") and, at every split, a random subset of the features. Each tree is a bit wrong in its
own way; averaging their votes cancels the individual mistakes. The forest:

- handles interactions ("dots matter when no HTTPS") that logistic regression cannot;
- barely needs scaling (trees compare thresholds, not magnitudes);
- reports **feature importance**: how much each feature reduced impurity across all trees — your
  chart `feature_importance.png`;
- but explains a *single* prediction less cleanly than logistic regression (hence the honest
  approximation in `Explainer`).

## 4.7 Cross-validation and grid search

Which `C`? Which `max_depth`? Trying them on the validation set is fine, but one split is noisy.
**k-fold cross-validation** (k = 5): split the *training* data into 5 parts; train on 4, score on
the 5th; rotate; average the 5 scores. **Grid search** does this for every combination of settings
and keeps the best. In code: `GridSearchCV(pipeline, param_grid, cv=5, scoring="f1")`. Test data is
never touched.

📄 **What GridSearchCV runs for the forest grid**
```text
max_depth ∈ {None, 10, 20}  ×  min_samples_leaf ∈ {1, 3}  = 6 combinations
× 5 folds = 30 trainings, then one final fit on all training data with the best settings.
```

## ✅ Check yourself — Chapter 4

1. With the weights of section 4.1, compute p for `http://bit.ly/x` where the features are
   at=0, brand=0, https=0, dots=1. Verdict at threshold 0.5?
2. The model predicts p = 0.30 for a URL that is actually phishing. Compute the log-loss. Now p = 0.95.
   Compare and explain the difference in words.
3. In the gradient formula, a feature with value 0 for this URL — does its weight change? Why does that make sense?
4. Ten URLs, 8 good and 2 bad. Compute the Gini of the group. Then a split puts both bad ones
   alone in one group of 2 — compute the weighted Gini and the gain.
5. Why would a single tree with no depth limit get 100% on training data? Why is that bad?
6. Grid: `C ∈ {0.1, 1, 10}`, 5 folds. How many model fits does `GridSearchCV` run in total (including the final refit)?
7. Give one thing the forest can learn that logistic regression cannot, with a URL example.

## 📚 Further reading — Chapter 4

- **StatQuest — Logistic Regression** (YouTube, ~10 min): https://www.youtube.com/watch?v=yIYKR4sgzI8
- **StatQuest — Decision Trees** and **Random Forests part 1**: https://www.youtube.com/watch?v=_L39rN6gz7Y · https://www.youtube.com/watch?v=J4Wdy0Wc_xQ
- **scikit-learn — Logistic regression**: https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression
- **scikit-learn — Random forests**: https://scikit-learn.org/stable/modules/ensemble.html#forest
- **scikit-learn — Pipeline and StandardScaler**: https://scikit-learn.org/stable/modules/compose.html · https://scikit-learn.org/stable/modules/preprocessing.html
- **Breiman (2001), Random Forests** — abstract + section 1: https://doi.org/10.1023/A:1010933404324
- **Google ML Crash Course — Logistic Regression**: https://developers.google.com/machine-learning/crash-course/logistic-regression
