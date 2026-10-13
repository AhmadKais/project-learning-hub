# %% [markdown]
# # 02 · Naive Bayes, from scratch
#
# **Read first:** `01_theory/04_naive_bayes.md` — this is the heart of your project.
#
# 1. the worked example of §4.10, computed in code — check it against your paper
# 2. why we need smoothing (zeros) and logarithms (underflow) — see both break
# 3. a complete Multinomial NB, trained on 5,574 SMS messages
# 4. **identical** to scikit-learn's `MultinomialNB` (to 1e-9)
# 5. explaining a verdict with log-odds

# %%
import csv
import math
import re
from collections import Counter
from pathlib import Path

import numpy as np

HAM, SPAM = 0, 1

# %% [markdown]
# ## 1. The worked example
#
# Two spam and two ham documents. Training Naive Bayes is **just counting**:
#
# $$ P(w\mid c) = \frac{\text{count}_c(w) + \alpha}{\text{total}_c + \alpha\,|V|} $$

# %%
docs = [["free", "money", "now"], ["free", "prize", "winner"],
        ["meeting", "tomorrow", "office"], ["project", "meeting", "notes"]]
ys = [SPAM, SPAM, HAM, HAM]

def fit(docs, ys, alpha=1.0):
    vocab = sorted({t for d in docs for t in d})
    log_prior, log_lik = {}, {}
    for c in (HAM, SPAM):
        docs_c = [d for d, y in zip(docs, ys) if y == c]
        log_prior[c] = math.log(len(docs_c) / len(docs))
        counts = Counter(t for d in docs_c for t in d)
        total = sum(counts.values())
        log_lik[c] = {w: math.log((counts[w] + alpha) / (total + alpha * len(vocab))) for w in vocab}
    return log_prior, log_lik

log_prior, log_lik = fit(docs, ys)
print("vocabulary size:", len(log_lik[SPAM]))
print(f"P(free|spam) = {math.exp(log_lik[SPAM]['free']):.4f}   (by hand: 3/16 = 0.1875)")
print(f"P(free|ham)  = {math.exp(log_lik[HAM]['free']):.4f}   (by hand: 1/16 = 0.0625)")
print(f"log-odds(free) = {log_lik[SPAM]['free'] - log_lik[HAM]['free']:.3f}   (by hand: log 3 = 1.099)")

# %% [markdown]
# ## 2. Why smoothing? Set α = 0 and see

# %%
def fit_no_smoothing(docs, ys):
    out = {}
    for c in (HAM, SPAM):
        counts = Counter(t for d, y in zip(docs, ys) if y == c for t in d)
        total = sum(counts.values())
        out[c] = {w: counts[w] / total for w in {t for d in docs for t in d}}
    return out

p = fit_no_smoothing(docs, ys)
msg = ["meeting", "tomorrow", "free"]          # a normal message with one "spammy" word
for c, name in ((HAM, "ham"), (SPAM, "spam")):
    print(name, "score:", 0.5 * math.prod(p[c][w] for w in msg))

# %% [markdown]
# **Both** scores are 0: `free` never appeared in ham, so it zeroes the ham score; `meeting` never appeared in
# spam, so it zeroes the spam score. Nothing can be compared — any message that mixes words from both classes
# breaks the classifier. With α = 1 every word gets a small probability instead of none.
#
# ## 3. Why logarithms? Multiply 300 small numbers

# %%
print("0.001 ** 300 =", 0.001 ** 300)
print("300 * log(0.001) =", 300 * math.log(0.001))

# %% [markdown]
# A product of 300 probabilities is exactly 0.0 in a `float` — for **both** classes, so they can no longer
# be compared. In log space the product becomes a sum, and sums are fine:
#
# $$ \log \text{score}(c) = \log P(c) + \sum_{w} \log P(w\mid c) $$
#
# and the probability comes back at the very end as the sigmoid of the **difference**:
#
# $$ P(\text{spam}) = \frac{1}{1 + e^{\,\text{score(ham)} - \text{score(spam)}}} $$

# %%
def log_scores(tokens, log_prior, log_lik):
    s = {}
    for c in (HAM, SPAM):
        s[c] = log_prior[c] + sum(log_lik[c][t] for t in tokens if t in log_lik[c])   # unknown words skipped
    return s

def proba_spam(tokens, log_prior, log_lik):
    s = log_scores(tokens, log_prior, log_lik)
    diff = s[HAM] - s[SPAM]
    if diff > 700:
        return 0.0
    if diff < -700:
        return 1.0
    return 1.0 / (1.0 + math.exp(diff))

