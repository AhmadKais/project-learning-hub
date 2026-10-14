# %% [markdown]
# # 04 · Measuring a ranking, and catching copied adverts
#
# **Read first:** `01_theory/06_evaluate.md`, `01_theory/05_explain.md` (the reliability check)
#
# 1. Precision@k and MRR — the worked example by hand, then in code
# 2. TF-IDF + cosine vs BM25 on the 5 jobs, with b = 0 and b = 0.75
# 3. skills coverage, and the reliability check that catches CVs that copied a job advert

# %%
import csv
import math
import re
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as STOP

# %% [markdown]
# ## 1. The metrics
#
# * **P@k** — of the top k, how many are relevant? Divide by **k**, not by the length of the list.
# * **RR** — 1 / position of the first relevant candidate; **MRR** = its average over the jobs.

# %%
def precision_at_k(ranking, relevant, k):
    return len([c for c in ranking[:k] if c in relevant]) / k

def reciprocal_rank(ranking, relevant):
    for position, c in enumerate(ranking, start=1):
        if c in relevant:
            return 1.0 / position
    return 0.0

ranking, relevant = ["C3", "C7", "C1", "C9"], {"C1", "C7"}
print("P@2 =", precision_at_k(ranking, relevant, 2), " P@4 =", precision_at_k(ranking, relevant, 4),
      " RR =", reciprocal_rank(ranking, relevant), "   (theory: 0.5, 0.5, 0.5)")
print("short ranking, P@10 =", precision_at_k(["C7"], relevant, 10), " <- 1/10, not 1/1")

# %% [markdown]
# ## 2. Both methods, compact (notebooks 02 and 03)

# %%
TOKEN_PATTERN = re.compile(r"\.?[A-Za-z֐-׿][A-Za-z0-9֐-׿+#.]*(?<!\.)")    # = config.TOKEN_PATTERN
SCRUB = [re.compile(r"\S+@\S+\.\w+"), re.compile(r"\+?\d[\d\-\s]{7,}\d")]
stem = SnowballStemmer("english").stem

def process(text):
    for p in SCRUB:
        text = p.sub(" ", text)
    toks = [t.lower() for t in TOKEN_PATTERN.findall(text)]
    toks = [stem(t) for t in toks if t and (t not in STOP and len(t) > 1 or t in ("c", "go", "r"))]
    return toks + [f"{a} {b}" for a, b in zip(toks, toks[1:])]

resumes = list(csv.DictReader(open(Path("../data/resumes.csv"), encoding="utf-8")))
jobs = list(csv.DictReader(open(Path("../data/jobs.csv"), encoding="utf-8")))
docs = [process(r["text"]) for r in resumes]
ids = [r["id"] for r in resumes]
N = len(docs)
df = Counter(t for d in docs for t in set(d))

def cosine_rank(job_text):
    idf = {t: math.log((1 + N) / (1 + df[t])) + 1 for t in df}
    def vec(terms):
        v = {t: c * idf[t] for t, c in Counter(terms).items() if t in idf}
        n = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / n for t, x in v.items()}
    q = vec(process(job_text))
    scores = [sum(w * q.get(t, 0) for t, w in vec(d).items()) for d in docs]
    return [ids[i] for i in np.argsort(-np.array(scores), kind="stable")], scores

def bm25_rank(job_text, k1=1.5, b=0.75):
    lens = np.array([len(d) for d in docs]); avgdl = lens.mean()
    scores = np.zeros(N)
    for t in set(process(job_text)):
        if t not in df:
            continue
        idf = math.log((N - df[t] + 0.5) / (df[t] + 0.5) + 1)
        for i, d in enumerate(docs):
            tf = d.count(t)
            if tf:
                scores[i] += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * lens[i] / avgdl))
    return [ids[i] for i in np.argsort(-scores, kind="stable")], scores

# %% [markdown]
# ## 3. The comparison over the 5 jobs

# %%
methods = {"TF-IDF + cosine": cosine_rank,
           "BM25, b = 0": lambda t: bm25_rank(t, b=0.0),
           "BM25, b = 0.75": bm25_rank}
