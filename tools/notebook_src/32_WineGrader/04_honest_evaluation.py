# %% [markdown]
# # 04 · Measuring without fooling yourself
#
# **Read first:** `01_theory/07_evaluation.md`
#
# 1. the confusion matrix, precision, recall, F1, macro-F1 — by hand, then in code
# 2. why one split is not enough: cross-validation with mean ± std
# 3. stratified folds
# 4. nested cross-validation: the honest score of "tune, then predict"

# %%
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

GRADES = ["low", "medium", "high"]

# %% [markdown]
# ## 1. The confusion matrix — the example from the theory chapter
#
# `cm[true][pred]` counts wines. Rows = truth, columns = prediction.

# %%
def confusion_matrix(y_true, y_pred, n=3):
    cm = np.zeros((n, n), dtype=int)
    np.add.at(cm, (y_true, y_pred), 1)
    return cm

y_true = np.array([0, 0, 1, 1, 1, 1, 2, 2, 2, 2])
y_pred = np.array([0, 1, 0, 1, 1, 1, 1, 2, 2, 2])
cm = confusion_matrix(y_true, y_pred)
print(cm)

# %% [markdown]
# * **precision** of a grade = diagonal ÷ **column** sum ("of the wines I *called* high, how many were?")
# * **recall** = diagonal ÷ **row** sum ("of the wines that *were* high, how many did I find?")
# * **F1** = 2PR / (P + R); a 0/0 counts as 0 (like scikit-learn's `zero_division=0`)
# * **macro-F1** = the plain average over the grades — the rare "high" counts as much as "medium"

# %%
def per_class(cm):
    tp = np.diag(cm).astype(float)
    col, row = cm.sum(0), cm.sum(1)
    prec = np.divide(tp, col, out=np.zeros_like(tp), where=col > 0)
    rec = np.divide(tp, row, out=np.zeros_like(tp), where=row > 0)
    f1 = np.divide(2 * prec * rec, prec + rec, out=np.zeros_like(tp), where=(prec + rec) > 0)
    return prec, rec, f1

prec, rec, f1 = per_class(cm)
for g in range(3):
    print(f"{GRADES[g]:7s} precision {prec[g]:.3f}  recall {rec[g]:.3f}  F1 {f1[g]:.3f}")
print(f"macro-F1 {f1.mean():.3f}")

from sklearn.metrics import f1_score            # only to check ourselves
print("sklearn  ", round(f1_score(y_true, y_pred, average="macro"), 3))

# %% [markdown]
# **Why not accuracy?** "Always say medium" has 44% accuracy on wine but macro-F1 0.20 — it never
# finds a single high wine, and macro-F1 shows it.
#
# ## 2. Load the wines and a compact k-NN

# %%
DATA = Path("../data")
def load(path, is_red):
    raw = np.genfromtxt(path, delimiter=";", skip_header=1)
    return np.column_stack([raw[:, :11], np.full(len(raw), float(is_red))]), raw[:, 11]
Xr, sr = load(DATA / "winequality-red.csv", 1)
Xw, sw = load(DATA / "winequality-white.csv", 0)
U = np.unique(np.column_stack([np.vstack([Xr, Xw]), np.concatenate([sr, sw])]), axis=0)
X, s = U[:, :-1], U[:, -1]
y = np.where(s <= 5, 0, np.where(s == 6, 1, 2))


def neighbours(Xtr, Xte, k_max, p=2):
    """For every test row: the k_max nearest training rows and their real distances."""
    orders, dists = [], []
    for start in range(0, len(Xte), 200):              # 200 rows at a time to save memory
        D = (np.abs(Xte[start:start + 200, None, :] - Xtr[None, :, :]) ** p).sum(2)
        order = np.argsort(D, axis=1, kind="stable")[:, :k_max]
        orders.append(order)
        dists.append(np.take_along_axis(D, order, 1) ** (1 / p))
    return np.vstack(orders), np.vstack(dists)


def knn_vote(ytr, order, dist, k, alpha=0.0):
    priors = np.bincount(ytr, minlength=3) / len(ytr)
    g = ytr[order[:, :k]]
    w = 1 / (dist[:, :k] + 1e-9) / priors[g] ** alpha
    scores = np.zeros((len(g), 3))
    for c in range(3):
        scores[:, c] = (w * (g == c)).sum(1)
    return scores.argmax(1)                 # (tie rule left out to keep this short)


def scale(train_X, *others):
    m, sd = train_X.mean(0), train_X.std(0)
    sd[sd == 0] = 1
    return [(a - m) / sd for a in (train_X, *others)]


