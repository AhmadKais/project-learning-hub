# Chapter 10 — Building it, stage by stage

💡 **In short:** eight stages, in order. Each ends with a set of tests going green. Do not start the next stage until the current one is done. Every function's docstring lists its steps; this chapter adds the reasoning and the parts that are easy to get wrong.

---

## Stage 1 — Loading the data

**Files:** `winegrader/data/loader.py`
**Green at the end:** `pytest tests/test_loader.py -v`

### 1.1 Get the files

```bash
python download_data.py
```

Two files appear in `data/corpus/`. Open one in a text editor (not Excel — Excel may "helpfully" change the semicolons) and look at the first lines.

### 1.2 quality_to_grade

Three `if`s against `config.LOW_MAX_QUALITY` and `config.MEDIUM_QUALITY`. Never type 5 or 6 into the function — the numbers belong in `config.py`.

### 1.3 validate_values

📄 **The checks, in order**
```python
def validate_values(values):
    if len(values) != config.N_FEATURES:
        return f"expected {config.N_FEATURES} values, got {len(values)}"
    for name, value in zip(config.FEATURES, values):
        value = float(value)                      # wrap in try: a string is "not a number"
        if not np.isfinite(value):
            return f"{name} is not a finite number"
        low, high = config.VALID_RANGES[name]
        if not low <= value <= high:
            return f"{name} = {value:g} is outside the valid range {low}..{high}"
    if float(values[-1]) not in (0.0, 1.0):
        return "is_red must be 0 or 1"
    return None
```

It returns a reason instead of raising, because the CSV reader wants to collect reasons for many lines and keep going.

### 1.4 parse_uci_csv

The docstring has the five steps. Two things people get wrong:

- **The size check comes before opening the file.** `os.path.getsize(path)` costs nothing; reading a 2 GB "CSV" into memory to discover it is too big costs everything.
- **The header is compared exactly** to `config.UCI_COLUMNS` (after `.strip()`). A file with the right number of columns in a different order is the most dangerous kind of wrong file.

### 1.5 duplicate_of and drop_exact_duplicates

📄 **First occurrence wins**
```python
def duplicate_of(X, quality):
    first, result = {}, []
    for i, (row, q) in enumerate(zip(X, quality)):
        key = tuple(float(v) for v in row) + (int(q),)
        if key in first:
            result.append(first[key])
        else:
            first[key] = i
            result.append(None)
    return result
```

A tuple can be a dictionary key; a numpy row cannot (it is not hashable). That is why the row is turned into a tuple.

**Before moving on:** run `test_real_data_has_1177_duplicates`. If you get a different number, check that quality is part of the key.

---

## Stage 2 — Looking at the data

**Files:** `winegrader/data/analysis.py`, `analyse.py`
**Green at the end:** `pytest tests/test_analysis.py -v`, and `python analyse.py` writes `reports/analysis.md`

Write `correlation_with` from the definition — the mean of the product of deviations, divided by both standard deviations — not with `np.corrcoef`. The test compares the two.

**Before you run `analyse.py`:** write on paper the three features you expect to matter most for quality. Then look. (Alcohol first by far, then density and volatile acidity, with the opposite sign.) The guess-then-check is worth a paragraph in the book.

Look at the min and max columns of the table. The ratio between the largest and smallest feature ranges is the reason for stage 3.

---

## Stage 3 — Scaling, distance, linear search

**Files:** `ml/scaler.py`, `ml/metrics.py`, `ml/index.py` (the `LinearIndex` part)
**Green at the end:** `pytest tests/test_scaler_metrics.py -v` and `pytest tests/test_index.py -k "not kdtree" -v`

### 3.1 The scalers

`fit` computes and stores; `transform` only applies. Use numpy's default `std` (population, `ddof=0`) — that is what scikit-learn uses, and `test_zscore_matches_sklearn` compares to it.

### 3.2 Distances — loop first

📄 **Write this first, then replace it**
```python
def minkowski_power(a, b, w, p):
    total = 0.0
    for i in range(len(a)):
        total += w[i] * abs(a[i] - b[i]) ** p
    return total
```

When the tests pass, replace the loop with `np.sum(w * np.abs(a - b) ** p)` and run them again. Being able to show both versions in the defence proves you understand what the one-liner does.

