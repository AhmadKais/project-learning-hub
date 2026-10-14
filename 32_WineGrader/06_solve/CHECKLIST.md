# WineGrader — the full checklist

Every function you still have to write in your skeleton: **107**, in the order of `TASKS.md`.
Tick each box when its tests are green. The text after each name is the first line of its TODO —
the full instructions are in the docstring in your code. `HINTS.md` (next to this file) helps with the hard ones.

Generated from your skeleton by `tools/make_checklists.py` — do not edit by hand.

## Stage 1 — Loading the data (2 weeks)

**`winegrader/data/loader.py`**

- [ ] `quality_to_grade(quality)` — map the 0..10 tasting score to one of the three grades.  
  ✅ checked by `tests/test_loader.py`
- [ ] `grades_from_quality(quality)` — quality_to_grade applied to every value, as an int array.  
  ✅ checked by `tests/test_loader.py`
- [ ] `validate_values(values)` — None if the wine is acceptable, else a reason in words.  
  ✅ checked by `tests/test_loader.py`
- [ ] `parse_uci_csv(path, is_red)` — read one UCI file into a LoadResult.  
  ✅ checked by `tests/test_loader.py`
- [ ] `load_wine_quality(red_path, white_path)` — both files, merged. Returns (X, quality).  
  ✅ checked by `tests/test_loader.py`
- [ ] `duplicate_of(X, quality)` — for each row, the index of the FIRST identical row, or None.  
  ✅ checked by `tests/test_loader.py`
- [ ] `drop_exact_duplicates(X, quality)` — keep only rows whose duplicate_of is None.  
  ✅ checked by `tests/test_loader.py`
- [ ] `class_balance(y)` — the share of each grade, by name.  
  ✅ checked by `tests/test_loader.py`

> **Exit condition:** `pytest tests/test_loader.py -v` green, including `test_real_data_has_1177_duplicates`. Say out loud why a duplicate is worse for k-NN than for almost any other model.

## Stage 2 — Looking at the data (2 weeks)

**`analyse.py`**

- [ ] `main(argv)` — load, de-duplicate, describe, correlate, plot, write.

**`winegrader/data/analysis.py`**

- [ ] `describe(X)` — one row per feature - name, mean, std, min, max.  
  ✅ checked by `tests/test_analysis.py`
- [ ] `correlation_with(X, target)` — Pearson correlation of every feature with `target`.  
  ✅ checked by `tests/test_analysis.py`
- [ ] `means_by_group(X, groups)` — {group: [mean of each feature]} - e.g. by grade, or red against white.  
  ✅ checked by `tests/test_analysis.py`
- [ ] `plot_histograms(X, path)` — a 3x4 grid of histograms, one per feature, saved as PNG.  
  ✅ checked by `tests/test_analysis.py`

> **Exit condition:** `pytest tests/test_analysis.py -v` green; `reports/analysis.md` exists. Compare the largest and smallest feature ranges — that ratio is the reason for stage 3.

## Stage 3 — Scaling, distance, linear search (2 weeks)

**`winegrader/ml/index.py`**

- [ ] `LinearIndex.build(X)` — just keep X (as a float array). Reset the counters.  
  ✅ checked by `tests/test_index.py`
- [ ] `LinearIndex.query(v, k)` — power_to_many, then the k smallest, ties by index.  
  ✅ checked by `tests/test_index.py`
- [ ] `LinearIndex.query_batch(Q, k, chunk)` — the vectorised version, chunk rows of Q at a time.  
  ✅ checked by `tests/test_index.py`

**`winegrader/ml/metrics.py`**

- [ ] `minkowski_power(a, b, w, p)` — SUM_i w[i] * |a[i] - b[i]| ** p - no root.  
  ✅ checked by `tests/test_scaler_metrics.py`
- [ ] `minkowski(a, b, w, p)` — minkowski_power(...) ** (1/p) - the real distance.  
  ✅ checked by `tests/test_scaler_metrics.py`
- [ ] `power_to_many(X, v, w, p)` — the power distance from v to EVERY row of X, shape (N,).  
  ✅ checked by `tests/test_scaler_metrics.py`
