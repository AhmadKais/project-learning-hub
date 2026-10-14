"""Lesson 10 - measuring a ranking: precision@k and (mean) reciprocal rank, then TF-IDF vs BM25 on real data."""
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


def p_at_k(ranking, relevant, k):
    return sum(c in relevant for c in ranking[:k]) / k


def rr(ranking, relevant):
    for pos, c in enumerate(ranking, start=1):
        if c in relevant:
            return 1 / pos
    return 0.0


def draw_list(ax, ranking, relevant, k=None, title="", x0=0.05, show_rr=True):
    first = next((i for i, c in enumerate(ranking) if c in relevant), None)
    for i, c in enumerate(ranking):
        y = 0.86 - i * 0.085
        hit = c in relevant
        inside = k is not None and i < k
        box(ax, x0, y, 0.22, 0.07, f"{i + 1}.  {c}", color=GREEN if hit else MUTED,
            fill="#d5ecd5" if hit else PAPER, fontsize=12, lw=3 if inside else 1.2)
        if show_rr and i == first:
            ax.text(x0 + 0.24, y + 0.035, f"← first relevant: RR = 1/{i + 1} = {1 / (i + 1):.2f}", va="center",
                    fontsize=12, color=GREEN)
    if k is not None:
        ax.plot([x0 - 0.02, x0 + 0.24], [0.86 - (k - 1) * 0.085 - 0.012] * 2, color=ORANGE, lw=3)
        ax.text(x0 - 0.03, 0.86 - (k - 1) * 0.085 + 0.02, f"k={k}", ha="right", color=ORANGE, fontsize=12,
                weight="bold")
    ax.text(x0, 0.96, title, fontsize=14, weight="bold")


# ---------------------------------------------------------------- 1. P@k walking down a list
ranking = ["C3", "C7", "C1", "C9", "C4", "C2", "C8", "C5", "C6", "C0"]
relevant = {"C1", "C7", "C5"}
if L.wanted("pk_walk"):
    fig, (ax, a2) = plt.subplots(1, 2, figsize=(14, 6.4), gridspec_kw={"width_ratios": [1.2, 1]})

    def upd(f):
        k = min(f + 1, 10)
        blank(ax)
        draw_list(ax, ranking, relevant, k, "the system's ranking  (green = truly relevant)")
        hits = sum(c in relevant for c in ranking[:k])
        ax.text(0.45, 0.45, f"P@{k} = {hits} / {k} = {hits / k:.2f}", fontsize=16, weight="bold", color=ORANGE)
        ax.text(0.45, 0.36, "divide by k — always", fontsize=12, color=INK2)
        a2.clear()
        ks = np.arange(1, k + 1)
        a2.plot(ks, [p_at_k(ranking, relevant, kk) for kk in ks], "o-", color=ORANGE)
        a2.set_xlim(0.5, 10.5)
        a2.set_ylim(0, 1.05)
        a2.set_xlabel("k")
        a2.set_ylabel("precision@k")
        a2.set_title("P@k as k grows")
    L.animate(fig, upd, 13, "pk_walk", fps=1)

# ---------------------------------------------------------------- 2. P@k and MRR disagree
if L.wanted("p_vs_rr"):
    fig, ax = plt.subplots(figsize=(14, 6.4))
    blank(ax)
    A = ["C2", "C1", "C5", "C7", "C9", "C3", "C4", "C6", "C8", "C0"]
    Bk = ["C1", "C2", "C3", "C4", "C6", "C8", "C9", "C0", "C5", "C7"]
    rel = {"C1", "C5", "C7", "C9"}
    draw_list(ax, A, rel, 5, "ranking A", x0=0.08)
    draw_list(ax, Bk, rel, 5, "ranking B", x0=0.58)
    ax.text(0.08, 0.0, f"P@5 = {p_at_k(A, rel, 5):.2f}    RR = {rr(A, rel):.2f}", fontsize=14, weight="bold")
    ax.text(0.58, 0.0, f"P@5 = {p_at_k(Bk, rel, 5):.2f}    RR = {rr(Bk, rel):.2f}", fontsize=14, weight="bold")
    L.save(fig, "p_vs_rr")

