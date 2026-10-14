"""Shared drawing helpers for every lesson's visualize.py.

Every lesson folder has a visualize.py that draws its pictures and animations:

    python visualize.py            # write figs/*.png, figs/*.gif and videos/*.mp4
    python visualize.py --live     # open the interactive version (sliders) - use it in class
    python visualize.py --no-video # PNG + GIF only (faster, no ffmpeg needed)

The colours are one fixed palette, large fonts for the projector, and the same
two colours always mean the same thing:  BLUE = the "good / negative" class
(ham, legitimate URL, free room) and ORANGE = the "bad / positive" class
(spam, phishing, collision).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import matplotlib

if "--live" not in sys.argv:
    matplotlib.use("Agg")          # no window: just write files

import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

HUB = Path(__file__).resolve().parents[2]          # project-learning-hub/

# --- palette (categorical, fixed order, colour-blind checked) -----------------
BLUE, ORANGE, AQUA, YELLOW = "#2a78d6", "#eb6834", "#1baf7a", "#eda100"
MAGENTA, GREEN, VIOLET, RED = "#e87ba4", "#008300", "#6250d6", "#e34948"
SERIES = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED]
INK, INK2, MUTED, GRID, PAPER = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
LIGHT_BLUE, LIGHT_ORANGE = "#d6e6f8", "#fbe0d4"

plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "font.size": 13, "axes.titlesize": 15, "axes.titleweight": "bold",
    "axes.labelsize": 13, "axes.edgecolor": MUTED, "axes.labelcolor": INK2,
    "xtick.color": INK2, "ytick.color": INK2, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
    "axes.prop_cycle": matplotlib.cycler(color=SERIES), "lines.linewidth": 2.2,
    "legend.frameon": False, "figure.dpi": 100,
})


class Lesson:
    """Knows where this lesson's figures go and how to save them."""

    def __init__(self, file: str):
        self.dir = Path(file).resolve().parent
        self.figs = self.dir / "figs"
        self.videos = self.dir / "videos"
        parser = argparse.ArgumentParser()
        parser.add_argument("--live", action="store_true", help="open the interactive version")
        parser.add_argument("--no-video", action="store_true", help="skip the MP4 files")
        parser.add_argument("--only", help="draw only the figures whose name contains this")
        self.args, _ = parser.parse_known_args()
        self.live = self.args.live
        self.figs.mkdir(exist_ok=True)

    def wanted(self, name: str) -> bool:
        return self.args.only is None or self.args.only in name

    def save(self, fig, name: str):
        """Save a still picture as figs/<name>.png."""
        path = self.figs / f"{name}.png"
        fig.savefig(path, dpi=110, bbox_inches="tight")
        plt.close(fig)
        print("  wrote", path.relative_to(HUB))

    def animate(self, fig, update, frames, name: str, fps: int = 4, init=None):
        """Save an animation as figs/<name>.gif (shown in the lesson) and videos/<name>.mp4.

        update(i) draws frame i.  The GIF plays inside GitHub and VS Code; the MP4 is the
        same animation for the projector (pause and step through it with the arrow keys).
        """
        anim = animation.FuncAnimation(fig, update, frames=frames, init_func=init,
                                       blit=False, repeat=True)
        gif = self.figs / f"{name}.gif"
        anim.save(gif, writer=animation.PillowWriter(fps=fps), dpi=72)
        print("  wrote", gif.relative_to(HUB))
        if not self.args.no_video and shutil.which("ffmpeg"):
            self.videos.mkdir(exist_ok=True)
            mp4 = self.videos / f"{name}.mp4"
            writer = animation.FFMpegWriter(fps=fps, codec="libx264",
                                            extra_args=["-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-pix_fmt", "yuv420p", "-crf", "28"])
            anim.save(mp4, writer=writer, dpi=110)
            print("  wrote", mp4.relative_to(HUB))
        plt.close(fig)


# --- diagram helpers ------------------------------------------------------------

def box(ax, x, y, w, h, text, color=BLUE, fill=None, fontsize=12, weight="normal",
        text_color=INK, radius=0.02, lw=2):
    """A rounded box with centred text, (x, y) = lower-left corner, in axes data units."""
    patch = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={radius}",
                           linewidth=lw, edgecolor=color, facecolor=fill or PAPER)
    ax.add_patch(patch)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fontsize,
            color=text_color, weight=weight, wrap=True)
    return patch


