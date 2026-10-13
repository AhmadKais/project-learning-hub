"""Automatic checks for exercises.py.   Run:  pytest test_exercises.py -v

Every test is named after its exercise, so  pytest -k ex10  runs just that one.
"""
import importlib
import math
import os
import random

import pytest

ex = importlib.import_module(os.environ.get("EXERCISES", "exercises"))


def test_ex01_scrub():
    out = ex.ex01_scrub("Mail noa@x.com or 054-1234567, thanks")
    assert "@" not in out and "1234567" not in out
    assert out.split() == ["Mail", "or", ",", "thanks"]
    assert "972" not in ex.ex01_scrub("call +972 50 123 4567 today")
    assert ex.ex01_scrub("Python 3 since 2019").split() == ["Python", "3", "since", "2019"]   # short numbers stay


def test_ex01_replaces_with_a_space():
    assert ex.ex01_scrub("hello@a.com").strip() == ""
    assert ex.ex01_scrub("word noa@x.com word").split() == ["word", "word"]
    assert ex.ex01_scrub("tel 0541234567").split() == ["tel"]


def test_ex02_tokenize_keeps_technical_tokens():
    assert ex.ex02_tokenize("I know C++, C# and Node.js. I love Python.") == \
        ["i", "know", "c++", "c#", "and", "node.js", "i", "love", "python"]
    assert ex.ex02_tokenize("Python. Python") == ["python", "python"]
    assert ex.ex02_tokenize("3.5 years") == ["years"]


def test_ex03_add_bigrams():
    assert ex.ex03_add_bigrams(["machin", "learn", "python"]) == \
        ["machin", "learn", "python", "machin learn", "learn python"]
    assert ex.ex03_add_bigrams(["solo"]) == ["solo"]
    assert ex.ex03_add_bigrams([]) == []


def test_ex04_document_frequency_counts_documents_not_occurrences():
    df = ex.ex04_document_frequency([["python", "python", "django"], ["python", "java"], ["sql"]])
    assert df["python"] == 2 and df["django"] == 1 and df["sql"] == 1


def test_ex05_idf_matches_theory():
    assert ex.ex05_idf(2, 3) == pytest.approx(1.2877, abs=1e-4)
    assert ex.ex05_idf(1, 3) == pytest.approx(1.6931, abs=1e-4)
    assert ex.ex05_idf(3, 3) == pytest.approx(1.0)


def test_ex06_unit_vector():
    v = ex.ex06_tfidf_unit_vector(["python", "python", "django", "unknown"], {"python": 1.0, "django": 2.0})
    assert set(v) == {"python", "django"}
    assert v["python"] == pytest.approx(v["django"])         # 2 * 1.0 == 1 * 2.0
    assert math.fsum(x * x for x in v.values()) == pytest.approx(1.0)
    assert ex.ex06_tfidf_unit_vector(["nothing"], {"python": 1.0}) == {}


def test_ex07_cosine():
    a = {"python": 2.0, "django": 1.0}
    assert ex.ex07_cosine(a, {"python": 4.0, "django": 2.0}) == pytest.approx(1.0)   # same direction
    assert ex.ex07_cosine(a, {"java": 1.0}) == 0.0
    assert ex.ex07_cosine({}, a) == 0.0
    assert ex.ex07_cosine({"x": 1.0, "y": 0.0}, {"x": 1.0, "y": 1.0}) == pytest.approx(1 / math.sqrt(2))


def test_ex08_explanation_sums_to_the_score():
    rnd = random.Random(1)
    words = [f"t{i}" for i in range(30)]
    idf = {w: rnd.uniform(1, 4) for w in words}
    r = ex.ex06_tfidf_unit_vector([rnd.choice(words) for _ in range(40)], idf)
    j = ex.ex06_tfidf_unit_vector([rnd.choice(words) for _ in range(10)], idf)
    parts = ex.ex08_contributions(r, j)
    assert math.fsum(v for _, v in parts) == pytest.approx(ex.ex07_cosine(r, j), abs=1e-9)
    values = [v for _, v in parts]
    assert values == sorted(values, reverse=True)


def test_ex09_bm25_idf_is_positive():
    assert ex.ex09_bm25_idf(150, 200) > 0
    assert ex.ex09_bm25_idf(195, 200) > 0
    assert ex.ex09_bm25_idf(5, 200) == pytest.approx(math.log(195.5 / 5.5 + 1))


def test_ex10_saturation_and_length():
    s = lambda tf, length=100: ex.ex10_bm25_term_score(tf, length, 100, 1.0)
    assert s(1) == pytest.approx(1.0)                         # tf=1 at average length -> idf
    assert s(2) == pytest.approx(2 * 2.5 / 3.5)
    assert s(1000) < 2.5                                      # never above k1 + 1
    assert s(1, 400) < s(1, 100) < s(1, 25)                    # longer -> lower
    no_len = lambda length: ex.ex10_bm25_term_score(3, length, 100, 1.0, b=0.0)
    assert no_len(400) == pytest.approx(no_len(25))            # b = 0 ignores length


def test_ex11_bm25_rank_and_touched():
    docs = [["python", "django", "python"], ["java", "spring"], ["python", "sql"], ["css", "html"]]
    scores, touched = ex.ex11_bm25_rank(docs, ["python", "python", "django"])
    assert touched == {0, 2}
    assert scores[1] == scores[3] == 0.0
    assert scores[0] > scores[2] > 0
    n, avgdl = 4, 9 / 4
    idf_py = math.log((n - 2 + 0.5) / (2 + 0.5) + 1)
    idf_dj = math.log((n - 1 + 0.5) / (1 + 0.5) + 1)
    expected0 = (idf_py * 2 * 2.5 / (2 + 1.5 * (0.25 + 0.75 * 3 / avgdl))
                 + idf_dj * 1 * 2.5 / (1 + 1.5 * (0.25 + 0.75 * 3 / avgdl)))
    assert scores[0] == pytest.approx(expected0)


def test_ex12_precision_at_k():
    ranking, relevant = ["C3", "C7", "C1", "C9"], {"C1", "C7"}
    assert ex.ex12_precision_at_k(ranking, relevant, 2) == 0.5
    assert ex.ex12_precision_at_k(ranking, relevant, 4) == 0.5
    assert ex.ex12_precision_at_k(["C7"], relevant, 10) == pytest.approx(0.1)    # denominator is k


def test_ex13_mrr():
    rankings = [["C3", "C7", "C1"], ["C1", "C2"], ["C5", "C6"]]
    relevants = [{"C1", "C7"}, {"C1"}, {"C9"}]
    assert ex.ex13_mean_reciprocal_rank(rankings, relevants) == pytest.approx((0.5 + 1.0 + 0.0) / 3)
