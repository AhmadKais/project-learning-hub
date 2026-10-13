# %% [markdown]
# # 01 · A URL as 20 numbers
#
# **Read first:** `01_theory/03_features.md`
#
# 1. parse a URL the way a browser does — the **registered domain is read from the right**
# 2. Shannon entropy, by hand and in code
# 3. the 20 features — checked against the hand-computed table of theory §3.3
# 4. on 11,430 real URLs: which features separate phishing from legitimate **before any model**?

# %%
import csv
import math
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlparse

import numpy as np

SUSPICIOUS_WORDS = ("login", "signin", "verify", "verification", "secure", "account", "update", "confirm",
                    "banking", "password", "wallet", "paypal", "ebay", "apple", "microsoft", "amazon",
                    "free", "bonus", "prize", "urgent", "suspended")
COMMON_TLDS = ("com", "org", "net", "edu", "gov", "il", "co.il", "ac.il", "uk", "de")
SUSPICIOUS_TLDS = ("xyz", "top", "tk", "ml", "ga", "cf", "gq", "buzz", "click", "loan", "work")
URL_SHORTENERS = ("bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "cutt.ly")
BRAND_WORDS = ("paypal", "apple", "microsoft", "amazon", "google", "facebook", "netflix", "bank")
IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

# %% [markdown]
# ## 1. Parsing — read the host from the RIGHT
#
# Last label = TLD (or the last two for two-part TLDs like `co.il`), the one before = the domain, everything
# else = subdomains that the domain's owner chose.

# %%
@dataclass
class ParsedURL:
    url: str
    scheme: str = ""
    host: str = ""
    subdomains: list = field(default_factory=list)
    domain: str = ""
    tld: str = ""
    port: int = None
    path: str = ""
    query: str = ""
    has_ip_host: bool = False

def parse(url):
    raw = url.strip()
    had_scheme = "://" in raw
    try:
        p = urlparse(raw if had_scheme else "http://" + raw)
        host = (p.hostname or "").lower()
        port = p.port
    except ValueError:                       # garbage input must never crash the scanner
        return ParsedURL(url)
    out = ParsedURL(url, scheme=p.scheme if had_scheme else "", host=host, port=port, path=p.path, query=p.query)
    if IP_PATTERN.match(host):
        out.has_ip_host, out.domain = True, host
        return out
    labels = [l for l in host.split(".") if l]
    n_tld = 2 if len(labels) >= 3 and ".".join(labels[-2:]) in COMMON_TLDS else 1
    if len(labels) > n_tld:
        out.tld = ".".join(labels[-n_tld:])
        out.domain = labels[-n_tld - 1]
        out.subdomains = labels[:-n_tld - 1]
    else:
        out.domain = host
    return out

for u in ("https://www.mail.paypal.com/signin?country=il#top",
          "http://paypal.com.secure-login.xyz/verify/account",
          "https://www.bankhapoalim.co.il/",
          "http://amazon.com@203.0.113.55/prize/claim",
          "paypal.com/x"):
    p = parse(u)
    owner = f"{p.domain}.{p.tld}" if p.tld else p.domain
    print(f"{u}\n   owner: {owner}   subdomains: {p.subdomains}   ip: {p.has_ip_host}   scheme: '{p.scheme}'")

# %% [markdown]
# Look at the 4th one: `amazon.com@203.0.113.55` — the browser ignores everything before `@`, so the real host
# is an **IP address**. A human reading from the left sees "amazon.com".
#
# ## 2. Shannon entropy
#
# $$ H = -\sum_c p(c)\,\log_2 p(c) \qquad p(c) = \frac{\text{count}(c)}{\text{length}} $$

# %%
def shannon_entropy(text):
    if not text:
        return 0.0
    n = len(text)
    return sum(c / n * math.log2(n / c) for c in Counter(text).values())     # = -sum p log2 p

for s in ("aaaa", "aaab", "abab", "abcdefgh", "/signin", "/8fa9q2z7"):
    print(f"{s:10s} H = {shannon_entropy(s):.3f}")

# %% [markdown]
# ## 3. The 20 features

# %%
FEATURE_NAMES = ["url_length", "host_length", "path_length", "num_dots", "num_hyphens", "num_underscores",
                 "num_slashes", "num_digits", "digit_ratio", "num_subdomains", "num_query_params",
                 "has_ip_host", "has_at_symbol", "has_https", "has_port", "suspicious_word_count",
                 "suspicious_tld", "is_shortener", "entropy", "brand_in_subdomain"]

def extract(url):
    p = parse(url)
    low = url.lower()
    after_scheme = url.split("://", 1)[1] if "://" in url else url
    digits = sum(ch.isdigit() for ch in url)
    sub = ".".join(p.subdomains)
    return {
        "url_length": len(url), "host_length": len(p.host), "path_length": len(p.path),
        "num_dots": url.count("."), "num_hyphens": url.count("-"), "num_underscores": url.count("_"),
        "num_slashes": after_scheme.count("/"), "num_digits": digits,
        "digit_ratio": digits / len(url) if url else 0.0,
        "num_subdomains": len(p.subdomains),
        "num_query_params": len([q for q in p.query.split("&") if q]),
        "has_ip_host": float(p.has_ip_host), "has_at_symbol": float("@" in url),
        "has_https": float(p.scheme == "https"), "has_port": float(p.port is not None),
        "suspicious_word_count": sum(w in low for w in SUSPICIOUS_WORDS),
        "suspicious_tld": float(p.tld in SUSPICIOUS_TLDS), "is_shortener": float(p.host in URL_SHORTENERS),
        "entropy": shannon_entropy(url),
        "brand_in_subdomain": float(any(b in sub for b in BRAND_WORDS) and not any(b in p.domain for b in BRAND_WORDS)),
    }

a = extract("https://www.google.com/search?q=x")
b = extract("http://paypal.com.secure-login.xyz/verify/account")
print(f"{'feature':24s} {'google':>8s} {'paypal phish':>13s}")
for name in FEATURE_NAMES:
    print(f"{name:24s} {a[name]:8.2f} {b[name]:13.2f}")

# %% [markdown]
# Compare every number with the table in theory §3.3 (url_length 33 and 49, entropy 4.19 and 4.40, …). If you
# can fill that table by hand, you understand the extractor. Careful with `suspicious_word_count` = **5**: besides
# secure, login, verify and account, **paypal** is in `SUSPICIOUS_WORDS` too — the count searches the whole URL.
#
# ## 4. On real URLs — before any model
#
# `data/phishing_urls.csv`: 11,430 URLs, half phishing, half legitimate (Hannousse & Yahiouche 2021, CC BY 4.0).

# %%
urls, labels = [], []
with open(Path("../data/phishing_urls.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(f):
        urls.append(row["URL"]); labels.append(1 if row["Label"] == "bad" else 0)
labels = np.array(labels)
X = np.array([[extract(u)[n] for n in FEATURE_NAMES] for u in urls])
print(X.shape, "phishing share:", labels.mean())

good, bad = X[labels == 0].mean(0), X[labels == 1].mean(0)
pooled = X.std(0) + 1e-9
order = np.argsort(-np.abs(bad - good) / pooled)
print(f"{'feature':24s} {'good':>8s} {'bad':>8s}   difference in std units")
for i in order:
    print(f"{FEATURE_NAMES[i]:24s} {good[i]:8.2f} {bad[i]:8.2f}   {(bad[i] - good[i]) / pooled[i]:+.2f}")

# %% [markdown]
# This table goes in your book **before** any model result: it shows the features carry signal, and later
# lets you say "the model learned what the table already shows". Which five features separate best?
#
# ## ✍️ Try it yourself
#
# 1. Fill the 20-feature table by hand for `http://amazon.com@203.0.113.55/prize/claim`, then check with `extract`.
# 2. Why is `has_https` computed from the **scheme** and not by searching "https" in the string? Find a URL where
#    the two disagree.
# 3. Invent a 21st feature that catches `paypa1.com`-style look-alikes. Compute it on the dataset — does it
#    separate the classes?
#
# Then solve exercises 1–5 in `03_exercises/`.
