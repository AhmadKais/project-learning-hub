# PhishGuard — hints, checks and traps, stage by stage

Use this file when you are **stuck** on a function of your skeleton. For each hard function:

- **Learn it in** — the theory section, notebook and exercise that teach the idea.
- **Hints** — hidden. Open one at a time: 💡 a nudge, 🔧 the steps.
- **Check yourself** — numbers you can compare against before you run the tests.
- **Traps** — the mistakes that make a test fail (or, worse, pass while the program is wrong).

`CHECKLIST.md` (next to this file) lists **every** function you have to write. The docstrings in your code and
the build chapter `04_build/10_build.md` give the step-by-step; this file is for the moments those are not enough.

> **The working loop.** One function → run **its** test (`pytest tests/test_parser.py -v`) → green → commit
> → next. Never write three functions and then test. If a test is red, read the *last* lines of the error first.

---

## Stage 1 — URL parsing and features

### `URLParser.parse`

**Learn it in:** theory `03_features` §3.1 · notebook `01_url_features` §1–2 · exercises **ex01, ex02**

<details><summary>💡 Hint 1</summary>

The owner of a host is read from the **right**: last label = TLD (or the last two, for `co.il`-style TLDs), the
one before = domain, everything to the left = subdomains. `paypal.com.secure-login.xyz` belongs to `secure-login`.
</details>

<details><summary>🔧 Hint 2 — the steps</summary>

1. `text = url.strip()`; remember `had_scheme = "://" in text`; if not, parse `"http://" + text` instead.
2. Put `urlparse(...)`, `.hostname` **and `.port`** inside one `try: ... except ValueError:` — `.port` raises on
   `http://a.com:99999` and `urlparse` raises on `http://[::1`. In the `except`, return a `ParsedURL` with
   empty fields.
3. If the host matches `IP_PATTERN`: `subdomains=[]`, `domain=host`, `tld=""`.
4. Else `labels = [l for l in host.split(".") if l]`; `n_tld = 2` if there are at least 3 labels **and** the last two
   joined (`"co.il"`) are in `config.COMMON_TLDS`, else `1`. Then `tld = ".".join(labels[-n_tld:])`,
   `domain = labels[-n_tld - 1]`, `subdomains = labels[:-n_tld - 1]`. If there are not enough labels
   (`localhost`), domain = host.
5. `scheme = parsed.scheme if had_scheme else ""`.
</details>

**Check yourself:**

| URL | subdomains | domain | tld | scheme | port |
|---|---|---|---|---|---|
| `http://paypal.com.secure-login.xyz/verify` | `['paypal', 'com']` | `secure-login` | `xyz` | `http` | `None` |
| `https://www.google.com/search?q=python&hl=en` | `['www']` | `google` | `com` | `https` | `None` |
| `http://192.168.1.10:8080/login.php` | `[]` | `192.168.1.10` | `''` | `http` | `8080` |
| `www.bgu.ac.il/apply` | `['www']` | `bgu` | `ac.il` | `''` | `None` |
| `bit.ly/3xYz9` | `[]` | `bit` | `ly` | `''` | `None` |

**Traps:** forgetting that the *original* had no scheme (`has_https` must then be 0) · `parsed.hostname` is
`None` for garbage → `(parsed.hostname or "")` · the `try` must cover `.port`, not only `urlparse`.

### `shannon_entropy`

**Learn it in:** theory §3.5 · notebook `01` §4 · **ex03**

<details><summary>🔧 Hint</summary>

`counts = Counter(text)`, `n = len(text)`, then `-sum(c/n * math.log2(c/n) for c in counts.values())`. Return
`0.0` for `""` **before** dividing.
</details>

**Check yourself:** `"aaaa"` → 0.0 · `"aabb"` → 1.0 · `"abcd"` → 2.0 · `"aaab"` → 0.811

### `URLFeatureExtractor.extract`

**Learn it in:** theory §3.2–3.4 (do the §3.3 table by hand first) · notebook `01` §3 · **ex04**

<details><summary>💡 Hint 1</summary>

Compute three helpers once at the top — the parsed URL, `lowered = url.lower()`, and the part after the scheme
(`url.split("://", 1)[1]` if there is one) — then build the dict feature by feature in the order of the module
docstring. Wrap every value in `float(...)`.
</details>

<details><summary>🔧 Hint 2 — the features that fail most often</summary>

- `num_slashes`: count `/` **after** the scheme, so `http://` does not add 2.
- `num_query_params`: `len([q for q in parsed.query.split("&") if q])` — `"".split("&")` is `[""]`, which is 1, not 0.
- `suspicious_word_count`: how many **different** words of the list appear in `lowered` (each word counts once).
- `brand_in_subdomain`: join the subdomains into one string; a brand must appear there **and not** in the domain.
- `digit_ratio`: guard `len(url) == 0`.
</details>

