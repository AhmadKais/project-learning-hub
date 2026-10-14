"""Lesson 25 - Viola-Jones face detection: Haar features, the integral image, the cascade, sliding windows, minNeighbors."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from matplotlib.patches import Rectangle

L = Lesson(__file__)
rng = np.random.default_rng(2)


def integral(img):
    """I[y, x] = sum of all pixels above and to the left (inclusive), with a zero row/column in front."""
    I = np.zeros((img.shape[0] + 1, img.shape[1] + 1))
    I[1:, 1:] = img.cumsum(0).cumsum(1)
    return I


def rect_sum(I, y, x, h, w):
    """Any rectangle's sum with 4 reads:  D − B − C + A."""
    return I[y + h, x + w] - I[y, x + w] - I[y + h, x] + I[y, x]


# ---------------------------------------------------------------- 1. Haar features on a face
if L.wanted("haar_features"):
    face = cartoon_face(96, "flat")
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    feats = [("two-rectangle: the eye band is DARKER\nthan the cheeks below", [(30, 22, 14, 52, "black"), (44, 22, 14, 52, "white")]),
             ("three-rectangle: the bridge of the nose is\nBRIGHTER than the eyes on both sides",
              [(30, 26, 14, 14, "black"), (30, 40, 14, 16, "white"), (30, 56, 14, 14, "black")]),
             ("feature value = sum(white) − sum(black)\nbig value = 'looks like this part of a face'", [])]
    for ax, (title, rects) in zip(axes, feats):
        ax.imshow(face, cmap="gray", vmin=0, vmax=255)
        for (y, x, h, w, col) in rects:
            ax.add_patch(Rectangle((x - 0.5, y - 0.5), w, h, color=col, alpha=0.55, ec=ORANGE, lw=2))
        ax.set_title(title, fontsize=11)
        ax.axis("off")
    I = integral(face.astype(float))
    v = rect_sum(I, 44, 22, 14, 52) - rect_sum(I, 30, 22, 14, 52)
    axes[2].text(48, 88, f"on this face: {v:,.0f}", ha="center", fontsize=13, color=ORANGE, weight="bold",
                 bbox=dict(fc=PAPER, ec="none"))
    L.save(fig, "haar_features")

# ---------------------------------------------------------------- 2. the integral image (the guide's 3 × 3)
if L.wanted("integral_image"):
    A = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    II = A.cumsum(0).cumsum(1)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12, 5.4))
    order = [(i, j) for i in range(3) for j in range(3)]

    def draw_grid(ax, M, title, shown=None, hl=None, region=None):
        ax.clear()
        blank(ax, (0, 3), (0, 3))
        ax.set_aspect("equal")
        for i in range(3):
            for j in range(3):
                fc = PAPER
                if region and (i, j) in region:
                    fc = LIGHT_BLUE
                if hl and (i, j) in hl:
                    fc = LIGHT_ORANGE
                ax.add_patch(Rectangle((j, 2 - i), 1, 1, fc=fc, ec=INK2, lw=1.5))
                if shown is None or (i, j) in shown:
                    ax.text(j + 0.5, 2.5 - i, str(M[i, j]), ha="center", va="center", fontsize=20)
        ax.set_title(title, fontsize=13)

    frames = list(range(9)) + [9] * 6

    def upd(f):
        if f < 9:
            i, j = order[f]
            region = [(a, b) for a in range(i + 1) for b in range(j + 1)]
            draw_grid(a1, A, "picture", region=region)
            draw_grid(a2, II, f"integral: cell ({i},{j}) = sum of the blue area = {II[i, j]}", shown=order[: f + 1],
                      hl=[(i, j)])
        else:
            draw_grid(a1, A, "sum of the 2 × 2 rectangle [5 6; 8 9] = 28", region=[(1, 1), (1, 2), (2, 1), (2, 2)])
            draw_grid(a2, II, "4 reads:  45 − 6 − 12 + 1 = 28", hl=[(2, 2), (0, 2), (2, 0), (0, 0)])
    L.animate(fig, upd, len(frames), "integral_image", fps=1)

# ---------------------------------------------------------------- 3. sliding windows + a 3-stage toy cascade
scene = (42 + rng.normal(0, 8, (120, 180))).clip(0, 255)
scene[:, :70] += np.linspace(0, 40, 70)                                   # some background texture
for (y, x) in [(30, 95)]:
    scene[y:y + 48, x:x + 48] = cartoon_face(48, "smile", seed=3)
scene = scene.clip(0, 255)
SI = integral(scene)