- [ ] `power_matrix(Q, X, w, p)` — power distances from every row of Q to every row of X, (m, N).  
  ✅ checked by `tests/test_scaler_metrics.py`, `tests/test_tuning_weights.py`

**`winegrader/ml/scaler.py`**

- [ ] `StandardScaler.fit(X)` — column means and (population) standard deviations.  
  ✅ checked by `tests/test_evaluation_bundle.py`, `tests/test_scaler_metrics.py`
- [ ] `StandardScaler.transform(X)` — (X - mean) / std. Not fitted yet -> RuntimeError("scaler is not fitted").  
  ✅ checked by `tests/test_evaluation_bundle.py`, `tests/test_scaler_metrics.py`
- [ ] `StandardScaler.inverse_transform(Z)` — back to lab units: Z * std + mean. Used to show neighbours.  
  ✅ checked by `tests/test_scaler_metrics.py`
- [ ] `MinMaxScaler.fit(X)` — column minimum and range (max - min); a zero range becomes 1.  
  ✅ checked by `tests/test_evaluation_bundle.py`, `tests/test_scaler_metrics.py`
- [ ] `MinMaxScaler.transform(X)` — (X - min) / range. Test rows may fall outside 0..1 - that is fine.  
  ✅ checked by `tests/test_evaluation_bundle.py`, `tests/test_scaler_metrics.py`
- [ ] `MinMaxScaler.inverse_transform(Z)` — Z * range + min.  
  ✅ checked by `tests/test_scaler_metrics.py`
- [ ] `scaler_from_dict(data)` — rebuild a fitted scaler from to_dict output.  
  ✅ checked by `tests/test_scaler_metrics.py`

> **Exit condition:** `pytest tests/test_scaler_metrics.py -v` green and the `LinearIndex` tests in `tests/test_index.py` green (`pytest tests/test_index.py -k "not kdtree" -v`). `test_zscore_matches_sklearn` and `test_fit_uses_only_given_rows` are the two that matter.

## Stage 4 — k-NN, baselines, measuring (3 weeks) — the heart of the project

**`winegrader/ml/classifiers.py`**

- [ ] `class_priors(y, n_classes)` — share of each class in y, shape (n_classes,).  
  ✅ checked by `tests/test_classifiers.py`
- [ ] `vote(dist_power, labels, p, alpha, priors, weighted)` — the vote for MANY queries at once.  
  ✅ checked by `tests/test_classifiers.py`
- [ ] `KNNClassifier.fit(X, y)` — this is ALL the training k-NN does.  
  ✅ checked by `tests/test_classifiers.py`, `tests/test_evaluation_bundle.py`
- [ ] `KNNClassifier.predict_one(v)` — one wine -> Prediction with its neighbours.  
  ✅ checked by `tests/test_classifiers.py`
- [ ] `KNNClassifier.predict(X)` — many wines at once - index.query_batch, then vote().  
  ✅ checked by `tests/test_classifiers.py`, `tests/test_evaluation_bundle.py`
- [ ] `MajorityClassifier.fit(X, y)` — remember the most frequent grade (np.bincount, argmax).  
  ✅ checked by `tests/test_classifiers.py`, `tests/test_evaluation_bundle.py`
- [ ] `MajorityClassifier.predict_one(v)` — always self.label, confidence 1.0, no neighbours.  
  ✅ checked by `tests/test_classifiers.py`
- [ ] `CentroidClassifier.fit(X, y)` — centroids[c] = mean of the rows of grade c, shape (n_classes, d).  
  ✅ checked by `tests/test_classifiers.py`, `tests/test_evaluation_bundle.py`
- [ ] `CentroidClassifier.predict_one(v)` — the grade whose centroid is nearest (Euclidean).  
  ✅ checked by `tests/test_classifiers.py`

**`winegrader/ml/evaluation.py`**

- [ ] `evaluate_split(factory, X, y, train, test, scaling, time_single)` — fit on train, score on test, return a FoldResult.  
  ✅ checked by `tests/test_evaluation_bundle.py`
