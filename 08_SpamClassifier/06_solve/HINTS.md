# SpamClassifier — hints, checks and traps, stage by stage

Use this file when you are **stuck** on a function of your skeleton. For each hard function:

- **Learn it in** — the theory section, notebook and exercise that teach the idea.
- **Hints** — hidden. Open one at a time: 💡 a nudge, 🔧 the steps.
- **Check yourself** — numbers to compare against before you run the tests.
- **Traps** — the mistakes that make a test fail (or pass while the program is wrong).

`CHECKLIST.md` (next to this file) lists **every** function you have to write. The docstrings and
`04_build/10_build.md` give the step-by-step; this file is for when those are not enough.

> **The working loop.** One function → run **its** test (`pytest tests/test_naive_bayes.py -k priors -v`) →
> green → commit → next. Read the *last* lines of a red test first.

---

## Stage 1 — Data and splitting

**Learn it in:** theory `02_ml_basics` §2.3–2.5

### `stratified_split`

<details><summary>🔧 Hint</summary>

```
n_test = round(len(texts) * config.TEST_RATIO)
n_val  = round(len(texts) * config.VAL_RATIO)
rest_t, test_t, rest_y, test_y = train_test_split(texts, labels, test_size=n_test, stratify=labels, random_state=seed)
train_t, val_t, train_y, val_y = train_test_split(rest_t, rest_y, test_size=n_val, stratify=rest_y, random_state=seed)
```

Whole numbers, not ratios: `0.15 / 0.85` of 85 messages is `15.000000000000002`, which scikit-learn rounds **up**
to 16.
</details>

**Check yourself:** 100 messages → 70 / 15 / 15. `class_balance` of 20 spam in 100 →
`{"ham": 80, "spam": 20, "spam_ratio": 0.2}`.

**Trap:** dropping duplicates **after** splitting. Do it in `load_corpus`, before anything else — the same text in
train and test means the model has seen the answer.

---

## Stage 2 — Cleaning and tokenizing

**Learn it in:** theory `03_features` §3.8–3.9 · notebook `01_text_to_numbers` §1–3 · exercises **ex01–ex03**

### `EmailParser.parse` — the order is the point

<details><summary>🔧 Hint — the order</summary>

1. `truncate` → 2. `split_headers` → 3. **measure** caps / `!` / digits on `f"{subject} {body}"`, and URLs / tags on
the body → 4. `strip_html` → 5. `replace_urls` → 6. lower-case, then put the token back:
`body.lower().replace(config.URL_TOKEN.lower(), config.URL_TOKEN)`.
</details>

**Check yourself** — `"Subject: Big OFFER!!\nFrom: spam@x.ru\n\n<b>FREE</b> money at http://x.ru/win"`:

```
subject 'big offer!!'      body 'free money at URLTOKEN'
exclamation_count 2   url_count 1   html_tag_count 2   caps_ratio 0.32 (measured before lower-casing)
tokens  ['big', 'offer', 'free', 'money', 'URLTOKEN']
```

### `split_headers`

<details><summary>💡 Hint</summary>

If the **first** line does not look like `Name: value` (`HEADER_RE`), there are no headers: return
`("", raw)`. Otherwise walk the lines: remember the Subject, and the first blank line ends the headers — everything
after it is the body. No blank line at all → the body is `""`.
</details>

### `Tokenizer.tokenize_text`

<details><summary>🔧 Hint</summary>

```
out = []
for i, part in enumerate(text.split(config.URL_TOKEN)):
    if i > 0:
        out.append(config.URL_TOKEN)          # put back the token the split removed
    out.extend(t for t in WORD_RE.findall(part.lower()) if self._keep(t))
return out
```
</details>

**Traps:** `strip_html` must replace a tag with a **space** and then collapse whitespace —
`"<b>free</b><i>offer</i>"` → `"free offer"`, not `"freeoffer"` · `caps_ratio` counts **letters** only:
`"AA!!99bb"` → 0.5 · `load_stopwords` downloads NLTK data the first time — catch `LookupError`,
`nltk.download("stopwords")`, try again.

