# Lesson 13 — Decision trees and random forests: a flow chart that writes itself

> **For:** Dani (PhishGuard — second model, feature importance) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 00 §1, §4; Lessons 01, 03, 12 &nbsp;·&nbsp; **After this:** comparing the two models (Lesson 04)

## The story

> New staff at the bank's help desk don't know Rana's points system. So Rana draws them a **flow chart**: *"Is there
> HTTPS? No → is a brand name in front of the real domain? Yes → block it."* It's easy to follow and explain. But which
> question should come first? Which ones after? A **decision tree** builds this flow chart by itself, from thousands of
> labelled URLs — and a **random forest** asks a hundred slightly different flow charts and lets them vote.

## 🎯 By the end, the student can

1. Read a decision tree and follow one URL down to its answer.
2. Compute Gini impurity and the gain of a split by hand, and explain how the tree chooses its question.
3. Explain, with the animation, why a very deep tree overfits.
4. Explain the two random ingredients of a forest and why voting helps.
5. Read a feature-importance chart — and say what it does **not** tell you.

## Words you need

| word | meaning |
|---|---|
| **node** | one question in the flow chart: "is num_digits ≤ 9.5?" |
| **split** | dividing a group of URLs into two by one question |
| **leaf** | an end of the flow chart: the answer for everyone who reaches it |
| **depth** | how many questions in a row, from the top to the deepest leaf |
| **pure group** | everyone in it has the same label |
| **Gini impurity** | how mixed a group is: 0 = pure, 0.5 = half-half |
| **gain** | how much a split reduces the mixing |
| **bootstrap sample** | a random sample of the rows, drawn *with replacement* (some twice, some not at all) |
| **random forest** | many trees, each from its own bootstrap sample and random features; they vote |
| **feature importance** | how much each feature helped the trees' splits, in total |

---

## 1. A tree is a flow chart

![a real depth-3 tree](figs/tree_diagram.png)

This tree was learned from the 20 PhishGuard features of real URLs (orange = mostly phishing, blue = mostly legitimate).
**Follow one URL from the top:**

1. "digit_ratio ≤ 0.013?" — a URL with many digits → **False** → go right.
2. "num_digits ≤ 9.5?" → it has 14 digits → **False** → right.
3. "num_hyphens ≤ 2.5?" → 1 hyphen → **True** → left.
4. Leaf: 1,036 training URLs ended here, **986 of them phishing** → answer: phishing (986 / 1,036 = 95 %).

Trees can learn **combinations** a points system can't: "hyphens matter only when there are many digits". And they need no
scaling — a question like "≤ 9.5?" doesn't care about units.

## 2. How the tree chooses its question — Gini impurity

The tree wants questions that **separate** phishing from legitimate as cleanly as possible. To measure "cleanly" it uses
**Gini impurity**:

$$\text{Gini} = 1 - (\text{share of class 1})^2 - (\text{share of class 2})^2$$

```
a group of 10 URLs, all phishing:     shares 1.0 and 0.0  →  1 − 1.0² − 0.0² = 1 − 1 − 0       = 0     (pure)
5 phishing, 5 good:                   shares 0.5 and 0.5  →  1 − 0.25 − 0.25                   = 0.5   (worst)
8 phishing, 2 good:                   shares 0.8 and 0.2  →  1 − 0.64 − 0.04                   = 0.32
```

![Gini](figs/gini.png)

### Choosing between two questions (Dani's guide)

10 URLs: 5 good, 5 phishing. Gini of the whole group = 0.5.

**Question A: "has HTTPS?"**

```
yes-group: 4 good, 1 phishing → shares 0.8, 0.2 → Gini = 1 − 0.64 − 0.04 = 0.32
no-group:  1 good, 4 phishing → Gini = 0.32
weighted average (each group is half the URLs):  0.5 × 0.32 + 0.5 × 0.32 = 0.32
gain = 0.5 − 0.32 = 0.18
```

**Question B: "more than 2 dots?"**

```
yes-group: 3 good, 3 phishing → Gini 0.5
no-group:  2 good, 2 phishing → Gini 0.5
weighted: 0.6 × 0.5 + 0.4 × 0.5 = 0.5        gain = 0.5 − 0.5 = 0
```

Question A separates; question B doesn't → the tree asks about HTTPS first. Then it does the same thing again **inside
each group** — that's how the whole flow chart grows. (The computer tries every feature and every possible cut point.)