- [ ] `cross_validate(factory, X, y, splits, scaling)` — evaluate_split on every fold. Default splits: stratified, OUTER_FOLDS.  
  ✅ checked by `tests/test_evaluation_bundle.py`
- [ ] `summarise(results)` — mean and std of every score across the folds.  
  ✅ checked by `tests/test_evaluation_bundle.py`

**`winegrader/ml/folds.py`**

- [ ] `stratified_kfold(y, folds, seed)` — `folds` (train, test) pairs; every row is in exactly one test set.  
  ✅ checked by `tests/test_classifiers.py`, `tests/test_evaluation_bundle.py`, `tests/test_tuning_weights.py`

**`winegrader/ml/scoring.py`**

- [ ] `confusion_matrix(y_true, y_pred, n_classes)` — cm[true][pred] = how many wines of grade `true` were called `pred`.  
  ✅ checked by `tests/test_classifiers.py`
- [ ] `precision_recall_f1(cm)` — per-class precision, recall and F1 from a confusion matrix.  
  ✅ checked by `tests/test_classifiers.py`
- [ ] `macro_f1(y_true, y_pred)` — the plain mean of the per-class F1 values.  
  ✅ checked by `tests/test_classifiers.py`
- [ ] `accuracy(y_true, y_pred)` — share of exact matches. 0.0 for empty input.  
  ✅ checked by `tests/test_classifiers.py`

> **Exit condition:** `pytest tests/test_classifiers.py -v` and `pytest tests/test_evaluation_bundle.py -k "evaluate or baseline or cross or summarise" -v` green — especially `test_knn_matches_sklearn` (identical answers) and `test_alpha_one_rescues_the_rare_class`. Cross-validate k-NN with k=15 on the real data with and without scaling (`scaling="none"`), and write both numbers down: that is the first result of the project book.

## Stage 5 — The kd-tree (2 weeks)

**`winegrader/ml/index.py`**

- [ ] `KDTreeIndex.build(X)` — keep X, reset the counters, root = _build(all row numbers).  
  ✅ checked by `tests/test_index.py`
- [ ] `KDTreeIndex._build(rows)` — recursively split `rows` (an array of row numbers).
- [ ] `KDTreeIndex.query(v, k)` — depth-first search with pruning.  
  ✅ checked by `tests/test_index.py`

> **Exit condition:** `pytest tests/test_index.py -v` all green — `test_kdtree_matches_linear` is the blocking test (1,000 queries, identical neighbours, with weights and without). Draw the tree for 8 points in 2 dimensions on paper and run one query by hand, marking every branch you prune.

## Stage 6 — Tuning, callbacks, weight learning, nested evaluation (3 weeks)

**`winegrader/ml/callbacks.py`**

- [ ] `EarlyStopping.update(score)` — record a score; return True when it is time to stop.  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `HistoryLogger.on_round_end(round_no, score, weights)` — append {"round": .., "score": .., "weights": list(weights)}.  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `Checkpoint.on_round_end(round_no, score, weights)` — if score beats self.best (or there is no best yet), save.  
  ✅ checked by `tests/test_tuning_weights.py`

**`winegrader/ml/evaluation.py`**

- [ ] `nested_cv(X, y, outer_splits, learn, index, grid, weight_kwargs, callbacks, progress)` — the honest estimate.  
  ✅ checked by `tests/test_evaluation_bundle.py`

**`winegrader/ml/tuning.py`**

- [ ] `prepare_folds(X, y, splits, scaling)` — scale every fold - fitting the scaler on that fold's TRAIN rows only.  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `fold_neighbours(fold, weights, p, k)` — (power distances, LABELS) of the k nearest training wines for every test wine of one fold. Both (m, k).  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `score_votes(fold, dist_power, labels, k, p, alpha)` — (macro-F1, recall of HIGH) when voting with the first k neighbours.
- [ ] `choose_configuration(rows, tolerance)` — the selection rule (see grid_search) on a list of result rows.  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `grid_search(X, y, splits, weights, scalings, ps, alphas, ks, patience)` — try every scaling x p x alpha x k; return the best by mean macro-F1.  
  ✅ checked by `tests/test_tuning_weights.py`

