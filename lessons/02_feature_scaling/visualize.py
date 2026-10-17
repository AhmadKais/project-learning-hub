"""Lesson 02 - feature scaling: why, z-score vs min-max, and what it does to k-NN and gradient descent."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)

white = np.genfromtxt(data("32_WineGrader", "winequality-white.csv"), delimiter=";", skip_header=1)
cols = ["fixed acidity", "volatile acidity", "citric acid", "residual sugar", "chlorides",
        "free sulfur dioxide", "total sulfur dioxide", "density", "pH", "sulphates", "alcohol", "quality"]
ALC, SO2 = cols.index("alcohol"), cols.index("total sulfur dioxide")
rng = np.random.default_rng(3)
sample = white[rng.choice(len(white), 300, replace=False)]
X = sample[:, [ALC, SO2]]
q = np.array([10.4, 140.0])            # the new wine


def zscore(A, ref):
    return (A - ref.mean(0)) / ref.std(0)


def nearest(A, point, k=7):
    d = np.sqrt(((A - point) ** 2).sum(1))
    return np.argsort(d)[:k]


# ---------------------------------------------------------------- 1. the ranges
if L.wanted("ranges"):
    fig, ax = plt.subplots(figsize=(12, 4.8))
    feats = cols[:-1]
    lo, hi = white[:, :-1].min(0), white[:, :-1].max(0)
    y = np.arange(len(feats))
    ax.barh(y, hi - lo, left=lo, color=BLUE, height=0.55)
    ax.set_yticks(y, feats)
    ax.set_xscale("symlog", linthresh=1)
    ax.set_xlabel("value range in the white-wine data (log scale)")
    ax.set_title("The 11 wine features live on completely different scales")
    for i in (SO2, cols.index("density")):
        ax.text(hi[i] * 1.1, i, f"{lo[i]:g} … {hi[i]:g}", va="center", fontsize=11, color=INK2)
    caption(fig, "A difference of 1 in total sulfur dioxide is nothing; a difference of 1 in density is impossible.")
    L.save(fig, "ranges")

# ---------------------------------------------------------------- 2. neighbours before / after
if L.wanted("neighbours"):
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.6))
    Z, qz = zscore(X, X), (q - X.mean(0)) / X.std(0)
    for ax, A, point, title in [(axes[0], X, q, "RAW numbers"), (axes[1], Z, qz, "after z-score scaling")]:
        nn = nearest(A, point)
        ax.scatter(A[:, 0], A[:, 1], s=18, color=MUTED, alpha=0.5)
        ax.scatter(A[nn, 0], A[nn, 1], s=70, color=ORANGE, edgecolor="white", zorder=3, label="7 nearest")
        ax.scatter(*point, s=260, marker="*", color=BLUE, edgecolor="white", zorder=4, label="new wine")
        r = np.sqrt(((A[nn[-1]] - point) ** 2).sum())
        if A is X:      # in raw units the "circle" is a thin horizontal band
            ax.axhspan(point[1] - r, point[1] + r, color=ORANGE, alpha=0.15)
        else:
            ax.add_patch(plt.Circle(point, r, fill=False, color=ORANGE, lw=1.5, ls="--"))
            ax.set_aspect("equal", adjustable="datalim")
        ax.set_title(title)
        ax.set_xlabel("alcohol" + (" (z)" if A is Z else " (%)"))
        ax.set_ylabel("total SO₂" + (" (z)" if A is Z else " (mg/l)"))
        ax.legend(loc="upper right", fontsize=10)
    caption(fig, "Left: the 'circle' of neighbours is a thin band - alcohol is ignored, only SO₂ counts.  "
                 "Right: both features count.")
    L.save(fig, "neighbours")

# ---------------------------------------------------------------- 3. the two steps, animated
if L.wanted("zscore_steps"):
    fig, ax = plt.subplots(figsize=(8, 6.4))
    mean, std = X.mean(0), X.std(0)
    stages = ([X] * 4 + [X + (0 - mean) * t for t in np.linspace(0, 1, 8)] + [X - mean] * 4
              + [(X - mean) / (1 + (std - 1) * t) for t in np.linspace(0, 1, 10)] + [(X - mean) / std] * 6)
    labels = (["1. the raw data"] * 4 + ["2. subtract the mean → centre at 0"] * 12
              + ["3. divide by the std → spread 1"] * 16)

    def upd(i):
        ax.clear()
        A = stages[i]
        ax.scatter(A[:, 0], A[:, 1], s=16, color=BLUE, alpha=0.7)
        ax.axhline(0, color=INK2, lw=1)
        ax.axvline(0, color=INK2, lw=1)
        span = max(np.abs(A).max(0)) * 1.05
        ax.set_xlim(-span, span)
        ax.set_ylim(-span, span)
        ax.set_aspect("equal")
        ax.set_title(labels[i])
        ax.set_xlabel("alcohol")
        ax.set_ylabel("total SO₂")
    L.animate(fig, upd, len(stages), "zscore_steps", fps=4)

# ---------------------------------------------------------------- 4. z-score vs min-max with an outlier
if L.wanted("outlier"):
    so2 = white[:, SO2]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4), sharey=True)
    mm = (so2 - so2.min()) / (so2.max() - so2.min())
    z = (so2 - so2.mean()) / so2.std()
    axes[0].hist(mm, bins=60, color=BLUE)
    axes[0].set_title("min-max: (x − min) / (max − min)")
    axes[0].set_xlabel("scaled value")
    axes[0].annotate(f"one wine at {so2.max():g}", xy=(1, 2), xytext=(0.6, 300),
                     arrowprops=dict(arrowstyle="->", color=INK2))
    axes[1].hist(z, bins=60, color=AQUA)
    axes[1].set_title("z-score: (x − mean) / std")
    axes[1].set_xlabel("scaled value")
    axes[0].set_ylabel("number of wines")
    caption(fig, f"Total SO₂ of 4,898 white wines.  min-max squeezes 99% of them into "
                 f"[{np.percentile(mm, 0.5):.2f}, {np.percentile(mm, 99.5):.2f}] because of one outlier.")
    L.save(fig, "outlier")

# ---------------------------------------------------------------- 5. gradient descent on stretched vs round bowl
if L.wanted("gradient_descent"):
    def run(a, b, lr, steps=40):
        p = np.array([-9.0, 2.6])
        path = [p.copy()]
        for _ in range(steps):
            p = p - lr * np.array([a * p[0], b * p[1]])
            path.append(p.copy())
        return np.array(path)

    raw = run(0.05, 1.8, 1.0)            # stretched bowl: the safe step for y is far too small for x
    scaled = run(1.0, 1.0, 0.35) * [0.3, 0.3 * 3 / 3.5 * 10 / 3]   # same start, in std units
    gx, gy = np.meshgrid(np.linspace(-10, 10, 200), np.linspace(-3.5, 3.5, 200))
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))

    sx, sy = np.meshgrid(np.linspace(-3.2, 3.2, 200), np.linspace(-3.2, 3.2, 200))

    def upd(i):
        for ax, path, (cx, cy, Zc), lim, title in [
                (axes[0], raw, (gx, gy, 0.05 * gx ** 2 + 1.8 * gy ** 2), (10, 3.5), "features NOT scaled"),
                (axes[1], scaled, (sx, sy, sx ** 2 + sy ** 2), (3.2, 3.2), "features scaled")]:
            ax.clear()
            ax.contour(cx, cy, Zc, levels=14, colors=MUTED, linewidths=1)
            ax.plot(path[: i + 1, 0], path[: i + 1, 1], "o-", color=ORANGE, ms=4)
            ax.plot(0, 0, "*", color=GREEN, ms=16)
            ax.set_title(f"{title} - step {i}")
            ax.set_xlim(-lim[0], lim[0])
            ax.set_ylim(-lim[1], lim[1])
            ax.set_xticks([])
            ax.set_yticks([])
        axes[1].set_aspect("equal")
        axes[0].set_xlabel("zig-zags across the narrow valley, crawls along it")
        axes[1].set_xlabel("walks straight to the minimum ★")
    L.animate(fig, upd, 30, "gradient_descent", fps=5)


# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 6. squeezing SO2 step by step: the neighbours change
if L.wanted("squeeze"):
    factors = [1, 1.5, 2, 3, 4, 6, 8, 11, 15, 20, 26, 33, X[:, 1].std() / X[:, 0].std()]
    fig, ax = plt.subplots(figsize=(10, 6))

    def upd(i):
        f = factors[min(i, len(factors) - 1)]
        A = X / np.array([1, f])
        p = q / np.array([1, f])
        nn = nearest(A, p)
        ax.clear()
        ax.scatter(A[:, 0], A[:, 1], s=18, color=MUTED, alpha=0.5)
        ax.scatter(A[nn, 0], A[nn, 1], s=80, color=ORANGE, edgecolor="white", zorder=3, label="7 nearest wines")
        ax.scatter(*p, s=300, marker="*", color=BLUE, edgecolor="white", zorder=4, label="the customer's wine")
        ax.set_xlabel("alcohol (%)")
        ax.set_ylabel(f"total SO₂ ÷ {f:.1f}")
        spread_alc = A[nn, 0].max() - A[nn, 0].min()
        ax.set_title(f"SO₂ divided by {f:.1f}:  the 7 nearest differ by {spread_alc:.1f} % alcohol")
        ax.legend(loc="upper right")
    frames = list(range(len(factors))) + [len(factors) - 1] * 4
    L.animate(fig, lambda i: upd(frames[i]), len(frames), "squeeze", fps=2)

# ---------------------------------------------------------------- 7. real histograms: raw vs z
if L.wanted("hist_raw_vs_z"):
    fig, axes = plt.subplots(2, 2, figsize=(13, 6.5))
    for j, (k, name, col) in enumerate([(ALC, "alcohol (%)", BLUE), (SO2, "total SO₂ (mg/l)", ORANGE)]):
        v = white[:, k]
        axes[0, j].hist(v, 40, color=col)
        axes[0, j].set_title(f"{name}: average {v.mean():.1f}, std {v.std():.1f}", fontsize=12)
        z = (v - v.mean()) / v.std()
        axes[1, j].hist(z, 40, color=col)
        axes[1, j].set_xlim(-4, 6)
        axes[1, j].set_title(f"after z-score: average 0, std 1", fontsize=12)
        axes[1, j].set_xlabel("z = how many 'typical steps' from the average")
    axes[0, 0].set_ylabel("number of wines")
    axes[1, 0].set_ylabel("number of wines")
    caption(fig, "Real white wines (4,898). The SHAPE never changes - only the ruler under it. After scaling both live on "
                 "the same ruler: −3 … +3.")
    L.save(fig, "hist_raw_vs_z")

# ---------------------------------------------------------------- 8. raw, min-max, z side by side
if L.wanted("three_ways"):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    mm = (X - X.min(0)) / (X.max(0) - X.min(0))
    Z = zscore(X, X)
    for ax, A, title in [(axes[0], X, "raw numbers"), (axes[1], mm, "min-max: (x − min) ÷ (max − min)"),
                         (axes[2], Z, "z-score: (x − average) ÷ std")]:
        ax.scatter(A[:, 0], A[:, 1], s=14, color=BLUE, alpha=0.6)
        ax.set_title(title, fontsize=12)
        ax.set_xlabel("alcohol")
        ax.set_ylabel("total SO₂")
        ax.set_aspect("equal", adjustable="datalim")
    caption(fig, "Same 300 wines. Raw: SO₂ (0-300) dwarfs alcohol (8-14). Min-max: both 0…1. z-score: both centred on 0, "
                 "spread 1.")
    L.save(fig, "three_ways")

# ---------------------------------------------------------------- 9. real world: comparing grades from two different exams
if L.wanted("exam_curving"):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
    r = np.random.default_rng(4)
    for ax, avg, sd, me, who, name, col in [(axes[0], 60, 10, 80, "Rami", "Hard maths exam (Class A)", BLUE),
                                            (axes[1], 85, 5, 90, "Lina", "Easy maths exam (Class B)", ORANGE)]:
        g = np.clip(r.normal(avg, sd, 400), 0, 100)
        ax.hist(g, np.arange(20, 101, 2.5), color=col, alpha=0.7)
        ax.axvline(me, color=INK, lw=3)
        ax.axvline(avg, color=MUTED, ls="--")
        ax.text(me + 1, ax.get_ylim()[1] * 0.85, f"{who}: {me}\nz = ({me} − {avg}) ÷ {sd}\n= {(me - avg) / sd:+.1f}",
                fontsize=12, weight="bold")
        ax.text(avg - 1, ax.get_ylim()[1] * 0.95, f"average {avg}", ha="right", fontsize=11, color=INK2)
        ax.set_title(name)
        ax.set_xlabel("grade")
        ax.set_xlim(20, 100)
    fig.suptitle("Who did better? 80 on the hard exam (2 steps above average) beats 90 on the easy one (1 step).",
                 fontsize=13, weight="bold")
    fig.tight_layout()
    L.save(fig, "exam_curving")

# ---------------------------------------------------------------- live
if L.live:
    from matplotlib.widgets import Slider
    fig, ax = plt.subplots(figsize=(8, 7))
    fig.subplots_adjust(bottom=0.18)
    s = Slider(fig.add_axes([0.2, 0.05, 0.6, 0.04]), "weight of SO₂", 0.0, 3.0, valinit=1.0)
    Z, qz = zscore(X, X), (q - X.mean(0)) / X.std(0)

    def draw(w):
        ax.clear()
        A = Z * [1, w]
        nn = nearest(A, qz * [1, w])
        ax.scatter(Z[:, 0], Z[:, 1], s=16, color=MUTED, alpha=0.5)
        ax.scatter(Z[nn, 0], Z[nn, 1], s=80, color=ORANGE)
        ax.scatter(*qz, s=260, marker="*", color=BLUE)
        ax.set_title("how the neighbours change when SO₂ counts more or less")
        fig.canvas.draw_idle()
    s.on_changed(draw)
    draw(1.0)
    plt.show()
