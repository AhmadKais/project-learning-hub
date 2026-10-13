# %% [markdown]
# # 05 · Teaching k-NN to weigh its features
#
# **Read first:** `01_theory/06_tuning_weights.md`
#
# 1. why gradient descent cannot learn these weights → coordinate search
# 2. the incremental update of the distance matrix: $D_{new} = D + (w_{new}-w_{old})\,|\Delta_i|^p$
# 3. proof that the fast update gives the same score as recomputing from scratch
# 4. a test on purpose-built data: two pure-noise features — does the search find them?
# 5. the real wines: does it help?

# %%
import time
import numpy as np
from pathlib import Path

# %% [markdown]
# ## 1. A k-NN scored on fixed folds, written around a distance matrix
#
# For a fold, `D[i, j]` = power distance from test wine i to training wine j. The score only needs `D`.

# %%
def macro_f1(y_true, y_pred, n=3):
    f1 = []
    for c in range(n):
        tp = np.sum((y_pred == c) & (y_true == c))
        p_, r_ = tp / max(np.sum(y_pred == c), 1), tp / max(np.sum(y_true == c), 1)
        f1.append(0 if p_ + r_ == 0 else 2 * p_ * r_ / (p_ + r_))
    return np.mean(f1)


class FoldDistances:
    """Everything needed to score one fold quickly, and to update D when a weight changes."""

    def __init__(self, Xtr, ytr, Xte, yte, w, p=2):
        self.Xtr, self.ytr, self.Xte, self.yte, self.p = Xtr, ytr, Xte, yte, p
        self.D = sum(w[i] * self.term(i) for i in range(Xtr.shape[1]))

    def term(self, i):
        """|Δ_i|^p : the contribution of feature i to every distance, before weighting."""
        return np.abs(self.Xte[:, i, None] - self.Xtr[None, :, i]) ** self.p

    def score(self, D, k=15):
        order = np.argsort(D, axis=1, kind="stable")[:, :k]
        dist = np.take_along_axis(D, order, 1) ** (1 / self.p)
        g = self.ytr[order]
        votes = np.stack([((g == c) / (dist + 1e-9)).sum(1) for c in range(3)], 1)
        return macro_f1(self.yte, votes.argmax(1))


def make_folds(X, y, w, folds=3, seed=0):
    rng = np.random.default_rng(seed)
    fold_of = np.empty(len(y), int)
    for c in np.unique(y):
        rows = rng.permutation(np.flatnonzero(y == c))
        fold_of[rows] = np.arange(len(rows)) % folds
    out = []
    for f in range(folds):
        tr, te = fold_of != f, fold_of == f
        m, sd = X[tr].mean(0), X[tr].std(0); sd[sd == 0] = 1
        out.append(FoldDistances((X[tr] - m) / sd, y[tr], (X[te] - m) / sd, y[te], w))
    return out


def cv_score(fds):
    return np.mean([fd.score(fd.D) for fd in fds])

# %% [markdown]
# ## 2. Coordinate search with the incremental update
#
# The score jumps when a neighbour swaps and is flat otherwise — there is no slope to follow.
# So: for each feature in turn, try its weight × 0, × 0.5, × 1.5, × 2, and keep a change only if the
# score improves by more than a **tolerance**. Stop when a whole pass changes nothing.
#
# The trick: the distance is a **sum over features**, so changing $w_i$ changes $D$ by one term only.

# %%
def learn_weights(fds, n_features, factors=(0, 0.5, 1.5, 2), tolerance=0.002, max_passes=3, log=print):
    w = np.ones(n_features)
    best = cv_score(fds)
    log(f"start: score {best:.4f}")
    for pass_no in range(1, max_passes + 1):
        changed = False
        for i in range(n_features):
            if w[i] == 0:
                continue                                   # a removed feature stays removed
            terms = [fd.term(i) for fd in fds]
            for factor in factors:
                new = w[i] * factor
                trial = [fd.D + (new - w[i]) * t for fd, t in zip(fds, terms)]
                s = np.mean([fd.score(D) for fd, D in zip(fds, trial)])
                if s > best + tolerance:
                    best, w[i], changed = s, new, True
                    for fd, D in zip(fds, trial):
                        fd.D = D                           # accept the trial
        log(f"pass {pass_no}: score {best:.4f}  weights {np.round(w, 2)}")
        if not changed:
            break
    return w, best

# %% [markdown]
# ## 3. A test where we *know* the answer
#
# Make 3 classes from 4 useful features, then add 2 features of pure noise. A good weight learner
# should switch the noise off.

# %%
rng = np.random.default_rng(0)
n = 2000
useful = rng.normal(size=(n, 4))
true_importance = np.array([1.0, 0.8, 0.6, 0.4])
y_syn = np.digitize(useful @ true_importance + rng.normal(0, .3, n), [-0.8, 0.8])
noise = rng.normal(size=(n, 2))
X_syn = np.column_stack([useful, noise])

fds = make_folds(X_syn, y_syn, np.ones(6))
w_syn, _ = learn_weights(fds, 6)
print("\nlearned weights:", w_syn, "  <- the last two are the noise features")
print("true importance:", true_importance)

# %% [markdown]
# Both noise features are switched off (weight 0), and the useful ones come out roughly in the order
# of their true importance. Make the labels noisier (`rng.normal(0, .5, n)`) and the search becomes
# less sure of itself — an improvement must beat the tolerance to be accepted.
#
# ## 4. Can we trust the fast version?
#
# Recompute the score **from scratch** with the final weights. It must equal the score the incremental
# search ended with. If an update was applied twice, or forgotten, these differ.

# %%
fresh = make_folds(X_syn, y_syn, w_syn)
print(f"incremental: {cv_score(fds):.6f}   from scratch: {cv_score(fresh):.6f}")
print("identical:", np.allclose(cv_score(fds), cv_score(fresh)))

# %% [markdown]
# ## 5. The real wines

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

t0 = time.perf_counter()
fds = make_folds(X, y, np.ones(12))
w_wine, best = learn_weights(fds, 12, max_passes=1)
print(f"\n{time.perf_counter() - t0:.0f} s for one pass")

# %% [markdown]
# Inside these folds the score may rise a little. Is it real? Notebook 04 showed the answer: only a
# **nested** evaluation can tell. In the full project the nested result is
#
# | weights | macro-F1 |
# |---|---|
# | uniform | 0.583 ± 0.018 |
# | learned | 0.579 ± 0.015 |
#
# — no real gain on wine, while the synthetic test proves the method works when there *are* useless
# features. "It did not help, and here is why" is a result you can defend.
#
# ## ✍️ Try it yourself
#
# 1. Set `tolerance=0`. How many more changes are accepted on the wines? Are they real?
# 2. Time one trial with the incremental update and one with `make_folds(X, y, new_w)` from scratch.
#    How many times faster is the update?
# 3. Make one noise feature *weakly* useful (add `0.2 * y_syn` to it). What weight does it get?
4. Change `rng.normal(0, .3, n)` to `.5`. Are both noise features still found? Why not?
#
# Then solve exercise 13 in `03_exercises/`.
