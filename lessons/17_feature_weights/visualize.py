"""Lesson 17 - learning a weight per feature: why no gradient, coordinate search, the incremental update."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from sklearn.model_selection import StratifiedKFold

L = Lesson(__file__)
rng = np.random.default_rng(6)
NAMES = ["fixed acid.", "volatile acid.", "citric acid", "resid. sugar", "chlorides", "free SO₂", "total SO₂",
         "density", "pH", "sulphates", "alcohol"]

red = np.genfromtxt(data("32_WineGrader", "winequality-red.csv"), delimiter=";", skip_header=1)
wht = np.genfromtxt(data("32_WineGrader", "winequality-white.csv"), delimiter=";", skip_header=1)
W = np.vstack([red, wht])
colour = np.r_[np.zeros(len(red)), np.ones(len(wht))]
_, first = np.unique(np.c_[W, colour], axis=0, return_index=True)
W = W[np.sort(first)]
W = W[rng.choice(len(W), 2400, replace=False)]           # a sample, so it runs in seconds
X, g = W[:, :-1], np.digitize(W[:, -1], [6, 7])
K, ALPHA, P = 21, 0.5, 2

# one fold set (3 folds), each with its per-feature term matrices |Δi|^p
folds = []
for tr, te in StratifiedKFold(3, shuffle=True, random_state=0).split(X, g):
    mu, sd = X[tr].mean(0), X[tr].std(0)
    A, B = ((X[te] - mu) / sd).astype(np.float32), ((X[tr] - mu) / sd).astype(np.float32)
    terms = [np.abs(A[:, None, i] - B[None, :, i]) ** P for i in range(11)]
    prior = np.bincount(g[tr], minlength=3) / len(tr)
    folds.append({"terms": terms, "ytr": g[tr], "yte": g[te], "prior": prior})


def macro_f1(pred, truth):
    f = []
    for c in range(3):
        tp = ((pred == c) & (truth == c)).sum()
        pr, rc = tp / max((pred == c).sum(), 1), tp / max((truth == c).sum(), 1)
        f.append(2 * pr * rc / (pr + rc) if pr + rc else 0)
    return np.mean(f)


def score(fold, D):
    idx = np.argpartition(D, K, axis=1)[:, :K]
    d = np.sqrt(np.take_along_axis(D, idx, 1))
    lab = fold["ytr"][idx]
    v = np.zeros((len(D), 3))
    for c in range(3):
        v[:, c] = ((lab == c) / (d + 1e-9)).sum(1) / fold["prior"][c] ** ALPHA
    return macro_f1(v.argmax(1), fold["yte"])


def full_D(fold, w):
    return sum(wi * t for wi, t in zip(w, fold["terms"]))


def cv_score(w, Ds=None):
    Ds = Ds or [full_D(f, w) for f in folds]
    return np.mean([score(f, D) for f, D in zip(folds, Ds)])


# ---------------------------------------------------------------- 1. the score is a staircase
if L.wanted("staircase"):
    w = np.ones(11)
    ws = np.linspace(0, 3, 61)
    fig, ax = plt.subplots(figsize=(12, 4.8))
    for feat, col in [(10, ORANGE), (1, BLUE)]:
        sc = []
        for v in ws:
            w2 = w.copy()
            w2[feat] = v
            sc.append(cv_score(w2))
        ax.step(ws, sc, where="mid", color=col, label=f"weight of {NAMES[feat]}")
    ax.set_xlabel("weight of one feature (all others = 1)")
    ax.set_ylabel("macro-F1 (3-fold)")
    ax.set_title("The score jumps in steps: there is no slope for gradient descent to follow")
    ax.legend()
    L.save(fig, "staircase")

# ---------------------------------------------------------------- 2. coordinate search, animated
if L.wanted("coordinate_search"):
    w = np.ones(11)
    Ds = [full_D(f, w) for f in folds]
    best = cv_score(w, Ds)
    log = [(w.copy(), best, None, None, None)]
    for rnd in range(2):
        changed = False
        for i in range(11):
            if w[i] == 0:
                continue
            for factor in (0, 0.5, 1.5, 2):
                new = w[i] * factor
                trial = [D + (new - w[i]) * f["terms"][i] for f, D in zip(folds, Ds)]   # the incremental update
                s = cv_score(None, trial)
                ok = s > best + 0.002
                log.append((w.copy(), best, i, factor, (s, ok)))
                if ok:
                    best, w[i], Ds, changed = s, new, trial, True
                    break
        if not changed:
            break
    log.append((w.copy(), best, None, None, None))
    full = cv_score(w)
    print(f"  final weights {np.round(w, 2)}  score {best:.4f}  full recompute {full:.4f}")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 6), gridspec_kw={"width_ratios": [1.4, 1]})
    fig.subplots_adjust(bottom=0.24, wspace=0.25)

    def upd(f):
        wk, bk, i, factor, res = log[f]
        a1.clear()
        cols = [GRID if v == 0 else BLUE for v in wk]
        if i is not None:
            cols[i] = GREEN if res[1] else ORANGE
        shown = wk.copy()
        if i is not None:
            shown[i] = wk[i] * factor
        a1.bar(range(11), shown, color=cols)
        a1.set_xticks(range(11), NAMES, rotation=45, ha="right")
        a1.set_ylim(0, 4.2)
        a1.set_ylabel("weight")
        if i is None:
            a1.set_title("start: every weight = 1" if f == 0 else "done: no change helps by more than 0.002")
        else:
            a1.set_title(f"try {NAMES[i]} × {factor}:  score {res[0]:.4f} vs best {bk:.4f}  →  "
                         f"{'KEEP' if res[1] else 'reject'}", fontsize=12.5, color=GREEN if res[1] else INK)
        a2.clear()
        tried = [l[4][0] for l in log[1: f + 1] if l[4]]
        bests = [l[1] for l in log[: f + 1]]
        a2.plot(range(len(tried)), tried, ".", color=MUTED, label="each trial")
        a2.plot(range(len(bests)), bests, color=GREEN, lw=2.5, label="best so far")
        a2.set_xlim(0, len(log))
        a2.set_ylim(min(l[4][0] for l in log if l[4]) - 0.005, max(l[1] for l in log) + 0.01)
        a2.set_xlabel("trial")
        a2.set_ylabel("macro-F1 (3-fold)")
        a2.legend(loc="lower right", fontsize=10)
    frames = list(range(len(log))) + [len(log) - 1] * 4
    L.animate(fig, lambda k: upd(frames[k]), len(frames), "coordinate_search", fps=3)

# ---------------------------------------------------------------- 3. the incremental update, as matrices
if L.wanted("incremental"):
    a = np.array([[0.2, 1.0], [1.5, 0.3], [0.9, 0.8]])        # 3 test wines, 2 features
    b = np.array([[0.0, 0.0], [1.0, 1.0], [2.0, 0.5], [0.5, 1.5]])
    T = [np.abs(a[:, None, i] - b[None, :, i]) ** 2 for i in range(2)]
    w_old, w_new = np.array([1.0, 1.0]), np.array([1.0, 2.0])
    D = w_old[0] * T[0] + w_old[1] * T[1]
    D2 = D + (w_new[1] - w_old[1]) * T[1]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, M, title in [(axes[0], D, "D  (weights 1, 1)"), (axes[1], T[1], "|Δ₂|²  (feature 2 only)"),
                         (axes[2], D2, "D + (2 − 1)·|Δ₂|²  =  D with weights (1, 2)")]:
        ax.imshow(M, cmap="Purples", vmin=0, vmax=D2.max())
        ax.grid(False)
        for i in range(3):
            for j in range(4):
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=13)
        ax.set_xticks(range(4), [f"train {j + 1}" for j in range(4)])
        ax.set_yticks(range(3), [f"test {i + 1}" for i in range(3)])
        ax.set_title(title, fontsize=12.5)
    direct = w_new[0] * T[0] + w_new[1] * T[1]
    caption(fig, f"Change ONE weight → add one matrix.  Check: max difference from a full recompute = "
                 f"{np.abs(direct - D2).max():.1e}")
    L.save(fig, "incremental")
