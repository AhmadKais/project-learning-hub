"""Lesson 06 - text preprocessing: the two pipelines (Spam and ResumeMatch) shown step by step."""
import csv
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)

try:
    from nltk.corpus import stopwords
    STOP = set(stopwords.words("english"))
except LookupError:                       # first run: python -c "import nltk; nltk.download('stopwords')"
    import nltk
    nltk.download("stopwords", quiet=True)
    from nltk.corpus import stopwords
    STOP = set(stopwords.words("english"))
from nltk.stem.snowball import SnowballStemmer

STEM = SnowballStemmer("english").stem
TOKEN_PATTERN = r"\.?[A-Za-z֐-׿][A-Za-z0-9֐-׿+#.]*(?<!\.)"     # ResumeMatch config.py
URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)                       # Spam email_parser.py
WORD_RE = re.compile(r"[a-z']+")


def chips(ax, tokens, y0=0.78, x0=0.02, width=0.96, status=None, fontsize=13):
    """Draw tokens as coloured chips, wrapping lines. status[i] in {keep, new, drop, changed}."""
    colors = {"keep": (BLUE, LIGHT_BLUE), "new": (GREEN, "#d5ecd5"), "drop": (RED, "#f8d6d6"),
              "changed": (YELLOW, "#fbecc4")}
    x, y = x0, y0
    for i, t in enumerate(tokens):
        st = status[i] if status else "keep"
        w = 0.014 * len(t) + 0.03
        if x + w > x0 + width:
            x, y = x0, y - 0.13
        ec, fc = colors[st]
        box(ax, x, y, w, 0.09, t, color=ec, fill=fc, fontsize=fontsize, radius=0.015, lw=1.5)
        if st == "drop":
            ax.plot([x + 0.005, x + w - 0.005], [y + 0.045, y + 0.045], color=RED, lw=2)
        x += w + 0.012


# ---------------------------------------------------------------- 1. ResumeMatch pipeline animation
cv_text = "Noa Saleh, noa96@mail.com. Developed REST APIs in C++ and Node.js; used Machine Learning with Docker."


def resume_steps():
    steps = []
    scrubbed = re.sub(r"\S+@\S+", "", cv_text).replace("Noa Saleh,", "")
    steps.append(("0. the raw CV text", [cv_text], ["keep"]))
    steps.append(("1. scrub personal data (name, e-mail)", [scrubbed.strip()], ["changed"]))
    toks = re.findall(TOKEN_PATTERN, scrubbed)
    steps.append(("2. tokenize with TOKEN_PATTERN — C++, Node.js, Docker (no dot) survive", toks, ["keep"] * len(toks)))
    low = [t.lower() for t in toks]
    steps.append(("3. lower-case", low, ["changed" if a != b else "keep" for a, b in zip(toks, low)]))
    st = ["drop" if t in STOP else "keep" for t in low]
    steps.append(("4. drop stop-words (NLTK list)", low, st))
    kept = [t for t in low if t not in STOP]
    stemmed = [STEM(t) if re.fullmatch(r"[a-z]+", t) else t for t in kept]
    steps.append(("5. stem (Snowball): developed → develop, learning → learn",
                  stemmed, ["changed" if a != b else "keep" for a, b in zip(kept, stemmed)]))
    bigrams = [f"{a} {b}" for a, b in zip(stemmed, stemmed[1:])]
    steps.append(("6. add bigrams — 'machin learn' is now ONE term", stemmed + bigrams,
                  ["keep"] * len(stemmed) + ["new"] * len(bigrams)))
    return steps


# ---------------------------------------------------------------- 2. Spam pipeline animation
sms = "WINNER!! You have won a FREE prize. Click http://win-now.com to claim it now"


def spam_steps():
    steps = [("0. the raw message", [sms], ["keep"])]
    letters = [c for c in sms if c.isalpha()]
    caps = sum(c.isupper() for c in letters) / len(letters)
    steps.append((f"1. MEASURE first: caps_ratio = {caps:.2f}, exclamation_count = {sms.count('!')}, "
                  f"url_count = 1", [sms], ["keep"]))
    no_url = URL_RE.sub("URLTOKEN", sms)
    steps.append(("2. replace every URL with URLTOKEN", [no_url], ["changed"]))
    parts = no_url.split("URLTOKEN")
    low = [p.lower() for p in parts]
    steps.append(("3. lower-case (but keep URLTOKEN)", ["URLTOKEN".join(low)], ["changed"]))
    toks = WORD_RE.findall(low[0]) + ["URLTOKEN"] + WORD_RE.findall(low[1])
    steps.append(("4. words = runs of letters  [a-z']+", toks, ["keep"] * len(toks)))
    st = ["keep" if t == "URLTOKEN" else ("drop" if len(t) < 3 or t in STOP else "keep") for t in toks]
    steps.append(("5. drop words shorter than 3 letters and stop-words", toks, st))
    kept = [t for t, s in zip(toks, st) if s == "keep"]
    bigrams = [f"{a} {b}" for a, b in zip(kept, kept[1:])]
    steps.append(("6. n-grams (1, 2): words + adjacent pairs", kept + bigrams,
                  ["keep"] * len(kept) + ["new"] * len(bigrams)))
    return steps


