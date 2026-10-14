"""Lesson 03 - the confusion matrix, precision, recall, F1, macro-F1 - on the real SMS data."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

L = Lesson(__file__)

# ---- a simple model on the real SMS data, to get real probabilities ---------------
with open(data("08_SpamClassifier", "sms_spam.csv"), encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
texts = [r["text"] for r in rows]
y = np.array([r["label"] == "spam" for r in rows], dtype=int)
tr_x, va_x, tr_y, va_y = train_test_split(texts, y, test_size=0.3, stratify=y, random_state=0)
vec = TfidfVectorizer(min_df=2)
model = LogisticRegression(C=3, max_iter=1000).fit(vec.fit_transform(tr_x), tr_y)
p = model.predict_proba(vec.transform(va_x))[:, 1]


def counts(t):
    pred = p >= t
    tp = int(((pred == 1) & (va_y == 1)).sum())
    fp = int(((pred == 1) & (va_y == 0)).sum())
    fn = int(((pred == 0) & (va_y == 1)).sum())
    tn = int(((pred == 0) & (va_y == 0)).sum())
    return tp, fp, fn, tn


def prf(tp, fp, fn):
    pr = tp / (tp + fp) if tp + fp else 1.0
    rc = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * pr * rc / (pr + rc) if pr + rc else 0.0
    return pr, rc, f1


def draw_matrix(ax, tp, fp, fn, tn, title="confusion matrix"):
    blank(ax, (0, 2), (0, 2.25))
    cells = [(0, 1, tn, "TN", "ham → ham\ncorrect", LIGHT_BLUE),
             (1, 1, fp, "FP", "ham → SPAM\nreal mail hidden!", "#f6c9b6"),
             (0, 0, fn, "FN", "spam → ham\nspam got through", "#f3e2b3"),
             (1, 0, tp, "TP", "spam → SPAM\ncaught", LIGHT_ORANGE)]
    for cx, cy, n, tag, what, col in cells:
        ax.add_patch(plt.Rectangle((cx + 0.02, cy + 0.02), 0.96, 0.96, color=col))
        ax.text(cx + 0.5, cy + 0.66, f"{tag} = {n}", ha="center", fontsize=15, weight="bold")
        ax.text(cx + 0.5, cy + 0.3, what, ha="center", va="center", fontsize=10.5, color=INK2)
    ax.text(0.5, 2.08, "predicted ham", ha="center", fontsize=11, color=INK2)
    ax.text(1.5, 2.08, "predicted SPAM", ha="center", fontsize=11, color=INK2)
    ax.text(-0.06, 1.5, "truly ham", ha="right", va="center", fontsize=11, color=INK2, rotation=90)
    ax.text(-0.06, 0.5, "truly spam", ha="right", va="center", fontsize=11, color=INK2, rotation=90)
    ax.set_title(title)


# ---------------------------------------------------------------- 1. the anatomy
if L.wanted("anatomy"):
    tp, fp, fn, tn = counts(0.5)
    pr, rc, f1 = prf(tp, fp, fn)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1, 1.1]})
    draw_matrix(a1, tp, fp, fn, tn, f"{len(va_y)} validation SMS, threshold 0.5")
    blank(a2)
    lines = [("accuracy", "(TP + TN) / all", f"({tp} + {tn}) / {len(va_y)} = {(tp + tn) / len(va_y):.3f}", INK),
             ("precision", "TP / (TP + FP)", f"{tp} / ({tp} + {fp}) = {pr:.3f}", ORANGE),
             ("", "of the messages I called spam,\nhow many really were?", "", INK2),
             ("recall", "TP / (TP + FN)", f"{tp} / ({tp} + {fn}) = {rc:.3f}", ORANGE),
             ("", "of all the real spam,\nhow much did I catch?", "", INK2),
             ("F1", "2·P·R / (P + R)", f"= {f1:.3f}", INK)]
    yy = 0.93
    for name, formula, value, col in lines:
        if name:
            a2.text(0.0, yy, name, fontsize=15, weight="bold", color=col)
            a2.text(0.3, yy, formula, fontsize=14, family="monospace")
            a2.text(0.3, yy - 0.075, value, fontsize=13, color=INK2, family="monospace")
            yy -= 0.17
        else:
            a2.text(0.3, yy + 0.04, formula, fontsize=11.5, color=INK2, style="italic", va="top")
            yy -= 0.12
    L.save(fig, "anatomy")

# ---------------------------------------------------------------- 2. the net picture (100 dots)
if L.wanted("net"):
    rng = np.random.default_rng(1)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    pts = rng.uniform(0, 1, (100, 2))
    is_spam = pts[:, 0] > 0.62                 # spam on the right
    for ax, r, title in [(axes[0], 0.30, "small net:  high precision, low recall"),
                         (axes[1], 0.48, "medium net"),
                         (axes[2], 0.75, "huge net:  high recall, low precision")]:
        blank(ax, (0, 1), (0, 1))
        ax.set_aspect("equal")
        caught = ((pts[:, 0] - 0.95) ** 2 + (pts[:, 1] - 0.5) ** 2) < r ** 2
        ax.add_patch(plt.Circle((0.95, 0.5), r, color=YELLOW, alpha=0.18, ec=YELLOW, lw=2))
        ax.scatter(pts[~is_spam, 0], pts[~is_spam, 1], s=45, color=BLUE, marker="o")
        ax.scatter(pts[is_spam, 0], pts[is_spam, 1], s=60, color=ORANGE, marker="s")
        tp = int((caught & is_spam).sum()); fp = int((caught & ~is_spam).sum()); fn = int((~caught & is_spam).sum())
        pr, rc, _ = prf(tp, fp, fn)
        ax.set_title(title, fontsize=12)
        ax.text(0.5, -0.08, f"precision {tp}/{tp + fp} = {pr:.2f}     recall {tp}/{tp + fn} = {rc:.2f}",
                ha="center", fontsize=12)
    caption(fig, "■ spam   ● ham   — the yellow circle is what the filter calls spam.  "
                 "Bigger net: catches more spam (recall ↑) and more real mail (precision ↓).")
    L.save(fig, "net")

# ---------------------------------------------------------------- 3. threshold sweep animation
ts = np.round(np.linspace(0.05, 0.95, 37), 3)
pr_curve = [prf(*counts(t)[:3]) for t in ts]


def draw_sweep(axes, i):
    a_hist, a_mat, a_curve = axes
    t = ts[i]
    tp, fp, fn, tn = counts(t)
    a_hist.clear()
    bins = np.linspace(0, 1, 41)
    a_hist.hist(p[va_y == 0], bins=bins, color=BLUE, alpha=0.85, label="real ham")
    a_hist.hist(p[va_y == 1], bins=bins, color=ORANGE, alpha=0.85, label="real spam")
    a_hist.set_yscale("log")
    a_hist.axvline(t, color=INK, lw=3)
    a_hist.axvspan(t, 1, color=YELLOW, alpha=0.12)
    a_hist.text(t + 0.01, 0.75, f"t = {t:.2f}  → SPAM", fontsize=11, weight="bold")
    a_hist.set_xlabel("the model's spam probability")
    a_hist.set_ylabel("messages (log scale)")
    a_hist.legend(loc="upper center")
    a_hist.set_title("move the threshold …")
    draw_matrix(a_mat, tp, fp, fn, tn, "… the matrix changes …")
    a_curve.clear()
    a_curve.plot(ts, [c[0] for c in pr_curve], color=ORANGE, label="precision")
    a_curve.plot(ts, [c[1] for c in pr_curve], color=AQUA, label="recall")
    a_curve.plot(ts, [c[2] for c in pr_curve], color=MUTED, ls="--", label="F1")
    pr, rc, f1 = pr_curve[i]
    a_curve.plot([t, t], [pr, rc], "o", color=INK, ms=8)
    a_curve.axvline(t, color=INK, lw=1)
    a_curve.set_ylim(0.4, 1.02)
    a_curve.set_xlabel("threshold")
    a_curve.set_title(f"… P = {pr:.2f}   R = {rc:.2f}")
    a_curve.legend(loc="lower left")


if L.wanted("threshold_sweep"):
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.2), gridspec_kw={"width_ratios": [1.2, 1, 1]})
    frames = list(range(len(ts))) + list(range(len(ts) - 2, 0, -1))
    L.animate(fig, lambda k: draw_sweep(axes, frames[k]), len(frames), "threshold_sweep", fps=5)

# ---------------------------------------------------------------- 4. the accuracy trap
if L.wanted("accuracy_trap"):
    tp, fp, fn, tn = counts(0.5)
    n = len(va_y)
    fig, ax = plt.subplots(figsize=(11, 4.4))
    models = ["'always ham'\n(no model at all)", "the real model\n(threshold 0.5)"]
    acc = [(va_y == 0).mean(), (tp + tn) / n]
    rec = [0.0, tp / (tp + fn)]
    xs = np.arange(2)
    ax.bar(xs - 0.18, acc, 0.34, color=BLUE, label="accuracy")
    ax.bar(xs + 0.18, rec, 0.34, color=ORANGE, label="recall of spam")
    for x, a, r in zip(xs, acc, rec):
        ax.text(x - 0.18, a + 0.02, f"{a:.1%}", ha="center", fontsize=13)
        ax.text(x + 0.18, r + 0.02, f"{r:.1%}", ha="center", fontsize=13)
    ax.set_xticks(xs, models)
    ax.set_ylim(0, 1.15)
    ax.set_title("A model that never finds any spam still scores 87% accuracy")
    ax.legend(loc="upper left")
    L.save(fig, "accuracy_trap")

# ---------------------------------------------------------------- 5. three classes, macro-F1 (wine)
if L.wanted("macro_f1"):
    from sklearn.model_selection import cross_val_predict
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    red = np.genfromtxt(data("32_WineGrader", "winequality-red.csv"), delimiter=";", skip_header=1)
    wht = np.genfromtxt(data("32_WineGrader", "winequality-white.csv"), delimiter=";", skip_header=1)
    W = np.vstack([red, wht])
    grade = np.digitize(W[:, -1], [6, 7])          # <=5 low, 6 medium, >=7 high
    pred = cross_val_predict(make_pipeline(StandardScaler(), KNeighborsClassifier(15, weights="distance")),
                             W[:, :-1], grade, cv=5)
    names = ["low", "medium", "high"]
    M = np.zeros((3, 3), int)
    for t_, p_ in zip(grade, pred):
        M[t_, p_] += 1
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.2), gridspec_kw={"width_ratios": [1, 1.1]})
    a1.imshow(M, cmap="Blues")
    a1.grid(False)
    for i in range(3):
        for j in range(3):
            a1.text(j, i, M[i, j], ha="center", va="center", fontsize=14,
                    color="white" if M[i, j] > M.max() * 0.5 else INK)
    a1.set_xticks(range(3), names)
    a1.set_yticks(range(3), names)
    a1.set_xlabel("predicted grade")
    a1.set_ylabel("true grade")
    a1.set_title("a quick, untuned k-NN on 6,497 wines")
    P = np.diag(M) / M.sum(0)
    R = np.diag(M) / M.sum(1)
    F = 2 * P * R / (P + R)
    xs = np.arange(3)
    a2.bar(xs - 0.25, P, 0.25, color=BLUE, label="precision")
    a2.bar(xs, R, 0.25, color=AQUA, label="recall")
    a2.bar(xs + 0.25, F, 0.25, color=ORANGE, label="F1")
    a2.axhline(F.mean(), color=INK, ls="--", lw=1.5)
    a2.text(2.45, F.mean() + 0.02, f"macro-F1 = {F.mean():.3f}", ha="right", fontsize=12)
    acc = np.trace(M) / M.sum()
    a2.set_xticks(xs, [f"{n}\n({M.sum(1)[k]} wines)" for k, n in enumerate(names)])
    a2.set_ylim(0, 1)
    a2.set_title(f"per class  (accuracy {acc:.3f})")
    a2.legend(loc="upper left", ncols=3, fontsize=10)
    caption(fig, "macro-F1 = the plain average of the three F1s: the small 'high' class counts as much as the big one.")
    L.save(fig, "macro_f1")

if L.live:
    from matplotlib.widgets import Slider
    fig, axes = plt.subplots(1, 3, figsize=(17, 5.8), gridspec_kw={"width_ratios": [1.2, 1, 1]})
    fig.subplots_adjust(bottom=0.2)
    s = Slider(fig.add_axes([0.2, 0.05, 0.6, 0.04]), "threshold", 0, len(ts) - 1, valinit=18, valstep=1)
    s.on_changed(lambda v: (draw_sweep(axes, int(v)), fig.canvas.draw_idle()))
    draw_sweep(axes, 18)
    plt.show()
