# Chapter 8 — Architecture, the two machines, security

💡 **In short:** four layers, and only the views know about Tkinter. Machine A trains and writes a bundle of four JSON files with a checksum; machine B refuses any bundle that was modified or lists the features in a different order. All SQL uses placeholders.

## 8.1 The layers (MVC)

| Layer | Folder | Knows about |
|---|---|---|
| View | `winegrader/views/` | Tkinter, the controller |
| Controller | `winegrader/controllers/` | the service, the repositories |
| Model — learning | `winegrader/ml/`, `data/`, `service.py` | numpy only |
| Model — storage | `winegrader/database/` | sqlite3 |

The rule: **nothing outside `views/` imports tkinter.** `test_no_tkinter_outside_views` enforces it by reading the source files. The reward: the whole lab-station flow — parse the form, grade, record, format — is tested in `test_app.py` without opening a window, and `train.py` / `evaluate.py` run without a screen.

The views are thin: they collect strings from the entry boxes and display dicts. Deciding colours, wording and parsing numbers happens in the controller, where it can be tested.

## 8.2 Design patterns, and why each is there

| Pattern | Where | Why |
|---|---|---|
| Strategy | `Classifier`, `NeighbourIndex`, `Scaler` | swap the algorithm without touching the code that uses it — the evaluation runs every model through one function |
| Template Method | `Classifier.predict` calls `predict_one` | subclasses fill in one step |
| Factory | `create_classifier`, `create_index`, `create_scaler` | a name from the config becomes an object |
| Observer | callbacks | the learning loop announces rounds; listeners decide what to do |
| Facade | `GradingService` | the controller calls `grade()`; scaling, search and voting are hidden |
| Repository | `database/repositories.py` | all SQL in one file |
| Value Object | `Prediction`, `Neighbour`, `FoldResult` | frozen results that travel between layers |

## 8.3 Two machines

The ministry requires deployment on two machines with a logical relationship between them. Here it is a producer and a consumer:

- **Machine A — training station.** `train.py` imports the data, tunes, learns the weights, fits the final scaler on all training rows and writes a bundle.
- **Machine B — lab station.** `run.py` loads a bundle and grades wines. It never trains.

The bundle is the contract between them:

| File | Contents |
|---|---|
| `train.json` | the scaled training wines and their grades |
| `scaler.json` | the mean and std (or min and range) of every feature |
| `model.json` | k, p, alpha, scaling, the weights — **and the feature names in order** |
| `meta.json` | version, date, scores, and the SHA-256 of the three files above |

## 8.4 The three checks on load

1. **All four files present** — else "incomplete bundle".
2. **The checksum matches** — else "the model files were modified". Computed before reading any content, so a modified file is refused whatever it contains.
3. **The feature names match `config.FEATURES`, name by name** — else "feature order mismatch".

❓ **Why is the feature order checked by name? The arrays have the right length anyway.**

That is exactly the danger. The weights are a list of 12 numbers. If machine B's code lists the features in a different order, the weight learned for alcohol is applied to pH, every array still has 12 entries, nothing crashes — and every answer is quietly wrong. A length check cannot see it; only comparing the names can.

## 8.5 Why JSON and never pickle

`pickle.load` runs whatever code the file tells it to. A bundle is a file that travels between machines; anyone who can replace it could run any program on the lab station. JSON can only ever be data. `test_no_pickle_anywhere` checks that pickle is never imported.

## 8.6 The database

Seven tables: `wines`, `folds`, `evaluations`, `learned_weights`, `confusion`, `predictions`, `gradings`. Points worth knowing for the defence:

- `PRAGMA foreign_keys = ON` on every connection. SQLite ignores `REFERENCES` and `ON DELETE CASCADE` without it — silently.
- `CHECK` constraints are a second line of defence: `grade IN ('low','medium','high')`, `confidence BETWEEN 0 AND 1`. The code validates first; the database refuses whatever slips past.
- Duplicates are kept in `wines` with `dup_of` pointing to the first copy, so the count of 1,177 can be shown — and are excluded from every training set.
- The import inserts 6,497 rows in **one transaction**. Committing after every row forces a disk write each time: the first version of this project took nine minutes to import; one commit at the end takes under a second.

## 8.7 Security

| Threat | Defence |
|---|---|
| a damaged or hostile CSV | header check, every value validated, bad lines rejected with their line number, file size limit |
| SQL injection through a run name or file content | every value through a `?` placeholder — `test_quotes_in_values_are_data_not_sql` |
| a modified bundle | SHA-256 checked before loading |
| code execution through the bundle | JSON only, pickle banned |
| data poisoning — a wrong grade typed at the lab station | manual wines are stored **unapproved** and never enter training until approved |
| leakage making the model look better than it is | the four guards of chapter 7 |

❓ **What is data poisoning, and why does it matter more for k-NN than for most models?**

Adding wrongly-labelled examples to the training data so the model learns the wrong thing. In k-NN every stored wine votes directly: one wine typed in with a false "high" grade becomes a neighbour of every similar wine and pushes them towards high. That is why manual wines wait for approval.
