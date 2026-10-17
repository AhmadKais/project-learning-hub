"""Lesson 24 - training in practice: augmentation, class weights, label smoothing, early stopping + checkpoints."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from PIL import Image

L = Lesson(__file__)
rng = np.random.default_rng(0)
EMOTIONS = ["angry", "disgust", "fear", "happy", "sad", "surprise", "neutral"]
COUNTS = np.array([3995, 436, 4097, 7215, 4830, 3171, 4965])          # FER-2013 training split, 28,709 faces

# ---------------------------------------------------------------- 1. augmentation
if L.wanted("augmentation"):
    face = cartoon_face(48, "smile", seed=1)
    big = Image.fromarray(face)

    def augment(seed):
        r = np.random.default_rng(seed)
        im = big
        if r.random() < 0.5:
            im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im = im.rotate(r.uniform(-10, 10), resample=Image.BILINEAR, fillcolor=40)
        dx, dy = r.integers(0, 5, 2)
        im = im.crop((dx, dy, dx + 44, dy + 44)).resize((48, 48))
        a = np.asarray(im).copy()
        if r.random() < 0.5:                                   # random erasing: a hand, glasses ...
            h, w = r.integers(6, 14, 2)
            y0, x0 = r.integers(0, 48 - h), r.integers(0, 48 - w)
            a[y0:y0 + h, x0:x0 + w] = r.integers(0, 255)
        return a

    fig, axes = plt.subplots(2, 6, figsize=(15, 5.6))
    axes[0, 0].imshow(face, cmap="gray", vmin=0, vmax=255)
    axes[0, 0].set_title("original", color=ORANGE, weight="bold")
    for k, ax in enumerate(axes.ravel()[1:], start=1):
        ax.imshow(augment(k), cmap="gray", vmin=0, vmax=255)
        ax.set_title(f"epoch {k}", fontsize=11)
    for ax in axes.ravel():
        ax.axis("off")
    caption(fig, "Flip · rotate ≤ 10° · small crop · random erase.  The network never sees the same picture twice - "
                 "training set ONLY, never validation / test / camera.")
    L.save(fig, "augmentation")

# ---------------------------------------------------------------- 2. imbalance and class weights
if L.wanted("class_weights"):
    w = COUNTS.sum() / (7 * COUNTS)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 4.8))
    a1.bar(range(7), COUNTS, color=[RED if c < 1000 else BLUE for c in COUNTS])
    for i, c in enumerate(COUNTS):
        a1.text(i, c + 100, f"{c:,}", ha="center", fontsize=11)
    a1.set_xticks(range(7), EMOTIONS, rotation=25)
    a1.set_title("FER-2013 training faces per emotion")
    a2.bar(range(7), w, color=[RED if c < 1000 else ORANGE for c in COUNTS])
    for i, v in enumerate(w):
        a2.text(i, v + 0.15, f"{v:.2f}", ha="center", fontsize=11)
    a2.set_xticks(range(7), EMOTIONS, rotation=25)
    a2.set_title("weight in the loss = total / (7 × count)")
    caption(fig, "A mistake on a 'disgust' face costs 9.41; on a 'happy' face 0.57.  "
                 "Without this the network learns to never say 'disgust'.")
    L.save(fig, "class_weights")

# ---------------------------------------------------------------- 3. label smoothing
if L.wanted("label_smoothing"):
    eps, K = 0.1, 7
    onehot = np.eye(7)[3]
    smooth = (1 - eps) * onehot + eps / K
    fig, (a1, a2, a3) = plt.subplots(1, 3, figsize=(16, 4.4))
    a1.bar(range(7), onehot, color=MUTED)
    a1.set_title("normal target: 100 % happy")
    a2.bar(range(7), smooth, color=ORANGE)
    for i, v in enumerate(smooth):
        a2.text(i, v + 0.02, f"{v:.3f}", ha="center", fontsize=10)
    a2.set_title("smoothed target (ε = 0.1): 0.914 / 0.014")
    for ax in (a1, a2):
        ax.set_xticks(range(7), EMOTIONS, rotation=30)
        ax.set_ylim(0, 1.1)
    p = np.linspace(0.15, 0.995, 200)

    def ce(target, p_happy):
        rest = (1 - p_happy) / 6
        probs = np.array([rest] * 3 + [p_happy] + [rest] * 3)
        return -(target * np.log(probs)).sum()

    a3.plot(p, [ce(onehot, q) for q in p], color=MUTED, label="normal: best at p = 1")
    lsc = [ce(smooth, q) for q in p]
    a3.plot(p, lsc, color=ORANGE, label="smoothed: best at p ≈ 0.91")
    a3.plot(p[np.argmin(lsc)], min(lsc), "o", color=ORANGE, ms=10)
    a3.set_xlabel("the network's probability for 'happy'")
    a3.set_ylabel("loss")
    a3.set_title("the loss stops rewarding over-confidence")
    a3.legend()
    L.save(fig, "label_smoothing")

# ---------------------------------------------------------------- 4. early stopping with patience 8 (an illustration)
if L.wanted("early_stopping"):
    ep = np.arange(1, 51)
    train = 1.8 * np.exp(-ep / 9) + 0.25 + rng.normal(0, 0.01, 50)
    val = 1.75 * np.exp(-ep / 8) + 0.95 + 0.0009 * (ep - 18).clip(0) ** 2 + rng.normal(0, 0.015, 50)
    acc = 0.68 - 0.4 * np.exp(-ep / 7) - 0.0004 * (ep - 20).clip(0) ** 2 + rng.normal(0, 0.004, 50)
    best, best_ep, wait, stop = -1, 0, 0, None
    hist = []
    for e, a in zip(ep, acc):
        if a > best:
            best, best_ep, wait = a, e, 0
        else:
            wait += 1
        hist.append((best, best_ep, wait))
        if wait >= 8:
            stop = e
            break
    stop = int(stop or len(ep))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5))

    def upd(f):
        k = min(f, stop - 1)
        e = ep[: k + 1]
        best, best_ep, wait = hist[k]
        a1.clear()
        a1.plot(e, train[: k + 1], color=BLUE, label="training loss")
        a1.plot(e, val[: k + 1], color=ORANGE, label="validation loss")
        a1.set_xlim(0, 51)
        a1.set_ylim(0, 2.6)
        a1.set_xlabel("epoch")
        a1.set_title("train loss falls, validation loss turns up")
        a1.legend(loc="upper right")
        a2.clear()
        a2.plot(e, acc[: k + 1], "o-", color=GREEN, ms=4)
        a2.plot(best_ep, best, "*", color=ORANGE, ms=22, label=f"checkpoint: epoch {best_ep} saved")
        a2.set_xlim(0, 51)
        a2.set_ylim(0.25, 0.72)
        a2.set_xlabel("epoch")
        a2.set_ylabel("validation accuracy")
        done = f >= stop - 1
        a2.set_title(f"epochs without improvement: {wait} / 8" + ("   →  STOP" if done else ""),
                     color=RED if done else INK)
        a2.legend(loc="lower right")
    L.animate(fig, upd, stop + 3, "early_stopping", fps=4)
    print(f"  illustration: best epoch {hist[stop - 1][1]}, stop at {stop}")

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 5. never the same picture twice: random augmentation, animated
if L.wanted("augment_live"):
    from PIL import Image as _Im
    base = cartoon_face(96, "smile")
    r = np.random.default_rng(4)
    fig, axes = plt.subplots(1, 2, figsize=(10, 5.2))

    def upd(k):
        img = _Im.fromarray(base)
        flip = r.random() < 0.5
        ang = r.uniform(-10, 10)
        if flip:
            img = img.transpose(_Im.FLIP_LEFT_RIGHT)
        img = img.rotate(ang, fillcolor=40)
        a = np.asarray(img).copy()
        dx, dy = r.integers(0, 9, 2)
        a = np.pad(a, 4, constant_values=40)[dy:dy + 96, dx:dx + 96]
        erased = r.random() < 0.5
        if erased:
            ex, ey = r.integers(10, 70, 2)
            a[ey:ey + 18, ex:ex + 24] = 0
        for ax in axes:
            ax.clear()
            ax.axis("off")
        axes[0].imshow(base, cmap="gray", vmin=0, vmax=255)
        axes[0].set_title("the stored training face")
        axes[1].imshow(a, cmap="gray", vmin=0, vmax=255)
        axes[1].set_title(f"epoch {k + 1}: what the network sees\nflip {'yes' if flip else 'no'} · "
                          f"rotate {ang:+.0f}° · shift ({dx - 4}, {dy - 4}) · erase {'yes' if erased else 'no'}",
                          fontsize=11)
    L.animate(fig, upd, 16, "augment_live", fps=2)

# ---------------------------------------------------------------- 6. the project's small network on the 7,178 FER test faces, per class
if L.wanted("per_class_real"):
    import torch
    from torch import nn
    from PIL import Image as _Im
    root = HUB / "13_FaceEmotion" / "data" / "fer2013" / "test"
    EMO = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

    def conv_bn(c_in, c_out, stride):
        return nn.Sequential(nn.Conv2d(c_in, c_out, 3, stride, 1, bias=False), nn.BatchNorm2d(c_out), nn.ReLU())

    class SmallNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.features = nn.Sequential(conv_bn(1, 32, 2), conv_bn(32, 64, 1), conv_bn(64, 128, 2), conv_bn(128, 256, 2))
            self.head = nn.Sequential(nn.AdaptiveAvgPool2d(1), nn.Flatten(), nn.Dropout(0.3), nn.Linear(256, 7))

        def forward(self, x):
            return self.head(self.features(x))
    net = SmallNet()
    net.load_state_dict(torch.load(HUB / "13_FaceEmotion" / "data" / "_smallnet.pt", map_location="cpu", weights_only=False))
    net.eval()
    import cv2
    xs, ys = [], []
    for c, e in enumerate(EMO):
        for f in sorted((root / e).iterdir()):
            g = cv2.equalizeHist(np.asarray(_Im.open(f).convert("L")))
            xs.append((g / 255 - 0.5013) / 0.2916)
            ys.append(c)
    X = torch.tensor(np.array(xs), dtype=torch.float32)[:, None]
    y = np.array(ys)
    with torch.no_grad():
        pred = torch.cat([net(X[i:i + 512]).argmax(1) for i in range(0, len(X), 512)]).numpy()
    P = np.array([((pred == c) & (y == c)).sum() / max((pred == c).sum(), 1) for c in range(7)])
    R = np.array([((pred == c) & (y == c)).sum() / (y == c).sum() for c in range(7)])
    F = 2 * P * R / np.maximum(P + R, 1e-9)
    fig, ax = plt.subplots(figsize=(13, 5))
    xx = np.arange(7)
    ax.bar(xx - 0.25, P, 0.25, color=BLUE, label="precision")
    ax.bar(xx, R, 0.25, color=AQUA, label="recall")
    ax.bar(xx + 0.25, F, 0.25, color=ORANGE, label="F1")
    ax.set_xticks(xx, [f"{e}\n({(y == c).sum():,} faces)" for c, e in enumerate(EMO)])
    ax.set_ylim(0, 1)
    ax.axhline(F.mean(), color=INK, ls="--", lw=1.2)
    ax.text(6.5, F.mean() + 0.02, f"macro-F1 {F.mean():.2f}", ha="right", fontsize=12)
    ax.set_title(f"The notebook's small network (8 CPU epochs, class weights + label smoothing) on all {len(y):,} FER-2013 "
                 f"test faces - accuracy {(pred == y).mean():.1%}", fontsize=12)
    ax.legend(loc="upper left", ncols=3)
    print("  per class P/R:", [(e, round(p, 2), round(r_, 2)) for e, p, r_ in zip(EMO, P, R)], "acc", (pred == y).mean())
    L.save(fig, "per_class_real")