---

## Stage 3 — Features

**Learn it in:** theory `03_features` §3.3–3.6 · notebook `01_text_to_numbers` §4–5 · exercises **ex04–ex07**

### `FeatureEngineer.fit`

<details><summary>🔧 Hint</summary>

```
df = {}
for m in messages:
    for t in set(ngrams(self._tokenizer.tokenize(m), NGRAM_MIN, NGRAM_MAX)):   # set: once per message
        df[t] = df.get(t, 0) + 1
keep = sorted(df, key=lambda t: (-df[t], t))[:config.MAX_FEATURES]           # most messages first, ties by name
self._vocabulary = sorted(keep)
self._idf = {t: self.idf_value(len(messages), df[t]) for t in self._vocabulary}
self._fitted = True
return self                                                                  # the tests chain .fit(...)
```
</details>

**Check yourself:** `idf_value(10, 1)` = ln 5 + 1 = **2.609** · `idf_value(10, 9)` = **1.0** ·
`l2_normalise({"a": 3, "b": 4})` = `{"a": 0.6, "b": 0.8}`.

**Traps:** `fit` must `return self` · `transform` before `fit` raises `RuntimeError` · terms outside the vocabulary
are **dropped** (`to_dense` gives every message the same width) · `handcrafted` returns the keys in
`config.HANDCRAFTED_FEATURES` order — build the dict in that order.

---

## Stage 4 — Naive Bayes, from scratch

**Learn it in:** theory `04_naive_bayes` §4.4–4.10 (do the §4.10 worked example by hand) · notebook
`02_naive_bayes_from_scratch` · exercises **ex08–ex11**

### `fit`

<details><summary>🔧 Hint</summary>

The vocabulary is **all** distinct tokens of **both** classes. For each class: the prior is
`log(n_c / N)`; count every occurrence (`Counter`) of the class's documents; then for **every** word of the
vocabulary — including words that never appear in that class — `log((count + alpha) / (total + alpha * |V|))`.
</details>

**Check yourself** — the tiny corpus of `conftest.py` (2 spam, 2 ham, 10 words, alpha 1):

```
P(free | spam) = (2 + 1) / (6 + 10) = 0.1875      P(free | ham) = (0 + 1) / (6 + 10) = 0.0625
predict_proba(["free"])            0.75
predict_proba(["meeting"])         0.25
predict_proba(["free", "prize"])   0.8571
predict_proba(["free"] * 300)      1.0 (not nan, not 0.0)
log_odds: free +1.099   prize +0.693   meeting -1.099   an unseen word 0.0
```

### `predict_proba` — without underflow

<details><summary>🔧 Hint</summary>

```
s = self.predict_log_scores(tokens)
d = s[HAM] - s[SPAM]
if d > 700:  return 0.0
if d < -700: return 1.0
return 1 / (1 + math.exp(d))
```
</details>

**Traps:** smoothing at predict time (unknown tokens are **skipped**) · counting documents instead of occurrences
(that is Bernoulli NB, and `test_matches_sklearn` fails) · `explain` must de-duplicate tokens before ranking —
`dict.fromkeys(tokens)` keeps the first occurrence of each, in order.

`test_matches_sklearn` is the one that proves your counting, smoothing and logs are right to 10⁻⁹. If it fails
and the others pass, print your `P(w|c)` table next to `np.exp(reference.feature_log_prob_)`.

---

## Stage 5 — SVM and comparison

**Learn it in:** theory `05_svm_comparison` §5.4–5.6 · notebook `03_compare_and_threshold` §1–2

- `SVMClassifier.fit`: `StandardScaler` → `LinearSVC`, wrapped in `CalibratedClassifierCV` (the docstring has the
  code). Without the scaler, `message_length` (thousands) drowns the TF-IDF values (0 to 1).
