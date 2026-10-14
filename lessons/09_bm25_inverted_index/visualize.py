"""Lesson 09 - BM25 (saturation, length normalisation, its IDF) and the inverted index."""
import csv
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
K1, B = 1.5, 0.75                    # ResumeMatch config.py


def sat(tf, k1):
    return tf * (k1 + 1) / (tf + k1)


# ---------------------------------------------------------------- 1. saturation, k1 sweeping
k1s = np.r_[np.linspace(0.2, 5, 25), np.linspace(5, 0.2, 25)]


def draw_sat(ax, k1):
    ax.clear()
    tf = np.linspace(0, 20, 200)
    ax.plot(tf, tf / 1.0, color=MUTED, ls="--", label="TF-IDF: linear in tf")
    ax.plot(tf, sat(tf, K1), color=BLUE, lw=1.5, alpha=0.6, label=f"BM25, k1 = {K1} (project)")
    ax.plot(tf, sat(tf, k1), color=ORANGE, lw=3.5, label=f"BM25, k1 = {k1:.2f}")
    ax.axhline(k1 + 1, color=ORANGE, ls=":", lw=1.5)
    ax.text(20.3, k1 + 1, f"ceiling\nk1+1 = {k1 + 1:.2f}", va="center", fontsize=11, color=ORANGE)
    for t in (1, 2, 5, 20):
        ax.plot(t, sat(t, k1), "o", color=ORANGE, ms=7)
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 7)
    ax.set_xlabel("tf = how many times the term is in the CV")
    ax.set_ylabel("how much it adds (× idf)")
    ax.set_title("Saturation: the 1st mention says a lot, the 20th almost nothing")
    ax.legend(loc="upper left")


if L.wanted("saturation"):
    fig, ax = plt.subplots(figsize=(12, 5.4))
    L.animate(fig, lambda k: draw_sat(ax, k1s[k]), len(k1s), "saturation", fps=6)

# ---------------------------------------------------------------- 2. the b knob
if L.wanted("length_b"):
    fig, ax = plt.subplots(figsize=(12, 5))
    ratio = np.linspace(0.2, 4, 200)
    for b, col in [(0, MUTED), (0.5, AQUA), (0.75, ORANGE), (1.0, VIOLET)]:
        tfp = 2 * (K1 + 1) / (2 + K1 * (1 - b + b * ratio))
        ax.plot(ratio, tfp, color=col, lw=3 if b == 0.75 else 2,
                label=f"b = {b}" + ("   (project)" if b == 0.75 else "   (length ignored)" if b == 0 else ""))
    ax.axvline(1, color=INK, lw=1)
    ax.text(1.03, 2.05, "average length", fontsize=11)
    ax.set_xlabel("|d| / avgdl   (this CV's length ÷ the average CV length)")
    ax.set_ylabel("contribution of a term with tf = 2")
    ax.set_title("Length normalisation: the same 2 mentions count less in a long CV")
    ax.legend()
    L.save(fig, "length_b")

# ---------------------------------------------------------------- 3. BM25's idf
if L.wanted("bm25_idf"):
    N = 200
    df = np.arange(1, N + 1)
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.plot(df, np.log((N - df + 0.5) / (df + 0.5)), color=RED, ls="--", label="without +1:  ln((N−df+0.5)/(df+0.5))")
    ax.plot(df, np.log((N - df + 0.5) / (df + 0.5) + 1), color=ORANGE, lw=3,
            label="ResumeMatch:  ln((N−df+0.5)/(df+0.5) + 1)")
    ax.axhline(0, color=INK, lw=1)
    ax.axvspan(N / 2, N, color=RED, alpha=0.07)
    ax.text(150, -1.5, "a word in more than half\nthe CVs would SUBTRACT", ha="center", color=RED, fontsize=12)
    ax.set_xlabel("df   (N = 200 CVs)")
    ax.set_ylabel("idf")
    ax.set_title("BM25 has its own IDF — the +1 keeps it positive")
    ax.legend()
    L.save(fig, "bm25_idf")

# ---------------------------------------------------------------- 4. inverted index animation
docs = {0: "python django rest", 1: "java spring sql", 2: "python pandas sql", 3: "react css html",
        4: "python django docker", 5: "java kotlin android"}
index = defaultdict(list)
for i, d in docs.items():
    for t, c in Counter(d.split()).items():
        index[t].append((i, c))
query = ["python", "django"]
terms_shown = ["python", "django", "java", "sql", "spring", "pandas", "react", "docker"]


