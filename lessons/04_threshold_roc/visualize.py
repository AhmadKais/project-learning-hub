"""Lesson 04 - thresholds, ROC / AUC, precision-recall curve and the two threshold rules."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

L = Lesson(__file__)
rng = np.random.default_rng(0)

# ---- real probabilities: a char-n-gram model on the PhishGuard URLs ------------------
with open(data("25_PhishGuard", "phishing_urls.csv"), encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
urls = [r["URL"] for r in rows]
y = np.array([r["Label"] == "bad" for r in rows], dtype=int)
tr_x, va_x, tr_y, va_y = train_test_split(urls, y, test_size=0.3, stratify=y, random_state=0)
vec = TfidfVectorizer(analyzer="char", ngram_range=(3, 4), min_df=3, max_features=20000)
clf = LogisticRegression(C=0.3, max_iter=2000).fit(vec.fit_transform(tr_x), tr_y)
p = clf.predict_proba(vec.transform(va_x))[:, 1]
pos, neg = p[va_y == 1], p[va_y == 0]


def rates(t):
    tpr = (pos >= t).mean()
    fpr = (neg >= t).mean()
    tp, fp = (pos >= t).sum(), (neg >= t).sum()
    prec = tp / (tp + fp) if tp + fp else 1.0
    return fpr, tpr, prec


ts = np.r_[1.01, np.sort(np.unique(np.round(p, 3)))[::-1], -0.01]
curve = np.array([rates(t) for t in ts])
auc = np.trapezoid(curve[:, 1], curve[:, 0])

# ---------------------------------------------------------------- 1. ROC being drawn
show = np.linspace(1.0, 0.0, 41)


def draw_roc(a1, a2, i):
    t = show[i]
    a1.clear()
    bins = np.linspace(0, 1, 41)
    a1.hist(neg, bins=bins, color=BLUE, alpha=0.85, label="legitimate URLs")
    a1.hist(pos, bins=bins, color=ORANGE, alpha=0.85, label="phishing URLs")
    a1.axvline(t, color=INK, lw=3)
    a1.axvspan(t, 1, color=YELLOW, alpha=0.12)
    a1.set_yscale("log")
    a1.set_xlabel("the model's phishing probability")
    a1.set_title(f"threshold = {t:.2f}")
    a1.legend(loc="upper center")
    a2.clear()
    pts = np.array([rates(s) for s in show[: i + 1]])
    a2.plot([0, 1], [0, 1], ls="--", color=MUTED, lw=1.2)
    a2.text(0.6, 0.52, "coin flip", color=MUTED, rotation=38)
    a2.plot(pts[:, 0], pts[:, 1], color=ORANGE, lw=2.5)
    a2.plot(*pts[-1, :2], "o", color=INK, ms=10)
    fpr, tpr, _ = pts[-1]
    a2.text(fpr + 0.03, tpr - 0.07, f"FPR {fpr:.3f}\nTPR {tpr:.3f}", fontsize=11)
    if i == len(show) - 1:
        a2.fill_between(curve[:, 0], curve[:, 1], color=ORANGE, alpha=0.15)
        a2.text(0.45, 0.25, f"AUC = {auc:.3f}", fontsize=16, weight="bold")
    a2.set_xlim(-0.01, 1)
    a2.set_ylim(0, 1.02)
    a2.set_aspect("equal")
    a2.set_xlabel("false-alarm rate  FP / all legitimate")
    a2.set_ylabel("recall  TP / all phishing")
    a2.set_title("each threshold = one point of the ROC curve")


if L.wanted("roc_build"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.6))
    frames = list(range(len(show))) + [len(show) - 1] * 8
    L.animate(fig, lambda k: draw_roc(a1, a2, frames[k]), len(frames), "roc_build", fps=5)

# ---------------------------------------------------------------- 2. shapes of ROC curves
if L.wanted("roc_shapes"):
    fig, axes = plt.subplots(1, 4, figsize=(16, 4.4))
    for ax, sep, title in zip(axes, [6, 2.0, 0.8, 0], ["near perfect", "good", "weak", "useless"]):
        a = rng.normal(0, 1, 4000)
        b = rng.normal(sep, 1, 4000)
        th = np.linspace(-5, 11, 300)
        fpr = [(a >= t).mean() for t in th]
        tpr = [(b >= t).mean() for t in th]
        ar = -np.trapezoid(tpr, fpr)
        ax.plot([0, 1], [0, 1], ls="--", color=MUTED, lw=1)
        ax.plot(fpr, tpr, color=ORANGE)
        ax.fill_between(fpr, tpr, color=ORANGE, alpha=0.15)
        ax.set_aspect("equal")
        ax.set_title(f"{title}: AUC {ar:.2f}", fontsize=13)
        ax.set_xlabel("FPR")
        ins = ax.inset_axes([0.5, 0.08, 0.45, 0.3])
        ins.hist(a, 40, color=BLUE, alpha=0.8)
        ins.hist(b, 40, color=ORANGE, alpha=0.8)
        ins.set_xticks([]); ins.set_yticks([]); ins.grid(False)
    axes[0].set_ylabel("TPR (recall)")
    caption(fig, "The small histograms are the two classes' scores.  The more they overlap, the closer the curve "
                 "is to the diagonal.")
    L.save(fig, "roc_shapes")

# ---------------------------------------------------------------- 3. what AUC means: pairs
if L.wanted("auc_pairs"):
    fig, ax = plt.subplots(figsize=(13, 4.8))
    k = 40
    pp, nn = rng.choice(pos, k), rng.choice(neg, k)
    good = pp > nn
    for i in range(k):
        ax.plot([i, i], [nn[i], pp[i]], color=GREEN if good[i] else RED, lw=2, alpha=0.8)
    ax.scatter(range(k), pp, color=ORANGE, s=50, zorder=3, label="a random phishing URL")
    ax.scatter(range(k), nn, color=BLUE, s=50, zorder=3, label="a random legitimate URL")
    ax.set_xlabel("40 random pairs")
    ax.set_ylabel("score")
    ax.set_title(f"AUC = the chance that a random phishing URL scores higher than a random legitimate one   "
                 f"(here {good.sum()}/{k} pairs; on all pairs {auc:.3f})", fontsize=12)
    ax.legend(loc="center right", fontsize=10)
    L.save(fig, "auc_pairs")

# ---------------------------------------------------------------- 4. the two threshold rules
if L.wanted("rules"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.2))
    grid = np.round(np.arange(0.05, 0.951, 0.01), 2)
    R = np.array([rates(t) for t in grid])
    prec, rec = R[:, 2], R[:, 1]
    # rule A (Spam): highest recall subject to precision >= floor
    floor = 0.98
    okA = prec >= floor
    iA = np.argmax(np.where(okA, rec, -1))
    a1.plot(rec, prec, color=ORANGE)
    a1.axhspan(floor, 1.0, color=GREEN, alpha=0.1)
    a1.axhline(floor, color=GREEN, ls="--")
    a1.text(0.02, floor + 0.003, f"allowed: precision ≥ {floor}", color=GREEN, fontsize=11)
    a1.plot(rec[iA], prec[iA], "o", color=INK, ms=11)
    a1.annotate(f"chosen: t = {grid[iA]:.2f}\nrecall {rec[iA]:.3f}", (rec[iA], prec[iA]),
                xytext=(0.3, 0.86), arrowprops=dict(arrowstyle="->"))
    a1.set_xlabel("recall")
    a1.set_ylabel("precision")
    a1.set_ylim(0.8, 1.005)
    a1.set_xlim(0, 1)
    a1.set_title("SPAM rule: precision ≥ 0.98, then best recall")
    # rule B (Phish): highest threshold with recall >= 0.95
    target = 0.95
    okB = rec >= target
    iB = np.max(np.where(okB)[0])
    a2.plot(grid, rec, color=AQUA, label="recall")
    a2.plot(grid, prec, color=ORANGE, label="precision")
    a2.axhline(target, color=GREEN, ls="--")
    a2.axvspan(0, grid[iB], color=GREEN, alpha=0.08)
    a2.plot(grid[iB], rec[iB], "o", color=INK, ms=11)
    a2.annotate(f"chosen: t = {grid[iB]:.2f}\n(highest t with recall ≥ {target})", (grid[iB], rec[iB]),
                xytext=(grid[iB] + 0.1, 0.83), arrowprops=dict(arrowstyle="->"))
    a2.set_xlabel("threshold")
    a2.set_ylim(0.75, 1.005)
    a2.set_title("PHISH rule: recall ≥ 0.95, then highest threshold")
    a2.legend(loc="lower left")
    caption(fig, "Same model, same validation data (real PhishGuard URLs).  "
                 "The rule comes from which mistake is more expensive in YOUR problem.")
    L.save(fig, "rules")

# ---------------------------------------------------------------- 5. cost decides the threshold
if L.wanted("cost"):
    fig, ax = plt.subplots(figsize=(12, 4.8))
    grid = np.linspace(0.01, 0.99, 99)
    for ratio, col in [(1, MUTED), (5, AQUA), (20, ORANGE)]:
        cost = [((neg >= t).sum() * 1 + (pos < t).sum() * ratio) for t in grid]
        cost = np.array(cost) / max(cost)
        ax.plot(grid, cost, color=col, label=f"a missed phish costs {ratio}× a false alarm")
        j = np.argmin(cost)
        ax.plot(grid[j], cost[j], "o", color=col, ms=10)
    ax.set_xlabel("threshold")
    ax.set_ylabel("total cost (scaled)")
    ax.set_title("The more a missed phish costs, the LOWER the best threshold")
    ax.legend()
    L.save(fig, "cost")

if L.live:
    from matplotlib.widgets import Slider
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.subplots_adjust(bottom=0.2)
    s = Slider(fig.add_axes([0.2, 0.05, 0.6, 0.04]), "step", 0, len(show) - 1, valinit=20, valstep=1)
    s.on_changed(lambda v: (draw_roc(a1, a2, int(v)), fig.canvas.draw_idle()))
    draw_roc(a1, a2, 20)
    plt.show()
