"""Lesson 15 - k-nearest neighbours on the real wines: distance, the weighted vote, k, the imbalance correction."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from matplotlib.colors import ListedColormap
from sklearn.model_selection import StratifiedKFold
from sklearn.neighbors import NearestNeighbors

L = Lesson(__file__)
rng = np.random.default_rng(2)
GRADES = ["low", "medium", "high"]
GCOL = [BLUE, YELLOW, ORANGE]

red = np.genfromtxt(data("32_WineGrader", "winequality-red.csv"), delimiter=";", skip_header=1)
wht = np.genfromtxt(data("32_WineGrader", "winequality-white.csv"), delimiter=";", skip_header=1)
W = np.vstack([red, wht])
colour = np.r_[np.zeros(len(red)), np.ones(len(wht))]
_, first = np.unique(np.c_[W, colour], axis=0, return_index=True)
W = W[np.sort(first)]
X, g = W[:, :-1], np.digitize(W[:, -1], [6, 7])      # <=5 low, 6 medium, >=7 high
Z = (X - X.mean(0)) / X.std(0)
ALC, VA = 10, 1                                       # alcohol, volatile acidity
P2 = Z[:, [ALC, VA]]


def vote(dists, labels, prior=None, alpha=0.0, eps=1e-9):
    s = np.zeros(3)
    for d, lab in zip(dists, labels):
        w = 1 / (d + eps)
        if prior is not None:
            w /= prior[lab] ** alpha
        s[lab] += w
    return s


# ---------------------------------------------------------------- 1. the query and its neighbours
sample = rng.choice(len(g), 700, replace=False)
S, gs = P2[sample], g[sample]
q = np.array([0.55, -0.35])
d_all = np.sqrt(((S - q) ** 2).sum(1))
order = np.argsort(d_all)


def draw_query(a1, a2, k):
    a1.clear()
    for c in range(3):
        a1.scatter(S[gs == c, 0], S[gs == c, 1], s=14, color=GCOL[c], alpha=0.45, label=GRADES[c])
    nn = order[:k]
    for c in range(3):
        m = gs[nn] == c
        a1.scatter(S[nn][m, 0], S[nn][m, 1], s=80, color=GCOL[c], edgecolor=INK, lw=1.2, zorder=3)
    a1.add_patch(plt.Circle(q, d_all[order[k - 1]], fill=False, color=INK, ls="--", lw=1.5))
    a1.scatter(*q, marker="*", s=420, color=INK, zorder=4, label="new wine")
    a1.set_xlim(q[0] - 1.4, q[0] + 1.4)
    a1.set_ylim(q[1] - 1.2, q[1] + 1.2)
    a1.set_aspect("equal")
    a1.set_xlabel("alcohol (z-score)")
    a1.set_ylabel("volatile acidity (z-score)")
    a1.set_title(f"k = {k}: the {k} nearest wines")
    a1.legend(loc="upper right", fontsize=9)
    a2.clear()
    s = vote(d_all[order[:k]], gs[order[:k]])
    a2.bar(range(3), s / s.sum(), color=GCOL)
    a2.set_xticks(range(3), GRADES)
    a2.set_ylim(0, 1)
    win = int(np.argmax(s))
    a2.set_title(f"weighted vote → {GRADES[win].upper()}  (confidence {s[win] / s.sum():.2f})")
    a2.set_ylabel("share of the votes (1/distance)")


if L.wanted("knn_query"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1.3, 1]})
    ks = [1, 2, 3, 4, 5, 7, 9, 12, 15, 20, 25, 35, 50]
    frames = ks + [ks[-1]] * 2
    L.animate(fig, lambda f: draw_query(a1, a2, frames[f]), len(frames), "knn_query", fps=1)

# ---------------------------------------------------------------- 2. decision regions for k = 1, 15, 151
if L.wanted("k_regions"):
    gx, gy = np.meshgrid(np.linspace(-2.2, 3.2, 220), np.linspace(-2.2, 3.0, 220))
    G = np.c_[gx.ravel(), gy.ravel()]
    nnm = NearestNeighbors().fit(P2)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5.6))
    cmap = ListedColormap(["#c9dcf4", "#fbe7b8", "#f9cdb9"])
    for ax, k in zip(axes, [1, 15, 151]):
        dist, idx = nnm.kneighbors(G, n_neighbors=k)
        pred = np.array([np.argmax(vote(d, g[i])) for d, i in zip(dist, idx)])
        ax.contourf(gx, gy, pred.reshape(gx.shape), levels=[-0.5, 0.5, 1.5, 2.5], cmap=cmap)
        for c in range(3):
            ax.scatter(S[gs == c, 0], S[gs == c, 1], s=7, color=GCOL[c], alpha=0.6)
        ax.set_ylim(-2.2, 3.0)
        ax.set_aspect("equal")
        ax.set_title({1: "k = 1: islands around single wines", 15: "k = 15: local and smooth",
                      151: "k = 151: no longer local"}[k], fontsize=12.5)
        ax.set_xlabel("alcohol (z)")
    axes[0].set_ylabel("volatile acidity (z)")
    caption(fig, "Background = the grade k-NN would give a new wine there (all 5,320 unique wines, two features).  "
                 "blue low · yellow medium · orange high")
    L.save(fig, "k_regions")

# ---------------------------------------------------------------- 3. Minkowski unit circles
if L.wanted("minkowski"):
    fig, ax = plt.subplots(figsize=(7.5, 7))
    t = np.linspace(0, 2 * np.pi, 400)
    for p, col, lab in [(1, ORANGE, "p = 1  Manhattan"), (2, BLUE, "p = 2  Euclidean"), (4, AQUA, "p = 4")]:
        x, y_ = np.cos(t), np.sin(t)
        n = (np.abs(x) ** p + np.abs(y_) ** p) ** (1 / p)
        ax.plot(x / n, y_ / n, color=col, lw=3, label=lab)
    ax.plot([0, 3 / 5], [0, 4 / 5], color=INK2, lw=1)
    ax.set_aspect("equal")
    ax.axhline(0, color=GRID)
    ax.axvline(0, color=GRID)
    ax.set_title("All points at distance 1 from the centre")
    ax.legend(loc="lower right")
    L.save(fig, "minkowski")

# ---------------------------------------------------------------- 4. the guide's vote and alpha examples
if L.wanted("vote_examples"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8))
    s = np.array([0, 1 / 0.9 + 1 / 1.0, 1 / 0.1])
    a1.bar(range(3), s, color=GCOL)
    for i, v in enumerate(s):
        a1.text(i, v + 0.2, f"{v:.1f}", ha="center", fontsize=13)
    a1.set_xticks(range(3), GRADES)
    a1.set_title("neighbours: high at 0.10, medium at 0.90 and 1.00\n→ HIGH, confidence 10.0 / 12.1 = 0.83",
                 fontsize=12.5)
    a1.set_ylabel("sum of 1 / distance")
    prior = np.array([0.37, 0.44, 0.19])
    for j, (alpha, col) in enumerate([(0, MUTED), (0.5, AQUA), (1, ORANGE)]):
        v = np.array([0, 2 / 0.44 ** alpha, 1 / 0.19 ** alpha])
        a2.bar(np.arange(3) + (j - 1) * 0.27, v, 0.27, color=col, label=f"alpha = {alpha}")
    a2.set_xticks(range(3), GRADES)
    a2.set_title("neighbours: medium, medium, high (all at distance 1)\nvote ÷ prior^alpha", fontsize=12.5)
    a2.legend()
    L.save(fig, "vote_examples")

# ---------------------------------------------------------------- 5. k and alpha on the real data (5-fold, 11 features)
if L.wanted("tuning_curves"):
    skf = StratifiedKFold(5, shuffle=True, random_state=0)
    folds = []
    for tr, te in skf.split(X, g):
        mu, sd = X[tr].mean(0), X[tr].std(0)                 # scaler fitted on the training rows only
        Ztr, Zte = (X[tr] - mu) / sd, (X[te] - mu) / sd
        dist, idx = NearestNeighbors().fit(Ztr).kneighbors(Zte, n_neighbors=101)
        prior = np.bincount(g[tr], minlength=3) / len(tr)
        folds.append((g[tr][idx], dist, g[te], prior))

    def score(k, alpha):
        f1s, rec_high = [], []
        for lab, dist, truth, prior in folds:
            pred = np.array([np.argmax(vote(d[:k], l[:k], prior, alpha)) for d, l in zip(dist, lab)])
            f = []
            for c in range(3):
                tp = ((pred == c) & (truth == c)).sum()
                pr = tp / max((pred == c).sum(), 1)
                rc = tp / (truth == c).sum()
                f.append(2 * pr * rc / (pr + rc) if pr + rc else 0)
            f1s.append(np.mean(f))
            rec_high.append(((pred == 2) & (truth == 2)).sum() / (truth == 2).sum())
        return np.mean(f1s), np.mean(rec_high)

    ks = [1, 3, 5, 9, 15, 21, 31, 51, 75, 101]
    kc = [score(k, 0.5)[0] for k in ks]
    alphas = np.linspace(0, 1.2, 7)
    ac = [score(21, a) for a in alphas]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8))
    a1.plot(ks, kc, "o-", color=VIOLET)
    a1.set_xscale("log")
    a1.set_xticks(ks, [str(k) for k in ks])
    a1.set_xlabel("k")
    a1.set_ylabel("macro-F1 (5-fold)")
    a1.set_title("k: too small = noise, too big = not local")
    a2.plot(alphas, [a[0] for a in ac], "o-", color=VIOLET, label="macro-F1")
    a2.plot(alphas, [a[1] for a in ac], "s-", color=ORANGE, label='recall of "high"')
    a2.set_xlabel("alpha (imbalance correction)")
    a2.set_title("alpha: find the rare 'high' wines")
    a2.legend()
    print("  k:", list(zip(ks, np.round(kc, 3))))
    print("  alpha (k=21):", [(round(a, 2), round(m, 3), round(r, 3)) for a, (m, r) in zip(alphas, ac)])
    caption(fig, "All 11 features, z-scored inside each fold, weighted vote.  A quick version of Seif's tuning table.")
    L.save(fig, "tuning_curves")


# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 6. the paper example, drawn
if L.wanted("paper_example"):
    pts = {"W1": ((0.6, 0.1), 2), "W2": ((0.4, 0.5), 1), "W3": ((-0.3, 0.0), 0), "W4": ((1.5, 0.3), 2)}
    Xq = np.array([0.5, 0.2])
    fig, ax = plt.subplots(figsize=(10, 6))
    for name, (p, lab) in pts.items():
        p = np.array(p)
        d = np.linalg.norm(p - Xq)
        ax.plot([Xq[0], p[0]], [Xq[1], p[1]], color=MUTED, ls="--", lw=1.5)
        off = {"W1": (0.12, -0.02), "W2": (-0.12, 0.0), "W3": (0, -0.07), "W4": (0, -0.07)}[name]
        ax.text((Xq[0] + p[0]) / 2 + off[0], (Xq[1] + p[1]) / 2 + off[1], f"d = {d:.2f}", fontsize=11.5, color=INK2,
                ha="center", bbox=dict(fc=PAPER, ec="none", pad=1))
        ax.scatter(*p, s=420, color=GCOL[lab], edgecolor=INK, zorder=3)
        above = name == "W2"
        ax.text(p[0], p[1] + (0.09 if above else -0.09), f"{name}\n{GRADES[lab]}", ha="center",
                va="bottom" if above else "top", fontsize=12)
    ax.scatter(*Xq, s=500, marker="*", color=INK, zorder=4)
    ax.annotate("X (the new wine)", Xq, xytext=(0.05, -0.45), fontsize=12, weight="bold",
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.add_patch(plt.Circle(Xq, 0.83, fill=False, ec=GREEN, lw=2, ls=":"))
    ax.text(-0.35, 0.95, "k = 3: the 3 nearest are inside the green circle", color=GREEN, fontsize=12)
    ax.set_xlim(-0.6, 1.8)
    ax.set_ylim(-0.75, 1.1)
    ax.set_aspect("equal")
    ax.set_xlabel("alcohol (scaled)")
    ax.set_ylabel("acidity (scaled)")
    ax.set_title("The paper example: distances from X to the four graded wines")
    L.save(fig, "paper_example")

# ---------------------------------------------------------------- 7. alpha sweeping: the winner flips
if L.wanted("alpha_sweep"):
    prior = np.array([0.37, 0.44, 0.19])
    labs = [1, 1, 2]                      # medium, medium, high - all at distance 1
    alphas = np.r_[np.linspace(0, 1, 21), [1] * 4]
    fig, ax = plt.subplots(figsize=(10, 5.2))

    def upd(k):
        a = alphas[k]
        v = vote([1, 1, 1], labs, prior, a)
        ax.clear()
        bars = ax.bar(GRADES, v, color=GCOL, edgecolor=INK)
        win = int(np.argmax(v))
        bars[win].set_linewidth(4)
        for i, val in enumerate(v):
            ax.text(i, val + 0.1, f"{val:.2f}", ha="center", fontsize=13, weight="bold" if i == win else "normal")
        ax.set_ylim(0, 6.2)
        ax.set_ylabel("total vote")
        ax.set_title(f"alpha = {a:.2f}  →  winner: {GRADES[win].upper()}\n"
                     "(neighbours: medium, medium, high - all at distance 1)", fontsize=13)
    L.animate(fig, upd, len(alphas), "alpha_sweep", fps=3)

# ---------------------------------------------------------------- 8. "nearest neighbours" in everyday life
if L.wanted("knn_world"):
    tiles = [("Estate agent", "a flat = (size, rooms, area, floor)", "price ≈ average price of the\n5 most similar flats sold"),
             ("Netflix / Spotify", "you = what you watched / played", "people most like you\nloved this → try it"),
             ("A new student", "joins a class", "'you'll be like the friends\nyou sit with'"),
             ("Plant identification app", "a photo → numbers", "the closest photos in the\ndatabase say: rose"),
             ("Doctor", "a patient = (age, symptoms, tests)", "the most similar past\npatients had…"),
             ("Seif's WineGrader", "a wine = 11 lab numbers", "the 15 most similar\ngraded wines vote")]
    fig, axes = plt.subplots(2, 3, figsize=(15, 6.4))
    for ax, (title, what, how), col in zip(axes.ravel(), tiles, SERIES):
        blank(ax)
        ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0,rounding_size=0.05", lw=2.5,
                                    edgecolor=col, facecolor=PAPER))
        ax.add_patch(FancyBboxPatch((0.02, 0.74), 0.96, 0.24, boxstyle="round,pad=0,rounding_size=0.05", lw=0,
                                    facecolor=col))
        ax.text(0.5, 0.86, title, ha="center", va="center", color="white", fontsize=13.5, weight="bold")
        ax.text(0.06, 0.52, what, fontsize=11.2)
        ax.text(0.06, 0.25, how, fontsize=11.2, weight="bold", wrap=True)
    fig.suptitle("\"Find the most similar known cases and copy their answer\" - k-NN in real life", fontsize=14,
                 weight="bold")
    L.save(fig, "knn_world")

if L.live:
    from matplotlib.widgets import Slider
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6.5), gridspec_kw={"width_ratios": [1.3, 1]})
    fig.subplots_adjust(bottom=0.18)
    s = Slider(fig.add_axes([0.2, 0.05, 0.6, 0.04]), "k", 1, 60, valinit=5, valstep=1)
    s.on_changed(lambda v: (draw_query(a1, a2, int(v)), fig.canvas.draw_idle()))
    draw_query(a1, a2, 5)
    plt.show()
