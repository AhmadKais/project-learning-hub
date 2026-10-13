# Appendix — Answers to "Check yourself"

For the supervisor: reasoning and calculation, not memorization; 80% correct = he understands.
For the student: try first.

## Chapter 1a

1. `['a', 'b', 'c']` — three pieces; `len("a.b.c")` is **5** (three letters + two dots).
2. `[len(s) for s in ["ab", "cde", "f"]]` → `[2, 3, 1]`.
3. `KeyError: 'y'`. Use `d.get("y")` → `None` (or `d.get("y", 0)` for a default).
4. **7** — `__init__` stored `n` on the object as `self.n`.
5. Open `url_parser.py`, function `parse`, line 40. Something was `None` and you called `.lower()` on it —
   almost certainly `parsed.hostname` was `None` (no scheme). Use `(parsed.hostname or "")`.
6. "Not written yet." You delete that line and write the function body in its place.

## Chapter 2

1. Accuracy = 392/549 ≈ **0.714**. Precision for phishing: no alarms at all → undefined, reported
   as **0**. Recall = 0/157k = **0**. A 71% model that catches nothing — why accuracy alone is useless here.
2. TP = 485, FN = 15, FP = 60, TN = 440. Precision = 485/545 = **0.890**; recall = 485/500 = **0.970**;
   F1 = 2·0.890·0.970/1.860 = **0.928**. The original (0.941 / 0.950) meets both targets
   (recall ≥ 0.95, precision ≥ 0.90); the new one misses precision by a hair. Ship the original —
   unless the product decision is "catch everything", in which case say so and accept 60 false alarms.
   The point: it is a *decision*, and you can show the table.
3. The test set took part in choosing the threshold, so the score is optimistic — leakage. Choose on
   validation (`choose_threshold` does), report test once.
4. Overfitting (high variance). Set `max_depth` (e.g. 10–20) and `min_samples_leaf` (3–5); grid search
   both; more data also helps.
5. (a) Time: extracting features for 549k rows takes minutes and a 30-fit grid search would take
   hours; (b) balance: the full file is 72/28 and would bias the model; (c) diminishing returns —
   with 20 features, 20k rows already saturate the models (your stage-7 experiment with 2k/10k/20k shows it).

## Chapter 3

1. scheme `http`; host `secure-bankhapoalim.co.il.account-update.top`; TLD `top`; domain
   `account-update`; subdomains `[secure-bankhapoalim, co, il]`; path `/login`; query `id=7731`.
   Owner: whoever registered **account-update.top** — not the bank.
2. `url_length` 42 · `host_length` 12 (`203.0.113.55`) · `path_length` 12 (`/prize/claim`) ·
   `num_dots` 4 · `num_hyphens` 0 · `num_underscores` 0 · `num_slashes` 2 · `num_digits` 9 ·
   `digit_ratio` 0.214 · `num_subdomains` 0 (IP host) · `num_query_params` 0 · `has_ip_host` 1 ·
   `has_at_symbol` 1 · `has_https` 0 · `has_port` 0 · `suspicious_word_count` 1 (`prize`) ·
   `suspicious_tld` 0 (no TLD) · `is_shortener` 0 · `entropy` 4.31 · `brand_in_subdomain` 0 —
   note: "amazon" sits *before* the `@` (the user-info part), which our subdomain feature does not
   see; `has_at_symbol` catches this case instead. A "brand in user-info" feature would be a fine addition.
3. `"aabb"`: p(a)=p(b)=½ → H = **1.0**. `"abcd"`: four × ¼ → H = **2.0**.
4. The scheme is what the browser uses; searching the string would give 1 for
   `http://evil.com/https-secure-login` — no TLS at all — and miss the point. Scheme: 0. String search: 1.
5. E.g. `digits_in_domain` (count digits in the *domain label only* — `paypa1` → 1, `google.com` → 0);
   or `min_edit_distance_to_brand` (Levenshtein `paypa1`↔`paypal` = 1 → flag when 1–2 and not 0).
   Compute from `parsed.domain`, add to `FEATURE_NAMES`, test, retrain.
6. "Skew is when the numbers the model learned from are computed differently from the numbers it
   gets in the app. If training counted dots in the whole URL and the app counts dots in the host,
   `num_dots` is systematically smaller in the app, so the model thinks every URL is simpler than it
   is — and confidently under-detects, with no error. We prevent it with one extractor class for both
   and a feature-name check when loading the model."

## Chapter 4

