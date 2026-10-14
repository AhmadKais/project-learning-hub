# Lesson 17 — Learning how much each feature matters: coordinate search

> **For:** Seif (WineGrader stage 6) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lessons 02, 05, 15 &nbsp;·&nbsp; **After this:** the tuning / results chapter of the book

## The story

> A wine expert tells Sami: *"For quality, alcohol matters a lot; chlorides (salt) hardly at all."* Right now Sami's k-NN
> treats all 11 measurements as **equally important** in the distance. Could the computer find, from the data, how much
> each measurement should count? Think of a **sound mixer** with 11 volume knobs, one per feature: turn a knob up and that
> feature counts more in "similar"; turn it to 0 and it is ignored. This lesson is how the computer turns the knobs — and
> the honest answer it found.

## 🎯 By the end, the student can

1. Explain what a feature weight does to the distance (and that weight 0 = the feature is removed).
2. Explain with the staircase picture why gradient descent can't be used here.
3. Run coordinate search by hand on a small table of trials.
4. Explain the incremental update and check it with numbers.
5. Report an honest "it didn't help" result.

## Words you need

| word | meaning |
|---|---|
| **feature weight wᵢ** | how much feature i counts in the distance; 1 = normal, 2 = double, 0 = ignored |
| **cross-validated score** | the average macro-F1 over the folds (Lessons 03, 05) |
| **coordinate search** | change one weight at a time, keep a change only if the score improves |
| **pass** | one round through all 11 features |
| **tolerance** | the minimum improvement we accept (0.002) — smaller ones are probably luck |
| **incremental update** | changing the stored distances instead of computing them all again |

---

## 1. What a weight does

$$d(a, b) = \Big(\sum_i w_i\,|a_i - b_i|^p\Big)^{1/p}\qquad\text{(Lesson 15, with weights)}$$

Two wines differ by 1.0 in alcohol and 1.0 in chlorides (scaled units), p = 2:

```
weights (1, 1):     1 × 1² + 1 × 1² = 2      distance √2 = 1.41
weights (2, 1):     2 × 1² + 1 × 1² = 3      distance √3 = 1.73   (alcohol counts double)
weights (1, 0):     1 × 1² + 0 × 1² = 1      distance √1 = 1.00   (chlorides ignored)
```

## 2. Why not gradient descent?

![the score is a staircase](figs/staircase.png)

Gradient descent (Lessons 12, 21) needs a smooth hill to walk down. Here, turn one knob a tiny bit: either **no**
neighbour changes (the score stays exactly the same — flat) or one neighbour swaps (the score **jumps**). The score is a
staircase — there's no slope to follow. We need a method that only **compares scores**.

## 3. Coordinate search — one knob at a time

![coordinate search](figs/coordinate_search.gif)

```
all weights = 1;  best = score(weights)
repeat (at most 3 passes):
    for each feature i that is not already 0:
        for factor in ×0, ×0.5, ×1.5, ×2:
            try weight i × factor;  s = cross-validated score
            if s > best + 0.002:  keep it, best = s, go to the next feature
    if a whole pass changed nothing: stop
```

### By hand — a made-up first pass with 3 features

Start: weights (1, 1, 1), best = 0.560.

```
feature 1 (alcohol):  ×0 → 0.541   ×0.5 → 0.552   ×1.5 → 0.565  (0.565 > 0.560 + 0.002 ✓ keep)
                      weights (1.5, 1, 1), best 0.565
feature 2 (acidity):  ×0 → 0.548   ×0.5 → 0.563   ×1.5 → 0.566 (not > 0.567 ✗)   ×2 → 0.562    → no change
feature 3 (chlorides):×0 → 0.570  (0.570 > 0.567 ✓ keep)
                      weights (1.5, 1, 0), best 0.570          ← chlorides removed: feature selection for free
pass 1 changed something → do pass 2 …
```

**Why the 0.002 tolerance?** With ~1,400 wines per fold, one wine changing grade moves macro-F1 by about 0.001.
Accepting smaller "improvements" means fitting which wines happen to be in which fold — luck, not wine.

**Analogy:** tuning an old radio with several knobs — turn one, listen; keep it if it's clearer; move to the next.

