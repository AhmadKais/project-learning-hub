"""SpamClassifier - solutions to exercises.py.

Try first. Then compare: there is more than one correct way to write each one.
To run the tests against these solutions:  EXERCISES=solutions pytest test_exercises.py
"""
import math
import re
from collections import Counter

HAM, SPAM = 0, 1
URL_TOKEN = "URLTOKEN"
WORD_RE = re.compile(r"[a-z']+")
TAG_RE = re.compile(r"<[^>]{0,200}>")


def ex01_caps_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(c.isupper() for c in letters) / len(letters)


def ex02_strip_html(text):
    return " ".join(TAG_RE.sub(" ", text).split())


def ex03_tokenize(cleaned, stopwords):
    out = []
    for i, part in enumerate(cleaned.split(URL_TOKEN)):
        if i > 0:
            out.append(URL_TOKEN)
        out.extend(w for w in WORD_RE.findall(part) if len(w) >= 3 and w not in stopwords)
    return out


def ex04_ngrams(tokens, n_min=1, n_max=2):
    tokens = list(tokens)
    return [" ".join(tokens[i:i + n])
            for n in range(n_min, n_max + 1)
            for i in range(len(tokens) - n + 1)]


def ex05_idf_value(n_documents, document_frequency):
    return math.log(n_documents / (1 + document_frequency)) + 1


def ex06_build_vocabulary(token_lists, max_features):
    df = Counter()
    for tokens in token_lists:
        df.update(set(tokens))
    ranked = sorted(df, key=lambda t: (-df[t], t))
    return ranked[:max_features]


def ex07_tfidf(tokens, idf):
    known = [t for t in tokens if t in idf]
    if not known:
        return {}
    counts = Counter(known)
    vec = {t: counts[t] / len(known) * idf[t] for t in counts}
    norm = math.sqrt(sum(v * v for v in vec.values()))
    return {t: v / norm for t, v in vec.items()} if norm else vec


def ex08_nb_fit(documents, labels, alpha=1.0):
    vocab = {t for d in documents for t in d}
    log_prior, log_lik = {}, {}
    for c in (HAM, SPAM):
        docs_c = [d for d, y in zip(documents, labels) if y == c]
        log_prior[c] = math.log(len(docs_c) / len(documents))
        counts = Counter(t for d in docs_c for t in d)
        total = sum(counts.values())
        denom = total + alpha * len(vocab)
        log_lik[c] = {w: math.log((counts[w] + alpha) / denom) for w in vocab}
    return log_prior, log_lik


def ex09_nb_log_scores(tokens, log_prior, log_likelihood):
    return {c: log_prior[c] + sum(log_likelihood[c][t] for t in tokens if t in log_likelihood[c])
            for c in (HAM, SPAM)}


def ex10_proba_spam(scores):
    diff = scores[HAM] - scores[SPAM]
    if diff > 700:
        return 0.0
    if diff < -700:
        return 1.0
    return 1.0 / (1.0 + math.exp(diff))


def ex11_explain(tokens, log_likelihood, top_n=5):
    seen = {}
    for t in tokens:
        if t not in seen and t in log_likelihood[SPAM]:
            seen[t] = log_likelihood[SPAM][t] - log_likelihood[HAM][t]
    ranked = sorted(seen.items(), key=lambda kv: abs(kv[1]), reverse=True)
    return ranked[:top_n]


def ex12_precision_recall_at(probs, labels, threshold):
    tp = fp = fn = 0
    for p, y in zip(probs, labels):
        predicted = p >= threshold
        if predicted and y == SPAM:
            tp += 1
        elif predicted:
            fp += 1
        elif y == SPAM:
            fn += 1
    precision = tp / (tp + fp) if tp + fp else 1.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return precision, recall


def ex13_choose_threshold(probs, labels, thresholds, min_precision=0.98):
    best = None
    for t in thresholds:
        precision, recall = ex12_precision_recall_at(probs, labels, t)
        if precision >= min_precision and (best is None or recall > best[2]):
            best = (t, precision, recall)
    if best is None:
        raise ValueError(f"no threshold reaches precision {min_precision}")
    return best
