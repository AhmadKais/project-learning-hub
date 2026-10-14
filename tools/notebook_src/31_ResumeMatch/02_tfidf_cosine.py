# %% [markdown]
# # 02 · TF-IDF and cosine similarity, from scratch
#
# **Read first:** `01_theory/01_vectors.md`, `01_theory/02_cosine.md`, `01_theory/05_explain.md`
#
# 1. IDF by hand — check the three numbers from the theory chapter
# 2. a sparse TF-IDF matrix of the 200 CVs, every row L2-normalised
# 3. ranking a job = **one** matrix-vector product
# 4. the explanation is an exact decomposition: the contributions **sum to the score**
# 5. why sparse: the memory numbers

# %%
import csv
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
from scipy import sparse
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as STOP

# the pipeline from notebook 01
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

# %% [markdown]
# ## 1. IDF — the smoothed version
#
# $$ idf(t) = \ln\frac{1 + N}{1 + df(t)} + 1 $$
#
# `df` counts **documents**, not occurrences.

# %%
def compute_idf(df, n_docs):
    return math.log((1 + n_docs) / (1 + df)) + 1

for df_, expected in ((2, 1.2877), (1, 1.6931), (3, 1.0)):
    print(f"df={df_}, N=3 -> {compute_idf(df_, 3):.4f}   (theory: {expected})")

# %% [markdown]
# ## 2. The TF-IDF matrix
#
# Rows = CVs, columns = terms. Stored **sparse**: only the non-zero entries. Then every row is divided by its
# length, so every CV is an arrow of length 1.

# %%
df = Counter(t for d in docs for t in set(d))
vocab = {t: j for j, t in enumerate(sorted(df))}
idf = np.array([compute_idf(df[t], len(docs)) for t in sorted(df)])

rows, cols, vals = [], [], []
for i, d in enumerate(docs):
    for t, tf in Counter(d).items():
        rows.append(i); cols.append(vocab[t]); vals.append(tf * idf[vocab[t]])
M = sparse.csr_matrix((vals, (rows, cols)), shape=(len(docs), len(vocab)))

norms = np.sqrt(M.multiply(M).sum(axis=1)).A.ravel()
norms[norms == 0] = 1.0
M = sparse.diags(1.0 / norms) @ M
print("matrix:", M.shape, " non-zeros:", M.nnz, f" ({M.nnz / (M.shape[0] * M.shape[1]):.2%} of the cells)")
print("row lengths after normalising:", np.round(np.sqrt(M.multiply(M).sum(axis=1)).A.ravel()[:5], 6))

# %% [markdown]
# ## 3. Ranking a job
#
# The job goes into **the same space with the collection's IDF** — never an IDF computed from the job alone.
# Then, because every vector has length 1, cosine = dot product, and ranking all CVs is one line.

# %%
def job_vector(text):
    q = np.zeros(len(vocab))
    for t in process(text):
        if t in vocab:
            q[vocab[t]] += 1
    q = q * idf
    n = np.linalg.norm(q)
    return q / n if n else q

job = jobs[0]
print(job["title"], "|", job["text"])
q = job_vector(job["text"])
scores = M @ q
top = np.argsort(-scores, kind="stable")[:8]
relevant = set(job["relevant_ids"].split())
for r in top:
    mark = "✔" if ids[r] in relevant else " "
    print(f"  {mark} {ids[r]}  {resumes[r]['role']:15s} cosine {scores[r]:.3f}   ({len(docs[r])} terms)")

# %% [markdown]
# If a CV of the wrong role sits at the top with a high score, look at its text: it may contain a copy of the
# advert. Notebook 04 shows how to catch that automatically.
#
# ## 4. The explanation — exact, not approximate
#
# score = Σ resume[t] × job[t], a **sum over terms**. Each product is one term's exact contribution.

# %%
inv_vocab = {j: t for t, j in vocab.items()}

def explain(row, q, top_n=5):
    r = M.getrow(row)
    contrib = [(inv_vocab[c], v * q[c]) for c, v in zip(r.indices, r.data) if q[c] > 0]
    contrib.sort(key=lambda x: -x[1])
    return contrib, sum(v for _, v in contrib)

best = next(r for r in top if ids[r] in relevant)        # the best GENUINE candidate
contrib, total = explain(best, q)
print(f"{ids[best]}: score {scores[best]:.6f}   sum of all contributions {total:.6f}")
for term, v in contrib[:5]:
    print(f"   {term:18s} {v:.3f}")

# %% [markdown]
# The sum equals the score to the last digit — your test `test_explanation_sums_to_the_score` checks this to
# 1e-9. That is why the project uses classical methods: with neural embeddings no such decomposition exists.
#
# ## 5. Does length matter for cosine? Paste a CV twice

# %%
r0 = resumes[0]["text"]
v1, v2 = job_vector(r0), job_vector(r0 + " " + r0)
print("cosine(CV, CV pasted twice) =", round(float(v1 @ v2), 6))

# %% [markdown]
# 1.0 — identical direction. Cosine handles length **for free**, from the geometry. BM25 (notebook 03) does it
# with an explicit knob instead.
#
# ## 6. Why sparse

# %%
dense_bytes = M.shape[0] * M.shape[1] * 8
sparse_bytes = M.data.nbytes + M.indices.nbytes + M.indptr.nbytes
print(f"dense {dense_bytes / 1e6:.1f} MB   sparse {sparse_bytes / 1e6:.2f} MB   ({dense_bytes / sparse_bytes:.0f}x smaller)")

# %% [markdown]
# ## ✍️ Try it yourself
#
# 1. Compute the IDF of the job from the job text alone and rank again. What happens to the scores, and why
#    is it wrong? (theory "Putting the job in the same space")
# 2. Rank job J4 (embedded C++). Does the C++ token matter? Replace the tokenizer with `\w+` and compare.
# 3. Remove the L2 normalisation of the rows. Which CVs climb to the top now?
#
# Then solve exercises 5–8 in `03_exercises/`.
