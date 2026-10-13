# Step 7b — Walking the stages

💡 **In short:** the previous step gave you the order. This one walks each stage with the code. Keep it open next to the editor.

---

## Stage 1 — Loading documents

**File:** `nlp/loader.py`
**Done when:** you can print the text of a PDF, a DOCX and a TXT and it looks right.

No test file for this one, because "did the PDF extract correctly" is a judgement your eyes make, not an assertion.

📄 **`loader.py`**
```python
def load(path):
    suffix = Path(path).suffix.lower()
    if suffix == ".pdf":
        return _load_pdf(path)
    if suffix == ".docx":
        return _load_docx(path)
    if suffix == ".txt":
        return Path(path).read_text(encoding="utf-8", errors="replace")
    raise ValueError(f"unsupported file type: {suffix}")
```

Two things that will bite you:

- **A scanned PDF has no text layer.** It extracts as an empty string, silently. Check for that and report the file by name rather than indexing a blank document — a blank CV scores 0 against everything and looks like a ranking bug.
- **`errors="replace"`** on the text path. CVs arrive in whatever encoding the sender's machine used, and one bad byte should not crash a batch of 500.

---

## Stage 2 — Preprocessing ★ the gatekeeper

**File:** `nlp/preprocessor.py`
**Done when:** all of `test_preprocessor.py` is green.

Do not move past this. Everything downstream consumes its output, and a bug here does not look like a preprocessing bug — it looks like a ranking bug, three stages later.

📄 **`process`**
```python
def process(self, text: str) -> list:
    text = text.lower()
    tokens = TOKEN_RE.findall(text)
    tokens = [t for t in tokens if not self._is_stopword(t)]
    if self._use_stemming:
        tokens = [self._stem(t) for t in tokens]
    if self._ngram_max > 1:
        tokens = tokens + self._bigrams(tokens)
    return tokens
```

The order is the contract. Stop words go **before** stemming — stemming them first turns "the" into something that no longer matches your stop list.

❓ **Why must technical tokens survive tokenizing?**

Because `c++`, `c#`, `node.js` and `.net` are skills, and a tokenizer that splits on every non-letter destroys all four. `test_technical_tokens_survive` pins them. Your `TOKEN_RE` has to allow `+`, `#` and `.` inside a token.

📄 **`fingerprint` — the part that saves you later**
```python
def fingerprint(self) -> dict:
    return {
        "use_stemming": self._use_stemming,
        "ngram_max": self._ngram_max,
        "stopword_count": len(self._stopwords),
        "token_pattern": TOKEN_RE.pattern,
    }
```

This goes into the index bundle in Stage 7 and is checked when the bundle loads. It is four lines and it is the difference between a loud failure and a silent one.

---

## Stage 3 — Vocabulary and IDF

**File:** `nlp/vocabulary.py`
**Done when:** `test_vocabulary.py` is green.

📄 **`build`**
```python
def build(self, processed_docs: list):
    df = Counter()
    for doc in processed_docs:
        df.update(set(doc))            # set() - once per document

    n = len(processed_docs)
    keep = [t for t, count in df.items()
            if count >= self._min_df and count / n <= self._max_df]
    keep.sort()                        # stable order, every run

    self.vocabulary = {term: i for i, term in enumerate(keep)}
    self.idf = [self.compute_idf(df[t], n) for t in keep]
```

Two lines carry the stage. `set(doc)` is document frequency rather than term frequency — Step 0.5 covered why. `keep.sort()` is not cosmetic: a vocabulary built from an unordered set gives different column indices on different runs, and then two index bundles built from the same data disagree.

📄 **The two IDF variants**
```python
@staticmethod
def compute_idf(df: int, n_docs: int) -> float:
    return math.log((1 + n_docs) / (1 + df)) + 1          # smoothed, for TF-IDF

@staticmethod
def compute_idf_bm25(df: int, n_docs: int) -> float:
    return math.log(1 + (n_docs - df + 0.5) / (df + 0.5))  # probabilistic
```

They are different on purpose and you will be asked why. The first comes from the vector space model; the second from the probabilistic relevance framework. The `1 +` inside the BM25 log is what keeps it positive for a term appearing in more than half the collection — without it, a common term would *subtract* from a candidate's score.

---

## Stage 4 — TF-IDF and cosine

**File:** `rank/tfidf.py`
**Done when:** `test_tfidf.py` is green.

📄 **`fit`**
```python
def fit(self, processed_docs, vocabulary, idf):
    rows, cols, values = [], [], []
    for row, doc in enumerate(processed_docs):
        tf = Counter(doc)
        for term, count in tf.items():
            if term in vocabulary:
                col = vocabulary[term]
                rows.append(row); cols.append(col)
                values.append(count * idf[col])

    self._matrix = csr_matrix((values, (rows, cols)),
                              shape=(len(processed_docs), len(vocabulary)))
    self._matrix = self._l2_normalise_rows(self._matrix)
```

Only non-zero entries are stored — that is the sparse matrix, and it is the dictionary idea from Step 0.2 with an index instead of a key.

📄 **Why `rank` is one line of arithmetic**
```python
def rank(self, job_terms, top_k):
    q = self._vectorise_job(job_terms)       # also L2-normalised
    scores = self._matrix @ q                # cosine, because both are unit length
    top = np.argsort(-scores)[:top_k]
    return [(int(i), float(scores[i])) for i in top]
```

