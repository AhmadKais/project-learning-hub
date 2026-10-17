# Lesson 03 — Is the model good? Counting its right and wrong answers

> **For:** Laith · Dani · Seif · Ryan &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 00 §1; Lesson 01

**In one sentence:** sort every answer into four boxes (caught, false alarm, missed, correct-no), and from those four
counts compute numbers that answer different questions: *can I trust it?* and *does it catch everything?*

## The story

> Omar's spam filter (Lesson 01) is ready. It sorted 1,673 new SMS into "inbox" and "spam folder". Omar proudly says: *"97.5 %
> correct!"* Maya asks two sharper questions: **"Did it hide any message from a customer?"** and **"How much spam still reaches
> me?"** One number can't answer both. Let's build the numbers that can.

## Words you need

| word | simple meaning |
|---|---|
| **positive** | the thing we are looking for — spam (in PhishGuard: phishing) |
| **negative** | the other thing — a normal message ("ham") |
| **prediction** | what the model said |
| **truth** | what it really was |

---

## Step 1 — Four boxes

> 📖 Maya checks each SMS: what did the filter say, and what was it really?

| | filter said **SPAM** | filter said **inbox** |
|---|---|---|
| **really spam** | **TP** — spam caught ✓ | **FN** — spam slipped into the inbox ✗ |
| **really a customer** | **FP** — a customer hidden in spam ✗ | **TN** — customer delivered ✓ |

The names: the second letter (P/N) is what the filter **said**; the first (T/F) is whether it was **right**. This table is
called the **confusion matrix**.

**Fill one by hand — 8 SMS:**

```
truth:      S   S   H   H   H   S   H   H          (S = spam, H = ham)
filter:     S   H   H   S   H   S   H   H
box:        TP  FN  TN  FP  TN  TP  TN  TN
count:      TP = 2     FN = 1     FP = 1     TN = 4
```

## Step 2 — The real counts

![confusion matrix anatomy](figs/anatomy.png)

TP = 187 · FN = 37 · FP = 5 · TN = 1,444.

## Step 3 — Three questions, three numbers

> 📖 Maya asks her questions one at a time.

**"How often is it right?" → accuracy**

```
right answers ÷ all answers = (187 + 1,444) ÷ 1,673 = 1,631 ÷ 1,673 = 0.975 → 97.5 %
```

**"When it says spam, can I trust it?" → precision.** Look only at what went to the **spam folder**:

```
TP ÷ (TP + FP) = 187 ÷ (187 + 5) = 187 ÷ 192 = 0.974
```

"Of 192 messages in the spam folder, 187 really were spam." The 5 others are customers Maya never answered.

**"Of all the spam, how much did it catch?" → recall.** Look only at the **real spam**:

```
TP ÷ (TP + FN) = 187 ÷ (187 + 37) = 187 ÷ 224 = 0.835
```

"It caught 83 % of the spam; 37 still reached the inbox."

**Memory trick:** **P**recision looks at what the filter **P**redicted. **R**ecall looks at what was **R**eally there.

## Step 4 — The fishing net: you can't have both for free

> 📖 Maya's cousin is a fisherman. *"If I use a small net, everything I catch is the fish I want — but I miss most of them.
> If I use a huge net, I catch all the fish — and also boots and seaweed."*

![precision and recall as a net](figs/net.png)

Small net → **high precision, low recall**. Huge net → **high recall, low precision**. Which matters more depends on what
each mistake costs (Lesson 04).

## Step 5 — Why "97 % correct" can be a lie

> 📖 Omar's lazy friend writes a "filter" in one line: *always say inbox*. It never catches any spam.

```
it gets every customer right (1,449 of 1,673) → accuracy 1,449 ÷ 1,673 = 86.6 %
it catches 0 spam                              → recall 0
```

86.6 % "correct" and useless — because most messages are normal anyway. When one class is rare, **accuracy alone lies**.

![accuracy trap](figs/accuracy_trap.png)

## Try it yourself

<details><summary>1. TP 90, FP 10, FN 30, TN 870. Accuracy, precision, recall.</summary>

accuracy (90 + 870) ÷ 1000 = **0.96** · precision 90 ÷ 100 = **0.90** · recall 90 ÷ 120 = **0.75**.
</details>

<details><summary>2. Which number matters most for PhishGuard, and which for the spam filter?</summary>

PhishGuard: **recall** — a missed phishing site can empty a bank account. Spam: **precision** — a hidden customer message
is expensive.
</details>

## Common mistakes

| student says | the truth |
|---|---|
| "Precision and recall are the same" | Same top (TP), different bottom: what it flagged vs what was really there. |
| "97 % — done" | First compare with "always say the common answer". |

## Class activities

1. **Be the filter (15 min).** Print 20 real SMS (5 spam). Each student labels them in 3 minutes, then fills their 4 boxes.
   Who had the best precision? The best recall?
2. **COVID test (5 min).** What is a false positive here? A false negative? Which is worse?

## In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/ml/threshold.py` → `confusion_at` · `ModelComparator.confusion_matrix` |
| PhishGuard | `phishguard/ml/evaluator.py` → `ModelEvaluator.metrics` |
| WineGrader | `winegrader/ml/scoring.py` → `confusion_matrix`, `precision_recall_f1`, `macro_f1`, `accuracy` |
| FaceEmotion | `app/ml/evaluator.py` → `evaluate`, `plot_confusion_matrix` |

<details><summary>🎓 <b>For the defence (advanced)</b></summary>

* **F1** combines precision and recall: F1 = 2 × P × R ÷ (P + R) = 2 × 0.974 × 0.835 ÷ 1.809 = **0.899**. It is only high
  when both are high (P = 1, R = 0 gives F1 = 0, not 0.5).
* **The threshold moves all four boxes** — the filter really gives a score, and a line decides:

  ![threshold sweep](figs/threshold_sweep.gif)

* **More than two classes (wine grades, emotions):** row = truth, column = prediction, the diagonal = correct. Compute P, R,
  F1 for each class separately ("this class vs all others"), then **macro-F1** = their plain average, so a small class
  counts as much as a big one:

  ![macro-F1 on wine](figs/macro_f1.png)

  "high": TP 472 · FP 109 + 433 = 542 · FN 248 + 557 = 805 → P 0.465, R 0.370, F1 0.412.
</details>

## 🎬 Watch & explore

* StatQuest — *The Confusion Matrix* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+confusion+matrix)
* MLU-Explain — [Precision & Recall](https://mlu-explain.github.io/precision-recall/)
