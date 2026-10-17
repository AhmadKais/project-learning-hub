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

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 12. percent of a number: the 10 x 10 grid filling up
if L.wanted("percent_grid"):
    fig, ax = plt.subplots(figsize=(6.5, 7))

    def upd(k):
        blank(ax, (0, 10), (-1.6, 10))
        ax.set_aspect("equal")
        for i in range(100):
            r, c = divmod(i, 10)
            col = ORANGE if i < k else GRID
            ax.add_patch(plt.Rectangle((c + 0.06, 9 - r + 0.06), 0.88, 0.88, color=col))
        ax.text(5, -0.6, f"{k} squares out of 100  =  {k / 100:.2f}  =  {k} %", ha="center", fontsize=17, weight="bold")
        ax.set_title("'per cent' = 'out of every 100'")
    steps = list(range(0, 14)) + [13] * 6 + list(range(13, 76, 3)) + [75] * 6
    L.animate(fig, lambda i: upd(steps[i]), len(steps), "percent_grid", fps=6)

# ---------------------------------------------------------------- 13. the average as a balance point (seesaw), animated
heights = [150, 158, 162, 165, 171, 174, 180]
if L.wanted("mean_balance"):
    fig, ax = plt.subplots(figsize=(12, 4.6))

    def upd(k):
        ax.clear()
        hs = heights[: k + 1]
        m = np.mean(hs)
        ax.plot([145, 185], [0, 0], color=INK2, lw=6, solid_capstyle="round")
        ax.add_patch(plt.Polygon([[m - 1.3, -0.9], [m + 1.3, -0.9], [m, 0]], color=ORANGE))
        for h in hs:
            ax.add_patch(plt.Circle((h, 0.55), 0.5, color=BLUE))
            ax.text(h, 1.35, str(h), ha="center", fontsize=11)
        ax.text(m, -1.5, f"balance point = average = {sum(hs)} ÷ {len(hs)} = {m:.1f} cm", ha="center", fontsize=14,
                color=ORANGE, weight="bold")
        ax.set_xlim(145, 185)
        ax.set_ylim(-2, 2)
        ax.set_aspect("equal")
        ax.set_yticks([])
        ax.set_xlabel("height (cm)")
        ax.set_title(f"{len(hs)} student(s) on the ruler - where does it balance?")
    frames = [k for k in range(len(heights)) for _ in range(3)] + [len(heights) - 1] * 4
    L.animate(fig, lambda i: upd(frames[i]), len(frames), "mean_balance", fps=3)

# ---------------------------------------------------------------- 14. mean vs median: one billionaire walks in
if L.wanted("mean_median"):
    salaries = [6, 7, 7, 8, 9, 10, 11]
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.8), sharey=True)
    for ax, sal, title in [(axes[0], salaries, "7 workers at a café"),
                           (axes[1], salaries + [500], "...the owner (500k) walks in")]:
        ax.bar(range(len(sal)), [min(s, 75) for s in sal], color=[BLUE] * 7 + [ORANGE] * (len(sal) - 7))
        if len(sal) > 7:
            ax.text(7, 76.5, "500 ↑", ha="center", fontsize=12, color=ORANGE, weight="bold")
        m, md = np.mean(sal), np.median(sal)
        ax.axhline(m, color=RED, ls="--")
        ax.axhline(md, color=GREEN, ls=":")
        ax.text(-0.4, max(m, md) + 2.5, f"average = {m:.1f}k", color=RED, fontsize=12)
        ax.text(-0.4, max(m, md) + 7.5, f"median = {md:.1f}k", color=GREEN, fontsize=12)
        ax.set_ylim(0, 82)
        ax.set_xticks([])
        ax.set_title(title)
        ax.set_ylabel("monthly salary (thousand ₪)")
    caption(fig, "One huge value pulls the average far away; the median (the middle person) hardly moves.")
    L.save(fig, "mean_median")

# ---------------------------------------------------------------- 15. standard deviation drawn as real squares
if L.wanted("std_squares"):
    vals = [2, 4, 4, 6]
    fig, ax = plt.subplots(figsize=(12, 5.2))
    m = np.mean(vals)
    ax.axvline(m, color=ORANGE, lw=2)
    ax.text(m, 4.6, "average = 4", ha="center", color=ORANGE, fontsize=13, weight="bold")
    ys = [0.3, 2.6, 2.6, 0.3]
    for v, yb, col in zip(vals, ys, [BLUE, AQUA, AQUA, VIOLET]):
        d = v - m
        ax.plot(v, yb, "o", color=col, ms=12, zorder=4)
        if d:
            x0 = min(v, m)
            ax.add_patch(plt.Rectangle((x0, yb), abs(d), abs(d), color=col, alpha=0.3))
            ax.text(x0 + abs(d) / 2, yb + abs(d) / 2, f"distance {d:+.0f}\nsquare = {d * d:.0f}", ha="center",
                    va="center", fontsize=12)
        else:
            ax.text(v + 0.15, yb + 0.15, "distance 0 → square 0", fontsize=11)
    ax.add_patch(plt.Rectangle((7.3, 0.3), np.sqrt(2), np.sqrt(2), color=GREEN, alpha=0.35))
    ax.text(7.3 + np.sqrt(2) / 2, 0.3 + np.sqrt(2) + 0.25, "the AVERAGE square:\n(4+0+0+4) ÷ 4 = 2\nside = √2 = 1.41 = std",
            ha="center", fontsize=12, color=GREEN, weight="bold")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.set_aspect("equal")
    ax.set_yticks([])
    ax.set_xlabel("value")
    ax.set_title("Standard deviation, literally: draw each distance as a square, average the squares, take the side")
    L.save(fig, "std_squares")

