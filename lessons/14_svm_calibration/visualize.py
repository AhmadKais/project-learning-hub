"""Lesson 14 - the linear SVM (maximum margin, C) and calibration (Platt scaling), compared with Naive Bayes."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from sklearn.svm import SVC

L = Lesson(__file__)
rng = np.random.default_rng(4)

# ---------------------------------------------------------------- 1. many lines separate - which one?
A = rng.normal([-1.6, -1.0], 0.55, (25, 2))
B = rng.normal([1.4, 1.2], 0.55, (25, 2))
Xs = np.vstack([A, B])
ys = np.r_[np.zeros(25), np.ones(25)]
gx, gy = np.meshgrid(np.linspace(-3.5, 3.5, 300), np.linspace(-3, 3.2, 300))


def scatter(ax, X, y):
    ax.scatter(X[y == 0, 0], X[y == 0, 1], s=50, color=BLUE, edgecolor="white", label="ham")
    ax.scatter(X[y == 1, 0], X[y == 1, 1], s=50, color=ORANGE, edgecolor="white", marker="s", label="spam")


if L.wanted("margin"):
    svm = SVC(kernel="linear", C=1000).fit(Xs, ys)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.6))
    scatter(a1, Xs, ys)
    for ang, off in [(-0.3, 0.1), (-1.4, -0.2), (-0.8, 0.5), (-2.2, 0.0)]:
        xs = np.linspace(-3.5, 3.5, 2)
        a1.plot(xs, ang * xs + off, color=MUTED, lw=1.5)
    a1.set_title("Many lines separate the two classes …")
    D = svm.decision_function(np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
    scatter(a2, Xs, ys)
    a2.contourf(gx, gy, D, levels=[-1, 1], colors=[YELLOW], alpha=0.18)
    a2.contour(gx, gy, D, levels=[-1, 0, 1], colors=[INK2, INK, INK2], linestyles=["--", "-", "--"], linewidths=[1.5, 3, 1.5])
    sv = svm.support_vectors_
    a2.scatter(sv[:, 0], sv[:, 1], s=260, facecolor="none", edgecolor=INK, lw=2, label="support vectors")
    w = svm.coef_[0]
    a2.set_title(f"… the SVM picks the one with the WIDEST street  (width = 2/‖w‖ = {2 / np.linalg.norm(w):.2f})")
    a2.legend(loc="lower right", fontsize=10)
    for ax in (a1, a2):
        ax.set_xlim(-3.5, 3.5)
        ax.set_ylim(-3, 3.2)
        ax.set_aspect("equal")
    caption(fig, "Only the circled points (the support vectors) decide the line. Move any other point - nothing changes.")
    L.save(fig, "margin")

# ---------------------------------------------------------------- 2. C: wide street with mistakes vs narrow street
A2 = rng.normal([-0.9, -0.6], 0.85, (60, 2))
B2 = rng.normal([0.9, 0.7], 0.85, (60, 2))
X2 = np.vstack([A2, B2])
y2 = np.r_[np.zeros(60), np.ones(60)]
Cs = np.logspace(-2.5, 2, 19)
models = [SVC(kernel="linear", C=c).fit(X2, y2) for c in Cs]


def draw_C(ax, k):
    ax.clear()
    m = models[k]
    D = m.decision_function(np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
    ax.contourf(gx, gy, D, levels=[-1, 1], colors=[YELLOW], alpha=0.18)
    ax.contour(gx, gy, D, levels=[-1, 0, 1], colors=[INK2, INK, INK2], linestyles=["--", "-", "--"],
               linewidths=[1.5, 3, 1.5])
    scatter(ax, X2, y2)
    ax.scatter(m.support_vectors_[:, 0], m.support_vectors_[:, 1], s=200, facecolor="none", edgecolor=INK, lw=1.2)
    err = (m.predict(X2) != y2).sum()
    ax.set_title(f"C = {Cs[k]:.3g}:  street width {2 / np.linalg.norm(m.coef_[0]):.2f},  "
                 f"{len(m.support_vectors_)} support vectors,  {err} training errors", fontsize=12)
    ax.set_xlim(-3.5, 3.5)
    ax.set_ylim(-3, 3.2)
    ax.set_aspect("equal")


if L.wanted("C_sweep"):
    fig, ax = plt.subplots(figsize=(10, 7.5))
    frames = list(range(len(Cs))) + [len(Cs) - 1] * 3
    L.animate(fig, lambda f: draw_C(ax, frames[f]), len(frames), "C_sweep", fps=2)

# ---------------------------------------------------------------- 3 + 4. real SMS: calibration, NB vs SVM
if L.wanted("calibration") or L.wanted("pr_compare"):
    from sklearn.calibration import CalibratedClassifierCV, calibration_curve
    from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
    from sklearn.metrics import precision_recall_curve
    from sklearn.model_selection import train_test_split
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.svm import LinearSVC
    with open(data("08_SpamClassifier", "sms_spam.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    texts = [r["text"] for r in rows]
    y = np.array([r["label"] == "spam" for r in rows], int)
    tr, va, ytr, yva = train_test_split(texts, y, test_size=0.3, stratify=y, random_state=0)
    tf = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
    Xtr, Xva = tf.fit_transform(tr), tf.transform(va)
    raw = LinearSVC(C=1.0).fit(Xtr, ytr)
    dist = raw.decision_function(Xva)
    cal = CalibratedClassifierCV(LinearSVC(C=1.0), method="sigmoid", cv=5).fit(Xtr, ytr)
    p_svm = cal.predict_proba(Xva)[:, 1]
    cv = CountVectorizer(ngram_range=(1, 2), min_df=2)
    nb = MultinomialNB(alpha=1.0).fit(cv.fit_transform(tr), ytr)
    p_nb = nb.predict_proba(cv.transform(va))[:, 1]

    if L.wanted("calibration"):
        fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.2))
        jit = rng.uniform(-0.04, 0.04, len(yva))
        a1.scatter(dist[yva == 0], yva[yva == 0] + jit[yva == 0], s=8, color=BLUE, alpha=0.5, label="ham (0)")
        a1.scatter(dist[yva == 1], yva[yva == 1] + jit[yva == 1], s=8, color=ORANGE, alpha=0.5, label="spam (1)")
        # Platt scaling by hand: a 1-feature logistic regression from distance to label
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import cross_val_predict
        d_tr = cross_val_predict(LinearSVC(C=1.0), Xtr, ytr, cv=5, method="decision_function")
        platt = LogisticRegression().fit(d_tr.reshape(-1, 1), ytr)
        A_, B_ = platt.coef_[0][0], platt.intercept_[0]
        xs = np.linspace(dist.min(), dist.max(), 200)
        a1.plot(xs, 1 / (1 + np.exp(-(A_ * xs + B_))), color=INK, lw=3,
                label=f"Platt: sigmoid({A_:.1f}·distance {B_:+.1f})")
        a1.axvline(0, color=MUTED, ls="--")
        a1.set_xlabel("LinearSVC output: signed distance from the line")
        a1.set_ylabel("probability of spam")
        a1.set_title("Platt scaling: distance → probability")
        a1.legend(loc="center right", fontsize=10)
        bins = np.linspace(0, 1, 21)
        a2.hist(p_nb, bins=bins, color=BLUE, alpha=0.75, label="Naive Bayes")
        a2.hist(p_svm, bins=bins, color=ORANGE, alpha=0.75, label="calibrated SVM")
        a2.set_yscale("log")
        a2.set_xlabel("predicted probability of spam")
        a2.set_ylabel("messages (log scale)")
        a2.set_title("NB: almost only 0 or 1.  SVM: uses the middle")
        a2.legend(loc="upper center", fontsize=10)
        L.save(fig, "calibration")

    if L.wanted("pr_compare"):
        fig, ax = plt.subplots(figsize=(11, 5.2))
        for p, name, col in [(p_nb, "Naive Bayes", BLUE), (p_svm, "calibrated SVM", ORANGE)]:
            pr, rc, th = precision_recall_curve(yva, p)
            ok = pr[:-1] >= 0.98
            best = rc[:-1][ok].max() if ok.any() else 0
            ax.plot(rc, pr, color=col, label=f"{name}: best recall at precision ≥ 0.98 = {best:.3f}")
            print(f"  {name}: recall at P>=0.98 {best:.3f}")
        ax.axhline(0.98, color=GREEN, ls="--")
        ax.set_xlim(0.5, 1.0)
        ax.set_ylim(0.85, 1.005)
        ax.set_xlabel("recall")
        ax.set_ylabel("precision")
        ax.set_title("Same validation SMS, same rule (Lesson 04): which model catches more spam?")
        ax.legend(loc="lower left")
        L.save(fig, "pr_compare")