**`winegrader/ml/weights.py`**

- [ ] `cv_score(folds, weights, params)` — mean macro-F1 over the prepared folds with these weights.  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `neighbours_from_matrix(D, k)` — the k smallest of every row of a distance matrix.  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `FoldDistances.__init__(fold, weights, p)` — keep the fold and p; D = power_matrix(Xte, Xtr, weights, p).  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `FoldDistances.term(i)` — |Xte[:, i, None] - Xtr[None, :, i]| ** p, shape (m, N). Weight NOT applied.  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `FoldDistances.score(D, params)` — macro-F1 of this fold when the distances are D.  
  ✅ checked by `tests/test_tuning_weights.py`
- [ ] `learn_weights(X, y, params, splits, factors, max_rounds, tolerance, callbacks)` — coordinate search over the feature weights.  
  ✅ checked by `tests/test_tuning_weights.py`

> **Exit condition:** `pytest tests/test_tuning_weights.py -v` and `pytest tests/test_evaluation_bundle.py -k nested -v` green. The two that matter: `test_incremental_matches_full_recompute` (the fast update gives exactly the slow answer) and `test_nested_never_sees_outer_test` (the honest estimate is honest). Time `learn_weights` with `cv_score` in the loop and with `FoldDistances`, and write both times down.

## Stage 7 — The two machines (3 weeks)

**`run.py`**

- [ ] `main(argv)` — wire everything together and open the window.

**`train.py`**

- [ ] `main(argv)` — the training pipeline, printing every step.

**`winegrader/controllers/app_controller.py`**

- [ ] `AppController.parse_form(fields)` — the form's strings -> 12 floats in config.FEATURES order.  
  ✅ checked by `tests/test_app.py`
- [ ] `AppController.classify(fields)` — parse, grade, record, and format for the view.  
  ✅ checked by `tests/test_app.py`
- [ ] `AppController.format(values, prediction)` — build the dict that classify() returns (see its docstring).
- [ ] `AppController.add_manual_wine(fields, quality)` — store a wine typed at the lab, NOT approved.  
  ✅ checked by `tests/test_app.py`
- [ ] `AppController.weights()` — [(feature, weight), ...] sorted by weight, largest first.  
  ✅ checked by `tests/test_app.py`
- [ ] `AppController.model_info()` — version, params, training size and stored scores, for the Model tab.  
  ✅ checked by `tests/test_app.py`
- [ ] `AppController.history(limit)` — recent gradings as dicts for the history table.  
  ✅ checked by `tests/test_app.py`

**`winegrader/database/db.py`**

- [ ] `connect(path)` — open the database with foreign keys ON.
- [ ] `initialise(conn)` — conn.executescript(SCHEMA); commit. Safe to call every start.

**`winegrader/database/repositories.py`**

- [ ] `WineRepository.add(values, quality, source, approved, dup_of, commit)` — insert one wine (12 values in config.FEATURES order); return its id.  
  ✅ checked by `tests/test_app.py`
- [ ] `WineRepository.import_arrays(X, quality, source)` — insert every wine, marking duplicates. Returns (inserted, duplicates).  
  ✅ checked by `tests/test_app.py`
- [ ] `WineRepository.training_set()` — (ids, X, quality) of every approved, non-duplicate wine, by id.  
  ✅ checked by `tests/test_app.py`
- [ ] `WineRepository.balance()` — counts by grade and colour, for the data screen.  
  ✅ checked by `tests/test_app.py`
- [ ] `EvaluationRepository.add(run, classifier, params, index_type, outer_fold, result)` — one evaluations row + its non-zero confusion cells; return the id.  
  ✅ checked by `tests/test_app.py`
- [ ] `EvaluationRepository.add_weights(eval_id, weights, round_no)` — one learned_weights row per feature.  
  ✅ checked by `tests/test_app.py`
- [ ] `EvaluationRepository.summary(run)` — per configuration of a run - mean macro-F1, mean recall_high, fold count.  
  ✅ checked by `tests/test_app.py`
