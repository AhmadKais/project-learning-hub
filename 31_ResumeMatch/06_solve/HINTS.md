# ResumeMatch — hints, checks and traps, stage by stage

Use this file when you are **stuck** on a function of your skeleton. For each hard function:

- **Learn it in** — the theory section, notebook and exercise that teach the idea.
- **Hints** — hidden. Open one at a time: 💡 a nudge, 🔧 the steps.
- **Check yourself** — numbers to compare against before you run the tests.
- **Traps** — the mistakes that make a test fail (or pass while the ranking is wrong).

`CHECKLIST.md` (next to this file) lists **every** function you have to write. Most docstrings already contain the
code shape, and `04_build/07_build.md` / `07b_stages.md` give the stages; this file is for when those are not
enough.

> **The working loop.** Read the failing test **first**, then write the code until it passes
> (`pytest tests/test_vocabulary.py -v`). The tests define the exact behaviour.

All numbers below use the three-document collection of `tests/conftest.py`:

```
doc0: python django python      doc1: python java      doc2: java sql
```

---

## Stage 1 — Load documents

**Learn it in:** theory `04_pipeline` (the pipeline in order)

- `_load_docx`: walk `doc.paragraphs` **and** `doc.tables` → `table.rows` → `row.cells` → `cell.text`. Half of many
  CVs lives in a table.
- `_clean`: `re.sub(r"-\n(\w)", r"\1", text)` joins `develo-\nper`; `re.sub(r"\s+", " ", text)` collapses every
  whitespace, `\xa0` included.
- `load_directory`: `try` / `except ResumeMatchError` **per file** — one corrupt PDF must not stop the other 199.

**Check yourself:** open three extracted texts and read them. If two columns came out interleaved, fix it now.

---

## Stage 2 — The preprocessing pipeline ★

**Learn it in:** theory `04_pipeline` · notebook `01_preprocessing` · exercises **ex01–ex03**

### `TextPreprocessor.process`

The order is fixed: scrub PII → tokenize → lower-case → stop words → stem → drop 1-letter tokens → add bigrams.

**Check yourself:**

```
process("I know C++ and C# and .NET well")        (no stemming, no bigrams)
    -> ['know', 'c++', 'c#', '.net', 'well']
process("developed developing develops developer development")   -> all five become 'develop'
process("machine learning engineer")
    -> ['machin', 'learn', 'engin', 'machin learn', 'learn engin']
process("Docker.")                                 -> ['docker']      (no trailing dot)
```

**Traps:** loading the NLTK stop words **inside** `process` (the whole project crawls — load them once in
`__init__`) · `config.TOKEN_PATTERN` is the only tokenizer — never `\w+` (it turns `C++` into `c`) · stripping
more than one Hebrew prefix · `if min_df` instead of `if min_df is None` (0 is a real value).

### `fingerprint`

Every field of the docstring, nothing invented. `test_fingerprint_changes_with_settings` checks that turning
stemming off changes it — that is the two-machine contract.

---

## Stage 3 — Vocabulary and IDF

**Learn it in:** theory `01_vectors`, `03_bm25` ("BM25 uses a different IDF") · notebook `02_tfidf_cosine` §1 ·
exercises **ex04, ex05, ex09**

<details><summary>🔧 Hint — document frequency</summary>

```
doc_freq = Counter()
for doc in processed_docs:
    doc_freq.update(set(doc.terms))        # set: python twice in doc0 still counts once
```
</details>

**Check yourself** (`min_df=1, max_df=1.0`):

| term | df | TF-IDF idf = ln((1+N)/(1+df)) + 1 | BM25 idf = ln((N−df+0.5)/(df+0.5) + 1) |
|---|---|---|---|
| django | 1 | 1.6931 | 0.9808 |
| java | 2 | 1.2877 | 0.4700 |
| python | 2 | 1.2877 | 0.4700 |
| sql | 1 | 1.6931 | 0.9808 |

Vocabulary (sorted): `{'django': 0, 'java': 1, 'python': 2, 'sql': 3}`.

---

## Stage 4 — TF-IDF + cosine

**Learn it in:** theory `02_cosine` · notebook `02_tfidf_cosine` · exercises **ex06–ex08**

**Check yourself** — `rank(["python", "django"], top_k=3)`:

```
doc0 0.9431     doc1 0.4280     doc2 0.0000
```