print(f"{'method':18s} {'P@5':>6s} {'P@10':>6s} {'MRR':>6s} {'median ms':>10s}")
for name, rank in methods.items():
    p5, p10, rr, times = [], [], [], []
    for job in jobs:
        rel = set(job["relevant_ids"].split())
        t0 = time.perf_counter(); r, _ = rank(job["text"]); times.append((time.perf_counter() - t0) * 1000)
        p5.append(precision_at_k(r, rel, 5)); p10.append(precision_at_k(r, rel, 10)); rr.append(reciprocal_rank(r, rel))
    print(f"{name:18s} {np.mean(p5):6.2f} {np.mean(p10):6.2f} {np.mean(rr):6.2f} {statistics.median(times):10.1f}")

# %% [markdown]
# Compare the rows: which method lets the long "familiar with everything" CVs into the top 10, and what does it
# cost in P@10? Synthetic data gives you the *method*; on real CVs with 50 hand-labelled jobs your results chapter
# reports the real numbers.
#
# **Label before you look.** Your ground truth must be written *before* you see the system's rankings, or you
# will unconsciously agree with the machine.
#
# ## 4. Skills coverage and the reliability check
#
# Copying wording from the advert raises **text similarity** but not **skill coverage**. When the two disagree,
# warn the recruiter.

# %%
REQUIRED = {"J1": ["Python", "Django", "REST APIs", "PostgreSQL"],
            "J2": ["Python", "Machine Learning", "pandas", "scikit-learn"],
            "J3": ["Kubernetes", "CI/CD", "Docker", "Linux"],
            "J4": ["C++", "microcontrollers", "RTOS", "embedded systems"],
            "J5": ["C#", ".NET", "ASP.NET", "SQL Server"]}

def norm_skill(s):
    return " ".join(t for t in process(s) if " " not in t) if len(s.split()) == 1 else \
           " ".join(t for t in process(s) if " " not in t)

def skills_section(text):
    """Only the 'Skills:' line counts as evidence of a skill, not free text."""
    m = re.search(r"Skills:(.*?)\.\s", text)
    return process(m.group(1)) if m else []

def coverage(row, job_id):
    have = set(skills_section(resumes[row]["text"]))
    need = REQUIRED[job_id]
    found = [s for s in need if norm_skill(s) in have]
    return len(found) / len(need), found

for job in jobs:
    ranking, scores = cosine_rank(job["text"])
    top = max(scores)
    for cid in ranking[:15]:
        row = ids.index(cid)
        score = scores[row] / top
        cov, found = coverage(row, job["job_id"])
        if score > 0.6 and cov < 0.35:
            print(f"⚠ {job['job_id']} {cid} ({resumes[row]['role']}): similarity {score:.2f} but skills {cov:.0%} {found}"
                  " - wording may be copied from the advert, review manually")

# %% [markdown]
# Every warning should be one of the "advert copiers" planted in the data (a CV whose role does not fit the job).
# Two independent signals disagreeing is information — that paragraph belongs in your book.
#
# ## 5. The metrics again, with flagged CVs moved to the end

# %%
def flagged(job, ranking, scores):
    top = max(scores)
    return {cid for cid in ranking[:15]
            if scores[ids.index(cid)] / top > 0.6 and coverage(ids.index(cid), job["job_id"])[0] < 0.35}

print(f"{'method':18s} {'P@5':>6s} {'P@10':>6s} {'MRR':>6s}")
for name, rank in methods.items():
    p5, p10, rr = [], [], []
    for job in jobs:
        rel = set(job["relevant_ids"].split())
        r, s = rank(job["text"])
        bad = flagged(job, r, s)
        r = [c for c in r if c not in bad] + [c for c in r if c in bad]
        p5.append(precision_at_k(r, rel, 5)); p10.append(precision_at_k(r, rel, 10)); rr.append(reciprocal_rank(r, rel))
    print(f"{name:18s} {np.mean(p5):6.2f} {np.mean(p10):6.2f} {np.mean(rr):6.2f}")

# %% [markdown]
# The reliability check is not only a warning for the recruiter — it measurably improves the ranking.
#
# ## ✍️ Try it yourself
#
# 1. Add P@3 and see whether the ranking of the three methods changes.
# 2. Lower the warning threshold to 0.5. Do you get false alarms? Which signal causes them?
# 3. Explain in two sentences what it means if P@5 is high but MRR is low.
#
# Then solve exercises 12–13 in `03_exercises/`.