**Check yourself** — `http://paypal.com.secure-login.xyz/verify`:

```
url_length 41   host_length 27   path_length 7   num_dots 3   num_hyphens 1   num_slashes 1
num_subdomains 2   has_https 0   suspicious_word_count 4 (paypal, secure, login, verify)
suspicious_tld 1   brand_in_subdomain 1   entropy 4.436
```

`http://192.168.1.10:8080/login.php` → `num_digits 13`, `digit_ratio 0.382`, `has_ip_host 1`, `has_port 1`.

**Traps:** returning ints for some features and floats for others is fine for the tests but makes the database
JSON inconsistent — use `float` everywhere · the `assert set(values) == set(FEATURE_NAMES)` at the end is your
friend: it catches a typo in a feature name immediately.

### `FeatureVector.as_list`

Loop over **`feature_names`**, never over `self.values`. Read the warning in the docstring twice — this one line is
the train == serve contract (theory §3.4).

---

## Stage 2 — Data

### `DatasetLoader.read / balance / load`

**Learn it in:** theory `02_ml_basics` §2.3 and §2.5 · notebook `02_models` §1

<details><summary>🔧 Hint — the two splits</summary>

```
first:  train_test_split(X, y, urls, test_size=0.15, stratify=y, random_state=self.seed)   -> rest | test
second: train_test_split(X_rest, y_rest, test_size=0.15 / 0.85, stratify=y_rest, random_state=self.seed)
```

`train_test_split` accepts **three** arrays at once — pass the URLs too, so you keep `urls_test` for
`worst_mistakes`.
</details>

**Check yourself:**

| per class | rows after balance | train | val | test |
|---|---|---|---|---|
| sample file (30 + 30) | 60 | 42 | 9 | 9 |
| 2,000 | 4,000 | 2,800 | 600 | 600 |
| 10,000 (default) | 20,000 | 14,000 | 3,000 | 3,000 |

**Traps:** removing duplicates **after** the split (the same URL in train and test = leakage, theory §2.3) ·
forgetting `stratify` · a different `random_state` in the two calls is fine, but a *missing* one makes
`test_split_is_reproducible` fail.

---

## Stage 3 — First model

### `ModelTrainer.build_logistic / build_forest`

The two pipeline steps **must** be named `"scaler"` and `"clf"`:
`Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(...))])`. The explainer looks them up by
these names, and the grid uses them (`"clf__C"` = parameter `C` of the step called `clf`).

**Learn it in:** theory `04_models` §4.1–4.4 · notebook `02_models` · **ex05–ex08** (logistic regression from
scratch — after them, `LogisticRegression` is no longer a black box).

### `ModelBundle.from_trained / save / load`

Follow the docstring. **Check yourself:** after `save`, `ModelBundle.load(path).version` is
`"logistic-2026-…"`, not `""` (set the version *before* `joblib.dump`).

**Trap:** `load` must compare with the extractor's **current** `FEATURE_NAMES` — that is what makes
`test_bundle_refuses_wrong_features` pass, and what protects you when you add a 21st feature later.

---

## Stage 4 — Compare, evaluate, choose the threshold

**Learn it in:** theory `05_evaluation` §5.1–5.4 · notebook `03_threshold_roc_mistakes` · **ex09–ex12**

### `ModelTrainer.fit_with_search`

<details><summary>🔧 Hint</summary>

```
start = time.time()
search = GridSearchCV(pipeline, param_grid, cv=config.CV_FOLDS, scoring="f1", n_jobs=-1)
search.fit(self.split.X_train, self.split.y_train)
return TrainedModel(name, search.best_estimator_, search.best_params_, search.best_score_, time.time() - start)
```
</details>

### `ModelEvaluator.choose_threshold`

<details><summary>💡 Hint 1</summary>

Recall can only go **down** as the threshold goes up. So among the thresholds that still reach the target recall,
the highest one is the one with the fewest false alarms.
</details>

<details><summary>🔧 Hint 2</summary>

`probs = pipeline.predict_proba(self.split.X_val)[:, 1]`; for `t` in `np.arange(0.05, 0.951, 0.01)`: if the
recall of `(probs >= t)` on `y_val` is ≥ the target, remember `t`. Return the last one remembered, or
`config.DEFAULT_THRESHOLD`.
</details>

**Trap:** using `X_test` here. The test split is touched **once**, in `compare`, after the threshold is fixed.

### `ModelEvaluator.compare`

Return `(best_name, report)` where `report[name]` contains at least `accuracy, precision, recall, f1, auc,
threshold, confusion` (`from_trained` and `train.py` read these keys). Choose with
`max(report, key=lambda n: (report[n]["f1"], report[n]["recall"]))` — a tuple key gives the tie-break for free.