def play(steps, name, title):
    fig, ax = plt.subplots(figsize=(14, 5.6))
    frames = [i for i in range(len(steps)) for _ in range(3)]

    def upd(k):
        blank(ax)
        cap, toks, status = steps[frames[k]]
        ax.text(0.02, 0.95, title, fontsize=15, weight="bold")
        ax.text(0.02, 0.88, cap, fontsize=13, color=INK2)
        if len(toks) == 1 and len(toks[0]) > 30:           # still a sentence: show as one block
            ec = {"keep": BLUE, "changed": YELLOW}[status[0]]
            ax.text(0.02, 0.7, toks[0], fontsize=14, family="monospace", va="top", wrap=True,
                    bbox=dict(boxstyle="round", fc=PAPER, ec=ec, lw=2))
        else:
            chips(ax, toks, y0=0.7, status=status)
        for j, (word, col) in enumerate([("kept", BLUE), ("changed", YELLOW), ("removed", RED), ("added", GREEN)]):
            ax.text(0.62 + j * 0.095, 0.03, "■ " + word, fontsize=12, color=col, weight="bold")
    L.animate(fig, upd, len(frames), name, fps=2)


if L.wanted("resume_pipeline"):
    play(resume_steps(), "resume_pipeline", "ResumeMatch: a CV becomes a list of terms")
if L.wanted("spam_pipeline"):
    play(spam_steps(), "spam_pipeline", "SpamClassifier: an SMS becomes a list of tokens")

# ---------------------------------------------------------------- 3. the bad tokenizer
if L.wanted("tokenizers"):
    words = ["C++", "C#", ".NET", "Node.js", "ASP.NET", "Docker.", "3.5", "scikit-learn"]
    fig, ax = plt.subplots(figsize=(13, 5.4))
    blank(ax)
    ax.text(0.02, 0.94, "input", weight="bold", fontsize=13)
    ax.text(0.32, 0.94, r"re.findall(r'\w+')", weight="bold", fontsize=13, color=RED, family="monospace")
    ax.text(0.65, 0.94, "TOKEN_PATTERN", weight="bold", fontsize=13, color=GREEN, family="monospace")
    for i, w in enumerate(words):
        y = 0.83 - i * 0.105
        ax.text(0.02, y, w, fontsize=14, family="monospace")
        ax.text(0.32, y, str(re.findall(r"\w+", w)), fontsize=13, family="monospace", color=RED)
        ax.text(0.65, y, str(re.findall(TOKEN_PATTERN, w)), fontsize=13, family="monospace", color=GREEN)
    caption(fig, "One regular expression decides whether a C++ developer can ever be found.")
    L.save(fig, "tokenizers")

# ---------------------------------------------------------------- 4. Zipf: a few words are everywhere
if L.wanted("zipf"):
    with open(data("08_SpamClassifier", "sms_spam.csv"), encoding="utf-8") as f:
        texts = [r["text"].lower() for r in csv.DictReader(f)]
    cnt = Counter(w for t in texts for w in WORD_RE.findall(t))
    ranked = cnt.most_common()
    freq = np.array([c for _, c in ranked])
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [1.2, 1]})
    r = np.arange(1, len(freq) + 1)
    is_stop = np.array([w in STOP for w, _ in ranked])
    a1.loglog(r, freq, "-", color=BLUE, lw=3, label="all words")
    a1.loglog(r[is_stop], freq[is_stop], "o", color=ORANGE, ms=5, label=f"the {is_stop.sum()} stop-words")
    a1.set_xlabel("rank of the word (1 = most common)")
    a1.set_ylabel("how many times it appears")
    a1.set_title(f"Zipf's law: {len(freq):,} different words in 5,574 SMS")
    a1.legend()
    top = ranked[:15]
    a2.barh(range(15)[::-1], [c for _, c in top], color=[ORANGE if w in STOP else BLUE for w, _ in top])
    a2.set_yticks(range(15)[::-1], [w for w, _ in top])
    a2.set_title("the 15 most common words")
    a2.set_xlabel("count")
    once = (freq == 1).sum()
    caption(fig, f"A handful of stop-words are everywhere and say nothing about spam;  "
                 f"{once:,} words ({once / len(freq):.0%}) appear only once.")
    L.save(fig, "zipf")
