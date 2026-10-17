"""Lesson 26 - real time: the frame budget, the camera thread, and temporal smoothing of the label."""
import sys
from collections import deque
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
rng = np.random.default_rng(4)
N = 5                                                 # config.SMOOTHING_WINDOW

# ---------------------------------------------------------------- simulated per-frame probabilities (happy vs neutral)
T = 100
true_happy = np.clip(0.5 + 0.35 * np.sin(np.linspace(0, 2.2 * np.pi, T) - 1.2), 0.05, 0.95)
p_happy = np.clip(true_happy + rng.normal(0, 0.13, T), 0.01, 0.99)
smooth = np.array([p_happy[max(0, t - N + 1): t + 1].mean() for t in range(T)])
raw_label = p_happy > 0.5
sm_label = smooth > 0.5


def changes(lbl):
    return int((lbl[1:] != lbl[:-1]).sum())


def draw_flicker(a1, a2, t):
    a1.clear()
    a1.plot(range(t + 1), p_happy[: t + 1], color=MUTED, lw=1.2, label="raw P(happy) each frame")
    a1.plot(range(t + 1), smooth[: t + 1], color=ORANGE, lw=3, label=f"moving average of the last {N}")
    a1.axhline(0.5, color=INK, ls="--", lw=1)
    a1.set_xlim(0, T)
    a1.set_ylim(0, 1)
    a1.set_ylabel("P(happy)")
    a1.legend(loc="upper right", fontsize=10)
    a1.set_title(f"frame {t}:  raw says {'HAPPY' if raw_label[t] else 'neutral'}  ·  "
                 f"smoothed says {'HAPPY' if sm_label[t] else 'neutral'}")
    a2.clear()
    for row, lbl, name in [(1, raw_label, "raw label"), (0, sm_label, "smoothed")]:
        for k in range(t + 1):
            a2.add_patch(plt.Rectangle((k, row + 0.1), 1, 0.8, color=ORANGE if lbl[k] else BLUE))
        a2.text(-1, row + 0.5, name, ha="right", va="center", fontsize=11)
    a2.set_xlim(0, T)
    a2.set_ylim(0, 2)
    a2.set_yticks([])
    a2.set_xlabel("frame (25 per second)")
    a2.set_title(f"label changes so far:  raw {changes(raw_label[: t + 1])}   ·   smoothed {changes(sm_label[: t + 1])}"
                 "     (orange = happy, blue = neutral)", fontsize=12)


if L.wanted("flicker"):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(13, 6.6), gridspec_kw={"height_ratios": [2.2, 1]})
    fig.subplots_adjust(hspace=0.45, left=0.12)
    frames = list(range(0, T, 2)) + [T - 1] * 4
    L.animate(fig, lambda f: draw_flicker(a1, a2, frames[f]), len(frames), "flicker", fps=8)
    print(f"  label changes over {T} frames: raw {changes(raw_label)}, smoothed {changes(sm_label)}")

# ---------------------------------------------------------------- average the probabilities, don't vote on labels
if L.wanted("average_vs_vote"):
    frames3 = np.array([[0.6, 0.4], [0.6, 0.4], [0.0, 1.0]])
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.9), sharey=True)
    for k in range(3):
        axes[k].bar([0, 1], frames3[k], color=[ORANGE, BLUE])
        axes[k].set_title(f"frame {k + 1}: {'happy' if frames3[k, 0] > 0.5 else 'sad'}")
        axes[k].set_xticks([0, 1], ["happy", "sad"])
    avg = frames3.mean(0)
    axes[3].bar([0, 1], avg, color=[ORANGE, BLUE])
    axes[3].set_xticks([0, 1], ["happy", "sad"])
    axes[3].set_title(f"average: happy {avg[0]:.1f}, sad {avg[1]:.1f} → SAD")
    axes[0].set_ylim(0, 1.05)
    caption(fig, "Voting on the labels says happy (2 against 1).  Averaging the probabilities says sad: "
                 "the third frame was very sure.  (test_probabilities_are_averaged_not_voted)")
    L.save(fig, "average_vs_vote")

# ---------------------------------------------------------------- the delay smoothing adds
if L.wanted("delay"):
    t = np.arange(40)
    step = (t >= 15).astype(float)
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.step(t, step, where="post", color=INK, lw=2, label="the face changes at frame 15")
    for n, col in [(5, ORANGE), (15, VIOLET)]:
        avg = np.array([step[max(0, k - n + 1): k + 1].mean() for k in t])
        cross = int(np.argmax(avg > 0.5))
        ax.plot(t, avg, "o-", color=col, ms=4, label=f"window {n}: label flips at frame {cross} "
                                                       f"({(cross - 15) / 25 * 1000:.0f} ms later)")
    ax.axhline(0.5, color=MUTED, ls="--", lw=1)
    ax.set_xlabel("frame (25 per second)")
    ax.set_ylabel("P(new emotion)")
    ax.set_title("A moving average lags by about N/2 frames:  N = 5 → ~100 ms (not noticed),  N = 15 → ~300 ms")
    ax.legend(loc="lower right")
    L.save(fig, "delay")

