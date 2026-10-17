"""Lesson 18 - a URL as numbers: anatomy, hand-made features, Shannon entropy, train/serve skew."""
import math
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)


def entropy(s):
    n = len(s)
    return abs(-sum(c / n * math.log2(c / n) for c in Counter(s).values())) if n else 0.0


# ---------------------------------------------------------------- 1. URL anatomy
if L.wanted("anatomy"):
    url = "http://paypal.com.secure-login.xyz:8080/verify/account?id=77&r=1"
    parts = [("http", "scheme", MUTED), ("://", "", None), ("paypal.com.secure-login", "subdomains + domain", ORANGE),
             (".xyz", "TLD", VIOLET), (":8080", "port", AQUA), ("/verify/account", "path", BLUE),
             ("?id=77&r=1", "query", GREEN)]
    fig, ax = plt.subplots(figsize=(15, 4.6))
    blank(ax)
    x = 0.02
    cw = 0.0142
    for text, label, col in parts:
        w = len(text) * cw
        ax.text(x, 0.62, text, fontsize=19, family="monospace", va="center", color=col or INK)
        if label:
            ax.plot([x, x + w - 0.003], [0.48, 0.48], color=col, lw=4)
            ax.text(x + w / 2, 0.38, label, ha="center", fontsize=12, color=col)
        x += w
    host = "paypal.com.secure-login.xyz"
    ax.text(0.02, 0.15, f"host = “{host}”  →  domain = secure-login.xyz,  subdomains = [paypal, com]   →   "
                        "brand_in_subdomain = 1  (the brand is NOT the real domain!)", fontsize=12.5)
    ax.text(0.02, 0.88, "Read a URL from the RIGHT end of the host: the real owner is the part just before the TLD.",
            fontsize=13, weight="bold")
    L.save(fig, "anatomy")

