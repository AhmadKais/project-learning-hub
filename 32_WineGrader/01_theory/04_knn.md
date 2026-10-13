# Chapter 4 — k-nearest neighbours

💡 **In short:** find the k most similar training wines and let them vote. Closer neighbours vote louder. Votes for rare grades are boosted by alpha. Ties go to the grade of the nearest neighbour. That is the whole algorithm — the rest of the project is making each part right.

## 4.1 The idea

To grade a new wine, find the k wines in the database that are most similar to it, and answer with the grade most of them have. It works because wines with similar chemistry tend to taste similar — not always, but often enough.

It is one of the oldest methods in machine learning (Fix & Hodges, 1951), and Cover & Hart (1967) proved something remarkable about it: with enough data, the error of the 1-nearest-neighbour rule is at most twice the error of the best possible classifier. A simple rule with a strong guarantee.

## 4.2 Distance

"Most similar" means "smallest distance". The project uses the **weighted Minkowski distance**:

    distance(a, b) = ( Σᵢ wᵢ · |aᵢ − bᵢ|ᵖ )^(1/p)

- p = 1 is **Manhattan** distance: the sum of the differences
- p = 2 is **Euclidean** distance: Pythagoras
- wᵢ is the **weight** of feature i: 1 normally, 0 removes the feature, 2 makes it count double

Manhattan is less dominated by one large difference, Euclidean is the natural geometric distance. Both are in the search, and the tuning table decides.

📄 **By hand, p = 2, weights 1**
```
a = (0, 0)   b = (3, 4)
(|0-3|² + |0-4|²) ** (1/2) = (9 + 16) ** 0.5 = 5
```

## 4.3 Skipping the root

The root `^(1/p)` never changes which of two distances is larger — if 25 < 36, then 5 < 6. k-NN only needs to **rank** distances, so the search uses the sum without the root, the "power distance". The root is taken only for the k neighbours that actually vote, where the real distance is needed for the vote weight and for display.

That is why `metrics.py` has both `minkowski_power` and `minkowski`, and why `test_skipping_the_root_keeps_the_order` exists.

## 4.4 The vote

Each of the k neighbours votes for its own grade. Not every vote is equal:

    vote = 1 / (distance + ε)

A neighbour at distance 0.1 votes ten times as loudly as one at 1.0. Without this, three far wines outvote one almost identical wine, which makes no sense. ε (a billionth) only prevents dividing by zero when the distance is exactly 0.

📄 **The vote, for one wine, k = 3**
```
neighbour   grade    distance   vote = 1/d
   1        high       0.10       10.0
   2        medium     0.90        1.1
   3        medium     1.00        1.0
score:  high 10.0,  medium 2.1   ->  HIGH,  confidence 10.0 / 12.1 = 0.83
```

The confidence is simply the winner's share of all the votes.

## 4.5 The imbalance correction

44% of wines are medium, 19% high. Pick a neighbour at random and it is 2.3 times more likely to be medium than high — before anything about the wine itself is considered. k-NN inherits that bias: in a mixed neighbourhood, medium wins by numbers.

The correction divides each vote by the share of its grade, raised to a power alpha:

    vote = vote / prior[grade] ** alpha

| alpha | effect |
|---|---|
| 0 | no correction — `prior ** 0 = 1` |
| 1 | full correction: a high vote is worth 0.44 / 0.19 = 2.3 medium votes, exactly cancelling the bias |
| 0.5 | halfway |

📄 **The same neighbours with alpha = 1, priors low 0.37, medium 0.44, high 0.19**
```
neighbours: medium, medium, high   (all at distance 1)
alpha = 0 :  medium 2.0       high 1.0       -> MEDIUM
alpha = 1 :  medium 2/0.44 = 4.5   high 1/0.19 = 5.3  -> HIGH
```

Too much correction and medium wines get called high; too little and high wines are never found. On the real data alpha = 0.5 keeps macro-F1 the same (0.585 against 0.586) while raising the recall of high-quality wines from 0.45 to 0.61. That is why the tuning rule (chapter 6) prefers it.

❓ **A class never appears in the training rows. What is its prior, and why?**

1.0, not 0. It can never be among the neighbours, so its prior is never actually used — but `0 ** alpha` would be a division by zero waiting to happen if it were. 1.0 is the safe neutral value.

## 4.6 Ties

With an unweighted vote, or by coincidence, two grades can get exactly the same score. `np.argmax` would then always pick the lower grade number — an arbitrary rule that favours "low". The project's rule: **the grade of the nearest neighbour among the tied grades wins.** It is deterministic (same wine, same answer, every time) and it is meaningful (the closest evidence decides).

## 4.7 Choosing k

- **k = 1**: the answer is one wine's grade. One mislabelled wine in the database causes an error every time someone tests a similar wine. And the tasters' scores *are* noisy.
- **k too large**: the neighbourhood stops being local. With k = 500 the answer is nearly always medium.

The tuning table shows the curve — macro-F1 rises quickly from k = 1, flattens around 15–25, and falls slowly after. Your book should show it and explain both ends.

## 4.8 The two baselines

`MajorityClassifier` remembers the most common grade and always answers it. `CentroidClassifier` computes the average wine of each grade and answers with the nearest average. The centroid is the "eager" opposite of k-NN: it summarises each grade into one point and forgets the wines.

| Model | macro-F1 (nested, real data) |
|---|---|
| majority | 0.20 |
| centroid | 0.49 |
| k-NN | 0.58 |

❓ **Why does k-NN beat the centroid here?**

Because one average point per grade cannot describe a grade whose wines are spread over several regions of the space — high-quality whites and high-quality reds have quite different chemistry, and their average is a wine that resembles neither. k-NN keeps every wine and so can follow any shape. The price is memory and search time.

## 4.9 Proving it is right

`test_knn_matches_sklearn` runs your k-NN and scikit-learn's `KNeighborsClassifier(weights="distance")` on the same 400 training points and 200 queries, for p = 1 and p = 2, and demands **identical** answers. It is the blocking test of stage 4. If it fails, compare the neighbours first (your index), then the votes.
