"""Lesson 00 - the maths toolkit, in pictures: percentages, averages, spread, probability, sums, powers, roots,
logarithms, e^x, slope, vectors and distance."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
rng = np.random.default_rng(0)

# ---------------------------------------------------------------- 1. a percentage is "out of 100"
if L.wanted("percent"):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, (k, n, title) in zip(axes, [(13, 100, "13 out of 100 = 13 %"), (3, 4, "3 out of 4 = 0.75 = 75 %"),
                                        (1, 8, "1 out of 8 = 0.125 = 12.5 %")]):
        blank(ax, (0, 10), (0, 10))
        ax.set_aspect("equal")
        cols = int(math.ceil(math.sqrt(n)))
        size = 10 / cols
        for i in range(n):
            r, c = divmod(i, cols)
            ax.add_patch(plt.Rectangle((c * size + 0.1, 10 - (r + 1) * size + 0.1), size - 0.2, size - 0.2,
                                       color=ORANGE if i < k else LIGHT_BLUE))
        ax.set_title(title, fontsize=14)
    caption(fig, "A fraction k / n is 'k out of n'.  Divide to get a decimal; × 100 to get a percentage.")
    L.save(fig, "percent")

# ---------------------------------------------------------------- 2. the average (mean) is the balance point
heights = np.array([150, 158, 162, 165, 171, 174, 180])
if L.wanted("mean"):
    fig, ax = plt.subplots(figsize=(13, 3.8))
    ax.scatter(heights, np.zeros_like(heights), s=260, color=BLUE, zorder=3)
    for h in heights:
        ax.text(h, 0.25, str(h), ha="center", fontsize=12)
    m = heights.mean()
    ax.plot([m], [-0.35], marker="^", ms=26, color=ORANGE)
    ax.text(m, -0.75, f"average = (150+158+162+165+171+174+180) / 7 = {heights.sum()} / 7 = {m:.1f}",
            ha="center", fontsize=13, color=ORANGE)
    ax.axhline(0, color=INK, lw=2)
    ax.set_ylim(-1.1, 0.7)
    ax.set_yticks([])
    ax.set_xlabel("height of 7 students (cm)")
    ax.set_title("The average is the point where the ruler balances")
    L.save(fig, "mean")

# ---------------------------------------------------------------- 3. spread: standard deviation
if L.wanted("spread"):
    fig, axes = plt.subplots(2, 1, figsize=(13, 5.6), sharex=True)
    for ax, data, title in [(axes[0], np.array([168, 169, 170, 170, 171, 172]), "class A: everyone close to the average"),
                            (axes[1], np.array([150, 158, 170, 172, 182, 188]), "class B: same average, very spread out")]:
        m, s = data.mean(), data.std()
        ax.scatter(data, np.zeros_like(data), s=200, color=BLUE, zorder=3)
        ax.axvline(m, color=ORANGE, lw=2)
        ax.axvspan(m - s, m + s, color=YELLOW, alpha=0.2)
        ax.set_yticks([])
        ax.set_title(f"{title}:  average {m:.1f},  standard deviation {s:.1f}", fontsize=12.5)
    axes[1].set_xlabel("height (cm)  —  yellow band = average ± one standard deviation")
    L.save(fig, "spread")

# ---------------------------------------------------------------- 4. probability = counting
if L.wanted("probability"):
    fig, ax = plt.subplots(figsize=(12, 4.6))
    blank(ax, (0, 12), (0, 4.6))
    balls = [ORANGE] * 3 + [BLUE] * 7
    rng2 = np.random.default_rng(3)
    for i, c in enumerate(balls):
        ax.add_patch(plt.Circle((1 + (i % 5) * 0.9, 1.3 + (i // 5) * 0.9), 0.38, color=c))
    ax.add_patch(plt.Rectangle((0.3, 0.6), 4.7, 2.3, fill=False, ec=INK2, lw=2))
    ax.text(2.6, 3.3, "a bag with 10 balls", ha="center", fontsize=13)
    ax.text(5.8, 3.0, "P(orange) = orange balls / all balls = 3 / 10 = 0.3", fontsize=14, color=ORANGE)
    ax.text(5.8, 2.2, "P(blue)   = 7 / 10 = 0.7", fontsize=14, color=BLUE)
    ax.text(5.8, 1.4, "together: 0.3 + 0.7 = 1  (something always happens)", fontsize=13)
    ax.text(5.8, 0.6, "a probability is always between 0 (never) and 1 (always)", fontsize=12, color=INK2)
    L.save(fig, "probability")

# ---------------------------------------------------------------- 5. the Σ sign is just "add them all up"
if L.wanted("sigma"):
    fig, ax = plt.subplots(figsize=(13, 3.8))
    blank(ax)
    ax.text(0.03, 0.75, r"$\sum_{i=1}^{4} x_i$", fontsize=40)
    ax.text(0.2, 0.8, "means:", fontsize=16)
    ax.text(0.3, 0.8, "x₁ + x₂ + x₃ + x₄", fontsize=22, family="monospace")
    ax.text(0.2, 0.45, "with  x = 3, 5, 2, 6:", fontsize=16)
    ax.text(0.45, 0.45, "3 + 5 + 2 + 6 = 16", fontsize=22, family="monospace", color=ORANGE)
    ax.text(0.03, 0.12, "Σ is the Greek capital S - 'Sum'.  In Python:  sum(x)  or a for-loop with total += …",
            fontsize=14, color=INK2)
    L.save(fig, "sigma")

# ---------------------------------------------------------------- 6. powers and square roots as squares
if L.wanted("powers"):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    for ax, n in zip(axes, [3, 4, 5]):
        blank(ax, (0, 6), (0, 6))
        ax.set_aspect("equal")
        for i in range(n):
            for j in range(n):
                ax.add_patch(plt.Rectangle((j + 0.5, i + 0.5), 0.92, 0.92, color=AQUA))
        ax.set_title(f"{n}² = {n} × {n} = {n * n}      √{n * n} = {n}", fontsize=14)
    caption(fig, "Squaring = the area of a square with that side.  The square root goes back: which side gives this area?")
    L.save(fig, "powers")

# ---------------------------------------------------------------- 7. the logarithm counts multiplications
if L.wanted("log"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5))
    blank(a1, (0, 10), (0, 7))
    vals = [1, 10, 100, 1000, 10000, 100000]
    for k, v in enumerate(vals):
        a1.add_patch(plt.Rectangle((1, k + 0.4), 3, 0.8, color=LIGHT_BLUE, ec=BLUE))
        a1.text(2.5, k + 0.8, f"{v:,}", ha="center", va="center", fontsize=13)
        a1.text(5, k + 0.8, f"log₁₀ = {k}", va="center", fontsize=13, color=ORANGE)
        if k:
            a1.text(0.5, k + 0.3, "×10", fontsize=10, color=INK2)
    a1.set_title("log₁₀(x) = how many times you multiply 10 to reach x", fontsize=13)
    x = np.linspace(0.05, 40, 400)
    a2.plot(x, np.log(x), color=ORANGE, lw=3)
    a2.axhline(0, color=INK, lw=1)
    for v in (1, 2.718, 10, 20, 40):
        a2.plot(v, np.log(v), "o", color=INK)
        a2.text(v + 0.6, np.log(v) - 0.35, f"ln {v:g} = {np.log(v):.2f}", fontsize=11)
    a2.set_title("ln(x) grows, but SLOWER and SLOWER", fontsize=13)
    a2.set_xlabel("x")
    L.save(fig, "log")

if L.wanted("log_rule"):
    fig, ax = plt.subplots(figsize=(13, 4.4))
    blank(ax)
    ax.text(0.02, 0.85, "The rule that makes logs useful:   log(a × b) = log(a) + log(b)", fontsize=16, weight="bold")
    ax.text(0.02, 0.62, "1,000 × 100 = 100,000          log₁₀:   3  +  2  =  5", fontsize=15, family="monospace")
    ax.text(0.02, 0.42, "0.001 × 0.001 × 0.001 = 0.000000001       log₁₀:   (−3) + (−3) + (−3) = −9", fontsize=15,
            family="monospace")
    ax.text(0.02, 0.18, "Multiplying many tiny numbers → the computer gets 0.0.  Adding their logs → no problem.  "
                        "(Naive Bayes, Lesson 11)", fontsize=13, color=INK2)
    L.save(fig, "log_rule")

# ---------------------------------------------------------------- 8. e^x grows fast; e^(-x) shrinks
if L.wanted("exp"):
    fig, ax = plt.subplots(figsize=(12, 4.6))
    x = np.linspace(-3, 3, 300)
    ax.plot(x, np.exp(x), color=ORANGE, lw=3, label="eˣ  (e ≈ 2.718)")
    ax.plot(x, np.exp(-x), color=BLUE, lw=3, label="e⁻ˣ = 1 / eˣ")
    for v in (-2, 0, 1, 2):
        ax.plot(v, np.exp(v), "o", color=INK)
        ax.text(v + 0.08, np.exp(v) + 0.6, f"e^{v} = {np.exp(v):.2f}", fontsize=11)
    ax.set_ylim(0, 21)
    ax.set_title("eˣ: always positive, grows faster and faster.  ln undoes it:  ln(eˣ) = x")
    ax.legend()
    L.save(fig, "exp")

# ---------------------------------------------------------------- 9. slope = steepness (the idea behind derivatives)
f = lambda x: 0.25 * (x - 3) ** 2 + 1
df = lambda x: 0.5 * (x - 3)
if L.wanted("slope"):
    xs = np.linspace(-1, 7, 300)
    pts = np.r_[np.linspace(-0.5, 6.5, 29)]
    fig, ax = plt.subplots(figsize=(12, 5.4))

    def upd(k):
        x0 = pts[k]
        ax.clear()
        ax.plot(xs, f(xs), color=INK2, lw=2)
        s = df(x0)
        tx = np.linspace(x0 - 1.5, x0 + 1.5, 10)
        ax.plot(tx, f(x0) + s * (tx - x0), color=ORANGE, lw=3)
        ax.plot(x0, f(x0), "o", color=ORANGE, ms=12)
        ax.set_ylim(0, 6.5)
        ax.set_xlim(-1, 7)
        word = "going DOWN → walk right" if s < -0.05 else ("going UP → walk left" if s > 0.05 else "flat: the BOTTOM")
        ax.set_title(f"at x = {x0:.2f} the slope is {s:+.2f}   ({word})")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
    L.animate(fig, upd, len(pts), "slope", fps=4)

# ---------------------------------------------------------------- 10. vectors and distance (Pythagoras)
if L.wanted("distance"):
    fig, ax = plt.subplots(figsize=(8, 7))
    a, b = np.array([1, 1]), np.array([4, 5])
    ax.plot(*a, "o", color=BLUE, ms=14)
    ax.plot(*b, "o", color=ORANGE, ms=14)
    ax.text(a[0] - 0.4, a[1] - 0.4, "A (1, 1)", fontsize=13)
    ax.text(b[0] + 0.15, b[1], "B (4, 5)", fontsize=13)
    ax.plot([1, 4], [1, 1], color=AQUA, lw=3)
    ax.plot([4, 4], [1, 5], color=VIOLET, lw=3)
    ax.plot([1, 4], [1, 5], color=INK, lw=3, ls="--")
    ax.text(2.5, 0.6, "4 − 1 = 3", ha="center", fontsize=13, color=AQUA)
    ax.text(4.2, 3, "5 − 1 = 4", fontsize=13, color=VIOLET)
    ax.text(1.4, 3.6, "distance = √(3² + 4²)\n= √(9 + 16) = √25 = 5", fontsize=13)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.set_title("Distance between two points = Pythagoras")
    L.save(fig, "distance")

# ---------------------------------------------------------------- 11. a table of numbers = a matrix
if L.wanted("table"):
    fig, ax = plt.subplots(figsize=(12, 4.2))
    blank(ax)
    cols = ["alcohol", "acidity", "sugar", "grade"]
    rows = [[12.8, 0.30, 2.0, "high"], [9.4, 0.70, 1.9, "low"], [10.5, 0.35, 6.1, "medium"]]
    for j, c in enumerate(cols):
        ax.text(0.25 + j * 0.18, 0.85, c, ha="center", fontsize=14, weight="bold", color=ORANGE if c == "grade" else INK)
    for i, r in enumerate(rows):
        ax.text(0.05, 0.62 - i * 0.18, f"wine {i + 1}", fontsize=13, color=INK2)
        for j, v in enumerate(r):
            ax.text(0.25 + j * 0.18, 0.62 - i * 0.18, str(v), ha="center", fontsize=14,
                    color=ORANGE if j == 3 else INK)
    ax.text(0.5, 0.02, "row = one example   ·   column = one feature   ·   last column = the answer (the label)",
            ha="center", fontsize=13, color=INK2)
    ax.set_title("Data = a table.  Each row is one thing, each column one measurement.")
    L.save(fig, "table")