`power_matrix` accumulates one feature at a time (the docstring explains why: memory). Make it work, then make it fast: `t * t` instead of `t ** 2`, and `out=` to work in place. It runs hundreds of times in stage 6.

### 3.3 LinearIndex

📄 **query**
```python
def query(self, v, k):
    d = power_to_many(self.X, v, self.weights, self.p)
    self.distance_calcs += len(self.X)
    self.queries += 1
    order = np.argsort(d, kind="stable")[:k]
    return [(float(d[i]), int(i)) for i in order]
```

`query_batch` does the same for many queries, chunk by chunk, with `argpartition` and then `lexsort` to order the k found by (distance, row). `test_batch_matches_single_queries` checks the two agree.

---

## Stage 4 — k-NN, baselines, measuring (the heart)

**Files:** `ml/classifiers.py`, `ml/scoring.py`, `ml/folds.py`, `ml/evaluation.py` (first three functions)
**Green at the end:** `pytest tests/test_classifiers.py -v` — above all `test_knn_matches_sklearn`

### 4.1 vote — the most important function in the project

📄 **vote, for m queries at once**
```python
def vote(dist_power, labels, p, alpha, priors, weighted=True):
    dist = dist_power ** (1.0 / p)                     # the root, only for k values
    v = 1.0 / (dist + config.VOTE_EPSILON) if weighted else np.ones_like(dist)
    v = v / priors[labels] ** alpha                    # imbalance correction
    score = np.zeros((len(labels), len(priors)))
    for c in range(len(priors)):
        score[:, c] = np.sum(v * (labels == c), axis=1)
    best = np.argmax(score, axis=1)
    # ... tie fix-up: rows where two grades share the top score
    conf = score[np.arange(len(best)), best] / score.sum(axis=1)
    return best, conf, score
```

`priors[labels]` is numpy fancy indexing: `labels` is an (m, k) array of grades, and the result is an (m, k) array of their priors. One line, no loop.

For the tie fix-up, find the rows where more than one grade equals the maximum (use `np.isclose`, not `==`, for floats), and for each such row walk its labels from nearest to farthest and take the first one that is among the tied grades.

### 4.2 KNNClassifier

`fit` stores y, computes the priors, and builds the index — that is all the training there is. `predict_one` calls `index.query`, turns the pairs into (1, k) arrays, calls `vote`, and builds the `Prediction` with its `Neighbour`s (real distance: power ** (1/p)). `predict` does the same in batch with `query_batch`.

### 4.3 Scoring and folds

The docstrings are enough. Check `confusion_matrix` against the hand example in `test_confusion_matrix_by_hand` — work it out on paper first.

### 4.4 evaluate_split

The order is the whole point: fit the scaler on `X[train]`, transform both parts with it, fit the model on the transformed training rows, predict the test rows. Then time `predict_one` on the first 50 test wines and take the median.

**Before moving on — your first result.** In a Python shell:

📄 **Does scaling matter?**
```python
from winegrader.data.loader import *
from winegrader.ml.classifiers import KNNClassifier
from winegrader.ml.evaluation import cross_validate, summarise
from winegrader.ml.folds import stratified_kfold

X, q = load_wine_quality(); X, q, _ = drop_exact_duplicates(X, q); y = grades_from_quality(q)
folds = stratified_kfold(y, 5)
for s in ("none", "zscore"):
    r = cross_validate(lambda: KNNClassifier(k=15, p=2, alpha=0.0), X, y, folds, scaling=s)
    print(s, summarise(r)["macro_f1_mean"])
```

About 0.45 against 0.58. Write both numbers in your notes; they open the results chapter.

---

## Stage 5 — The kd-tree

**Files:** `ml/index.py` (`KDTreeIndex`)
**Green at the end:** `pytest tests/test_index.py -v` — `test_kdtree_matches_linear` is blocking

### 5.1 Do it on paper first

Take 8 points in 2 dimensions, build the tree by hand (leaf size 2), then run one query with k = 1 and mark every branch you prune and why. Twenty minutes with a pencil saves a day of debugging.

### 5.2 The search

📄 **query, the inner function**
```python
def search(node):
    if isinstance(node, _Leaf):
        d = power_to_many(self.X[node.rows], v, w, p)
        self.distance_calcs += len(node.rows)
        for dist, row in zip(d, node.rows):
            offer(float(dist), int(row))
        return
    diff = v[node.axis] - node.threshold
    near, far = (node.left, node.right) if diff < 0 else (node.right, node.left)
    search(near)
    gap = w[node.axis] * abs(diff) ** p
    if len(heap) < k or gap <= -heap[0][0]:
        search(far)
```