# ---------------------------------------------------------------- 16. two cities, same average temperature
if L.wanted("two_cities"):
    days = np.arange(1, 31)
    r = np.random.default_rng(5)
    a = 22 + r.normal(0, 1.2, 30)
    b = 22 + 9 * np.sin(days / 30 * 2 * np.pi * 2) + r.normal(0, 2.5, 30)
    a += 22 - a.mean()
    b += 22 - b.mean()
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.plot(days, a, "o-", color=BLUE, label=f"Haifa-by-the-sea: average {a.mean():.0f}°, std {a.std():.1f}°")
    ax.plot(days, b, "s-", color=ORANGE, label=f"Desert town: average {b.mean():.0f}°, std {b.std():.1f}°")
    ax.axhline(22, color=MUTED, ls="--")
    ax.set_xlabel("day of the month")
    ax.set_ylabel("temperature at noon (°C)")
    ax.set_title("Same average, very different life: the std tells you whether to pack a coat")
    ax.legend(loc="upper right")
    L.save(fig, "two_cities")

# ---------------------------------------------------------------- 17. probability as a long experiment (law of large numbers)
if L.wanted("sweets_experiment"):
    r = np.random.default_rng(2)
    draws = r.random(400) < 0.3
    running = np.cumsum(draws) / np.arange(1, 401)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8), gridspec_kw={"width_ratios": [1, 2]})
    marks = list(range(1, 21)) + list(range(22, 60, 3)) + list(range(60, 401, 20)) + [400] * 4

    def upd(k):
        n = marks[k]
        blank(a1, (0, 10), (0, 10))
        a1.set_aspect("equal")
        for i in range(min(n, 100)):
            rr, cc = divmod(i, 10)
            a1.add_patch(plt.Circle((cc + 0.5, 9.5 - rr), 0.4, color=ORANGE if draws[i] else BLUE))
        a1.set_title(f"draws so far: {n}" + ("  (first 100 shown)" if n > 100 else ""))
        a2.clear()
        a2.plot(np.arange(1, n + 1), running[:n], color=ORANGE, lw=2.5)
        a2.axhline(0.3, color=INK, ls="--")
        a2.text(400, 0.315, "the true chance: 3 ÷ 10 = 0.3", ha="right", fontsize=12)
        a2.set_xlim(0, 400)
        a2.set_ylim(0, 1)
        a2.set_xlabel("number of draws (put the sweet back each time)")
        a2.set_ylabel("share of orange so far")
        a2.set_title(f"orange so far: {draws[:n].sum()} / {n} = {running[n - 1]:.2f}")
    L.animate(fig, upd, len(marks), "sweets_experiment", fps=4)

# ---------------------------------------------------------------- 18. "given that" = first keep only part of the crowd
if L.wanted("given_that"):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.2))
    people = [("teacher", "card")] * 6 + [("teacher", "cash")] * 2 + [("student", "card")] * 7 + [("student", "cash")] * 25
    for ax, keep, title in [(axes[0], None, "everyone: P(card) = 13 ÷ 40 = 0.33"),
                            (axes[1], "teacher", "keep ONLY teachers: P(card | teacher) = 6 ÷ 8 = 0.75")]:
        blank(ax, (0, 10), (0.7, 4.95))
        ax.set_aspect("equal")
        for i, (who, pay) in enumerate(people):
            rr, cc = divmod(i, 10)
            faded = keep is not None and who != keep
            col = (ORANGE if pay == "card" else BLUE)
            ax.add_patch(plt.Circle((cc + 0.5, 4.4 - rr * 1.05), 0.38, color=col, alpha=0.12 if faded else 1))
            ax.text(cc + 0.5, 4.4 - rr * 1.05, "T" if who == "teacher" else "S", ha="center", va="center",
                    color="white" if not faded else MUTED, fontsize=11, weight="bold")
        ax.set_title(title, fontsize=13)
    caption(fig, "orange = paid by card, blue = cash, T = teacher, S = student.  The bar | means: first keep only the "
                 "people after it, then count.")
    L.save(fig, "given_that")

