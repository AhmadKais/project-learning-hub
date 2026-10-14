"""Lesson 20 - the neuron, activations, layers (a forward pass you can watch), softmax and cross-entropy."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]


def softmax(z):
    e = np.exp(z - np.max(z))
    return e / e.sum()


# ---------------------------------------------------------------- 1. one neuron, the guide's numbers
if L.wanted("neuron"):
    x, w, b = [0.5, -1.0, 2.0], [0.8, 0.3, -0.4], 0.1
    z = sum(xi * wi for xi, wi in zip(x, w)) + b
    fig, ax = plt.subplots(figsize=(14, 5.2))
    blank(ax)
    for i, (xi, wi) in enumerate(zip(x, w)):
        y = 0.8 - i * 0.3
        box(ax, 0.02, y - 0.07, 0.11, 0.14, f"x{i + 1} = {xi}", color=BLUE)
        arrow(ax, (0.13, y), (0.42, 0.5), text=f"× w{i + 1} = {wi}   →  {xi * wi:+.1f}", fontsize=12,
              text_offset=(0, 0.02 if i != 1 else 0.03))
    ax.add_patch(plt.Circle((0.48, 0.5), 0.075, color=LIGHT_ORANGE, ec=ORANGE, lw=3))
    ax.text(0.48, 0.5, "Σ + b", ha="center", va="center", fontsize=15, weight="bold")
    ax.text(0.48, 0.34, f"z = 0.4 − 0.3 − 0.8 + 0.1 = {z:.1f}", ha="center", fontsize=12.5)
    arrow(ax, (0.555, 0.5), (0.66, 0.5))
    box(ax, 0.66, 0.4, 0.14, 0.2, "ReLU\nmax(0, z)", color=VIOLET, weight="bold")
    arrow(ax, (0.8, 0.5), (0.88, 0.5))
    box(ax, 0.88, 0.4, 0.1, 0.2, f"out = {max(0, z):.1f}", color=GREEN, weight="bold")
    ax.set_title("A neuron: multiply each input by its weight, add, add the bias, apply the activation")
    L.save(fig, "neuron")

# ---------------------------------------------------------------- 2. activation functions
if L.wanted("activations"):
    t = np.linspace(-5, 5, 300)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    for ax, f, name, col in [(axes[0], np.maximum(0, t), "ReLU = max(0, z)   (EmotionNet)", ORANGE),
                             (axes[1], 1 / (1 + np.exp(-t)), "sigmoid (Lesson 12)", BLUE),
                             (axes[2], np.tanh(t), "tanh", AQUA)]:
        ax.plot(t, f, color=col, lw=3)
        ax.axhline(0, color=MUTED, lw=1)
        ax.axvline(0, color=MUTED, lw=1)
        ax.set_title(name, fontsize=13)
    caption(fig, "Without a bent function between layers, many layers collapse into ONE linear function.  "
                 "ReLU is the simplest bend: cheap, and its slope is 1 or 0.")
    L.save(fig, "activations")

# ---------------------------------------------------------------- 3. why layers: a curved boundary
if L.wanted("why_layers"):
    from sklearn.datasets import make_moons
    from sklearn.linear_model import LogisticRegression
    from sklearn.neural_network import MLPClassifier
    X, y = make_moons(400, noise=0.18, random_state=0)
    gx, gy = np.meshgrid(np.linspace(-1.6, 2.6, 250), np.linspace(-1.2, 1.7, 250))
    G = np.c_[gx.ravel(), gy.ravel()]
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))
    models = [(LogisticRegression(), "1 neuron (no hidden layer)"),
              (MLPClassifier((4,), activation="relu", max_iter=4000, random_state=1), "1 hidden layer, 4 ReLU neurons"),
              (MLPClassifier((32, 32), activation="relu", max_iter=4000, random_state=1), "2 hidden layers, 32 + 32")]
    for ax, (m, title) in zip(axes, models):
        m.fit(X, y)
        P = m.predict_proba(G)[:, 1].reshape(gx.shape)
        ax.contourf(gx, gy, P, levels=np.linspace(0, 1, 11), cmap="RdBu_r", alpha=0.45)
        ax.contour(gx, gy, P, levels=[0.5], colors=INK, linewidths=2)
        ax.scatter(X[y == 0, 0], X[y == 0, 1], s=14, color=BLUE)
        ax.scatter(X[y == 1, 0], X[y == 1, 1], s=14, color=ORANGE)
        ax.set_title(f"{title}\naccuracy {m.score(X, y):.2f}", fontsize=12.5)
        ax.set_xticks([])
        ax.set_yticks([])
    L.save(fig, "why_layers")

# ---------------------------------------------------------------- 4. a forward pass you can watch
if L.wanted("forward_pass"):
    rng = np.random.default_rng(3)
    sizes = [4, 5, 5, 3]
    Ws = [rng.normal(0, 0.9, (sizes[i + 1], sizes[i])) for i in range(3)]
    bs = [rng.normal(0, 0.3, sizes[i + 1]) for i in range(3)]
    acts = [np.array([0.9, -0.4, 0.3, 1.2])]
    for i, (Wm, bv) in enumerate(zip(Ws, bs)):
        z = Wm @ acts[-1] + bv
        acts.append(np.maximum(0, z) if i < 2 else softmax(z))
    xs = [0.1, 0.38, 0.66, 0.9]
    pos = [[(xs[l], 0.5 + (j - (n - 1) / 2) * 0.16) for j in range(n)] for l, n in enumerate(sizes)]
    names = ["input", "hidden 1 (ReLU)", "hidden 2 (ReLU)", "softmax"]
    fig, ax = plt.subplots(figsize=(13, 6.4))

    def upd(f):
        layer = min(f, 3)
        blank(ax)
        for l in range(3):
            for j, p in enumerate(pos[l]):
                for k, q in enumerate(pos[l + 1]):
                    wv = Ws[l][k, j]
                    on = l < layer
                    ax.plot([p[0], q[0]], [p[1], q[1]], color=(ORANGE if wv > 0 else BLUE) if on else GRID,
                            lw=0.4 + 1.6 * min(abs(wv), 1.5) if on else 0.8, alpha=0.8 if on else 0.6, zorder=1)
        for l in range(4):
            for j, p in enumerate(pos[l]):
                v = acts[l][j]
                lit = l <= layer
                ax.add_patch(plt.Circle(p, 0.045, color=LIGHT_ORANGE if lit else PAPER, ec=INK if lit else GRID,
                                        lw=2, zorder=3))
                if lit:
                    ax.text(*p, f"{v:.2f}", ha="center", va="center", fontsize=11, zorder=4)
            ax.text(xs[l], 0.07, names[l], ha="center", fontsize=12, weight="bold" if l == layer else "normal")
        ax.set_title(["the input numbers", "layer 1: weighted sums, then ReLU (negatives → 0)",
                      "layer 2: the same again", "output: softmax turns the last numbers into probabilities (sum = 1)"][layer],
                     fontsize=13)
        ax.text(0.5, 0.97, "orange line = positive weight, blue = negative, thickness = size", ha="center",
                fontsize=11, color=INK2)
    L.animate(fig, upd, 7, "forward_pass", fps=1)

# ---------------------------------------------------------------- 5. softmax and cross-entropy on 7 emotions
if L.wanted("softmax"):
    rng = np.random.default_rng(1)
    start = np.array([0.2, -1.0, 0.3, 0.4, 0.1, -0.2, 0.5])
    target = 3                                                   # truth: happy
    frames = 24
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5))

    def upd(f):
        t = min(f / (frames - 6), 1.0)
        z = start + t * np.array([-0.5, -0.8, -0.6, 3.4, -0.6, 0.3, 0.4])   # training pushes "happy" up
        p = softmax(z)
        a1.clear()
        a1.bar(range(7), z, color=[ORANGE if i == target else MUTED for i in range(7)])
        a1.axhline(0, color=INK, lw=1)
        a1.set_ylim(-2.5, 4.5)
        a1.set_xticks(range(7), EMOTIONS, rotation=30)
        a1.set_title("logits z  (the network's raw scores, any numbers)")
        a2.clear()
        a2.bar(range(7), p, color=[ORANGE if i == target else BLUE for i in range(7)])
        a2.set_ylim(0, 1)
        a2.set_xticks(range(7), EMOTIONS, rotation=30)
        a2.set_title(f"softmax → probabilities.   truth = happy:  loss = −ln({p[target]:.3f}) = {-np.log(p[target]):.2f}")
    L.animate(fig, upd, frames, "softmax", fps=4)

# ---------------------------------------------------------------- 6. the guide's softmax example
if L.wanted("softmax_example"):
    z = np.array([2.0, 0.5, -1.0])
    p = softmax(z)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    axes[0].bar(range(3), z, color=MUTED)
    axes[0].set_title("logits z = [2.0, 0.5, −1.0]")
    axes[1].bar(range(3), np.exp(z), color=AQUA)
    axes[1].set_title(f"e^z = [{np.exp(z)[0]:.2f}, {np.exp(z)[1]:.2f}, {np.exp(z)[2]:.2f}],  sum {np.exp(z).sum():.2f}")
    axes[2].bar(range(3), p, color=[MUTED, ORANGE, MUTED])
    axes[2].set_title(f"p = [{p[0]:.3f}, {p[1]:.3f}, {p[2]:.3f}];  truth = class 1 → loss {-np.log(p[1]):.3f}")
    for ax in axes:
        ax.set_xticks(range(3), ["class 0", "class 1", "class 2"])
    L.save(fig, "softmax_example")
