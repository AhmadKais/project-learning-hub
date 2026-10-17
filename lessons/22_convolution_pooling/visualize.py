"""Lesson 22 - convolution (a small filter sliding over the picture), feature maps, stride, pooling, receptive field."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)


def conv2d(img, k):
    """'valid' cross-correlation - what nn.Conv2d computes (without padding)."""
    kh, kw = k.shape
    out = np.zeros((img.shape[0] - kh + 1, img.shape[1] - kw + 1))
    for i in range(out.shape[0]):
        for j in range(out.shape[1]):
            out[i, j] = (img[i:i + kh, j:j + kw] * k).sum()
    return out


# ---------------------------------------------------------------- 1. the filter slides
img = np.array([[0, 0, 0, 9, 9, 9, 9],
                [0, 0, 0, 9, 9, 9, 9],
                [0, 0, 0, 9, 9, 9, 9],
                [0, 0, 0, 9, 9, 9, 9],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0, 0]], float)
K = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]], float)       # vertical-edge detector
OUT = conv2d(img, K)


def grid_numbers(ax, M, cmap, vmin, vmax, title, fmt="{:.0f}"):
    ax.imshow(M, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            level = (M[i, j] - vmin) / (vmax - vmin + 1e-9)
            dark = level < 0.4 if cmap == "Greys_r" else level > 0.6
            ax.text(j, i, fmt.format(M[i, j]), ha="center", va="center", fontsize=12,
                    color="white" if dark else INK)
    ax.set_title(title, fontsize=12.5)


if L.wanted("conv_slide"):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4), gridspec_kw={"width_ratios": [1.3, 0.7, 1]})
    positions = [(i, j) for i in range(5) for j in range(5)]

    def upd(f):
        i, j = positions[min(f, 24)]
        for ax in axes:
            ax.clear()
        grid_numbers(axes[0], img, "Greys_r", 0, 12, "picture (7 × 7)")
        axes[0].add_patch(plt.Rectangle((j - 0.5, i - 0.5), 3, 3, fill=False, ec=ORANGE, lw=4))
        grid_numbers(axes[1], K, "coolwarm", -1.5, 1.5, "filter (3 × 3)\nvertical edges")
        shown = np.full_like(OUT, np.nan)
        for (a, b) in positions[: min(f, 24) + 1]:
            shown[a, b] = OUT[a, b]
        axes[2].imshow(np.nan_to_num(shown), cmap="PuOr", vmin=-30, vmax=30)
        axes[2].grid(False)
        axes[2].set_xticks([])
        axes[2].set_yticks([])
        for a in range(5):
            for b in range(5):
                if not np.isnan(shown[a, b]):
                    axes[2].text(b, a, f"{shown[a, b]:.0f}", ha="center", va="center", fontsize=12)
        axes[2].add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, ec=ORANGE, lw=4))
        patch = img[i:i + 3, j:j + 3]
        axes[2].set_title(f"feature map (5 × 5)\nsum of 9 products = {OUT[i, j]:.0f}", fontsize=12.5)
        fig.suptitle("multiply the 9 pixels under the filter by the 9 filter weights, add them up, write one number",
                     fontsize=13)
    L.animate(fig, upd, 28, "conv_slide", fps=3)

# ---------------------------------------------------------------- 2. classic filters on a face and a photo
if L.wanted("filters"):
    from sklearn.datasets import load_sample_image
    photo = load_sample_image("china.jpg").mean(2)[60:380, 120:500]
    face = cartoon_face(96, "smile").astype(float)
    kernels = {"vertical edges": K, "horizontal edges": K.T,
               "blur": np.ones((3, 3)) / 9, "sharpen": np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], float)}
    fig, axes = plt.subplots(2, 5, figsize=(17, 7))
    for r, picture in enumerate([face, photo]):
        axes[r, 0].imshow(picture, cmap="gray")
        axes[r, 0].set_title("input")
        for c, (name, k) in enumerate(kernels.items(), start=1):
            out = conv2d(picture, k)
            if "edges" in name:
                out = np.abs(out)
            axes[r, c].imshow(out, cmap="gray")
            axes[r, c].set_title(name)
    for ax in axes.ravel():
        ax.axis("off")
    caption(fig, "Hand-made filters.  A CNN LEARNS its own: EmotionNet's first layer has 64 of them, found by "
                 "gradient descent.")
    L.save(fig, "filters")

# ---------------------------------------------------------------- 3. max pooling and stride
if L.wanted("pooling"):
    M = np.array([[1, 3, 2, 1], [4, 6, 5, 0], [3, 1, 1, 2], [0, 2, 7, 4]], float)
    P = M.reshape(2, 2, 2, 2).max(axis=(1, 3))
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6), gridspec_kw={"width_ratios": [1.6, 1]})
    cols = [LIGHT_BLUE, LIGHT_ORANGE, "#d5ecd5", "#ece8fb"]
    for ax, A, title in [(axes[0], M, "4 × 4 feature map"), (axes[1], P, "2 × 2 after max-pool (2 × 2, stride 2)")]:
        n = A.shape[0]
        blank(ax, (0, n), (0, n))
        ax.set_aspect("equal")
        for i in range(n):
            for j in range(n):
                q = (i // (n // 2)) * 2 + j // (n // 2) if n == 4 else i * 2 + j
                ax.add_patch(plt.Rectangle((j, n - 1 - i), 1, 1, color=cols[q], ec=PAPER, lw=3))
                is_max = n == 2 or A[i, j] == P[i // 2, j // 2]
                ax.text(j + 0.5, n - 0.5 - i, f"{A[i, j]:.0f}", ha="center", va="center", fontsize=18,
                        weight="bold" if is_max else "normal", color=INK if is_max else MUTED)
        ax.set_title(title, fontsize=12.5)
    caption(fig, "Keep the strongest response in each 2 × 2 block: 4× fewer numbers, and a feature that moves "
                 "by one pixel gives the same answer.")
    L.save(fig, "pooling")

# ---------------------------------------------------------------- 4. receptive field grows with depth
if L.wanted("receptive_field"):
    fig, ax = plt.subplots(figsize=(13, 5.4))
    blank(ax, (0, 22), (0, 6.2))
    layers = [("input", 21, 1), ("conv 3×3", 19, 3), ("conv 3×3", 17, 5), ("conv 3×3", 15, 7)]
    for r, (name, n, rf) in enumerate(layers):
        y = 0.6 + r * 1.4
        x0 = (22 - n) / 2
        for c in range(n):
            ax.add_patch(plt.Rectangle((x0 + c, y), 0.9, 0.9, color=GRID))
        ax.text(0.2, y + 0.45, name, va="center", fontsize=12)
    # the cone of one top unit
    top = 3
    centre = 11
    for r in range(top, -1, -1):
        y = 0.6 + r * 1.4
        half = top - r
        for c in range(centre - half - 1, centre + half):
            ax.add_patch(plt.Rectangle((c + 0.5, y), 0.9, 0.9, color=ORANGE, alpha=0.35 + 0.15 * (r == top)))
        if r < top:
            ax.text(centre + half + 1.2, y + 0.45, f"the top unit depends on {2 * half + 1} here", va="center", fontsize=12, color=ORANGE)
    ax.set_title("Receptive field: each 3×3 layer lets a unit 'see' 2 more pixels;  stride-2 layers double the growth",
                 fontsize=12.5)
    L.save(fig, "receptive_field")

# ---------------------------------------------------------------- 5. why not a dense layer?
if L.wanted("why_conv"):
    fig, ax = plt.subplots(figsize=(11, 4.2))
    dense = 48 * 48 * 512
    conv = 3 * 3 * 1 * 64
    ax.barh([1, 0], [dense, conv], color=[RED, GREEN])
    ax.set_xscale("log")
    ax.set_yticks([1, 0], ["dense layer:\n2,304 pixels → 512 neurons", "conv layer:\n64 filters of 3 × 3"])
    ax.text(dense * 1.1, 1, f"{dense:,} weights", va="center", fontsize=13)
    ax.text(conv * 1.1, 0, f"{conv:,} weights", va="center", fontsize=13)
    ax.set_xlim(100, 1e8)
    ax.set_title("A filter is SHARED over the whole picture: an eye detector works anywhere, and costs 9 weights")
    L.save(fig, "why_conv")

# ================================================================ expanded lesson: more pictures
def _equalize(img):
    hist = np.bincount(img.ravel(), minlength=256)
    cdf = hist.cumsum()
    cmin = cdf[cdf > 0][0]
    lut = np.round((cdf - cmin) / (cdf[-1] - cmin) * 255).clip(0, 255).astype(np.uint8)
    return lut[img]


def _smallnet_conv1():
    import torch
    sd = torch.load(HUB / "13_FaceEmotion" / "data" / "_smallnet.pt", map_location="cpu", weights_only=False)
    return sd["features.0.0.weight"][:, 0].numpy()          # (32, 3, 3)


# ---------------------------------------------------------------- 6. the detective's stencil: an eye template sliding over a face
if L.wanted("stencil_search"):
    face = cartoon_face(48, "smile").astype(float)
    tmpl = face[15:23, 14:22]                                 # the left eye
    t = (tmpl - tmpl.mean()) / tmpl.std()
    H = face.shape[0] - 8 + 1
    match = np.full((H, H), np.nan)
    order = [(i, j) for i in range(H) for j in range(H)]
    for i, j in order:
        p = face[i:i + 8, j:j + 8]
        match[i, j] = ((p - p.mean()) / (p.std() + 1e-6) * t).mean()
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(14, 5), gridspec_kw={"width_ratios": [0.5, 1, 1]})
    a1.imshow(tmpl, cmap="gray", vmin=0, vmax=255)
    a1.set_title("the stencil\n(an eye, 8 × 8)")
    a1.axis("off")
    steps = list(range(0, len(order), 41)) + [len(order) - 1] * 4

    def upd(k):
        n = steps[k]
        i, j = order[n]
        a2.clear()
        a2.imshow(face, cmap="gray", vmin=0, vmax=255)
        a2.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 8, 8, fill=False, ec=ORANGE, lw=3))
        a2.set_title("sliding over the face")
        a2.axis("off")
        a3.clear()
        shown = np.full_like(match, np.nan)
        for (ii, jj) in order[: n + 1]:
            shown[ii, jj] = match[ii, jj]
        a3.imshow(np.nan_to_num(shown, nan=-1), cmap="magma", vmin=-0.6, vmax=1)
        a3.set_title("the map of marks: bright = 'looks like my stencil'")
        a3.axis("off")
    L.animate(fig, upd, len(steps), "stencil_search", fps=5)

# ---------------------------------------------------------------- 7. REAL learned filters from the project's trained network
if L.wanted("learned_filters"):
    W1 = _smallnet_conv1()
    fig, axes = plt.subplots(4, 8, figsize=(12, 6.4))
    for ax, w in zip(axes.ravel(), W1):
        m = np.abs(w).max()
        ax.imshow(w, cmap="RdBu_r", vmin=-m, vmax=m)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
    fig.suptitle("The 32 filters (3 × 3) of the first layer, LEARNED by the small FaceEmotion network from FER-2013\n"
                 "red = positive weight, blue = negative. Some look like edge or spot detectors; real learned filters are noisy.",
                 fontsize=13)
    L.save(fig, "learned_filters")

# ---------------------------------------------------------------- 8. what those learned filters see on a face
if L.wanted("learned_maps"):
    W1 = _smallnet_conv1()
    face = _equalize(cartoon_face(48, "smile"))
    x = (face / 255 - 0.5013) / 0.2916
    xp = np.pad(x, 1)
    strength = [np.abs(conv2d(xp, w)).mean() for w in W1]
    pick = np.argsort(strength)[::-1][:7]
    fig, axes = plt.subplots(2, 8, figsize=(16, 4.8))
    axes[0, 0].imshow(face, cmap="gray")
    axes[0, 0].set_title("input face", fontsize=11)
    axes[1, 0].axis("off")
    for c, f in enumerate(pick, start=1):
        w = W1[f]
        m = np.abs(w).max()
        axes[0, c].imshow(w, cmap="RdBu_r", vmin=-m, vmax=m)
        axes[0, c].set_title(f"filter {f}", fontsize=11)
        fm = np.maximum(conv2d(xp, w), 0)                    # + ReLU
        axes[1, c].imshow(fm, cmap="magma")
        axes[1, c].set_title("its feature map", fontsize=11)
    for ax in axes.ravel():
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
    fig.suptitle("Seven learned filters slid over a drawn face (after ReLU): each lights up a different kind of edge",
                 fontsize=13)
    fig.tight_layout()
    L.save(fig, "learned_maps")