1. z = 0 + 0 − 0 + 0.05·1 − 1.0 = −0.95 → p = 1/(1+e^0.95) = 1/(1+2.586) = **0.28** → *legitimate*
   at 0.5. The tiny model has no `is_shortener` weight, so it misses it — a good illustration of why
   the feature exists.
2. p = 0.30, truth 1: loss = −ln 0.30 = **1.20**. p = 0.95: −ln 0.95 = **0.05**. Twenty-four times
   larger: the loss grows sharply as confidence in the wrong direction grows — and a wrong 0.30 is
   penalized much more than a right 0.95 is rewarded.
3. Gradient = (p − y)·x_i = (p − y)·0 = **0** → no change. Sensible: a feature that was absent gave
   no evidence for this URL, so it earns neither blame nor credit.
4. Root Gini = 1 − (0.8² + 0.2²) = 1 − 0.68 = **0.32**. Split: group 1 = 2 bad → 0; group 2 = 8 good → 0;
   weighted = **0**; gain = **0.32** — a perfect split.
5. It keeps asking questions until every leaf holds rows of one class — it can always find *some*
   feature threshold that separates the last few rows, i.e. it memorizes. Bad because those last
   splits describe noise, not phishing; on new URLs they mislead (high variance).
6. 3 values × 5 folds = 15 fits + 1 final refit on all training data = **16**.
7. An interaction. `http://a.b.c.d.example.com/x` (no HTTPS, 4 subdomains) may be phishing while
   `https://a.b.c.d.example.com/x` is a normal CDN path; the forest can learn "many subdomains matter
   *when* HTTPS is absent"; logistic regression adds the two effects independently and cannot condition one on the other.

## Chapter 5

1. Precision = 1380/(1380+25) = **0.982**; recall = 1380/1500 = **0.920**. ✓
2. F1 is highest at **0.50** (0.961). The rule also picks **0.50** here (0.70 fails recall; 0.50 is the
   highest that passes). They can differ in general: F1 weighs precision and recall equally; our rule
   fixes recall first and then minimizes false alarms — a different objective, chosen on purpose.
3. Not bad — the *ranking* is excellent (AUC 0.99); the cut-off is wrong. Lower the threshold
   (`choose_threshold` on validation) and recall will rise with little precision loss.
4. No. On training data even an overfitted model looks perfect. ROC/AUC, like every reported number,
   must come from validation (for choosing) or test (for reporting).
5. FP: `https://shop.example.com/track?order=8827361&sid=a8f7d6e5c4b3a2f1&utm=…` — long, digit-heavy,
   many parameters: `url_length`, `digit_ratio`, `num_query_params`, `entropy` are fooled although the
   domain is fine. FN: `https://blog-of-a-real-school.edu/wp-content/login.php` — a hacked legitimate
   site: `has_https`=1, common TLD, few dots, one suspicious word; the structure looks fine.
6. Data: ≥ 30 phishing URLs verified on PhishTank *this week* plus ≥ 30 fresh legitimate URLs.
   Metric: recall on the new phishing (and precision on the new legitimate). Drift is confirmed if
   recall drops clearly below the test-set value (e.g. 0.95 → under 0.85) — a drop bigger than what
   30-sample noise explains. Then inspect the misses: which new tricks appear?

## Chapter 6

1. `ModelBundle.load` compares the stored 20 names with the extractor's 21 and raises
   `RuntimeError("model was trained with different features - retrain")` at startup — before any
   prediction. Good because the alternative is silent, confident, wrong verdicts.
2. The scaler is gone: raw features go into a classifier trained on scaled ones → nonsense
   probabilities. The threshold and the feature order are lost too. That is why the *bundle* exists.
3. `True` (Singleton). `False` (ordinary class; a new object per call).
4. With `?`: the quote is just data; the row is stored. Without: the SQL statement breaks on the
   quote (syntax error) — and a crafted URL could inject SQL.
5. Mean and std are *learned parameters*. Fitting on all data lets the test rows shape the scaling
   the model is trained with — a small leak, but a leak; and cross-validation folds would each see
   the others' statistics. Fit on train only; the Pipeline enforces it.
6. Change: `trainer.py` (`build_boosting`, its grid, `train`), maybe `config.py`. Unchanged:
   `evaluator.py` (`importances` already handles `feature_importances_`), `explainer.py` (branches on
   `hasattr`), `bundle.py`, `predictor.py`, views, database. If you had to touch the predictor — the
   architecture is leaking.