- [ ] `EvaluationRepository.weight_stability(run)` — per feature - mean, min and max learned weight across the run's folds.  
  ✅ checked by `tests/test_app.py`
- [ ] `GradingRepository.add(values, prediction, model_version)` — store the 12 input values as JSON with the answer; return the id.  
  ✅ checked by `tests/test_app.py`
- [ ] `GradingRepository.recent(limit)` — the newest `limit` gradings, newest first.

**`winegrader/ml/bundle.py`**

- [ ] `compute_checksum(folder)` — one SHA-256 over FILES, in that order.
- [ ] `save(folder, X_scaled, y, scaler, params, weights, scores, version)` — write the four files; return the version string.  
  ✅ checked by `tests/test_evaluation_bundle.py`
- [ ] `load(folder, expected_features)` — read, VERIFY, rebuild. Every failure is a BundleError in plain words.  
  ✅ checked by `tests/test_evaluation_bundle.py`
- [ ] `latest(models_dir)` — the newest bundle folder in models_dir.  
  ✅ checked by `tests/test_evaluation_bundle.py`

**`winegrader/service.py`**

- [ ] `GradingService.from_bundle(folder, index)` — load a bundle (default: bundle.latest()) and wrap it.  
  ✅ checked by `tests/test_app.py`
- [ ] `GradingService.grade(values)` — twelve raw lab values -> Prediction.  
  ✅ checked by `tests/test_app.py`
- [ ] `GradingService.neighbour_values(neighbour)` — the neighbour's 12 values in LAB units (not scaled) - for display.  
  ✅ checked by `tests/test_app.py`
- [ ] `GradingService.feature_gaps(values, neighbour)` — how much each feature adds to the distance to this neighbour.  
  ✅ checked by `tests/test_app.py`

**`winegrader/views/classify_view.py`**

- [ ] `ClassifyView.build()` — lay out the widgets.
- [ ] `ClassifyView.on_example()` — fill the form with EXAMPLE.
- [ ] `ClassifyView.on_clear()` — empty every entry and reset the result area.
- [ ] `ClassifyView.on_grade()` — collect the strings, call controller.classify, display.
- [ ] `ClassifyView.display(result)` — banner text + colour, confidence, sentence, neighbour rows.

**`winegrader/views/main_window.py`**

- [ ] `MainWindow.build()` — title, size, a ttk.Notebook with the four tabs.

**`winegrader/views/model_views.py`**

- [ ] `WeightsView.build()` — a horizontal matplotlib bar chart inside the tab.
- [ ] `ModelView.build()` — show controller.model_info() as label rows.
- [ ] `HistoryView.build()` — a Treeview (when | grade | confidence | model) and a Refresh button.
- [ ] `HistoryView.refresh()` — reload the rows from controller.history().

> **Exit condition:** `pytest -v` green except stage 8's functions. `python train.py` writes a bundle; `python run.py` grades the example wine. Copy the bundle to a second computer and grade a wine there. Change one number in `model.json` by hand and confirm the station refuses to load it.

## Stage 8 — Measure and write (2 weeks)

**`evaluate.py`**

- [ ] `main(argv)` — the comparison table, measured honestly.
- [ ] `write_report(summaries, nested, index_rows, curve, by_colour, stability, balance, n)` — the markdown report described in main().

**`winegrader/database/repositories.py`**

- [ ] `EvaluationRepository.add_predictions(eval_id, wine_ids, predicted)` — one predictions row per test wine - the raw material for error analysis.
- [ ] `EvaluationRepository.accuracy_by_colour(run)` — {"red": (n, accuracy), "white": (n, accuracy)} over a run's predictions.
- [ ] `EvaluationRepository.save_folds(wine_ids, splits, seed)` — record which outer fold each wine was tested in, so a run can be reproduced.

**`winegrader/ml/evaluation.py`**

- [ ] `kdtree_dimension_curve(X, y, train, test, k, dims, queries)` — how much the kd-tree saves as the number of features grows.

> **Exit condition:** `pytest -v` fully green; `reports/evaluation.md` exists. A target you missed is written as missed and discussed — targets are never edited afterwards to match the result.