def draw_index(ax, step):
    blank(ax)
    ax.text(0.02, 0.95, "inverted index:  term → [(CV, tf), …]", fontsize=14, weight="bold")
    ax.text(0.68, 0.95, "scores for job: “python django”", fontsize=14, weight="bold")
    touched = set()
    scores = defaultdict(float)
    walked = query[:step]
    for t in walked:
        for i, c in index[t]:
            touched.add(i)
            scores[i] += 1.0                      # same weight per hit, for the picture
    for r, t in enumerate(terms_shown):
        y = 0.84 - r * 0.1
        active = t in walked
        box(ax, 0.02, y, 0.12, 0.07, t, color=ORANGE if active else MUTED,
            fill=LIGHT_ORANGE if active else PAPER, fontsize=12, weight="bold" if active else "normal")
        for k, (i, c) in enumerate(index[t]):
            box(ax, 0.17 + k * 0.12, y, 0.1, 0.07, f"CV{i}, tf={c}", color=ORANGE if active else GRID,
                fill=LIGHT_ORANGE if active else PAPER, fontsize=10.5)
    for r, i in enumerate(docs):
        y = 0.84 - r * 0.12
        hit = i in touched
        box(ax, 0.68, y, 0.09, 0.08, f"CV{i}", color=BLUE if hit else GRID, fill=LIGHT_BLUE if hit else PAPER,
            fontsize=12)
        ax.text(0.79, y + 0.04, f"{scores[i]:.0f} hit(s)" if hit else "never touched", va="center",
                fontsize=12, color=INK if hit else MUTED)
    ax.text(0.68, 0.06, f"documents looked at: {len(touched)} of {len(docs)}", fontsize=13, weight="bold")


if L.wanted("inverted_index"):
    fig, ax = plt.subplots(figsize=(14, 6.2))
    frames = [0, 0, 1, 1, 1, 2, 2, 2, 2, 2]
    L.animate(fig, lambda k: draw_index(ax, frames[k]), len(frames), "inverted_index", fps=1)
    fig, ax = plt.subplots(figsize=(14, 6.2))
    draw_index(ax, 2)
    L.save(fig, "inverted_index_final")

# ---------------------------------------------------------------- 5. the b = 0 experiment on the real CVs
STOP = {"and", "the", "of", "in", "to", "a", "with", "for", "on", "as", "an", "at", "by", "is", "it", "i", "we",
        "you", "our", "are", "be", "will", "my", "that", "this", "from", "have", "has", "was"}
if L.wanted("b_experiment"):
    with open(data("31_ResumeMatch", "resumes.csv"), encoding="utf-8") as f:
        res = list(csv.DictReader(f))
    with open(data("31_ResumeMatch", "jobs.csv"), encoding="utf-8") as f:
        jobs = list(csv.DictReader(f))
    tok = lambda s: [w for w in re.findall(r"[a-z][a-z+#.]*[a-z+#]|[a-z]", s.lower()) if w not in STOP]
    D = [Counter(tok(r["text"])) for r in res]
    lens = np.array([sum(d.values()) for d in D])
    avg = lens.mean()
    N = len(D)
    dfc = Counter(t for d in D for t in d)

    def bm25(q, b):
        s = np.zeros(N)
        for t in set(tok(q)):
            if t not in dfc:
                continue
            idf = math.log((N - dfc[t] + 0.5) / (dfc[t] + 0.5) + 1)
            for i, d in enumerate(D):
                if t in d:
                    s[i] += idf * d[t] * (K1 + 1) / (d[t] + K1 * (1 - b + b * lens[i] / avg))
        return s

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5))
    bs = [0.0, 0.25, 0.5, 0.75, 1.0]
    toplen = [np.mean([lens[np.argsort(-bm25(j["text"], b))[:10]].mean() for j in jobs]) for b in bs]
    p10 = [np.mean([np.mean([res[i]["id"] in set(j["relevant_ids"].split())
                             for i in np.argsort(-bm25(j["text"], b))[:10]]) for j in jobs]) for b in bs]
    a1.plot(bs, toplen, "o-", color=ORANGE, ms=9)
    a1.axhline(avg, color=MUTED, ls="--")
    a1.text(0.02, avg + 3, f"average CV length = {avg:.0f} terms", color=INK2)
    a1.set_xlabel("b")
    a1.set_ylabel("mean length of the top-10 CVs")
    a1.set_title("b = 0: long CVs flood the top")
    a2.plot(bs, p10, "o-", color=GREEN, ms=9)
    a2.set_ylim(0, 1)
    a2.set_xlabel("b")
    a2.set_ylabel("mean P@10 over the 5 jobs")
    a2.set_title("…while P@10 hardly moves on this data")
    print("  b:", bs, " top-10 length:", np.round(toplen, 1), " P@10:", np.round(p10, 3))
    caption(fig, "The project's 200 CVs and 5 jobs, k1 = 1.5.  Kosai's 'b = 0' experiment: report BOTH charts - an honest result.")
    L.save(fig, "b_experiment")

if L.live:
    from matplotlib.widgets import Slider
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.subplots_adjust(bottom=0.2)
    s = Slider(fig.add_axes([0.2, 0.05, 0.6, 0.04]), "k1", 0.1, 5, valinit=K1)
    s.on_changed(lambda v: (draw_sat(ax, v), fig.canvas.draw_idle()))
    draw_sat(ax, K1)
    plt.show()