**Traps:** recomputing an IDF from the job (one document cannot define document frequency — use the collection's) ·
forgetting to L2-normalise the rows (then a longer CV scores higher — `test_longer_document_is_not_favoured`) ·
`np.argsort(-scores)` gives the best first; `rank_position` starts at **1**.

<details><summary>🔧 Hint — <code>explain</code> with a sparse row</summary>

```
row = self.matrix.getrow(doc_row)
for col, value in zip(row.indices, row.data):     # only the non-zero cells
    if q[col] > 0:
        contributions.append((term_of[col], value * q[col]))
```

Build `term_of = {i: t for t, i in vocabulary.items()}` once in `fit`. The sum of **all** contributions equals the
score exactly — that is the decomposition the test checks.
</details>

---

## Stage 5 — BM25

**Learn it in:** theory `03_bm25` · notebook `03_bm25` · exercises **ex09–ex11**

**Check yourself:**

```
avgdl = (3 + 2 + 2) / 3 = 2.333
saturation factor with doc_length == avgdl, k1 = 1.5:
    tf 1 -> 1.00    tf 2 -> 1.43    tf 5 -> 1.92    tf 20 -> 2.33    never above k1 + 1 = 2.5
rank(["python", "django"], top_k=3):
    doc0 raw 1.4840 -> 1.0000     doc1 raw 0.5023 -> 0.3385     doc2 -> 0.0 (filled in, never touched)
```

**Traps:** using the TF-IDF idf in BM25 (a silent accuracy bug — the docstring warns) · with fewer scoring documents
than `top_k`, fill up with the untouched ones at score 0 (the test expects `top_k` positions) · `b = 0` must switch
the length normalisation off completely (`test_b_zero_disables_length_normalisation`).

---

## Stage 6 — Skills, explanation and metrics

**Learn it in:** theory `05_explain`, `06_evaluate` · notebook `04_evaluate` · exercises **ex12, ex13**

### `SkillExtractor.load` — the same pipeline as the CVs

<details><summary>🔧 Hint</summary>

```
words = [t for t in self.preprocessor.process(name) if " " not in t]    # single words only
self.skills[" ".join(words)] = row["skill"]
```

`process("Machine Learning")` returns `['machin', 'learn', 'machin learn']`. Joining all three would store
`"machin learn machin learn"`, which no CV contains; joining the single words stores `"machin learn"` — exactly the
bigram the CV's own `process()` produces.
</details>

**Check yourself:** for the text *"Experienced in machine learning, Python and Docker. Test driven development
fan, TDD, .NET and C# too."* `extract(process(text))` → `['C#', 'Docker', 'Machine Learning', 'Python',
'Test Driven Development']` (TDD is found through its alias — three-word skills cannot match on their own).

### The metrics

`precision_at_k` divides by **k**, not by `len(top)`. `reciprocal_rank`: first relevant at position 1 → 1.0, at 2
→ 0.5, none → 0.0. `mean_reciprocal_rank` averages **only** the jobs that have labels.

---

## Stage 7 — The index bundle and two machines

Save JSON and `.npz`, never pickle. `load` checks: files → code version → SHA-256 of `matrix.npz` → **every**
fingerprint field. Test it for real: build on one computer, copy the folder, change one setting on the other
(`USE_STEMMING = False`) and check that `load` refuses with the field's name.

---

## Stages 8–11 — Database, GUI, experiments

- Repositories: the four shapes in the docstring at the top of `repositories.py`; labels are stored **before** you
  look at a ranking (`before_ranking = 1`) — otherwise you grade the system with its own answers.
- `tune.py`: change one of `k1`, `b` at a time, keep every row, and report the MRR **with** the number of labelled
  jobs — 10 jobs is a small sample; say so.

---

## When nothing works

| Symptom | Likely cause |
|---|---|
| every score is 0.000 on machine B | the fingerprint differs (stemming, stop words, regex) — `load` should have refused |
| `LookupError: Resource stopwords not found` | `python -c "import nltk; nltk.download('stopwords')"` once |
| `C++` developers never rank | a tokenizer other than `config.TOKEN_PATTERN` somewhere |
| "Docker." and "Docker" are two terms | an old `TOKEN_PATTERN` without `(?<!\.)` at the end |
| no two-word skill is ever found | bigrams joined into the skill key (see stage 6) |
| `TypeError: only 0-dimensional arrays ...` | `float()` of a 1-element array — take `[0]` first |
| BM25 favours long CVs | `b` not used, or `avgdl` computed from the wrong lengths |
