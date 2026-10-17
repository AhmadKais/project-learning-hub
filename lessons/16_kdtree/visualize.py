"""Lesson 16 - the kd-tree: building by halving, searching with pruning, and the curse of dimensionality."""
import heapq
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
rng = np.random.default_rng(5)


class Node:
    def __init__(self, idx, lo, hi, depth):
        self.idx, self.lo, self.hi, self.depth = idx, lo, hi, depth
        self.axis = self.thr = self.left = self.right = None


def build(P, idx, lo, hi, leaf, depth=0, log=None):
    """Seif's rule: split on the widest axis, at the middle POSITION of the sorted points."""
    node = Node(idx, lo.copy(), hi.copy(), depth)
    if len(idx) <= leaf:
        return node
    spread = P[idx].max(0) - P[idx].min(0)
    ax = int(np.argmax(spread))
    order = idx[np.argsort(P[idx, ax], kind="stable")]
    mid = len(order) // 2
    node.axis, node.thr = ax, P[order[mid], ax]
    if log is not None:
        log.append((ax, node.thr, lo.copy(), hi.copy()))
    hl, lr = hi.copy(), lo.copy()
    hl[ax], lr[ax] = node.thr, node.thr
    node.left = build(P, order[:mid], lo, hl, leaf, depth + 1, log)
    node.right = build(P, order[mid:], lr, hi, leaf, depth + 1, log)
    return node


def search(P, node, q, k, events=None, p=2):
    heap, touched = [], [0]

    def visit(n):
        if n.axis is None:                                   # leaf: measure every point
            for i in n.idx:
                d = (np.abs(P[i] - q) ** p).sum()
                touched[0] += 1
                if len(heap) < k:
                    heapq.heappush(heap, (-d, -i))
                elif d < -heap[0][0]:
                    heapq.heapreplace(heap, (-d, -i))
            if events is not None:
                events.append(("leaf", n, sorted(-i for _, i in heap)))
            return
        diff = q[n.axis] - n.thr
        near, far = (n.left, n.right) if diff <= 0 else (n.right, n.left)
        visit(near)
        gap = abs(diff) ** p
        if len(heap) < k or gap <= -heap[0][0]:
            visit(far)
        elif events is not None:
            events.append(("prune", far, sorted(-i for _, i in heap)))

    visit(node)
    return sorted(-i for _, i in heap), touched[0]


# ---------------------------------------------------------------- data: 2-D wine sample (alcohol, volatile acidity)
red = np.genfromtxt(data("32_WineGrader", "winequality-red.csv"), delimiter=";", skip_header=1)
wht = np.genfromtxt(data("32_WineGrader", "winequality-white.csv"), delimiter=";", skip_header=1)
W = np.vstack([red, wht])
Xall = W[:, :-1]
Zall = (Xall - Xall.mean(0)) / Xall.std(0)
P = Zall[rng.choice(len(Zall), 160, replace=False)][:, [10, 1]]
P = np.clip(P, -2.5, 3.2)
LO, HI = np.array([-2.6, -2.6]), np.array([3.3, 3.3])
LEAF = 8

# ---------------------------------------------------------------- 1. building, cut by cut
if L.wanted("kd_build"):
    cuts = []
    root = build(P, np.arange(len(P)), LO, HI, LEAF, log=cuts)
    fig, ax = plt.subplots(figsize=(8.6, 8))

    def upd(f):
        ax.clear()
        ax.scatter(P[:, 0], P[:, 1], s=22, color=BLUE)
        n = min(f, len(cuts))
        for j, (axis, thr, lo, hi) in enumerate(cuts[:n]):
            col = ORANGE if j == n - 1 else INK2
            lw = 3 if j == n - 1 else 1.2
            if axis == 0:
                ax.plot([thr, thr], [lo[1], hi[1]], color=col, lw=lw)
            else:
                ax.plot([lo[0], hi[0]], [thr, thr], color=col, lw=lw)
        ax.set_xlim(LO[0], HI[0])
        ax.set_ylim(LO[1], HI[1])
        ax.set_aspect("equal")
        ax.set_xlabel("alcohol (z)")
        ax.set_ylabel("volatile acidity (z)")
        ax.set_title(f"cut {n} of {len(cuts)}: split the WIDEST side at the middle point\n"
                     f"(stop when a box has ≤ {LEAF} wines)", fontsize=12.5)
    L.animate(fig, upd, len(cuts) + 4, "kd_build", fps=2)

