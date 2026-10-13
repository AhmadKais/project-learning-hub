"""WineGrader - solutions to exercises.py.

Try first. Then compare: there is more than one correct way to write each one.
To run the tests against these solutions:  EXERCISES=solutions pytest test_exercises.py
"""
import heapq

import numpy as np

EPS = 1e-9


def ex01_to_grade(score):
    score = np.asarray(score)
    return np.where(score <= 5, 0, np.where(score == 6, 1, 2))


def ex02_drop_exact_duplicates(X, y):
    seen, keep = set(), []
    for i in range(len(X)):
        key = tuple(X[i].tolist()) + (y[i].item(),)
        if key not in seen:
            seen.add(key)
            keep.append(i)
    keep = np.array(keep, dtype=int)
    return X[keep], y[keep], len(X) - len(keep)


def ex03_zscore_fit(X):
    std = X.std(axis=0)
    return X.mean(axis=0), np.where(std == 0, 1.0, std)


def ex04_minmax_fit(X):
    low = X.min(axis=0)
    rng = X.max(axis=0) - low
    return low, np.where(rng == 0, 1.0, rng)


def ex05_minkowski(a, b, p=2, w=None):
    w = np.ones(len(a)) if w is None else np.asarray(w)
    return float((w * np.abs(np.asarray(a) - np.asarray(b)) ** p).sum() ** (1 / p))


def _power(X_train, q, p):
    return (np.abs(X_train - q) ** p).sum(axis=1)


def ex06_k_nearest(X_train, q, k, p=2):
    return np.argsort(_power(X_train, q, p), kind="stable")[:k]


def ex07_vote(neigh_grades, neigh_dist, priors, alpha=0.0, n_classes=3):
    neigh_grades = np.asarray(neigh_grades)
    w = 1.0 / (np.asarray(neigh_dist) + EPS) / np.asarray(priors)[neigh_grades] ** alpha
    scores = np.zeros(n_classes)
    np.add.at(scores, neigh_grades, w)
    tied = np.flatnonzero(np.isclose(scores, scores.max()))
    winner = tied[0] if len(tied) == 1 else next(g for g in neigh_grades if g in tied)
    return int(winner), float(scores[winner] / scores.sum())


def ex08_knn_predict(X_train, y_train, X_test, k=15, p=2, alpha=0.0):
    priors = np.bincount(y_train, minlength=3) / len(y_train)
    priors = np.where(priors == 0, 1.0, priors)
    out = []
    for q in X_test:
        d = _power(X_train, q, p)
        idx = np.argsort(d, kind="stable")[:k]
        out.append(ex07_vote(y_train[idx], d[idx] ** (1 / p), priors, alpha)[0])
    return np.array(out, dtype=int)


def ex09_kd_neighbours(X, q, k, p=2, leaf_size=16):
    def build(rows):
        if len(rows) <= leaf_size:
            return ("leaf", rows)
        pts = X[rows]
        axis = int(np.argmax(pts.max(0) - pts.min(0)))
        order = rows[np.argsort(pts[:, axis], kind="stable")]
        mid = len(order) // 2
        return ("node", axis, X[order[mid], axis], build(order[:mid]), build(order[mid:]))

    heap, count = [], [0]

    def visit(node):
        if node[0] == "leaf":
            rows = node[1]
            count[0] += len(rows)
            for dist, row in zip(_power(X[rows], q, p), rows):
                item = (-dist, -row)
                if len(heap) < k:
                    heapq.heappush(heap, item)
                elif item > heap[0]:
                    heapq.heapreplace(heap, item)
            return
        _, axis, thr, left, right = node
        diff = q[axis] - thr
        near, far = (left, right) if diff <= 0 else (right, left)
        visit(near)
        if len(heap) < k or abs(diff) ** p <= -heap[0][0]:
            visit(far)

    visit(build(np.arange(len(X))))
    best = sorted((-d, -r) for d, r in heap)
    return np.array([r for _, r in best], dtype=int), count[0]


def ex10_confusion_matrix(y_true, y_pred, n_classes=3):
    cm = np.zeros((n_classes, n_classes), dtype=int)
    np.add.at(cm, (np.asarray(y_true), np.asarray(y_pred)), 1)
    return cm


def ex11_macro_f1(y_true, y_pred, n_classes=3):
    cm = ex10_confusion_matrix(y_true, y_pred, n_classes)
    f1s = []
    for c in range(n_classes):
        tp = cm[c, c]
        prec = tp / cm[:, c].sum() if cm[:, c].sum() else 0.0
        rec = tp / cm[c, :].sum() if cm[c, :].sum() else 0.0
        f1s.append(2 * prec * rec / (prec + rec) if prec + rec else 0.0)
    return float(np.mean(f1s))


def ex12_stratified_kfold(y, folds=5, seed=0):
    y = np.asarray(y)
    rng = np.random.default_rng(seed)
    fold_of = np.empty(len(y), dtype=int)
    for c in np.unique(y):
        rows = np.flatnonzero(y == c)
        rng.shuffle(rows)
        fold_of[rows] = np.arange(len(rows)) % folds
    return [(np.flatnonzero(fold_of != f), np.flatnonzero(fold_of == f)) for f in range(folds)]


def ex13_update_distances(D, X_test, X_train, i, w_old, w_new, p=2):
    term = np.abs(X_test[:, i, None] - X_train[None, :, i]) ** p
    return D + (w_new - w_old) * term
