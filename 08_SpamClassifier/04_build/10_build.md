# Chapter 10 — Building it, stage by stage

💡 **In short:** eight stages, in order. Each one ends with a set of tests going green. Do not start the next until the current one is done — every stage is built on the one before it.

---

## Stage 1 — Data and splitting

**Files:** `ml/dataset.py`
**Green at the end:** `pytest tests/test_dataset.py -v`

### 1.1 Get the corpus

Download SMS Spam Collection or Enron-Spam (see `data/README.md`) and save it as `data/corpus/messages.csv` with two columns, `text` and `label`.

### 1.2 Load it

📄 **`load_corpus`**
```python
import pandas as pd

def load_corpus(path=None):
    path = path or config.CORPUS_PATH
    frame = pd.read_csv(path)

    for column in ("text", "label"):
        if column not in frame.columns:
            raise ValueError(f"corpus is missing the '{column}' column")

    bad = set(frame["label"].unique()) - {"spam", "ham"}
    if bad:
        raise ValueError(f"unexpected labels: {sorted(bad)}")

    before = len(frame)
    frame = frame.drop_duplicates(subset="text")
    dropped = before - len(frame)
    if dropped:
        print(f"dropped {dropped} duplicate messages")

    texts = frame["text"].astype(str).tolist()
    labels = [1 if lab == "spam" else 0 for lab in frame["label"]]
    return texts, labels
```

The de-duplication is not tidiness. Public corpora contain repeated messages, and if the same text lands in both train and test, the model has literally seen the answer. This is the cheapest leak prevention available.

### 1.3 Check the balance

📄 **`class_balance`**
```python
def class_balance(labels):
    spam = sum(labels)
    ham = len(labels) - spam
    return {"ham": ham, "spam": spam, "spam_ratio": spam / len(labels)}
```

Print it immediately after loading. If the ratio is nowhere near the ~13% the literature reports, something is wrong with the corpus — find out now, not after training.

### 1.4 Split, stratified and seeded

See chapter 2, section 2.4. Two `train_test_split` calls, `stratify=` on both, `random_state=config.RANDOM_SEED`.

### 1.5 Check for leakage

📄 **`assert_no_leakage`**
```python
def assert_no_leakage(split):
    train, validation, test = set(split.train[0]), set(split.validation[0]), set(split.test[0])
    for a, b, names in ((train, validation, "train/validation"),
                        (train, test, "train/test"),
                        (validation, test, "validation/test")):
        overlap = a & b
        assert not overlap, f"{len(overlap)} texts appear in both {names}"
```

Call it from `train.py` on **every** run, not just once while developing.

---

## Stage 2 — Cleaning and tokenizing

**Files:** `preprocessing/email_parser.py`, `preprocessing/tokenizer.py`
**Green at the end:** `pytest tests/test_email_parser.py tests/test_tokenizer.py -v`

### 2.1 Build the helpers first

Each one has its own test. Write them in this order, running the tests as you go: `truncate`, `caps_ratio`, `exclamation_count`, `digit_ratio`, `count_urls`, `count_html_tags`, `strip_html`, `replace_urls`, `split_headers`. Only then write `parse`.

📄 **`split_headers`**
```python
def split_headers(self, raw):
    if "\n\n" in raw:
        header_block, body = raw.split("\n\n", 1)
    else:
        header_block, body = raw, ""

    subject = ""
    looks_like_headers = False
    for line in header_block.split("\n"):
        match = HEADER_RE.match(line)
        if match:
            looks_like_headers = True
            if match.group(1).lower() == "subject":
                subject = match.group(2).strip()

    if not looks_like_headers:
        return "", raw            # no headers at all: it is all body
    return subject, body.strip()
```

That last check is what makes `test_split_headers_without_headers` pass: a plain message with no `Name: value` lines is all body, not all headers.

📄 **`caps_ratio`**
```python
@staticmethod
def caps_ratio(text):
    letters = [c for c in text if c.isalpha()]
    if not letters:
        return 0.0
    return sum(1 for c in letters if c.isupper()) / len(letters)
```

Letters only. `isalpha()` excludes digits and punctuation from *both* the numerator and the denominator, which is what `test_caps_ratio_counts_letters_only` checks with `"AA!!99bb"`.

### 2.2 Then `parse`, in the right order

📄 **`parse`**
```python
def parse(self, raw):
    raw = self.truncate(raw)
    subject, body = self.split_headers(raw)

    raw_length = len(raw)
    caps = self.caps_ratio(body)              # BEFORE lower-casing
    excl = self.exclamation_count(body)
    digits = self.digit_ratio(body)
    urls = self.count_urls(body)
    tags = self.count_html_tags(body)

    body = self.strip_html(body)
    body = self.replace_urls(body)

    return CleanedMessage(
        subject=subject.lower(), body=body.lower(), raw_length=raw_length,
        caps_ratio=caps, exclamation_count=excl, digit_ratio=digits,
        url_count=urls, html_tag_count=tags)
```

