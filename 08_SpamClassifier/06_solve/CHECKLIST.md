# SpamClassifier — the full checklist

Every function you still have to write in your skeleton: **99**, in the order of `TASKS.md`.
Tick each box when its tests are green. The text after each name is the first line of its TODO —
the full instructions are in the docstring in your code. `HINTS.md` (next to this file) helps with the hard ones.

Generated from your skeleton by `tools/make_checklists.py` — do not edit by hand.

## Stage 1 — Data and splitting

**`spamclassifier/ml/dataset.py`**

- [ ] `load_corpus(path)` — read the CSV, return (texts, labels).
- [ ] `class_balance(labels)` — {"ham": n, "spam": n, "spam_ratio": float}.  
  ✅ checked by `tests/test_dataset.py`
- [ ] `stratified_split(texts, labels, seed)` — split 70 / 15 / 15, preserving the class ratio in each part.  
  ✅ checked by `tests/test_dataset.py`
- [ ] `assert_no_leakage(split)` — raise AssertionError if any text appears in two splits.  
  ✅ checked by `tests/test_dataset.py`

> **Exit condition:** `pytest tests/test_dataset.py -v` green. Print the class balance and say out loud what the spam ratio is — if it is far from ~13%, find out why before writing another line.

## Stage 2 — Cleaning and tokenizing

**`spamclassifier/preprocessing/email_parser.py`**

- [ ] `EmailParser.parse(raw)` — run the seven steps above, in that order, and return a CleanedMessage.  
  ✅ checked by `tests/test_email_parser.py`
- [ ] `EmailParser.truncate(raw)` — return at most config.MAX_INPUT_CHARS characters.  
  ✅ checked by `tests/test_email_parser.py`
- [ ] `EmailParser.split_headers(raw)` — return (subject, body).  
  ✅ checked by `tests/test_email_parser.py`
- [ ] `EmailParser.strip_html(text)` — remove every <...> tag, leaving the text between them.  
  ✅ checked by `tests/test_email_parser.py`
- [ ] `EmailParser.replace_urls(text)` — replace every URL with config.URL_TOKEN.  
  ✅ checked by `tests/test_email_parser.py`
- [ ] `EmailParser.caps_ratio(text)` — uppercase letters / all letters, in [0, 1].  
  ✅ checked by `tests/test_email_parser.py`
- [ ] `EmailParser.exclamation_count(text)` — how many "!" characters the text contains.  
  ✅ checked by `tests/test_email_parser.py`
- [ ] `EmailParser.digit_ratio(text)` — digits / all characters, in [0, 1]. Empty string -> 0.0.  
  ✅ checked by `tests/test_email_parser.py`
- [ ] `EmailParser.count_urls(text)` — how many URLs appear, using URL_RE.  
  ✅ checked by `tests/test_email_parser.py`
- [ ] `EmailParser.count_html_tags(text)` — how many <...> tags appear.  
  ✅ checked by `tests/test_email_parser.py`

**`spamclassifier/preprocessing/tokenizer.py`**

- [ ] `load_stopwords()` — return the NLTK English stop-word set.
- [ ] `Tokenizer.tokenize(message)` — tokenize message.text and apply the four rules above.  
  ✅ checked by `tests/test_pipeline.py`, `tests/test_tokenizer.py`
- [ ] `Tokenizer.tokenize_text(text)` — the same thing for a bare string.  
  ✅ checked by `tests/test_tokenizer.py`
- [ ] `Tokenizer._keep(token)` — True if the token survives filtering.

> **Exit condition:** `pytest tests/test_email_parser.py tests/test_tokenizer.py -v` green. Clean five messages by hand and check the output word by word. `test_parse_measures_caps_before_lowercasing` is the one that matters — if it fails, the ordering is wrong and a real signal is being destroyed.

## Stage 3 — Features

**`spamclassifier/features/feature_engineer.py`**

- [ ] `FeatureEngineer.fit(messages)` — build the vocabulary and the IDF table.  
  ✅ checked by `tests/test_feature_engineer.py`, `tests/test_pipeline.py`