## 3. Watch a tree overfit

![tree growing](figs/tree_growing.gif)

*(A toy dataset you can see in 2-D.)* Each colour region is "what the tree would answer here".

* **Depth 1:** one question, one straight cut. Too simple.
* **Depth 5:** a sensible shape. Test accuracy 0.89.
* **No limit:** 101 leaves, tiny boxes around single points. **100 % on training**, 0.85 on test — it memorised
  (Lesson 01).

The brakes: `max_depth` (how many questions in a row) and `min_samples_leaf` (a leaf needs at least that many URLs) —
chosen by cross-validation (Lesson 05).

## 4. Random forest — ask a hundred colleagues

![forest](figs/forest_vote.png)

Breiman's idea (2001): grow **many** trees, each a bit different, and let them **vote** (or average their probabilities).
Each tree is made different in two ways:

1. **Bootstrap sample:** draw N rows **with replacement**. Example with 5 URLs (A–E): one tree might get A, A, C, D, E
   (B missing, A twice), another B, C, C, D, E. About a third of the rows are left out of each tree.
2. **Random features:** at each question, the tree may only choose among a random few features.

Each tree makes its own mistakes; when you average, **different mistakes cancel**, the common truth remains.

![more trees](figs/forest_growing.gif)

**Analogy — guess the number of sweets in a jar.** Each student is far off; the **class average** is usually close —
*if they guessed independently*. The two random ingredients are what keep the trees independent.

## 5. Feature importance

![importance](figs/importance.png)

For each feature: add up how much Gini it removed, over all the splits of all 300 trees. On the real URLs (test accuracy
≈ 0.85 with default settings), `entropy`, `host_length`, `path_length` and `url_length` help most. (The single tree in §1 started with digits — a forest spreads the work over many features.)

⚠️ What importance does **not** tell you: the **direction** (do many digits mean phishing, or legitimate?) and the reason
for **one** URL. That's why PhishGuard's explanation for the forest is only an approximation, while for logistic
regression it is exact (Lesson 12).

## 6. Common mistakes

| student says | the truth |
|---|---|
| "100 % on training — perfect tree" | It memorised. Look at the test curve. |
| "A forest is one big tree" | Many independent trees + a vote. |
| "More trees can overfit" | More trees only cost time. Depth and leaf size are what overfit. |
| "Important feature = it *causes* phishing" | Only "it helped separate in this data". |

## 7. Activities

1. **20 questions (5 min).** One student thinks of an animal; the class asks yes/no questions. Which first question splits
   best? That's Gini gain.
2. **Build a tree by hand (20 min).** 10 cards with 3 URL features + label. Groups compute the Gini gain of 3 candidate
   questions, choose the best, then split once more.
3. **Sweets jar (5 min).** Collect guesses, compare the average with the truth.

## 8. Do it yourself

<details><summary>1. A group: 6 phishing, 2 good. Gini?</summary>

shares 0.75 and 0.25 → 1 − 0.5625 − 0.0625 = **0.375**.
</details>

<details><summary>2. Parent: 4 phishing, 4 good. A question gives (4 ph, 1 good) and (0 ph, 3 good). Gain?</summary>

parent 0.5 · left: 0.8/0.2 → 0.32 · right: pure → 0 · weighted: 5/8 × 0.32 + 3/8 × 0 = 0.2 · gain **0.3**.
</details>

<details><summary>3. Why does every tree in the forest get a different sample?</summary>

So they make different mistakes. Identical trees would vote identically and averaging would change nothing.
</details>

## 9. In your project

| Project | Where |
|---|---|
| PhishGuard | exercise `ex09_gini_gain` · `phishguard/ml/trainer.py` → `ModelTrainer.build_forest`, `fit_with_search` · `ml/evaluator.py` → `importances`, `compare` · theory `25_PhishGuard/01_theory/04_models.md` §4.5–4.7 · notebook `02_models.ipynb` |

## 🎬 Watch & explore

* R2D3 — [A visual introduction to machine learning](https://r2d3.us/visual-intro-to-machine-learning-part-1/) (a tree, scroll-animated)
* MLU-Explain — [Decision Trees](https://mlu-explain.github.io/decision-tree/) and [Random Forest](https://mlu-explain.github.io/random-forest/)
* StatQuest — *Decision Trees* · *Random Forests* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+decision+trees+random+forests)
