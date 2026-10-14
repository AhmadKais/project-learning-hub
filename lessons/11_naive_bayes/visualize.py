"""Lesson 11 - Bayes' theorem and Multinomial Naive Bayes, from scratch, on the real SMS data."""
import csv
import math
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
from nltk.corpus import stopwords

STOP = set(stopwords.words("english"))
URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)


def tokens(text):
    text = URL_RE.sub(" URLTOKEN ", text)
    out = []
    for w in re.findall(r"URLTOKEN|[A-Za-z']+", text):
        if w == "URLTOKEN":
            out.append(w)
        else:
            w = w.lower()
            if len(w) >= 3 and w not in STOP:
                out.append(w)
    return out


with open(data("08_SpamClassifier", "sms_spam.csv"), encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
docs = [tokens(r["text"]) for r in rows]
labels = [r["label"] for r in rows]


class NB:
    """The same Multinomial Naive Bayes as Laith's stage 4 (alpha = 1, log space)."""

    def __init__(self, alpha=1.0):
        self.alpha = alpha

    def fit(self, docs, labels):
        self.vocab = sorted({t for d in docs for t in d})
        V = len(self.vocab)
        self.log_prior, self.loglik = {}, {}
        for c in ("ham", "spam"):
            dc = [d for d, y in zip(docs, labels) if y == c]
            self.log_prior[c] = math.log(len(dc) / len(docs))
            cnt = Counter(t for d in dc for t in d)
            total = sum(cnt.values())
            self.loglik[c] = {w: math.log((cnt[w] + self.alpha) / (total + self.alpha * V)) for w in self.vocab}
        return self

    def scores(self, toks):
        return {c: self.log_prior[c] + sum(self.loglik[c][t] for t in toks if t in self.loglik[c])
                for c in ("ham", "spam")}

    def proba(self, toks):
        s = self.scores(toks)
        d = s["ham"] - s["spam"]
        return 0.0 if d > 700 else 1.0 if d < -700 else 1 / (1 + math.exp(d))

    def log_odds(self, t):
        return self.loglik["spam"][t] - self.loglik["ham"][t] if t in self.loglik["spam"] else 0.0


nb = NB().fit(docs, labels)

# ---------------------------------------------------------------- 1. Bayes with real counts: the square
n = len(labels)
n_spam = labels.count("spam")
has_free = ["free" in d for d in docs]
a = sum(h and y == "spam" for h, y in zip(has_free, labels))     # spam with "free"
b = sum(h and y == "ham" for h, y in zip(has_free, labels))      # ham with "free"
ps = n_spam / n
pf_s = a / n_spam
pf_h = b / (n - n_spam)


def draw_square(ax, step):
    blank(ax, (0, 1), (0, 1.12))
    ax.set_aspect("equal")
    w = ps
    ax.add_patch(plt.Rectangle((0, 0), w, 1, color=LIGHT_ORANGE, ec=ORANGE, lw=2))
    ax.add_patch(plt.Rectangle((w, 0), 1 - w, 1, color=LIGHT_BLUE, ec=BLUE, lw=2))
    ax.text(w / 2, 1.04, f"spam\n{ps:.1%}", ha="center", fontsize=11, color=ORANGE)
    ax.text(w + (1 - w) / 2, 1.04, f"ham {1 - ps:.1%}", ha="center", fontsize=12, color=BLUE)
    msgs = ["All 5,574 messages. Width = how common each class is (the PRIOR).",
            f"Shade the messages that contain “free”:  {pf_s:.1%} of spam,  {pf_h:.2%} of ham  (the LIKELIHOOD).",
            "We KNOW the new message contains “free”: only the shaded areas are possible now.",
            f"P(spam | free) = orange area / all shaded = {a} / ({a} + {b}) = {a / (a + b):.2f}   (the POSTERIOR)"]
    if step >= 1:
        ax.add_patch(plt.Rectangle((0, 0), w, pf_s, color=ORANGE, alpha=0.9))
        ax.add_patch(plt.Rectangle((w, 0), 1 - w, max(pf_h, 0.006), color=BLUE, alpha=0.9))
        ax.text(w / 2, pf_s / 2, f"{a}", ha="center", va="center", color="white", fontsize=14, weight="bold")
        ax.text(w + 0.05, 0.02, f"{b}", ha="left", va="bottom", color=BLUE, fontsize=14, weight="bold")
    if step >= 2:
        ax.add_patch(plt.Rectangle((0, pf_s), w, 1 - pf_s, color=PAPER, alpha=0.85))
        ax.add_patch(plt.Rectangle((w, max(pf_h, 0.006)), 1 - w, 1 - pf_h, color=PAPER, alpha=0.85))
    ax.set_title(msgs[step], fontsize=12.5)


if L.wanted("bayes_square"):
    fig, ax = plt.subplots(figsize=(11, 7.4))
    frames = [0, 0, 1, 1, 1, 2, 2, 3, 3, 3, 3]
    L.animate(fig, lambda k: draw_square(ax, frames[k]), len(frames), "bayes_square", fps=1)

# ---------------------------------------------------------------- 2. word by word: the log-score race
msg = "URGENT! You have won a free prize. Call now to claim your cash award"
toks = tokens(msg)


def draw_race(a1, a2, k):
    seen = toks[:k]
    s = {c: nb.log_prior[c] + sum(nb.loglik[c][t] for t in seen if t in nb.loglik[c]) for c in ("ham", "spam")}
    a1.clear()
    a1.barh([1, 0], [s["ham"], s["spam"]], color=[BLUE, ORANGE], height=0.5)
    a1.set_yticks([1, 0], ["log score HAM", "log score SPAM"])
    a1.set_xlim(-110, 0)
    for y, c in [(1, "ham"), (0, "spam")]:
        a1.text(s[c] + 1, y, f"{s[c]:.1f}", ha="left", va="center", color="white", fontsize=13, weight="bold")
    p = nb.proba(seen)
    a1.set_title(f"after {k} word(s):  spam − ham = {s['spam'] - s['ham']:+.1f}   →   P(spam) = {p:.4f}")
    a1.set_xlabel("log probability (closer to 0 = more likely)")
    a2.clear()
    lo = [nb.log_odds(t) for t in toks]
    a2.bar(range(len(toks)), lo, color=[(ORANGE if v > 0 else BLUE) if i < k else GRID for i, v in enumerate(lo)])
    a2.set_xticks(range(len(toks)), toks, rotation=40, ha="right")
    a2.axhline(0, color=INK, lw=1)
    a2.set_ylabel("log-odds of the word")
    a2.set_title("each word's vote:  log P(w|spam) − log P(w|ham)")


if L.wanted("word_race"):
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(12, 8), gridspec_kw={"height_ratios": [1, 1.2]})
    fig.subplots_adjust(hspace=0.55)
    frames = list(range(len(toks) + 1)) + [len(toks)] * 3
    L.animate(fig, lambda f: draw_race(a1, a2, frames[f]), len(frames), "word_race", fps=1)

