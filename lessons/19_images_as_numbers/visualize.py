"""Lesson 19 - a picture is a table of numbers: pixels, channels, normalisation, histogram equalisation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
MEAN, STD = 0.5013, 0.2916                    # FaceEmotion config.py (equalised FER-2013 training pixels)
face = cartoon_face(48, "smile")


def equalize(img):
    """What cv2.equalizeHist does: map each grey level through the cumulative histogram."""
    hist = np.bincount(img.ravel(), minlength=256)
    cdf = hist.cumsum()
    cdf_min = cdf[cdf > 0][0]
    lut = np.round((cdf - cdf_min) / (cdf[-1] - cdf_min) * 255).clip(0, 255).astype(np.uint8)
    return lut[img], lut


# ---------------------------------------------------------------- 1. zoom into the pixels
if L.wanted("zoom"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 6.6), gridspec_kw={"width_ratios": [1, 1.25]})
    sizes = [48, 40, 32, 24, 18, 14, 10, 8]
    cy, cx = 19, 18                                        # around the left eye

    def upd(f):
        n = sizes[min(f, len(sizes) - 1)]
        y0, x0 = max(0, cy - n // 2), max(0, cx - n // 2)
        y0, x0 = min(y0, 48 - n), min(x0, 48 - n)
        a1.clear()
        a1.imshow(face, cmap="gray", vmin=0, vmax=255)
        a1.add_patch(plt.Rectangle((x0 - 0.5, y0 - 0.5), n, n, fill=False, ec=ORANGE, lw=3))
        a1.set_title("48 × 48 face = 2,304 numbers")
        a1.axis("off")
        a2.clear()
        crop = face[y0:y0 + n, x0:x0 + n]
        a2.imshow(crop, cmap="gray", vmin=0, vmax=255)
        a2.set_xticks([])
        a2.set_yticks([])
        a2.grid(False)
        if n <= 10:
            for i in range(n):
                for j in range(n):
                    v = crop[i, j]
                    a2.text(j, i, str(v), ha="center", va="center", fontsize=10 if n == 10 else 12,
                            color="white" if v < 128 else INK)
        a2.set_title(f"zoom: {n} × {n}" + ("  — every square is one number, 0 = black … 255 = white" if n <= 10 else ""),
                     fontsize=12.5)
    L.animate(fig, upd, len(sizes) + 4, "zoom", fps=1)

# ---------------------------------------------------------------- 2. a colour picture = 3 tables (and the BGR trap)
if L.wanted("channels"):
    from sklearn.datasets import load_sample_image
    img = load_sample_image("flower.jpg")[100:340, 150:470]
    fig, axes = plt.subplots(1, 5, figsize=(17, 3.6))
    axes[0].imshow(img)
    axes[0].set_title("the picture (RGB)")
    for ax, c, name, cmap in zip(axes[1:4], range(3), ["R channel", "G channel", "B channel"], ["Reds", "Greens", "Blues"]):
        ax.imshow(img[:, :, c], cmap="gray")
        ax.set_title(name, color={"Reds": RED, "Greens": GREEN, "Blues": BLUE}[cmap])
    axes[4].imshow(img[:, :, ::-1])
    axes[4].set_title("shown as BGR by mistake")
    for ax in axes:
        ax.axis("off")
    caption(fig, "OpenCV stores colour as B, G, R.  Forget cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) and the colours swap.  "
                 "FaceEmotion converts to ONE grey channel anyway.")
    L.save(fig, "channels")

# ---------------------------------------------------------------- 3. histogram equalisation
if L.wanted("equalize"):
    dark = (20 + face.astype(float) * 70 / 255).astype(np.uint8)        # the same face in bad light: 20..90
    eq, lut = equalize(dark)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8.4), gridspec_kw={"height_ratios": [1.15, 1]})
    axes[0, 0].imshow(dark, cmap="gray", vmin=0, vmax=255)
    axes[0, 0].set_title(f"dark face: pixels {dark.min()} … {dark.max()}")
    axes[0, 2].imshow(eq, cmap="gray", vmin=0, vmax=255)
    axes[0, 2].set_title(f"equalised: {eq.min()} … {eq.max()}")
    for ax in (axes[0, 0], axes[0, 2]):
        ax.axis("off")
    axes[0, 1].plot(np.arange(256), lut, color=ORANGE, lw=3)
    axes[0, 1].plot([0, 255], [0, 255], color=MUTED, ls="--", lw=1)
    axes[0, 1].set_xlim(0, 255)
    axes[0, 1].set_ylim(0, 255)
    axes[0, 1].set_aspect("equal")
    axes[0, 1].set_xlabel("old grey level")
    axes[0, 1].set_ylabel("new grey level")
    axes[0, 1].set_title("mapping old → new", fontsize=13)
    axes[1, 0].hist(dark.ravel(), bins=64, range=(0, 255), color=MUTED)
    axes[1, 0].set_title("histogram before")
    axes[1, 1].plot(np.bincount(dark.ravel(), minlength=256).cumsum() / dark.size, color=ORANGE)
    axes[1, 1].set_title("cumulative share of pixels")
    axes[1, 1].set_xlim(0, 255)
    axes[1, 2].hist(eq.ravel(), bins=64, range=(0, 255), color=BLUE)
    axes[1, 2].set_title("histogram after: spread over 0 … 255")
    L.save(fig, "equalize")

# ---------------------------------------------------------------- 4. normalisation
if L.wanted("normalise"):
    eq, _ = equalize(face)
    x0 = eq.astype(float).ravel()
    x1 = x0 / 255
    x2 = (x1 - MEAN) / STD
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, v, title, col in [(axes[0], x0, "raw pixels: 0 … 255", MUTED), (axes[1], x1, "÷ 255 → 0 … 1", AQUA),
                              (axes[2], x2, "(x − 0.5013) / 0.2916 → around 0, spread ≈ 1", ORANGE)]:
        ax.hist(v, bins=40, color=col)
        ax.axvline(0, color=INK, lw=1)
        ax.set_title(title, fontsize=12.5)
        ax.set_yticks([])
    caption(fig, "0.5013 and 0.2916 are the mean and std of the EQUALISED FER-2013 training pixels.  "
                 "The same two numbers in training and with the camera - always.")
    L.save(fig, "normalise")
