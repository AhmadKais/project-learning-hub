# Chapter 3 — Turning text into numbers

💡 **In short:** a model cannot read. You convert each message into a fixed-length list of numbers: 5,000 TF-IDF values for words and word-pairs, plus seven handcrafted signals. Measure the handcrafted ones on the *raw* text, before lower-casing, or you destroy them.

## 3.1 The problem

A model multiplies and adds. It cannot take `"Win a FREE iPhone!!!"` as input. Your job is to turn a message of any length into a list of numbers of **fixed** length — the same length every time, or the model cannot consume it.

This is feature engineering, and it is not a preparatory step before the interesting part. It *is* the interesting part: a good feature separates the classes, a bad one adds noise, and no model recovers from bad features.

## 3.2 Bag of words, and why it is not enough

The simplest representation: count each word.

```
"free money free"  ->  {"free": 2, "money": 1}
```

Two problems. First, common words dominate — `the` appears in everything and separates nothing. Second, longer messages produce bigger numbers throughout, so the model learns to detect length.

## 3.3 TF-IDF

TF-IDF fixes the first problem. It scores a word highly when it is frequent **here** and rare **everywhere else** — which is precisely when it is characteristic of this message.

```
tf(w, d)  = count of w in d  /  number of terms in d
idf(w)    = log( N / (1 + df(w)) ) + 1
tfidf     = tf × idf
```

where `N` is the number of documents and `df(w)` is how many documents contain `w`.

📄 **Stage 3: the IDF formula**
```python
@staticmethod
def idf_value(n_documents: int, document_frequency: int) -> float:
    return math.log(n_documents / (1 + document_frequency)) + 1
```

Work through what it does:

| Word | Appears in | IDF (N=1000) | Meaning |
|---|---|---|---|
| `the` | 1000 docs | ≈ 1.0 | everywhere, so nearly worthless |
| `meeting` | 100 docs | ≈ 3.3 | moderately informative |
| `viagra` | 5 docs | ≈ 6.1 | rare, so very informative when present |

The two `+1`s are both deliberate. The one in the denominator stops a division by zero for a word in every document; the one outside keeps the result positive, so a very common word is weighted *down* rather than erased entirely.

## 3.4 Document frequency, not total count

When choosing which 5,000 terms to keep, rank by **document frequency** — how many messages contain the word — not by total occurrences.

A word repeated 500 times in one ranting email has a total count of 500 and a document frequency of 1. It is not a useful feature; it is one person shouting. A word appearing once each in 500 messages is genuinely common across the corpus.

📄 **Stage 3: building the vocabulary**
```python
from collections import Counter

df = Counter()
for message in messages:
    terms = set(ngrams(self._tokenizer.tokenize(message), NGRAM_MIN, NGRAM_MAX))
    df.update(terms)          # set(), so each term counts once per document

self._vocabulary = [t for t, _ in df.most_common(config.MAX_FEATURES)]
self._idf = {t: self.idf_value(len(messages), df[t]) for t in self._vocabulary}
```

The `set()` is the whole point of this snippet. Remove it and you are counting occurrences.

## 3.5 L2 normalisation

This fixes the second problem — length.

```
norm = sqrt( sum of v² over all components )
each component is divided by norm
```

After it, every vector has length exactly 1, so a 20-word message and a 2,000-word message are directly comparable.

📄 **Stage 3**
```python
@staticmethod
def l2_normalise(vector):
    norm = math.sqrt(sum(v * v for v in vector.values()))
    if norm == 0:
        return vector                       # empty vector: nothing to scale
    return {k: v / norm for k, v in vector.items()}
```

❓ **What happens if you skip the normalisation?**

Every component of a long message is larger than the same component of a short one, simply because there is more text. The model picks up on that, and what it learns is "long messages are spam" rather than anything about content. `test_long_and_short_messages_are_comparable` is the test that catches it.

## 3.6 N-grams

A unigram is one word; a bigram is two adjacent words.

```
ngrams(["click", "here", "now"], 1, 2)
  -> ["click", "here", "now", "click here", "here now"]
```

Bigrams earn their place because `"click here"` carries meaning that neither `click` nor `here` carries alone. Trigrams and beyond multiply the vocabulary for very little further gain, which is why `config.yaml` caps the range at 2.

## 3.7 The seven handcrafted features

TF-IDF only sees words. These seven see things words cannot express:

| Feature | What it captures |
|---|---|
| `caps_ratio` | SHOUTING |
| `exclamation_count` | `!!!` |
| `message_length` | very short or very long messages |
| `digit_ratio` | prices, phone numbers, "100% FREE" |
| `url_count` | how many links |
| `trigger_word_count` | how many of the ten known lure words |
| `unique_word_ratio` | repetitive filler text |

Their names and order live in `config.HANDCRAFTED_FEATURES`, get written into `features.json` inside the model bundle, and are verified when the bundle loads. That check exists because a mismatch between training order and scanning order produces *no error at all* — just wrong answers. Section 9.3 returns to this.

## 3.8 Measure before you normalise

This is the most important rule in the chapter, and the easiest to get wrong.

📄 **Wrong — and it destroys a real signal**
```python
text = raw.lower()                      # lower-case first
caps = caps_ratio(text)                 # always 0.0. Always.
```

📄 **Right**
```python
caps = caps_ratio(body)                 # measure on the raw text
body = body.lower()                     # then normalise
```

`"FREE MONEY NOW"` and `"free money now"` are the same to TF-IDF, and they should be — you want both to match the word `free`. But they are *not* the same message, and `caps_ratio` is how that difference survives. Lower-case first and you have thrown it away before measuring it.

`EmailParser.parse` does them in the right order, and `test_parse_measures_caps_before_lowercasing` fails loudly if you reorder them.

## 3.9 Cleaning, step by step

```
1. cap the length            100,000 characters maximum
2. split headers from body   keep Subject, drop the rest
3. MEASURE the raw signals   <-- before anything is normalised
4. strip HTML tags
5. replace URLs with URLTOKEN
6. lower-case
```

Two of these are decisions rather than mechanics.

**Why drop the headers?** `From`, `To` and `Received` identify particular mail servers. Keep them and the model learns "mail from this server in the corpus is spam", which is true of your corpus and useless on anything else. `Subject` stays, because it is content.

**Why replace URLs instead of keeping the domain?** Learning that `bit.ly` is suspicious is learning this corpus. It does not transfer to a link the model has never seen — and every link in real incoming spam is one it has never seen. What *does* transfer is the fact that a link is present at all, so every URL becomes the same token.

📄 **Stage 2: stripping tags without gluing words**
```python
TAG_RE = re.compile(r"<[^>]{0,200}>")

def strip_html(self, text):
    return " ".join(TAG_RE.sub(" ", text).split())
```

Substituting a space rather than an empty string is what keeps `<b>free</b><i>offer</i>` from becoming `freeoffer`. The `.split()` then collapses the extra whitespace. `test_strip_html_keeps_words_apart` exists because this is a mistake people make once.

## 3.10 The full vector

```
[ 5,000 TF-IDF values ][ 7 handcrafted values ]  =  5,007 numbers
```

Always 5,007, for every message, in the same order every time. `to_dense` produces it, `feature_names` lists what each position means, and both orders are frozen in `config.py` because the bundle contract depends on them.

❓ **A term in a new message is not in the vocabulary. What happens to it?**

It is dropped. It cannot be added, because the vector must be exactly 5,007 wide or the model cannot take it. This is a genuine limitation — a brand-new word carries no weight until the next retrain — and it is listed as such in the proposal. `test_unknown_terms_do_not_widen_the_vector` pins the behaviour.
