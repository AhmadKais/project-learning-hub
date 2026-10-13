# Chapter 6 — The architecture: pipeline, bundle, patterns, MVC

💡 **In short:** `train.py` learns and saves one file (model + scaler + feature list + threshold). `run.py` loads it and scans. The screens never touch the model or the database directly — a controller sits between them.


## 6.1 Two pipelines, one extractor

```text
TRAINING (train.py, once)                      SCANNING (run.py, every URL)
CSV ──▶ DatasetLoader ──▶ URLFeatureExtractor  user ──▶ URLFeatureExtractor ──▶ Predictor
    ──▶ ModelTrainer ──▶ ModelEvaluator             ──▶ Explainer ──▶ ScanRepository ──▶ ScanView
    ──▶ ModelBundle.save()  ──────────────▶  models/phishguard_best.joblib  ──▶ ModelBundle.load()
```

The extractor is shared; the bundle file is the hand-over between the two. Nothing else crosses.

## 6.2 The sklearn `Pipeline` — the scaler travels with the model

`Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression())])`. `fit()` fits the scaler
on the training data, transforms, then fits the classifier; `predict_proba()` scales and predicts.
Save the pipeline and you save both. Forget the pipeline and one day someone loads the classifier
without the scaler and every prediction is garbage.

## 6.3 `ModelBundle` — model + features + threshold, verified

The file stores the pipeline, `FEATURE_NAMES` in order, the chosen threshold, the metrics and a
version string. `load()` compares the stored names with the extractor's current `FEATURE_NAMES` and
refuses to run on a mismatch. This is the guard against train/serve skew (chapter 3.4) after you add
a 21st feature and forget to retrain. `test_bundle_refuses_wrong_features` pins it.

## 6.4 Singleton — `Predictor` and `Database`

Loading a joblib file takes ~100 ms and memory; the app must not do it on every click.
`Predictor.__new__` returns the same instance every time. The test suite resets `_instance` between
tests (`conftest.py`) — the known downside of singletons.

## 6.5 Repository — all SQL in one file

`ScanRepository`, `ModelRepository`. The controller says `scans.add(result)` and gets an id; it never
sees `INSERT`. Placeholders `?` always — a URL containing a quote must not break (or inject) the query.

## 6.6 MVC — the desktop app

- **Model**: `Predictor`, `Explainer`, repositories, the entities.
- **View**: `views/` — Tkinter only; receives a `ScanResult` and shows it; calls back plain functions.
- **Controller**: `AppController` — the only class that imports both sides.

📄 **Check it**
```bash
grep -rn "sklearn\|joblib\|sqlite3" phishguard/views/     # must be empty
grep -rn "tkinter" phishguard/ml phishguard/database        # must be empty
```

## 6.7 The database

`scans` (every scan with its features as JSON and optional feedback) and `models` (every training
run with its metrics — your experiments table, persisted). A scan references a model by *version
text*, not a foreign key, so deleting a model file never breaks history — mention that choice.

## 6.8 The full flow — one scan

📄 **From click to screen**
```text
 1. user pastes URL, presses Scan            [View]        ScanView -> on_scan(url)
 2. AppController.on_scan                    [Controller]  validate length
 3.   Predictor.predict(url)                 [Model/ml]
 4.     URLFeatureExtractor.extract          [Model/features]   URLParser inside
 5.     pipeline.predict_proba -> 0.91       [Model/ml]
 6.     threshold 0.40 -> Verdict.PHISHING
 7.   Explainer.explain(result)              [Model/ml]    top-3 contributions
 8.   ScanRepository.add(result)             [Model/database]
 9.   ScanView.show_result(result)           [View]        red meter, sentences
```

## ✅ Check yourself — Chapter 6

1. You add feature #21 to the extractor and run the app without retraining. What happens, exactly where, and why is that good?
2. Someone saves only `pipeline.named_steps["clf"]` to disk and loads it later. What breaks?
3. `Predictor() is Predictor()` → ? And `ScanRepository() is ScanRepository()` → ?
4. A URL contains a single quote: `http://x.com/it's`. What happens in `ScanRepository.add` with
   `?` placeholders? Without them?
5. Why is the scaler fitted only on the training split? What would fitting it on all data leak?
6. List which files change to add a third model (gradient boosting) — and which do not.

## 📚 Further reading — Chapter 6

- **scikit-learn — Model persistence**: https://scikit-learn.org/stable/model_persistence.html
- **scikit-learn — Pipelines and composite estimators**: https://scikit-learn.org/stable/modules/compose.html
- **Refactoring Guru — Singleton, Strategy**: https://refactoring.guru/design-patterns/singleton · https://refactoring.guru/design-patterns/strategy
- **Python docs — sqlite3**: https://docs.python.org/3/library/sqlite3.html
- **Real Python — MVC**: https://realpython.com/lessons/mvc-summary/
- **pytest — Getting Started**: https://docs.pytest.org/en/stable/getting-started.html