# ---------------------------------------------------------------- 2. entropy, string by string
strings = ["aaaa", "aaab", "abab", "abcdefgh", "/signin", "/8fa9q2z7x"]
if L.wanted("entropy"):
    fig, ax = plt.subplots(figsize=(11, 5))

    def upd(f):
        s = strings[min(f // 2, len(strings) - 1)]
        cnt = Counter(s)
        chars = sorted(cnt)
        ax.clear()
        ax.bar(range(len(chars)), [cnt[c] / len(s) for c in chars], color=VIOLET)
        ax.set_xticks(range(len(chars)), [repr(c)[1:-1] for c in chars], fontsize=14)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("p(c) = count / length")
        terms = " + ".join(f"{cnt[c]}/{len(s)}·log₂" for c in chars[:3]) + (" …" if len(chars) > 3 else "")
        ax.set_title(f"“{s}”   H = {entropy(s):.3f} bits per character", fontsize=15)
        ax.text(0.98, 0.92, "H = − Σ p(c) · log₂ p(c)", transform=ax.transAxes, ha="right", fontsize=13)
        ax.text(0.98, 0.82, f"max for {len(s)} characters = log₂ {len(s)} = {math.log2(len(s)):.2f}",
                transform=ax.transAxes, ha="right", fontsize=11, color=INK2)
    L.animate(fig, upd, 2 * len(strings) + 2, "entropy", fps=1)

# ---------------------------------------------------------------- 3. the features before any model
X, y, names = phish_features()
if L.wanted("distributions"):
    feats = ["url_length", "num_digits", "entropy", "num_slashes", "suspicious_word_count", "num_query_params"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, f in zip(axes.ravel(), feats):
        j = names.index(f)
        hi = np.percentile(X[:, j], 99)
        integer = np.all(X[:, j] == np.round(X[:, j])) and hi - X[:, j].min() <= 12
        bins = np.arange(-0.5, hi + 1.5, 1) if integer else np.linspace(X[:, j].min(), hi, 31)
        ax.hist(X[y == 0, j], bins=bins, color=BLUE, alpha=0.6, density=True, label="legitimate")
        ax.hist(X[y == 1, j], bins=bins, color=ORANGE, alpha=0.6, density=True, label="phishing")
        ax.set_title(f"{f}   (means {X[y == 0, j].mean():.2f} vs {X[y == 1, j].mean():.2f})", fontsize=12)
        ax.set_yticks([])
    axes[0, 0].legend()
    caption(fig, "11,430 real URLs.  No single feature separates the classes - each one shifts the odds a little.  "
                 "The model combines them.")
    L.save(fig, "distributions")

# ---------------------------------------------------------------- 4. train / serve skew
if L.wanted("skew"):
    import csv
    with open(data("25_PhishGuard", "phishing_urls.csv"), encoding="utf-8") as f:
        urls = [r["URL"] for r in csv.DictReader(f)][:4000]

    def host(u):
        rest = u.split("://", 1)[1] if "://" in u else u
        return rest.split("/", 1)[0]

    train_dots = [u.count(".") for u in urls]          # training code: dots in the whole URL
    serve_dots = [host(u).count(".") for u in urls]    # a "slightly different" app: dots in the host only
    fig, (a0, a1) = plt.subplots(1, 2, figsize=(15, 4.8), gridspec_kw={"width_ratios": [1, 1.1]})
    blank(a0)
    box(a0, 0.02, 0.62, 0.3, 0.2, "train.py", color=INK2)
    box(a0, 0.02, 0.18, 0.3, 0.2, "the app (scan)", color=INK2)
    box(a0, 0.42, 0.38, 0.32, 0.24, "ONE class:\nURLFeatureExtractor", color=GREEN, fill="#d5ecd5", weight="bold")
    arrow(a0, (0.32, 0.72), (0.42, 0.55))
    arrow(a0, (0.32, 0.28), (0.42, 0.45))
    box(a0, 0.8, 0.38, 0.18, 0.24, "model", color=BLUE)
    arrow(a0, (0.74, 0.5), (0.8, 0.5))
    a0.set_title("RIGHT: one extractor for both")
    bins = np.arange(-0.5, 12.5, 1)
    a1.hist(train_dots, bins=bins, color=BLUE, alpha=0.6, label="num_dots as trained (whole URL)")
    a1.hist(serve_dots, bins=bins, color=RED, alpha=0.6, label="num_dots in a buggy app (host only)")
    a1.set_xlabel("num_dots")
    a1.set_title("WRONG: two versions of num_dots")
    a1.legend()
    caption(fig, "Train/serve skew gives no error message - just confident, wrong answers.  "
                 "Guard: one extractor + feature names/order saved in the bundle and checked on load.")
    L.save(fig, "skew")

for s in strings:
    print(f"  H({s!r}) = {entropy(s):.3f}")

# ================================================================ expanded lesson: more pictures
sys.path.insert(0, str(HUB / "25_PhishGuard" / "02_examples"))
import url_features as uf  # noqa: E402

# ---------------------------------------------------------------- 5. read the host from the RIGHT (animated)
if L.wanted("read_right"):
    hosts = ["login.microsoft.com", "microsoft.com.login-check.ru", "paypal.com.secure-login.xyz", "www.bankhapoalim.co.il"]
    fig, ax = plt.subplots(figsize=(13, 5.6))

    def upd(step):
        blank(ax, (0, 1), (0, 1))
        for r_, h in enumerate(hosts):
            pr = uf.parse("http://" + h)
            labels = h.split(".")
            n_tld = len(pr["tld"].split("."))
            y = 0.82 - r_ * 0.22
            x = 0.03
            for j, lab in enumerate(labels):
                from_right = len(labels) - 1 - j
                if from_right < n_tld:
                    role, col = "TLD", MUTED
                elif from_right == n_tld:
                    role, col = "OWNER", GREEN
                else:
                    role, col = "anything the owner wants", ORANGE
                show = step > from_right
                w_ = 0.012 * len(lab) + 0.03
                box(ax, x, y, w_, 0.09, lab, color=col if show else GRID, fill=PAPER, fontsize=13,
                    weight="bold" if role == "OWNER" and show else "normal")
                if show and role == "OWNER":
                    ax.text(x + w_ / 2, y - 0.045, "real owner", ha="center", fontsize=10, color=GREEN)
                x += w_ + 0.012
                if j < len(labels) - 1:
                    ax.text(x - 0.009, y + 0.03, ".", fontsize=16)
            if step >= len(labels):
                ax.text(0.78, y + 0.03, f"→ belongs to '{pr['domain']}.{pr['tld']}'", fontsize=12, color=GREEN)
        ax.set_title("Read the host from the RIGHT: TLD → the real owner → whatever the owner chose to write", fontsize=13)
    frames = [s_ for s_ in range(6) for _ in range(2)] + [5] * 4
    L.animate(fig, lambda i: upd(frames[i]), len(frames), "read_right", fps=2)

# ---------------------------------------------------------------- 6. entropy = the number of yes/no questions
if L.wanted("questions"):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.6))
    ax = blank(axes[0])
    letters = list("abcdefgh")
    levels = [[letters], [letters[:4], letters[4:]], [letters[:2], letters[2:4], letters[4:6], letters[6:]],
              [[c] for c in letters]]
    for lv, groups in enumerate(levels):
        y = 0.88 - lv * 0.26
        n = len(groups)
        for gi, grp in enumerate(groups):
            x = (gi + 0.5) / n
            w_ = 0.1 if len(grp) == 1 else 0.035 * len(grp) + 0.03
            box(ax, x - w_ / 2, y - 0.05, w_, 0.1, "".join(grp), color=VIOLET, fontsize=12)
            if lv < 3:
                for child in (2 * gi, 2 * gi + 1):
                    cx = (child + 0.5) / (2 * n)
                    ax.plot([x, cx], [y - 0.05, y - 0.21], color=MUTED, lw=1.2)
        if lv < 3:
            ax.text(0.99, y - 0.13, f"question {lv + 1}", ha="right", fontsize=10, color=INK2)
    ax.set_title("8 equally likely letters: 3 yes/no questions\n→ entropy = log₂ 8 = 3", fontsize=13)
    ax2 = axes[1]
    strings = ["aaaa", "aaab", "abab", "abcd", "abcdefgh", "/signin", "/8fa9q2z7x"]
    hs = [entropy(s) for s in strings]
    ax2.barh(range(len(strings))[::-1], hs, color=[GREEN if h < 2.5 else ORANGE for h in hs])
    for i, h in enumerate(hs):
        ax2.text(h + 0.05, len(strings) - 1 - i, f"{h:.2f}", va="center", fontsize=12)
    ax2.set_yticks(range(len(strings))[::-1], strings, family="monospace")
    ax2.set_xlabel("entropy = average yes/no questions per character")
    ax2.set_title("predictable → few questions;  random → many", fontsize=13)
    ax2.set_xlim(0, 3.8)
    L.save(fig, "questions")

# ---------------------------------------------------------------- 7. entropy on the real URLs
if L.wanted("entropy_real"):
    X, y, names = phish_features()
    e = X[:, names.index("entropy")]
    fig, ax = plt.subplots(figsize=(12, 4.8))
    bins = np.linspace(2.5, 5.6, 50)
    ax.hist(e[y == 0], bins, color=BLUE, alpha=0.7, label=f"legitimate (average {e[y == 0].mean():.2f})")
    ax.hist(e[y == 1], bins, color=ORANGE, alpha=0.7, label=f"phishing (average {e[y == 1].mean():.2f})")
    ax.set_xlabel("Shannon entropy of the whole URL")
    ax.set_ylabel("URLs")
    ax.set_title("Real PhishGuard URLs: phishing is a little more random on average - a weak clue, big overlap")
    ax.legend()
    L.save(fig, "entropy_real")

# ---------------------------------------------------------------- 8. one URL becomes 20 numbers
if L.wanted("feature_card"):
    url = "http://paypal.com.secure-login.xyz/verify/account"
    vals = uf.extract(url)
    fig, ax = plt.subplots(figsize=(13, 6.4))
    blank(ax)
    ax.text(0.5, 0.95, url, ha="center", fontsize=15, family="monospace", weight="bold", color=RED)
    ax.text(0.5, 0.88, "↓  URLFeatureExtractor.extract  ↓", ha="center", fontsize=12, color=INK2)
    for i, (n, v) in enumerate(zip(uf.FEATURE_NAMES, vals)):
        col, row = divmod(i, 10)
        x, y_ = 0.05 + col * 0.48, 0.78 - row * 0.075
        hot = n in ("has_https", "suspicious_word_count", "suspicious_tld", "brand_in_subdomain", "num_subdomains")
        ax.text(x, y_, n, fontsize=12, family="monospace", color=INK2)
        ax.text(x + 0.33, y_, f"{v:.3g}" if isinstance(v, (int, float)) else str(v), fontsize=13, family="monospace",
                weight="bold", color=ORANGE if hot else INK)
    ax.text(0.5, 0.02, "This row of 20 numbers is all the model ever sees. Orange = the strongest clues for this URL.",
            ha="center", fontsize=12, style="italic", color=INK2)
    L.save(fig, "feature_card")