`cos(a,b) = (a·b) / (|a||b|)`, and both norms are 1, so the denominator disappears and cosine *is* the dot product. True here, not true in general — say it that way if you are asked.

💡 If a cosine score comes out above 1.0, you normalised twice or not at all. There is no third cause.

---

## Stage 5 — BM25

**File:** `rank/bm25.py`
**Done when:** `test_bm25.py` is green.

📄 **`_term_score` — the whole formula**
```python
def _term_score(self, tf: int, doc_length: int, idf: float) -> float:
    norm = 1 - self.b + self.b * (doc_length / self._avg_doc_length)
    return idf * (tf * (self.k1 + 1)) / (tf + self.k1 * norm)
```

Read the two halves separately:

**Saturation.** As `tf` grows, the fraction approaches `k1 + 1` and stops. The tenth occurrence of "Python" adds almost nothing over the ninth. Compare that with TF-IDF, where the tenth counts exactly as much as the first — this is the real difference between the two methods, and it is in one line.

**Length normalisation.** `norm` is 1 for a document of average length, above 1 for a long one, below for a short one, and it sits in the denominator — so a long document is penalised. `b` controls how much: at `b = 0` the term vanishes and length is ignored entirely; at `b = 1` it applies in full.

❓ **Set `b = 0` and run it. Who wins, and why?**

Long CVs. With no length normalisation a 9-page CV contains more of every term and outscores a 1-page CV from an equally good candidate. That is the unfairness the whole project is about, and your MRR-vs-`b` chart is the evidence.

---

## Stage 6 — Skills, explanation, metrics

**Files:** `rank/skills.py`, `rank/explainer.py`, `eval/metrics.py`
**Done when:** `test_metrics.py` is green.

📄 **`precision_at_k` and `reciprocal_rank`**
```python
def precision_at_k(ranking: list, relevant: set, k: int) -> float:
    top = ranking[:k]
    if not top:
        return 0.0
    return sum(1 for doc in top if doc in relevant) / len(top)


def reciprocal_rank(ranking: list, relevant: set) -> float:
    for position, doc in enumerate(ranking, start=1):
        if doc in relevant:
            return 1.0 / position
    return 0.0                      # nothing relevant found at all
```

`len(top)` rather than `k` in the denominator: if a query returns three results and you asked for five, precision is out of three. Dividing by five would punish the ranker for the collection being small.

📄 **The explanation, and the test that makes it trustworthy**
```python
def explain(self, doc_row, q):
    row = self._matrix.getrow(doc_row)
    contributions = [(term, row[0, col] * q[col])
                     for term, col in self._vocabulary.items()
                     if row[0, col] and q[col]]
    return sorted(contributions, key=lambda kv: -abs(kv[1]))
```

Because the score is a sum of per-term products, each product is one term's **exact** contribution — not an estimate. The test sums all of them and asserts equality with the score to 1e-9, and that test is why you can say "exact" rather than "approximately" in the room.

---

## Stage 7 — The index bundle

**File:** `rank/bundle.py`

The bundle holds the vocabulary, the IDF tables, the document matrix, the average document length BM25 needs, the preprocessing fingerprint, and a version.

📄 **Load, in this order**
```python
def load(path):
    data = _read(path)
    stored = data["preprocess"]
    current = TextPreprocessor().fingerprint()
    if stored != current:
        differences = {k: (stored.get(k), current.get(k))
                       for k in set(stored) | set(current)
                       if stored.get(k) != current.get(k)}
        raise ValueError(f"preprocessing contract mismatch: {differences}")
    return ...
```

Naming the differing fields matters. "Contract mismatch" sends you hunting; "`use_stemming`: True vs False" tells you what happened.

**Demo this in the defence.** Edit the stored fingerprint by hand, run `run.py`, show the refusal. Thirty seconds, and it demonstrates you understand deployment and not only algorithms.

---

## Stages 8–10 — Database, controller, GUI

Build the controller and get it working **before** writing any Tkinter. If the controller is right the views are mechanical; if it is wrong you will be debugging logic through a GUI, which is miserable and slow.

Every SQL statement goes in `database/repositories.py`, parameterised:

```python
# correct
conn.execute("INSERT INTO jobs (title, text) VALUES (?, ?)", (title, text))

# never
conn.execute(f"INSERT INTO jobs (title, text) VALUES ('{title}', '{text}')")
```

A CV is a file somebody sent you. Treat it as untrusted for exactly as long as it is in your program.

---

## Stage 11 — The experiments

Step 7 already lists the sweeps and the figures. One addition: **record every run in the database as you go**, not at the end.

```python
for k1 in (0.5, 1.2, 1.5, 2.0):
    for b in (0.0, 0.25, 0.5, 0.75, 1.0):
        results = evaluate(ranker, jobs, relevant, preprocessor)
        repo.save_run(k1=k1, b=b, **results)
```

Twenty runs, and if you crash on the eighteenth you still have seventeen. Reconstructing numbers you have already computed, in June, is the worst possible use of the last fortnight.

💡 Write the results chapter while the experiments run. The figures are fresh, you remember why each sweep was worth doing, and the book stops being a thing you dread.