- `cross_validate`: the full code is in `04_build/10_build.md`, stage 5. Pass the **class** as the factory:
  `cross_validate(NaiveBayesClassifier, texts, labels)` — every call gives a fresh, unfitted model.
- `compare`: a gap smaller than the larger standard deviation is "no significant difference". Say it.

**Check yourself:** on the 10-message `data/sample_messages.csv` with 3 folds both models run without warnings and
give means with a large spread (±0.15–0.25) — on 10 messages that is the honest answer. The real corpus is what
counts.

---

## Stage 6 — Threshold and bundle

**Learn it in:** theory `06_evaluation` §6.1–6.5 · notebook `03` §3 · exercises **ex12–ex13**

### `choose_threshold`

<details><summary>🔧 Hint</summary>

Loop `t` over `np.arange(SEARCH_START, SEARCH_STOP, SEARCH_STEP)` (round each `t` to 2 decimals); keep the `t`
whose precision clears the floor with the **highest recall**. Track the best precision you saw, so that the
`ValueError` can say it: `"no threshold reaches precision 0.98; best was 0.833"`.
</details>

**Check yourself** — `PROBS` / `LABELS` of `test_threshold.py`:

| floor | threshold | precision | recall |
|---|---|---|---|
| 0.50 | 0.50 | 0.714 | 1.0 |
| 0.80 | 0.56 | 0.833 | 1.0 |
| 0.98 | 0.86 | 1.0 | 0.8 |

**Trap:** choosing on the test split. The threshold is chosen on **validation**; the test split is read once, by
`evaluate.py`.

### `ModelBundle.save / load`

Build into `<version>.partial`, write every file, write `checksum.txt` **last**, then `os.replace` the folder into
place. `load` checks files → checksums → feature contract, and only then unpickles. `compute_checksum`: one
`hashlib.sha256()`, `update()` with the bytes of each file in **sorted** name order, `checksum.txt` excluded.

---

## Stage 7 — Database, UI and the explanation

**Learn it in:** the docstrings of `database/` · `04_build/10_build.md` stage 7

- The repositories here take a **connection** (`ScanRepository(conn)`), not a `Database` object. After every
  `INSERT` / `UPDATE`: `self._conn.commit()`.
- `ScanRepository.save`: `body[:config.BODY_EXCERPT_CHARS]`; reasons as
  `json.dumps([[r.token, r.weight] for r in verdict.reasons])`; `scanned_at = datetime.now().isoformat()`.
- `recent`: `ORDER BY scanned_at DESC, id DESC LIMIT ?` — two scans in the same microsecond still come out in order.
- `FeedbackRepository.mark_used` returns `cur.rowcount`.
- `SpamFilter.classify` must call the **same** parser, tokenizer and engineer that `train.py` used — that is what
  `test_pipeline.py` protects.

**Check yourself:** `pytest -v` fully green (91 tests).

---

## Stage 8 — Train, measure, write

Follow the ten steps of `train.py` in order. The two lines that can quietly ruin the project are step 4 (the
vocabulary is fitted on **train** only) and step 7 (the threshold on **validation** only). Run `assert_no_leakage`
every time.

---

## When nothing works

| Symptom | Likely cause |
|---|---|
| `LookupError: Resource stopwords not found` | `nltk.download("stopwords")` once — or let `load_stopwords` do it |
| `test_matches_sklearn` off by a little | smoothing denominator: `total + alpha * |V|` with `|V|` = the vocabulary of **both** classes |
| `predict_proba` returns `nan` or 0.0 on long mail | `exp` taken of a single score instead of the difference |
| every message gets ≈ the same probability | the engineer was refitted at scan time, or the bundle's vocabulary differs from training |
| `ConvergenceWarning` from `LinearSVC` | the `StandardScaler` is missing |
| `URLTOKEN` missing from the tokens | `parse` lower-cased it to `urltoken` — put it back after `.lower()` |
| `sqlite3.IntegrityError: FOREIGN KEY` | feedback for a scan id that does not exist |
