# Part B — Build the code, step by step

How to use this part: **do not read ahead.** Do one step, run the command it gives, look at the
result, then do the next step. Every step is small. If a step says "you should see X" and you see
something else — stop and fix it before continuing. Chapter 16a has the common errors.

Every stage has the same rhythm:

1. **Goal** — what the stage gives you, in one sentence.
2. **Files** — which files you open.
3. **Steps** — numbered. Each one is a few lines of code or one command.
4. **Check** — the command to run and what you should see.
5. **Commit** — save your progress in Git.

# Chapter 10 — Stage 0: get comfortable (30 minutes)

**Goal:** see the project run, see a test fail, understand what "not implemented" looks like.

**Step 0.1** — Open the terminal in VS Code (Ctrl+`). Make sure you see `(.venv)` at the start of
the line. If not: `.venv\Scripts\activate`.

**Step 0.2** — Run all the tests:
```
pytest -v
```
You should see a long list, every line ending in **FAILED** or **ERROR**, and the last line saying
something like `25 failed`. That is correct: nothing is written yet.

**Step 0.3** — Run one test file and read the error:
```
pytest tests/test_parser.py -v
```
Scroll up to the first failure. Find the line `NotImplementedError`. Above it you will see
`File ".../url_parser.py", line NN, in parse`. That is the function you will write first.

**Step 0.4** — Open `phishguard/features/url_parser.py`. Read the text at the top of the file (the
module docstring) and the text inside `parse` (the function docstring). The numbered list inside is
your to-do list for the function. **The last line of the function is `raise NotImplementedError` —
that is the line you will replace with your code.**

**Step 0.5** — Open `config.py`. Read it top to bottom once. You will not change it, but you will
use names from it (`config.SUSPICIOUS_WORDS`, `config.COMMON_TLDS`…).

You are ready.

# Chapter 11 — Stage 1: the URL parser and the features

**Goal:** turn any URL string into 20 numbers.
**Files:** `phishguard/features/url_parser.py`, `phishguard/features/extractor.py`, `phishguard/models/entities.py`.
**Guide chapters to have open:** 3 (features), 1a (Python).

## 11.1 `URLParser.parse` — the URL into pieces

**What it must do:** given `"http://paypal.com.secure-login.xyz/verify"` return a `ParsedURL` with
`scheme="http"`, `host="paypal.com.secure-login.xyz"`, `subdomains=["paypal","com"]`,
`domain="secure-login"`, `tld="xyz"`, `path="/verify"`, `query=""`, `port=None`, `has_ip_host=False`.

**Step 1.1** — At the top of the function, delete `raise NotImplementedError`. Type this — it
handles the scheme and gets the host:
```python
raw = url.strip()
had_scheme = "://" in raw
parsed = urlparse(raw if had_scheme else "http://" + raw)
host = (parsed.hostname or "").lower()
scheme = parsed.scheme if had_scheme else ""
```
*Why the `"http://" +`:* `urlparse("paypal.com/x")` does not find a host without a scheme. We add
one just for parsing and remember it was not there (`scheme = ""`).

**Step 1.2** — The port can raise an error on garbage, so:
```python
try:
    port = parsed.port
except ValueError:
    port = None
```

**Step 1.3** — Is the host an IP address?
```python
has_ip = bool(IP_PATTERN.match(host))
```

**Step 1.4** — Split the host into labels and decide TLD / domain / subdomains. Write it yourself
following this recipe:
- `labels = host.split(".") if host else []`
- if `has_ip`: `subdomains = []`, `domain = host`, `tld = ""`
- else if the last two labels joined with "." (for example `"co.il"`) are in `config.COMMON_TLDS`:
  `tld` = those two joined, `domain` = the label before them, `subdomains` = all labels before that
- else if there are at least 2 labels: `tld` = last label, `domain` = the one before, `subdomains` = the rest
- else (one label or none): `tld = ""`, `domain = host`, `subdomains = []`

Hint for "all labels before that": list slicing — `labels[:-2]` is everything except the last two.

**Step 1.5** — Return the object:
```python
return ParsedURL(raw=raw, scheme=scheme, host=host, subdomains=subdomains, domain=domain,
                 tld=tld, port=port, path=parsed.path, query=parsed.query, has_ip_host=has_ip)
```

**Check:**
```
pytest tests/test_parser.py -v
```
You should see 6 **PASSED**. If `test_two_part_tld` fails: your step 1.4 checks the two-label
ending before the one-label case? (`co.il` must win over `il`.) If `test_missing_scheme_is_handled`
fails: step 1.1 — `scheme` must be `""` when the URL had no `://`.

## 11.2 `shannon_entropy` — how random is a string

**What it must do:** `shannon_entropy("abcd") == 2.0`, `shannon_entropy("aaaa") == 0.0`, empty → `0.0`.

**Step 1.6** — Follow the formula from guide 3.5, one line per step:
- if `text` is empty: `return 0.0`
- `counts = Counter(text)` (already imported) — a dict of character → how many times
- `n = len(text)`
- for each count `c` in `counts.values()`: `p = c / n`, add `p * math.log2(p)` to a running total
- `return -total`

**Check:**
```
pytest tests/test_extractor.py -k entropy -v
```
1 PASSED.

## 11.3 `FeatureVector.as_list` — dict to ordered list

Open `phishguard/models/entities.py`, find `as_list`.

**Step 1.7** — One line (guide 1a.2): `return [self.values[name] for name in feature_names]`.

## 11.4 `URLFeatureExtractor.extract` — the 20 numbers

**What it must do:** return a `FeatureVector` whose `.values` is a dict with exactly the 20 names in
`FEATURE_NAMES`, every value a float.

**Step 1.8** — The frame. Type this, then add features between the two comments:
```python
parsed = self.parser.parse(url)
lowered = parsed.raw.lower()
values = {}
# ---- features start ----
values["url_length"] = float(len(parsed.raw))
values["num_dots"] = float(parsed.raw.count("."))
values["has_https"] = 1.0 if parsed.scheme == "https" else 0.0
# ---- features end ----
assert set(values) == set(FEATURE_NAMES), f"missing: {set(FEATURE_NAMES) - set(values)}"
return FeatureVector(values)
```

**Step 1.9** — Run the test:
```
pytest tests/test_extractor.py -k all_features -v
```
It fails with `AssertionError: missing: {...}` and lists the 17 names you have not written yet.
**This list is your to-do list.** Add features one at a time, run the test, watch the list shrink.

**Step 1.10** — Write the 17 features. For each one, this table tells you what to compute. Every
value must be wrapped in `float(...)` (or written as `1.0 / 0.0`).

| Feature | Compute | Hint |
|---|---|---|
| `host_length` | length of `parsed.host` | `len(...)` |
| `path_length` | length of `parsed.path` | |
| `num_hyphens` | count of `"-"` in the raw URL | `.count("-")` |
| `num_underscores` | count of `"_"` | |
| `num_slashes` | count of `"/"` in the raw URL, minus 2 if `"://"` is in it | |
| `num_digits` | how many characters are digits | `sum(ch.isdigit() for ch in parsed.raw)` |
| `digit_ratio` | `num_digits / url_length`, but `0.0` if the length is 0 | reuse `values["num_digits"]` |
| `num_subdomains` | `len(parsed.subdomains)` | |
| `num_query_params` | number of non-empty pieces when you split `parsed.query` on `"&"` | `len([p for p in parsed.query.split("&") if p])` |
| `has_ip_host` | `1.0` if `parsed.has_ip_host` | |
| `has_at_symbol` | `1.0` if `"@"` in the raw URL | |
| `has_port` | `1.0` if `parsed.port` is not `None` | |
| `suspicious_word_count` | how many words of `config.SUSPICIOUS_WORDS` appear in `lowered` | `sum(1 for w in config.SUSPICIOUS_WORDS if w in lowered)` |
| `suspicious_tld` | `1.0` if `parsed.tld` in `config.SUSPICIOUS_TLDS` | |
| `is_shortener` | `1.0` if `parsed.host` in `config.URL_SHORTENERS` | |
| `entropy` | `shannon_entropy(parsed.raw)` | |
| `brand_in_subdomain` | `1.0` if any word of `BRAND_WORDS` is inside `" ".join(parsed.subdomains)` **and not** inside `parsed.domain` | two conditions with `and` |

**Check:**
```
pytest tests/test_extractor.py -v
```
10 PASSED. If `test_phishing_url_features` fails on `suspicious_word_count >= 3`: are you searching
in `lowered` (lower-case)? If `test_counts` fails on `num_query_params`: empty pieces must not count.

## 11.5 `extract_many` — many URLs to a matrix

**Step 1.11** — One line: `return [self.extract(u).as_list(FEATURE_NAMES) for u in urls]`.

## 11.6 See it with your own eyes

**Step 1.12** — Create a throw-away file `try_features.py` in the project folder:
```python
from phishguard.features.extractor import URLFeatureExtractor
ex = URLFeatureExtractor()
for url in ["https://www.google.com/search?q=x", "http://paypal.com.secure-login.xyz/verify/account"]:
    print(url)
    for name, value in ex.extract(url).values.items():
        print(f"   {name:24} {value}")
```
Run `python try_features.py`. Compare with the table in guide 3.3. Every number must match.
Then delete the file (or add it to `.gitignore`).

**Commit:**
```
git add .
git commit -m "stage 1: parser and feature extractor"
git push
```
Send Ahmad the output of `pytest tests/test_parser.py tests/test_extractor.py -v`.

# Chapter 12 — Stage 2: the data

**Goal:** read the CSV, take a balanced sample, compute features for every row, split into
train / validation / test.
**Files:** `phishguard/ml/dataset.py`.
**Guide chapters:** 2 (train/val/test), 3.6 (feature table).

Before you start: `data/phishing_site_urls.csv` must exist (see `data/README.md`). Until it does,
use `config.SAMPLE_PATH` (the 60-row file) — the tests use it anyway.

## 12.1 `read`

**What it must do:** return a DataFrame with two columns, `url` (clean string) and `label` (0 / 1).

**Step 2.1** — Type:
```python
df = pd.read_csv(self.path)
df = df[[config.DATASET_URL_COLUMN, config.DATASET_LABEL_COLUMN]].dropna()
```
**Step 2.2** — Clean the URL and make the label a number:
```python
df["url"] = df[config.DATASET_URL_COLUMN].astype(str).str.strip().str.lower()
df["label"] = (df[config.DATASET_LABEL_COLUMN] == config.POSITIVE_LABEL).astype(int)
```
**Step 2.3** — Keep only the two new columns, remove duplicate URLs, return:
```python
df = df[["url", "label"]].drop_duplicates("url").reset_index(drop=True)
return df
```
**Check:** `pytest tests/test_dataset.py -k read -v` → 1 PASSED (the sample has exactly 30 `bad` rows).

## 12.2 `balance`

**What it must do:** the same number of rows from each class, shuffled.

**Step 2.4** — Recipe:
- `bad = df[df["label"] == 1]`, `good = df[df["label"] == 0]`
- `n = min(self.per_class, len(bad), len(good))`
- take `n` random rows from each: `bad.sample(n=n, random_state=self.seed)` and the same for `good`
- `both = pd.concat([...])`, then shuffle: `both.sample(frac=1, random_state=self.seed).reset_index(drop=True)`
- `print(f"balanced sample: {n} per class")` and return

## 12.3 `load`

**What it must do:** features for every row, then the double split, returned as a `DatasetSplit`.

**Step 2.5** — Features:
```python
df = self.balance(self.read())
urls = df["url"].tolist()
X = np.array(self.extractor.extract_many(urls))
y = df["label"].to_numpy()
```
(On 20,000 rows this takes a few seconds. Fine.)

**Step 2.6** — Split off the test set, then the validation set from what is left:
```python
from sklearn.model_selection import train_test_split
X_rest, X_test, y_rest, y_test, urls_rest, urls_test = train_test_split(
    X, y, urls, test_size=config.TEST_SIZE, stratify=y, random_state=self.seed)
val_share = config.VALIDATION_SIZE / (1 - config.TEST_SIZE)
X_train, X_val, y_train, y_val = train_test_split(
    X_rest, y_rest, test_size=val_share, stratify=y_rest, random_state=self.seed)
```
*Why two splits:* `train_test_split` makes two groups; we need three, so we do it twice.
*Why `stratify`:* keeps 50/50 in every group. *Why `random_state`:* the same split every run.

**Step 2.7** — Return `DatasetSplit(X_train, y_train, X_val, y_val, X_test, y_test, FEATURE_NAMES, urls_test)`.

**Check:** `pytest tests/test_dataset.py -v` → 3 PASSED.

## 12.4 `feature_table` — look before you model

**Step 2.8** —
```python
urls = df["url"].tolist()
X = np.array(self.extractor.extract_many(urls))
table = pd.DataFrame(X, columns=FEATURE_NAMES)
table["label"] = df["label"].to_numpy()
return table
```
**Step 2.9** — Throw-away script: load with `DatasetLoader(config.DATASET_PATH, per_class=2000)`,
`df = loader.balance(loader.read())`, `t = loader.feature_table(df)`,
`print(t.groupby("label").mean().T)` and save with `.to_csv("reports/feature_means.csv")`.
Look at the two columns (0 = good, 1 = bad). Write three sentences about the biggest differences.
Keep them — they go in the book.

**Commit:** `git commit -am "stage 2: dataset loader"` → push → send Ahmad `pytest tests/test_dataset.py -v`.

# Chapter 13 — Stage 3: the first model

**Goal:** train logistic regression, save it, load it back.
**Files:** `phishguard/ml/trainer.py`, `phishguard/ml/bundle.py`, `train.py`.
**Guide chapters:** 4.1–4.4, 6.2–6.3.

## 13.1 `build_logistic`

**Step 3.1** — Two imports at the top of `trainer.py`:
```python
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
```
**Step 3.2** — The function body:
```python
return Pipeline([("scaler", StandardScaler()),
                 ("clf", LogisticRegression(max_iter=1000, class_weight="balanced",
                                            random_state=config.RANDOM_SEED))])
```

## 13.2 `train` (stage-3 version, no grid search yet)

**Step 3.3** — Recipe:
- `results = {}`
- if `models` is `"logistic"` or `"both"`: `pipeline = self.build_logistic()`; `start = time.perf_counter()`;
  `pipeline.fit(self.split.X_train, self.split.y_train)`; `seconds = time.perf_counter() - start`;
  `results["logistic"] = TrainedModel("logistic", pipeline, {}, -1.0, seconds)`
- (the forest branch comes in stage 4)
- `return results`

## 13.3 `ModelBundle` — save and load

**Step 3.4** — `from_trained`:
```python
return cls(pipeline=trained.pipeline, feature_names=list(feature_names),
           threshold=report_entry.get("threshold", config.DEFAULT_THRESHOLD),
           model_name=trained.name, metrics=report_entry)
```
**Step 3.5** — `save`:
```python
self.version = f"{self.model_name}-{self.trained_at}"
joblib.dump(self, path)
```
**Step 3.6** — `load` — with the safety check (guide 6.3):
```python
from phishguard.features.extractor import FEATURE_NAMES     # import inside to avoid a circle
bundle = joblib.load(path)
if list(bundle.feature_names) != list(FEATURE_NAMES):
    raise RuntimeError("model was trained with different features - run train.py again")
return bundle
```

## 13.4 `train.py` — wire it together (first version)

**Step 3.7** — Imports at the top of `train.py`:
```python
from phishguard.ml.bundle import ModelBundle
from phishguard.ml.dataset import DatasetLoader
from phishguard.ml.trainer import ModelTrainer
```
**Step 3.8** — In `main`, replace `raise NotImplementedError` with:
```python
loader = DatasetLoader(path, per_class=args.per_class)
split = loader.load()
trainer = ModelTrainer(split)
results = trainer.train(models="logistic")
model = results["logistic"]
probs = model.pipeline.predict_proba(split.X_val)[:, 1]
val_accuracy = ((probs >= 0.5) == split.y_val).mean()
print(f"logistic: validation accuracy {val_accuracy:.3f}  ({model.train_seconds:.1f} s)")
ModelBundle.from_trained(model, split.feature_names, {"threshold": 0.5}).save(config.BEST_MODEL_PATH)
print(f"saved {config.BEST_MODEL_PATH}")
```
(In stage 4 you will replace the middle with the evaluator.)

**Check 1:** `python train.py --sample` → prints an accuracy (any number — 60 rows is tiny) and
"saved ...". **Check 2:** `python train.py --model logistic` on the real data → validation accuracy
**above 0.90**. If it is around 0.50: the labels are wrong — go back to `read` (step 2.2). If
`ConvergenceWarning`: fine for now; `max_iter=1000` is there.

**Commit:** `git commit -am "stage 3: logistic regression + bundle"` → push → send Ahmad the two printed lines.

# Chapter 14 — Stage 4: compare, evaluate, choose the threshold

**Goal:** the random forest, grid search, all the metrics, the threshold, four chart files.
**Files:** `trainer.py`, `evaluator.py`, `train.py`.
**Guide chapters:** 4.5–4.7, 5.

## 14.1 `build_forest`

**Step 4.1** — `from sklearn.ensemble import RandomForestClassifier`, then the same Pipeline shape
with `RandomForestClassifier(n_estimators=config.RANDOM_FOREST_TREES, n_jobs=-1,
class_weight="balanced", random_state=config.RANDOM_SEED)`.

## 14.2 `fit_with_search`

**Step 4.2** — `from sklearn.model_selection import GridSearchCV`. Body:
```python
search = GridSearchCV(pipeline, param_grid, cv=config.CV_FOLDS, scoring="f1", n_jobs=-1)
start = time.perf_counter()
search.fit(self.split.X_train, self.split.y_train)
return TrainedModel(name, search.best_estimator_, search.best_params_,
                    float(search.best_score_), time.perf_counter() - start)
```
**Step 4.3** — Update `train` so both branches call `fit_with_search` with these grids:
`{"clf__C": [0.01, 0.1, 1, 10]}` for logistic; `{"clf__max_depth": [None, 10, 20], "clf__min_samples_leaf": [1, 3]}`
for the forest. (`clf__` = "the parameter C of the step called clf".)

## 14.3 `ModelEvaluator.metrics`

**Step 4.4** — Imports: `from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix`.
**Step 4.5** — Body:
```python
probs = pipeline.predict_proba(X)[:, 1]
preds = (probs >= threshold).astype(int)
tn, fp, fn, tp = confusion_matrix(y, preds, labels=[0, 1]).ravel()
return {"accuracy": float(accuracy_score(y, preds)), "precision": float(precision_score(y, preds, zero_division=0)),
        "recall": float(recall_score(y, preds, zero_division=0)), "f1": float(f1_score(y, preds, zero_division=0)),
        "auc": float(roc_auc_score(y, probs)), "threshold": float(threshold),
        "confusion": [[int(tn), int(fp)], [int(fn), int(tp)]]}
```

## 14.4 `choose_threshold`

**Step 4.6** — Recipe (guide 5.1): `best = config.DEFAULT_THRESHOLD`; for `t` in
`np.arange(0.05, 0.96, 0.05)`: `m = self.metrics(pipeline, self.split.X_val, self.split.y_val, t)`;
if `m["recall"] >= target_recall`: `best = float(t)` (keep going — we want the *highest* that passes).
Return `best`. Uses **validation** only.

## 14.5 `importances`

**Step 4.7** — `clf = pipeline.named_steps["clf"]`; if `hasattr(clf, "coef_")`: `weights = clf.coef_[0]`;
else `weights = clf.feature_importances_`; return `{name: float(w) for name, w in zip(self.split.feature_names, weights)}`.

## 14.6 `compare`

**Step 4.8** — For each `name, trained` in `trained.items()`: `t = self.choose_threshold(trained.pipeline)`;
`entry = self.metrics(trained.pipeline, X_test, y_test, t)`; add `entry["cv_f1"] = trained.cv_score`,
`entry["best_params"] = trained.best_params`, `entry["train_seconds"]`, `entry["importances"] = self.importances(...)`;
store in `report[name]`. Then `best = max(report, key=lambda n: (report[n]["f1"], report[n]["recall"]))`.
Return `(best, report)`.

## 14.7 `worst_mistakes`

**Step 4.9** — `probs` on `X_test`; false positives = indexes where `y_test == 0` and `probs >= threshold`,
sorted by `probs` descending, first `n`; false negatives = `y_test == 1` and `probs < threshold`,
sorted ascending. Return `{"false_positives": [(url, prob), ...], "false_negatives": [...]}` using `self.split.urls_test`.

## 14.8 `save_reports`

**Step 4.10** — `metrics.json`: `json.dump(report, f, indent=2)` (remove the `importances` dict from
the copy if you want it shorter, or keep it).
**Step 4.11** — Confusion matrix picture, per model:
```python
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
cm = np.array(entry["confusion"])
fig, ax = plt.subplots(figsize=(4, 4))
ax.imshow(cm, cmap="Blues")
for i in range(2):
    for j in range(2):
        ax.text(j, i, str(cm[i, j]), ha="center", va="center", fontsize=14)
ax.set_xticks([0, 1]); ax.set_xticklabels(["good", "phishing"]); ax.set_xlabel("predicted")
ax.set_yticks([0, 1]); ax.set_yticklabels(["good", "phishing"]); ax.set_ylabel("actual")
ax.set_title(f"{name}  (threshold {entry['threshold']:.2f})")
fig.tight_layout(); fig.savefig(os.path.join(directory, f"confusion_matrix_{name}.png")); plt.close(fig)
```
**Step 4.12** — ROC: `from sklearn.metrics import RocCurveDisplay`; one `fig, ax`; for each model
`RocCurveDisplay.from_estimator(pipeline, X_test, y_test, name=name, ax=ax)`; save `roc_curve.png`.
(You will need the pipelines here — pass `trained` into `save_reports` too, or store them on `self` in `compare`.)
**Step 4.13** — Importances: sort the best model's dict by absolute value, `ax.barh(names, values)`, save `feature_importance.png`.

## 14.9 `train.py` — final version

**Step 4.14** — Replace the middle of `main` with: `results = trainer.train(models=args.model)`;
`evaluator = ModelEvaluator(split)`; `best, report = evaluator.compare(results)`;
`evaluator.save_reports(report, config.REPORTS_DIR)`; print one line per model
(`name, precision, recall, f1, auc, threshold, seconds`); save the bundle of `results[best]` with
`report[best]`; print the worst mistakes.

**Check:** `python train.py` → under 2 minutes; `reports/` contains `metrics.json`,
`confusion_matrix_logistic.png`, `confusion_matrix_forest.png`, `roc_curve.png`, `feature_importance.png`.
Open `metrics.json`: **recall ≥ 0.95 and precision ≥ 0.90** for the best model. Open the pictures.
Read the 10 worst mistakes and, for 5 of them, write one line why the model was fooled.

**Commit** → push → send Ahmad `metrics.json` and the four pictures.

# Chapter 15 — Stage 5: predict one URL and explain it

**Goal:** paste a URL, get verdict + probability + three reasons, from the terminal.
**Files:** `predictor.py`, `explainer.py`, `evaluate.py`.

## 15.1 `Predictor.load`

**Step 5.1** —
```python
if not os.path.exists(self.model_path):
    print(f"no model at {self.model_path} - run: python train.py")
    self.is_ready = False
    return
self.bundle = ModelBundle.load(self.model_path)
self.is_ready = True
```
(add `import os` at the top.)

## 15.2 `Predictor.predict`

**Step 5.2** — Exactly the six lines in the docstring. Two traps:

- The first line, `url = url.strip().lower()`, is the **same** clean-up `DatasetLoader.read` did to every
  training URL (Step 2.2). Leave it out and the model sees `PayPal.com` at scan time while it only ever saw
  `paypal.com` in training — the entropy is different, so the probability is different, with no error.
  That is the train/serve rule of §3.4 again: whatever happens to a URL before training must happen at scan
  time too. `test_pipeline.py` checks it by scanning the same URL in capitals.
- `float(...)` around the probability.

## 15.3 `Explainer.contributions`

**Step 5.3** — Get the pieces:
```python
names = self.bundle.feature_names
clf = self.bundle.pipeline.named_steps["clf"]
scaler = self.bundle.pipeline.named_steps["scaler"]
x = [result.features[n] for n in names]
x_scaled = scaler.transform([x])[0]
```
**Step 5.4** — Two cases:
```python
if hasattr(clf, "coef_"):
    contribs = clf.coef_[0] * x_scaled
else:
    contribs = clf.feature_importances_ * np.sign(x_scaled)
```
**Step 5.5** — Build the list: for `i, name in enumerate(names)`: `raw = result.features[name]`;
`text = TEMPLATES.get(name, name).format(value=raw)` — except when `raw == 0` and `name` is in
`TEMPLATES_WHEN_ZERO`: then `text = TEMPLATES_WHEN_ZERO[name]`. (Why: an `http://` URL has `has_https = 0`,
which pushes toward phishing — the reason shown must be "Does not use HTTPS", not "Uses HTTPS".) Append
`Explanation(feature=name, value=raw, contribution=float(contribs[i]), text=text)`. Return the list.

## 15.4 `Explainer.explain`

**Step 5.6** — `wanted_sign = 1 if result.verdict is Verdict.PHISHING else -1`;
keep contributions where `c.contribution * wanted_sign > 0`; sort by `abs(c.contribution)` descending;
`result.explanations = kept[:top]`; return it.

## 15.5 `evaluate.py`

**Step 5.7** — For `--url` / `--file`: build the list of URLs; `predictor = Predictor()`;
`explainer = Explainer(predictor.bundle)`; for each: `r = predictor.predict(url)`;
`explainer.explain(r)`; print `url`, `r.verdict.label`, `f"{r.probability:.0%}"`, then each
explanation's `text` on its own line with `->` or `<-`.

**Check:** `pytest tests/test_pipeline.py -v` → 2 PASSED. Then:
```
python evaluate.py --url "http://paypal.com.secure-login.xyz/verify"
python evaluate.py --url "https://www.google.com/"
```
The first says phishing with a high percentage and three sensible reasons; the second legitimate.
Now collect 10 real phishing URLs from https://phishtank.org/ and 10 real sites into `my_urls.txt`
and run `--file`. Count how many are right. Write the number down.

**Commit** → push → send Ahmad the `--file` output.

# Chapter 16 — Stage 6: the database and the app

**Goal:** the desktop app: scan tab, history tab, statistics tab.
**Files:** `database/db.py`, `database/repositories.py`, `models/entities.py` (`risk_level`),
`controllers/app_controller.py`, `views/*.py`, `utils/exporter.py`, `train.py` (register the model).

## 16.1 `Database` — three methods

**Step 6.1** — `get_connection`:
```python
conn = sqlite3.connect(self.db_path)
conn.row_factory = sqlite3.Row
conn.execute("PRAGMA foreign_keys = ON")
return conn
```
**Step 6.2** — `connection` (the context manager — copy this shape exactly, it is plumbing):
```python
conn = self.get_connection()
try:
    yield conn
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
```
**Step 6.3** — `initialize_schema`: `with self.connection() as conn: conn.executescript(SCHEMA)`.

## 16.2 `ScanRepository`

**Step 6.4** — `add` (written out in full — the others follow its shape):
```python
with self.db.connection() as conn:
    cursor = conn.execute(
        "INSERT INTO scans (url, scanned_at, probability, verdict, threshold, features, model_version, feedback) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (result.url, result.scanned_at.isoformat(), result.probability, result.verdict.value,
         result.threshold, json.dumps(result.features), result.model_version, result.feedback))
    return cursor.lastrowid
```
**Step 6.5** — A helper `_row_to_result(self, row)` that builds a `ScanResult` from a row:
`url=row["url"]`, `probability=row["probability"]`, `verdict=Verdict(row["verdict"])`,
`threshold=row["threshold"]`, `features=json.loads(row["features"])`, `model_version=row["model_version"]`,
`scanned_at=datetime.fromisoformat(row["scanned_at"])`, `feedback=row["feedback"]`, `id=row["id"]`.
**Step 6.6** — `get`: `SELECT * FROM scans WHERE id = ?` → `fetchone()` → `None` or `_row_to_result`.
**Step 6.7** — `list_recent`: build the query in pieces:
```python
conditions, params = [], []
if verdict is not None:
    conditions.append("verdict = ?"); params.append(verdict.value)
if search:
    conditions.append("url LIKE ?"); params.append(f"%{search}%")
where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
sql = f"SELECT * FROM scans{where} ORDER BY scanned_at DESC LIMIT ?"
params.append(limit)
```
then `fetchall()` and map each row.
**Step 6.8** — `set_feedback`: one `UPDATE`. **Step 6.9** — `counts_by_verdict`:
`SELECT verdict, COUNT(*) AS n FROM scans GROUP BY verdict` → `{Verdict(row["verdict"]): row["n"]}`.

**Check:** `pytest tests/test_repositories.py -k "scan or feedback or list" -v`.

## 16.3 `ModelRepository`

**Step 6.10** — `register`: `INSERT OR REPLACE INTO models (version, model_name, trained_at, train_rows,
accuracy, precision_, recall, f1, auc, threshold, notes) VALUES (?,...)` with the values from `metrics`
(`metrics.get("accuracy")` etc.). **Step 6.11** — `list_all`: `SELECT * ... ORDER BY trained_at DESC` → `[dict(row) for row in rows]`.
**Step 6.12** — In `train.py`, after saving the bundle: `ModelRepository().register(bundle.version, best, bundle.trained_at, len(split.y_train), report[best], report[best]["threshold"])`.

**Check:** `pytest -v` → everything green (25 tests).

## 16.4 `ScanResult.risk_level`

**Step 6.13** — `"low"` if `probability < config.RISK_LOW`, `"high"` if `> config.RISK_HIGH`, else `"medium"`.

## 16.5 The views — build them small, then grow

Do the tabs in this order, running `python run.py` after each one.

**Step 6.14** — `MainWindow.__init__`:
```python
notebook = ttk.Notebook(self)
notebook.pack(fill="both", expand=True)
self.scan = ScanView(notebook, on_scan)
self.history = HistoryView(notebook, on_filter, on_feedback, on_export)
self.stats = StatsView(notebook)
notebook.add(self.scan, text="Scan"); notebook.add(self.history, text="History"); notebook.add(self.stats, text="Statistics")
```
(import the three view classes at the top). `show_error` / `show_info`: `from tkinter import messagebox` inside the method, then `messagebox.showerror("PhishGuard", text)`.

**Step 6.15** — `ScanView.__init__` — the minimum:
```python
self.url_var = tk.StringVar()
entry = ttk.Entry(self, textvariable=self.url_var, width=80)
entry.grid(row=0, column=0, sticky="ew", padx=4)
entry.bind("<Return>", lambda e: self.on_scan(self.url_var.get()))
ttk.Button(self, text="Scan", command=lambda: self.on_scan(self.url_var.get())).grid(row=0, column=1)
self.verdict_label = tk.Label(self, text="-", font=("Segoe UI", 22, "bold"))
self.verdict_label.grid(row=1, column=0, columnspan=2, pady=12)
self.meter = ttk.Progressbar(self, maximum=100, length=400)
self.meter.grid(row=2, column=0, columnspan=2)
self.prob_label = ttk.Label(self, text="")
self.prob_label.grid(row=3, column=0, columnspan=2, pady=4)
self.reasons = tk.Text(self, height=6, width=90, state="disabled")
self.reasons.grid(row=4, column=0, columnspan=2, pady=8)
self.columnconfigure(0, weight=1)
```
(`import tkinter as tk` at the top.) **Step 6.16** — `show_result`:
- colour: `{"low": "#2e7d32", "medium": "#ef6c00", "high": "#c62828"}[result.risk_level]`
- `self.verdict_label.configure(text=result.verdict.label, fg=colour)`
- `self.meter["value"] = result.probability * 100`
- `self.prob_label.configure(text=f"phishing probability {result.probability:.0%}  (threshold {result.threshold:.0%})")`
- the Text: `configure(state="normal")`, `delete("1.0", "end")`, insert one line per explanation
  (`"-> " if e.contribution > 0 else "<- "` + `e.text`), `configure(state="disabled")`.

**Step 6.17** — `AppController.__init__` and `on_scan` — recipe:
- `__init__`: create `Predictor()`, `Explainer(...)` if ready, `ScanRepository()`, `ModelRepository()`,
  then `MainWindow(root, on_scan=self.on_scan, on_filter=self.on_filter, on_feedback=self.on_feedback, on_export=self.on_export)`.
- `start`: if not `predictor.is_ready`: `view.show_error("No trained model. Run: python train.py")`.
- `on_scan(url)`: `url = url.strip()`; if empty → `show_error("Paste a URL first")`; if not ready → error;
  `try:` `result = predictor.predict(url)`; `explainer.explain(result)`; `result.id = scans.add(result)`;
  `view.scan.show_result(result)`; `except Exception as exc: view.show_error(str(exc))`.

**Check:** `python run.py` → paste a URL → verdict, meter, reasons. If the window opens and closes
immediately: read the traceback in the terminal.

**Step 6.18** — `HistoryView`: a filter row (`ttk.Combobox(values=["all", "legitimate", "phishing"])`,
a search `Entry`, an "Apply" button calling `on_filter(verdict_or_None, search_text)`), a
`ttk.Treeview(columns=("time", "url", "probability", "verdict", "feedback"), show="headings")`,
three buttons: "Mark correct" → `on_feedback(self.selected_id(), "correct")`, "Mark wrong",
"Export CSV" → `on_export()`. In `show_rows`: `for item in tree.get_children(): tree.delete(item)`,
then `tree.insert("", "end", iid=str(r.id), values=(...))`. `selected_id`: `sel = tree.selection()`;
`return int(sel[0]) if sel else None`.

**Step 6.19** — `AppController.on_filter`, `on_feedback`, `on_export` — each is two or three lines
calling the repository / exporter and refreshing. `ReportExporter.export_history`: `csv.writer` into
`exports/history_<timestamp>.csv` with `encoding="utf-8-sig"`; return the path.

**Step 6.20** — `StatsView`: `from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg` and
`from matplotlib.figure import Figure`; in `__init__` create `Figure((5, 3))`, `self.ax = fig.add_subplot()`,
`self.canvas = FigureCanvasTkAgg(fig, master=self)`, `self.canvas.get_tk_widget().pack()`, and a
`Treeview` for the models. In `show`: `self.ax.clear()`, `self.ax.bar(["legitimate", "phishing"], [counts.get(...,0), ...])`,
`self.canvas.draw_idle()`; refill the tree from `models`.

**Check:** the three tabs work; a scan appears in History; "Mark wrong" changes the row; Export
creates a file that opens in Excel; Statistics shows the bars and your model rows.

**Commit:** `git commit -am "stage 6: database and desktop app"` → push → send Ahmad a screenshot of each tab.

# Chapter 16b — Stage 7: experiments and documentation

**Step 7.1** — Fill the experiments table (guide 5.6) by running `train.py` with the variations
(`--model logistic`, `--per-class 2000 / 10000 / 20000`; comment out `class_weight` once) and copying
the numbers from `metrics.json` each time. **Step 7.2** — Drift test (guide 5.5) with 30 URLs from
PhishTank this week. **Step 7.3** — Your own tests: one for `Explainer.explain` (top-3, right sign),
one for `risk_level`, one for `export_history` (file exists, header line right). **Step 7.4** — UML
(`docs/UML.md`). **Step 7.5** — The book, chapter by chapter from `docs/PROJECT_BOOK_MAP.md`.
**Step 7.6** — A 3-minute demo video of the app, in case the laptop misbehaves at the defense.

# Chapter 16a — Troubleshooting

| Message / symptom | Cause | Fix |
|---|---|---|
| `NotImplementedError` | That function is not written yet | Look at the traceback: which file, which function; open it |
| `ModuleNotFoundError: No module named 'phishguard'` | Wrong folder | `cd` to the `PhishGuard` folder (the one with `config.py`) |
| `ModuleNotFoundError: No module named 'sklearn'` | venv not active or not installed | `.venv\Scripts\activate` then `pip install -r requirements.txt` |
| `AssertionError: missing: {...}` in `extract` | Features not yet written | The set in the message is your to-do list |
| `assert 2 == 3` in a test | Your value differs from the expected | Print the feature for that URL; compare with guide 3.3 |
| `AttributeError: 'NoneType' object has no attribute 'lower'` | `parsed.hostname` is `None` | `(parsed.hostname or "")` — step 1.1 |
| `ValueError: could not convert string to float` | A feature returned text or None | Every feature `float(...)` |
| `X has 21 features, but StandardScaler is expecting 20` | New feature, old model | `python train.py` again |
| Accuracy exactly 0.50 / 0.72 | Labels all the same | Step 2.2: `POSITIVE_LABEL` and `astype(int)` |
| `ConvergenceWarning` | Normal with unscaled data | The scaler is in the Pipeline; ignore if metrics are fine |
| `train.py` runs 20+ minutes | Grid too big / no `n_jobs` | `n_jobs=-1`; `--per-class 5000` while developing |
| `TypeError: Object of type float32 is not JSON serializable` | numpy numbers in `features` | `float(v)` in `extract` |
| `sqlite3.IntegrityError: CHECK constraint failed: verdict` | Stored the enum, not `.value` | `verdict.value` on write |
| `no such table: scans` | Schema not created | `Database().initialize_schema()` runs in `run.py`; in a script call it yourself |
| App says "No trained model" but the file exists | Wrong path / `is_ready` not set | Print `config.BEST_MODEL_PATH`; step 5.1 |
| Window opens then closes | Exception in `AppController.__init__` | Read the terminal traceback |
| `_tkinter.TclError: unknown option "-fg"` | `fg` on a `ttk.Label` | Use `tk.Label` for coloured text (step 6.15) |
| A test passes alone, fails with others | Singleton leak | `Predictor._instance = None` / `Database._instance = None` (see `conftest.py`) |

**Method, always:** last line of the traceback = *what*; first line in your own file = *where*;
`print(type(x), x)` before that line; reproduce on the 60-row sample; write down every bug that
cost 30 minutes in `TASKS.md`.
