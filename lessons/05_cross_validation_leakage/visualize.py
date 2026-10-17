"""Lesson 05 - k-fold cross-validation, stratified folds, nested CV, and a live leakage demonstration."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, KFold, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_classif

L = Lesson(__file__)
rng = np.random.default_rng(0)

red = np.genfromtxt(data("32_WineGrader", "winequality-red.csv"), delimiter=";", skip_header=1)
wht = np.genfromtxt(data("32_WineGrader", "winequality-white.csv"), delimiter=";", skip_header=1)
W = np.vstack([red, wht])
colour = np.r_[np.zeros(len(red)), np.ones(len(wht))]
_, first = np.unique(np.c_[W, colour], axis=0, return_index=True)        # the duplicate trap: keep each wine once
Wd = W[np.sort(first)]
Xw, yw = Wd[:, :-1], np.digitize(Wd[:, -1], [6, 7])

# ---------------------------------------------------------------- 1. k-fold animation
K = 5
model = make_pipeline(StandardScaler(), KNeighborsClassifier(15, weights="distance"))
scores = cross_val_score(model, Xw, yw, cv=StratifiedKFold(K, shuffle=True, random_state=1), scoring="f1_macro")
print(f"  unique wines {len(Wd)}, duplicates {len(W) - len(Wd)}; 5-fold macro-F1 {np.round(scores, 3)} "
      f"mean {scores.mean():.3f} +- {scores.std():.3f}")


def draw_kfold(ax_grid, ax_bar, i):
    blank(ax_grid, (0, 1), (0, K + 0.8))
    for r in range(K):
        for c in range(K):
            is_test = c == r
            done = r <= i
            col = (ORANGE if is_test else BLUE) if done else GRID
            ax_grid.add_patch(plt.Rectangle((c / K + 0.004, K - 1 - r + 0.1), 1 / K - 0.008, 0.8, color=col))
        ax_grid.text(-0.02, K - 1 - r + 0.5, f"round {r + 1}", ha="right", va="center", fontsize=12,
                     weight="bold" if r == i else "normal")
    ax_grid.text(0.35, K + 0.35, "the data cut into 5 folds:", ha="center", fontsize=12)
    ax_grid.text(0.68, K + 0.35, "■ train", ha="center", fontsize=12, color=BLUE, weight="bold")
    ax_grid.text(0.82, K + 0.35, "■ test", ha="center", fontsize=12, color=ORANGE, weight="bold")
    ax_grid.set_title("each fold is the test set exactly once")
    ax_bar.clear()
    shown = scores[: i + 1]
    ax_bar.barh(np.arange(i + 1)[::-1] + (K - 1 - i), shown, color=ORANGE, height=0.6)
    for r, s in enumerate(shown):
        ax_bar.text(s + 0.005, K - 1 - r, f"{s:.3f}", va="center", fontsize=12)
    ax_bar.set_xlim(scores.min() - 0.06, scores.max() + 0.04)
    ax_bar.set_ylim(-0.6, K - 0.4)
    ax_bar.set_yticks([])
    ax_bar.set_xlabel("macro-F1 on the test fold")
    if i == K - 1:
        ax_bar.axvline(scores.mean(), color=INK, ls="--")
        ax_bar.set_title(f"result: {scores.mean():.3f} ± {scores.std():.3f}")
    else:
        ax_bar.set_title("score of each round")


if L.wanted("kfold"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8), gridspec_kw={"width_ratios": [1.4, 1]})
    frames = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 4, 4]
    L.animate(fig, lambda k: draw_kfold(a1, a2, frames[k]), len(frames), "kfold", fps=2)

# ---------------------------------------------------------------- 2. stratified vs random folds
if L.wanted("stratified"):
    # a small, unlucky sample makes the point visible: 300 wines
    idx = rng.choice(len(yw), 300, replace=False)
    ys = yw[idx]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.4), sharey=True)
    for ax, cv, title in [(axes[0], KFold(10, shuffle=True, random_state=4), "random folds"),
                          (axes[1], StratifiedKFold(10, shuffle=True, random_state=4), "stratified folds")]:
        shares = [(ys[te] == 2).mean() for _, te in cv.split(np.zeros(len(ys)), ys)]
        ax.bar(range(1, 11), shares, color=AQUA)
        ax.axhline((ys == 2).mean(), color=INK, ls="--")
        ax.set_title(title)
        ax.set_xlabel("fold")
        ax.set_xticks(range(1, 11))
    axes[0].set_ylabel('share of "high" wines in the fold')
    caption(fig, "Dashed line = the share in the whole sample.  Random folds swing between "
                 "very few and very many; stratified folds all keep the same share.")
    L.save(fig, "stratified")

# ---------------------------------------------------------------- 3. nested CV diagram
if L.wanted("nested"):
    fig, ax = plt.subplots(figsize=(14, 6.4))
    blank(ax, (0, 1), (0, 1))
    ax.text(0.5, 0.96, "OUTER loop (5 folds): measures the WHOLE procedure", ha="center", fontsize=14, weight="bold")
    for c in range(5):
        ax.add_patch(plt.Rectangle((0.1 + c * 0.16, 0.8), 0.155, 0.1, color=ORANGE if c == 1 else BLUE))
    ax.text(0.1 + 0.16 * 1 + 0.078, 0.85, "outer TEST\n(locked)", ha="center", va="center", color="white", fontsize=11)
    ax.text(0.5, 0.75, "the other 4 folds = outer TRAIN  ↓", ha="center", fontsize=12, color=INK2)
    ax.add_patch(plt.Rectangle((0.08, 0.2), 0.84, 0.5, fill=False, ec=AQUA, lw=2, ls="--"))
    ax.text(0.5, 0.66, "INNER loop (3 folds) — only on the outer TRAIN rows: choose k, p, alpha, scaling, weights",
            ha="center", fontsize=12, weight="bold", color=INK)
    for r in range(3):
        for c in range(3):
            ax.add_patch(plt.Rectangle((0.15 + c * 0.13, 0.5 - r * 0.09), 0.125, 0.07,
                                       color=AQUA if c == r else LIGHT_BLUE))
        ax.text(0.56, 0.535 - r * 0.09, f"try every setting → score", va="center", fontsize=11)
    ax.text(0.85, 0.44, "pick the\nbest setting", ha="center", fontsize=12, weight="bold")
    arrow(ax, (0.75, 0.44), (0.79, 0.44))
    ax.text(0.5, 0.1, "train with the chosen setting on all outer TRAIN rows  →  score ONCE on the outer TEST fold",
            ha="center", fontsize=12.5)
    ax.text(0.5, 0.03, "repeat for each of the 5 outer folds  →  the average is an honest estimate",
            ha="center", fontsize=12.5, weight="bold")
    L.save(fig, "nested")

# ---------------------------------------------------------------- 4. leakage demo: pure noise looks learnable
if L.wanted("leakage"):
    n, d = 100, 5000
    X = rng.normal(size=(n, d))
    y = rng.integers(0, 2, n)                    # labels are COIN FLIPS - nothing can be learned
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    # wrong: choose the 20 "best" features using ALL rows, then cross-validate
    Xsel = SelectKBest(f_classif, k=20).fit_transform(X, y)
    wrong = cross_val_score(LogisticRegression(max_iter=1000), Xsel, y, cv=cv).mean()
    # right: feature selection inside each training fold
    right = cross_val_score(make_pipeline(SelectKBest(f_classif, k=20), LogisticRegression(max_iter=1000)),
                            X, y, cv=cv).mean()
    print(f"  leakage demo: leak {wrong:.3f}, honest {right:.3f}")
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.bar([0, 1], [wrong, right], color=[RED, GREEN], width=0.5)
    ax.axhline(0.5, color=INK, ls="--")
    ax.text(1.3, 0.51, "coin flip", fontsize=11)
    for x, v in [(0, wrong), (1, right)]:
        ax.text(x, v + 0.02, f"{v:.0%}", ha="center", fontsize=16, weight="bold")
    ax.set_xticks([0, 1], ["choose features on ALL rows,\nthen cross-validate  (LEAK)",
                           "choose features INSIDE\neach training fold  (honest)"])
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("cross-validated accuracy")
    ax.set_title("The labels are random coin flips.  Leakage still 'finds' a pattern.")
    L.save(fig, "leakage")

# ---------------------------------------------------------------- 5. the duplicate trap, measured
if L.wanted("duplicates"):
    Xa, ya = W[:, :-1], np.digitize(W[:, -1], [6, 7])
    cv = StratifiedKFold(5, shuffle=True, random_state=1)
    knn1 = make_pipeline(StandardScaler(), KNeighborsClassifier(1))
    with_dups = cross_val_score(knn1, Xa, ya, cv=cv, scoring="f1_macro").mean()
    without = cross_val_score(knn1, Xw, yw, cv=cv, scoring="f1_macro").mean()
    print(f"  1-NN macro-F1 with duplicates {with_dups:.3f}, without {without:.3f}")
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.bar([0, 1], [with_dups, without], color=[RED, GREEN], width=0.5)
    for x, v in [(0, with_dups), (1, without)]:
        ax.text(x, v + 0.015, f"{v:.3f}", ha="center", fontsize=16, weight="bold")
    ax.set_xticks([0, 1], [f"all {len(W):,} rows\n(duplicates in train AND test)",
                           f"{len(Wd):,} unique wines\n(each wine once)"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("macro-F1, 1-NN, 5-fold CV")
    ax.set_title(f"{len(W) - len(Wd):,} wines appear twice: the copy in the test fold finds itself at distance 0")
    L.save(fig, "duplicates")

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 6. one split = one roll of the dice (real wines)
if L.wanted("dice_rolls"):
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import f1_score
    rolls = []
    for seed in range(40):
        a, b, ya_, yb_ = train_test_split(Xw, yw, test_size=300, stratify=yw, random_state=seed)
        rolls.append(f1_score(yb_, model.fit(a, ya_).predict(b), average="macro"))
    rolls = np.array(rolls)
    print(f"  40 single splits of 300 test wines: min {rolls.min():.3f} max {rolls.max():.3f}")
    fig, ax = plt.subplots(figsize=(12, 5))
    bins = np.arange(0.48, 0.70, 0.01)

    def upd(k):
        ax.clear()
        ax.hist(rolls[: k + 1], bins, color=ORANGE, edgecolor="white")
        ax.axvline(rolls[k], color=INK, lw=2)
        ax.set_xlim(0.48, 0.70)
        ax.set_ylim(0, 10)
        ax.set_xlabel("macro-F1 on 300 test wines")
        ax.set_ylabel("how many times")
        ax.set_title(f"split #{k + 1}: score {rolls[k]:.3f}     (lowest so far {rolls[:k + 1].min():.3f}, "
                     f"highest {rolls[:k + 1].max():.3f})")
    frames = list(range(40)) + [39] * 5
    L.animate(fig, lambda i: upd(frames[i]), len(frames), "dice_rolls", fps=4)

# ---------------------------------------------------------------- 7. mean ± std: a win or a tie?
if L.wanted("tie_or_win"):
    fig, ax = plt.subplots(figsize=(12, 4.6))
    cases = []
    for kk, col in [(15, BLUE), (17, AQUA), (1, ORANGE)]:
        mdl = make_pipeline(StandardScaler(), KNeighborsClassifier(kk, weights="distance"))
        sc = cross_val_score(mdl, Xw, yw, cv=StratifiedKFold(K, shuffle=True, random_state=1), scoring="f1_macro")
        cases.append((f"k = {kk}", sc.mean(), sc.std(), col))
        print(f"  k={kk}: {sc.mean():.3f} +- {sc.std():.3f}")
    for i, (name, m, s, col) in enumerate(cases):
        ax.errorbar(m, i, xerr=s, fmt="o", color=col, ms=14, capsize=10, lw=3)
        ax.text(m, i + 0.25, f"{name}:  {m:.3f} ± {s:.3f}", ha="center", fontsize=13, weight="bold")
    ax.axvspan(cases[0][1] - cases[0][2], cases[0][1] + cases[0][2], color=BLUE, alpha=0.08)
    ax.set_yticks([])
    ax.set_ylim(-0.6, 2.7)
    ax.set_xlim(0.50, 0.63)
    ax.set_xlabel("cross-validated macro-F1 (the dot = mean, the bar = ± std)")
    ax.set_title("k = 15 vs k = 17: the bars overlap → a TIE.   k = 1 is clearly lower → a real difference.")
    L.save(fig, "tie_or_win")

# ---------------------------------------------------------------- 8. the folds as a deck of cards (stratified dealing)
if L.wanted("deal_folds"):
    r = np.random.default_rng(3)
    deck = np.array([1] * 8 + [0] * 12)
    r.shuffle(deck)
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.4))
    for ax, strat in [(axes[0], False), (axes[1], True)]:
        blank(ax, (0, 4), (0, 6))
        if strat:
            order = np.r_[np.flatnonzero(deck == 1), np.flatnonzero(deck == 0)]
        else:
            order = np.arange(20)
        folds = [[] for _ in range(4)]
        for j, idx in enumerate(order):
            folds[j % 4 if strat else j // 5].append(deck[idx])
        for f_, cards in enumerate(folds):
            for c_, v in enumerate(cards):
                ax.add_patch(plt.Rectangle((f_ + 0.15, 4.6 - c_ * 0.85), 0.7, 0.7, color=RED if v else INK2))
            ax.text(f_ + 0.5, 0.15, f"fold {f_ + 1}\n{sum(cards)} red", ha="center", fontsize=11)
        ax.set_title("RANDOM cut: red cards bunch up" if not strat else "STRATIFIED: deal red and black separately",
                     fontsize=13)
    caption(fig, "20 cards, 8 red (= the rare class). Stratified dealing gives every fold the same share: 2 red each.")
    L.save(fig, "deal_folds")
