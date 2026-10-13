# Chapter 9 — Map of the code

💡 **In short:** where everything is, and what to read before writing each file.

## 9.1 Files you do not write

| File | What it is |
|---|---|
| `config.py` | every number and path. Read it first — `FEATURES`, `GRADES`, the grid, the tolerances |
| `winegrader/entities.py` | the dataclasses passed between layers |
| `winegrader/errors.py` | `WineGraderError`, `DataError`, `BundleError` |
| `download_data.py` | fetches the two CSV files |
| `tests/` | the specification |

## 9.2 Files you write, in order

| Stage | File | Functions |
|---|---|---|
| 1 | `data/loader.py` | `quality_to_grade`, `grades_from_quality`, `validate_values`, `parse_uci_csv`, `load_wine_quality`, `duplicate_of`, `drop_exact_duplicates`, `class_balance` |
| 2 | `data/analysis.py`, `analyse.py` | `describe`, `correlation_with`, `means_by_group`, `plot_histograms`, `main` |
| 3 | `ml/scaler.py` | `StandardScaler`, `MinMaxScaler`, `scaler_from_dict` |
| 3 | `ml/metrics.py` | `minkowski_power`, `minkowski`, `power_to_many`, `power_matrix` |
| 3 | `ml/index.py` | `LinearIndex.build`, `query`, `query_batch` |
| 4 | `ml/classifiers.py` | `class_priors`, `vote`, `KNNClassifier`, `MajorityClassifier`, `CentroidClassifier` |
| 4 | `ml/scoring.py`, `ml/folds.py` | the metrics; `stratified_kfold` |
| 4 | `ml/evaluation.py` | `evaluate_split`, `cross_validate`, `summarise` |
| 5 | `ml/index.py` | `KDTreeIndex.build`, `_build`, `query` |
| 6 | `ml/callbacks.py` | `EarlyStopping.update`, `HistoryLogger`, `Checkpoint` |
| 6 | `ml/tuning.py` | `prepare_folds`, `fold_neighbours`, `score_votes`, `choose_configuration`, `grid_search` |
| 6 | `ml/weights.py` | `cv_score`, `neighbours_from_matrix`, `FoldDistances`, `learn_weights` |
| 6 | `ml/evaluation.py` | `nested_cv` |
| 7 | `ml/bundle.py` | `compute_checksum`, `save`, `load`, `latest` |
| 7 | `database/db.py`, `repositories.py` | `connect`, `initialise`, the repositories |
| 7 | `service.py`, `controllers/app_controller.py` | grading and formatting |
| 7 | `views/*.py`, `run.py`, `train.py` | the window and the two machines |
| 8 | `repositories.py`, `evaluation.py`, `evaluate.py` | `add_predictions`, `accuracy_by_colour`, `save_folds`, `kdtree_dimension_curve`, `main`, `write_report` |

## 9.3 How one wine travels through the code

```
ClassifyView.on_grade          strings from 12 entry boxes
 └ AppController.classify
    ├ parse_form               -> 12 floats ("9,5" accepted)
    ├ GradingService.grade
    │  ├ validate_values       -> DataError if impossible
    │  ├ scaler.transform      -> the TRAINING scaler from the bundle
    │  └ KNNClassifier.predict_one
    │     ├ index.query(v, k)  -> k (power distance, row) pairs
    │     └ vote(...)          -> grade, confidence
    ├ GradingRepository.add    -> one row in gradings
    └ format                   -> dict: grade, colour, sentence, 5 neighbours
```

## 9.4 How training travels

```
train.py
 ├ WineRepository.import_arrays    first run only; marks the 1,177 duplicates
 ├ WineRepository.training_set     5,320 wines, is_red last
 ├ grid_search                      ~5 s -> Params(k, p, alpha, scaling)
 ├ learn_weights                    ~20 s -> 12 weights, with Checkpoint + HistoryLogger
 ├ create_scaler(...).fit(X)        ALL training wines now - this is the final model
 └ bundle.save                      models/wg-<date>-<time>/
```
