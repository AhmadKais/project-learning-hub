"""Lesson 23 - EmotionNet: the residual block, vanishing gradients, BatchNorm, Dropout, train() vs eval()."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
rng = np.random.default_rng(0)

# ---------------------------------------------------------------- 1. the architecture with its shapes
if L.wanted("architecture"):
    layers = [("input", 1, 48, "1×48×48", 0), ("stem\nconv+BN+ReLU", 64, 48, "64×48×48", 704),
              ("block 1", 64, 48, "64×48×48", 73_984), ("block 2\nstride 2", 128, 24, "128×24×24", 230_144),
              ("block 3\nstride 2", 256, 12, "256×12×12", 919_040), ("block 4\nstride 2", 512, 6, "512×6×6", 3_673_088),
              ("global\navg pool", 512, 1, "512", 0), ("dropout 0.3\n+ linear", 7, 1, "7 logits", 3_591)]
    fig, ax = plt.subplots(figsize=(16, 6))
    blank(ax, (0, 16.5), (-3.2, 4.2))
    x = 0.2
    for name, ch, size, shape, params in layers:
        h = 0.6 + 2.8 * size / 48
        d = 0.15 + 1.6 * np.log2(ch + 1) / 9
        ax.add_patch(plt.Polygon([[x, 0], [x + d, 0], [x + d + 0.35, 0.35], [x + d + 0.35, h + 0.35], [x + 0.35, h + 0.35],
                                  [x, h]], color=LIGHT_ORANGE if "block" in name else LIGHT_BLUE,
                                 ec=ORANGE if "block" in name else BLUE, lw=1.5))
        ax.text(x + d / 2 + 0.15, -0.45, name, ha="center", va="top", fontsize=11, weight="bold")
        ax.text(x + d / 2 + 0.15, -1.55, shape, ha="center", va="top", fontsize=10.5, color=INK2)
        ax.text(x + d / 2 + 0.15, -2.15, f"{params:,} w" if params else "", ha="center", va="top", fontsize=10.5,
                color=VIOLET)
        x += d + 0.75
    ax.text(8, 3.95, "EmotionNet (Mini-ResNet): the picture gets SMALLER and DEEPER - from pixels to 512 face features",
            ha="center", fontsize=13.5, weight="bold")
    ax.text(8, -2.95, "total ≈ 4,900,551 weights  (box height = picture size, box depth = number of channels)",
            ha="center", fontsize=12, color=INK2)
    L.save(fig, "architecture")

# ---------------------------------------------------------------- 2. the residual block
if L.wanted("residual_block"):
    fig, axes = plt.subplots(1, 2, figsize=(15, 6.2))
    for ax, proj in zip(axes, [False, True]):
        blank(ax)
        steps = ["x", "conv 3×3" + (", stride 2" if proj else ""), "BatchNorm", "ReLU", "conv 3×3", "BatchNorm", "+", "ReLU",
                 "out"]
        ys = np.linspace(0.92, 0.06, len(steps))
        for s, y in zip(steps, ys):
            if s == "+":
                ax.add_patch(plt.Circle((0.35, y), 0.035, color=LIGHT_ORANGE, ec=ORANGE, lw=2))
                ax.text(0.35, y, "+", ha="center", va="center", fontsize=18, weight="bold")
            else:
                box(ax, 0.22, y - 0.035, 0.26, 0.07, s, color=BLUE if s not in ("x", "out") else INK2, fontsize=11.5)
        for a, b in zip(ys[:-1], ys[1:]):
            arrow(ax, (0.35, a - 0.037), (0.35, b + 0.037))
        sc = "1×1 conv, stride 2\n+ BatchNorm\n(match the shape)" if proj else "identity\n(just copy x)"
        ax.annotate("", (0.39, ys[6]), (0.48, ys[0]), arrowprops=dict(arrowstyle="-|>", lw=3, color=ORANGE,
                                                                      connectionstyle="arc3,rad=-0.55"))
        ax.text(0.72, 0.5, f"SHORTCUT\n{sc}", ha="center", va="center", fontsize=12.5, color=ORANGE, weight="bold")
        ax.set_title("block 1: 64 → 64" if not proj else "blocks 2–4: channels ×2, picture ÷2", fontsize=13)
    caption(fig, "out = ReLU( F(x) + x ).  The layers only have to learn the CORRECTION to x; if nothing is needed, "
                 "F(x) = 0 and x passes through.")
    L.save(fig, "residual_block")

# ---------------------------------------------------------------- 3. vanishing gradients: plain vs residual
if L.wanted("gradient_flow"):
    depth, width = 40, 64
    Ws = [rng.normal(0, 1 / np.sqrt(width), (width, width)) * 0.8 for _ in range(depth)]

    def grad_norms(residual):
        x = rng.normal(size=width)
        hs, masks = [x], []
        for Wm in Ws:
            z = Wm @ hs[-1]
            m = (z > 0).astype(float)
            h = (0.2 * np.maximum(0, z) + hs[-1]) if residual else np.maximum(0, z)   # BN keeps the branch small
            masks.append(m)
            hs.append(h)
        g = np.ones(width)
        norms = []
        for Wm, m in zip(reversed(Ws), reversed(masks)):
            g_new = Wm.T @ (g * m)
            g = (0.2 * g_new + g) if residual else g_new
            norms.append(np.linalg.norm(g))
        return norms[::-1]

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.semilogy(range(1, depth + 1), grad_norms(False), "o-", color=RED, ms=4, label="plain network (no shortcuts)")
    ax.semilogy(range(1, depth + 1), grad_norms(True), "o-", color=GREEN, ms=4, label="with residual shortcuts")
    ax.set_xlabel("layer (1 = first, near the input)")
    ax.set_ylabel("size of the gradient that arrives")
    ax.set_title("Vanishing gradient: in a deep plain network the first layers get (almost) nothing to learn from")
    ax.legend()
    L.save(fig, "gradient_flow")

# ---------------------------------------------------------------- 4. BatchNorm in three steps
if L.wanted("batchnorm"):
    batch = rng.normal(3.0, 2.5, 128)
    xh = (batch - batch.mean()) / np.sqrt(batch.var() + 1e-5)
    gamma, beta = 1.5, 0.5
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.2), sharey=True)
    for ax, v, title, col in [(axes[0], batch, f"one channel over a batch of 128\nmean {batch.mean():.2f}, std {batch.std():.2f}", MUTED),
                              (axes[1], xh, "x̂ = (x − μ_B) / √(σ²_B + ε)\nmean 0, std 1", AQUA),
                              (axes[2], gamma * xh + beta, f"y = γ·x̂ + β   (learned γ = {gamma}, β = {beta})", ORANGE)]:
        ax.hist(v, bins=25, color=col)
        ax.axvline(0, color=INK, lw=1)
        ax.set_xlim(-6, 10)
        ax.set_title(title, fontsize=12)
    caption(fig, "In eval() there is no batch (one face from the camera): BatchNorm uses running_mean / running_var "
                 "collected during training instead.")
    L.save(fig, "batchnorm")

# ---------------------------------------------------------------- 5. dropout: train vs eval
if L.wanted("dropout"):
    sizes = [6, 8, 8, 4]
    xs = [0.12, 0.4, 0.68, 0.92]
    pos = [[(xs[l], 0.5 + (j - (n - 1) / 2) * 0.1) for j in range(n)] for l, n in enumerate(sizes)]
    fig, ax = plt.subplots(figsize=(11, 6.2))
    frames = 10

    def upd(f):
        blank(ax)
        train = f < 7
        drop = [np.zeros(n, bool) for n in sizes]
        if train:
            r = np.random.default_rng(f)
            for l in (1, 2):
                drop[l] = r.random(sizes[l]) < 0.3
        for l in range(3):
            for j, p in enumerate(pos[l]):
                for k, q in enumerate(pos[l + 1]):
                    if not drop[l][j] and not drop[l + 1][k]:
                        ax.plot([p[0], q[0]], [p[1], q[1]], color=INK2, lw=0.6, alpha=0.6)
        for l in range(4):
            for j, p in enumerate(pos[l]):
                ax.add_patch(plt.Circle(p, 0.03, color=GRID if drop[l][j] else LIGHT_BLUE,
                                        ec=RED if drop[l][j] else BLUE, lw=2))
                if drop[l][j]:
                    ax.text(*p, "×", ha="center", va="center", color=RED, fontsize=16, weight="bold")
        ax.set_title("model.train(): every batch, a random 30 % of neurons are switched off (the rest ×1/0.7)"
                     if train else "model.eval(): everyone works - the same answer every time", fontsize=12.5)
    L.animate(fig, upd, frames, "dropout", fps=2)
