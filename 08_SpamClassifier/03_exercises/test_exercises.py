"""Automatic checks for exercises.py.   Run:  pytest test_exercises.py -v

Every test is named after its exercise, so  pytest -k ex08  runs just that one.
"""
import importlib
import math
import os
import random

import pytest

ex = importlib.import_module(os.environ.get("EXERCISES", "exercises"))
HAM, SPAM = 0, 1

SPAM_DOCS = [["free", "money", "now"], ["free", "prize", "winner"]]
HAM_DOCS = [["meeting", "tomorrow", "office"], ["project", "meeting", "notes"]]
DOCS = SPAM_DOCS + HAM_DOCS
LABELS = [SPAM, SPAM, HAM, HAM]


def test_ex01_caps_ratio():
    assert ex.ex01_caps_ratio("FREE money 100!") == pytest.approx(4 / 9)
    assert ex.ex01_caps_ratio("ABC") == 1.0
    assert ex.ex01_caps_ratio("123 !!!") == 0.0
    assert ex.ex01_caps_ratio("") == 0.0


def test_ex02_strip_html_keeps_words_apart():
    assert ex.ex02_strip_html("<b>free</b><i>offer</i>  now") == "free offer now"
    assert ex.ex02_strip_html('<a href="x">click</a>here') == "click here"
    assert ex.ex02_strip_html("no tags") == "no tags"


def test_ex03_tokenize():
    stop = {"the", "you", "and"}
    assert ex.ex03_tokenize("free URLTOKEN offer to you", stop) == ["free", "URLTOKEN", "offer"]
    assert ex.ex03_tokenize("the and you go to it", stop) == []
    assert ex.ex03_tokenize("URLTOKEN", stop) == ["URLTOKEN"]
    assert ex.ex03_tokenize("don't stop", stop) == ["don't", "stop"]


def test_ex04_ngrams():
    assert ex.ex04_ngrams(["click", "here", "now"], 1, 2) == ["click", "here", "now", "click here", "here now"]
    assert ex.ex04_ngrams(["a", "b", "c"], 2, 3) == ["a b", "b c", "a b c"]
    assert ex.ex04_ngrams(["solo"], 1, 2) == ["solo"]


def test_ex05_idf_value():
    assert ex.ex05_idf_value(1000, 999) == pytest.approx(1.0)
    assert ex.ex05_idf_value(1000, 5) == pytest.approx(math.log(1000 / 6) + 1)


def test_ex06_vocabulary_counts_documents_not_occurrences():
    docs = [["shout"] * 50, ["free", "win"], ["free", "call"], ["free", "win"]]
    assert ex.ex06_build_vocabulary(docs, 3) == ["free", "win", "call"]   # call and shout tie at 1 -> alphabetical


def test_ex07_tfidf_by_hand():
    idf = {"free": 1.0, "prize": math.log(3 / 2) + 1}
    v = ex.ex07_tfidf(["free", "prize", "free", "unknown"], idf)
    raw_free, raw_prize = 2 / 3 * 1.0, 1 / 3 * idf["prize"]
    norm = math.hypot(raw_free, raw_prize)
    assert set(v) == {"free", "prize"}
    assert v["free"] == pytest.approx(raw_free / norm)
    assert v["prize"] == pytest.approx(raw_prize / norm)
    assert math.fsum(x * x for x in v.values()) == pytest.approx(1.0)
    assert ex.ex07_tfidf(["nothing", "known"], idf) == {}


def test_ex07_long_and_short_are_comparable():
    idf = {"free": 1.5, "prize": 2.0}
    short = ex.ex07_tfidf(["free", "prize"], idf)
    long_ = ex.ex07_tfidf(["free", "prize"] * 100, idf)
    assert short == pytest.approx(long_)


def test_ex08_nb_fit_worked_example():
    log_prior, ll = ex.ex08_nb_fit(DOCS, LABELS, alpha=1.0)
    assert log_prior[SPAM] == pytest.approx(math.log(0.5))
    assert math.exp(ll[SPAM]["free"]) == pytest.approx(3 / 16)
    assert math.exp(ll[HAM]["free"]) == pytest.approx(1 / 16)
    assert len(ll[SPAM]) == len(ll[HAM]) == 10
    for c in (HAM, SPAM):
        assert math.fsum(math.exp(v) for v in ll[c].values()) == pytest.approx(1.0)