- [ ] `FeatureEngineer.transform(message)` — turn one message into a FeatureVector.  
  ✅ checked by `tests/test_feature_engineer.py`, `tests/test_pipeline.py`
- [ ] `FeatureEngineer.handcrafted(message)` — the seven numbers, keyed by config.HANDCRAFTED_FEATURES.  
  ✅ checked by `tests/test_feature_engineer.py`
- [ ] `FeatureEngineer.l2_normalise(vector)` — divide every value by the Euclidean norm.  
  ✅ checked by `tests/test_feature_engineer.py`
- [ ] `FeatureEngineer.idf_value(n_documents, document_frequency)` — log(N / (1 + df)) + 1.  
  ✅ checked by `tests/test_feature_engineer.py`
- [ ] `FeatureEngineer.to_dense(vector)` — flatten to a plain list, vocabulary order first, then handcrafted in config.HANDCRAFTED_FEATURES order.  
  ✅ checked by `tests/test_feature_engineer.py`, `tests/test_pipeline.py`

**`spamclassifier/preprocessing/tokenizer.py`**

- [ ] `ngrams(tokens, n_min, n_max)` — every n-gram with n_min <= n <= n_max, joined by a space.  
  ✅ checked by `tests/test_tokenizer.py`

> **Exit condition:** `pytest tests/test_feature_engineer.py -v` green. Print the 20 highest-IDF and 20 lowest-IDF terms and explain why each group is where it is. You should be able to defend `fit(train only)` in one sentence.

## Stage 4 — Naive Bayes, from scratch (the heart of the project)

**`spamclassifier/ml/naive_bayes.py`**

- [ ] `NaiveBayesClassifier.fit(documents, labels)` — count, smooth, take logs, store.  
  ✅ checked by `tests/test_naive_bayes.py`, `tests/test_pipeline.py`
- [ ] `NaiveBayesClassifier.predict_log_scores(tokens)` — the log score of each class for one document.  
  ✅ checked by `tests/test_naive_bayes.py`
- [ ] `NaiveBayesClassifier.predict_proba(tokens)` — P(spam) in [0, 1].  
  ✅ checked by `tests/test_naive_bayes.py`, `tests/test_pipeline.py`
- [ ] `NaiveBayesClassifier.predict(tokens, threshold)` — SPAM if predict_proba >= threshold, else HAM.  
  ✅ checked by `tests/test_naive_bayes.py`
- [ ] `NaiveBayesClassifier.log_odds(token)` — log P(token|spam) - log P(token|ham).  
  ✅ checked by `tests/test_naive_bayes.py`
- [ ] `NaiveBayesClassifier.explain(tokens, top_n)` — the top_n tokens with the largest |log_odds|.  
  ✅ checked by `tests/test_naive_bayes.py`, `tests/test_pipeline.py`
- [ ] `NaiveBayesClassifier.most_discriminative(top_n)` — the top_n vocabulary entries by |log_odds|, descending.  
  ✅ checked by `tests/test_naive_bayes.py`

> **Exit condition:** `pytest tests/test_naive_bayes.py -v` all green — especially `test_matches_sklearn` (agreement to 1e-9) and `test_no_underflow_on_long_document`. If the first fails, the counting or the smoothing is wrong. If the second fails, you left log space too early. Before moving on: write out Bayes' theorem on paper and point at the line of your code that implements each part of it.

## Stage 5 — SVM and comparison

**`spamclassifier/ml/comparator.py`**

- [ ] `ModelComparator.cross_validate(model_factory, texts, labels)` — stratified k-fold, returning mean and std per metric.
- [ ] `ModelComparator.compare(results_a, results_b)` — per metric, say which model wins, or that neither does.
- [ ] `ModelComparator.confusion_matrix(predictions, labels)` — the four counts. Mind the order of the middle two.

**`spamclassifier/ml/svm_classifier.py`**