# ---------------------------------------------------------------- 3. the most telling words
if L.wanted("log_odds"):
    cnt_all = Counter(t for d in docs for t in d)
    common = [t for t, c in cnt_all.items() if c >= 8]
    ranked = sorted(common, key=nb.log_odds)
    ham_w, spam_w = ranked[:12], ranked[-12:]
    fig, ax = plt.subplots(figsize=(12, 7))
    words = ham_w + spam_w
    vals = [nb.log_odds(t) for t in words]
    ax.barh(range(len(words)), vals, color=[BLUE if v < 0 else ORANGE for v in vals])
    ax.set_yticks(range(len(words)), words)
    ax.axvline(0, color=INK, lw=1)
    ax.set_xlabel("log-odds   (> 0 pushes to spam,  < 0 pushes to ham)")
    ax.set_title("What the model learned: the strongest words (seen ≥ 8 times)")
    L.save(fig, "log_odds")

# ---------------------------------------------------------------- 4. underflow
if L.wanted("underflow"):
    ns = np.arange(1, 401)
    prod = np.array([0.001 ** k for k in ns])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.6))
    a1.semilogy(ns, np.where(prod > 0, prod, np.nan), color=ORANGE)
    z = int(np.argmax(prod == 0))
    a1.axvline(ns[z], color=RED, ls="--")
    a1.text(ns[z] + 5, 1e-200, f"from {ns[z]} words on:\nexactly 0.0", color=RED, fontsize=12)
    a1.set_xlabel("number of words")
    a1.set_title("product of probabilities (0.001 each)")
    a2.plot(ns, ns * math.log(0.001), color=GREEN)
    a2.set_xlabel("number of words")
    a2.set_title("sum of logs: fine forever")
    caption(fig, "A float cannot hold anything below ~1e-308.  Multiplying hundreds of small probabilities hits 0.0;  "
                 "adding their logs never does.")
    L.save(fig, "underflow")

# ---------------------------------------------------------------- 5. smoothing
if L.wanted("smoothing"):
    toy = [["free", "money", "now"], ["free", "prize", "winner"], ["meeting", "tomorrow", "office"],
           ["project", "meeting", "notes"]]
    ty = ["spam", "spam", "ham", "ham"]
    words = ["free", "money", "meeting", "notes"]
    fig, axes = plt.subplots(1, 2, figsize=(14, 4.6), sharey=True)
    for ax, alpha, title in [(axes[0], 0.0, "no smoothing (alpha = 0)"), (axes[1], 1.0, "Laplace smoothing (alpha = 1)")]:
        V = 10
        res = []
        for w in words:
            ps_ = (sum(d.count(w) for d, y in zip(toy, ty) if y == "spam") + alpha) / (6 + alpha * V)
            ph_ = (sum(d.count(w) for d, y in zip(toy, ty) if y == "ham") + alpha) / (6 + alpha * V)
            res.append((ps_, ph_))
        x = np.arange(len(words))
        ax.bar(x - 0.2, [r[0] for r in res], 0.4, color=ORANGE, label="P(w | spam)")
        ax.bar(x + 0.2, [r[1] for r in res], 0.4, color=BLUE, label="P(w | ham)")
        for i, (p1, p2) in enumerate(res):
            for dx, p in [(-0.2, p1), (0.2, p2)]:
                ax.text(i + dx, p + 0.01, "0 !" if p == 0 else f"{p:.3f}", ha="center", fontsize=11,
                        color=RED if p == 0 else INK)
        ax.set_xticks(x, words)
        ax.set_title(title)
        ax.legend(loc="upper right", fontsize=10)
    caption(fig, "The 4-message worked example.  Without smoothing, one unseen word multiplies a class by ZERO "
                 "- whatever else the message says.")
    L.save(fig, "smoothing")

print(f"  'free': {a} spam + {b} ham messages; P(spam|free) = {a / (a + b):.3f}; prior spam {ps:.3f}")
print(f"  race message tokens: {toks};  P(spam) = {nb.proba(toks):.6f}")
