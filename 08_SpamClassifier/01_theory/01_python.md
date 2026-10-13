# Chapter 1 — The Python you need

💡 **In short:** dictionaries, comprehensions, `Counter`, dataclasses and f-strings. If those five are comfortable, skip to chapter 2.

## 1.1 Dictionaries are the whole project

Almost every structure in this project is a dictionary from a word to a number.

📄 **The shape of nearly everything**
```python
word_counts = {"free": 42, "meeting": 7, "winner": 19}

word_counts["free"]              # 42
word_counts.get("zzz", 0)        # 0  - safe default, no KeyError
"free" in word_counts            # True
word_counts.items()              # ("free", 42), ("meeting", 7), ...
```

`.get(key, default)` matters more than it looks. When you ask for the probability of a word the model has never seen, `word_counts["zzz"]` raises `KeyError` and crashes the application; `word_counts.get("zzz", 0)` returns a sensible zero.

## 1.2 Comprehensions

A comprehension builds a list or a dict in one line.

📄 **Four you will write many times**
```python
# every token, lower-cased
lowered = [t.lower() for t in tokens]

# only the long ones
long_tokens = [t for t in tokens if len(t) >= 3]

# a dict from a list
lengths = {t: len(t) for t in tokens}

# scale every value in a dict
scaled = {k: v / total for k, v in counts.items()}
```

The last one is `l2_normalise` in miniature. When you get to `FeatureEngineer`, you are writing exactly this with a square root in the denominator.

## 1.3 Counter

`collections.Counter` is a dictionary that counts. You will use it in `NaiveBayesClassifier.fit`.

📄 **Counting words**
```python
from collections import Counter

counts = Counter(["free", "money", "free", "now"])
# Counter({"free": 2, "money": 1, "now": 1})

counts["free"]            # 2
counts["unseen"]          # 0   - no KeyError, unlike a plain dict
counts.most_common(2)     # [("free", 2), ("money", 1)]

total = sum(counts.values())    # 4
```

💡 `Counter` returns 0 for a missing key instead of raising. That is convenient, but do not let it hide a bug: in Naive Bayes a count of zero must still go through Laplace smoothing, so you add alpha explicitly rather than relying on the zero.

## 1.4 Sets, and why `fit` uses them

A set holds each item once and tests membership instantly.

📄 **Document frequency needs a set**
```python
tokens = ["free", "free", "free", "money"]

len(tokens)        # 4  - occurrences
len(set(tokens))   # 2  - distinct words
```

This distinction decides a real question in chapter 3. Document frequency counts *in how many documents* a word appears, so a word repeated 500 times in one message counts once. Using the raw count instead would rank a single ranting email above a word that appears across the whole corpus.

## 1.5 Dataclasses

A dataclass is a class whose job is to hold values. `frozen=True` makes it unchangeable.

📄 **From `models/entities.py`**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Reason:
    token: str
    weight: float

    @property
    def direction(self) -> str:
        return "spam" if self.weight > 0 else "ham"

r = Reason("winner", 2.81)
r.token        # "winner"
r.direction    # "spam"
r.weight = 5   # FrozenInstanceError
```

Everything in `entities.py` is frozen on purpose. A `Verdict` that could be edited after it was stored would make the scan history meaningless — you could never be sure the row you are reading is the decision that was actually made.

## 1.6 Type hints

```python
def predict_proba(self, tokens: Sequence[str]) -> float:
```

Hints do nothing at runtime. They are there so that you — and your examiner — can see what goes in and what comes out without reading the body. Use them on every function you write; they cost nothing and they are the cheapest documentation available.

## 1.7 f-strings

```python
print(f"{token}: {weight:.2f}")        # winner: 2.81
print(f"P(spam) = {probability:.1%}")  # P(spam) = 94.0%
```

`:.2f` is two decimal places, `:.1%` formats as a percentage. The UI uses these constantly — nobody wants to read `0.9403726`.

## 1.8 Working in log space

One mathematical fact drives all of chapter 4:

```
log(a × b) = log(a) + log(b)
```

In Python:

📄 **Why logs are not optional here**
```python
import math

p = 0.001
product = p ** 300      # 300 small probabilities multiplied
print(product)          # 0.0   - not approximately zero. Exactly zero.

log_sum = 300 * math.log(p)
print(log_sum)          # -2072.3  - a perfectly ordinary number
```

A `float` cannot hold a number smaller than about 1e-308. Multiply 300 probabilities and you fall off the bottom of what the hardware can represent, and the result is exactly `0.0` — for both classes, so the comparison becomes meaningless. Adding logarithms stays comfortably in range.

❓ **Why can we compare log scores instead of probabilities?**

Because `log` is strictly increasing: if `a > b` then `log(a) > log(b)`. Taking logs changes the numbers but never their order, and classification only needs the order. You then convert back to a probability at the very end, once, using the sigmoid of the *difference* — never by exponentiating each score on its own.

## 1.9 Running the tests

```bash
pytest -v                                 # everything
pytest tests/test_naive_bayes.py -v       # one file
pytest -k "laplace" -v                    # tests matching a name
pytest -x                                 # stop at the first failure
pytest --cov=spamclassifier               # coverage
```

`pytest -x` is the one to use while building: a single failure in full detail beats ninety failures scrolling past.
