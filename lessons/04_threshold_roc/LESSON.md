# Lesson 04 — Where to draw the line: the threshold, ROC and AUC

> **For:** Laith (precision floor) · Dani (ROC, recall target) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 03 &nbsp;·&nbsp; **After this:** Spam stage 6, PhishGuard stage 4

## The story

> **Rana works at a bank's help desk.** Customers forward her links they got by SMS: "Is this really the bank?". The
> bank buys a program that gives each link a **phishing score** from 0 to 1. Rana's boss asks: *"At what score do we
> block a link?"* If they block at 0.9, some phishing gets through and a customer may lose their savings. If they block
> at 0.1, half of the normal sites are blocked and customers call angrily. The program can't decide this — **people**
> must. This lesson is how to decide well.

## 🎯 By the end, the student can

1. Explain that a classifier gives a **score**, and a **threshold** turns the score into a yes/no.
2. Compute the true-positive rate and false-alarm rate for one threshold, and draw a ROC curve by hand.
3. Explain AUC in one sentence, with numbers between 0.5 and 1.
4. Apply their project's rule for choosing the threshold — on the validation set — and defend it.

## Words you need

| word | meaning |
|---|---|
| **score / probability** | the model's number for one example, 0 … 1: "how phishing-like" |
| **threshold** | the cut: score ≥ threshold → "phishing" |
| **TPR (true-positive rate) = recall** | of all phishing links, the share we block — Lesson 03 |
| **FPR (false-positive rate) = false-alarm rate** | of all **good** links, the share we block by mistake |
| **ROC curve** | the line of (FPR, TPR) points for every possible threshold |
| **AUC** | "area under the curve": one number for the whole ROC curve, 0.5 … 1 |

---

## 1. Score + threshold = decision

Ten links, sorted by the model's score (P = phishing, G = good):

```
link:    1     2     3     4     5     6     7     8     9     10
score:  0.95  0.90  0.80  0.70  0.60  0.45  0.40  0.30  0.20  0.10
truth:   P     P     G     P     P     G     P     G     G     G
```

Count first: 5 phishing (links 1, 2, 4, 5, 7) and 5 good (links 3, 6, 8, 9, 10).

**Threshold 0.65** → block links with score ≥ 0.65 → links 1, 2, 3, 4.

```
blocked phishing (TP) = 1, 2, 4      → 3        TPR = 3 / 5 phishing = 0.6
blocked good     (FP) = 3            → 1        FPR = 1 / 5 good     = 0.2
```

**Threshold 0.35** → block 1–7.

```
TP = 1, 2, 4, 5, 7 → 5     TPR = 5/5 = 1.0
FP = 3, 6          → 2     FPR = 2/5 = 0.4
```

Lower threshold → more phishing caught **and** more false alarms. Every threshold is a **trade**.

## 2. The ROC curve — every threshold at once

Do it for **every** threshold, from very strict (block nothing) to very loose (block everything), and put each
(FPR, TPR) pair as a point on a chart. Connect the points: that's the **ROC curve**.

Our 10 links, threshold moving down one link at a time:

```
block down to link:  none  1    2    3    4    5    6    7    8    9    10
TP:                   0    1    2    2    3    4    4    5    5    5    5
FP:                   0    0    0    1    1    1    2    2    3    4    5
TPR = TP/5:           0   .2   .4   .4   .6   .8   .8   1.0  1.0  1.0  1.0
FPR = FP/5:           0    0    0   .2   .2   .2   .4   .4   .6   .8   1.0
```

Every phishing link moves the point **up**; every good link moves it **right**. A perfect model would go straight up
first (all phishing have higher scores than all good), then right.

![ROC being built](figs/roc_build.gif)

The same thing on the **real** PhishGuard URLs. Left: scores of good URLs (blue) and phishing URLs (orange); the black
line is the threshold. Right: the point for that threshold. As the line slides down, the point draws the curve.

## 3. Shapes of ROC curves

![ROC shapes](figs/roc_shapes.png)

The small histograms show the two piles of scores. **The less they overlap, the closer the curve hugs the top-left
corner.** If the scores of both classes are mixed together (useless model), every threshold blocks good and bad
equally → the diagonal.

## 4. AUC — one number for the whole curve

**AUC** = the area under the ROC curve (the coloured area). The square is 1 × 1, so AUC is between 0 and 1:

