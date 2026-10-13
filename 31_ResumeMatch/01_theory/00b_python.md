# Step 0 — The Python you need

💡 **In short:** dictionaries, comprehensions, `Counter`, sets and `math.log`. Five things. If they are comfortable, go straight to Step 1.

The intro said you need functions, classes, lists and dictionaries. That is true, but four of those get used in a particular way in this project, and it is worth seeing them once before they appear inside a ranking formula.

## 0.1 A document is a dictionary

Every document in this project — every CV, every job advert — ends up as a dictionary from a term to a number.

📄 **The shape of everything**
```python
weights = {"python": 0.41, "sql": 0.22, "docker": 0.18}

weights["python"]             # 0.41
weights.get("rust", 0.0)      # 0.0  - safe default, no KeyError
"sql" in weights              # True
weights.items()               # ("python", 0.41), ("sql", 0.22), ...
```

`.get(term, 0.0)` is the one to internalise. A job advert will constantly ask for terms a CV does not contain, and `weights["rust"]` raises `KeyError` and crashes the ranking. `weights.get("rust", 0.0)` returns the right answer: that candidate scores zero on that term.

## 0.2 This is already a sparse vector

You will read "sparse matrix" in Step 1 and it sounds like a new data structure. It is not. A dictionary that only stores the terms a document actually contains **is** a sparse vector.

```
dense:   [0, 0, 0.41, 0, 0, 0.22, 0, 0, ...]   20,000 slots, 300 non-zero
sparse:  {"python": 0.41, "sql": 0.22, ...}     300 entries
```

Same information. The dense version is 98.5% zeros and, as the exam chapter notes, 80 MB at 500 documents. The dictionary is 1.8 MB. That is the entire argument, and you now already understand it.

## 0.3 Comprehensions

📄 **Four you will write repeatedly**
```python
# lower-case every term
lowered = [t.lower() for t in terms]

# drop the short ones
kept = [t for t in terms if len(t) > 2]

# build a dict from a list
lengths = {t: len(t) for t in terms}

# scale every weight - this is L2 normalisation in miniature
scaled = {t: w / norm for t, w in weights.items()}
```

That last one is the normalisation step from Step 2, with the square root left out. When you meet it in the real code it will not be new.

## 0.4 Counter does the counting

`collections.Counter` is a dictionary that counts. Term frequency is one line with it.

📄 **Term frequency**
```python
from collections import Counter

tf = Counter(["python", "sql", "python", "docker"])
# Counter({"python": 2, "sql": 1, "docker": 1})

tf["python"]          # 2
tf["rust"]            # 0   - no KeyError, unlike a plain dict
tf.most_common(2)     # [("python", 2), ("sql", 1)]
sum(tf.values())      # 4   - the document length, which BM25 needs
```

That last line matters more than it looks. BM25 normalises by document length relative to the collection average, so `sum(tf.values())` is not a detail — it is an input to the formula.

## 0.5 Sets, and why document frequency needs one

```python
terms = ["python", "python", "python", "sql"]

len(terms)        # 4  - occurrences
len(set(terms))   # 2  - distinct terms
```

Document frequency counts **in how many documents** a term appears, so a CV that says "Python" eleven times counts once. Use `set()` when building the vocabulary, and the eleven-times CV stops distorting the IDF of every other document.

Get this wrong and nothing crashes — the IDF weights are simply wrong, and every ranking that follows is wrong with them.

## 0.6 Logarithms

Two facts carry the whole of IDF:

```python
import math

math.log(1)      # 0.0     - a term in every document adds nothing
math.log(100)    # 4.6     - a rare term adds a lot
math.log(10000)  # 9.2     - much rarer, but only twice the weight
```

The third line is the point. Rarity multiplied by 100 raises the weight by a factor of two, not a hundred. That compression is why IDF uses a log at all, and it is the first question in the exam chapter.

`math.log` is the natural log (base *e*). The base does not matter for ranking — switching to base 10 scales every weight by the same constant and changes no ordering — but be consistent, and say `ln` when you mean natural log.

## 0.7 Dataclasses

📄 **From `models/entities.py`**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ScoredCandidate:
    name: str
    score: float
    matched_terms: dict

c = ScoredCandidate("Amir", 0.81, {"python": 0.41})
c.score        # 0.81
c.score = 0.9  # FrozenInstanceError
```

`frozen=True` means a score cannot be edited after it was produced. That is deliberate: a ranking you could quietly rewrite afterwards would make the stored results worthless as evidence.

## 0.8 Running the tests

```bash
pytest -v                               # all of them
pytest tests/test_bm25.py -v            # one file
pytest -k "idf" -v                      # anything with "idf" in the name
pytest -x                               # stop at the first failure
```

`pytest -x` is the one to use while building. One failure in full detail is far more useful than fifty scrolling past.

💡 When you are not sure what a function should return, **read its test**. The expected numbers were worked out by hand; your job is to make the code agree with them.
