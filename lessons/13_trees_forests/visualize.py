"""Lesson 13 - decision trees (Gini), overfitting by depth, random forests (bootstrap + vote), importance."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from matplotlib.colors import ListedColormap
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

L = Lesson(__file__)
rng = np.random.default_rng(1)
X, y, names = phish_features()
CMAP = ListedColormap([LIGHT_BLUE, LIGHT_ORANGE])


def gini(counts):
    counts = np.asarray(counts, float)
    p = counts / counts.sum()
    return 1 - (p ** 2).sum()


# ---------------------------------------------------------------- 1. Gini impurity
if L.wanted("gini"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8))
    p = np.linspace(0, 1, 200)
    a1.plot(p, 1 - p ** 2 - (1 - p) ** 2, color=INK)
    for pp, lab in [(0, "pure"), (0.2, "4 vs 1"), (0.5, "50 / 50")]:
        g = 1 - pp ** 2 - (1 - pp) ** 2
        a1.plot(pp, g, "o", color=ORANGE, ms=10)
        a1.text(pp + 0.02, g + 0.02, f"{lab}: {g:.2f}", fontsize=12)
    a1.set_xlabel("share of phishing in the group")
    a1.set_ylabel("Gini = 1 − Σ p²")
    a1.set_title("Gini impurity: how MIXED a group is")
    # the guide's example: 10 URLs, split A (has_https) vs split B (num_dots > 2)
    blank(a2)
    a2.set_title("Choosing the first question (10 URLs: 5 good, 5 phishing)")

    def group(x, yy, good, bad, label):
        for i in range(good):
            a2.add_patch(plt.Circle((x + i * 0.035, yy), 0.014, color=BLUE))
        for i in range(bad):
            a2.add_patch(plt.Circle((x + (good + i) * 0.035, yy), 0.014, color=ORANGE))
        a2.text(x, yy - 0.07, f"{label}  Gini {gini([good, bad]):.2f}", fontsize=11)

    a2.text(0.02, 0.86, "split A:  has_https?", fontsize=13, weight="bold")
    group(0.04, 0.76, 4, 1, "yes")
    group(0.52, 0.76, 1, 4, "no")
    a2.text(0.02, 0.6, "weighted = 0.32     gain = 0.50 − 0.32 = 0.18  ✓", fontsize=12, color=GREEN)
    a2.text(0.02, 0.4, "split B:  num_dots > 2?", fontsize=13, weight="bold")
    group(0.04, 0.3, 3, 3, "yes")
    group(0.52, 0.3, 2, 2, "no")
    a2.text(0.02, 0.14, "weighted = 0.50     gain = 0  ✗", fontsize=12, color=RED)
    a2.set_ylim(0.05, 0.95)
    L.save(fig, "gini")

# ---------------------------------------------------------------- 2. a tree growing (2-D toy data you can SEE)
# Two real URL features overlap too much to see anything, so the pictures use a toy set with two
# overlapping classes; the real 20-feature numbers are in the importance chart below.
from sklearn.datasets import make_moons
X2, y2 = make_moons(1500, noise=0.32, random_state=3)
Xtr, Xte, ytr, yte = train_test_split(X2, y2, test_size=0.5, random_state=0, stratify=y2)
show = rng.choice(len(ytr), 400, replace=False)
gx, gy = np.meshgrid(np.linspace(-1.8, 2.8, 300), np.linspace(-1.4, 1.9, 300))
grid = np.c_[gx.ravel(), gy.ravel()]


def draw_region(ax, model, title):
    ax.clear()
    ax.contourf(gx, gy, model.predict(grid).reshape(gx.shape), levels=[-0.5, 0.5, 1.5], cmap=CMAP)
    s = show
    ax.scatter(Xtr[s][ytr[s] == 0, 0], Xtr[s][ytr[s] == 0, 1], s=14, color=BLUE, label="class 0")
    ax.scatter(Xtr[s][ytr[s] == 1, 0], Xtr[s][ytr[s] == 1, 1], s=14, color=ORANGE, label="class 1")
    ax.set_xlim(-1.8, 2.8)
    ax.set_ylim(-1.4, 1.9)
    ax.set_xlabel("feature 1")
    ax.set_ylabel("feature 2")
    ax.set_title(title, fontsize=12.5)


depths = list(range(1, 13)) + [None]
trees = [DecisionTreeClassifier(max_depth=d, random_state=0).fit(Xtr, ytr) for d in depths]
acc = [(t.score(Xtr, ytr), t.score(Xte, yte)) for t in trees]

if L.wanted("tree_growing"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1.2, 1]})

    def upd(k):
        d = depths[k]
        draw_region(a1, trees[k], f"max_depth = {d if d else 'unlimited'}   ({trees[k].get_n_leaves()} leaves)")
        a1.legend(loc="upper right", fontsize=9)
        a2.clear()
        xs = np.arange(len(depths))
        a2.plot(xs[: k + 1], [a[0] for a in acc[: k + 1]], "o-", color=BLUE, label="train accuracy")
        a2.plot(xs[: k + 1], [a[1] for a in acc[: k + 1]], "^-", color=ORANGE, label="test accuracy")
        a2.set_xticks(xs, [str(d) if d else "∞" for d in depths])
        a2.set_xlim(-0.5, len(depths) - 0.5)
        a2.set_ylim(0.7, 1.01)
        a2.set_xlabel("max_depth")
        a2.set_title("deeper = memorises the training set")
        a2.legend(loc="lower right")
    L.animate(fig, upd, len(depths), "tree_growing", fps=1)

# ---------------------------------------------------------------- 3. a real tree, readable
if L.wanted("tree_diagram"):
    Xa_tr, _, ya_tr, _ = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
    # trained on 1 - y so that scikit-learn's colours match ours: phishing orange, legitimate blue
    t = DecisionTreeClassifier(max_depth=3, random_state=0).fit(Xa_tr, 1 - ya_tr)
    fig, ax = plt.subplots(figsize=(17, 7))
    plot_tree(t, feature_names=names, class_names=["phish", "legit"], filled=True, rounded=True, fontsize=10,
              impurity=True, proportion=False, ax=ax)
    ax.set_title("A depth-3 tree learned from the 20 PhishGuard features (orange = mostly phishing, blue = mostly legitimate)")
    L.save(fig, "tree_diagram")

# ---------------------------------------------------------------- 4. forest: many trees, one vote
if L.wanted("forest_vote"):
    forest = RandomForestClassifier(n_estimators=100, max_features=1, random_state=0, n_jobs=-1).fit(Xtr, ytr)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8.4))
    for k, ax in enumerate(axes.ravel()[:5]):
        draw_region(ax, forest.estimators_[k], f"tree {k + 1}: its own bootstrap sample")
        ax.set_xlabel("")
        ax.set_ylabel("")
    ax = axes.ravel()[5]
    ax.clear()
    prob = forest.predict_proba(grid)[:, 1].reshape(gx.shape)
    ax.contourf(gx, gy, prob, levels=np.linspace(0, 1, 11), cmap="RdBu_r", alpha=0.5)
    ax.contour(gx, gy, prob, levels=[0.5], colors=INK, linewidths=2)
    ax.set_title(f"FOREST of 100: the average vote\ntest accuracy {forest.score(Xte, yte):.3f} "
                 f"(one deep tree: {acc[-1][1]:.3f})", fontsize=12.5)
    ax.set_xlim(-1.8, 2.8)
    ax.set_ylim(-1.4, 1.9)
    caption(fig, "Each tree sees a different random sample of rows (and features) and makes its own mistakes; "
                 "averaging cancels them.")
    L.save(fig, "forest_vote")

if L.wanted("forest_growing"):
    ns = [1, 2, 3, 5, 8, 12, 20, 35, 60, 100]
    accs = []
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1.2, 1]})
    models = [RandomForestClassifier(n_estimators=n, max_features=1, random_state=0, n_jobs=-1).fit(Xtr, ytr) for n in ns]
    accs = [m.score(Xte, yte) for m in models]

    def upd(k):
        a1.clear()
        prob = models[k].predict_proba(grid)[:, 1].reshape(gx.shape)
        a1.contourf(gx, gy, prob, levels=np.linspace(0, 1, 11), cmap="RdBu_r", alpha=0.5)
        a1.contour(gx, gy, prob, levels=[0.5], colors=INK, linewidths=2)
        a1.set_title(f"forest of {ns[k]} tree(s)")
        a1.set_xlabel("feature 1")
        a1.set_ylabel("feature 2")
        a2.clear()
        a2.plot(ns[: k + 1], accs[: k + 1], "o-", color=GREEN)
        a2.set_xscale("log")
        a2.set_xlim(0.8, 130)
        a2.set_ylim(min(accs) - 0.01, max(accs) + 0.01)
        a2.set_xlabel("number of trees")
        a2.set_ylabel("test accuracy")
        a2.set_title("more trees: smoother, steadier, better")
    L.animate(fig, upd, len(ns), "forest_growing", fps=1)

# ---------------------------------------------------------------- 5. feature importance (all 20 features)
if L.wanted("importance"):
    Xa_tr, Xa_te, ya_tr, ya_te = train_test_split(X, y, test_size=0.3, random_state=0, stratify=y)
    rf = RandomForestClassifier(n_estimators=300, random_state=0, n_jobs=-1).fit(Xa_tr, ya_tr)
    imp = rf.feature_importances_
    order = np.argsort(imp)
    fig, ax = plt.subplots(figsize=(11, 7))
    ax.barh(range(len(order)), imp[order], color=AQUA)
    ax.set_yticks(range(len(order)), [names[i] for i in order])
    ax.set_xlabel("importance (how much the feature reduced Gini, over all 300 trees)")
    ax.set_title(f"Random forest on all 20 features: test accuracy {rf.score(Xa_te, ya_te):.3f}")
    print(f"  forest accuracy on 20 features: {rf.score(Xa_te, ya_te):.3f}")
    L.save(fig, "importance")

print("  depth: train/test", [(d, round(a, 3), round(b, 3)) for d, (a, b) in zip(depths, acc)])
