# Chapter 8 — The code, file by file

💡 **In short:** a map. When a test fails and you do not know where to look, start here.

## 8.1 Where everything lives

| File | What it does | Stage |
|---|---|---|
| `config.py` / `config.yaml` | every tunable number | — |
| `spamclassifier/models/entities.py` | the frozen data objects | — |
| `preprocessing/email_parser.py` | raw text → `CleanedMessage` | 2 |
| `preprocessing/tokenizer.py` | text → tokens, and `ngrams` | 2, 3 |
| `features/feature_engineer.py` | tokens → `FeatureVector` | 3 |
| `ml/dataset.py` | load the corpus, split it, check for leakage | 1 |
| `ml/naive_bayes.py` | **the algorithm, from scratch** | 4 |
| `ml/svm_classifier.py` | the calibrated yardstick | 5 |
| `ml/comparator.py` | cross-validation and the honesty rule | 5 |
| `ml/threshold.py` | confusion matrix, threshold choice | 6 |
| `ml/bundle.py` | save, checksum, verify, load | 6 |
| `ml/explainer.py` | weights → a readable sentence | 7 |
| `database/db.py` | connection and schema | 7 |
| `database/repositories.py` | **all** the SQL | 7 |
| `spam_filter.py` | the facade: parse → vectorize → predict → explain | 7 |
| `presenters/app_presenter.py` | all testable logic | 7 |
| `views/` | three passive Tkinter tabs | 7 |
| `train.py` | produce a bundle | 8 |
| `evaluate.py` | the final measurement, once | 8 |
| `run.py` | start the application | 7 |

## 8.2 Which test covers what

| Test file | Covers | Tests |
|---|---|---|
| `test_email_parser.py` | cleaning, and the ordering rule | 16 |
| `test_tokenizer.py` | tokens, stop words, n-grams | 10 |
| `test_feature_engineer.py` | TF-IDF, normalisation, the seven | 16 |
| `test_naive_bayes.py` | the algorithm, incl. the sklearn check | 14 |
| `test_threshold.py` | the confusion matrix and the choice | 8 |
| `test_dataset.py` | splitting and leakage | 6 |
| `test_repositories.py` | the database layer | 13 |
| `test_pipeline.py` | end to end | 8 |

Ninety-one in total.

## 8.3 Reading a failure

```
FAILED tests/test_naive_bayes.py::test_matches_sklearn
  assert 0.7321 == approx(0.6894 ± 1e-09)
```

Three things to read off it: which file (the algorithm), which behaviour (agreement with the reference), and how far off (noticeably, not marginally). A large gap points at the smoothing or the counting; a tiny one points at a rounding or an ordering difference.

```bash
pytest tests/test_naive_bayes.py::test_matches_sklearn -v   # just that one
pytest -x                                                    # stop at the first
pytest -k "laplace" -v                                       # by name
```

## 8.4 The five files that matter most

If you only properly understand five, make them these:

1. **`ml/naive_bayes.py`** — the project. Every line should be one you can explain.
2. **`features/feature_engineer.py`** — where text becomes numbers, and where leakage happens.
3. **`ml/threshold.py`** — short, and the place where the cost argument becomes a number.
4. **`preprocessing/email_parser.py`** — the ordering rule.
5. **`presenters/app_presenter.py`** — the architecture made concrete.

## 8.5 Common mistakes, and where they show up

| Symptom | Look at |
|---|---|
| `caps_ratio` always 0.0 | `email_parser.parse` — lower-casing before measuring |
| `freeoffer` instead of `free offer` | `strip_html` — substituting `""` not `" "` |
| Scores suspiciously high | leakage — is `fit` on the train split only? |
| `predict_proba` returns 0.0 for long messages | left log space too early |
| Disagrees with scikit-learn | smoothing denominator, or `|V|` |
| Vector widths differ | unknown terms being added instead of dropped |
| Verdicts change after retraining an unchanged model | the split is not seeded |