def stage_of(y, x, s=48):
    """Return how many stages the window passes (0..3). Thresholds tuned on the drawn face."""
    k = s / 48
    eyes = rect_sum(SI, int(y + 15 * k), int(x + 11 * k), int(7 * k), int(26 * k)) / (7 * 26 * k * k)
    cheek = rect_sum(SI, int(y + 22 * k), int(x + 11 * k), int(7 * k), int(26 * k)) / (7 * 26 * k * k)
    if cheek - eyes < 12:                                                # stage 1: eyes darker than cheeks
        return 0
    bridge = rect_sum(SI, int(y + 15 * k), int(x + 21 * k), int(7 * k), int(6 * k)) / (7 * 6 * k * k)
    if bridge - eyes < 10:                                               # stage 2: nose bridge brighter
        return 1
    inner = rect_sum(SI, int(y + 8 * k), int(x + 12 * k), int(32 * k), int(24 * k)) / (32 * 24 * k * k)
    border = rect_sum(SI, int(y), int(x), int(48 * k), int(4 * k)) / (48 * 4 * k * k)
    if inner - border < 40:                                              # stage 3: face brighter than its side
        return 2
    return 3


windows = [(y, x) for y in range(0, 120 - 48 + 1, 3) for x in range(0, 180 - 48 + 1, 3)]
stages = np.array([stage_of(y, x) for y, x in windows])
if L.wanted("sliding_window"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5.4), gridspec_kw={"width_ratios": [1.5, 1]})
    face_hits = [i for i, st in enumerate(stages) if st >= 1]
    show = sorted(set(list(range(0, len(windows), 30)) + face_hits[::3] + [len(windows) - 1]))
    cols = {0: RED, 1: YELLOW, 2: VIOLET, 3: GREEN}

    def upd(f):
        k = show[min(f, len(show) - 1)]
        a1.clear()
        a1.imshow(scene, cmap="gray", vmin=0, vmax=255)
        for i in range(k + 1):
            if stages[i] == 3:
                y, x = windows[i]
                a1.add_patch(Rectangle((x, y), 48, 48, fill=False, ec=GREEN, lw=1))
        y, x = windows[k]
        a1.add_patch(Rectangle((x, y), 48, 48, fill=False, ec=cols[stages[k]], lw=3))
        a1.axis("off")
        msg = {0: "rejected at stage 1 (2 features)", 1: "rejected at stage 2", 2: "rejected at stage 3",
               3: "passed every stage → FACE candidate"}[stages[k]]
        a1.set_title(f"window {k + 1} of {len(windows)}: {msg}", fontsize=12.5, color=cols[stages[k]])
        a2.clear()
        counts = [(stages[: k + 1] >= s).sum() for s in range(4)]
        a2.barh(range(4)[::-1], counts, color=[MUTED, RED, YELLOW, GREEN])
        a2.set_yticks(range(4)[::-1], ["all", "pass 1", "pass 2", "pass 3"])
        for i, c in enumerate(counts):
            a2.text(c + 2, 3 - i, str(c), va="center", fontsize=12)
        a2.set_xlim(0, len(windows) * 1.15)
        a2.set_title("the cascade throws most windows away early")
    L.animate(fig, upd, len(show) + 4, "sliding_window", fps=6)
    print(f"  windows: {len(windows)}, passed: {[int((stages >= s).sum()) for s in range(4)]}")

# ---------------------------------------------------------------- 4. the cascade arithmetic + minNeighbors
if L.wanted("cascade_numbers"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 4.8))
    st = np.arange(0, 23)
    a1.semilogy(st, 100_000 * 0.5 ** st, "o-", color=RED, label="non-face windows left (start 100,000)")
    a1.semilogy(st, 0.995 ** st, "s-", color=GREEN, label="share of real faces still passing")
    a1.axhline(1, color=MUTED, ls="--", lw=1)
    a1.set_xlabel("stage")
    a1.set_title("22 stages: each keeps 99.5 % of faces, drops 50 % of the rest")
    a1.text(22, 100_000 * 0.5 ** 22 * 3, f"{100_000 * 0.5 ** 22:.3f}", ha="right", color=RED)
    a1.text(22, 0.995 ** 22 * 1.6, f"{0.995 ** 22:.2f}", ha="right", color=GREEN)
    a1.legend(loc="center left", fontsize=10)
    a2.imshow(scene, cmap="gray", vmin=0, vmax=255)
    hits = [w for w, s in zip(windows, stages) if s == 3]
    for (y, x) in hits:
        a2.add_patch(Rectangle((x, y), 48, 48, fill=False, ec=GREEN, lw=0.8))
    fake = (10, 10)
    a2.add_patch(Rectangle((fake[1], fake[0]), 48, 48, fill=False, ec=RED, lw=2, ls="--"))
    a2.text(fake[1] + 24, fake[0] + 60, "a lonely false hit:\n1 window → dropped", ha="center", color=RED, fontsize=11)
    a2.set_title(f"the real face fires {len(hits)} overlapping windows;\nminNeighbors = 5 keeps groups of ≥ 5", fontsize=12)
    a2.axis("off")
    L.save(fig, "cascade_numbers")