# ---------------------------------------------------------------- 3. TF-IDF+cosine vs BM25, real data
STOP = {"and", "the", "of", "in", "to", "a", "with", "for", "on", "as", "an", "at", "by", "is", "it", "i", "we",
        "you", "our", "are", "be", "will", "my", "that", "this", "from", "have", "has", "was"}
if L.wanted("compare"):
    with open(data("31_ResumeMatch", "resumes.csv"), encoding="utf-8") as f:
        res = list(csv.DictReader(f))
    with open(data("31_ResumeMatch", "jobs.csv"), encoding="utf-8") as f:
        jobs = list(csv.DictReader(f))
    tok = lambda s: [w for w in re.findall(r"[a-z][a-z+#.]*[a-z+#]|[a-z]", s.lower()) if w not in STOP]
    D = [Counter(tok(r["text"])) for r in res]
    ids = [r["id"] for r in res]
    N = len(D)
    lens = np.array([sum(d.values()) for d in D])
    dfc = Counter(t for d in D for t in d)
    idf = {t: math.log((1 + N) / (1 + c)) + 1 for t, c in dfc.items()}
    rows = []
    for d in D:
        v = {t: c * idf[t] for t, c in d.items()}
        n = math.sqrt(sum(x * x for x in v.values()))
        rows.append({t: x / n for t, x in v.items()})

    def cosine_rank(q):
        qv = {t: c * idf[t] for t, c in Counter(tok(q)).items() if t in idf}
        n = math.sqrt(sum(x * x for x in qv.values()))
        s = [sum(r.get(t, 0) * x / n for t, x in qv.items()) for r in rows]
        return [ids[i] for i in np.argsort(-np.array(s), kind="stable")]

    def bm25_rank(q, k1=1.5, b=0.75):
        s = np.zeros(N)
        for t in set(tok(q)):
            if t not in dfc:
                continue
            w = math.log((N - dfc[t] + 0.5) / (dfc[t] + 0.5) + 1)
            for i, d in enumerate(D):
                if t in d:
                    s[i] += w * d[t] * (k1 + 1) / (d[t] + k1 * (1 - b + b * lens[i] / lens.mean()))
        return [ids[i] for i in np.argsort(-s, kind="stable")]

    ks = np.arange(1, 21)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [1.4, 1]})
    mrr = {}
    for name, fn, col in [("TF-IDF + cosine", cosine_rank, BLUE), ("BM25", bm25_rank, ORANGE)]:
        rk = {j["job_id"]: fn(j["text"]) for j in jobs}
        rel = {j["job_id"]: set(j["relevant_ids"].split()) for j in jobs}
        pk = [np.mean([p_at_k(rk[j], rel[j], k) for j in rk]) for k in ks]
        mrr[name] = np.mean([rr(rk[j], rel[j]) for j in rk])
        a1.plot(ks, pk, "o-", color=col, label=name, ms=5)
        print(f"  {name}: P@5 {pk[4]:.3f}  P@10 {pk[9]:.3f}  MRR {mrr[name]:.3f}")
    a1.set_xlabel("k")
    a1.set_ylabel("mean P@k over the 5 jobs")
    a1.set_ylim(0, 1.05)
    a1.set_xticks([1, 5, 10, 15, 20])
    a1.legend()
    a1.set_title("precision@k")
    a2.bar([0, 1], list(mrr.values()), color=[BLUE, ORANGE], width=0.5)
    for i, v in enumerate(mrr.values()):
        a2.text(i, v + 0.02, f"{v:.2f}", ha="center", fontsize=14)
    a2.set_xticks([0, 1], list(mrr))
    a2.set_ylim(0, 1.1)
    a2.set_title("MRR")
    caption(fig, "Simple versions of both methods on the project's 200 CVs and 5 labelled jobs.")
    L.save(fig, "compare")