# ---------------------------------------------------------------- 19. normal ruler vs log ruler
if L.wanted("log_ruler"):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 4.6))
    things = [(1, "1 ₪\ncoffee tip"), (10, "10 ₪\nfalafel"), (100, "100 ₪\nshoes"), (1000, "1,000 ₪\nphone"),
              (10000, "10,000 ₪\nused car"), (100000, "100,000 ₪\nnew car"), (1000000, "1,000,000 ₪\nflat")]
    for ax, logscale in [(a1, False), (a2, True)]:
        ax.set_ylim(-1, 1)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.grid(False)
        for v, lab in things:
            xv = math.log10(v) if logscale else v
            ax.plot(xv, 0, "o", color=ORANGE, ms=10)
            if logscale or v >= 100000:
                ax.text(xv, 0.25, lab, ha="center", fontsize=9.5)
        if not logscale:
            ax.annotate("1 ₪, 10 ₪, 100 ₪, 1,000 ₪ and\n10,000 ₪ are ALL in here", (0, 0), xytext=(160000, 0.45),
                        fontsize=10, arrowprops=dict(arrowstyle="->", color=INK))
        if logscale:
            ax.set_xlim(-0.4, 6.4)
            ax.set_xticks(range(7))
            ax.set_xticklabels([f"log = {i}" for i in range(7)])
            ax.set_title("LOG ruler: every step = ×10 → everything fits and is easy to compare", fontsize=13)
        else:
            ax.set_xlim(-30000, 1030000)
            ax.set_xticks([0, 250000, 500000, 750000, 1000000])
            ax.set_xticklabels(["0", "250,000", "500,000", "750,000", "1,000,000"])
            ax.set_title("NORMAL ruler: six of the seven prices are squashed into the left corner", fontsize=13)
    fig.tight_layout()
    L.save(fig, "log_ruler")

# ---------------------------------------------------------------- 20. the rumour: doubling, and the log answers "how many days?"
if L.wanted("doubling"):
    fig, ax = plt.subplots(figsize=(12, 5))
    d = np.arange(0, 12)
    ax.bar(d, 2.0 ** d, color=[ORANGE if 2 ** k >= 1000 else BLUE for k in d])
    for k in d:
        ax.text(k, 2 ** k + 30, f"{2 ** k:,}", ha="center", fontsize=10)
    ax.axhline(1000, color=INK, ls="--")
    ax.text(0, 1050, "1,000 people", fontsize=12)
    ax.set_xlabel("day")
    ax.set_ylabel("people who heard the rumour")
    ax.set_title("Doubling every day: day 10 passes 1,000 → log₂(1000) ≈ 9.97")
    L.save(fig, "doubling")

# ---------------------------------------------------------------- 21. slope of a road, in numbers
if L.wanted("road_slope"):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
    for ax, s, name in [(axes[0], -0.4, "downhill: slope −0.4"), (axes[1], 0.0, "flat: slope 0"),
                        (axes[2], 0.25, "uphill: slope +0.25")]:
        ax.plot([0, 10], [5, 5 + 10 * s], color=INK2, lw=5)
        ax.annotate("", (8, 5 + 8 * s), (4, 5 + 4 * s), arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=3))
        ax.plot([4, 8, 8], [5 + 4 * s, 5 + 4 * s, 5 + 8 * s], color=AQUA, lw=2, ls="--")
        ax.text(6, 9.0, f"4 steps right, {4 * s:+.1f} up", ha="center", color=AQUA, fontsize=11)
        ax.set_title(f"{name}\n= {4 * s:+.1f} up ÷ 4 right", fontsize=12)
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_aspect("equal")
    caption(fig, "slope = how much you go UP for every 1 step RIGHT.  A road sign '10%' means slope 0.10.")
    L.save(fig, "road_slope")

# ---------------------------------------------------------------- 22. vectors: a list of numbers drawn as an arrow
if L.wanted("vector_arrows"):
    fig, ax = plt.subplots(figsize=(8, 7))
    for v, col, lab in [((3, 1), BLUE, "wine A = (3, 1)"), ((1, 3), ORANGE, "wine B = (1, 3)"),
                        ((2.6, 1.4), AQUA, "wine C = (2.6, 1.4)")]:
        ax.annotate("", v, (0, 0), arrowprops=dict(arrowstyle="-|>", color=col, lw=3, mutation_scale=22))
        ax.text(v[0] + 0.08, v[1] + 0.1, lab, color=col, fontsize=13, weight="bold")
    ax.plot([3, 2.6], [1, 1.4], color=INK, ls=":", lw=2)
    ax.text(2.9, 1.25, "close!", fontsize=11)
    ax.set_xlim(0, 4.2)
    ax.set_ylim(0, 4.2)
    ax.set_aspect("equal")
    ax.set_xlabel("feature 1: alcohol (scaled)")
    ax.set_ylabel("feature 2: sugar (scaled)")
    ax.set_title("A list of numbers = a point = an arrow (a 'vector')")
    L.save(fig, "vector_arrows")
