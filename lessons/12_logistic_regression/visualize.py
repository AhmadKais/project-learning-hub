"""Lesson 12 - logistic regression from scratch: sigmoid, log-loss, gradient descent, weights as explanation."""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
rng = np.random.default_rng(0)


def sigmoid(z):
    return 1 / (1 + np.exp(-z))


# ---------------------------------------------------------------- 1. the sigmoid with the guide's three URLs
if L.wanted("sigmoid"):
    fig, ax = plt.subplots(figsize=(12, 5))
    z = np.linspace(-7, 7, 300)
    ax.plot(z, sigmoid(z), color=INK, lw=3)
    ax.axhline(0.5, color=MUTED, ls="--", lw=1)
    ax.axvline(0, color=MUTED, ls="--", lw=1)
    for name, zz, col in [("URL B  google.com", -2.40, BLUE), ("URL A  paypal.com.secure-login.xyz", 0.35, YELLOW),
                          ("URL A'  … with an @", 1.15, ORANGE)]:
        ax.plot(zz, sigmoid(zz), "o", color=col, ms=13, zorder=3)
        ax.annotate(f"{name}\nz = {zz:+.2f}  →  p = {sigmoid(zz):.3f}", (zz, sigmoid(zz)),
                    xytext=(zz + (1 if zz < 0 else 0.6), sigmoid(zz) + (0.2 if zz < 0 else -0.05 if zz > 1 else -0.2)), fontsize=12,
                    arrowprops=dict(arrowstyle="->", color=INK2))
    ax.set_xlabel("z = w·x + bias   (the weighted vote, any number)")
    ax.set_ylabel("p = sigmoid(z)   (a probability)")
    ax.set_title("sigmoid(z) = 1 / (1 + e^(−z))  squashes any number into (0, 1)")
    L.save(fig, "sigmoid")

# ---------------------------------------------------------------- 2. the log-loss
if L.wanted("logloss"):
    fig, ax = plt.subplots(figsize=(12, 5))
    p = np.linspace(0.005, 0.995, 300)
    ax.plot(p, -np.log(p), color=ORANGE, label="truth = phishing:  loss = −ln(p)")
    ax.plot(p, -np.log(1 - p), color=BLUE, label="truth = legitimate:  loss = −ln(1 − p)")
    for pp, lab in [(0.76, "0.27"), (0.10, "2.30")]:
        ax.plot(pp, -math.log(pp), "o", color=ORANGE, ms=10)
        ax.text(pp + 0.02, -math.log(pp) + 0.1, f"p = {pp} → {lab}", fontsize=12, color=ORANGE)
    ax.set_ylim(0, 5)
    ax.set_xlabel("predicted probability of phishing  p")
    ax.set_ylabel("loss")
    ax.set_title("Log-loss: confident and WRONG is punished very hard")
    ax.legend(loc="upper center")
    L.save(fig, "logloss")

# ---------------------------------------------------------------- 3. gradient descent learning a boundary (real URLs)
X, y, names = phish_features()
f1, f2 = names.index("digit_ratio"), names.index("url_length")
idx = rng.choice(len(y), 500, replace=False)
P2 = np.c_[X[idx, f1], np.log(X[idx, f2])]
mu, sd = P2.mean(0), P2.std(0)
Z = (P2 - mu) / sd
Y = y[idx]
w, bias, lr = np.array([-1.5, 1.5]), 0.0, 0.5
hist = []
for step in range(60):
    pr = sigmoid(Z @ w + bias)
    loss = -np.mean(Y * np.log(pr + 1e-12) + (1 - Y) * np.log(1 - pr + 1e-12))
    hist.append((w.copy(), bias, loss))
    grad_w = Z.T @ (pr - Y) / len(Y)          # "error times input"
    grad_b = np.mean(pr - Y)
    w, bias = w - lr * grad_w, bias - lr * grad_b
gx, gy = np.meshgrid(np.linspace(-1.5, 5, 200), np.linspace(-3, 4, 200))


def draw_gd(a1, a2, k):
    wk, bk, lk = hist[k]
    a1.clear()
    a1.contourf(gx, gy, sigmoid(wk[0] * gx + wk[1] * gy + bk), levels=np.linspace(0, 1, 11), cmap="RdBu_r", alpha=0.35)
    a1.contour(gx, gy, sigmoid(wk[0] * gx + wk[1] * gy + bk), levels=[0.5], colors=INK, linewidths=3)
    a1.scatter(Z[Y == 0, 0], Z[Y == 0, 1], s=18, color=BLUE, edgecolor="white", lw=0.4, label="legitimate")
    a1.scatter(Z[Y == 1, 0], Z[Y == 1, 1], s=18, color=ORANGE, edgecolor="white", lw=0.4, label="phishing")
    a1.set_xlim(-1.5, 5)
    a1.set_ylim(-3, 4)
    a1.set_xlabel("digit_ratio (scaled)")
    a1.set_ylabel("log url_length (scaled)")
    a1.set_title(f"step {k}:  w = ({wk[0]:+.2f}, {wk[1]:+.2f}),  bias {bk:+.2f}")
    a1.legend(loc="upper right", fontsize=10)
    a2.clear()
    a2.plot([h[2] for h in hist[: k + 1]], color=ORANGE)
    a2.set_xlim(0, len(hist))
    a2.set_ylim(min(h[2] for h in hist) - 0.02, hist[0][2] + 0.05)
    a2.set_xlabel("gradient-descent step")
    a2.set_ylabel("average log-loss")
    a2.set_title(f"loss = {lk:.3f}")


