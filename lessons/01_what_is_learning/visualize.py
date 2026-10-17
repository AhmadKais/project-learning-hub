"""Lesson 01 - what learning is: rules vs. learning, train/validation/test, overfitting."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
rng = np.random.default_rng(7)

# ---------------------------------------------------------------- 1. rules vs learning
if L.wanted("rules_vs_learning"):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    for ax, title, inputs, out, col in [
        (axes[0], "Normal programming", ["rules\n(you write them)", "data"], "answers", BLUE),
        (axes[1], "Machine learning", ["data", "answers\n(labels)"], "rules\n(the model)", ORANGE),
    ]:
        blank(ax)
        ax.set_title(title)
        box(ax, 0.02, 0.58, 0.3, 0.26, inputs[0], color=INK2)
        box(ax, 0.02, 0.14, 0.3, 0.26, inputs[1], color=INK2)
        box(ax, 0.42, 0.33, 0.22, 0.32, "computer", color=col, fill=LIGHT_BLUE if col == BLUE else LIGHT_ORANGE,
            weight="bold")
        box(ax, 0.74, 0.33, 0.25, 0.32, out, color=col, weight="bold")
        arrow(ax, (0.32, 0.71), (0.42, 0.55))
        arrow(ax, (0.32, 0.27), (0.42, 0.43))
        arrow(ax, (0.64, 0.49), (0.74, 0.49))
    caption(fig, "Spam: you cannot write rules for every trick - so you give examples with answers, "
                 "and the computer finds the rules.")
    L.save(fig, "rules_vs_learning")

# ---------------------------------------------------------------- 2. the three splits
if L.wanted("split"):
    fig, ax = plt.subplots(figsize=(13, 3.6))
    blank(ax)
    parts = [(0.0, 0.6, "TRAIN  60%", "the model learns from these\n(the textbook + homework)", BLUE),
             (0.6, 0.2, "VALID. 20%", "choose settings\n(the mock exam)", AQUA),
             (0.8, 0.2, "TEST  20%", "used ONCE, at the end\n(the real exam)", ORANGE)]
    for x, w, name, what, col in parts:
        ax.add_patch(plt.Rectangle((x, 0.45), w - 0.006, 0.3, color=col))
        ax.text(x + w / 2, 0.6, name, ha="center", va="center", color="white", fontsize=14, weight="bold")
        ax.text(x + w / 2, 0.3, what, ha="center", va="top", fontsize=12, color=INK)
    # tiny "rows" so it looks like a table of examples
    for i in range(60):
        ax.plot([i / 60 + 0.004] * 2, [0.76, 0.84], color=SERIES[i % 2], lw=2)
    ax.text(0.5, 0.92, "every row = one example with its correct answer (shuffled, and stratified: "
                       "every part keeps the same % of each class)", ha="center", fontsize=12, color=INK2)
    L.save(fig, "split")

# ---------------------------------------------------------------- 3. overfitting animation
x = np.sort(rng.uniform(0, 1, 18))
y = np.sin(2 * np.pi * x) + rng.normal(0, 0.25, x.size)
xv = np.sort(rng.uniform(0, 1, 40))
yv = np.sin(2 * np.pi * xv) + rng.normal(0, 0.25, xv.size)
grid = np.linspace(0, 1, 400)
degrees = list(range(0, 16))


def fit(deg):
    coef = np.polyfit(x, y, deg)
    tr = np.mean((np.polyval(coef, x) - y) ** 2)
    va = np.mean((np.polyval(coef, xv) - yv) ** 2)
    return coef, tr, va


results = [fit(d) for d in degrees]
train_err = [r[1] for r in results]
val_err = [r[2] for r in results]
best = int(np.argmin(val_err))


def draw_overfit(axl, axr, i):
    coef, tr, va = results[i]
    d = degrees[i]
    axl.clear()
    axl.scatter(x, y, color=BLUE, s=60, zorder=3, label="training points")
    axl.scatter(xv, yv, color=ORANGE, s=30, alpha=0.7, marker="^", zorder=2, label="validation points")
    axl.plot(grid, np.polyval(coef, grid), color=INK, lw=2.5, label=f"model: degree {d}")
    axl.set_ylim(-2, 2)
    axl.set_xlim(0, 1)
    state = "UNDERFIT" if d < 3 else ("good fit" if d <= 6 else "OVERFIT")
    axl.set_title(f"degree {d}:  {state}")
    axl.legend(loc="lower left", fontsize=10)
    axr.clear()
    axr.plot(degrees[: i + 1], train_err[: i + 1], "o-", color=BLUE, label="error on training data")
    axr.plot(degrees[: i + 1], val_err[: i + 1], "^-", color=ORANGE, label="error on NEW data")
    axr.axvline(best, color=MUTED, ls="--", lw=1)
    axr.text(best + 0.2, 0.9, "best", color=INK2)
    axr.set_xlim(-0.5, 15.5)
    axr.set_ylim(0, 1.0)
    axr.set_xlabel("model complexity (polynomial degree)")
    axr.set_ylabel("mean squared error")
    axr.set_title("error: training vs. NEW data")
    axr.legend(loc="upper right", fontsize=10)


if L.wanted("overfitting"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    L.animate(fig, lambda i: draw_overfit(a1, a2, i), len(degrees), "overfitting", fps=2)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    draw_overfit(a1, a2, len(degrees) - 1)
    L.save(fig, "overfitting_final")

# ---------------------------------------------------------------- 4. bias / variance darts
if L.wanted("bias_variance"):
    fig, axes = plt.subplots(1, 4, figsize=(15, 4.2))
    cases = [("low bias, low variance", 0, 0.08, GREEN, "the goal"),
             ("low bias, HIGH variance", 0, 0.35, ORANGE, "overfitting"),
             ("HIGH bias, low variance", 0.55, 0.08, VIOLET, "underfitting"),
             ("HIGH bias, HIGH variance", 0.55, 0.35, RED, "worst")]
    for ax, (title, off, spread, col, tag) in zip(axes, cases):
        blank(ax, (-1.2, 1.2), (-1.2, 1.2))
        ax.set_aspect("equal")
        for r, c in [(1, GRID), (0.66, "#f1f0ec"), (0.33, GRID)]:
            ax.add_patch(plt.Circle((0, 0), r, color=c, ec=MUTED))
        ax.add_patch(plt.Circle((0, 0), 0.08, color=INK))
        pts = rng.normal([off, off * 0.6], spread, (12, 2))
        ax.scatter(pts[:, 0], pts[:, 1], color=col, s=55, edgecolor="white", zorder=3)
        ax.set_title(title, fontsize=12)
        ax.text(0, -1.35, tag, ha="center", fontsize=12, color=INK2)
    caption(fig, "Each dart = the model trained on a different sample of data.  "
                 "Bias = how far the centre is off;  variance = how scattered the darts are.")
    L.save(fig, "bias_variance")

# ---------------------------------------------------------------- 5. learning from examples (fruit)
fruit_rng = np.random.default_rng(3)
apples = np.c_[fruit_rng.normal(170, 18, 14), fruit_rng.normal(2.5, 1.0, 14)]
lemons = np.c_[fruit_rng.normal(110, 15, 14), fruit_rng.normal(7.8, 1.0, 14)]
order = [(a, 0) for a in apples] + [(l, 1) for l in lemons]
order = [order[i] for i in fruit_rng.permutation(len(order))]
new_fruit = np.array([128, 6.2])


def draw_fruit(ax, n, show_new=False):
    ax.clear()
    seen = order[:n]
    gx, gy = np.meshgrid(np.linspace(60, 230, 200), np.linspace(0, 10.5, 200))
    a = np.array([p for p, c in seen if c == 0])
    l = np.array([p for p, c in seen if c == 1])
    if len(a) and len(l):
        # the "rule": a new fruit belongs to the group whose average it is closest to (scaled axes)
        sc = np.array([170 - 110, 10])
        ca, cl = a.mean(0) / sc, l.mean(0) / sc
        pts = np.c_[gx.ravel(), gy.ravel()] / sc
        lab = (np.linalg.norm(pts - cl, axis=1) < np.linalg.norm(pts - ca, axis=1)).reshape(gx.shape)
        ax.contourf(gx, gy, lab, levels=[-0.5, 0.5, 1.5], colors=[LIGHT_BLUE, "#fbf0c8"], alpha=0.9)
        ax.contour(gx, gy, lab, levels=[0.5], colors=[INK2], linewidths=2, linestyles="--")
    if len(a):
        ax.scatter(a[:, 0], a[:, 1], s=140, color=RED, edgecolor="white", zorder=3, label="apple")
    if len(l):
        ax.scatter(l[:, 0], l[:, 1], s=140, color=YELLOW, edgecolor=INK2, zorder=3, label="lemon")
    if show_new:
        ax.scatter(*new_fruit, s=320, marker="*", color=INK, zorder=4)
        ax.annotate("new fruit: 128 g, yellowness 6.2\n-> on the lemon side -> 'lemon'", new_fruit,
                    xytext=(150, 8.7), fontsize=12, arrowprops=dict(arrowstyle="->", color=INK))
    ax.set_xlim(60, 230)
    ax.set_ylim(0, 10.5)
    ax.set_xlabel("weight (grams)")
    ax.set_ylabel("how yellow (0 = red, 10 = yellow)")
    ax.set_title(f"the computer has seen {n} labelled fruits" + ("  - now it can answer" if show_new else ""))
    ax.legend(loc="upper right")


if L.wanted("fruit_learning"):
    fig, ax = plt.subplots(figsize=(10, 6))
    frames = list(range(1, len(order) + 1)) + [len(order)] * 4
    L.animate(fig, lambda i: draw_fruit(ax, frames[i], show_new=i >= len(order)), len(frames), "fruit_learning", fps=3)
    fig, ax = plt.subplots(figsize=(10, 6))
    draw_fruit(ax, len(order), show_new=True)
    caption(fig, "Every dot is an example with its answer. The dashed line is the rule the computer found by itself.")
    L.save(fig, "fruit_learning_final")

# ---------------------------------------------------------------- 6. machine learning in everyday life
if L.wanted("ml_everywhere"):
    tiles = [("Gmail spam folder", "one e-mail", "words, sender, links", "spam / not spam"),
             ("Phone face unlock", "one photo of a face", "pixel brightness", "you / not you"),
             ("Bank card fraud alert", "one card payment", "amount, country, time", "fraud / normal"),
             ("Netflix / YouTube", "one (person, film) pair", "what you watched before", "will you like it?"),
             ("Google Maps arrival time", "one trip", "hour, road, day of week", "minutes to arrive"),
             ("Doctor's X-ray helper", "one X-ray image", "pixel brightness", "healthy / sick")]
    fig, axes = plt.subplots(2, 3, figsize=(15, 7.2))
    for ax, (title, ex, feat, lab), col in zip(axes.ravel(), tiles, SERIES):
        blank(ax)
        ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0,rounding_size=0.05",
                                    lw=2.5, edgecolor=col, facecolor=PAPER))
        ax.add_patch(FancyBboxPatch((0.02, 0.74), 0.96, 0.24, boxstyle="round,pad=0,rounding_size=0.05",
                                    lw=0, facecolor=col))
        ax.text(0.5, 0.86, title, ha="center", va="center", color="white", fontsize=14, weight="bold")
        for yy, k, v in [(0.58, "example", ex), (0.37, "features", feat), (0.16, "label", lab)]:
            ax.text(0.07, yy, k, fontsize=11, color=MUTED, va="center")
            ax.text(0.33, yy, v, fontsize=11.5, color=INK, va="center", weight="bold" if k == "label" else "normal")
    fig.suptitle("You already use machine learning every day - always the same three parts", fontsize=16,
                 weight="bold")
    L.save(fig, "ml_everywhere")

# ---------------------------------------------------------------- 7. real SMS as two numbers
import csv
with open(data("08_SpamClassifier", "sms_spam.csv"), encoding="utf-8") as f:
    sms = list(csv.DictReader(f))
sms_len = np.array([len(r["text"]) for r in sms])
sms_dig = np.array([sum(ch.isdigit() for ch in r["text"]) for r in sms])
sms_y = np.array([r["label"] == "spam" for r in sms], int)

if L.wanted("sms_two_features"):
    fig, ax = plt.subplots(figsize=(11, 6.5))
    jit = np.random.default_rng(0)
    for lab, col, name in [(0, BLUE, "ham (normal)"), (1, ORANGE, "spam")]:
        m = sms_y == lab
        ax.scatter(np.minimum(sms_len[m], 300), sms_dig[m] + jit.uniform(-0.3, 0.3, m.sum()), s=10, alpha=0.45,
                   color=col, label=f"{name}: {m.sum():,} SMS")
    ax.set_xlabel("feature 1: length of the SMS (characters, cut at 300)")
    ax.set_ylabel("feature 2: how many digits it contains")
    ax.set_ylim(-1, 50)
    ax.set_title(f"All {len(sms):,} real SMS from Laith's data, each turned into just two numbers")
    ax.annotate("spam lives here:\nlong, full of phone numbers\nand prices", (150, 25), xytext=(210, 38), fontsize=12,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.annotate("ham lives here:\nshort, few digits", (40, 1), xytext=(60, 14), fontsize=12,
                arrowprops=dict(arrowstyle="->", color=INK))
    ax.legend(loc="upper left", markerscale=3)
    caption(fig, "Two simple numbers already separate most spam from ham. The model's job: find the best border.")
    L.save(fig, "sms_two_features")

# ---------------------------------------------------------------- 8. more examples -> better model (real SMS)
if L.wanted("learning_curve"):
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.model_selection import train_test_split
    texts = np.array([r["text"] for r in sms])
    tr_x, te_x, tr_y, te_y = train_test_split(texts, sms_y, test_size=0.3, stratify=sms_y, random_state=0)
    sizes = [10, 20, 50, 100, 200, 500, 1000, 2000, len(tr_x)]
    acc = []
    for n in sizes:
        scores = []
        for seed in range(5):
            idx = np.random.default_rng(seed).choice(len(tr_x), n, replace=False)
            if len(set(tr_y[idx])) < 2:
                idx[0] = np.flatnonzero(tr_y == 1)[0]
            vec = CountVectorizer().fit(tr_x[idx])
            model = MultinomialNB().fit(vec.transform(tr_x[idx]), tr_y[idx])
            scores.append((model.predict(vec.transform(te_x)) == te_y).mean())
        acc.append(np.mean(scores) * 100)
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(sizes, acc, "o-", color=AQUA, lw=3, ms=9)
    for n, a in zip(sizes, acc):
        ax.annotate(f"{a:.0f}%", (n, a), xytext=(0, 10), textcoords="offset points", ha="center", fontsize=11)
    ax.axhline(100 * (1 - sms_y.mean()), color=MUTED, ls="--")
    ax.text(12, 100 * (1 - sms_y.mean()) - 2.2, "a lazy program that always says 'ham' already gets 87%", color=INK2)
    ax.set_xscale("log")
    ax.set_xticks(sizes)
    ax.set_xticklabels([f"{s:,}" for s in sizes])
    ax.set_ylim(70, 101)
    ax.set_xlabel("how many labelled SMS the model studied (log scale)")
    ax.set_ylabel("% right on 1,672 NEW SMS")
    ax.set_title("More examples -> a better model (the same simple spam model, real data)")
    caption(fig, "Each dot: a model trained on that many SMS, graded on SMS it never saw (average of 5 tries).")
    L.save(fig, "learning_curve")
    print("   learning curve:", [f"{n}:{a:.1f}" for n, a in zip(sizes, acc)])

# ---------------------------------------------------------------- 9. memorise vs. understand
if L.wanted("memorise_vs_learn"):
    fig, ax = plt.subplots(figsize=(10, 5))
    xs = np.arange(2)
    ax.bar(xs - 0.18, [100, 85], 0.34, color=BLUE, label="last year's exam (already seen)")
    ax.bar(xs + 0.18, [40, 82], 0.34, color=ORANGE, label="this year's exam (NEW questions)")
    for x0, v in zip([-0.18, 0.82, 0.18, 1.18], [100, 85, 40, 82]):
        ax.text(x0, v + 2, str(v), ha="center", fontsize=14, weight="bold")
    ax.set_xticks(xs)
    ax.set_xticklabels(["Dana: memorised the answers\n(= OVERFITTING)", "Her friend: learned the methods\n(= GENERALISING)"])
    ax.set_ylim(0, 115)
    ax.set_ylabel("grade")
    ax.legend(loc="upper right")
    ax.set_title("Only the orange bars tell you who really learned")
    L.save(fig, "memorise_vs_learn")

# ---------------------------------------------------------------- 10. dealing the three piles (stratified)
if L.wanted("deal_piles"):
    deck_rng = np.random.default_rng(11)
    cards = np.array([1] * 6 + [0] * 34)           # 40 SMS, 6 spam (15 %)
    deck_rng.shuffle(cards)
    # stratified: deal spam and ham separately, 70 / 15 / 15
    piles = {0: [], 1: [], 2: []}
    target = []
    for lab in (1, 0):
        idx = [i for i in range(len(cards)) if cards[i] == lab]
        n = len(idx)
        cut = [round(0.7 * n), round(0.85 * n)]
        for j, i in enumerate(idx):
            target.append((i, 0 if j < cut[0] else (1 if j < cut[1] else 2)))
    target.sort(key=lambda t: t[0])
    names = ["TRAINING (70%)", "VALIDATION (15%)", "TEST (15%)"]
    cols = [BLUE, AQUA, ORANGE]

    def draw_deal(ax, k):
        blank(ax, (0, 10), (0, 6))
        for p, (nm, c) in enumerate(zip(names, cols)):
            x0 = [0.2, 5.95, 8.0][p]
            w = [5.5, 1.85, 1.85][p]
            ax.add_patch(FancyBboxPatch((x0, 0.2), w, 2.6, boxstyle="round,pad=0,rounding_size=0.15", lw=2.5,
                                        edgecolor=c, facecolor=PAPER))
            ax.text(x0 + w / 2, 3.05, nm, ha="center", fontsize=12, weight="bold", color=c)
        counts = [[0, 0], [0, 0], [0, 0]]
        for step, (i, p) in enumerate(target):
            lab = cards[i]
            if step < k:
                x0 = [0.2, 5.95, 8.0][p]
                per_row = [10, 3, 3][p]
                n = sum(counts[p])
                ax.add_patch(plt.Rectangle((x0 + 0.15 + (n % per_row) * 0.53, 2.2 - (n // per_row) * 0.62), 0.45, 0.52,
                                           color=ORANGE if lab else BLUE))
                counts[p][lab] += 1
            else:
                ax.add_patch(plt.Rectangle((0.3 + i * 0.235, 4.4), 0.2, 0.9, color=ORANGE if lab else BLUE))
        ax.text(5, 5.6, "40 SMS (6 spam = orange) waiting to be dealt", ha="center", fontsize=12, color=INK2)
        for p in range(3):
            x0 = [0.2, 5.95, 8.0][p]
            w = [5.5, 1.85, 1.85][p]
            tot = sum(counts[p])
            if tot:
                ax.text(x0 + w / 2, -0.25, f"{counts[p][1]} spam / {tot}", ha="center", fontsize=11, color=INK2)

    fig, ax = plt.subplots(figsize=(12, 5))
    frames = list(range(0, len(target) + 1)) + [len(target)] * 5
    L.animate(fig, lambda i: draw_deal(ax, frames[i]), len(frames), "deal_piles", fps=5)

# ---------------------------------------------------------------- 11. learning = trying rules, keeping the best
def draw_cut(ax1, ax2, t_show, upto=None):
    ts = np.arange(1, 21)
    accs = np.array([((sms_dig >= t) == (sms_y == 1)).mean() * 100 for t in ts])
    ax1.clear()
    bins = np.arange(0, 41)
    ax1.hist(np.minimum(sms_dig[sms_y == 0], 40), bins, color=BLUE, alpha=0.75, label="ham")
    ax1.hist(np.minimum(sms_dig[sms_y == 1], 40), bins, color=ORANGE, alpha=0.75, label="spam")
    ax1.set_yscale("log")
    ax1.axvline(t_show, color=INK, lw=2.5)
    ax1.text(t_show + 0.4, 2500, f"rule: digits >= {t_show}\n-> spam", fontsize=12)
    ax1.set_xlabel("number of digits in the SMS")
    ax1.set_ylabel("how many SMS (log scale)")
    ax1.set_title("where do I cut?")
    ax1.legend(loc="center right")
    ax2.clear()
    k = int(t_show) - 1
    u = k if upto is None else upto - 1
    ax2.plot(ts[: u + 1], accs[: u + 1], "o-", color=AQUA, ms=8)
    ax2.plot(ts[k], accs[k], "o", ms=14, mfc="none", mec=INK, mew=2)
    ax2.set_xlim(0, 21)
    ax2.set_ylim(84, 99)
    ax2.set_xticks(range(0, 21, 2))
    best = int(np.argmax(accs))
    if u >= best:
        ax2.plot(ts[best], accs[best], "*", ms=22, color=ORANGE)
        ax2.annotate(f"best: digits >= {ts[best]}  ->  {accs[best]:.1f}% right", (ts[best], accs[best]),
                     xytext=(7, 88), fontsize=12, arrowprops=dict(arrowstyle="->", color=INK))
    ax2.set_xlabel("the cut-off the computer tries")
    ax2.set_ylabel("% of the 5,574 SMS right")
    ax2.set_title(f"cut-off {t_show}: {accs[k]:.1f}% right")


if L.wanted("best_cut"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.2))
    tlist = list(range(1, 21)) + [20] * 4
    L.animate(fig, lambda i: draw_cut(a1, a2, tlist[i]), len(tlist), "best_cut", fps=2)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.2))
    draw_cut(a1, a2, 5, upto=20)
    caption(fig, "'Learning' in its smallest form: try every rule of one shape, measure each on the examples, keep the best.")
    L.save(fig, "best_cut")

# ---------------------------------------------------------------- live
if L.live:
    from matplotlib.widgets import Slider
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5.5))
    fig.subplots_adjust(bottom=0.2)
    s = Slider(fig.add_axes([0.2, 0.05, 0.6, 0.04]), "degree", 0, 15, valinit=1, valstep=1)
    s.on_changed(lambda v: (draw_overfit(a1, a2, int(v)), fig.canvas.draw_idle()))
    draw_overfit(a1, a2, 1)
    plt.show()
