"""Lesson 08 - documents as arrows: dot product, length, cosine similarity, and a real ranking."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)


def cos(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


job = np.array([1.0, 1.0])
cvs = {"CV A (2, 1)": np.array([2.0, 1.0]), "CV B (4, 2)": np.array([4.0, 2.0]), "CV C (0, 3)": np.array([0.0, 3.0])}


# ---------------------------------------------------------------- 1. documents are arrows
if L.wanted("arrows"):
    fig, ax = plt.subplots(figsize=(8.5, 7))
    ax.annotate("", (job[0], job[1]), (0, 0), arrowprops=dict(arrowstyle="-|>", lw=4, color=INK))
    ax.text(job[0] + 0.05, job[1] + 0.15, "JOB (1, 1)", fontsize=14, weight="bold")
    for (name, v), col in reversed(list(zip(cvs.items(), [BLUE, AQUA, ORANGE]))):
        ax.annotate("", (v[0], v[1]), (0, 0), arrowprops=dict(arrowstyle="-|>", lw=7 if "B" in name else 3,
                                                               color=col, alpha=0.5 if "B" in name else 1))
        ang = np.degrees(np.arccos(cos(v, job)))
        ax.text(v[0] + 0.08, v[1] - (0.35 if "A" in name else 0.05), f"{name}\nangle {ang:.0f}°   cos = {cos(v, job):.3f}", fontsize=12, color=col)
    ax.set_xlim(0, 5.6)
    ax.set_ylim(0, 3.6)
    ax.set_aspect("equal")
    ax.set_xlabel("how much 'python'")
    ax.set_ylabel("how much 'sql'")
    ax.set_title("Each document is an arrow; similarity = the angle")
    caption(fig, "CV A and CV B point the SAME way (B is just A said twice) - same cosine.  CV C points elsewhere.")
    L.save(fig, "arrows")

# ---------------------------------------------------------------- 2. rotating arrow
angles = np.r_[np.linspace(0, 180, 37), np.linspace(175, 5, 35)]


def draw_rot(a1, a2, k):
    th = np.radians(angles[k])
    v = 2 * np.array([np.cos(th), np.sin(th)])
    a1.clear()
    a1.annotate("", (2, 0), (0, 0), arrowprops=dict(arrowstyle="-|>", lw=4, color=INK))
    a1.annotate("", tuple(v), (0, 0), arrowprops=dict(arrowstyle="-|>", lw=4, color=ORANGE))
    arc = np.linspace(0, th, 50)
    a1.plot(0.6 * np.cos(arc), 0.6 * np.sin(arc), color=MUTED)
    a1.text(0.7 * np.cos(th / 2), 0.7 * np.sin(th / 2), f"{angles[k]:.0f}°", fontsize=13)
    a1.set_xlim(-2.3, 2.3)
    a1.set_ylim(-0.4, 2.3)
    a1.set_aspect("equal")
    a1.set_xticks([]); a1.set_yticks([])
    a1.text(2.05, -0.25, "job", fontsize=12)
    a1.text(v[0] * 1.08, v[1] * 1.08, "CV", fontsize=12, color=ORANGE)
    c = np.cos(th)
    label = "same direction" if c > 0.95 else ("unrelated (no shared words)" if abs(c) < 0.05 else
                                               ("opposite (impossible with counts)" if c < -0.95 else ""))
    a1.set_title(f"cos = {c:+.2f}   {label}")
    a2.clear()
    xs = np.linspace(0, 180, 200)
    a2.plot(xs, np.cos(np.radians(xs)), color=MUTED)
    a2.axvspan(90, 180, color=GRID, alpha=0.6)
    a2.text(135, 0.6, "never happens\nwith word counts\n(all ≥ 0)", ha="center", fontsize=11, color=INK2)
    a2.plot(angles[k], c, "o", color=ORANGE, ms=12)
    a2.set_xlabel("angle (degrees)")
    a2.set_ylabel("cosine")
    a2.set_title("cosine of the angle")


if L.wanted("rotate"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    L.animate(fig, lambda k: draw_rot(a1, a2, k), len(angles), "rotate", fps=8)

# ---------------------------------------------------------------- 3. the length trap: euclid vs cosine
if L.wanted("length_trap"):
    short = np.array([1.0, 1.0, 0.0])
    long = 5 * short
    other = np.array([0.0, 1.2, 1.0])
    query = np.array([1.0, 1.0, 0.0])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.4))
    labels = ["short CV\n(1,1,0)", "same CV ×5\n(5,5,0)", "different CV\n(0,1.2,1)"]
    vecs = [short, long, other]
    eu = [np.linalg.norm(v - query) for v in vecs]
    cs = [cos(v, query) for v in vecs]
    a1.bar(range(3), eu, color=[BLUE, AQUA, ORANGE])
    a1.set_xticks(range(3), labels)
    a1.set_title("Euclidean distance to the job (smaller = closer)")
    a2.bar(range(3), cs, color=[BLUE, AQUA, ORANGE])
    a2.set_xticks(range(3), labels)
    a2.set_ylim(0, 1.1)
    a2.set_title("cosine similarity (bigger = closer)")
    for ax, vals in [(a1, eu), (a2, cs)]:
        for i, v in enumerate(vals):
            ax.text(i, v + 0.05, f"{v:.2f}", ha="center", fontsize=13)
    caption(fig, "Distance says the repeated CV is the WORST match.  Cosine ignores length and says it is identical.")
    L.save(fig, "length_trap")

# ---------------------------------------------------------------- 4. a real ranking
if L.wanted("real_ranking"):
    from sklearn.feature_extraction.text import TfidfVectorizer
    with open(data("31_ResumeMatch", "resumes.csv"), encoding="utf-8") as f:
        res = list(csv.DictReader(f))
    with open(data("31_ResumeMatch", "jobs.csv"), encoding="utf-8") as f:
        jobs = list(csv.DictReader(f))
    vec = TfidfVectorizer(stop_words="english", token_pattern=r"(?u)\b[a-zA-Z][a-zA-Z+#.]*[a-zA-Z+#]\b")
    M = vec.fit_transform([r["text"] for r in res])
    j = jobs[0]
    s = (M @ vec.transform([j["text"]]).T).toarray().ravel()     # rows are L2-normalised -> dot = cosine
    rel = set(j["relevant_ids"].split())
    order = np.argsort(-s)[:40]
    fig, ax = plt.subplots(figsize=(14, 4.8))
    ax.bar(range(1, 41), s[order], color=[GREEN if res[i]["id"] in rel else MUTED for i in order])
    for r, i in enumerate(order, start=1):
        if j["text"][:60] in res[i]["text"]:
            ax.annotate(f"{res[i]['id']} is a {res[i]['role']} CV that pasted THIS job advert", (r, s[i]),
                        xytext=(r + 4, s[i] - 0.03), fontsize=11, arrowprops=dict(arrowstyle="->"))
    ax.set_xlabel("rank (the 40 best CVs of 200)")
    ax.set_ylabel("cosine similarity")
    hits10 = sum(res[i]["id"] in rel for i in order[:10])
    ax.set_title(f"Job '{j['title']}': green = a CV a human marked relevant   (P@10 = {hits10}/10)")
    L.save(fig, "real_ranking")
