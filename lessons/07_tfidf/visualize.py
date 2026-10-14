"""Lesson 07 - bag of words and TF-IDF, built step by step on a tiny example and on the real CVs."""
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

docs = {"CV 1": "python python sql docker", "CV 2": "java sql spring", "CV 3": "python sql pandas"}
terms = ["python", "sql", "docker", "java", "spring", "pandas"]
names = list(docs)
C = np.array([[d.split().count(t) for t in terms] for d in docs.values()], float)
N = len(docs)
df = (C > 0).sum(0)
idf = np.log((1 + N) / (1 + df)) + 1           # ResumeMatch's smoothed IDF
T = C * idf
U = T / np.linalg.norm(T, axis=1, keepdims=True)


def heat(ax, M, rows, cols, title, fmt="{:.0f}", cmap="Blues", highlight_cols=None, vmax=None):
    ax.clear()
    ax.imshow(M, cmap=cmap, vmin=0, vmax=vmax or max(M.max(), 1e-9), aspect="auto")
    ax.grid(False)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            ax.text(j, i, fmt.format(v), ha="center", va="center", fontsize=13,
                    color="white" if v > (vmax or M.max()) * 0.6 else INK)
    ax.set_xticks(range(len(cols)), cols)
    ax.set_yticks(range(len(rows)), rows)
    ax.set_title(title)
    if highlight_cols is not None:
        for j in highlight_cols:
            ax.add_patch(plt.Rectangle((j - 0.5, -0.5), 1, M.shape[0], fill=False, ec=ORANGE, lw=3))


# ---------------------------------------------------------------- 1. bag of words
if L.wanted("bag_of_words"):
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(14, 4), gridspec_kw={"width_ratios": [0.8, 1.2]})
    blank(a0)
    for i, (n, d) in enumerate(docs.items()):
        a0.text(0.02, 0.8 - i * 0.3, f"{n}:  “{d}”", fontsize=14, family="monospace")
    a0.set_title("three tiny CVs (already preprocessed)")
    heat(a1, C, names, terms, "bag of words: count every term")
    caption(fig, "Each CV becomes a row of numbers.  The order of the words is forgotten — hence 'bag'.")
    L.save(fig, "bag_of_words")

# ---------------------------------------------------------------- 2. TF-IDF, step by step
if L.wanted("tfidf_build"):
    fig = plt.figure(figsize=(14, 6.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1.2])
    ax, axi = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    steps = [
        ("1. count the terms in each CV (tf)", C, "{:.0f}", None),
        ("2. df = in how many CVs does each term appear?", C, "{:.0f}", "df"),
        ("3. idf = ln((1+N)/(1+df)) + 1   — rare terms get MORE weight", C, "{:.0f}", "idf"),
        ("4. tf × idf   — 'python' twice in CV 1, and rarer than 'sql'", T, "{:.2f}", "idf"),
        ("5. divide each row by its length (L2) — every CV now has length 1", U, "{:.2f}", "idf"),
    ]
    frames = [i for i in range(len(steps)) for _ in range(3)]

    def upd(k):
        title, M, fmt, extra = steps[frames[k]]
        heat(ax, M, names, terms, title, fmt=fmt, cmap="Oranges" if M is not C else "Blues")
        axi.clear()
        axi.axis("off")
        if extra:
            row = df if extra == "df" else idf
            label = "df" if extra == "df" else "idf"
            axi.set_xlim(-0.5, len(terms) - 0.5)
            axi.set_ylim(0, 1)
            for j, v in enumerate(row):
                axi.text(j, 0.5, f"{label} = {v:.0f}" if extra == "df" else f"{label} = {v:.3f}",
                         ha="center", va="center", fontsize=13,
                         bbox=dict(boxstyle="round", fc=LIGHT_ORANGE if extra == "idf" else LIGHT_BLUE, ec="none"))
    L.animate(fig, upd, len(frames), "tfidf_build", fps=1)
    fig = plt.figure(figsize=(14, 6.2))
    gs = fig.add_gridspec(2, 1, height_ratios=[3, 1.2])
    ax, axi = fig.add_subplot(gs[0]), fig.add_subplot(gs[1])
    upd(len(frames) - 1)
    L.save(fig, "tfidf_final")

# ---------------------------------------------------------------- 3. the IDF curve
if L.wanted("idf_curve"):
    Nc = 200
    d = np.arange(1, Nc + 1)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(d, np.log(Nc / d), color=MUTED, ls="--", label="plain:  ln(N / df)")
    ax.plot(d, np.log((1 + Nc) / (1 + d)) + 1, color=BLUE, label="ResumeMatch:  ln((1+N)/(1+df)) + 1")
    ax.plot(d, np.log(Nc / (1 + d)) + 1, color=ORANGE, label="SpamClassifier:  ln(N/(1+df)) + 1")
    for word, dfv in [("kubernetes", 5), ("python", 60), ("experience", 190)]:
        v = math.log((1 + Nc) / (1 + dfv)) + 1
        ax.plot(dfv, v, "o", color=INK, ms=8)
        ax.annotate(f"{word}  (df={dfv})", (dfv, v), xytext=(dfv + 8, v + 0.35), fontsize=12)
    ax.set_xlabel("df = number of documents containing the term   (N = 200 CVs)")
    ax.set_ylabel("idf weight")
    ax.set_title("Rare terms get a big weight; a term in every document gets the minimum")
    ax.legend()
    L.save(fig, "idf_curve")

# ---------------------------------------------------------------- 4. real CVs: count vs tf-idf
from nltk.corpus import stopwords
STOP = set(stopwords.words("english")) | {"and", "the", "of", "in", "to", "a", "with", "for", "on", "as", "an", "at", "by", "is", "it", "from",
        "new", "led", "used", "using", "wrote", "years", "experience", "team", "work", "worked", "responsible",
        "involving", "built", "completed", "applied", "personal", "project", "online", "course", "members",
        "trained", "documentation", "migration", "legacy", "component", "code", "reviews", "email", "phone"}
if L.wanted("real_cv"):
    with open(data("31_ResumeMatch", "resumes.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    tok = [[w for w in re.findall(r"[a-z][a-z+#.]*[a-z+#]|[a-z]", r["text"].lower()) if w not in STOP]
           for r in rows]
    Nr = len(tok)
    dfr = Counter(t for doc in tok for t in set(doc))
    i = 1
    cnt = Counter(tok[i])
    raw = cnt.most_common(8)
    weights = {t: c * (math.log((1 + Nr) / (1 + dfr[t])) + 1) for t, c in cnt.items()}
    best = sorted(weights.items(), key=lambda kv: -kv[1])[:8]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5))
    a1.barh(range(8)[::-1], [c for _, c in raw], color=BLUE)
    a1.set_yticks(range(8)[::-1], [f"{t}  (in {dfr[t]} CVs)" for t, _ in raw])
    a1.set_title("raw counts: the words this CV repeats")
    a2.barh(range(8)[::-1], [w for _, w in best], color=ORANGE)
    a2.set_yticks(range(8)[::-1], [f"{t}  (in {dfr[t]} CVs)" for t, _ in best])
    a2.set_title("tf × idf: the words that make it DIFFERENT")
    caption(fig, f"CV {rows[i]['id']} ({rows[i]['role']}) among the project's {Nr} CVs.  Rare skills rise - and so does "
                 "the candidate's NAME: that is why ResumeMatch scrubs personal data first.")
    L.save(fig, "real_cv")