- [ ] `SVMClassifier.fit(vectors, labels)` — fit a calibrated LinearSVC.
- [ ] `SVMClassifier.predict_proba(vector)` — P(spam) for one dense vector, in [0, 1].
- [ ] `SVMClassifier.predict(vector, threshold)` — 1 if predict_proba >= threshold else 0.
- [ ] `SVMClassifier.explain(vector, feature_names, top_n)` — (optional): approximate reasons from the linear coefficients - coef[i] * value[i], largest absolute first.

> **Exit condition:** both models cross-validated over the same 5 folds, with mean and standard deviation printed for precision, recall and F1. Be ready to say which model won — or that the gap is smaller than the spread and neither did.

## Stage 6 — Threshold and bundle

**`spamclassifier/ml/bundle.py`**

- [ ] `ModelBundle.new_version()` — a version id like '2026-03-11-a'.
- [ ] `ModelBundle.save(vectorizer, nb_model, svm_model, threshold_choice, metrics, feature_names)` — write all eight files, checksum last.
- [ ] `ModelBundle.load()` — verify, then load.
- [ ] `ModelBundle.compute_checksum()` — SHA-256 over the seven files, in sorted name order.
- [ ] `ModelBundle.verify()` — True if files are present and checksums match.
- [ ] `ModelBundle.verify_feature_contract(feature_names)` — raise ValueError if the stored handcrafted names differ from config.HANDCRAFTED_FEATURES in content or in order.
- [ ] `ModelBundle.latest_version()` — newest verifying bundle in models/, or None.

**`spamclassifier/ml/naive_bayes.py`**

- [ ] `NaiveBayesClassifier.to_dict()` — plain dict for the bundle - priors, likelihoods, vocab, alpha.  
  ✅ checked by `tests/test_naive_bayes.py`
- [ ] `NaiveBayesClassifier.from_dict(data)` — rebuild a fitted classifier from to_dict output.  
  ✅ checked by `tests/test_naive_bayes.py`

**`spamclassifier/ml/svm_classifier.py`**

- [ ] `SVMClassifier.to_dict()` — picklable state for the bundle.
- [ ] `SVMClassifier.from_dict(data)` — rebuild from to_dict output.

**`spamclassifier/ml/threshold.py`**

- [ ] `confusion_at(probabilities, labels, threshold)` — count the four cells at this threshold.  
  ✅ checked by `tests/test_threshold.py`
- [ ] `choose_threshold(probabilities, labels, min_precision)` — the best threshold meeting the precision floor.  
  ✅ checked by `tests/test_threshold.py`
- [ ] `precision_recall_curve(probabilities, labels)` — (thresholds, precisions, recalls) over the search range.

> **Exit condition:** `pytest tests/test_threshold.py -v` green. A bundle saves and loads. Corrupt one byte of a `.pkl` by hand and confirm the load is refused — if it is not, the checksum is not doing its job.

## Stage 7 — Database, UI and the explanation

**`run.py`**

- [ ] `main()` — wire everything together and open the window.

**`spamclassifier/database/db.py`**

- [ ] `connect(path)` — open a connection and prepare it.
- [ ] `initialise(conn)` — executescript(SCHEMA) and commit. Safe to call repeatedly.

**`spamclassifier/database/repositories.py`**

- [ ] `ScanRepository.save(verdict, subject, body)` — insert one scan, return its new id.
- [ ] `ScanRepository.recent(limit)` — the newest `limit` scans, newest first.
- [ ] `ScanRepository.get(scan_id)` — one scan by id, or None.
- [ ] `ScanRepository.count_by_verdict()` — {"ham": n, "spam": n} via GROUP BY.
- [ ] `FeedbackRepository.submit(scan_id, correct_label)` — record that a verdict was wrong, return the new id.
- [ ] `FeedbackRepository.pending()` — (body_excerpt, correct_label) for unused feedback.
- [ ] `FeedbackRepository.mark_used(training_run_id)` — mark all pending rows as used by this run; return the count.
- [ ] `FeedbackRepository.false_positive_count()` — scans marked spam that the user says were ham.
- [ ] `TrainingRepository.start_run(model_version, n_samples, n_feedback, threshold, notes)` — insert a training_runs row, return its id.
- [ ] `TrainingRepository.save_metrics(run_id, results)` — insert one metrics row per MetricResult (executemany).
- [ ] `TrainingRepository.save_vocabulary(run_id, entries)` — bulk-insert the most discriminative tokens.
- [ ] `TrainingRepository.latest_metrics()` — every metric from the most recent run.
- [ ] `TrainingRepository.runs(limit)` — recent training runs, newest first - the history panel.

