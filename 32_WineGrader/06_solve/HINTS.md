# WineGrader — hints, checks and traps, stage by stage

Use this file when you are **stuck** on a function of your skeleton. For each hard function:

- **Learn it in** — the theory section, notebook and exercise that teach the idea.
- **Hints** — hidden. Open one at a time: 💡 a nudge, 🔧 the steps.
- **Check yourself** — numbers to compare against before you run the tests.
- **Traps** — the mistakes that make a test fail (or pass while the result is dishonest).

`CHECKLIST.md` (next to this file) lists **every** function you have to write. Your docstrings are unusually
complete — most of them contain the algorithm line by line. This file adds the numbers to check against and the
traps the docstrings only hint at.

> **The working loop.** One function → run **its** test (`pytest tests/test_metrics.py -k minkowski -v`) →
> green → commit → next. The k-d tree and the weight learning each have a test that compares them with the slow,
> obvious version — trust those tests.

All "check yourself" numbers on the real data use both UCI files (`data/README.md` says where to get them; the
hub has a copy in `32_WineGrader/data/`).

---

## Stage 1 — Loading the data

**Learn it in:** theory `03_data_scaling` §3.1–3.4 · notebook `01_data_and_scaling` §1–2 · exercises **ex01, ex02**

**Check yourself:**

```
quality_to_grade: 3 -> LOW (0)   5 -> LOW   6 -> MEDIUM (1)   7 -> HIGH (2)   9 -> HIGH
load_wine_quality(red, white)        6,497 rows x 12 features (11 measurements + is_red)
drop_exact_duplicates                1,177 duplicates dropped -> 5,320 wines
class_balance after de-duplication   low 0.374   medium 0.437   high 0.190
```

<details><summary>💡 Hint — <code>duplicate_of</code> in one pass</summary>

A dict from the row (as a `tuple`) **and its quality** to the first index that had it. A row whose key is already in
the dict is a duplicate of that index. One pass, O(N) — no double loop.
</details>

**Trap:** de-duplicating **after** splitting into folds. The same wine in train and test is the cheapest leak there
is (theory §3.4) — that is why it happens in stage 1.

---

## Stage 2 — Looking at the data

`describe`, `correlation_with`, `means_by_group`, `plot_histograms` — plain NumPy. Use the population standard
deviation (`np.std`, `ddof=0`) everywhere, the same one the scaler uses. In `plot_histograms` call
`matplotlib.use("Agg")` before importing `pyplot`, and `plt.close(fig)` after saving.

---

## Stage 3 — Scaling, distance, linear search

**Learn it in:** theory `03_data_scaling` §3.5–3.8, `04_knn` §4.2 · notebook `01` §3, `02_knn_from_scratch` §1 ·
exercises **ex03–ex06**

**Check yourself:**

```
a = [0, 0], b = [3, 4], w = [1, 1]
minkowski_power(a, b, w, p=2) = 25.0      minkowski(..., p=2) = 5.0      minkowski(..., p=1) = 7.0
```

**Traps:** a column with standard deviation 0 must become 1 in the scaler (no division by zero) · `transform`
before `fit` raises `RuntimeError("scaler is not fitted")` · `np.argsort(d, kind="stable")` — the default sort is
not stable, and the tests check that ties come out by row index · `power_matrix` should broadcast
(`Q[:, None, :] - X[None, :, :]`), but on 5,000 × 4,000 × 12 that is ~2 GB — `query_batch` exists to process it in
chunks.

---

## Stage 4 — k-NN, baselines, measuring ★

**Learn it in:** theory `04_knn` §4.3–4.9, `07_evaluation` §7.1–7.5 · notebooks `02`, `04_honest_evaluation` ·
exercises **ex07, ex08, ex10–ex12**

### `vote`

Follow the docstring. The two lines that matter:

- `v = v / priors[labels] ** alpha` — the imbalance correction. With `alpha = 0` it does nothing; with `alpha = 1` a
  vote for the rare HIGH grade counts about twice as much as one for MEDIUM.
- the tie rule — the grade of the **nearest** neighbour among the tied grades wins, never "the lowest number".

### The metrics

**Check yourself:**

