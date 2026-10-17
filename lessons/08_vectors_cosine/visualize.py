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

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 5. the dot product as matching boxes
if L.wanted("dot_boxes"):
    words = ["python", "sql", "docker", "java"]
    a = [2, 1, 1, 0]
    b = [1, 1, 0, 2]
    fig, ax = plt.subplots(figsize=(13, 4.6))
    blank(ax)
    for j, w in enumerate(words):
        x = 0.16 + j * 0.17
        ax.text(x + 0.06, 0.9, w, ha="center", fontsize=13, weight="bold")
        box(ax, x, 0.66, 0.12, 0.14, str(a[j]), color=BLUE, fill=LIGHT_BLUE, fontsize=16)
        box(ax, x, 0.42, 0.12, 0.14, str(b[j]), color=ORANGE, fill=LIGHT_ORANGE, fontsize=16)
        p = a[j] * b[j]
        box(ax, x, 0.12, 0.12, 0.14, f"{a[j]}×{b[j]} = {p}", color=GREEN if p else MUTED, fontsize=13)
        ax.text(x + 0.06, 0.32, "↓", ha="center", fontsize=18)
    ax.text(0.02, 0.73, "CV", fontsize=14, color=BLUE, weight="bold")
    ax.text(0.02, 0.49, "advert", fontsize=14, color=ORANGE, weight="bold")
    ax.text(0.02, 0.19, "multiply", fontsize=13, color=INK2)
    ax.text(0.85, 0.19, f"add: {sum(x * y for x, y in zip(a, b))}", fontsize=18, weight="bold", color=GREEN)
    ax.set_title("dot product = multiply the numbers in matching positions, then add them all", fontsize=14)
    caption(fig, "A word only adds to the dot product when it is in BOTH texts (docker and java add 0).")
    L.save(fig, "dot_boxes")

# ---------------------------------------------------------------- 6. three words = three dimensions (same maths)
if L.wanted("arrows_3d"):
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
    fig = plt.figure(figsize=(9, 7.5))
    ax = fig.add_subplot(projection="3d")
    J3 = np.array([1, 1, 0.0])
    vs = [("advert (1, 1, 0)", J3, INK), ("CV A (2, 1, 0)", np.array([2, 1, 0.0]), BLUE),
          ("CV D (1, 1, 2)", np.array([1, 1, 2.0]), AQUA), ("CV E (0, 0, 3)", np.array([0, 0, 3.0]), ORANGE)]
    for name, v, col in vs:
        ax.quiver(0, 0, 0, *v, color=col, lw=3, arrow_length_ratio=0.12)
        c = cos(J3, v)
        ax.text(*(v * 1.05), f"{name}\ncos = {c:.2f}" if name[:3] != "adv" else name, color=col, fontsize=11)
    ax.set_xlim(0, 3)
    ax.set_ylim(0, 3)
    ax.set_zlim(0, 3)
    ax.set_xlabel("python")
    ax.set_ylabel("sql")
    ax.set_zlabel("figma")
    ax.view_init(22, 35)
    ax.set_title("3 words = 3 dimensions. 5,000 words = 5,000 dimensions:\nwe can't draw it, but the arithmetic is identical")
    L.save(fig, "arrows_3d")

# ---------------------------------------------------------------- 7. real CVs: who resembles whom? (cosine matrix)
if L.wanted("cv_matrix"):
    import math
    import re
    from collections import Counter
    with open(data("31_ResumeMatch", "resumes.csv"), encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    roles = ["python_backend", "data_science", "frontend", "devops", "qa"]
    pick = [r for role in roles for r in [x for x in rows if x["role"] == role][:6]]
    toks = [re.findall(r"[a-z][a-z+#.]*[a-z+#]", r["text"].lower().split(". ", 1)[1]) for r in rows]
    Nr = len(rows)
    dfr = Counter(t for d in toks for t in set(d))
    idf = {t: math.log((1 + Nr) / (1 + c)) + 1 for t, c in dfr.items()}
    vocab = sorted(idf)
    pos = {t: i for i, t in enumerate(vocab)}

    def vec(text):
        v = np.zeros(len(vocab))
        for t, c in Counter(re.findall(r"[a-z][a-z+#.]*[a-z+#]", text.lower().split(". ", 1)[1])).items():
            v[pos[t]] = c * idf[t]
        return v / np.linalg.norm(v)
    V = np.array([vec(r["text"]) for r in pick])
    S = V @ V.T
    fig, ax = plt.subplots(figsize=(9.5, 8.5))
    im = ax.imshow(S, cmap="Blues", vmin=0, vmax=1)
    ax.grid(False)
    for k, role in enumerate(roles):
        ax.text(-1, k * 6 + 2.5, role.replace("_", " "), ha="right", va="center", fontsize=11)
        ax.add_patch(plt.Rectangle((k * 6 - 0.5, k * 6 - 0.5), 6, 6, fill=False, ec=ORANGE, lw=2))
    ax.set_xticks([])
    ax.set_yticks([])
    fig.colorbar(im, ax=ax, label="cosine similarity", shrink=0.8)
    ax.set_title("30 real CVs, every pair compared (TF-IDF + cosine)\nCVs of the same job type light up the orange squares")
    L.save(fig, "cv_matrix")

# ---------------------------------------------------------------- 8. cosine in everyday life
if L.wanted("cosine_world"):
    tiles = [("Spotify 'similar songs'", "a song = (tempo, energy, dance, ...)", "songs pointing the same way"),
             ("Face recognition", "a face = 128 numbers from a network", "today's face vs the saved one: high cos → open"),
             ("Plagiarism checker", "an essay = its TF-IDF row", "two essays with cos 0.95 → copied?"),
             ("Shop: 'you may also like'", "a customer = what they bought", "customers pointing your way bought…"),
             ("News: 'related articles'", "an article = its TF-IDF row", "the 5 articles with the highest cos"),
             ("Kosai's ResumeMatch", "a CV / an advert = TF-IDF row", "sort the 200 CVs by cos with the advert")]
    fig, axes = plt.subplots(2, 3, figsize=(15, 6.6))
    for ax, (title, what, how), col in zip(axes.ravel(), tiles, SERIES):
        blank(ax)
        ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0,rounding_size=0.05", lw=2.5,
                                    edgecolor=col, facecolor=PAPER))
        ax.add_patch(FancyBboxPatch((0.02, 0.74), 0.96, 0.24, boxstyle="round,pad=0,rounding_size=0.05", lw=0,
                                    facecolor=col))
        ax.text(0.5, 0.86, title, ha="center", va="center", color="white", fontsize=13.5, weight="bold")
        ax.text(0.06, 0.56, "the arrow:", fontsize=10.5, color=MUTED)
        ax.text(0.06, 0.45, what, fontsize=11.5)
        ax.text(0.06, 0.28, "cosine finds:", fontsize=10.5, color=MUTED)
        ax.text(0.06, 0.17, how, fontsize=11.5)
    fig.suptitle("Turn things into arrows, compare the angle - one idea behind many apps", fontsize=15, weight="bold")
    L.save(fig, "cosine_world")
