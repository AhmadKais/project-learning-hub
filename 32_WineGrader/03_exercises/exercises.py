"""WineGrader - exercises.

Fill in every function marked TODO. Use only numpy (and the standard library).
Check yourself after each exercise:

    pytest test_exercises.py -k ex01 -v        # one exercise
    pytest test_exercises.py -v                # all of them

Stuck for more than 20 minutes? Re-read the theory chapter named in the
docstring, look at the notebook, and only then open solutions.py.
"""
import numpy as np


# ---------------------------------------------------------------- data (notebook 01)

def ex01_to_grade(score):
    """Turn quality scores (0..10) into grades: 3,4,5 -> 0 (low), 6 -> 1 (medium), 7,8,9 -> 2 (high).

    score: 1-D int array.  Returns a 1-D int array of the same length.
    >>> ex01_to_grade(np.array([3, 5, 6, 7, 9]))
    array([0, 0, 1, 2, 2])
    Theory 3.2
    """
    raise NotImplementedError("TODO ex01")


def ex02_drop_exact_duplicates(X, y):
    """Remove rows that are exact copies (same features AND same label) of an EARLIER row.

    Keep the first copy and keep the original order.
    Returns (X_unique, y_unique, n_dropped).
    Theory 3.4
    """
    raise NotImplementedError("TODO ex02")


def ex03_zscore_fit(X):
    """Learn the z-score parameters from X.

    Returns (mean, std), each a 1-D array with one value per column.
    A column with std 0 must get std 1 (so we never divide by zero).
    Theory 3.6
    """
    raise NotImplementedError("TODO ex03")


def ex04_minmax_fit(X):
    """Learn the min-max parameters from X.

    Returns (low, range) so that (X - low) / range maps every column to [0, 1].
    A constant column must get range 1.
    Theory 3.7
    """
    raise NotImplementedError("TODO ex04")


# ---------------------------------------------------------------- k-NN (notebook 02)

def ex05_minkowski(a, b, p=2, w=None):
    """Weighted Minkowski distance between two 1-D vectors:  (sum w_i |a_i - b_i|^p) ^ (1/p).

    w=None means all weights are 1.
    >>> ex05_minkowski(np.array([0., 0.]), np.array([3., 4.]))
    5.0
    Theory 4.2
    """
    raise NotImplementedError("TODO ex05")


def ex06_k_nearest(X_train, q, k, p=2):
    """Indices of the k rows of X_train nearest to q, nearest first.

    Two rows at exactly the same distance: the smaller row index comes first.
    Hint: you do not need the root to rank distances (theory 4.3).
    """
    raise NotImplementedError("TODO ex06")


def ex07_vote(neigh_grades, neigh_dist, priors, alpha=0.0, n_classes=3):
    """The weighted vote of the neighbours.

    neigh_grades: grades of the neighbours, NEAREST FIRST.  neigh_dist: their real distances.
    vote of one neighbour = 1 / (distance + 1e-9) / priors[grade] ** alpha
    Tie between grades (scores equal up to np.isclose): the grade of the NEAREST neighbour among
    the tied grades wins.
    Returns (winner, confidence) where confidence = winner's score / sum of all scores.
    Theory 4.4 - 4.6
    """
    raise NotImplementedError("TODO ex07")


def ex08_knn_predict(X_train, y_train, X_test, k=15, p=2, alpha=0.0):
    """Predict a grade for every row of X_test with ex06 + ex07.

    priors = share of each grade (0, 1, 2) in y_train.  Returns a 1-D int array.
    Must give exactly the same answers as sklearn KNeighborsClassifier(weights="distance") when alpha=0.
    """
    raise NotImplementedError("TODO ex08")


# ---------------------------------------------------------------- k-d tree (notebook 03)

def ex09_kd_neighbours(X, q, k, p=2, leaf_size=16):
    """Build a k-d tree over X and return (indices, n_distances_computed).

    indices must be EXACTLY what ex06_k_nearest returns (same order, same ties).
    n_distances_computed = how many rows had their distance to q computed (the leaves you opened).
    Split on the column with the largest spread, cut at the middle position, prune the far side
    when  |q[axis] - threshold| ** p  >  the k-th best power distance so far.
    Theory 5.2 - 5.4
    """
    raise NotImplementedError("TODO ex09")


# ---------------------------------------------------------------- evaluation (notebook 04)

def ex10_confusion_matrix(y_true, y_pred, n_classes=3):
    """cm[t][p] = number of rows with true class t predicted as p. Returns an int array (n, n).
    Theory 7.1
    """
    raise NotImplementedError("TODO ex10")


def ex11_macro_f1(y_true, y_pred, n_classes=3):
    """Average over the classes of F1 = 2PR / (P + R).

    precision = TP / predicted-as-class, recall = TP / really-class.  0/0 counts as 0 (never nan).
    Theory 7.2 - 7.3
    """
    raise NotImplementedError("TODO ex11")


def ex12_stratified_kfold(y, folds=5, seed=0):
    """Return a list of `folds` pairs (train_idx, test_idx).

    Every row is in exactly one test fold. Each class is dealt out over the folds separately, so
    every fold has the same class mix (within one row per class).
    Use np.random.default_rng(seed) to shuffle.
    Theory 7.5
    """
    raise NotImplementedError("TODO ex12")


# ---------------------------------------------------------------- weights (notebook 05)

def ex13_update_distances(D, X_test, X_train, i, w_old, w_new, p=2):
    """D[a, b] is the weighted POWER distance from X_test[a] to X_train[b].

    Feature i's weight changes from w_old to w_new. Return the new D WITHOUT recomputing
    the other features:  D + (w_new - w_old) * |X_test[:, i] - X_train[:, i]| ** p
    Do not change D in place - return a new array.
    Theory 6.7
    """
    raise NotImplementedError("TODO ex13")