def macro_f1(y_true, y_pred):
    return per_class(confusion_matrix(y_true, y_pred))[2].mean()

# %% [markdown]
# ## 3. One split is a lottery
#
# Score the *same* model (k = 15) on 20 different random 80/20 splits:

# %%
rng = np.random.default_rng(0)
scores = []
for rep in range(20):
    perm = rng.permutation(len(y))
    tr, te = perm[: int(.8 * len(y))], perm[int(.8 * len(y)):]
    Xtr, Xte = scale(X[tr], X[te])
    order, dist = neighbours(Xtr, Xte, 15)
    scores.append(macro_f1(y[te], knn_vote(y[tr], order, dist, 15)))
print(f"macro-F1 from {min(scores):.3f} to {max(scores):.3f}  (mean {np.mean(scores):.3f}, std {np.std(scores):.3f})")

# %% [markdown]
# A difference of 0.01 between two models is **smaller than the luck of the split**. So we use
# k-fold cross-validation and always report **mean ± std**.
#
# ## 4. Stratified folds
#
# Deal each grade out over the folds like cards, so every fold has the same mix of grades.

# %%
def stratified_kfold(y, folds=5, seed=0):
    rng = np.random.default_rng(seed)
    fold_of = np.empty(len(y), dtype=int)
    for c in np.unique(y):
        rows = np.flatnonzero(y == c)
        rng.shuffle(rows)
        fold_of[rows] = np.arange(len(rows)) % folds
    return [(np.flatnonzero(fold_of != f), np.flatnonzero(fold_of == f)) for f in range(folds)]

for f, (tr, te) in enumerate(stratified_kfold(y)):
    print(f"fold {f}: {len(te)} wines, share high = {np.mean(y[te] == 2):.3f}")
print(f"whole dataset: share high = {np.mean(y == 2):.3f}")

# %% [markdown]
# ## 5. Tuning on the test folds = cheating, a little
#
# Choose the best k by 5-fold CV and report that same CV score. The k was chosen *because* it did well
# on those folds, so the score is optimistic.
#
# **Nested CV:** the outer fold is held out; tuning happens **only** inside the outer training rows,
# with its own inner folds; the chosen model is scored once on the outer fold.

# %%
K_GRID = [1, 5, 9, 15, 21, 31]

def cv_score_per_k(X, y, splits):
    """Mean macro-F1 for every k in K_GRID, scaling fitted inside each fold."""
    out = np.zeros(len(K_GRID))
    for tr, te in splits:
        Xtr, Xte = scale(X[tr], X[te])
        order, dist = neighbours(Xtr, Xte, max(K_GRID))
        out += [macro_f1(y[te], knn_vote(y[tr], order, dist, k)) for k in K_GRID]
    return out / len(splits)

outer = stratified_kfold(y, 5, seed=1)

# the optimistic way: tune and report on the same folds
plain = cv_score_per_k(X, y, outer)
print(f"plain CV, best k = {K_GRID[plain.argmax()]}  score {plain.max():.4f}")

# the honest way
outer_scores, chosen = [], []
for tr, te in outer:
    inner = [(tr[a], tr[b]) for a, b in stratified_kfold(y[tr], 3, seed=2)]
    k = K_GRID[cv_score_per_k(X, y, inner).argmax()]          # decided WITHOUT the outer fold
    Xtr, Xte = scale(X[tr], X[te])
    order, dist = neighbours(Xtr, Xte, k)
    outer_scores.append(macro_f1(y[te], knn_vote(y[tr], order, dist, k)))
    chosen.append(k)
print("nested CV, k chosen per fold =", chosen)
print(f"nested score {np.mean(outer_scores):.4f} ± {np.std(outer_scores):.4f}")

# %% [markdown]
# Here the two are close — this tuning is not badly overfitted. With a bigger search (weights,
# α, p, scaling…) the gap grows, and only the nested number is honest. Note that each outer fold may
# pick a different k: what is evaluated is the **procedure** "tune, then predict".
#
# ## ✍️ Try it yourself
#
# 1. Replace `stratified_kfold` with plain random folds. How much does the share of high wines vary?
# 2. Add `alpha` (0, 0.5, 1) to the grid. Does the gap between plain and nested CV grow?
# 3. **Leak on purpose:** scale `X` once on all rows before the CV. Does the score change? Why is it
#    still wrong even if it does not?
#
# Then solve exercises 10–12 in `03_exercises/`.
