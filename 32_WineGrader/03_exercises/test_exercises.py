"""Automatic checks for exercises.py.   Run:  pytest test_exercises.py -v

Every test is named after its exercise, so  pytest -k ex07  runs just that one.
"""
import importlib
import os

import numpy as np
import pytest

ex = importlib.import_module(os.environ.get("EXERCISES", "exercises"))
rng = np.random.default_rng(12345)


def test_ex01_to_grade():
    got = ex.ex01_to_grade(np.array([3, 4, 5, 6, 7, 8, 9]))
    assert list(got) == [0, 0, 0, 1, 2, 2, 2]


def test_ex02_drop_exact_duplicates():
    X = np.array([[1., 2.], [3., 4.], [1., 2.], [1., 2.], [5., 6.]])
    y = np.array([0, 1, 0, 1, 2])          # row 3 has the same features as row 0 but another label
    Xu, yu, n = ex.ex02_drop_exact_duplicates(X, y)
    assert n == 1
    assert Xu.tolist() == [[1, 2], [3, 4], [1, 2], [5, 6]]
    assert yu.tolist() == [0, 1, 1, 2]


def test_ex03_zscore_fit():
    X = np.array([[1., 5.], [3., 5.], [5., 5.]])
    mean, std = ex.ex03_zscore_fit(X)
    assert np.allclose(mean, [3, 5])
    assert np.allclose(std, [np.std([1, 3, 5]), 1.0])      # constant column -> std 1
    Z = (X - mean) / std
    assert np.allclose(Z.mean(0), 0)


def test_ex04_minmax_fit():
    X = np.array([[0., 7.], [10., 7.], [5., 7.]])
    low, rng_ = ex.ex04_minmax_fit(X)
    assert np.allclose((X - low) / rng_, [[0, 0], [1, 0], [0.5, 0]])


def test_ex05_minkowski():
    a, b = np.array([0., 0.]), np.array([3., 4.])
    assert ex.ex05_minkowski(a, b, p=2) == pytest.approx(5.0)
    assert ex.ex05_minkowski(a, b, p=1) == pytest.approx(7.0)
    assert ex.ex05_minkowski(a, b, p=2, w=np.array([0., 1.])) == pytest.approx(4.0)
    assert ex.ex05_minkowski(a, b, p=2, w=np.array([4., 1.])) == pytest.approx(np.sqrt(36 + 16))


def test_ex06_k_nearest_order_and_ties():
    X = np.array([[0., 0.], [1., 0.], [0., 1.], [5., 5.], [-1., 0.]])
    got = ex.ex06_k_nearest(X, np.array([0., 0.]), k=4)
    assert list(got) == [0, 1, 2, 4]          # rows 1, 2, 4 are tied at distance 1 -> row order


def test_ex06_k_nearest_matches_brute_force():
    X = rng.random((200, 4))
    q = rng.random(4)
    d = np.sqrt(((X - q) ** 2).sum(1))
    assert list(ex.ex06_k_nearest(X, q, 10)) == list(np.argsort(d)[:10])


def test_ex07_vote_worked_example():
    winner, conf = ex.ex07_vote(np.array([2, 1, 1]), np.array([0.1, 0.9, 1.0]), np.ones(3) / 3)
    assert winner == 2
    assert conf == pytest.approx(10 / (10 + 1 / 0.9 + 1), rel=1e-6)


def test_ex07_vote_alpha():
    g, d, pr = np.array([1, 1, 2]), np.ones(3), np.array([0.37, 0.44, 0.19])
    assert ex.ex07_vote(g, d, pr, alpha=0)[0] == 1
    assert ex.ex07_vote(g, d, pr, alpha=1)[0] == 2


def test_ex07_vote_tie_goes_to_nearest():
    # grades 0 and 2 both score exactly 1+1; the nearest neighbour is grade 2
    g, d = np.array([2, 0, 0, 2]), np.array([1., 1., 1., 1.])
    assert ex.ex07_vote(g, d, np.ones(3))[0] == 2


def test_ex08_knn_matches_sklearn():
    sk = pytest.importorskip("sklearn.neighbors")
    X = rng.normal(size=(400, 5))
    y = rng.integers(0, 3, 400)
    Xq = rng.normal(size=(150, 5))
    for p in (1, 2):
        ref = sk.KNeighborsClassifier(n_neighbors=9, p=p, weights="distance", algorithm="brute").fit(X, y).predict(Xq)
        assert np.array_equal(ex.ex08_knn_predict(X, y, Xq, k=9, p=p), ref)


def test_ex09_kdtree_matches_linear():
    X = rng.random((800, 3))
    for p in (1, 2):
        for q in rng.random((100, 3)):
            got, _ = ex.ex09_kd_neighbours(X, q, k=7, p=p)
            assert list(got) == list(ex.ex06_k_nearest(X, q, 7, p))


def test_ex09_kdtree_ties_on_integer_data():
    X = rng.integers(0, 3, (500, 3)).astype(float)
    for q in rng.integers(0, 3, (50, 3)).astype(float):
        assert list(ex.ex09_kd_neighbours(X, q, k=10)[0]) == list(ex.ex06_k_nearest(X, q, 10))


def test_ex09_kdtree_prunes_in_low_dimensions():
    X = rng.random((5000, 2))
    _, n = ex.ex09_kd_neighbours(X, np.array([0.5, 0.5]), k=5)
    assert n < 500, f"computed {n} of 5000 distances - the tree is not pruning"


def test_ex10_confusion_matrix():
    y_true = np.array([0, 0, 1, 1, 1, 1, 2, 2, 2, 2])
    y_pred = np.array([0, 1, 0, 1, 1, 1, 1, 2, 2, 2])
    assert ex.ex10_confusion_matrix(y_true, y_pred).tolist() == [[1, 1, 0], [1, 3, 0], [0, 1, 3]]


def test_ex11_macro_f1_matches_sklearn():
    metrics = pytest.importorskip("sklearn.metrics")
    for _ in range(20):
        a, b = rng.integers(0, 3, 50), rng.integers(0, 3, 50)
        assert ex.ex11_macro_f1(a, b) == pytest.approx(metrics.f1_score(a, b, average="macro", zero_division=0))


def test_ex11_never_predicted_class_is_zero_not_nan():
    score = ex.ex11_macro_f1(np.array([0, 1, 2]), np.array([1, 1, 1]))
    assert not np.isnan(score)
    assert score == pytest.approx((0 + 2 * (1 / 3) / (1 / 3 + 1) + 0) / 3)


def test_ex12_stratified_kfold():
    y = np.array([0] * 50 + [1] * 30 + [2] * 20)
    splits = ex.ex12_stratified_kfold(y, folds=5, seed=0)
    assert len(splits) == 5
    all_test = np.concatenate([te for _, te in splits])
    assert sorted(all_test.tolist()) == list(range(100))           # every row tested once
    for tr, te in splits:
        assert len(set(tr) & set(te)) == 0
        assert np.bincount(y[te], minlength=3).tolist() == [10, 6, 4]


def test_ex13_update_matches_recompute():
    Xte, Xtr = rng.random((20, 4)), rng.random((30, 4))
    w = np.array([1.0, 2.0, 0.5, 1.0])
    full = lambda w: (w * np.abs(Xte[:, None, :] - Xtr[None, :, :]) ** 2).sum(2)
    D = full(w)
    D_before = D.copy()
    w_new = w.copy(); w_new[1] = 0.0
    got = ex.ex13_update_distances(D, Xte, Xtr, 1, w[1], w_new[1])
    assert np.allclose(got, full(w_new))
    assert np.array_equal(D, D_before), "D was changed in place"