**`spamclassifier/ml/explainer.py`**

- [ ] `Explainer.reasons_for(tokens, top_n)` — delegate to the classifier's explain().
- [ ] `Explainer.to_sentence(reasons, verdict)` — one readable line.
- [ ] `Explainer.format_weight(weight)` — a short human label for a log-odds weight.

**`spamclassifier/presenters/app_presenter.py`**

- [ ] `AppPresenter.check_message(raw_text, model_name)` — classify one message, store it, return the verdict.
- [ ] `AppPresenter.submit_feedback(correct_label)` — record that the last verdict was wrong.
- [ ] `AppPresenter.recent_scans(limit)` — hand the history table its rows.
- [ ] `AppPresenter.pending_feedback_count()` — how many corrections are waiting. Shown on the button.
- [ ] `AppPresenter.retrain(progress)` — retrain on the corpus plus the pending feedback.
- [ ] `AppPresenter.comparison_metrics()` — both models' metrics from the latest run.
- [ ] `AppPresenter.comparison_summary()` — per metric, which model won - or that neither did.
- [ ] `AppPresenter.most_discriminative_words(top_n)` — the words the model found most decisive, for display.
- [ ] `AppPresenter.format_verdict(verdict)` — a dict of display strings.

**`spamclassifier/spam_filter.py`**

- [ ] `SpamFilter.from_bundle(version)` — build a SpamFilter from a saved bundle.
- [ ] `SpamFilter.classify(raw_text, model_name)` — the full pipeline, returning a Verdict.

**`spamclassifier/views/check_view.py`**

- [ ] `CheckView.build()` — lay out the widgets.
- [ ] `CheckView.on_check()` — read the box, call presenter.check_message, display it.
- [ ] `CheckView.on_mark_wrong()` — call submit_feedback with the opposite label, confirm it.
- [ ] `CheckView.display_verdict(formatted)` — fill the banner and the reasons list.
- [ ] `CheckView.refresh_history()` — reload the Treeview from presenter.recent_scans().

**`spamclassifier/views/compare_view.py`**

- [ ] `CompareView.build()` — a metrics table: metric, NB (mean ± std), SVM (mean ± std), winner - two confusion matrices side by side - a precision-recall curve for both models on one set of axes - a marker on the curve at the chosen threshold -...
- [ ] `CompareView.draw_curves()` — embed the Matplotlib figure.
- [ ] `CompareView.refresh()` — reload everything from the latest training run.

**`spamclassifier/views/main_window.py`**

- [ ] `MainWindow.build()` — create the notebook and add the three tabs.
- [ ] `MainWindow.run()` — build() then mainloop().
- [ ] `MainWindow.show_error(message)` — messagebox.showerror. The only error path in the UI.

**`spamclassifier/views/train_view.py`**

- [ ] `TrainView.build()` — a label: "N corrections waiting" - "Retrain now", disabled when N is 0 - a scrolling progress log - a table of past runs: version, date, samples, threshold, F1 - after a run, the metric deltas against the previous ver...
- [ ] `TrainView.on_retrain()` — run the retrain, streaming progress into the log.
- [ ] `TrainView.append_log(line)` — append a line and scroll to the bottom.

> **Exit condition:** `pytest -v` fully green, including `tests/test_pipeline.py`. The application opens, classifies a pasted message, shows the reasons, and records the scan. Mark a verdict wrong and confirm it appears in the pending-feedback count.

## Stage 8 — Train, measure, write

**`evaluate.py`**

- [ ] `main()` — load the bundle, score the test split, print the report.

**`train.py`**

- [ ] `main()` — the full training run.

> **Exit condition:** `reports/evaluation.md` exists and every target in the proposal has a measured number next to it. A target you missed is written down as missed and discussed — targets are never edited afterwards to match the result.