The measurement block sits above the normalisation block. Move it below and `test_parse_measures_caps_before_lowercasing` fails — as it should.

### 2.3 The tokenizer

📄 **`tokenize_text`**
```python
def tokenize_text(self, text):
    out = []
    for part in text.split(config.URL_TOKEN.lower()):
        out.extend(t for t in WORD_RE.findall(part.lower()) if self._keep(t))
        out.append(config.URL_TOKEN)
    out.pop()                       # one too many from the final split
    return out
```

Splitting on the URL token and putting it back is how it survives a filter that would otherwise drop it. `test_url_token_survives_filtering` is there because the obvious implementation loses it.

---

## Stage 3 — Features

**Files:** `preprocessing/tokenizer.py` (`ngrams`), `features/feature_engineer.py`
**Green at the end:** `pytest tests/test_feature_engineer.py -v`

### 3.1 `ngrams`

📄
```python
def ngrams(tokens, n_min, n_max):
    tokens = list(tokens)
    out = []
    for n in range(n_min, n_max + 1):
        for i in range(len(tokens) - n + 1):
            out.append(" ".join(tokens[i:i + n]))
    return out
```

Unigrams first, then bigrams — that is the order `test_ngrams_unigrams_and_bigrams` expects.

### 3.2 `fit` and `transform`

Both are in chapter 3. The two things to get right:

- `fit` on the **training split only**
- rank the vocabulary by **document frequency** (use `set()`)

📄 **`transform`**
```python
def transform(self, message):
    if not self._fitted:
        raise RuntimeError("FeatureEngineer.transform called before fit")

    terms = ngrams(self._tokenizer.tokenize(message), config.NGRAM_MIN, config.NGRAM_MAX)
    counts = Counter(terms)
    total = len(terms) or 1

    raw = {t: (counts[t] / total) * self._idf[t]
           for t in self._vocabulary if counts[t]}
    full = {t: raw.get(t, 0.0) for t in self._vocabulary}

    return FeatureVector(tfidf=self.l2_normalise(full),
                         values=self.handcrafted(message))
```

The `RuntimeError` matters. Returning zeros instead would give you a model that trains without complaint and predicts nonsense for ever.

### 3.3 The handcrafted seven

📄
```python
def handcrafted(self, message):
    tokens = self._tokenizer.tokenize(message)
    unique_ratio = len(set(tokens)) / len(tokens) if tokens else 0.0
    text = message.text
    triggers = sum(1 for w in config.TRIGGER_WORDS if w in text)

    values = {
        "caps_ratio": message.caps_ratio,
        "exclamation_count": float(message.exclamation_count),
        "message_length": float(message.raw_length),
        "digit_ratio": message.digit_ratio,
        "url_count": float(message.url_count),
        "trigger_word_count": float(triggers),
        "unique_word_ratio": unique_ratio,
    }
    return {name: values[name] for name in config.HANDCRAFTED_FEATURES}
```

That final comprehension forces the order to match `config`. The order is part of the bundle contract, so do not rely on dictionary insertion order being right by accident.

---

## Stage 4 — Naive Bayes

**File:** `ml/naive_bayes.py`
**Green at the end:** `pytest tests/test_naive_bayes.py -v`, especially `test_matches_sklearn`

All of the code is in chapter 4. Build in this order:

1. `fit` → `test_fit_marks_fitted`, `test_priors_are_balanced`
2. `predict_log_scores` → `test_laplace_smoothing_prevents_zero`
3. `predict_proba` → `test_no_underflow_on_long_document`
4. `predict` → `test_predict_respects_threshold`
5. `log_odds`, `explain` → the explanation tests
6. `to_dict` / `from_dict` → `test_round_trip_through_dict`
7. then `test_matches_sklearn` should pass on its own

If step 7 fails, the table in chapter 4 section 4.9 maps the symptom to the cause.

💡 Before moving on: write Bayes' theorem on paper and point at the line of your code implementing each part. If you cannot, go back to chapter 4 — this is the part you will be examined on.

---

## Stage 5 — SVM and comparison

**Files:** `ml/svm_classifier.py`, `ml/comparator.py`

Code in chapter 5. The two things that go wrong:

- **refit the feature engineer inside every fold** (section 5.6)
- **`model_factory()`, not a model instance** — a reused model arrives at each fold already fitted

