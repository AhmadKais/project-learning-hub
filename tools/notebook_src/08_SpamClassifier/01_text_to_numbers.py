# %% [markdown]
# # 01 · Turning text into numbers
#
# **Read first:** `01_theory/03_features.md`
#
# A model cannot read. In this notebook you turn every message into a fixed-length list of numbers:
#
# 1. measure the raw signals (CAPS, `!`, digits, links) **before** cleaning
# 2. clean: strip HTML, replace URLs with one token, lower-case
# 3. tokenize: words of 3+ letters, no stop words, `URLTOKEN` survives
# 4. n-grams, document frequency, IDF
# 5. TF-IDF with L2 normalisation — by hand on 3 messages, then on the real corpus

# %%
import csv
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

texts, labels = [], []
with open(Path("../data/sms_spam.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(f):
        texts.append(row["text"])
        labels.append(1 if row["label"] == "spam" else 0)
labels = np.array(labels)
print(len(texts), "messages,", labels.sum(), f"spam ({labels.mean():.1%})")
for i in (0, 2, 5):
    print(["ham ", "SPAM"][labels[i]], "|", texts[i])

# %% [markdown]
# ## 1. The raw signals — measured BEFORE lower-casing
#
# `"FREE MONEY NOW"` and `"free money now"` are the same words but not the same message.
# If you lower-case first, `caps_ratio` is always 0 — the signal is destroyed before you measure it.

# %%
URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]{0,200}>")

def caps_ratio(text):
    letters = [c for c in text if c.isalpha()]
    return sum(c.isupper() for c in letters) / len(letters) if letters else 0.0

def digit_ratio(text):
    return sum(c.isdigit() for c in text) / len(text) if text else 0.0

def raw_signals(text):
    return {"caps_ratio": caps_ratio(text), "exclamation_count": text.count("!"),
            "digit_ratio": digit_ratio(text), "url_count": len(URL_RE.findall(text)),
            "message_length": len(text)}

print(raw_signals("FREE MONEY NOW!!! Call 09061701461 www.win.com"))
print(raw_signals("free money now!!! call 09061701461 www.win.com".lower()))

# %% [markdown]
# Do the signals separate spam from ham? Compare the averages:

# %%
sig = [raw_signals(t) for t in texts]
print(f"{'signal':18s} {'ham':>8s} {'spam':>8s}")
for key in sig[0]:
    v = np.array([s[key] for s in sig])
    print(f"{key:18s} {v[labels == 0].mean():8.3f} {v[labels == 1].mean():8.3f}")

# %% [markdown]
# Spam has **far** more digits (phone numbers, prices) and is longer. Before any model exists you can
# already say which features will matter — say it in your book.
#
# ## 2. Cleaning
#
# Strip tags with a **space** (so `<b>free</b><i>offer</i>` does not become `freeoffer`), replace every
# URL with the same token (the *presence* of a link transfers to new spam; the domain does not), lower-case.

# %%
URL_TOKEN = "URLTOKEN"

def clean(text):
    text = " ".join(TAG_RE.sub(" ", text).split())
    text = URL_RE.sub(f" {URL_TOKEN} ", text)
    return text.lower().replace(URL_TOKEN.lower(), URL_TOKEN)

print(clean("<b>FREE</b><i>offer</i> at http://bit.ly/x9 NOW"))

# %% [markdown]
# ## 3. Tokenizing
#
# Rules from your project: words are runs of letters and apostrophes, at least 3 characters, no stop words,
# and `URLTOKEN` always survives. (Your project uses NLTK's stop-word list; here we use scikit-learn's,
# which is very similar, so you need nothing extra.)

# %%
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as STOP

WORD_RE = re.compile(r"[a-z']+")

def tokenize(cleaned):
    out = []
    for part_i, part in enumerate(cleaned.split(URL_TOKEN)):
        if part_i > 0:
            out.append(URL_TOKEN)
        out += [w for w in WORD_RE.findall(part) if len(w) >= 3 and w not in STOP]
    return out

print(tokenize(clean("WINNER!! You have won a FREE prize, click http://x.co now to claim")))
print(tokenize(clean("ok i'll see you at the office tomorrow")))

# %% [markdown]
# ## 4. N-grams
#
# A bigram is two neighbouring tokens. `"click here"` means something neither word means alone.

# %%
def ngrams(tokens, n_min=1, n_max=2):
    return [" ".join(tokens[i:i + n]) for n in range(n_min, n_max + 1) for i in range(len(tokens) - n + 1)]

print(ngrams(["click", "here", "now"]))

# %% [markdown]
# ## 5. TF-IDF by hand on three messages
#
# $$ tf(w,d) = \frac{\text{count of } w \text{ in } d}{\text{terms in } d} \qquad
#    idf(w) = \log\frac{N}{1 + df(w)} + 1 \qquad tfidf = tf \times idf $$
#
# $df(w)$ = in how many **documents** the word appears (not how many times in total).

# %%
docs = [["free", "prize", "free"], ["meeting", "office"], ["free", "meeting"]]
N = len(docs)
df = Counter(t for d in docs for t in set(d))          # set(): once per document!
idf = {t: math.log(N / (1 + df[t])) + 1 for t in df}
for t in sorted(idf):
    print(f"{t:8s} df={df[t]}  idf={idf[t]:.3f}")

def tfidf(doc, idf):
    counts = Counter(doc)
    v = {t: counts[t] / len(doc) * idf[t] for t in counts if t in idf}
    norm = math.sqrt(sum(x * x for x in v.values()))
    return {t: x / norm for t, x in v.items()} if norm else v

for d in docs:
    print(d, "->", {t: round(x, 3) for t, x in tfidf(d, idf).items()})

# %% [markdown]
# Check the first vector by hand: tf(free) = 2/3, tf(prize) = 1/3. Multiply by the IDFs above, then divide
# both by the length of the vector. The result always has length 1 — that is the **L2 normalisation**,
# and it is what stops the model from learning "long messages are spam".
#
# ## 6. On the real corpus: the vocabulary
#
# Keep the 5,000 terms with the highest **document frequency**.

# %%
tokens = [ngrams(tokenize(clean(t))) for t in texts]
df_all = Counter(t for d in tokens for t in set(d))
vocab = [t for t, _ in df_all.most_common(5000)]
idf_all = {t: math.log(len(tokens) / (1 + df_all[t])) + 1 for t in vocab}
print("distinct terms:", len(df_all), " kept:", len(vocab))
print("most common:", vocab[:15])

# %% [markdown]
# Which terms are most typical of spam? Compare in how many spam vs ham messages each appears.

# %%
df_spam = Counter(t for d, y in zip(tokens, labels) if y == 1 for t in set(d))
df_ham = Counter(t for d, y in zip(tokens, labels) if y == 0 for t in set(d))
ratio = {t: (df_spam[t] + 1) / (df_ham[t] + 1) for t in vocab if df_all[t] >= 10}
top = sorted(ratio, key=ratio.get, reverse=True)[:15]
for t in top:
    print(f"{t:18s} spam docs {df_spam[t]:4d}   ham docs {df_ham[t]:4d}")

# %% [markdown]
# ## 7. The vector of one message
#
# Every message becomes **exactly** `len(vocab)` numbers (+ the handcrafted ones). A word not in the
# vocabulary is dropped — it cannot widen the vector.

# %%
index = {t: i for i, t in enumerate(vocab)}

def to_dense(doc_terms):
    v = np.zeros(len(vocab))
    for t, x in tfidf([t for t in doc_terms if t in index], idf_all).items():
        v[index[t]] = x
    return v

msg = "URGENT! You have won a free prize. Call now to claim xyzzyplugh"
v = to_dense(ngrams(tokenize(clean(msg))))
print("length of the vector:", len(v), " non-zero:", np.count_nonzero(v), " L2 norm:", np.linalg.norm(v).round(6))
for i in np.argsort(-v)[:6]:
    print(f"  {vocab[i]:18s} {v[i]:.3f}")

# %% [markdown]
# ## ✍️ Try it yourself
#
# 1. Remove `set()` from the `df` line in section 5. Which IDF changes, and why is that wrong?
# 2. Lower-case **before** `raw_signals` in section 1. What happens to the spam/ham difference in caps_ratio?
# 3. Set `n_max=3`. How many distinct terms are there now? Are any trigrams in the top 15 spam terms?
#
# Then solve exercises 1–7 in `03_exercises/`.
