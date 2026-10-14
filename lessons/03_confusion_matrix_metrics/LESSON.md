# Lesson 03 — Measuring a classifier: confusion matrix, precision, recall, F1

> **For:** Laith · Dani · Seif · Ryan (and Kosai for precision in Lesson 10) &nbsp;·&nbsp; **Time:** 45 – 60 min
> **Before:** Lesson 01 &nbsp;·&nbsp; **After this:** Lesson 04 (threshold, ROC)

## 🎯 By the end, the student can

1. Fill a confusion matrix from predictions, and name the four cells **with their meaning in their own project**.
2. Compute precision, recall, F1 and accuracy by hand, and explain why accuracy lies on imbalanced data.
3. Explain macro-F1 for more than two classes (Wine: 3 grades, Face: 7 emotions).

---

## 1. Start with the picture: the fishing net

![precision and recall as a net](figs/net.png)

Orange squares are spam, blue dots are real messages. The yellow circle is "what the filter calls spam".

* **Precision** = of what is *inside the net*, how much is spam? (Did I catch only fish, or also boots?)
* **Recall** = of all the spam *in the sea*, how much is inside the net?

A bigger net → higher recall, lower precision. **You cannot have both for free.** Ask the class before showing
the third panel: *"What if the net is the whole sea?"* (recall 1.0, precision = the share of spam.)

## 2. The confusion matrix — real numbers from the SMS data

![confusion matrix anatomy](figs/anatomy.png)

A simple model, 1,673 validation messages, threshold 0.5:

| Cell | Name | In Spam | In PhishGuard | In WineGrader |
|---|---|---|---|---|
| TP | true positive | spam caught | phishing blocked | — (per class, see §5) |
| FP | false positive | **real mail hidden** 😱 | legitimate site blocked | |
| FN | false negative | spam in the inbox | **phishing let through** 😱 | |
| TN | true negative | real mail delivered | legitimate site allowed | |

😱 marks the expensive mistake. It is a **different cell** in the two projects — that is why Laith and Dani choose
their thresholds with opposite rules (Lesson 04).

## 3. The formulas, and the same numbers by hand

$$\text{precision}=\frac{TP}{TP+FP}\qquad \text{recall}=\frac{TP}{TP+FN}\qquad F_1=\frac{2PR}{P+R}\qquad \text{accuracy}=\frac{TP+TN}{\text{all}}$$

```
TP = 187   FP = 5   FN = 37   TN = 1444          (all = 1673)

precision = 187 / 192  = 0.974     "when it says spam, it is right 97% of the time"
recall    = 187 / 224  = 0.835     "it catches 83% of the spam"
F1        = 2·0.974·0.835 / (0.974 + 0.835) = 0.899
accuracy  = 1631 / 1673 = 0.975
```

**Memory trick:** **P**recision looks at the **P**redicted column. **R**ecall looks at the **R**eal row.

**Why F1 is a *harmonic* mean:** if P = 1.0 and R = 0.0, the ordinary average is 0.5 — a useless model looks
"half good". The harmonic mean gives 0: F1 is only high when **both** are high.

## 4. Accuracy lies on imbalanced data

![accuracy trap](figs/accuracy_trap.png)

87 % of the SMS are ham. A "model" that always answers *ham* has 87 % accuracy and catches **nothing**.
Every ML project here is imbalanced (spam 13 %, high-quality wine 19 %, "disgust" in FER-2013 ≈ 1.5 %), so
**accuracy is never the main number** in their books.

## 5. Watch everything move with the threshold

![threshold sweep](figs/threshold_sweep.gif)

Left: the model's scores for real ham (blue) and real spam (orange). Everything right of the black line is called
spam. Middle: the matrix. Right: precision, recall and F1 for every threshold. **Pause the video at three places
and let the students read the four numbers aloud.** Questions to ask while it plays:

* "Why does FP explode when the line goes left?" (the big blue pile is on the left)
* "Where is F1 highest? Is that where Laith should put his threshold?" (No — Lesson 04.)

## 6. More than two classes: macro-F1

![macro-F1 on wine](figs/macro_f1.png)

For each class, treat it as "positive" and all others as "negative", and compute P, R, F1. Then:

* **macro-F1** = the plain average of the per-class F1s → every class counts the same, even the small "high".
* accuracy is dominated by the big classes.

Reading the matrix: the **row** is the truth, the **column** the prediction, the **diagonal** is correct. Most errors
in wine are between *neighbouring* grades (low↔medium, medium↔high) — the tasters themselves disagree there.
(This quick model is untuned; Seif's tuned k-NN reaches ≈ 0.58.)

## 7. Misconceptions

| Student says | Truth |
|---|---|
| "Precision and recall are the same thing basically" | Same numerator, different denominator: predicted column vs real row. |
| "My accuracy is 97 %, done" | Compare with the "always majority" baseline first. |
| "High recall is always good" | Calling everything positive gives recall 1.0. Always report both. |
| "F1 is the best threshold" | F1 treats FP and FN as equally bad — they are not in any of these projects. |

## 8. Activities

1. **Human classifier (15 min).** Print 20 real SMS from `08_SpamClassifier/data/sms_spam.csv` (5 spam). Each
   student labels them in 3 minutes. Build each one's confusion matrix on the board; compute P and R. Who had
   the best precision? the best recall? Were they the same student?
2. **Fill the matrix (5 min).** Truth: `S S H H H S H H`, predicted: `S H H S H S H H` → TP 2, FN 1, FP 1, TN 4.
3. **Pause-and-read** the GIF (above).

## 9. Check yourself

<details><summary>1. TP 90, FP 10, FN 30, TN 870. P, R, F1, accuracy?</summary>

P = 90/100 = 0.90 · R = 90/120 = 0.75 · F1 = 2·0.9·0.75/1.65 = 0.818 · accuracy = 960/1000 = 0.96
</details>

<details><summary>2. Which number should PhishGuard keep high, and which one Spam?</summary>

PhishGuard: **recall** (a missed phishing site can cost someone their bank account). Spam: **precision** (a hidden
real message can cost an interview). Same matrix, opposite priorities.
</details>

<details><summary>3. In a 3-class problem, class "high" has P = 0.46, R = 0.37. What is its F1, and why is it low?</summary>

F1 = 2·0.46·0.37 / 0.83 = 0.41. It is the smallest class, and k-NN's neighbourhoods are dominated by the
bigger classes (Lesson 15: the imbalance correction).
</details>

## 10. In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/ml/threshold.py` → `confusion_at`, `precision_recall_curve` · `ModelComparator.confusion_matrix` |
| PhishGuard | `phishguard/ml/evaluator.py` → `ModelEvaluator.metrics`, `worst_mistakes` |
| WineGrader | `winegrader/ml/scoring.py` → `confusion_matrix`, `precision_recall_f1`, `macro_f1`, `accuracy` |
| FaceEmotion | `app/ml/evaluator.py` → `ModelEvaluator.evaluate`, `plot_confusion_matrix` (7 × 7) |

## 🎬 Watch & explore

* StatQuest — *The Confusion Matrix* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+confusion+matrix)
* StatQuest — *Sensitivity and Specificity* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+sensitivity+and+specificity)
* MLU-Explain — [Precision & Recall](https://mlu-explain.github.io/precision-recall/) (interactive)
* Google ML Crash Course — [Accuracy, precision, recall](https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall)