long_msg = ["free", "prize", "money"] * 300          # 900 tokens
s = log_scores(long_msg, log_prior, log_lik)
print("log scores:", {k: round(v, 1) for k, v in s.items()})
print("exp of each score:", math.exp(s[SPAM]), math.exp(s[HAM]), " <- the WRONG way: 0 / (0 + 0)")
print("P(spam) the right way:", proba_spam(long_msg, log_prior, log_lik))
print("P(spam) for 'meeting tomorrow free':", round(proba_spam(msg, log_prior, log_lik), 3))

# %% [markdown]
# ## 4. The real corpus
#
# Same cleaning and tokenizing as notebook 01 (unigrams + bigrams).

# %%
URL_RE = re.compile(r"(?:https?://|www\.)\S+", re.IGNORECASE)
WORD_RE = re.compile(r"[a-z']+")
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS as STOP

def tokenize(text):
    text = URL_RE.sub(" URLTOKEN ", text).lower().replace("urltoken", "URLTOKEN")
    out = []
    for i, part in enumerate(text.split("URLTOKEN")):
        if i:
            out.append("URLTOKEN")
        out += [w for w in WORD_RE.findall(part) if len(w) >= 3 and w not in STOP]
    return out + [a + " " + b for a, b in zip(out, out[1:])]

texts, labels = [], []
with open(Path("../data/sms_spam.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(f):
        texts.append(tokenize(row["text"]))
        labels.append(SPAM if row["label"] == "spam" else HAM)
labels = np.array(labels)

rng = np.random.default_rng(42)
perm = rng.permutation(len(texts))
cut = int(0.8 * len(texts))
train, test = perm[:cut], perm[cut:]

log_prior, log_lik = fit([texts[i] for i in train], labels[train])
probs = np.array([proba_spam(texts[i], log_prior, log_lik) for i in test])
pred = (probs >= 0.5).astype(int)
y = labels[test]
tp, fp, fn = np.sum((pred == 1) & (y == 1)), np.sum((pred == 1) & (y == 0)), np.sum((pred == 0) & (y == 1))
print(f"accuracy {np.mean(pred == y):.3f}   precision {tp / (tp + fp):.3f}   recall {tp / (tp + fn):.3f}")

# %% [markdown]
# ## 5. Is it right? Compare with scikit-learn's MultinomialNB
#
# Same counts, same α → the posterior must agree to 1e-9. This is the blocking test of your stage 4.

# %%
from sklearn.naive_bayes import MultinomialNB

vocab = sorted(log_lik[SPAM])
col = {t: j for j, t in enumerate(vocab)}

def counts_matrix(rows):
    M = np.zeros((len(rows), len(vocab)))
    for r, i in enumerate(rows):
        for t in texts[i]:
            if t in col:
                M[r, col[t]] += 1
    return M

sk = MultinomialNB(alpha=1.0).fit(counts_matrix(train), labels[train])
sk_probs = sk.predict_proba(counts_matrix(test))[:, 1]
print("largest difference from sklearn:", np.abs(sk_probs - probs).max())

# %% [markdown]
# ## 6. Explaining a verdict
#
# $$ \text{log-odds}(w) = \log P(w\mid\text{spam}) - \log P(w\mid\text{ham}) $$
#
# Positive pushes towards spam, negative towards ham. It is read **straight from the model** — this is
# why Naive Bayes is the primary model of your project.

# %%
def explain(tokens, top_n=5):
    seen = {t: log_lik[SPAM][t] - log_lik[HAM][t] for t in dict.fromkeys(tokens) if t in log_lik[SPAM]}
    return sorted(seen.items(), key=lambda kv: abs(kv[1]), reverse=True)[:top_n]

for raw in ["URGENT! You have WON a guaranteed prize. Call 0800 now to claim",
            "Sorry, I'll call you later, in a meeting now"]:
    t = tokenize(raw)
    print(f"P(spam) = {proba_spam(t, log_prior, log_lik):.4f}   <- {raw}")
    for w, lo in explain(t):
        print(f"     {w:18s} {lo:+.2f}")

# %% [markdown]
# The strongest spam words of the whole model:

# %%
lo_all = {w: log_lik[SPAM][w] - log_lik[HAM][w] for w in vocab}
print("spam:", [w for w in sorted(lo_all, key=lo_all.get, reverse=True)[:12]])
print("ham: ", [w for w in sorted(lo_all, key=lo_all.get)[:12]])

# %% [markdown]
# ## ✍️ Try it yourself
#
# 1. Change α to 0.1 and to 10. How do accuracy and the largest log-odds change? Why?
# 2. Remove the bigrams from `tokenize`. Does precision go up or down?
# 3. Find a ham message in the test set the model calls spam. Use `explain` to say why.
#
# Then solve exercises 8–11 in `03_exercises/`.
