"""ResumeMatch - exercises.

Fill in every function marked TODO. Use only the standard library (math, re, collections).
Check yourself after each exercise:

    pytest test_exercises.py -k ex01 -v        # one exercise
    pytest test_exercises.py -v                # all of them

Stuck for more than 20 minutes? Re-read the theory section named in the
docstring, look at the notebook, and only then open solutions.py.
"""
import math
import re
from collections import Counter, defaultdict

TOKEN_PATTERN = re.compile(r"\.?[A-Za-z֐-׿][A-Za-z0-9֐-׿+#.]*(?<!\.)")   # the same pattern as your config.py


# ---------------------------------------------------------------- preprocessing (notebook 01)

def ex01_scrub(text):
    """Replace every email address and every phone number with ONE SPACE.

    email: something@something.something        phone: 9 or more digits, may contain '-' or spaces, may start with '+'
    >>> ex01_scrub("Mail noa@x.com or 054-1234567, thanks")
    'Mail   or  , thanks'

    Theory 04_pipeline "Scrubbing personal data"
    """
    raise NotImplementedError("TODO ex01")


def ex02_tokenize(text):
    """Tokens using TOKEN_PATTERN, lower-cased, with a trailing '.' removed (end of sentence).

    C++, C#, Node.js must survive. Tokens that become empty are dropped.
    >>> ex02_tokenize("I know C++, C# and Node.js. I love Python.")
    ['i', 'know', 'c++', 'c#', 'and', 'node.js', 'i', 'love', 'python']

    Theory 04_pipeline "Tokenizing"
    """
    raise NotImplementedError("TODO ex02")


def ex03_add_bigrams(tokens):
    """tokens + every pair of neighbouring tokens joined by one space.
    >>> ex03_add_bigrams(["machin", "learn", "python"])
    ['machin', 'learn', 'python', 'machin learn', 'learn python']
    """
    raise NotImplementedError("TODO ex03")


# ---------------------------------------------------------------- TF-IDF + cosine (notebook 02)

def ex04_document_frequency(docs):
    """Counter {term: number of DOCUMENTS containing it}. A term twice in one document counts once.
    Theory 01_vectors (the counting mistake)
    """
    raise NotImplementedError("TODO ex04")


def ex05_idf(df, n_docs):
    """Smoothed IDF:  ln((1 + N) / (1 + df)) + 1
    ex05_idf(2, 3) == 1.2877...   ex05_idf(3, 3) == 1.0
    """
    raise NotImplementedError("TODO ex05")


def ex06_tfidf_unit_vector(terms, idf):
    """{term: count * idf[term]} for the terms that are in idf, divided by the vector's length (L2).
    No known terms -> {}.
    Theory 02_cosine "The trick that makes it fast"
    """
    raise NotImplementedError("TODO ex06")


def ex07_cosine(a, b):
    """Cosine similarity of two sparse vectors given as dicts {term: weight} (NOT necessarily unit length).
    If either has length 0, return 0.0.
    """
    raise NotImplementedError("TODO ex07")


def ex08_contributions(resume_vec, job_vec):
    """The explanation: list of (term, resume_vec[t] * job_vec[t]) for every term in BOTH vectors,
    largest contribution first (equal values: alphabetical).
    For unit vectors the contributions sum EXACTLY to the cosine score.
    Theory 05_explain
    """
    raise NotImplementedError("TODO ex08")


# ---------------------------------------------------------------- BM25 (notebook 03)

def ex09_bm25_idf(df, n_docs):
    """BM25's own IDF:  ln((N - df + 0.5) / (df + 0.5) + 1)     - always positive."""
    raise NotImplementedError("TODO ex09")


def ex10_bm25_term_score(tf, doc_length, avgdl, idf, k1=1.5, b=0.75):
    """idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_length / avgdl))
    Theory 03_bm25 "The full formula"
    """
    raise NotImplementedError("TODO ex10")


def ex11_bm25_rank(docs, query_terms, k1=1.5, b=0.75):
    """Rank documents (lists of terms) for a query with BM25 and an INVERTED INDEX.

    Build {term: [(doc_row, tf), ...]}, then walk only the DISTINCT query terms.
    Returns (scores, touched): scores = list of floats, one per document (0.0 if never touched);
    touched = the set of doc rows that shared at least one term with the query.
    """
    raise NotImplementedError("TODO ex11")


# ---------------------------------------------------------------- evaluation (notebook 04)

def ex12_precision_at_k(ranking, relevant, k):
    """Of the first k items of `ranking`, the share that is in `relevant`. Divide by k ALWAYS.
    Theory 06_evaluate
    """
    raise NotImplementedError("TODO ex12")


def ex13_mean_reciprocal_rank(rankings, relevants):
    """Average over the queries of 1 / (position of the first relevant item), positions start at 1.
    A query with no relevant item in its ranking contributes 0.
    rankings: list of lists.  relevants: list of sets (same order).
    """
    raise NotImplementedError("TODO ex13")
