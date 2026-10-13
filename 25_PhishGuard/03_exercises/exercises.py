"""PhishGuard - exercises.

Fill in every function marked TODO. Use the standard library and numpy.
Check yourself after each exercise:

    pytest test_exercises.py -k ex01 -v        # one exercise
    pytest test_exercises.py -v                # all of them

Stuck for more than 20 minutes? Re-read the theory section named in the
docstring, look at the notebook, and only then open solutions.py.
"""
import math
import re
from collections import Counter
from urllib.parse import urlparse

import numpy as np

COMMON_TLDS = ("com", "org", "net", "edu", "gov", "il", "co.il", "ac.il", "uk", "de")
BRAND_WORDS = ("paypal", "apple", "microsoft", "amazon", "google", "facebook", "netflix", "bank")
IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


# ---------------------------------------------------------------- features (notebook 01)

def ex01_split_host(host):
    """Split a host name, reading from the RIGHT. Returns (subdomains, domain, tld).

    - the last label is the TLD, or the last TWO if they form a two-part TLD in COMMON_TLDS (e.g. "co.il")
      and there are at least 3 labels
    - the label before the TLD is the domain; everything before it is the list of subdomains
    - a host with only one label (e.g. "localhost") -> ([], host, "")
    >>> ex01_split_host("paypal.com.secure-login.xyz")
    (['paypal', 'com'], 'secure-login', 'xyz')
    Theory 3.1
    """
    raise NotImplementedError("TODO ex01")


def ex02_has_ip_host(url):
    """True if the host of the URL is an IPv4 address. Remember: the browser ignores everything before "@".
    A URL without a scheme ("1.2.3.4/x") must work too.
    Theory 3.1 (the @ trick)
    """
    raise NotImplementedError("TODO ex02")


def ex03_entropy(text):
    """Shannon entropy in bits: -sum p(c) * log2 p(c). Empty text -> 0.0.
    "aaab" -> 0.811,  "abcdefgh" -> 3.0
    Theory 3.5
    """
    raise NotImplementedError("TODO ex03")


def ex04_brand_in_subdomain(url):
    """1.0 if a BRAND_WORD appears in the subdomains (joined with ".") but NOT in the domain, else 0.0.
    "http://paypal.com.secure-login.xyz/" -> 1.0     "https://www.paypal.com/" -> 0.0
    """
    raise NotImplementedError("TODO ex04")


# ---------------------------------------------------------------- logistic regression (notebook 02)

def ex05_sigmoid(z):
    """1 / (1 + e^-z), for a number or a numpy array. Must not overflow for z = -1000 (hint: np.exp of a huge
    positive number is inf, and 1 / (1 + inf) = 0 is fine - but avoid the RuntimeWarning by clipping z to
    [-500, 500])."""
    raise NotImplementedError("TODO ex05")


def ex06_log_loss(y, p):
    """Mean log-loss: mean of -[y ln p + (1 - y) ln(1 - p)]. Clip p to [1e-12, 1 - 1e-12] first.
    Theory 4.2
    """
    raise NotImplementedError("TODO ex06")


def ex07_gradient(X, y, w, b):
    """Gradient of the MEAN log-loss of logistic regression (no regularisation).

    p = sigmoid(X @ w + b);  grad_w = X.T @ (p - y) / n;  grad_b = mean(p - y)
    Returns (grad_w, grad_b).  "Error times input" - theory 4.2
    """
    raise NotImplementedError("TODO ex07")


def ex08_fit_logistic(X, y, lr=0.5, epochs=2000):
    """Gradient descent from w = 0, b = 0 using ex07. Returns (w, b)."""
    raise NotImplementedError("TODO ex08")


# ---------------------------------------------------------------- trees (notebook 02)

def ex09_gini_gain(parent, left, right):
    """Gini gain of a split. Each argument is a list of class counts, e.g. [5, 5].

    gini(counts) = 1 - sum((c / total) ** 2);   gain = gini(parent) - weighted average of the children's gini
    (weights = share of the parent's items in each child).
    >>> round(ex09_gini_gain([5, 5], [4, 1], [1, 4]), 2)
    0.18
    Theory 4.5
    """
    raise NotImplementedError("TODO ex09")


# ---------------------------------------------------------------- evaluation (notebook 03)

def ex10_recall_precision(p, y, threshold):
    """Phishing = p >= threshold. Returns (recall, precision). No positive predictions -> precision 1.0.
    No real phishing -> recall 0.0.
    """
    raise NotImplementedError("TODO ex10")


def ex11_choose_threshold(p, y, target_recall=0.95):
    """The HIGHEST threshold in 0.99, 0.98, ..., 0.01 whose recall >= target_recall. If none: 0.0.
    Use round(t, 2) when generating the thresholds so 0.29 is exactly 0.29.
    Theory 5.1
    """
    raise NotImplementedError("TODO ex11")


def ex12_auc(p, y):
    """Area under the ROC curve, from scratch.

    Sort by p descending; walk down the list; recall (TPR) and false-alarm rate (FPR) grow; add the area of each
    trapezoid. Rows with the SAME p must be added in one step (otherwise ties give a staircase that depends on
    the order). Must equal sklearn.metrics.roc_auc_score.
    Theory 5.2
    """
    raise NotImplementedError("TODO ex12")