# ---------------------------------------------------------------- the frame budget
if L.wanted("budget"):
    steps = [("Haar detection", 14, ORANGE), ("pre-processing", 1, AQUA), ("inference (GPU)", 3, VIOLET),
             ("draw + convert", 5, BLUE)]
    fig, ax = plt.subplots(figsize=(13, 3.8))
    left = 0
    for name, ms, col in steps:
        ax.barh(1, ms, left=left, color=col, height=0.5, label=f"{name}: {ms} ms")
        left += ms
    ax.legend(loc="upper right", fontsize=10.5, ncols=2)
    ax.barh(0, 35, color=RED, height=0.5)
    ax.text(17.5, 0, "cap.read(): 30–40 ms", ha="center", va="center",
            color="white", fontsize=11.5, weight="bold")
    ax.axvline(40, color=INK, ls="--")
    ax.text(40.5, 0.55, "25 fps\n40 ms", fontsize=11)
    ax.axvline(66, color=INK2, ls=":")
    ax.text(66.5, 0.55, "15 fps\n66 ms", fontsize=11)
    ax.set_yticks([1, 0], ["GUI thread", "camera thread"])
    ax.set_xlim(0, 80)
    ax.set_ylim(-0.5, 2.4)
    ax.set_xlabel("milliseconds")
    ax.set_title("Where one frame's time goes (typical laptop with a GPU, from Ryan's guide)")
    L.save(fig, "budget")

# ---------------------------------------------------------------- latest-frame-only vs a queue
if L.wanted("latest_frame"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 4.8))
    for ax, title, latest in [(a1, "a QUEUE: frames pile up → the screen shows the past", False),
                              (a2, "LATEST FRAME ONLY: overwrite one slot → always fresh", True)]:
        blank(ax)
        box(ax, 0.02, 0.4, 0.2, 0.2, "camera thread\n30 frames / s", color=INK2)
        box(ax, 0.78, 0.4, 0.2, 0.2, "GUI (slower)\n15 frames / s", color=INK2)
        if latest:
            box(ax, 0.4, 0.38, 0.2, 0.24, "frame #97\n(with a Lock,\nread() returns a copy)", color=GREEN, fill="#d5ecd5",
                fontsize=11)
        else:
            for i in range(6):
                box(ax, 0.3 + i * 0.065, 0.42, 0.055, 0.16, f"#{60 + i}", color=RED, fill="#f8d6d6", fontsize=9)
            ax.text(0.5, 0.25, "grows by 15 frames every second …", ha="center", color=RED, fontsize=11)
        arrow(ax, (0.22, 0.5), (0.3 if not latest else 0.4, 0.5))
        arrow(ax, (0.7 if not latest else 0.6, 0.5), (0.78, 0.5))
        ax.set_title(title, fontsize=12.5)
    L.save(fig, "latest_frame")

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 6. what the user SEES: two app screens side by side
if L.wanted("two_screens"):
    face = cartoon_face(96, "smile")
    fig, axes = plt.subplots(1, 2, figsize=(11, 5.4))

    def upd(t):
        for ax, lbl_arr, p_arr, title in [(axes[0], raw_label, p_happy, "without smoothing"),
                                          (axes[1], sm_label, smooth, f"moving average of {N} frames")]:
            ax.clear()
            ax.imshow(face, cmap="gray", vmin=0, vmax=255, extent=(0, 96, 96, 0))
            happy = bool(lbl_arr[t])
            col = ORANGE if happy else BLUE
            word = "HAPPY" if happy else "NEUTRAL"
            ax.add_patch(plt.Rectangle((0, 78), 96, 18, color=col, alpha=0.9))
            ax.text(48, 87, f"{word}  {p_arr[t] if happy else 1 - p_arr[t]:.0%}", ha="center", va="center",
                    color="white", fontsize=16, weight="bold")
            ax.set_xlim(0, 96)
            ax.set_ylim(96, 0)
            ax.axis("off")
            ax.set_title(f"{title}\nlabel changes so far: {changes(lbl_arr[: t + 1])}", fontsize=12)
        fig.suptitle(f"frame {t + 1} of {T}  (25 frames = 1 second)", fontsize=12)
    L.animate(fig, upd, T, "two_screens", fps=12)

# ---------------------------------------------------------------- 7. window size: calm vs late
if L.wanted("window_sizes"):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6), sharey=True)
    for ax, n in zip(axes, (1, 5, 15)):
        sm = np.array([p_happy[max(0, t - n + 1): t + 1].mean() for t in range(T)])
        ax.plot(true_happy, color=GREEN, lw=2, ls="--", label="the real expression")
        ax.plot(sm, color=ORANGE, lw=2.5, label=f"shown (N = {n})")
        ax.axhline(0.5, color=MUTED, lw=1)
        delay_ms = (n - 1) / 2 * 40
        ax.set_title(f"N = {n}: {changes(sm > 0.5)} label changes, delay ≈ {delay_ms:.0f} ms", fontsize=12)
        ax.set_xlabel("frame")
        ax.legend(loc="lower right", fontsize=9)
    axes[0].set_ylabel("P(happy)")
    caption(fig, "Bigger window = calmer label but later reaction. N = 5 is calm enough and still feels instant.")
    L.save(fig, "window_sizes")
