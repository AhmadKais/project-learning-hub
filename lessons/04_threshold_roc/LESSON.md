# Lesson 04 — Where do we draw the line? Thresholds and the ROC curve

> **For:** Laith (spam threshold) · Dani (PhishGuard threshold, ROC) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 03

**In one sentence:** a model gives each example a **score** from 0 to 1; **people** choose the line (threshold) above which
we say "yes" — and the right line depends on which mistake costs more.

## The story

> **Rana works at a bank.** Customers forward her strange links: *"Is this really the bank?"* The bank's new program gives
> every link a **danger score** from 0 to 1. Rana's boss asks: *"From what score do we block a link?"*
> If they block only above 0.9, some fake links get through and a customer may lose her savings. If they block everything
> above 0.1, half of the normal websites are blocked and customers call angrily. The program can't decide this. **Rana must.**

## Words you need

| word | simple meaning |
|---|---|
| **score** | the model's number for one link, 0 … 1: "how dangerous it looks" |
| **threshold** | the line: score ≥ threshold → block |
| **catch rate (recall)** | of all the fake links, the share we block (Lesson 03) |
| **false-alarm rate** | of all the **good** links, the share we block by mistake |
| **ROC curve** | a picture of catch rate vs false-alarm rate for **every** threshold |
| **AUC** | one number for how good the scores are: 0.5 = useless, 1 = perfect |

---

## Step 1 — Ten links, one line

> 📖 Rana tests on 10 links where she knows the truth. She sorts them by score.

```
link:    1     2     3     4     5     6     7     8     9     10
score:  0.95  0.90  0.80  0.70  0.60  0.45  0.40  0.30  0.20  0.10
truth:  fake  fake  good  fake  fake  good  fake  good  good  good
```

5 fake (1, 2, 4, 5, 7) and 5 good (3, 6, 8, 9, 10).

**Line at 0.65** → block links 1, 2, 3, 4:

```
fake ones blocked: 1, 2, 4 → 3 of 5 → catch rate 0.6
good ones blocked: 3       → 1 of 5 → false-alarm rate 0.2
```

**Line at 0.35** → block links 1 to 7:

```
fake blocked: 1, 2, 4, 5, 7 → 5 of 5 → catch rate 1.0
good blocked: 3, 6          → 2 of 5 → false-alarm rate 0.4
```

Lower line → catch more fakes **and** more false alarms. Every line is a trade.

## Step 2 — Try every line: the ROC curve

> 📖 Rana tries every possible line, one link at a time, and marks each result as a point on squared paper: across = false
> alarms, up = catches.

```
line just below link:  none  1    2    3    4    5    6    7    8    9    10
catch rate:             0   .2   .4   .4   .6   .8   .8   1.0  1.0  1.0  1.0
false-alarm rate:       0    0    0   .2   .2   .2   .4   .4   .6   .8   1.0
```

Every **fake** link moves the point **up** (good!). Every **good** link moves it **right** (bad). Join the points: that's the
**ROC curve**.

![ROC being built](figs/roc_build.gif)

The same thing on real PhishGuard URLs: as the line slides down (left), the point draws the curve (right).

## Step 3 — What a good curve looks like

![ROC shapes](figs/roc_shapes.png)

A good model gives fake links high scores and good links low scores — the two piles don't overlap, and the curve shoots
straight up first (top-left corner). A useless model mixes them — the curve is the diagonal.

**AUC** = the area under the curve. For Rana's 10 links it is **0.84**. Simple meaning: *take one fake and one good link at
random — AUC is the chance the fake one got the higher score.* (21 of the 25 possible pairs are in the right order: 21 ÷ 25 =
0.84.)

## Step 4 — Choosing the line: which mistake hurts more?

> 📖 The bank and Maya's phone shop face the same question with opposite answers.

![the two rules](figs/rules.png)

| | Laith's spam filter | Dani's PhishGuard |
|---|---|---|
| the painful mistake | hiding a customer's message | letting a fake bank link through |
| so we demand | precision ≥ 0.98 | catch rate ≥ 0.95 |
| then pick | the line that catches the most spam | the highest line (fewest false alarms) |

Both are chosen on the **practice pile** (validation), never on the final test (Lesson 01).

## Try it yourself

<details><summary>1. Rana's links, line at 0.5. Catch rate and false-alarm rate?</summary>

blocked 1–5 · fake blocked 1, 2, 4, 5 → **0.8** · good blocked 3 → **0.2**.
</details>

<details><summary>2. A model's AUC is 0.5. What does that mean?</summary>

Its scores are no better than a coin flip.
</details>

## Common mistakes

| student says | the truth |
|---|---|
| "The model decides" | It gives scores; people choose the line. |
| "AUC 0.97 = 97 % correct" | AUC is about the order of the scores, not about one line. |

## Class activities

1. **Human ROC (15 min).** Hand out the 10 link cards. Walk the line down card by card; plot each point on squared paper;
   count the squares under the curve.
2. **Bank vs news site (5 min).** Role-play: who wants a low line, who a high one?
3. `python visualize.py --live` — slide the line yourself.

## In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/ml/threshold.py` → `choose_threshold` (precision ≥ 0.98) |
| PhishGuard | `phishguard/ml/evaluator.py` → `ModelEvaluator.choose_threshold` (recall ≥ 0.95), `compare` · exercises ex10–ex12 |

<details><summary>🎓 <b>For the defence (advanced)</b></summary>

* **Laith's algorithm:** for t = 0.50, 0.51 … 0.99 compute precision and recall on validation; keep the t with precision ≥
  0.98 and the highest recall; if none reaches 0.98, **raise an error** (never silently use 0.5).
  Dani: if no line reaches 0.95, fall back to `config.DEFAULT_THRESHOLD`.
* **AUC as pairs on real URLs:**

  ![AUC as pairs](figs/auc_pairs.png)

* **Cost decides:** give each mistake a price; the cheapest line moves left when a missed phish is expensive. 0.5 and
  "best F1" both pretend the mistakes cost the same.

  ![cost curves](figs/cost.png)
</details>

## 🎬 Watch & explore

* StatQuest — *ROC and AUC, Clearly Explained!* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+ROC+and+AUC+clearly+explained)
* MLU-Explain — [ROC & AUC](https://mlu-explain.github.io/roc-auc/)
