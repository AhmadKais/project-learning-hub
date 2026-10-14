# PhishGuard — the full checklist

Every function you still have to write in your skeleton: **59**, in the order of `TASKS.md`.
Tick each box when its tests are green. The text after each name is the first line of its TODO —
the full instructions are in the docstring in your code. `HINTS.md` (next to this file) helps with the hard ones.

Generated from your skeleton by `tools/make_checklists.py` — do not edit by hand.

## Stage 1 — URL parsing and features (the heart of the project)

**`phishguard/features/extractor.py`**

- [ ] `shannon_entropy(text)` — H = -sum(p_c * log2(p_c)) over the characters of `text`, where p_c = count(c) / len(text). Empty string -> 0.0. Random-looking strings ("x7f9q2") have high entropy; "aaaa" has 0.  
  ✅ checked by `tests/test_extractor.py`
- [ ] `URLFeatureExtractor.extract(url)` — parse, then compute every feature in FEATURE_NAMES into a dict {name: float}. Assert at the end that set(values) == set(FEATURE_NAMES) - a missing feature must fail loudly here, not silently shift the columns.  
  ✅ checked by `tests/test_extractor.py`

**`phishguard/features/url_parser.py`**

- [ ] `URLParser.parse(url)` — 1. strip whitespace; if there is no "://", prepend "http://" so urlparse finds the host (people paste "paypal.com/x" without a scheme; remember that the ORIGINAL had no scheme -> scheme = "") 2. parsed = urlparse(url)...  
  ✅ checked by `tests/test_parser.py`

**`phishguard/models/entities.py`**

- [ ] `FeatureVector.as_list(feature_names)` — one line, but read the warning: return [self.values[name] for name in feature_names]

> **Exit condition:** `pytest tests/test_parser.py tests/test_extractor.py -v` all green. Print the 20 features for 5 URLs of your choice and check them by hand — you must be able to justify every number.

## Stage 2 — Data

**`phishguard/features/extractor.py`**

- [ ] `URLFeatureExtractor.extract_many(urls)` — [self.extract(u).as_list(FEATURE_NAMES) for u in urls] - the matrix X.

**`phishguard/ml/dataset.py`**

- [ ] `DatasetLoader.read()` — df = pd.read_csv(self.path) keep the two columns; drop NaN; lower-case + strip the URL; drop duplicates y = (df[label] == config.POSITIVE_LABEL).astype(int) # 1 = phishing return a DataFrame with columns ["url", "label"]  
  ✅ checked by `tests/test_dataset.py`
- [ ] `DatasetLoader.balance(df)` — sample min(per_class, available) rows from EACH class with random_state=self.seed, concatenate, shuffle (sample(frac=1)). Print how many of each class you ended up with.
- [ ] `DatasetLoader.load()` — df = self.balance(self.read()) X = np.array(self.extractor.extract_many(df["url"].tolist())) # shape (n, 20) y = df["label"].to_numpy() two calls to sklearn.model_selection.train_test_split with stratify=y and random_...  
  ✅ checked by `tests/test_dataset.py`, `tests/test_pipeline.py`
- [ ] `DatasetLoader.feature_table(df)` — (for the book): a DataFrame of all features + label, so you can do df.groupby("label").mean() and SEE which features differ between classes before training anything. Save it as reports/feature_means.csv.

> **Exit condition:** `pytest tests/test_dataset.py -v` green. `feature_table` on 2,000 rows per class saved to `reports/feature_means.csv` — and you can say which 5 features differ most between the classes **before** any model exists.

## Stage 3 — First model

**`phishguard/ml/bundle.py`**

