# Chapter 20 — Answers

💡 Short answers to chapter 17. Say them in your own words — a memorised answer sounds memorised.

## The algorithm

**1.** Find the k training wines closest to the new one and answer with the grade they vote for. Lazy, because it does no work at training time — it stores the wines and does everything when asked.

**2.** `(Σ wᵢ · |aᵢ − bᵢ|ᵖ)^(1/p)`. p = 1 is Manhattan (sum of differences), p = 2 is Euclidean (Pythagoras).

**3.** `x^(1/p)` is increasing, so it never changes which distance is smaller, and ranking is all the search needs. The root is taken only for the k neighbours, for the vote weight and for display.

**4.** So a nearly identical wine counts more than a distant one. Without it, three far wines outvote one almost identical wine.

**5.** `vote / prior[grade] ** alpha`. alpha = 0: no correction. alpha = 1: a vote for a grade is scaled by the inverse of its share, exactly cancelling the fact that common grades appear more often among neighbours.

**6.** It can never be among the neighbours, so its value is never used — but 0 would mean dividing by zero. 1 is the neutral value.

**7.** The grade of the nearest neighbour among the tied grades wins. `argmax` would always favour the lowest grade number — arbitrary — and the nearest-neighbour rule is both deterministic and meaningful.

**8.** k = 1: one mislabelled or noisy wine decides every similar query. k = 500: the neighbourhood is no longer local and the answer drifts to the majority grade.

**9.** From training rows only: the scaler's parameters, the class priors, and a weight for each feature (coordinate search). The hyper-parameters k, p, alpha and the scaling are chosen by grid search.

**10.** `test_knn_matches_sklearn` — identical answers to scikit-learn's distance-weighted k-NN on 200 queries, for p = 1 and p = 2.

## Data

**11.** Scores 3, 4, 8, 9 have too few wines to learn as classes (five wines of score 9 in total), and three grades are what a wine maker needs.

**12.** Because a copy in training and its twin in testing are each "unique" within their own part. Removing them first is the only way to guarantee no wine is tested against its own copy. Otherwise the score is inflated.

**13.** The twin is the nearest neighbour at distance zero, with the right answer — the model looks the answer up instead of predicting it.

**14.** The features have very different ranges; without scaling the distance is decided by the feature with the largest numbers (sulfur dioxide). Measured: macro-F1 0.45 unscaled, 0.58 with z-score.

**15.** z-score. One extreme wine (total SO₂ = 440) stretches min-max's range and squeezes every other wine into a small part of it; z-score is far less affected. Both were in the search and the tuning table decided.

**16.** The mean and std are learned from data; fitting them on test rows lets the test set shape the model — leakage.

**17.** The one saved in the bundle from training. Never a new one — the new wine must be in the same coordinate system as the training wines.

**18.** It is rejected with its line number and the reason ("ph = 19 is outside the valid range 0.0..14.0"); the rest of the file is loaded. One typo should not lose 5,000 good lines, and silently skipping it would hide a damaged file.

## The kd-tree

**19.** Choose the axis with the largest (weighted) spread, sort the points on it, cut at the middle position, recurse until 16 or fewer points. By position because with many equal values "< median" can put everything on one side and never terminate.

**20.** An axis with weight 0 adds nothing to any distance, so a split on it could never prune anything.

**21.** Every point on the far side differs from the query by at least |diff| on that axis, so its power distance is at least `w · |diff|ᵖ` — the other axes can only add. If even that exceeds the current k-th best, nothing there can enter the result.

**22.** A far point at exactly the k-th distance with a smaller row number must still be reachable, so that ties come out exactly as in the linear search.

**23.** `heapq` is a min-heap; negating makes the root the *worst* of the k best — the one to compare with and replace.

**24.** `test_kdtree_matches_linear`: 1,000 random queries, uniform and mixed weights (including zeros), p = 1 and 2 — identical neighbours.

**25.** Too few cuts per axis (a tree ~8 levels deep for 12 axes) and concentrating distances, so the k-th best distance stays large and `gap` rarely exceeds it. The dimension curve shows pruning fall from ~2% at 2 features to ~54% at 12.

**26.** The project's claim is how to decide, not that the tree wins. It is implemented, proven correct and measured; the measurement — and the dimension curve explaining it — chose the linear index. On a 4-feature model the same tree would measure under 10% of the wines.

## Tuning and weights

**27.** For a fixed scaling, p and weights, the neighbours do not depend on k or alpha. Find them once up to k = 31; every (alpha, k) pair is just a vote over the first k columns.

**28.** Among configurations within 0.005 macro-F1 of the best — a difference smaller than fold noise — take the one with the highest recall of high-quality wines. Fixed before the final measurement. On the data: alpha 0.5 keeps macro-F1 (0.585 against 0.586) and raises high recall from 0.45 to 0.61.

**29.** The score is not a smooth function of the weights — it is flat, then jumps when a neighbour changes. There is no gradient to follow.

**30.** The weighted distance is a sum over features, so changing wᵢ changes every distance by `(w_new − w_old) · |Δᵢ|ᵖ`. One pass instead of twelve. `test_incremental_matches_full_recompute` checks the final score equals a from-scratch computation.

**31.** Accepting changes that only reflect which wines are in which fold — one wine changing grade moves macro-F1 by about 0.001.

**32.** After scaling, no feature is so useless or dominant that reweighting helps; the small inner-fold gain was overfitting, and the outer folds showed it. Kept because it is a correct method, correctly evaluated — and on data with truly irrelevant features (the noise-feature test) it finds them.

**33.** HistoryLogger (convergence plot, database), Checkpoint (best weights saved safely), EarlyStopping (stop when a round, or three k values, bring no real improvement).

## Evaluation

**34.** 44% of wines are medium: always-medium is 44% accurate but scores 0.20 macro-F1. Accuracy hides the small class; macro-F1 does not.

**35.** Per grade: precision = correct ÷ predicted as that grade; recall = correct ÷ truly that grade; F1 = 2PR/(P+R). Macro-F1 = plain mean of the three F1s.

**36.** So every fold has the same grade mix; otherwise a fold with few high wines gives an F1 that measures the cut, not the model.

**37.** A score reported for the configuration chosen on the same folds is optimistic. Nested: the inner loop chooses on outer-training rows only; the outer test fold is touched once. Proof: scramble the outer test labels — the chosen parameters and weights stay identical.

**38.** Running it again after seeing the result makes the outer folds part of the tuning, and the honest number stops being honest.

## Architecture and security

**39.** Each weight is applied to the wrong feature; every array still has 12 entries, nothing crashes, every answer is silently wrong. `model.json` stores the names, and `bundle.load` compares them one by one with `config.FEATURES`.

**40.** Any four of: hostile CSV (validation, line-level rejection, size limit); SQL injection (placeholders only); modified bundle (SHA-256); code execution (JSON, no pickle); data poisoning (manual wines unapproved until checked); leakage (the four guards).
