# Chapter 2 — What is machine learning?

💡 **In short:** instead of writing rules, we show the computer 20,000 URLs with the right answer and it finds the rules itself. We keep some URLs hidden (the test set) to check it really learned. We measure with recall (how many phishing we caught) and precision (how many alarms were real) — not just accuracy.


## 2.1 Rules vs. learning

You could try to write rules:

📄 **A hand-written rule — and why it fails**
```python
def is_phishing(url):
    if "@" in url or url.startswith("http://") and "login" in url:
        return True
    return False
```

Every rule you write, attackers break next week; every rule catches some real sites too
(`https://accounts.google.com/login` has "login"). After fifty rules you have a mess that nobody can tune.

Machine learning turns this around: **we do not write rules, we show examples.** We give the program
20,000 URLs marked "good" or "bad", and it finds by itself how much each property matters — as
numbers (weights) adjusted until the answers come out right on the examples.

## 2.2 The vocabulary

- **Sample** — one URL.
- **Label** — the correct answer: `good` (0) or `bad` (1). In our code, 1 = phishing.
- **Dataset** — all samples with labels. Ours: Kaggle "Phishing Site URLs", ~549,000 rows.
- **Feature** — one number describing a sample: `url_length = 43`. We compute 20 per URL.
- **Feature vector** — the 20 numbers of one URL, in a fixed order.
- **Supervised learning** — learning from labelled examples. What we do.
- **Binary classification** — two classes: phishing / legitimate.
- **Model** — the thing that learns. Ours: logistic regression and a random forest.
- **Training** — fitting the model to the examples. **Inference** — using it on a new URL.
- **Probability** — the model's output, between 0 and 1. **Threshold** — the cut-off that turns it into a verdict.

## 2.3 Train, validation, test

If a teacher gives you 100 solved questions and then the exam has the same 100, a perfect score
proves nothing — maybe you memorized. Same for a model. So we split the data:

| Group | Share | Used for |
|---|---|---|
| Train | 70% | the model learns **only** from these |
| Validation | 15% | choosing settings (which model, which threshold) |
| Test | 15% | touched **once**, at the end, to report the final score |

💡 If you choose the threshold by looking at the test set, your reported score is a lie — the test
took part in the decision. That is **leakage**. Validation exists for exactly this.

❓ **Possible supervisor question: 99% on train, 88% on test — what happened?**
**Overfitting**: the model memorized the training URLs instead of learning the general pattern.
Classic with a random forest that grows unlimited trees. Cures: limit tree depth, more data,
cross-validation to pick settings.

## 2.4 Measuring honestly — accuracy is not enough

The full Kaggle file is 72% good / 28% bad. A model that always says "good" gets 72% accuracy and
catches **zero** phishing. So we look at the four cases:

📄 **The confusion matrix (positive = phishing)**
```text
                         predicted good     predicted phishing
actually good                TN                  FP   (false alarm)
actually phishing            FN  (missed!)       TP

Accuracy  = (TP + TN) / all
Precision = TP / (TP + FP)      of all alarms, how many were real
Recall    = TP / (TP + FN)      of all phishing, how many we caught
F1        = 2 * P * R / (P + R)
```

📄 **Worked example — 1,000 test URLs, 500 of each**
```text
                  pred good   pred phishing
good                 470            30          -> 30 false alarms
phishing              25           475          -> 25 missed

Accuracy  = (475 + 470) / 1000 = 0.945
Precision = 475 / (475 + 30)   = 0.941
Recall    = 475 / (475 + 25)   = 0.950
F1        = 2 * 0.941 * 0.950 / (0.941 + 0.950) = 0.945
```

Which mistake is worse? A missed phishing (FN) can cost someone their bank account; a false alarm
(FP) costs a few seconds of doubt. So **recall for phishing is our most important metric** — the
proposal targets ≥ 0.95 — and we accept a slightly lower precision to get it. Chapter 5 shows how the
threshold trades one for the other.

## 2.5 Balance

Training on 72/28 data teaches the model that "good" is the safe guess. Two fixes, and we use both:
take a **balanced sample** (10,000 of each class — `DatasetLoader.balance`), and tell the model to
weigh the rare class more (`class_weight="balanced"` in scikit-learn).

## 2.6 Bias and variance — reading your results

- **High bias** (underfitting): low score on train *and* test. The model is too simple or the features
  are weak. Fix: better features, a more flexible model (the forest).
- **High variance** (overfitting): high on train, much lower on test. Fix: limit depth, more data,
  regularization (`C` in logistic regression).

📄 **What to expect**
```text
                          train   val    diagnosis
logistic, 20 features     0.93    0.92   fine - small gap
forest, unlimited depth   1.00    0.95   overfits a little - limit max_depth
forest, max_depth=20      0.98    0.96   better
```

## ✅ Check yourself — Chapter 2

1. A model always says "good" on the full Kaggle file (392k good, 157k bad). Compute accuracy,
   precision and recall for phishing.
2. In the worked example, the threshold is lowered and now 15 phishing are missed but 60 false
   alarms happen. Recompute precision, recall, F1. Which version would you ship, and why?
3. Your friend tuned the threshold by trying values on the *test* set until F1 was highest. Why is
   his reported F1 not trustworthy? What should he have used?
4. Train 0.99, test 0.86 with a random forest. Name the problem and two settings to change.
5. Why do we sample 10,000 per class instead of using all 549,000 rows? Give two reasons.

## 📚 Further reading — Chapter 2

- **Google — Machine Learning Crash Course**: Classification, Precision/Recall, ROC — https://developers.google.com/machine-learning/crash-course
- **scikit-learn — Model evaluation**: https://scikit-learn.org/stable/modules/model_evaluation.html (3.4.2–3.4.4)
- **scikit-learn — Cross-validation**: https://scikit-learn.org/stable/modules/cross_validation.html
- **StatQuest — Confusion Matrix, Sensitivity/Specificity** (YouTube, 10 min each): https://www.youtube.com/c/joshstarmer