- [ ] `ModelBundle.from_trained(trained, feature_names, report_entry)` — gather everything the scanner will need later: return cls( pipeline=trained.pipeline, model_name=trained.name, feature_names=list(feature_names), # copy - order is a contract threshold=report_entry.get("threshold", co...  
  ✅ checked by `tests/test_pipeline.py`
- [ ] `ModelBundle.save(path)` — two lines: self.version = f"{self.model_name}-{self.trained_at}" joblib.dump(self, path)  
  ✅ checked by `tests/test_pipeline.py`
- [ ] `ModelBundle.load(path)` — bundle = joblib.load(path); then VERIFY bundle.feature_names == extractor.FEATURE_NAMES, raising a clear RuntimeError("model was trained with different features - retrain") otherwise.  
  ✅ checked by `tests/test_pipeline.py`

**`phishguard/ml/trainer.py`**

- [ ] `ModelTrainer.build_logistic()` — Pipeline(scaler + LogisticRegression(max_iter=1000, class_weight="balanced")).
- [ ] `ModelTrainer.train(models)` — /4: build + fit the requested models; return {name: TrainedModel}.  
  ✅ checked by `tests/test_pipeline.py`

**`train.py`**

- [ ] `main()` — (logistic) / stage 4 (both): loader = DatasetLoader(path, per_class=args.per_class) split = loader.load() # DatasetSplit with X/y for train/val/test trainer = ModelTrainer(split) results = trainer.train(models=args.mo...

> **Exit condition:** `python train.py --sample` runs end to end; `python train.py --model logistic` on the real data prints a validation accuracy above 90%; `models/phishguard_best.joblib` exists.

## Stage 4 — Compare, evaluate, choose the threshold

**`phishguard/ml/evaluator.py`**

- [ ] `ModelEvaluator.metrics(pipeline, X, y, threshold)` — probs = pipeline.predict_proba(X)[:, 1] preds = (probs >= threshold).astype(int) from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix return {"accuracy",...  
  ✅ checked by `tests/test_pipeline.py`
- [ ] `ModelEvaluator.choose_threshold(pipeline, target_recall)` — on the VALIDATION split, sweep thresholds 0.05..0.95 and return the HIGHEST threshold whose recall >= target_recall (highest = fewest false alarms while still catching 95%). Fall back to DEFAULT_THRESHOLD if none. Nev...
- [ ] `ModelEvaluator.compare(trained)` — for each model: threshold = choose_threshold(...); metrics on test at that threshold; feature importances (see importances()). Pick the best by F1 (tie -> higher recall). Return (best_name, {name: {...}}).  
  ✅ checked by `tests/test_pipeline.py`
- [ ] `ModelEvaluator.importances(pipeline)` — logistic -> clf.coef_[0] (signed weights on SCALED features); forest -> clf.feature_importances_. Return {feature_name: value}.
- [ ] `ModelEvaluator.worst_mistakes(pipeline, threshold, n)` — (for the book): the n false positives with the highest probability and the n false negatives with the lowest - real URLs the model got wrong, from split.urls_test. Nothing explains a model's limits better.
- [ ] `ModelEvaluator.save_reports(report, directory)` — metrics.json (the whole report), confusion_matrix.png (one per model, 2x2 heat-map with numbers), roc_curve.png (both models on one axis, AUC in the legend), feature_importance.png (horizontal bars, best model).

**`phishguard/ml/trainer.py`**

- [ ] `ModelTrainer.build_forest()` — Pipeline(scaler + RandomForestClassifier(n_estimators=config.RANDOM_FOREST_TREES, n_jobs=-1, random_state=config.RANDOM_SEED, class_weight="balanced")).
- [ ] `ModelTrainer.fit_with_search(name, pipeline, param_grid)` — GridSearchCV(pipeline, param_grid, cv=config.CV_FOLDS, scoring="f1", n_jobs=-1) .fit(X_train, y_train). Time it. Return TrainedModel(name, search.best_estimator_, search.best_params_, search.best_score_, seconds). Gri...

> **Exit condition:** `reports/metrics.json`, `confusion_matrix.png`, `roc_curve.png`, `feature_importance.png` exist; **recall ≥ 0.95 and precision ≥ 0.90** for phishing on the test split; you can explain why the chosen threshold is not 0.5; `worst_mistakes` printed 10 real URLs the model got wrong and you can say why for at least 5.

## Stage 5 — Live prediction and explanation

**`evaluate.py`**

- [ ] `main()` — if args.url or args.file: predictor = Predictor(); explainer = Explainer(predictor.bundle) for each url: result = predictor.predict(url); print verdict, probability, explainer.explain(result) else: rebuild the split (...

**`phishguard/ml/explainer.py`**

- [ ] `Explainer.contributions(result)` — clf = self.bundle.pipeline.named_steps["clf"]; scaler = ...["scaler"] x = [result.features[n] for n in feature_names]; x_scaled = scaler.transform([x])[0] if the clf has coef_: contrib_i = coef_[0][i] * x_scaled[i] el...
- [ ] `Explainer.explain(result, top)` — the `top` strongest contributions toward the VERDICT that was given (positive for phishing, negative for legitimate), sorted by |contribution|. Store them on result.explanations and return them.

**`phishguard/ml/predictor.py`**

- [ ] `Predictor.load()` — if the file is missing -> is_ready False and return (the app must still open and say "train first"). Else self.bundle = ModelBundle.load(path).  
  ✅ checked by `tests/test_pipeline.py`
- [ ] `Predictor.predict(url)` — url = url.strip().lower() # the SAME clean-up as DatasetLoader.read: train == serve features = self.extractor.extract(url) X = [features.as_list(self.bundle.feature_names)] probability = float(self.bundle.pipeline.pre...  
  ✅ checked by `tests/test_pipeline.py`

> **Exit condition:** `pytest tests/test_pipeline.py -v` green. `python evaluate.py --url ...` on 20 URLs you collected yourself (10 real phishing from phishtank.org, 10 legitimate) — note how many are right; each verdict shows 3 explanations that make sense.

## Stage 6 — Database and UI

**`phishguard/controllers/app_controller.py`**

- [ ] `AppController.__init__(root)` — self.predictor = Predictor() self.explainer = Explainer(self.predictor.bundle) if self.predictor.is_ready else None self.scans = ScanRepository(); self.models = ModelRepository() self.view = MainWindow(root, on_scan=s...
- [ ] `AppController.start()` — show the scan screen; if the model is missing show a warning with the train command.
- [ ] `AppController.on_scan(url)` — validate (non-empty, < 2048 chars); result = predictor.predict(url); explainer.explain(result); result.id = scans.add(result); view.scan.show_result(result). Wrap in try/except and show errors in the view - a bad URL...
- [ ] `AppController.on_filter(verdict, search)` — rows = scans.list_recent(config.HISTORY_PAGE_SIZE, verdict, search); view.history.show_rows(rows).
- [ ] `AppController.on_feedback(scan_id, feedback)` — scans.set_feedback(...); refresh the history.
- [ ] `AppController.on_export()` — ReportExporter().export_history(...) -> tell the user the path.
- [ ] `AppController.refresh_stats()` — view.stats.show(counts_by_verdict(), models.list_all()).

**`phishguard/database/db.py`**

- [ ] `Database.get_connection()` — connect, row_factory = sqlite3.Row, PRAGMA foreign_keys = ON.
- [ ] `Database.connection()` — yield conn; commit on success; rollback on exception; always close.
- [ ] `Database.initialize_schema()` — executescript(SCHEMA).

**`phishguard/database/repositories.py`**

- [ ] `ScanRepository.add(result)` — INSERT (features as json.dumps, verdict.value, isoformat time); return id.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `ScanRepository.get(scan_id)` — SELECT one; map with _row_to_result (write it once).  
  ✅ checked by `tests/test_repositories.py`
- [ ] `ScanRepository.list_recent(limit, verdict, search)` — newest first; optional WHERE verdict=? and/or url LIKE ? (search wrapped in %...%). Build the WHERE clause from a list of conditions.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `ScanRepository.set_feedback(scan_id, feedback)` — UPDATE scans SET feedback=? WHERE id=? ("correct" / "wrong").  
  ✅ checked by `tests/test_repositories.py`
- [ ] `ScanRepository.counts_by_verdict()` — SELECT verdict, COUNT(*) ... GROUP BY verdict -> {Verdict: n}.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `ModelRepository.register(version, model_name, trained_at, train_rows, metrics, threshold, notes)` — INSERT OR REPLACE by version; return id.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `ModelRepository.list_all()` — every registered model, newest first - the experiments table.  
  ✅ checked by `tests/test_repositories.py`

**`phishguard/models/entities.py`**

- [ ] `ScanResult.risk_level` — turn the probability into a word the user understands: if self.probability < config.RISK_LOW: return "low" if self.probability < config.RISK_HIGH: return "medium" return "high"

**`phishguard/utils/exporter.py`**

- [ ] `ReportExporter.export_history(directory)` — exports/history_<timestamp>.csv with columns scanned_at, url, probability, verdict, threshold, model_version, feedback. encoding="utf-8-sig" so Excel opens it correctly. Return the path.

**`phishguard/views/history_view.py`**

- [ ] `HistoryView.__init__(parent, on_filter, on_feedback, on_export)` — filter row (Combobox all/legitimate/phishing + search Entry + Apply), a Treeview (time, url, probability, verdict, feedback), buttons "Mark correct", "Mark wrong", "Export CSV". Store the scan id in the Treeview item'...
- [ ] `HistoryView.show_rows(rows)`
- [ ] `HistoryView.selected_id()` — the scan id of the selected row, or None.

**`phishguard/views/main_window.py`**

- [ ] `MainWindow.__init__(root, on_scan, on_filter, on_feedback, on_export)` — Notebook; self.scan = ScanView(...); self.history = HistoryView(...); self.stats = StatsView(...); add the three tabs.
- [ ] `MainWindow.show_error(text)` — messagebox.showerror.
- [ ] `MainWindow.show_info(text)` — messagebox.showinfo.

**`phishguard/views/scan_view.py`**

- [ ] `ScanView.__init__(parent, on_scan)` — an Entry (bind <Return>), a "Scan" button, a verdict label (large font), a ttk.Progressbar used as a risk meter (0-100), a label for "probability 87% - threshold 40%", and a Listbox/Text for explanations.
- [ ] `ScanView.show_result(result)` — verdict text + colour by result.risk_level (green/orange/red), meter = probability*100, explanations one per line with an arrow ("-> pushes toward phishing" / "<- pushes toward legitimate").
- [ ] `ScanView.clear()`

**`phishguard/views/stats_view.py`**

- [ ] `StatsView.__init__(parent)` — a matplotlib Figure (bar chart legitimate vs phishing) embedded with FigureCanvasTkAgg, and a Treeview of registered models (version, name, trained_at, precision, recall, f1, auc, threshold).
- [ ] `StatsView.show(counts, models)`

> **Exit condition:** `pytest -v` all green. `python run.py`: scan a URL → verdict, meter, explanations; History tab lists it, feedback buttons work, CSV export opens in Excel; Statistics tab shows the chart and the model table.

## Stage 7 — Experiments, drift test, documentation

**`phishguard/database/repositories.py`**

- [ ] `ScanRepository.wrong_feedback()` — (optional): scans marked "wrong" - candidates for retraining.

> **Exit condition:** a complete project book where every number comes from `reports/`, `pytest`, or a run.