`offer` pushes `(-dist, -row)` while the heap holds fewer than k entries; after that it replaces `heap[0]` (the worst) only if the new entry is better — which with negated keys means `entry > heap[0]`.

### 5.3 When test_kdtree_matches_linear fails

- **Different neighbours, same distances** — the tie rule. Check `<=` in the prune and the `(-dist, -row)` ordering.
- **A neighbour missing entirely** — the prune bound is wrong. Is the weight in `gap`? Is `p` applied? Is it compared with the *power* distance (no root)?
- **Infinite recursion** — the split. Are you splitting by position (`order[:mid]`, `order[mid:]`)?

---

## Stage 6 — Tuning, weights, nested evaluation

**Files:** `ml/callbacks.py`, `ml/tuning.py`, `ml/weights.py`, `nested_cv` in `ml/evaluation.py`
**Green at the end:** `pytest tests/test_tuning_weights.py -v` and `pytest tests/test_evaluation_bundle.py -k nested -v`

### 6.1 In this order

1. The callbacks — small and independent.
2. `prepare_folds`, `fold_neighbours`, `score_votes` — the building blocks.
3. `choose_configuration` — test it on the hand-made rows.
4. `grid_search` — the loops in the docstring.
5. `cv_score` — the **slow, simple** version: every call recomputes everything.
6. `learn_weights` using `cv_score` in the loop. Make the tests pass. **Time it** on the real data.
7. `FoldDistances` and the incremental `learn_weights`. `test_incremental_matches_full_recompute` must pass. **Time it again.**

Steps 6 and 7 together give you a before-and-after for the efficiency chapter of the book: the ministry asks for efficiency "with justification", and there is no better justification than two measured times.

### 6.2 nested_cv

Follow the docstring. The thing to get right: `grid_search` and `learn_weights` receive `X[train]` and `y[train]` and nothing else. `test_nested_never_sees_outer_test` will tell you if anything leaks.

---

## Stage 7 — The two machines

**Files:** `ml/bundle.py`, `database/`, `service.py`, `controllers/`, `views/`, `train.py`, `run.py`
**Green at the end:** everything except the stage 8 functions

### 7.1 Order

1. `bundle.py` — `pytest tests/test_evaluation_bundle.py -v` (the evaluation tests in it already pass from stages 4 and 6).
2. `db.py` and the repositories — the database tests in `test_app.py`.
3. `service.py`, then the controller — the rest of `test_app.py`.
4. `train.py` — run it on `--sample`, then on the real data.
5. The views and `run.py` — no tests; you test them by using them.

### 7.2 The import transaction

`import_arrays` inserts 6,497 rows. If `add` commits after every row, that is 6,497 disk writes and several minutes. Pass `commit=False` inside the loop and commit once at the end — under a second. Measure both; it is a good example for the book.

### 7.3 The views

Keep them thin. If you find yourself writing an `if` about grades or colours in a view, it belongs in the controller. The `EXAMPLE` wine in `classify_view.py` lets you try the screen in one click.

### 7.4 The two-machine demonstration

1. `python train.py` on your computer.
2. Copy one `models/wg-…` folder to a second computer (or a second user account) that has the project but has never trained.
3. `python run.py` there. Grade a wine.
4. Open `model.json` in the copy, change `"k": 23` to `"k": 3`, save, run again. The station must refuse: "the model files were modified".

Screenshots of steps 3 and 4 go in the book's deployment chapter.

---

## Stage 8 — Measure and write

**Files:** the stage 8 functions in `repositories.py` and `evaluation.py`, `evaluate.py`
**Green at the end:** `pytest -v` — everything

1. Implement the remaining functions; check `evaluate.py --sample` runs end to end.
2. Run `python evaluate.py` **once** on the real data (about two minutes).
3. Open `reports/evaluation.md`. Every target from the proposal has PASS, FAIL or REPORTED next to it.
4. Write the results chapter from it. Use `docs/PROJECT_BOOK_MAP.md` — it lists the six results that must be *discussed*, not just reported.

💡 A missed target is written as missed, with the reason. Targets are never edited afterwards to match the result. An examiner trusts a book that says "this did not work, and here is why" far more than one where everything passed.