```
y_true = [0, 0, 1, 2, 2, 2]     y_pred = [0, 1, 1, 2, 2, 0]
confusion_matrix -> [[1, 1, 0],
                     [0, 1, 0],
                     [1, 0, 2]]       (rows = true grade, columns = predicted)
macro_f1 -> 0.6556
stratified_kfold(y, 5) on the 5,320 wines -> test sizes 1065, 1065, 1065, 1063, 1062
```

### The numbers that make the project

| | macro-F1 (5-fold) |
|---|---|
| always "medium" (`MajorityClassifier`) | 0.20 |
| `CentroidClassifier` | 0.49 |
| k-NN without scaling | 0.45 |
| k-NN, z-score, k ≈ 15–21 | 0.58 |

If your k-NN without scaling is **not** worse than the centroid baseline, something else is scaling the data for
you. If your z-score k-NN is far above 0.60, check for a leak.

**Trap:** fitting the scaler on all the data before splitting. In `evaluate_split` the scaler is fitted on the
**train** rows of that fold, then applied to its test rows.

---

## Stage 5 — The kd-tree

**Learn it in:** theory `05_kdtree` §5.2–5.7 · notebook `03_kdtree` · exercise **ex09**

The docstrings of `_build` and `query` contain the whole algorithm. Three things that are easy to get wrong:

- split by **position** (`mid = len(order) // 2`), not by "< median" — with many equal values the second never ends
- `heapq` is a **min**-heap: store `(-distance, -row)` so that `heap[0]` is the **worst** of the k best
- prune with `gap <= worst`, not `<` — otherwise a tie with a smaller row number can be lost

**Check yourself:** the k-d tree must return **exactly** what `LinearIndex` returns, for every query
(`tests/test_index.py` compares them). In 12 dimensions it computes ~55% of the distances and is *slower* than the
vectorised linear search; on 2 features it computes ~2%. That is the curse of dimensionality (theory §5.7) — a
result for the book, not a bug.

---

## Stage 6 — Tuning, callbacks, weight learning, nested evaluation

**Learn it in:** theory `06_tuning_weights` §6.1–6.9, `07_evaluation` §7.6–7.9 · notebook `05_feature_weights` ·
exercise **ex13**

- `grid_search`: compute the neighbours **once** per (scaling, p) with the largest k, then vote with the first k of
  them for every smaller k — that is the trick of theory §6.2.
- `choose_configuration`: among the rows within `F1_TOLERANCE` of the best macro-F1, the highest `recall_high` wins.
  On the real data alpha 0 and 0.5 score 0.586 and 0.585, with HIGH recall 0.45 against 0.61.
- `learn_weights`: the incremental update `D + (new - w[i]) * term(i)` must give the same score as recomputing
  from scratch — `test_incremental_matches_full_recompute` is the proof.
- `nested_cv`: the inner loop (grid search + weights) sees **only** the outer fold's training rows. The outer test
  fold is scored once, with whatever the inner loop chose.

**Trap:** reporting the grid-search score as the final result. That number was chosen *because* it was the
highest — it is optimistic. The honest number is the nested-CV one (theory §7.6).

---

## Stage 7 — The two machines

`train.py` builds and saves the bundle on the training machine; the GUI loads it on the second. The bundle stores
the scaler, the weights, the chosen parameters and a checksum. `bundle.load` checks, **in this order**: every file
is there → the checksum matches → the feature list matches name by name → the sizes agree — and only then rebuilds.
Test it by editing one number in the saved files: the load must refuse with "files were modified".

---

## When nothing works

| Symptom | Likely cause |
|---|---|
| macro-F1 ≈ 0.20 | every wine predicted MEDIUM — the labels or the vote are wrong |
| the k-d tree disagrees with `LinearIndex` on a few queries | ties: `kind="stable"`, `(-dist, -row)` keys, `gap <= worst` |
| `RecursionError` in `_build` | splitting by "< median" instead of by position |
| `MemoryError` in `power_matrix` | use `query_batch` with chunks |
| nested CV is as high as the grid search | the inner loop saw the outer test fold |
| the weight learning makes the score worse | an update applied twice — run `test_incremental_matches_full_recompute` |
