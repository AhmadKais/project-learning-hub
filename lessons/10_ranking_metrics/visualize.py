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

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 4. people only look at the top: a results page
if L.wanted("results_page"):
    fig, ax = plt.subplots(figsize=(12, 7.2))
    blank(ax)
    looks = [100, 96, 85, 70, 58, 45, 36, 28, 22, 18]          # an illustrative "attention" curve
    ax.add_patch(FancyBboxPatch((0.03, 0.9), 0.6, 0.07, boxstyle="round,pad=0,rounding_size=0.02", ec=INK2,
                                fc=PAPER, lw=1.5))
    ax.text(0.05, 0.935, "search:  backend python developer", fontsize=13, va="center")
    for i in range(10):
        y = 0.8 - i * 0.08
        ax.add_patch(plt.Rectangle((0.03, y), 0.6, 0.06, color="#f1f0ec"))
        ax.text(0.05, y + 0.03, f"{i + 1}.  CV result number {i + 1}", fontsize=12, va="center")
        ax.add_patch(plt.Rectangle((0.68, y + 0.005), 0.28 * looks[i] / 100, 0.05, color=ORANGE, alpha=0.85))
        ax.text(0.69 + 0.28 * looks[i] / 100, y + 0.03, f"{looks[i]}%", fontsize=11, va="center")
    ax.text(0.68, 0.87, "how often people look at it", fontsize=12, color=INK2)
    ax.text(0.03, 0.0, "Page 2 …  (almost nobody goes there)", fontsize=12, color=MUTED, style="italic")
    ax.set_title("A ranking is judged at the TOP: that's why we measure P@k and the position of the first hit",
                 fontsize=13)
    caption(fig, "The attention numbers are illustrative - real eye-tracking studies of search pages show the same shape: "
                 "the first results get most of the looks.")
    L.save(fig, "results_page")

# ---------------------------------------------------------------- 5. 1 / position: steep at the top, flat further down
if L.wanted("rr_curve"):
    fig, ax = plt.subplots(figsize=(11, 4.6))
    pos = np.arange(1, 21)
    ax.bar(pos, 1 / pos, color=[GREEN if p == 1 else AQUA for p in pos])
    for p in [1, 2, 3, 4, 5, 10, 20]:
        ax.text(p, 1 / p + 0.03, f"1/{p}\n= {1 / p:.2f}", ha="center", fontsize=10)
    ax.set_xticks(pos)
    ax.set_ylim(0, 1.25)
    ax.set_xlabel("position of the FIRST relevant CV")
    ax.set_ylabel("reciprocal rank")
    ax.set_title("Moving the first hit from 2nd to 1st is worth +0.5; from 20th to 19th only +0.003")
    L.save(fig, "rr_curve")

# ---------------------------------------------------------------- 6. MRR over three jobs, animated
if L.wanted("mrr_jobs"):
    jobs3 = [("Job 1", ["R4", "R2", "R9", "R1", "R7"], {"R4", "R1"}),
             ("Job 2", ["R3", "R8", "R5", "R6", "R0"], {"R8"}),
             ("Job 3", ["R6", "R0", "R2", "R5", "R9"], {"R5", "R9"})]
    fig, ax = plt.subplots(figsize=(14, 5.6))

    def upd(k):
        blank(ax)
        rrs = []
        for j, (name, rank, rel) in enumerate(jobs3):
            x0 = 0.03 + j * 0.33
            ax.text(x0, 0.95, name, fontsize=14, weight="bold")
            first = next(i for i, c in enumerate(rank) if c in rel)
            for i, c in enumerate(rank):
                y = 0.82 - i * 0.12
                hit = c in rel
                show = j < k
                box(ax, x0, y, 0.12, 0.09, f"{i + 1}. {c}", color=GREEN if hit and show else MUTED,
                    fill="#d5ecd5" if hit and show else PAPER, fontsize=12)
                if show and i == first:
                    ax.text(x0 + 0.13, y + 0.045, f"← RR = 1/{i + 1}\n    = {1 / (i + 1):.2f}", fontsize=12,
                            color=GREEN, va="center")
            if j < k:
                rrs.append(1 / (first + 1))
        if k == len(jobs3):
            ax.text(0.5, 0.06, f"MRR = ({' + '.join(f'{r:.2f}' for r in rrs)}) ÷ 3 = {np.mean(rrs):.2f}", ha="center",
                    fontsize=16, weight="bold")
    frames = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 3, 3]
    L.animate(fig, lambda i: upd(frames[i]), len(frames), "mrr_jobs", fps=2)

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

    # per job: where does the first relevant CV sit?
    fig, ax = plt.subplots(figsize=(13, 4.8))
    x = np.arange(len(jobs))
    for off, (name, fn, col) in zip([-0.2, 0.2], [("TF-IDF + cosine", cosine_rank, BLUE), ("BM25", bm25_rank, ORANGE)]):
        firsts = []
        for j in jobs:
            rk = fn(j["text"])
            rel = set(j["relevant_ids"].split())
            firsts.append(next(i for i, c in enumerate(rk, 1) if c in rel))
        ax.bar(x + off, firsts, 0.38, color=col, label=name)
        for xx, f_ in zip(x + off, firsts):
            ax.text(xx, f_ + 0.05, f"pos {f_}\nRR {1 / f_:.2f}", ha="center", fontsize=10)
        print(f"  {name} first relevant per job: {firsts}")
    ax.set_xticks(x, [j["title"] for j in jobs], fontsize=10)
    ax.set_ylabel("position of the first relevant CV")
    ax.set_ylim(0, 4)
    ax.set_title("Per job: in 4 of 5 jobs CVs that copied the advert push the first real hit down to position 2 or 3")
    ax.legend(loc="upper right")
    L.save(fig, "per_job")
