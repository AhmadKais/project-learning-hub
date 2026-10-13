# Step 6b — The code, file by file

💡 **In short:** a map. When a test fails and you do not know where to look, start here.

## 6b.1 Where everything lives

| File | What it does | Stage |
|---|---|---|
| `config.py` | every tunable number, including `k1` and `b` | — |
| `models/entities.py` | the frozen data objects | — |
| `nlp/loader.py` | PDF / DOCX / TXT → raw text | 1 |
| `nlp/preprocessor.py` | **the gatekeeper** — raw text → terms | 2 |
| `nlp/pii.py` | strips identifying terms before indexing | 2 |
| `nlp/vocabulary.py` | the vocabulary and the IDF table | 3 |
| `rank/base.py` | the interface both rankers implement | 4 |
| `rank/tfidf.py` | TF-IDF weights + cosine similarity | 4 |
| `rank/bm25.py` | saturation and explicit length normalisation | 5 |
| `rank/skills.py` | skill extraction, matched and missing | 6 |
| `rank/explainer.py` | score → per-term contributions | 6 |
| `eval/metrics.py` | Precision@k and MRR | 6 |
| `rank/bundle.py` | the index bundle, and the contract check | 7 |
| `database/db.py`, `repositories.py` | SQLite, and **all** the SQL | 8 |
| `controllers/app_controller.py` | all testable logic | 9 |
| `views/` | four passive Tkinter views | 10 |
| `build_index.py` | build an index bundle | 7 |
| `tune.py` | the `k1` / `b` experiments | 11 |
| `evaluate.py` | the final measurement | 11 |
| `run.py` | start the application | 10 |

## 6b.2 Which test covers what

| Test file | Covers |
|---|---|
| `test_preprocessor.py` | tokenizing, stemming, stop words, the contract |
| `test_vocabulary.py` | document frequency, IDF, both variants |
| `test_tfidf.py` | weighting, L2 normalisation, cosine |
| `test_bm25.py` | saturation, length normalisation, `k1` and `b` |
| `test_metrics.py` | Precision@k and MRR, on hand-computed examples |

Fifty-three tests in total.

## 6b.3 The two files that matter most

**`nlp/preprocessor.py`** — Step 4 calls it the gatekeeper and that is not an exaggeration. Every term that reaches either ranker passed through it. If it stems differently at ranking time from indexing time, the job's terms are not in the vocabulary, every score is `0.000`, and **nothing raises an exception**. That is the silent failure the bundle contract exists to catch.

**`rank/bm25.py`** — where your research question lives. The `k1` and `b` parameters are the only knobs in the project, and the experiment you run on them in Stage 11 is what turns "I implemented two rankers" into "I compared two rankers and here is what I found".

## 6b.4 Reading a failure

```
FAILED tests/test_bm25.py::test_saturation_limits_repeated_terms
  assert 3.81 == approx(2.94 ± 1e-09)
```

Three things to read off it: which file (BM25), which behaviour (saturation), and how far off. A score that keeps rising with repetition means the `k1` term is in the wrong place — almost always the numerator and denominator being multiplied rather than divided.

## 6b.5 Symptoms and where to look

| Symptom | Look at |
|---|---|
| Every score is exactly 0.000 | `preprocessor.py` — indexing and ranking disagree |
| Long CVs always win | `b = 0`, or L2 normalisation skipped |
| Repetition still dominates | the `k1` saturation term in `bm25.py` |
| Cosine above 1.0 | vectors not normalised, or normalised twice |
| IDF negative | BM25's IDF without the `+1` inside the log |
| Contributions do not sum to the score | `explainer.py` — a term dropped or double-counted |
| Ranking slow on 500 documents | the inverted index is not being used |
| Scores change between runs | vocabulary built from a set with no stable ordering |
