"""Lesson 21 - how a network learns: backpropagation with numbers, SGD / momentum / Adam, the learning-rate schedule."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)

# ---------------------------------------------------------------- 1. backprop on the guide's tiny network
if L.wanted("backprop"):
    nodes = {"x": (0.05, 0.55), "w1": (0.05, 0.85), "b1": (0.2, 0.85), "z1": (0.27, 0.55), "h": (0.45, 0.55),
             "w2": (0.45, 0.85), "b2": (0.6, 0.85), "y": (0.66, 0.55), "t": (0.88, 0.85), "L": (0.88, 0.55)}
    fwd = {"x": "x = 2", "w1": "w1 = 0.5", "b1": "b1 = 0", "z1": "z1 = w1·x + b1\n= 1.0", "h": "h = ReLU(z1)\n= 1.0",
           "w2": "w2 = −1.0", "b2": "b2 = 1", "y": "y = w2·h + b2\n= 0.0", "t": "target t = 1", "L": "L = (y − t)²\n= 1.0"}
    grads = [("L", "y", "dL/dy = 2(y−t) = −2"), ("y", "w2", "dL/dw2 = −2·h = −2"), ("y", "b2", "dL/db2 = −2"),
             ("y", "h", "dL/dh = −2·w2 = 2"), ("h", "z1", "dL/dz1 = 2·1 = 2  (ReLU slope 1)"),
             ("z1", "w1", "dL/dw1 = 2·x = 4"), ("z1", "b1", "dL/db1 = 2")]
    edges = [("x", "z1"), ("w1", "z1"), ("b1", "z1"), ("z1", "h"), ("h", "y"), ("w2", "y"), ("b2", "y"), ("y", "L"),
             ("t", "L")]
    fig, ax = plt.subplots(figsize=(15, 6.4))
    stages = ["forward"] * 3 + [f"back{i}" for i in range(len(grads)) for _ in range(2)] + ["update"] * 5

    def upd(f):
        st = stages[f]
        blank(ax)
        for a, b in edges:
            arrow(ax, nodes[a], nodes[b], color=GRID if st != "forward" else INK2, lw=1.5)
        nb = int(st[4:]) + 1 if st.startswith("back") else (len(grads) if st == "update" else 0)
        for i, (a, b, txt) in enumerate(grads[:nb]):
            pa, pb = nodes[a], nodes[b]
            arrow(ax, (pa[0], pa[1] - 0.03), (pb[0] + 0.01, pb[1] - 0.03), color=RED, lw=2.5, rad=0.25)
            ax.text(0.02, 0.33 - i * 0.045, txt, fontsize=11.5, color=RED, family="monospace")
        for n, (x, y) in nodes.items():
            box(ax, x - 0.06 if n not in ("x",) else x - 0.04, y - 0.06, 0.12 if n != "x" else 0.08, 0.12, fwd[n],
                color=ORANGE if n in ("w1", "b1", "w2", "b2") else BLUE, fontsize=10.5)
        if st == "update":
            ax.text(0.5, 0.33, "update, lr = 0.1:   w1 = 0.5 − 0.1·4 = 0.1    b1 = 0 − 0.1·2 = −0.2\n"
                               "                     w2 = −1 − 0.1·(−2) = −0.8    b2 = 1 − 0.1·(−2) = 1.2", fontsize=12,
                    family="monospace")
            ax.text(0.5, 0.18, "new forward pass:  z1 = 0.0,  h = 0,  y = 1.2,  L = (1.2 − 1)² = 0.04", fontsize=13,
                    weight="bold", color=GREEN)
        ax.set_title({"forward": "1. FORWARD: compute every value from left to right",
                      "update": "3. UPDATE every weight: w = w − lr · gradient  →  the loss drops from 1.0 to 0.04"}.get(
            st, "2. BACKWARD: the chain rule, from the loss back to every weight"), fontsize=13.5)
    L.animate(fig, upd, len(stages), "backprop", fps=1)

# ---------------------------------------------------------------- 2. learning rate on a bumpy landscape
f = lambda w: 0.15 * (w - 1) ** 2 + 0.6 * np.sin(2.2 * w) + 2
df = lambda w: 0.3 * (w - 1) + 1.32 * np.cos(2.2 * w)
if L.wanted("learning_rate"):
    ws = np.linspace(-4, 6, 400)
    runs = {0.02: [-1.8], 0.15: [-1.8], 2.3: [-1.8]}
    for lr, path in runs.items():
        for _ in range(30):
            path.append(path[-1] - lr * df(path[-1]))
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)

    def upd(k):
        for ax, (lr, path) in zip(axes, runs.items()):
            ax.clear()
            ax.plot(ws, f(ws), color=MUTED)
            p = np.array(path[: k + 1])
            ax.plot(p, f(p), "-", color=ORANGE, lw=1, alpha=0.6)
            ax.plot(p[-1], f(p[-1]), "o", color=ORANGE, ms=14)
            ax.set_xlim(-4, 6)
            ax.set_ylim(0.8, 6.5)
            ax.set_title({0.02: "lr 0.02: too small - crawls", 0.15: "lr 0.15: good - settles in a valley",
                          2.3: "lr 2.3: too big - jumps around"}[lr], fontsize=12.5)
            ax.set_xlabel("weight")
        axes[0].set_ylabel("loss")
    L.animate(fig, upd, 31, "learning_rate", fps=4)

# ---------------------------------------------------------------- 3. SGD vs momentum vs Adam
if L.wanted("optimizers"):
    def loss(p):
        x, y = p
        return 0.05 * x ** 2 + 2.0 * y ** 2

    def grad(p, noise):
        x, y = p
        return np.array([0.1 * x, 4.0 * y]) + noise

    rng = np.random.default_rng(0)
    noises = rng.normal(0, 0.15, (80, 2))
    start = np.array([-9.0, 2.2])
    paths = {}
    p = start.copy(); path = [p.copy()]
    for g_n in noises:
        p = p - 0.2 * grad(p, g_n); path.append(p.copy())
    paths["SGD"] = np.array(path)
    p, m = start.copy(), np.zeros(2); path = [p.copy()]
    for g_n in noises:
        m = 0.9 * m + grad(p, g_n); p = p - 0.04 * m; path.append(p.copy())
    paths["momentum"] = np.array(path)
    p, m, v = start.copy(), np.zeros(2), np.zeros(2); path = [p.copy()]
    for t, g_n in enumerate(noises, start=1):
        g = grad(p, g_n)
        m = 0.9 * m + 0.1 * g; v = 0.999 * v + 0.001 * g ** 2
        p = p - 0.3 * (m / (1 - 0.9 ** t)) / (np.sqrt(v / (1 - 0.999 ** t)) + 1e-8); path.append(p.copy())
    paths["Adam"] = np.array(path)
    gx, gy = np.meshgrid(np.linspace(-10, 10, 200), np.linspace(-3, 3, 200))
    fig, ax = plt.subplots(figsize=(13, 5.4))

    def upd(k):
        ax.clear()
        ax.contour(gx, gy, loss((gx, gy)), levels=20, colors=GRID)
        for (name, P), col in zip(paths.items(), [MUTED, BLUE, ORANGE]):
            ax.plot(P[: k + 1, 0], P[: k + 1, 1], "-o", color=col, ms=3, lw=1.6, label=name)
        ax.plot(0, 0, "*", color=GREEN, ms=18)
        ax.set_xlim(-10, 10)
        ax.set_ylim(-3, 3)
        ax.legend(loc="upper right")
        ax.set_title(f"step {k}: a long narrow valley, noisy gradients (mini-batches)")
    L.animate(fig, upd, 60, "optimizers", fps=6)

# ---------------------------------------------------------------- 4. the schedule: warm-up then cosine
if L.wanted("schedule"):
    lr_max = 1e-3
    ep = np.arange(1, 51)
    lr = [lr_max * (0.1 + 0.9 * e / 3) if e <= 3 else 0.5 * lr_max * (1 + math.cos(math.pi * (e - 3) / 47)) for e in ep]
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.plot(ep, lr, "o-", color=VIOLET, ms=4)
    ax.axvspan(0.5, 3.5, color=YELLOW, alpha=0.15)
    ax.text(2, 1.1e-3, "warm-up", ha="center", fontsize=12)
    ax.text(27, 0.75e-3, "cosine decay: big steps first, tiny steps to settle", fontsize=12)
    for e in (1, 3, 15, 27, 40, 50):
        ax.annotate(f"{lr[e - 1]:.1e}", (e, lr[e - 1]), xytext=(e, lr[e - 1] + 1.2e-4), ha="center", fontsize=10)
    ax.set_xlabel("epoch")
    ax.set_ylabel("learning rate")
    ax.set_ylim(0, 1.2e-3)
    ax.set_title("FaceEmotion's schedule: 3 warm-up epochs, then cosine over 47 (lr_max = 1e-3)")
    L.save(fig, "schedule")

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 5. gears: effects along a chain multiply
if L.wanted("gears"):
    fig, ax = plt.subplots(figsize=(13, 4.6))
    blank(ax, (0, 12.5), (-0.6, 5))
    ax.set_aspect("equal")
    gears = [(1.8, 2.6, 1.4, "A", "w1", BLUE), (4.55, 2.6, 0.7, "B", "z1, h", AQUA), (7.0, 2.6, 1.4, "C", "y", YELLOW),
             (9.9, 2.6, 0.7, "D", "loss", ORANGE)]
    for x, y_, r, name, what, col in gears:
        th = np.linspace(0, 2 * np.pi, 300)
        teeth = r + 0.12 * (np.sin(th * (24 if r > 1 else 12)) > 0)
        ax.fill(x + teeth * np.cos(th), y_ + teeth * np.sin(th), color=col, alpha=0.85)
        ax.add_patch(plt.Circle((x, y_), 0.18, color=PAPER))
        ax.text(x, y_ - r - 0.45, f"{name}: {what}", ha="center", fontsize=12, weight="bold")
    for x, txt in [(3.4, "× 2"), (5.8, "× (−1)"), (8.6, "× (−2)")]:
        ax.text(x, 4.5, txt, ha="center", fontsize=14, color=INK2, weight="bold")
    ax.text(6.0, -0.5, "turn w1 a little → the loss turns 2 × (−1) × (−2) = 4 times as much  →  dL/dw1 = 4",
            ha="center", fontsize=13, weight="bold")
    ax.set_title("The chain rule: effects along a chain of gears MULTIPLY (the numbers of Part 2)")
    L.save(fig, "gears")

# ---------------------------------------------------------------- 6. real training curves: SGD vs Adam vs a too-big step (wines)
if L.wanted("real_training"):
    import torch
    from torch import nn
    red = np.genfromtxt(data("32_WineGrader", "winequality-red.csv"), delimiter=";", skip_header=1)
    wht = np.genfromtxt(data("32_WineGrader", "winequality-white.csv"), delimiter=";", skip_header=1)
    Wd = np.vstack([red, wht])
    Xw = (Wd[:, :-1] - Wd[:, :-1].mean(0)) / Wd[:, :-1].std(0)
    yw = np.digitize(Wd[:, -1], [6, 7])
    Xt, yt = torch.tensor(Xw, dtype=torch.float32), torch.tensor(yw)
    runs = [("SGD, lr 0.01 (too careful)", "sgd", 0.01, BLUE), ("SGD + momentum, lr 0.05", "mom", 0.05, AQUA),
            ("Adam, lr 0.003", "adam", 0.003, GREEN), ("SGD, lr 3.0 (too big)", "sgd", 3.0, RED)]
    fig, ax = plt.subplots(figsize=(12, 5.4))
    for name, kind, lr, col in runs:
        torch.manual_seed(0)
        net = nn.Sequential(nn.Linear(11, 32), nn.ReLU(), nn.Linear(32, 32), nn.ReLU(), nn.Linear(32, 3))
        opt = {"sgd": lambda: torch.optim.SGD(net.parameters(), lr=lr),
               "mom": lambda: torch.optim.SGD(net.parameters(), lr=lr, momentum=0.9),
               "adam": lambda: torch.optim.Adam(net.parameters(), lr=lr)}[kind]()
        lossf = nn.CrossEntropyLoss()
        g = torch.Generator().manual_seed(0)
        hist = []
        for epoch in range(15):
            perm = torch.randperm(len(Xt), generator=g)
            for s in range(0, len(Xt), 128):
                idx = perm[s:s + 128]
                opt.zero_grad()
                loss = lossf(net(Xt[idx]), yt[idx])
                loss.backward()
                opt.step()
                hist.append(min(loss.item(), 3.0))
        sm = np.convolve(hist, np.ones(10) / 10, mode="valid")
        ax.plot(sm, color=col, lw=2.2, label=f"{name}: final loss {np.mean(hist[-50:]):.2f}")
    ax.axhline(np.log(3), color=MUTED, ls="--")
    ax.text(5, np.log(3) + 0.03, "ln 3 = 1.10: the loss of pure guessing", color=INK2, fontsize=11)
    ax.set_xlabel("training step (one batch of 128 wines)")
    ax.set_ylabel("cross-entropy loss (smoothed)")
    ax.set_ylim(0.6, 1.8)
    ax.set_title("A real network learning the 6,497 wines: same network, four ways of stepping")
    ax.legend(loc="upper right", fontsize=10)
    L.save(fig, "real_training")
