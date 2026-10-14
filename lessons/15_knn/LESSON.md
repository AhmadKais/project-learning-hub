# Lesson 15 — k-nearest neighbours: "tell me who your neighbours are"

> **For:** Seif (WineGrader stage 4 — the heart of the project) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lessons 02, 03, 05 &nbsp;·&nbsp; **After this:** Lesson 16 (kd-tree), Lesson 17 (feature weights)

## 🎯 By the end, the student can

1. Explain k-NN in one sentence and run it by hand on a small table.
2. Compute a weighted Minkowski distance (p = 1 and p = 2), and explain why the root can be skipped for ranking.
3. Compute the **weighted vote** and its confidence, and apply the **imbalance correction** with alpha.
4. Explain with pictures what a small and a large k do.

---

## 1. The idea

To grade a new wine, find the **k most similar wines** we already graded and let them vote. There is no training — the
"model" *is* the stored data (a **lazy** learner). All the work happens at prediction time.

![k-NN on the real wines](figs/knn_query.gif)

Two of the 11 features (alcohol and volatile acidity, z-scored). The star is a new wine; the dashed circle grows as k
grows; on the right, the weighted vote. **Watch the answer change with k**: k = 1 says *high* (one very close high wine),
k = 15 says *medium*.

## 2. Distance

$$d(a,b)=\Big(\sum_i w_i\,|a_i-b_i|^p\Big)^{1/p}\qquad p=1\text{ Manhattan},\ p=2\text{ Euclidean},\ w_i=\text{feature weight}$$

![Minkowski circles](figs/minkowski.png)

By hand, p = 2, weights 1: a = (0, 0), b = (3, 4) → (9 + 16)^½ = **5**. With p = 1: 3 + 4 = **7**.

**Skip the root** for the search: if 25 < 36 then 5 < 6 — the order is the same. Seif's `minkowski_power` ranks;
`minkowski` (with the root) is only computed for the k winners (`test_skipping_the_root_keeps_the_order`).

⚠️ Scale first (Lesson 02) — otherwise total SO₂ decides every distance.

## 3. The weighted vote

![vote examples](figs/vote_examples.png)

$$\text{vote}=\frac{1}{d+\varepsilon}\qquad\text{confidence}=\frac{\text{winner's votes}}{\text{all votes}}$$

The guide's example (left): one *high* wine at 0.10 votes 10.0; two *medium* wines at 0.90 and 1.00 vote 1.1 + 1.0 = 2.1
→ **HIGH**, confidence 10.0 / 12.1 = **0.83**. Without weights, the two far wines would outvote the almost identical one.

## 4. The imbalance correction (alpha)

44 % of wines are medium, 19 % high: in a mixed neighbourhood, *medium* wins by numbers alone. Divide each vote by its
grade's share raised to alpha:

$$\text{vote}=\frac{1/(d+\varepsilon)}{\text{prior}[\text{grade}]^{\alpha}}$$

Right panel: neighbours medium, medium, high (all at distance 1). alpha = 0 → medium 2.0 vs high 1.0. alpha = 1 → medium
2/0.44 = 4.5 vs high 1/0.19 = **5.3 → HIGH**.

## 5. Choosing k and alpha — the real curves

![k regions](figs/k_regions.png)

| k | behaviour |
|---|---|
| 1 | islands around single wines — one mislabelled wine causes an error every time |
| 15–25 | local and smooth |
| 151 | not local any more — almost everything becomes medium |

![tuning curves](figs/tuning_curves.png)

On the real data (5,320 unique wines, 11 features, 5-fold): macro-F1 rises from 0.54 (k = 1) to ≈ 0.58 around k = 21 and
then stays flat. alpha trades: macro-F1 stays about the same up to ≈ 0.4–0.5 while the recall of *high* wines rises from
0.45 to ≈ 0.6 — which is why Seif's tuning rule prefers alpha = 0.5 (theory §4.5: 0.585 vs 0.586, recall 0.45 → 0.61).

## 6. Ties

Two grades with exactly the same votes: `np.argmax` would always pick the lower grade number — an arbitrary bias toward
*low*. The project's rule: **the grade of the nearest neighbour among the tied grades wins** — deterministic and meaningful.

## 7. Proving it is right

`test_knn_matches_sklearn` runs your k-NN and `KNeighborsClassifier(weights="distance")` on the same 400 training points
and 200 queries, for p = 1 and p = 2, and demands **identical** answers. If it fails, compare the **neighbours** first (the
index), then the votes.

## 8. Misconceptions

| Student says | Truth |
|---|---|
| "k-NN trains a model" | It stores the data. `fit` = remember (and the scaler). |
| "k = 1 is the most accurate, it uses the closest wine" | It is the most **noisy**. Tasters disagree; one wine is not evidence. |
| "Bigger k is safer" | Too big = the majority class everywhere. |
| "The prior of a missing class is 0" | 1.0 — `0 ** alpha` would divide by zero. (Seif's FAQ in theory §4.5.) |

## 9. Activities

1. **Human k-NN (15 min).** Tape a grid on the floor (alcohol × acidity). 15 students hold "wine cards" with a grade and
   stand at their position. A new student enters — the class counts the 1, 3, 5 nearest. Change k, change the answer.
2. **Vote by hand (10 min).** Distances 0.2 (high), 0.5 (medium), 0.6 (medium), 1.0 (low), 1.1 (medium). k = 5,
   weighted. → high 5.0, medium 2.0 + 1.67 + 0.91 = 4.58, low 1.0 → HIGH, confidence 5.0 / 10.58 = 0.47.
3. **Live slider.** `python visualize.py --live` — drag k from 1 to 60.

## 10. Check yourself

<details><summary>1. p = 1, weights (1, 2): distance between (1, 5) and (4, 3)?</summary>

1·|1−4| + 2·|5−3| = 3 + 4 = **7**.
</details>

<details><summary>2. Why is k-NN slow at prediction time, and what does Seif try against it?</summary>

It computes the distance to every training wine (~4,250). Lesson 16: the kd-tree, which tries to skip regions — and the
measurement that shows when it doesn't help.
</details>

<details><summary>3. Centroid baseline 0.49, k-NN 0.58. Why does k-NN win?</summary>

One average point per grade can't describe a grade spread over several regions (high reds and high whites differ). k-NN
keeps every wine and can follow any shape.
</details>

## 11. In your project

| Project | Where |
|---|---|
| WineGrader | `winegrader/ml/metrics.py` → `minkowski_power`, `minkowski`, `power_to_many`, `power_matrix` · `ml/index.py` → `LinearIndex` · `ml/classifiers.py` → `class_priors`, `vote`, `KNNClassifier`, `MajorityClassifier`, `CentroidClassifier` · theory `32_WineGrader/01_theory/04_knn.md` · notebook `02_knn_from_scratch.ipynb` |

## 🎬 Watch & explore

* StatQuest — *K-nearest neighbors, Clearly Explained* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+K-nearest+neighbors+clearly+explained)
* MIT 6.034 (Winston) — *Learning: Nearest Neighbors* — [search on YouTube](https://www.youtube.com/results?search_query=MIT+6.034+nearest+neighbors+Winston)
* scikit-learn — [Nearest Neighbors Classification example](https://scikit-learn.org/stable/auto_examples/neighbors/plot_classification.html)