def arrow(ax, start, end, color=INK2, text=None, lw=2, style="-|>", rad=0.0, fontsize=11,
          text_offset=(0, 0.02)):
    """An arrow from start to end; optional label at its middle."""
    a = FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=18, linewidth=lw,
                        color=color, connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a)
    if text:
        mx, my = (start[0] + end[0]) / 2 + text_offset[0], (start[1] + end[1]) / 2 + text_offset[1]
        ax.text(mx, my, text, ha="center", va="bottom", fontsize=fontsize, color=INK2)
    return a


def blank(ax, xlim=(0, 1), ylim=(0, 1)):
    """Turn an axes into an empty canvas for diagrams (clears what was drawn before)."""
    ax.clear()
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    return ax


def caption(fig, text):
    """A one-line message under the figure - what to notice."""
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.text(0.5, 0.005, text, ha="center", va="bottom", fontsize=12, color=INK2, style="italic")


def data(project: str, name: str) -> Path:
    """Path of a data file of a project, e.g. data('32_WineGrader', 'winequality-red.csv')."""
    return HUB / project / "data" / name


def phish_features():
    """(X, y, names) for the PhishGuard URLs, with the 20 features of 25_PhishGuard/02_examples/url_features.py.

    y = 1 for phishing.  Cached in _viz/_phish_cache.npz (git-ignored) because extraction takes a few seconds.
    """
    import csv
    import numpy as np
    sys.path.insert(0, str(HUB / "25_PhishGuard" / "02_examples"))
    import url_features as uf
    cache = Path(__file__).with_name("_phish_cache.npz")
    if cache.exists():
        z = np.load(cache)
        return z["X"], z["y"], list(uf.FEATURE_NAMES)
    with open(data("25_PhishGuard", "phishing_urls.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    X = np.array([uf.extract(r["URL"]) for r in rows], float)
    y = np.array([r["Label"] == "bad" for r in rows], int)
    np.savez(cache, X=X, y=y)
    return X, y, list(uf.FEATURE_NAMES)


def cartoon_face(size=48, mouth="smile", light=1.0, seed=0):
    """A drawn grey-scale face, size x size, values 0..255 (uint8).

    FER-2013 faces may not be redistributed, so the lessons draw their own: an oval face with
    eyes, brows, nose and a mouth (smile / frown / open / flat), soft shading and a little noise.
    """
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    big = 4 * size
    img = Image.new("L", (big, big), 40)
    d = ImageDraw.Draw(img)
    s = big / 48
    d.ellipse([8 * s, 4 * s, 40 * s, 46 * s], fill=170)                    # face
    for x in (15, 27):                                                     # eyes + brows
        d.ellipse([x * s, 16.5 * s, (x + 6) * s, 21.5 * s], fill=240)
        d.ellipse([(x + 1.5) * s, 17 * s, (x + 4.5) * s, 21 * s], fill=15)
        brow_y = {"frown": 13.5, "open": 12, "smile": 14.5, "flat": 14.5}[mouth]
        tilt = 1.2 if mouth == "frown" else 0
        if x == 15:
            d.line([x * s, (brow_y - tilt) * s, (x + 6) * s, (brow_y + tilt) * s], fill=60, width=int(1.4 * s))
        else:
            d.line([x * s, (brow_y + tilt) * s, (x + 6) * s, (brow_y - tilt) * s], fill=60, width=int(1.4 * s))
    d.line([24 * s, 21 * s, 22.5 * s, 29 * s, 25 * s, 30 * s], fill=120, width=int(s))   # nose
    if mouth == "smile":
        d.arc([16 * s, 26 * s, 32 * s, 38 * s], 20, 160, fill=40, width=int(2.4 * s))
    elif mouth == "frown":
        d.arc([17 * s, 34 * s, 31 * s, 42 * s], 200, 340, fill=40, width=int(2.4 * s))
    elif mouth == "open":
        d.ellipse([20 * s, 32 * s, 28 * s, 41 * s], fill=35)
    else:
        d.line([18 * s, 36 * s, 30 * s, 36 * s], fill=50, width=int(1.6 * s))
    img = img.filter(ImageFilter.GaussianBlur(0.45 * s)).resize((size, size), Image.LANCZOS)
    a = np.asarray(img, float)
    yy, xx = np.mgrid[0:size, 0:size] / size
    a = a * (0.75 + 0.35 * (1 - xx)) * light                                 # light from the left
    a += np.random.default_rng(seed).normal(0, 4, a.shape)
    return np.clip(a, 0, 255).astype(np.uint8)
