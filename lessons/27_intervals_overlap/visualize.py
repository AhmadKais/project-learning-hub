"""Lesson 27 - do two stays collide? Half-open intervals, the rule a < d and c < b, all eight cases, De Morgan."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
A, B = 3, 7                                     # our stay [3, 7)


def overlaps(a, b, c, d):
    return a < d and c < b


# ---------------------------------------------------------------- 1. half-open: nights, not days
if L.wanted("half_open"):
    fig, ax = plt.subplots(figsize=(14, 3.6))
    blank(ax, (0.5, 12.5), (-0.6, 2.4))
    for day in range(1, 13):
        ax.text(day, -0.4, f"{day} Mar", ha="center", fontsize=11, color=INK2)
        ax.plot([day, day], [-0.2, 2.2], color=GRID, lw=1)
    for (s, e, row, name, col) in [(2, 9, 1.3, "guest 1: check-in 2, check-out 9  →  7 nights", BLUE),
                                   (9, 12, 0.3, "guest 2: check-in 9", ORANGE)]:
        for n in range(s, e):
            ax.add_patch(plt.Rectangle((n + 0.05, row), 0.9, 0.6, color=col, alpha=0.85))
            ax.text(n + 0.5, row + 0.3, "☾", ha="center", va="center", color="white", fontsize=14)
        ax.text(s, row + 0.75, name, fontsize=12, color=col, weight="bold")
    ax.annotate("9 March: guest 1 leaves in the morning,\nguest 2 arrives in the afternoon - NO conflict",
                (9, 0.95), xytext=(10.2, 1.7), fontsize=11, arrowprops=dict(arrowstyle="->"))
    ax.set_title("A stay [check-in, check-out) is HALF-OPEN: it occupies the NIGHTS from check-in up to, "
                 "not including, check-out", fontsize=12.5)
    L.save(fig, "half_open")

# ---------------------------------------------------------------- 2. all eight cases (Eran's guide)
cases = [("A", 5, 9, "overlaps on the right"), ("B", 1, 5, "overlaps on the left"), ("C", 4, 6, "inside ours"),
         ("D", 1, 9, "contains ours"), ("E", 3, 7, "identical"), ("F", 7, 9, "starts the day we leave"),
         ("G", 1, 3, "ends the day we arrive"), ("H", 9, 11, "far away")]
if L.wanted("eight_cases"):
    fig, ax = plt.subplots(figsize=(14, 7.4))
    blank(ax, (0, 16.5), (-0.6, 9.6))
    for d in range(1, 12):
        ax.plot([d, d], [-0.2, 9.2], color=GRID, lw=1)
        ax.text(d, -0.5, str(d), ha="center", fontsize=11, color=INK2)
    ax.add_patch(plt.Rectangle((A, 8.3), B - A, 0.6, color=INK))
    ax.text(0.2, 8.6, "ours [3,7)", va="center", fontsize=12, weight="bold")
    for i, (name, c, d, what) in enumerate(cases):
        y = 7.2 - i * 0.95
        hit = overlaps(A, B, c, d)
        col = RED if hit else GREEN
        ax.add_patch(plt.Rectangle((c, y), d - c, 0.6, color=col, alpha=0.85))
        ax.text(0.2, y + 0.3, f"{name} [{c},{d})", va="center", fontsize=12)
        c1, c2 = A < d, c < B
        ax.text(11.6, y + 0.3, f"{A}<{d} {'✓' if c1 else '✗'}   {c}<{B} {'✓' if c2 else '✗'}  →  "
                               f"{'COLLIDE' if hit else 'free'}", va="center", fontsize=11.5, color=col,
                weight="bold" if name == "F" else "normal", family="monospace")
        ax.text(c + (d - c) / 2, y + 0.3, what, ha="center", va="center", fontsize=9.5, color="white")
    ax.set_title("collide  ⇔  a < d  and  c < b        (ours = [a, b) = [3, 7),  theirs = [c, d))", fontsize=13.5)
    caption(fig, "Case F is the one careless code gets wrong: with <= instead of <, a guest arriving the day another "
                 "leaves is refused.")
    L.save(fig, "eight_cases")

# ---------------------------------------------------------------- 3. a stay sliding past ours
if L.wanted("overlap_slide"):
    fig, ax = plt.subplots(figsize=(13, 4.6))
    starts = np.arange(-2.0, 10.01, 0.5)

    def upd(k):
        c = starts[k]
        d = c + 3
        blank(ax, (-2.5, 13.5), (-0.8, 3.4))
        for day in range(-2, 14):
            ax.plot([day, day], [-0.2, 2.6], color=GRID, lw=1)
        ax.add_patch(plt.Rectangle((A, 1.6), B - A, 0.6, color=INK))
        ax.text(A + 2, 1.9, "ours [3, 7)", ha="center", va="center", color="white", fontsize=12)
        hit = overlaps(A, B, c, d)
        ax.add_patch(plt.Rectangle((c, 0.6), 3, 0.6, color=RED if hit else GREEN))
        ax.text(c + 1.5, 0.9, f"[{c:g}, {d:g})", ha="center", va="center", color="white", fontsize=12)
        c1, c2 = A < d, c < B
        ax.text(-2.3, 3.0, f"a < d :  3 < {d:g}  {'✓' if c1 else '✗'}        c < b :  {c:g} < 7  {'✓' if c2 else '✗'}"
                           f"        →  {'COLLIDE' if hit else 'FREE'}", fontsize=14, color=RED if hit else GREEN,
                weight="bold", family="monospace")
    L.animate(fig, upd, len(starts), "overlap_slide", fps=3)

# ---------------------------------------------------------------- 4. the proof with De Morgan
if L.wanted("de_morgan"):
    fig, ax = plt.subplots(figsize=(14, 5.6))
    blank(ax)
    lines = [("1. When are two stays FREE of each other?  Only two ways:", INK, "bold"),
             ("      theirs ends before ours starts:   d ≤ a          OR          theirs starts after ours ends:   b ≤ c", BLUE, "normal"),
             ("2. So they COLLIDE exactly when that is NOT true:", INK, "bold"),
             ("      collide  =  NOT ( d ≤ a  OR  b ≤ c )", INK2, "normal"),
             ("3. De Morgan:  NOT (P or Q)  =  (NOT P) and (NOT Q)", INK, "bold"),
             ("      collide  =  NOT (d ≤ a)  AND  NOT (b ≤ c)  =  a < d  AND  c < b", ORANGE, "bold"),
             ("Two comparisons. No special cases, no if-ladder for the eight situations.", GREEN, "normal")]
    for i, (t, col, w) in enumerate(lines):
        ax.text(0.02, 0.9 - i * 0.13, t, fontsize=13.5, color=col, weight=w, family="monospace" if "  " in t[:6] else None)
    L.save(fig, "de_morgan")

# ---------------------------------------------------------------- 5. brute-force check: the rule vs "share a night"
if L.wanted("brute_force"):
    rng = np.random.default_rng(0)
    M = np.zeros((12, 12))
    mism = 0
    pairs = 0
    for a in range(1, 12):
        for b in range(a + 1, 13):
            for c in range(1, 12):
                for d in range(c + 1, 13):
                    pairs += 1
                    share = len(set(range(a, b)) & set(range(c, d))) > 0
                    mism += share != overlaps(a, b, c, d)
    # a picture: for ours = [3, 7), which (c, d) collide?
    for c in range(1, 12):
        for d in range(c + 1, 13):
            M[c - 1, d - 1] = 2 if overlaps(A, B, c, d) else 1
    fig, ax = plt.subplots(figsize=(8, 7))
    ax.imshow(np.ma.masked_equal(M, 0), cmap=plt.matplotlib.colors.ListedColormap([GREEN, RED]), origin="lower",
              extent=(0.5, 12.5, 0.5, 11.5))
    ax.set_xlabel("their check-out  d")
    ax.set_ylabel("their check-in  c")
    ax.set_xticks(range(1, 13))
    ax.set_yticks(range(1, 12))
    ax.grid(False)
    ax.set_title(f"ours = [3, 7):  red = collide, green = free\nchecked against 'share a night' on all {pairs:,} pairs: "
                 f"{mism} mismatches", fontsize=12.5)
    print(f"  {pairs} pairs, {mism} mismatches")
    L.save(fig, "brute_force")