# ---------------------------------------------------------------- 2. searching with pruning
if L.wanted("kd_search"):
    root = build(P, np.arange(len(P)), LO, HI, LEAF)
    q = np.array([0.9, -0.2])
    K = 5
    events = []
    res, touched = search(P, root, q, K, events)
    fig, ax = plt.subplots(figsize=(8.6, 8.4))

    def upd(f):
        ax.clear()
        ax.scatter(P[:, 0], P[:, 1], s=20, color=GRID)
        measured = set()
        for kind, node, best in events[: f + 1]:
            r = plt.Rectangle(node.lo, *(node.hi - node.lo), color=GREEN if kind == "leaf" else MUTED,
                              alpha=0.15 if kind == "leaf" else 0.45, ec=INK2)
            ax.add_patch(r)
            if kind == "leaf":
                measured.update(node.idx.tolist())
        m = np.array(sorted(measured)) if measured else np.array([], int)
        if len(m):
            ax.scatter(P[m, 0], P[m, 1], s=26, color=BLUE)
        kind, node, best = events[min(f, len(events) - 1)]
        ax.scatter(P[best, 0], P[best, 1], s=90, facecolor="none", edgecolor=ORANGE, lw=2.5)
        if len(best) == K:
            r = np.sqrt(((P[best] - q) ** 2).sum(1)).max()
            ax.add_patch(plt.Circle(q, r, fill=False, color=ORANGE, ls="--"))
        ax.scatter(*q, marker="*", s=380, color=INK, zorder=4)
        ax.set_xlim(LO[0], HI[0])
        ax.set_ylim(LO[1], HI[1])
        ax.set_aspect("equal")
        msg = "measure every wine in this box" if kind == "leaf" else "far side can't be closer → SKIPPED"
        ax.set_title(f"step {min(f, len(events) - 1) + 1}: {msg}\n"
                     f"distances computed so far: {len(m)} of {len(P)}", fontsize=12.5)
    L.animate(fig, upd, len(events) + 3, "kd_search", fps=1)
    print(f"  kd search: {touched} of {len(P)} points measured, k={K}")

# ---------------------------------------------------------------- 3. the curse of dimensionality
if L.wanted("curse"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5))
    dims = [1, 2, 3, 5, 8, 12, 20, 50, 100]
    contrast = []
    for d in dims:
        U = rng.uniform(size=(2000, d))
        qq = rng.uniform(size=d)
        dist = np.sqrt(((U - qq) ** 2).sum(1))
        contrast.append(dist.max() / dist.min())
    a1.loglog(dims, contrast, "o-", color=VIOLET)
    a1.set_xlabel("number of dimensions")
    a1.set_ylabel("farthest ÷ nearest distance")
    a1.set_title("distances concentrate: 'near' and 'far' look alike")
    # share of the wines the tree measures, keeping the d features most correlated with quality
    corr = np.abs([np.corrcoef(Zall[:, j], W[:, -1])[0, 1] for j in range(11)])
    order = np.argsort(-corr)
    _, first = np.unique(W, axis=0, return_index=True)
    Zu = Zall[np.sort(first)]
    tr = rng.permutation(len(Zu))
    train, test = Zu[tr[:4250]], Zu[tr[4250:4450]]
    ds, shares = [2, 4, 6, 8, 11], []
    for d in ds:
        cols = order[:d]
        Pt = train[:, cols]
        root = build(Pt, np.arange(len(Pt)), Pt.min(0) - 1, Pt.max(0) + 1, 16)
        shares.append(np.mean([search(Pt, root, t[cols], 20)[1] for t in test]) / len(Pt))
    a2.plot(ds, shares, "o-", color=ORANGE)
    for d, s in zip(ds, shares):
        a2.text(d, s + 0.02, f"{s:.0%}", ha="center", fontsize=12)
    a2.set_ylim(0, 1)
    a2.set_xlabel("number of wine features used")
    a2.set_ylabel("share of wines measured per query")
    a2.set_title("the kd-tree on the real wines (k = 20, leaf 16)")
    print("  kd shares:", list(zip(ds, np.round(shares, 3))))
    caption(fig, "In 2-D the tree skips almost everything; with all 11 features it measures most wines anyway.")
    L.save(fig, "curse")

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 4. the paper example: 8 wines, 4 boxes, Q, who was measured
if L.wanted("paper_tree"):
    pts = {"A": (1, 7), "B": (2, 2), "C": (3, 9), "D": (5, 4), "E": (6, 8), "F": (7, 1), "G": (8, 6), "H": (9, 3)}
    measured = {"B", "D", "F", "H"}
    Q = (5.5, 2.5)
    fig, ax = plt.subplots(figsize=(8.5, 8))
    boxes = [((0, 0), 6, 7, "{B, D}"), ((0, 7), 6, 3, "{A, C}"), ((6, 0), 4, 6, "{F, H}"), ((6, 6), 4, 4, "{G, E}")]
    for (x0, y0), w_, h_, name in boxes:
        skipped = name in ("{A, C}", "{G, E}")
        ax.add_patch(plt.Rectangle((x0, y0), w_, h_, fc="#ecebe7" if skipped else LIGHT_BLUE, ec=INK2, lw=2))
        ax.text(x0 + 0.15, y0 + h_ - 0.4, "SKIPPED" if skipped else "searched", fontsize=11,
                color=MUTED if skipped else BLUE, weight="bold")
    ax.plot([6, 6], [0, 10], color=RED, lw=4)
    ax.plot([0, 6], [7, 7], color=ORANGE, lw=3)
    ax.plot([6, 10], [6, 6], color=ORANGE, lw=3)
    ax.text(6.1, 9.6, "cut 1: x = 6", color=RED, fontsize=12, weight="bold")
    ax.text(0.15, 7.15, "cut 2: y = 7", color=ORANGE, fontsize=11)
    ax.text(8.0, 6.15, "cut 3: y = 6", color=ORANGE, fontsize=11)
    for n, (x, y_) in pts.items():
        ax.scatter(x, y_, s=200, color=GREEN if n in measured else MUTED, edgecolor=INK, zorder=3)
        ax.text(x + 0.2, y_ + 0.2, n, fontsize=13, weight="bold")
    ax.scatter(*Q, s=380, marker="*", color=INK, zorder=4)
    ax.text(Q[0] - 0.2, Q[1] - 0.6, "Q", fontsize=14, weight="bold")
    ax.add_patch(plt.Circle(Q, np.sqrt(2.5), fill=False, ec=GREEN, lw=2, ls="--"))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.set_aspect("equal")
    ax.set_title("Nearest wine to Q: green = measured (4 of 8), grey = never looked at.\n"
                 "Dashed circle = the best distance so far (D): the grey boxes are outside it", fontsize=12)
    L.save(fig, "paper_tree")

