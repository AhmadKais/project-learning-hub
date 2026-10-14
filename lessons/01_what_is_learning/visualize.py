"""Lesson 01 - what learning is: rules vs. learning, train/validation/test, overfitting."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
rng = np.random.default_rng(7)

# ---------------------------------------------------------------- 1. rules vs learning
if L.wanted("rules_vs_learning"):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    for ax, title, inputs, out, col in [
        (axes[0], "Normal programming", ["rules\n(you write them)", "data"], "answers", BLUE),
        (axes[1], "Machine learning", ["data", "answers\n(labels)"], "rules\n(the model)", ORANGE),
    ]:
        blank(ax)
        ax.set_title(title)
        box(ax, 0.02, 0.58, 0.3, 0.26, inputs[0], color=INK2)
        box(ax, 0.02, 0.14, 0.3, 0.26, inputs[1], color=INK2)
        box(ax, 0.42, 0.33, 0.22, 0.32, "computer", color=col, fill=LIGHT_BLUE if col == BLUE else LIGHT_ORANGE,
            weight="bold")
        box(ax, 0.74, 0.33, 0.25, 0.32, out, color=col, weight="bold")
        arrow(ax, (0.32, 0.71), (0.42, 0.55))
        arrow(ax, (0.32, 0.27), (0.42, 0.43))
        arrow(ax, (0.64, 0.49), (0.74, 0.49))
    caption(fig, "Spam: you cannot write rules for every trick - so you give examples with answers, "
                 "and the computer finds the rules.")
    L.save(fig, "rules_vs_learning")

# ---------------------------------------------------------------- 2. the three splits
if L.wanted("split"):
    fig, ax = plt.subplots(figsize=(13, 3.6))
    blank(ax)
    parts = [(0.0, 0.6, "TRAIN  60%", "the model learns from these\n(the textbook + homework)", BLUE),
             (0.6, 0.2, "VALID. 20%", "choose settings\n(the mock exam)", AQUA),
             (0.8, 0.2, "TEST  20%", "used ONCE, at the end\n(the real exam)", ORANGE)]
    for x, w, name, what, col in parts:
        ax.add_patch(plt.Rectangle((x, 0.45), w - 0.006, 0.3, color=col))
        ax.text(x + w / 2, 0.6, name, ha="center", va="center", color="white", fontsize=14, weight="bold")
        ax.text(x + w / 2, 0.3, what, ha="center", va="top", fontsize=12, color=INK)
    # tiny "rows" so it looks like a table of examples
    for i in range(60):
        ax.plot([i / 60 + 0.004] * 2, [0.76, 0.84], color=SERIES[i % 2], lw=2)
    ax.text(0.5, 0.92, "every row = one example with its correct answer (shuffled, and stratified: "
                       "every part keeps the same % of each class)", ha="center", fontsize=12, color=INK2)
    L.save(fig, "split")

# ---------------------------------------------------------------- 3. overfitting animation
x = np.sort(rng.uniform(0, 1, 18))
y = np.sin(2 * np.pi * x) + rng.normal(0, 0.25, x.size)
xv = np.sort(rng.uniform(0, 1, 40))
yv = np.sin(2 * np.pi * xv) + rng.normal(0, 0.25, xv.size)
grid = np.linspace(0, 1, 400)
degrees = list(range(0, 16))


def fit(deg):
    coef = np.polyfit(x, y, deg)
    tr = np.mean((np.polyval(coef, x) - y) ** 2)
    va = np.mean((np.polyval(coef, xv) - yv) ** 2)
    return coef, tr, va


results = [fit(d) for d in degrees]
train_err = [r[1] for r in results]
val_err = [r[2] for r in results]
best = int(np.argmin(val_err))


def draw_overfit(axl, axr, i):
    coef, tr, va = results[i]
    d = degrees[i]
    axl.clear()
    axl.scatter(x, y, color=BLUE, s=60, zorder=3, label="training points")
    axl.scatter(xv, yv, color=ORANGE, s=30, alpha=0.7, marker="^", zorder=2, label="validation points")
    axl.plot(grid, np.polyval(coef, grid), color=INK, lw=2.5, label=f"model: degree {d}")
    axl.set_ylim(-2, 2)
    axl.set_xlim(0, 1)
    state = "UNDERFIT" if d < 3 else ("good fit" if d <= 6 else "OVERFIT")
    axl.set_title(f"degree {d}:  {state}")
    axl.legend(loc="lower left", fontsize=10)
    axr.clear()
    axr.plot(degrees[: i + 1], train_err[: i + 1], "o-", color=BLUE, label="error on training data")
    axr.plot(degrees[: i + 1], val_err[: i + 1], "^-", color=ORANGE, label="error on NEW data")
    axr.axvline(best, color=MUTED, ls="--", lw=1)
    axr.text(best + 0.2, 0.9, "best", color=INK2)
    axr.set_xlim(-0.5, 15.5)
    axr.set_ylim(0, 1.0)
    axr.set_xlabel("model complexity (polynomial degree)")
    axr.set_ylabel("mean squared error")
    axr.set_title("error: training vs. NEW data")
    axr.legend(loc="upper right", fontsize=10)


if L.wanted("overfitting"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    L.animate(fig, lambda i: draw_overfit(a1, a2, i), len(degrees), "overfitting", fps=2)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    draw_overfit(a1, a2, len(degrees) - 1)
    L.save(fig, "overfitting_final")

# ---------------------------------------------------------------- 4. bias / variance darts
if L.wanted("bias_variance"):
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.2))
    cases = [("low bias, low variance", 0, 0.08, GREEN, "the goal"),
             ("low bias, HIGH variance", 0, 0.35, ORANGE, "overfitting"),
             ("HIGH bias, low variance", 0.55, 0.08, VIOLET, "underfitting"),
             ("HIGH bias, HIGH variance", 0.55, 0.35, RED, "worst")]
    for ax, (title, off, spread, col, tag) in zip(axes, cases):
        blank(ax, (-1.2, 1.2), (-1.2, 1.2))
        ax.set_aspect("equal")
        for r, c in [(1, GRID), (0.66, "#f1f0ec"), (0.33, GRID)]:
            ax.add_patch(plt.Circle((0, 0), r, color=c, ec=MUTED))
        ax.add_patch(plt.Circle((0, 0), 0.08, color=INK))
        pts = rng.normal([off, off * 0.6], spread, (12, 2))
        ax.scatter(pts[:, 0], pts[:, 1], color=col, s=55, edgecolor="white", zorder=3)
        ax.set_title(title, fontsize=12)
        ax.text(0, -1.35, tag, ha="center", fontsize=12, color=INK2)
    caption(fig, "Each dart = the model trained on a different sample of data.  "
                 "Bias = how far the centre is off;  variance = how scattered the darts are.")
    L.save(fig, "bias_variance")

# ---------------------------------------------------------------- live
if L.live:
    from matplotlib.widgets import Slider
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.subplots_adjust(bottom=0.2)
    s = Slider(fig.add_axes([0.2, 0.05, 0.6, 0.04]), "degree", 0, 15, valinit=1, valstep=1)
    s.on_changed(lambda v: (draw_overfit(a1, a2, int(v)), fig.canvas.draw_idle()))
    draw_overfit(a1, a2, 1)
    plt.show()