def test_ex09_log_scores_skip_unknown_and_count_repeats():
    log_prior, ll = ex.ex08_nb_fit(DOCS, LABELS)
    s1 = ex.ex09_nb_log_scores(["free"], log_prior, ll)
    s2 = ex.ex09_nb_log_scores(["free", "never-seen"], log_prior, ll)
    s3 = ex.ex09_nb_log_scores(["free", "free"], log_prior, ll)
    assert s1 == pytest.approx(s2)
    assert s3[SPAM] == pytest.approx(log_prior[SPAM] + 2 * ll[SPAM]["free"])


def test_ex10_proba_no_underflow_or_overflow():
    assert ex.ex10_proba_spam({HAM: -10.0, SPAM: -10.0}) == pytest.approx(0.5)
    assert ex.ex10_proba_spam({HAM: -2496.0, SPAM: -1750.0}) == 1.0
    assert ex.ex10_proba_spam({HAM: -1750.0, SPAM: -2496.0}) == 0.0
    assert ex.ex10_proba_spam({HAM: -11.0, SPAM: -10.0}) == pytest.approx(1 / (1 + math.exp(-1)))


def test_ex08_to_ex10_match_sklearn():
    np = pytest.importorskip("numpy")
    nb = pytest.importorskip("sklearn.naive_bayes")
    rnd = random.Random(0)
    words = [f"w{i}" for i in range(40)]
    docs = [[rnd.choice(words[:25] if i % 2 else words[15:]) for _ in range(rnd.randint(3, 15))] for i in range(200)]
    labels = [i % 2 for i in range(200)]
    log_prior, ll = ex.ex08_nb_fit(docs, labels)
    vocab = sorted(ll[SPAM])
    col = {w: j for j, w in enumerate(vocab)}
    X = np.zeros((len(docs), len(vocab)))
    for r, d in enumerate(docs):
        for t in d:
            X[r, col[t]] += 1
    ref = nb.MultinomialNB(alpha=1.0).fit(X, labels).predict_proba(X)[:, 1]
    ours = [ex.ex10_proba_spam(ex.ex09_nb_log_scores(d, log_prior, ll)) for d in docs]
    assert max(abs(a - b) for a, b in zip(ours, ref)) < 1e-9


def test_ex11_explain():
    _, ll = ex.ex08_nb_fit(DOCS, LABELS)
    reasons = ex.ex11_explain(["free", "free", "meeting", "unknown", "now"], ll, top_n=5)
    tokens = [t for t, _ in reasons]
    # free (+log 3) and meeting (-log 3) have equal size, so first appearance decides; "now" is smaller
    assert tokens == ["free", "meeting", "now"]
    assert dict(reasons)["free"] == pytest.approx(math.log(3))
    assert dict(reasons)["meeting"] == pytest.approx(-math.log(3))
    assert len(ex.ex11_explain(["free", "meeting", "now"], ll, top_n=2)) == 2


def test_ex12_precision_recall_at():
    probs = [0.9, 0.8, 0.7, 0.4, 0.2]
    labels = [SPAM, HAM, SPAM, SPAM, HAM]
    assert ex.ex12_precision_recall_at(probs, labels, 0.5) == pytest.approx((2 / 3, 2 / 3))
    assert ex.ex12_precision_recall_at(probs, labels, 0.85) == pytest.approx((1.0, 1 / 3))
    assert ex.ex12_precision_recall_at(probs, labels, 0.95) == pytest.approx((1.0, 0.0))


def test_ex13_choose_threshold():
    probs = [0.99, 0.95, 0.9, 0.85, 0.7, 0.6, 0.3]
    labels = [SPAM, SPAM, SPAM, HAM, SPAM, HAM, HAM]
    ts = [0.5, 0.6, 0.7, 0.8, 0.9]
    t, p, r = ex.ex13_choose_threshold(probs, labels, ts, min_precision=0.98)
    assert t == 0.9 and p == 1.0 and r == pytest.approx(3 / 4)
    t, p, r = ex.ex13_choose_threshold(probs, labels, ts, min_precision=0.75)
    assert t == 0.7 and r == 1.0
    with pytest.raises(ValueError):
        ex.ex13_choose_threshold([0.9, 0.9], [HAM, HAM], ts)
