"""ResumeMatch - solutions to exercises.py.

Try first. Then compare: there is more than one correct way to write each one.
To run the tests against these solutions:  EXERCISES=solutions pytest test_exercises.py
"""
import math
import re
from collections import Counter, defaultdict

TOKEN_PATTERN = re.compile(r"\.?[A-Za-z֐-׿][A-Za-z0-9֐-׿+#.]*(?<!\.)")   # the same pattern as your config.py
EMAIL_RE = re.compile(r"\S+@\S+\.\w+")
PHONE_RE = re.compile(r"\+?\d[\d\- ]{7,}\d")


def ex01_scrub(text):
    text = EMAIL_RE.sub(" ", text)
    return PHONE_RE.sub(" ", text)


def ex02_tokenize(text):
    out = []
    for tok in TOKEN_PATTERN.findall(text):
        tok = tok.rstrip(".").lower()
        if tok:
            out.append(tok)
    return out


def ex03_add_bigrams(tokens):
    return list(tokens) + [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]


def ex04_document_frequency(docs):
    df = Counter()
    for d in docs:
        df.update(set(d))
    return df


def ex05_idf(df, n_docs):
    return math.log((1 + n_docs) / (1 + df)) + 1


def ex06_tfidf_unit_vector(terms, idf):
    vec = {t: c * idf[t] for t, c in Counter(terms).items() if t in idf}
    norm = math.sqrt(sum(v * v for v in vec.values()))
    return {t: v / norm for t, v in vec.items()} if norm else {}


def ex07_cosine(a, b):
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    dot = sum(v * b[t] for t, v in a.items() if t in b)
    return dot / (na * nb)


def ex08_contributions(resume_vec, job_vec):
    pairs = [(t, resume_vec[t] * job_vec[t]) for t in resume_vec if t in job_vec]
    return sorted(pairs, key=lambda p: (-p[1], p[0]))


def ex09_bm25_idf(df, n_docs):
    return math.log((n_docs - df + 0.5) / (df + 0.5) + 1)


def ex10_bm25_term_score(tf, doc_length, avgdl, idf, k1=1.5, b=0.75):
    numerator = tf * (k1 + 1)
    denominator = tf + k1 * (1 - b + b * doc_length / avgdl)
    return idf * numerator / denominator


def ex11_bm25_rank(docs, query_terms, k1=1.5, b=0.75):
    inverted = defaultdict(list)
    for row, d in enumerate(docs):
        for term, tf in Counter(d).items():
            inverted[term].append((row, tf))
    lengths = [len(d) for d in docs]
    avgdl = sum(lengths) / len(docs)
    scores = [0.0] * len(docs)
    touched = set()
    for term in set(query_terms):
        postings = inverted.get(term)
        if not postings:
            continue
        idf = ex09_bm25_idf(len(postings), len(docs))
        for row, tf in postings:
            scores[row] += ex10_bm25_term_score(tf, lengths[row], avgdl, idf, k1, b)
            touched.add(row)
    return scores, touched


def ex12_precision_at_k(ranking, relevant, k):
    return sum(1 for c in ranking[:k] if c in relevant) / k


def ex13_mean_reciprocal_rank(rankings, relevants):
    total = 0.0
    for ranking, relevant in zip(rankings, relevants):
        for position, c in enumerate(ranking, start=1):
            if c in relevant:
                total += 1.0 / position
                break
    return total / len(rankings)