## 4. Making it fast — the incremental update

Every trial needs the distances between every test wine and every training wine, in every fold. Computing them from
scratch took ~2.8 seconds per trial — with hundreds of trials, far too slow.

The insight: the distance (before the root) is a **sum over features**. Changing one weight changes only **one term**:

$$D_{\text{new}} = D + (w_{\text{new}} - w_{\text{old}})\times|\Delta_i|^p$$

![incremental update](figs/incremental.png)

### Check it with numbers

One pair of wines: differences per feature (2, 1), p = 2, weights (1, 1).

```
D = 1 × 2² + 1 × 1² = 4 + 1 = 5
change weight 2 from 1 to 3:
   incremental:   D_new = 5 + (3 − 1) × 1² = 5 + 2 = 7
   from scratch:  1 × 4 + 3 × 1 = 7   ✓ the same
```

One addition instead of recomputing all 11 features → Seif's run dropped from ~5 minutes to ~20 seconds.
`test_incremental_matches_full_recompute` checks that the fast way gives exactly the slow way's score.

## 5. Callbacks — small helpers that listen

After every pass, the loop tells its helpers "round finished, here is the score and the weights": `HistoryLogger` (for the
chart), `Checkpoint` (saves the best weights safely), `EarlyStopping` (says when to stop). The loop doesn't need to know
about files or charts. This is the **Observer pattern**.

## 6. The honest result

| weights | nested macro-F1 (real data, Seif's guide) |
|---|---|
| all equal | 0.583 ± 0.018 |
| learned | 0.579 ± 0.015 |

Inside the inner folds the learning helped a little (0.581 → 0.585); on the untouched outer folds the gain **disappeared**.
That's overfitting to the inner folds — exactly what nested CV (Lesson 05) is built to catch. The conclusion for the book:
*once the features are scaled, no wine feature is useless or dominant enough for re-weighting to help.* On data with pure
noise columns (a test), the same code finds and removes them.

## 7. Common mistakes

| student says | the truth |
|---|---|
| "The learned weights are better — the inner score went up" | Only the outer (nested) score counts. |
| "Try every combination of weights" | 4¹¹ ≈ 4 million combinations × CV — impossible. Coordinate search tries ~100. |
| "The incremental update is an approximation" | It's exact — §4 checks it. |

## 8. Activities

1. **The mixer (5 min).** Any music app's equaliser: tune one slider at a time to make a song clearer.
2. **Paper update (10 min).** Give a 2 × 3 distance table and the table of one feature's squared differences; students
   compute the new table for weight 0.5, then check one cell from scratch.
3. **Noise test (10 min).** Add two random columns in the notebook; run coordinate search; watch their weights go to 0.

## 9. Do it yourself

<details><summary>1. D = 2.0 between two wines (weights 1); the pH term |Δ|² is 0.5. D after setting pH's weight to 0?</summary>

2.0 + (0 − 1) × 0.5 = **1.5**.
</details>

<details><summary>2. Best 0.570. A trial scores 0.571. Keep it?</summary>

No: 0.571 is not > 0.570 + 0.002 = 0.572.
</details>

<details><summary>3. Learned 0.579, equal 0.583 ± 0.018. Did learning make it worse?</summary>

No — the difference (0.004) is far smaller than the jump between folds (0.018): a tie. The conclusion is "re-weighting
doesn't help on this data", and why.
</details>

## 10. In your project

| Project | Where |
|---|---|
| WineGrader | `winegrader/ml/weights.py` → `cv_score`, `neighbours_from_matrix`, `FoldDistances` (`term`, `score`), `learn_weights` · `ml/callbacks.py` → `EarlyStopping`, `HistoryLogger`, `Checkpoint` · `ml/evaluation.py` → `nested_cv` · theory `32_WineGrader/01_theory/06_tuning_weights.md` · notebook `05_feature_weights.ipynb` |

## 🎬 Watch & explore

* *Coordinate descent explained* — [search on YouTube](https://www.youtube.com/results?search_query=coordinate+descent+optimization+explained)
* Refactoring Guru — [The Observer pattern](https://refactoring.guru/design-patterns/observer)