# ---------------------------------------------------------------- 5. halving: why trees are fast (the phone book)
if L.wanted("halving"):
    ns = np.array([10, 100, 1000, 10_000, 100_000, 1_000_000, 10_000_000])
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.loglog(ns, ns, "o-", color=RED, label="look at every item")
    ax.loglog(ns, np.ceil(np.log2(ns)), "o-", color=GREEN, label="halve again and again (a sorted phone book, a tree)")
    for n in ns:
        ax.text(n, np.ceil(np.log2(n)) * 1.6, f"{int(np.ceil(np.log2(n)))}", ha="center", fontsize=11, color=GREEN)
    ax.set_xlabel("number of items")
    ax.set_ylabel("steps to find one (log scale)")
    ax.set_title("10 million names: 10,000,000 looks one by one - or 24 halvings")
    ax.legend()
    L.save(fig, "halving")

# ---------------------------------------------------------------- 6. the honest timing on the real wines
if L.wanted("timing"):
    import time
    corr = np.abs([np.corrcoef(Zall[:, j], W[:, -1])[0, 1] for j in range(11)])
    order = np.argsort(-corr)
    _, first = np.unique(W, axis=0, return_index=True)
    Zu = Zall[np.sort(first)]
    perm = rng.permutation(len(Zu))
    train, test = Zu[perm[:4250]], Zu[perm[4250:4350]]
    ds, t_lin, t_tree = [2, 4, 6, 8, 11], [], []
    for d in ds:
        cols = order[:d]
        Pt = train[:, cols]
        root = build(Pt, np.arange(len(Pt)), Pt.min(0) - 1, Pt.max(0) + 1, 16)
        t0 = time.perf_counter()
        for q in test[:, cols]:
            np.argpartition(((Pt - q) ** 2).sum(1), 20)[:20]
        t_lin.append((time.perf_counter() - t0) / len(test) * 1000)
        t0 = time.perf_counter()
        for q in test[:, cols]:
            search(Pt, root, q, 20)
        t_tree.append((time.perf_counter() - t0) / len(test) * 1000)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(ds, t_lin, "o-", color=BLUE, lw=3, label="linear: numpy measures all 4,250 at once")
    ax.plot(ds, t_tree, "o-", color=ORANGE, lw=3, label="kd-tree written in plain Python")
    ax.set_yscale("log")
    ax.set_xlabel("number of wine features used")
    ax.set_ylabel("milliseconds per new wine (log)")
    ax.set_title("Measured on this computer: fewer distances is not the same as less time")
    ax.legend()
    print("  timing ms:", list(zip(ds, np.round(t_lin, 3), np.round(t_tree, 3))))
    caption(fig, "Numpy does thousands of distances in one fast C loop; the Python tree pays for every step it walks.")
    L.save(fig, "timing")