| AUC | meaning |
|---|---|
| 1.0 | perfect: some threshold separates them completely |
| 0.9 – 0.99 | good (PhishGuard's target: ≥ 0.97) |
| 0.5 | coin flip: the diagonal |

**AUC in plain words:**

![AUC as pairs](figs/auc_pairs.png)

> Pick one random phishing link and one random good link. AUC = the probability that the **phishing one got the higher
> score**.

On our 10 links: 5 phishing × 5 good = 25 pairs. Count the pairs where the phishing link scored higher:

```
phishing 1 (0.95): beats all 5 good                         → 5
phishing 2 (0.90): beats all 5 good                         → 5
phishing 4 (0.70): beats good 6, 8, 9, 10 (not good 3, 0.80) → 4
phishing 5 (0.60): beats 6, 8, 9, 10                        → 4
phishing 7 (0.40): beats 8, 9, 10 (not 3 or 6)              → 3
total 21 of 25 pairs  →  AUC = 21 / 25 = 0.84
```

Because AUC only looks at the **order** of the scores, it doesn't depend on any threshold — the fairest single number to
compare two models (Dani: logistic regression vs random forest).

## 5. Choosing the threshold — the cost of each mistake

![the two rules](figs/rules.png)

| | Spam (Laith) | PhishGuard (Dani) |
|---|---|---|
| the expensive mistake | **FP**: a real message hidden | **FN**: a phishing site let through |
| so we demand | precision ≥ **0.98** | recall ≥ **0.95** |
| and then take | the threshold with the **highest recall** | the **highest** threshold (fewest false alarms) |
| if nothing reaches the demand | **raise an error** (never silently use 0.5) | fall back to `config.DEFAULT_THRESHOLD` |

Laith's algorithm, step by step:

```
best = nothing
for t = 0.50, 0.51, 0.52, … 0.99:
    P, R = precision and recall on the VALIDATION set, when "spam" means score ≥ t
    if P ≥ 0.98 and (best is nothing or R > best.R):
        best = (t, P, R)
if best is nothing: raise an error saying the best precision reached
return best
```

**Why validation and not test?** Choosing the threshold is a decision made from data — the test set must stay unseen
(Lesson 01).

![cost curves](figs/cost.png)

Give each mistake a price and add up the cost at every threshold. If a missed phish costs 20× a false alarm, the
cheapest threshold moves **left** (block more). 0.5 and "best F1" both pretend the two mistakes cost the same.

## 6. Common mistakes

| student says | the truth |
|---|---|
| "The model decides phishing or not" | The model gives a score; **people** choose the threshold. |
| "AUC 0.97 means 97 % accuracy" | AUC is about the order of scores; accuracy is about one threshold. |
| "I'll pick the threshold on the test set" | A decision made with the test set → leakage. |

## 7. Activities

1. **Human ROC (15 min).** Hand out the 10 link cards above (score + hidden truth). Sort, walk the threshold down card by
   card, and plot each (FP/5, TP/5) on squared paper. Count the squares under the curve → AUC.
2. **Bank vs newspaper (5 min).** Role-play: the bank wants to block more; a news site wants fewer false alarms. Which
   threshold does each choose from the table in `25_PhishGuard/01_theory/05_evaluation.md` §5.1?
3. `python visualize.py --live` — slide the threshold and watch the point.

## 8. Do it yourself

<details><summary>1. In the 10-link example, threshold 0.5. TP, FP, TPR, FPR?</summary>

Blocked: 1–5. TP = 1, 2, 4, 5 → 4 (TPR 0.8); FP = 3 → 1 (FPR 0.2).
</details>

<details><summary>2. The ROC passes through (0.02, 0.90). Say it in words.</summary>

At some threshold the model blocks 90 % of phishing links while blocking only 2 % of good ones.
</details>

<details><summary>3. A model's AUC is 0.35. What probably happened?</summary>

The order is mostly backwards — labels are swapped somewhere. Flipping the scores would give 0.65.
</details>

## 9. In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/ml/threshold.py` → `confusion_at`, `choose_threshold`, `precision_recall_curve`; the threshold is saved in the bundle (`threshold.json`) · theory `08_SpamClassifier/01_theory/06_evaluation.md` |
| PhishGuard | `phishguard/ml/evaluator.py` → `ModelEvaluator.choose_threshold`, `compare` (ROC for both models) · exercises `ex10`–`ex12` · theory `25_PhishGuard/01_theory/05_evaluation.md` |

## 🎬 Watch & explore

* StatQuest — *ROC and AUC, Clearly Explained!* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+ROC+and+AUC+clearly+explained)
* MLU-Explain — [ROC & AUC](https://mlu-explain.github.io/roc-auc/) (interactive)
* Google ML Crash Course — [ROC and AUC](https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc)
