# Chapter 6 — Tuning, and teaching k-NN to weigh its features

💡 **In short:** a grid search picks k, p, alpha and the scaling; a fixed rule picks among near-ties. Then coordinate search learns a weight per feature, made fast by updating the distance matrix instead of recomputing it. On this data the weights barely help — and explaining why is part of the result.

## 6.1 The grid

| Hyper-parameter | Values tried |
|---|---|
| scaling | z-score, min-max |
| p | 1, 2 |
| alpha | 0, 0.5, 1 |
| k | 1, 3, 5, …, 31 |

2 × 2 × 3 × 16 = 192 combinations, each scored by macro-F1 averaged over 3 inner folds.

## 6.2 The trick that makes it cheap

For a fixed scaling, p and weights, a wine's neighbours do not depend on k or alpha. So for each fold the neighbours are found **once**, up to k = 31, and every (alpha, k) pair is just a different vote over the first k columns of the same table:

    find the 31 nearest neighbours once          expensive (distances)
    vote with k = 1..31 and alpha = 0, 0.5, 1    cheap (a few array operations)

192 full evaluations become 4. The whole grid runs in about 5 seconds on the real data.

## 6.3 Early stopping in the k sweep

For each (scaling, p, alpha), k goes up from 1. If three k values in a row bring no improvement, the sweep stops — the curve has flattened and is falling. That is `EarlyStopping(patience=3)`.

## 6.4 The choice — not simply the highest score

On the real data, two configurations score almost the same:

| alpha | macro-F1 | recall of high wines |
|---|---|---|
| 0 | 0.586 | 0.45 |
| 0.5 | 0.585 | 0.61 |

The difference in macro-F1 is 0.001 — less than the difference between two random sets of folds. Calling the first one "better" is reading noise. So the rule, `choose_configuration`, is:

1. find the top macro-F1
2. keep every configuration within 0.005 of it — these are equally good
3. among them, take the one with the highest recall on high-quality wines

The rule was fixed before the final measurement and is written in the proposal. A rule invented after seeing the test results would be a way of choosing the answer you wanted.

❓ **Why recall of the high class as the tie-breaker, and not precision?**

Because the business question is "which wines are good?". A grader that misses most of the good wines is useless for that, however precise it is on the few it names. Among models that are equally good overall, the one that finds more good wines is the more useful one. Precision still matters — it is inside macro-F1, which already decided the shortlist.

## 6.5 Feature weights — what they are

Each feature gets a weight wᵢ ≥ 0 inside the distance (chapter 4). A weight of 2 on alcohol means a difference of one standard deviation in alcohol counts like two. A weight of 0 on pH removes pH entirely.

The weights change who the neighbours are, so they change every answer. Choosing them to score as well as possible is genuine learning: parameters fitted to training data to minimise an error.

## 6.6 Coordinate search

The score (macro-F1 of a k-NN) is not a smooth function of the weights: nudge one weight slightly and either no neighbour changes and the score stays exactly the same, or one neighbour swaps and the score jumps. There is no slope, so gradient descent has nothing to follow. Instead:

1. start with every weight at 1
2. for each feature in turn, try its weight × 0, × 0.5, × 1.5, × 2
3. keep a change only if the cross-validated score improves by **more than 0.002**
4. repeat the pass; stop when a whole pass changes nothing (early stopping, patience 1), or after 3 passes

A weight that reaches 0 removes its feature and stays removed — feature selection for free.

❓ **Why the 0.002 tolerance?**

With 3 folds of ~1,400 wines, one wine changing grade moves macro-F1 by roughly 0.001. Accepting changes that small means accepting changes caused by which wines happen to be in which fold — fitting the folds, not the wine. The tolerance demands a real improvement.

## 6.7 Making it fast — the incremental update

Each trial needs the score with the new weights, which means the distances from every test wine to every training wine of every fold. Recomputing them from scratch for each trial took about 2.8 seconds per trial; a learning run needs ~100 trials per fold set, and the nested evaluation 5 of those runs. Far too slow.

The insight: the weighted distance is a **sum over features**. Changing one weight changes every entry of the distance matrix by that feature's term only:

    D_new = D + (w_new − w_old) · |Δᵢ|ᵖ

where |Δᵢ|ᵖ is the matrix of that one feature's differences. One pass over the matrix instead of twelve, plus the neighbour search. `FoldDistances` keeps D for each fold and applies this update; accepted trials replace D, rejected ones are thrown away. A learning run on the real data fell from about five minutes to about twenty seconds.

📄 **The core of learn_weights**
```python
terms = [fd.term(i) for fd in fds]              # |Δi|^p, once per feature
for factor in factors:
    new = w[i] * factor
    trial_D = [fd.D + (new - w[i]) * t for fd, t in zip(fds, terms)]
    score = mean(fd.score(D, params) for fd, D in zip(fds, trial_D))
    if score > best + tolerance:
        best, w[i] = score, new
        for fd, D in zip(fds, trial_D):
            fd.D = D                             # accept
```

A fast version you cannot trust is worthless, so `test_incremental_matches_full_recompute` checks that the score after learning equals `cv_score` computed from scratch with the final weights. If an update was applied twice or not at all, that test fails.

## 6.8 Callbacks

The learning loop does not know about files, logs or stopping rules. At the end of each round it calls `on_round_end(round, score, weights)` on every callback it was given:

- **HistoryLogger** — keeps every round, for the convergence plot and the database
- **Checkpoint** — writes the best weights so far to `models/checkpoint.json` (to a `.tmp` file first, then renamed, so a crash never leaves half a file)
- **EarlyStopping** — decides when another round is not worth it

This is the Observer pattern, and the same idea as Keras callbacks. The ministry requires "callbacks used with a justification"; the justification of each is above.

## 6.9 The honest result

On the real data, the nested evaluation gives:

| Weights | macro-F1 |
|---|---|
| uniform | 0.583 ± 0.018 |
| learned | 0.579 ± 0.015 |

The learned weights do **not** beat uniform weights — the difference is a fifth of the fold-to-fold spread. Inside the inner loop the learning did improve the score slightly (0.581 → 0.585); on the untouched outer folds that small gain disappeared. That is overfitting to the inner folds, in miniature, and it is exactly what nested cross-validation is designed to reveal.

❓ **So why keep the weight learning?**

Because it is a correct method, correctly evaluated, and the evaluation says something true about this data: once the features are scaled, no feature is so useless or so dominant that reweighting it helps k-NN. The correlation table of stage 2 already hints at it — apart from alcohol, every feature is weakly related to quality, and they are related to each other. On data with genuinely irrelevant features (the test with two pure-noise features) the same code finds them and down-weights them. Reporting "it did not help, and here is why" is a stronger result than hiding the number.
