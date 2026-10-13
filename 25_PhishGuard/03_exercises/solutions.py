"""PhishGuard - solutions to exercises.py.

Try first. Then compare: there is more than one correct way to write each one.
To run the tests against these solutions:  EXERCISES=solutions pytest test_exercises.py
"""
import math
import re
from collections import Counter
from urllib.parse import urlparse

import numpy as np

COMMON_TLDS = ("com", "org", "net", "edu", "gov", "il", "co.il", "ac.il", "uk", "de")
BRAND_WORDS = ("paypal", "apple", "microsoft", "amazon", "google", "facebook", "netflix", "bank")
IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def ex01_split_host(host):
    labels = [l for l in host.lower().split(".") if l]
    n_tld = 2 if len(labels) >= 3 and ".".join(labels[-2:]) in COMMON_TLDS else 1
    if len(labels) <= n_tld:
        return [], host, ""
    return labels[:-n_tld - 1], labels[-n_tld - 1], ".".join(labels[-n_tld:])


def _host(url):
    url = url.strip()
    try:
        return (urlparse(url if "://" in url else "http://" + url).hostname or "").lower()
    except ValueError:
        return ""


def ex02_has_ip_host(url):
    return bool(IP_PATTERN.match(_host(url)))


def ex03_entropy(text):
    if not text:
        return 0.0
    n = len(text)
    return sum(c / n * math.log2(n / c) for c in Counter(text).values())


def ex04_brand_in_subdomain(url):
    host = _host(url)
    if IP_PATTERN.match(host):
        return 0.0
    subs, domain, _ = ex01_split_host(host)
    sub = ".".join(subs)
    return float(any(b in sub for b in BRAND_WORDS) and not any(b in domain for b in BRAND_WORDS))


def ex05_sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))


def ex06_log_loss(y, p):
    p = np.clip(np.asarray(p, dtype=float), 1e-12, 1 - 1e-12)
    y = np.asarray(y, dtype=float)
    return float(-np.mean(y * np.log(p) + (1 - y) * np.log(1 - p)))


def ex07_gradient(X, y, w, b):
    p = ex05_sigmoid(X @ w + b)
    error = p - y
    return X.T @ error / len(y), float(error.mean())


def ex08_fit_logistic(X, y, lr=0.5, epochs=2000):
    w, b = np.zeros(X.shape[1]), 0.0
    for _ in range(epochs):
        gw, gb = ex07_gradient(X, y, w, b)
        w -= lr * gw
        b -= lr * gb
    return w, b


def _gini(counts):
    total = sum(counts)
    return 1 - sum((c / total) ** 2 for c in counts) if total else 0.0


def ex09_gini_gain(parent, left, right):
    n = sum(parent)
    return _gini(parent) - (sum(left) / n * _gini(left) + sum(right) / n * _gini(right))


def ex10_recall_precision(p, y, threshold):
    p, y = np.asarray(p), np.asarray(y)
    pred = p >= threshold
    tp = np.sum(pred & (y == 1))
    fn = np.sum(~pred & (y == 1))
    fp = np.sum(pred & (y == 0))
    recall = tp / (tp + fn) if tp + fn else 0.0
    precision = tp / (tp + fp) if tp + fp else 1.0
    return float(recall), float(precision)


def ex11_choose_threshold(p, y, target_recall=0.95):
    for i in range(99, 0, -1):
        t = round(i / 100, 2)
        if ex10_recall_precision(p, y, t)[0] >= target_recall:
            return t
    return 0.0


def ex12_auc(p, y):
    p, y = np.asarray(p, dtype=float), np.asarray(y)
    order = np.argsort(-p, kind="stable")
    p, y = p[order], y[order]
    n_pos, n_neg = np.sum(y == 1), np.sum(y == 0)
    area, tpr, fpr, i = 0.0, 0.0, 0.0, 0
    while i < len(p):
        j = i
        while j < len(p) and p[j] == p[i]:            # one step per distinct score
            j += 1
        new_tpr = tpr + np.sum(y[i:j] == 1) / n_pos
        new_fpr = fpr + np.sum(y[i:j] == 0) / n_neg
        area += (new_fpr - fpr) * (new_tpr + tpr) / 2
        tpr, fpr, i = new_tpr, new_fpr, j
    return float(area)