if L.wanted("gd_boundary"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1.3, 1]})
    frames = list(range(0, 20)) + list(range(20, 60, 3)) + [59] * 4
    L.animate(fig, lambda f: draw_gd(a1, a2, frames[f]), len(frames), "gd_boundary", fps=4)

# ---------------------------------------------------------------- 4. one gradient step on the loss curve (1-D)
if L.wanted("gd_1d"):
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.4), sharey=True)
    f = lambda t: (t - 2) ** 2 + 0.5
    df_ = lambda t: 2 * (t - 2)
    tt = np.linspace(-1.5, 5.5, 200)
    for ax, lr_, title in [(axes[0], 0.1, "learning rate too small: crawls"), (axes[1], 0.4, "good learning rate"),
                           (axes[2], 1.05, "too big: jumps over and diverges")]:
        ax.plot(tt, f(tt), color=MUTED)
        t = -1.0
        pts = [t]
        for _ in range(8):
            t = t - lr_ * df_(t)
            pts.append(t)
        pts = np.array(pts)
        ax.plot(pts, f(pts), "o-", color=ORANGE, ms=7)
        ax.set_title(f"{title}\n(lr = {lr_})", fontsize=12)
        ax.set_xlabel("weight w")
        ax.set_xlim(-1.5, 5.5)
        ax.set_ylim(0, 13)
    axes[0].set_ylabel("loss")
    caption(fig, "w_new = w − learning_rate × slope.   Walk downhill; the step size decides everything.")
    L.save(fig, "gd_1d")

# ---------------------------------------------------------------- 5. the weights ARE the explanation (guide's toy model)
if L.wanted("contributions"):
    feats = ["has_at_symbol", "brand_in_subdomain", "has_https", "num_dots", "bias"]
    wts = np.array([0.8, 1.2, -1.5, 0.05, -1.0])
    urls = {"A'  http://paypal.com@secure-login.xyz/verify": np.array([1, 1, 0, 3, 1]),
            "B   https://www.google.com/": np.array([0, 0, 1, 2, 1])}
    fig, axes = plt.subplots(1, 2, figsize=(15, 4.6), sharey=True)
    for ax, (u, x) in zip(axes, urls.items()):
        c = wts * x
        ax.barh(range(5)[::-1], c, color=[ORANGE if v > 0 else BLUE for v in c])
        for i, v in enumerate(c):
            ax.text(v + (0.05 if v >= 0 else -0.05), 4 - i, f"{wts[i]:+.2f} × {x[i]:g} = {v:+.2f}",
                    va="center", ha="left" if v >= 0 else "right", fontsize=11)
        ax.axvline(0, color=INK, lw=1)
        ax.set_xlim(-2.6, 2.6)
        zz = c.sum()
        ax.set_title(f"{u}\nz = {zz:+.2f}   p = {sigmoid(zz):.2f}", fontsize=12)
    axes[0].set_yticks(range(5)[::-1], feats)
    caption(fig, "weight × value per feature: exactly the sentences PhishGuard's Explainer shows the user.")
    L.save(fig, "contributions")

# ---------------------------------------------------------------- 6. regularisation: weights shrink as C falls
if L.wanted("regularisation"):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler
    keep = [i for i, n in enumerate(names) if n not in ("has_port", "is_shortener")]
    Xs = StandardScaler().fit_transform(X[:, keep])
    Cs = np.logspace(-3, 1, 14)
    W = np.array([LogisticRegression(C=c, max_iter=3000).fit(Xs, y).coef_[0] for c in Cs])
    fig, ax = plt.subplots(figsize=(12, 5.4))
    top = np.argsort(-np.abs(W[-1]))[:6]
    for j in range(W.shape[1]):
        lab = names[keep[j]] if j in top else None
        ax.semilogx(Cs, W[:, j], color=SERIES[list(top).index(j)] if j in top else GRID, lw=2.5 if j in top else 1,
                    label=lab)
    ax.axhline(0, color=INK, lw=1)
    ax.set_xlabel("C   (small C = strong brake)")
    ax.set_ylabel("weight (scaled features)")
    ax.set_title("L2 regularisation pulls every weight toward 0 as C gets smaller")
    ax.legend(fontsize=10, loc="upper left")
    L.save(fig, "regularisation")