**Check yourself** on the sample file (60 rows): it runs end to end and prints two F1 values between 0 and 1. The
numbers mean nothing on 9 test URLs — run the real data before you believe anything.

### `worst_mistakes` and `save_reports`

`worst_mistakes`: `probs` on the test split; false positives = `y == 0` and `pred == 1`, sorted by probability
**descending**; false negatives = `y == 1` and `pred == 0`, sorted **ascending**. Take `split.urls_test[i]` for
the URLs. For the plots, put `import matplotlib; matplotlib.use("Agg")` **before** `import matplotlib.pyplot` —
otherwise saving a figure from a script can try to open a window.

---

## Stage 5 — Live prediction and explanation

### `Predictor.predict`

The first line, `url = url.strip().lower()`, is the **same** clean-up `DatasetLoader.read` gives every training
URL. Without it, `PayPal.com` and `paypal.com` get different entropy and therefore different probabilities.
`test_pipeline.py` scans one URL in capitals to check this.

### `Explainer.contributions / explain`

**Learn it in:** theory §4.1 (a logistic model is a weighted vote: contribution = weight × scaled value) ·
`04_build/10_build.md` §15.3–15.4

**Check yourself** — a logistic model trained on the 60-row sample file (`python train.py --sample --model
logistic`) gives:

```
http://paypal.com.secure-login.xyz/verify/account   phishing
    +0.26  5 suspicious words (login, verify, secure...)
    +0.14  Does not use HTTPS
    +0.13  Ends with a top-level domain often used by attackers
https://www.google.com/                              legitimate
    -0.14  Uses HTTPS
    -0.14  Character randomness (entropy) is 3.64
    -0.12  URL length is 23 characters
```

Your exact numbers will differ a little; the **signs** and the kind of reasons must match. Every sentence must be
*true* about the URL — read them aloud.

**Traps:** sorting by the contribution instead of by its absolute value — a legitimate verdict then shows its
weakest reasons first · using `TEMPLATES` for a yes/no feature whose value is 0 — the app then says "Uses HTTPS"
about an `http://` link (that is what `TEMPLATES_WHEN_ZERO` is for).

---

## Stage 6 — Database and UI

**Learn it in:** the long docstring at the top of `repositories.py` (four shapes cover every method) ·
`04_build/10_build.md` chapter 16

- `Database.connection` is a `@contextmanager`: `conn = self.get_connection()`, then
  `try: yield conn; conn.commit()` / `except: conn.rollback(); raise` / `finally: conn.close()`.
- `list_recent`: build `conditions` and `params` lists, join with `" AND "`, and pass `limit` as the **last**
  parameter: `f"SELECT * FROM scans {where} ORDER BY scanned_at DESC, id DESC LIMIT ?"`. The f-string only
  inserts the `WHERE ... ?` text you built yourself — never a value.
- `counts_by_verdict`: `{Verdict(r["verdict"]): r["n"] for r in rows}` with `COUNT(*) AS n`.
- `ModelRepository.list_all`: `[dict(r) for r in rows]` — a `sqlite3.Row` converts to a dict directly.

**Check yourself:** `pytest tests/test_repositories.py -v` — five tests, including the one that stores
`http://x.com/'); DROP TABLE scans;--` as plain text.

**Traps:** `PRAGMA foreign_keys` and `row_factory` must be set on **every** new connection (in `get_connection`) ·
a test that passes alone and fails with the others = a singleton left over (`Database._instance = None`, see
`conftest.py`).

### The GUI (`views/`, `app_controller.py`)

Views draw and call the controller; the controller calls the predictor and the repositories; nothing else. Build
one screen at a time and run `python run.py` after each. If a click "does nothing", the exception went to the
terminal — look there.

---

## Stage 7 — Experiments, drift, the book

- The experiments table: change **one** thing per row (model, class weights, threshold, sample size) and record
  every number from `reports/metrics.json`, not from memory.
- Drift test: 30 phishing URLs from this week (phishtank.org). If the model catches far fewer than on the test
  split, that is **concept drift** (theory §5.5) — a result, not a failure. Write it up.

---

## When nothing works

| Symptom | Likely cause |
|---|---|
| `ModuleNotFoundError: phishguard` | run `pytest` / `python` from the project root, with the venv active |
| every prediction ≈ the same probability | features in the wrong order (`as_list`), or the scaler is missing from the pipeline |
| validation accuracy ≈ 0.50 | labels wrong in `read` — print `df["label"].value_counts()` |
| real-data accuracy much higher than the drift test | normal — attackers change; see stage 7 |
| `ValueError: Port out of range` | `.port` is outside your `try` in `parse` |
| `TypeError: '_GeneratorContextManager' …` | `@contextmanager` written twice, or `connection` called without `with` |
