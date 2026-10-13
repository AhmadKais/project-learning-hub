"""SpamClassifier - exercises.

Fill in every function marked TODO. Use only the standard library (math, re, collections).
Check yourself after each exercise:

    pytest test_exercises.py -k ex01 -v        # one exercise
    pytest test_exercises.py -v                # all of them

Stuck for more than 20 minutes? Re-read the theory section named in the
docstring, look at the notebook, and only then open solutions.py.
"""
import math
import re
from collections import Counter

HAM, SPAM = 0, 1
URL_TOKEN = "URLTOKEN"
WORD_RE = re.compile(r"[a-z']+")


# ---------------------------------------------------------------- text -> numbers (notebook 01)

def ex01_caps_ratio(text):
    """Uppercase letters / all letters, in [0, 1]. Digits and punctuation are not letters.
    No letters at all -> 0.0.
    >>> ex01_caps_ratio("FREE money 100!")
    0.4444444444444444
    Theory 3.7 - 3.8
    """
    raise NotImplementedError("TODO ex01")


def ex02_strip_html(text):
    """Remove every <...> tag, replacing it with a SPACE, then collapse runs of whitespace to one space
    and strip the ends.
    >>> ex02_strip_html("<b>free</b><i>offer</i>  now")
    'free offer now'
    Theory 3.9
    """
    raise NotImplementedError("TODO ex02")


def ex03_tokenize(cleaned, stopwords):
    """Tokens of an already cleaned (lower-cased) text.

    - words are matches of WORD_RE  ([a-z']+)
    - keep only words with at least 3 characters that are not in `stopwords`
    - the exact token "URLTOKEN" always survives, in its place
    >>> ex03_tokenize("free URLTOKEN offer to you", {"you"})
    ['free', 'URLTOKEN', 'offer']
    """
    raise NotImplementedError("TODO ex03")


def ex04_ngrams(tokens, n_min=1, n_max=2):
    """Every n-gram with n_min <= n <= n_max, words joined by one space.
    All the 1-grams first (in order), then all the 2-grams (in order), and so on.
    >>> ex04_ngrams(["click", "here", "now"], 1, 2)
    ['click', 'here', 'now', 'click here', 'here now']
    Theory 3.6
    """
    raise NotImplementedError("TODO ex04")


def ex05_idf_value(n_documents, document_frequency):
    """idf = log(N / (1 + df)) + 1      (natural log)
    Theory 3.3
    """
    raise NotImplementedError("TODO ex05")


def ex06_build_vocabulary(token_lists, max_features):
    """The `max_features` terms with the highest DOCUMENT frequency (count each term once per document).

    Order: highest document frequency first; equal frequencies in alphabetical order.
    Theory 3.4
    """
    raise NotImplementedError("TODO ex06")


def ex07_tfidf(tokens, idf):
    """TF-IDF vector of one document as a dict {term: value}, L2-normalised.

    tf = count of the term in the document / number of tokens in the document.
    Tokens that are not keys of `idf` are dropped BEFORE counting.
    An empty result (no known tokens) -> {}.
    Theory 3.3 and 3.5
    """
    raise NotImplementedError("TODO ex07")


# ---------------------------------------------------------------- Naive Bayes (notebook 02)

def ex08_nb_fit(documents, labels, alpha=1.0):
    """Train Multinomial Naive Bayes.

    documents: list of token lists. labels: list of HAM / SPAM.
    Returns (log_prior, log_likelihood):
        log_prior[c]         = log(number of documents of class c / number of documents)
        log_likelihood[c][w] = log((count of w in class c + alpha) / (total tokens in c + alpha * |V|))
    for c in (HAM, SPAM) and every w in the vocabulary V (all words of all documents).
    Theory 4.4 - 4.5
    """
    raise NotImplementedError("TODO ex08")


def ex09_nb_log_scores(tokens, log_prior, log_likelihood):
    """{HAM: score, SPAM: score} with score(c) = log_prior[c] + sum of log_likelihood[c][t].
    Tokens that are not in the vocabulary are skipped. Repeated tokens count every time.
    Theory 4.6
    """
    raise NotImplementedError("TODO ex09")


def ex10_proba_spam(scores):
    """P(spam) from the two log scores, without underflow or overflow:
        1 / (1 + exp(scores[HAM] - scores[SPAM]))
    If the difference is > 700 return 0.0; if < -700 return 1.0.
    Theory 4.7
    """
    raise NotImplementedError("TODO ex10")


def ex11_explain(tokens, log_likelihood, top_n=5):
    """The reasons for a verdict: list of (token, log_odds), log_odds = loglik[SPAM][t] - loglik[HAM][t].

    - each distinct token once (in order of first appearance before sorting)
    - unknown tokens are left out
    - sorted by ABSOLUTE log-odds, largest first (Python's sort is stable: keep the first-appearance
      order for equal values)
    - at most top_n items
    Theory 4.8
    """
    raise NotImplementedError("TODO ex11")


# ---------------------------------------------------------------- threshold (notebook 03)

def ex12_precision_recall_at(probs, labels, threshold):
    """Precision and recall of the SPAM class when "spam" means prob >= threshold.
    Returns (precision, recall). Nothing predicted spam -> precision 1.0. No real spam -> recall 0.0.
    Theory 6.1 - 6.2
    """
    raise NotImplementedError("TODO ex12")


def ex13_choose_threshold(probs, labels, thresholds, min_precision=0.98):
    """Among `thresholds`, the one with the HIGHEST RECALL whose precision >= min_precision.
    On equal recall keep the earlier threshold. Returns (threshold, precision, recall).
    No threshold reaches the floor -> raise ValueError.
    Theory 6.3
    """
    raise NotImplementedError("TODO ex13")