📄 **`cross_validate`**
```python
from sklearn.model_selection import StratifiedKFold

def cross_validate(self, model_factory, texts, labels):
    kfold = StratifiedKFold(n_splits=self.folds, shuffle=True,
                            random_state=config.RANDOM_SEED)
    scores = {"precision": [], "recall": [], "f1": []}

    for train_idx, test_idx in kfold.split(texts, labels):
        engineer = FeatureEngineer(Tokenizer()).fit([messages[i] for i in train_idx])
        model = model_factory()
        model.fit(...)
        matrix = self.confusion_matrix(predictions, [labels[i] for i in test_idx])
        scores["precision"].append(matrix.precision)
        scores["recall"].append(matrix.recall)
        scores["f1"].append(matrix.f1)

    import statistics
    return [MetricResult(name, metric, statistics.mean(v), statistics.pstdev(v))
            for metric, v in scores.items()]
```

---

## Stage 6 — Threshold and bundle

**Files:** `ml/threshold.py`, `ml/bundle.py`
**Green at the end:** `pytest tests/test_threshold.py -v`

`choose_threshold` is in chapter 6. For the bundle:

📄 **`save`, built then renamed**
```python
def save(self, vectorizer, nb_model, svm_model, threshold_choice, metrics, feature_names):
    temporary = self.path + ".partial"
    os.makedirs(temporary, exist_ok=True)

    joblib.dump(vectorizer, os.path.join(temporary, "vectorizer.pkl"))
    joblib.dump(nb_model.to_dict(), os.path.join(temporary, "nb_model.pkl"))
    joblib.dump(svm_model.to_dict(), os.path.join(temporary, "svm_model.pkl"))

    write_json(temporary, "features.json", {
        "version": self.version,
        "handcrafted": list(config.HANDCRAFTED_FEATURES),
        "tfidf_dim": len(vectorizer.vocabulary),
        "total_dim": len(feature_names)})
    ...
    write checksum.txt last
    os.rename(temporary, self.path)      # atomic: appears complete or not at all
```

Building into `.partial` and renaming at the end is the Builder pattern. A crash halfway through leaves a directory that is obviously incomplete, rather than one that looks loadable and is not.

**Test it by hand:** save a bundle, open a `.pkl` in a hex editor, change one byte, and load it. If it loads, your checksum is not being checked.

---

## Stage 7 — Database, UI, explanation

**Files:** `database/`, `explainer.py`, `spam_filter.py`, `presenters/`, `views/`, `run.py`
**Green at the end:** `pytest -v` — everything

### 7.1 Database first

📄 **`connect`**
```python
def connect(path=None):
    conn = sqlite3.connect(path or config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")       # per connection, not per database
    return conn
```

The PRAGMA is easy to forget and `test_foreign_keys_are_enabled` is there because of it: SQLite has foreign keys **off** by default, so without this line every `REFERENCES` in the schema is decoration.

### 7.2 Repositories

Parameterised queries throughout, and truncate the body:

📄
```python
def save(self, verdict, subject, body):
    cursor = self._conn.execute(
        "INSERT INTO scans (subject, body_excerpt, scanned_at, probability,"
        " threshold, verdict, model_name, model_version, top_reasons, elapsed_ms)"
        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (subject, body[:config.BODY_EXCERPT_CHARS], datetime.now().isoformat(),
         verdict.probability, verdict.threshold, verdict.label,
         verdict.model_name, verdict.model_version,
         json.dumps([{"token": r.token, "weight": r.weight} for r in verdict.reasons]),
         verdict.elapsed_ms))
    self._conn.commit()
    return cursor.lastrowid
```

### 7.3 Then the presenter, then the views

Build the presenter and get `test_pipeline.py` green **before** writing a single line of Tkinter. If the presenter is right, the views are mechanical; if it is wrong, you will be debugging logic through a GUI, which is miserable.

### 7.4 The views

Three tabs. Keep them dumb — chapter 7, section 7.2. Two rules:

- never render the pasted message as HTML, and never make a link in it clickable
- retraining goes on a worker thread; results come back via `self.after`

---

## Stage 8 — Train, measure, write

**Files:** `train.py`, `evaluate.py`

`train.py` is the ten steps in its docstring. The two that can quietly ruin the project are step 4 (fit on train only) and step 7 (threshold on validation only).

Then, once:

```bash
python3 evaluate.py
```

Fill in every row of the success-metrics table with the number you measured. A target you missed is written down as missed and discussed in the book.

💡 Finish the project book as you go, not at the end. Each stage of this chapter corresponds to a chapter of the book, and writing it while the work is fresh is far easier than reconstructing it in June.
