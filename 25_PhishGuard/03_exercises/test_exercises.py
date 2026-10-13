"""Automatic checks for exercises.py.   Run:  pytest test_exercises.py -v

Every test is named after its exercise, so  pytest -k ex07  runs just that one.
"""
import importlib
import math
import os

import numpy as np
import pytest

ex = importlib.import_module(os.environ.get("EXERCISES", "exercises"))
rng = np.random.default_rng(7)


def test_ex01_split_host():
    assert ex.ex01_split_host("paypal.com.secure-login.xyz") == (["paypal", "com"], "secure-login", "xyz")
    assert ex.ex01_split_host("www.mail.paypal.com") == (["www", "mail"], "paypal", "com")
    assert ex.ex01_split_host("www.bankhapoalim.co.il") == (["www"], "bankhapoalim", "co.il")
    assert ex.ex01_split_host("example.com") == ([], "example", "com")
    assert ex.ex01_split_host("localhost") == ([], "localhost", "")


def test_ex02_has_ip_host():
    assert ex.ex02_has_ip_host("http://192.168.4.77/login") is True
    assert ex.ex02_has_ip_host("http://amazon.com@203.0.113.55/prize") is True
    assert ex.ex02_has_ip_host("1.2.3.4/x") is True
    assert ex.ex02_has_ip_host("https://www.google.com/") is False
    assert ex.ex02_has_ip_host("http://v1.2.3.example.com/") is False


def test_ex03_entropy():
    assert ex.ex03_entropy("aaaa") == 0.0
    assert ex.ex03_entropy("aaab") == pytest.approx(0.8113, abs=1e-4)
    assert ex.ex03_entropy("abab") == pytest.approx(1.0)
    assert ex.ex03_entropy("abcdefgh") == pytest.approx(3.0)
    assert ex.ex03_entropy("") == 0.0


def test_ex04_brand_in_subdomain():
    assert ex.ex04_brand_in_subdomain("http://paypal.com.secure-login.xyz/verify") == 1.0
    assert ex.ex04_brand_in_subdomain("https://www.paypal.com/signin") == 0.0
    assert ex.ex04_brand_in_subdomain("https://www.google.com/") == 0.0
    assert ex.ex04_brand_in_subdomain("http://login.apple.id-check.top/") == 1.0


def test_ex05_sigmoid():
    assert ex.ex05_sigmoid(0) == pytest.approx(0.5)
    assert ex.ex05_sigmoid(5) == pytest.approx(0.9933, abs=1e-4)
    assert ex.ex05_sigmoid(0.35) == pytest.approx(0.587, abs=1e-3)
    out = ex.ex05_sigmoid(np.array([-1000.0, 0.0, 1000.0]))
    assert out[0] == pytest.approx(0.0) and out[2] == pytest.approx(1.0)


def test_ex06_log_loss():
    assert ex.ex06_log_loss([1], [0.76]) == pytest.approx(-math.log(0.76))
    assert ex.ex06_log_loss([0], [0.08]) == pytest.approx(-math.log(0.92))
    assert ex.ex06_log_loss([1, 0], [0.5, 0.5]) == pytest.approx(math.log(2))
    assert np.isfinite(ex.ex06_log_loss([1, 0], [0.0, 1.0]))


def test_ex07_gradient_matches_numerical_derivative():
    X = rng.normal(size=(50, 3)); y = (rng.random(50) > 0.5).astype(float)
    w, b = rng.normal(size=3), 0.3
    gw, gb = ex.ex07_gradient(X, y, w, b)
    loss = lambda w_, b_: ex.ex06_log_loss(y, 1 / (1 + np.exp(-(X @ w_ + b_))))
    h = 1e-6
    for i in range(3):
        e = np.zeros(3); e[i] = h
        assert gw[i] == pytest.approx((loss(w + e, b) - loss(w - e, b)) / (2 * h), abs=1e-6)
    assert gb == pytest.approx((loss(w, b + h) - loss(w, b - h)) / (2 * h), abs=1e-6)


def test_ex08_fit_logistic_learns():
    X = rng.normal(size=(400, 2))
    y = (X[:, 0] - 2 * X[:, 1] + rng.normal(0, .3, 400) > 0).astype(float)
    w, b = ex.ex08_fit_logistic(X, y)
    acc = np.mean((1 / (1 + np.exp(-(X @ w + b))) >= .5) == y)
    assert acc > 0.9
    assert w[0] > 0 > w[1]                              # it found the directions


def test_ex09_gini_gain():
    assert ex.ex09_gini_gain([5, 5], [4, 1], [1, 4]) == pytest.approx(0.18)
    assert ex.ex09_gini_gain([5, 5], [3, 3], [2, 2]) == pytest.approx(0.0)
    assert ex.ex09_gini_gain([8, 2], [8, 0], [0, 2]) == pytest.approx(0.32)   # perfect split


def test_ex10_recall_precision():
    p = [0.9, 0.8, 0.6, 0.4, 0.2]
    y = [1, 0, 1, 1, 0]
    assert ex.ex10_recall_precision(p, y, 0.5) == pytest.approx((2 / 3, 2 / 3))
    assert ex.ex10_recall_precision(p, y, 0.3) == pytest.approx((1.0, 3 / 4))
    assert ex.ex10_recall_precision(p, y, 0.95) == pytest.approx((0.0, 1.0))


def test_ex11_choose_threshold_takes_the_highest():
    p = np.array([0.95, 0.9, 0.7, 0.45, 0.3, 0.2, 0.1])
    y = np.array([1, 1, 1, 1, 0, 1, 0])
    assert ex.ex11_choose_threshold(p, y, 0.8) == 0.45      # 4 of the 5 phishing URLs have p >= 0.45
    assert ex.ex11_choose_threshold(p, y, 1.0) == 0.2
    assert ex.ex11_choose_threshold(p, y, 0.4) == 0.9


def test_ex12_auc_matches_sklearn():
    metrics = pytest.importorskip("sklearn.metrics")
    for _ in range(10):
        y = (rng.random(200) > 0.4).astype(int)
        p = np.round(np.clip(y * 0.3 + rng.random(200) * 0.7, 0, 1), 1)      # rounding -> many ties
        assert ex.ex12_auc(p, y) == pytest.approx(metrics.roc_auc_score(y, p))
    assert ex.ex12_auc([0.9, 0.8, 0.2, 0.1], [1, 1, 0, 0]) == pytest.approx(1.0)
    assert ex.ex12_auc([0.5, 0.5, 0.5, 0.5], [1, 0, 1, 0]) == pytest.approx(0.5)
