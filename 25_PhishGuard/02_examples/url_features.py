"""The URL parser and the 20-feature extractor, exactly as built step by step in notebook 01.

Notebooks 02 and 03 import it so they do not repeat the code:
    from url_features import extract, FEATURE_NAMES
"""
import math
import re
from collections import Counter
from urllib.parse import urlparse

SUSPICIOUS_WORDS = ("login", "signin", "verify", "verification", "secure", "account", "update", "confirm",
                    "banking", "password", "wallet", "paypal", "ebay", "apple", "microsoft", "amazon",
                    "free", "bonus", "prize", "urgent", "suspended")
COMMON_TLDS = ("com", "org", "net", "edu", "gov", "il", "co.il", "ac.il", "uk", "de")
SUSPICIOUS_TLDS = ("xyz", "top", "tk", "ml", "ga", "cf", "gq", "buzz", "click", "loan", "work")
URL_SHORTENERS = ("bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "cutt.ly")
BRAND_WORDS = ("paypal", "apple", "microsoft", "amazon", "google", "facebook", "netflix", "bank")
IP_PATTERN = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")

FEATURE_NAMES = ["url_length", "host_length", "path_length", "num_dots", "num_hyphens", "num_underscores",
                 "num_slashes", "num_digits", "digit_ratio", "num_subdomains", "num_query_params",
                 "has_ip_host", "has_at_symbol", "has_https", "has_port", "suspicious_word_count",
                 "suspicious_tld", "is_shortener", "entropy", "brand_in_subdomain"]


def shannon_entropy(text):
    if not text:
        return 0.0
    n = len(text)
    return sum(c / n * math.log2(n / c) for c in Counter(text).values())     # = -sum p log2 p


def parse(url):
    """-> dict with scheme, host, subdomains, domain, tld, port, path, query, has_ip_host."""
    raw = url.strip()
    had_scheme = "://" in raw
    out = {"scheme": "", "host": "", "subdomains": [], "domain": "", "tld": "", "port": None,
           "path": "", "query": "", "has_ip_host": False}
    try:
        p = urlparse(raw if had_scheme else "http://" + raw)
        host = (p.hostname or "").lower()
        port = p.port
    except ValueError:
        return out
    out.update(scheme=p.scheme if had_scheme else "", host=host, port=port, path=p.path, query=p.query)
    if IP_PATTERN.match(host):
        out.update(has_ip_host=True, domain=host)
        return out
    labels = [l for l in host.split(".") if l]
    n_tld = 2 if len(labels) >= 3 and ".".join(labels[-2:]) in COMMON_TLDS else 1
    if len(labels) > n_tld:
        out.update(tld=".".join(labels[-n_tld:]), domain=labels[-n_tld - 1], subdomains=labels[:-n_tld - 1])
    else:
        out["domain"] = host
    return out


def extract(url):
    """The 20 features, as a list in FEATURE_NAMES order."""
    p = parse(url)
    low = url.lower()
    after_scheme = url.split("://", 1)[1] if "://" in url else url
    digits = sum(ch.isdigit() for ch in url)
    sub = ".".join(p["subdomains"])
    return [
        len(url), len(p["host"]), len(p["path"]),
        url.count("."), url.count("-"), url.count("_"), after_scheme.count("/"),
        digits, digits / len(url) if url else 0.0,
        len(p["subdomains"]), len([q for q in p["query"].split("&") if q]),
        float(p["has_ip_host"]), float("@" in url), float(p["scheme"] == "https"), float(p["port"] is not None),
        sum(w in low for w in SUSPICIOUS_WORDS), float(p["tld"] in SUSPICIOUS_TLDS),
        float(p["host"] in URL_SHORTENERS), shannon_entropy(url),
        float(any(b in sub for b in BRAND_WORDS) and not any(b in p["domain"] for b in BRAND_WORDS)),
    ]
