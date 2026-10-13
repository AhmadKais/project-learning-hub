# Part C — Pass the exam

# Chapter 17 — Question and answer bank

Point at the file and the line when you answer. "In `evaluator.py`, `choose_threshold`, the loop over
0.05–0.95" beats any definition.

## 17.1 The problem

**1. What does the system do?** Decides from the structure of a URL alone — no visit, no blacklist —
whether it is phishing, with a probability and the reasons, using models trained on ~20,000 labelled URLs.

**2. What is phishing?** A fake site pretending to be a trusted one to steal credentials, reached
through a disguised link.

**3. Why not a blacklist?** Most phishing sites live under a day; a list is always behind. A model
generalizes to URLs it never saw.

**4. Why URL-only?** Fast (< 10 ms), safe (never loads the page), works before the click. The limit:
it cannot see page content — a phishing page on a hijacked good domain looks fine. Declared limitation.

**5. Where does the data come from?** Kaggle "Phishing Site URLs", ~549k rows, `good`/`bad`; balanced
sample of 10k per class.

## 17.2 Features

**6. What is a feature?** One number describing a URL — length, dots, HTTPS…

**7. Name eight features and the attacker trick each catches.** [Table in chapter 3.1.]

**8. How do you find the real domain in `paypal.com.secure-login.xyz`?** Read from the right: TLD
`xyz`, domain `secure-login`, everything else is subdomains chosen by the attacker.

**9. What does `@` do in a URL?** The browser treats everything before it as a username and goes to
what is after it — `amazon.com@203.0.113.55` goes to the IP.

**10. What is entropy and why is it a feature?** Randomness of the characters, `−Σ p log₂ p`.
Auto-generated paths are random; human paths are words.

**11. What is train/serve skew and how do you prevent it?** Different feature code in training and
scanning. One extractor class for both; feature names stored in the bundle and verified on load.

**12. Which features differed most between classes in your data?** [From `feature_means.csv`.]

**13. How would you add a new feature?** Add the name to `FEATURE_NAMES`, compute it in `extract`,
add a test, retrain. The bundle check forces the retrain.

**14. What does the extractor do with garbage input?** The parser returns empty fields instead of
raising; every feature still comes out as a number; the model gives a (probably high) probability.

## 17.3 Machine learning basics

**15. Rules vs. learning?** Rules are written by hand and break; learning finds weights from examples.

**16. Supervised, binary classification — meaning?** Labelled examples; two classes.

**17. Train / validation / test — roles?** Learn / choose settings and threshold / final score, once.

**18. What is leakage? Give your example.** Test data influencing a decision — e.g. choosing the
threshold on the test set, or fitting the scaler on all data.

**19. Overfitting — how did you see it and fix it?** Forest at unlimited depth: train 1.00, val 0.95;
`max_depth`/`min_samples_leaf` via grid search.

**20. Why balance the classes?** 72/28 teaches "say good". Balanced sample + `class_weight="balanced"`.

**21. Precision vs. recall — which matters more here and why?** Recall for phishing: a miss costs an
account, a false alarm costs seconds. Target recall ≥ 0.95.

**22. Draw the confusion matrix and define the four cells.** [Chapter 2.4.]

**23. What is F1?** Harmonic mean of precision and recall; punishes imbalance between them.

**24. What is AUC?** Area under the ROC curve; threshold-free comparison; 0.5 random, 1 perfect.

## 17.4 The models

**25. Explain logistic regression in one minute.** Weighted sum of features + bias, through a sigmoid
→ probability. Weights learned by minimizing log-loss with gradient descent.

**26. What is the sigmoid?** `1/(1+e^−z)`; maps any number to (0,1).

**27. What is log-loss?** `−ln p` for a true positive, `−ln(1−p)` for a true negative. Confident-and-wrong is punished hard.

**28. What is gradient descent?** Move each weight against its gradient; here gradient = `(p − y)·x`.

**29. Why scale the features and why inside a Pipeline?** Features on different scales make weights
incomparable and training slow. The scaler is fitted on train only and must be saved with the model.

**30. What is `C`?** Inverse regularization strength; small `C` = simpler model.

**31. How does a decision tree choose a split?** The feature/threshold that most reduces Gini impurity. [Worked example 4.5.]

**32. Why does a single tree overfit?** Grown to purity it memorizes every training row.

**33. What is a random forest?** Many trees on bootstrap samples with random feature subsets; majority vote. Lower variance.

**34. What is feature importance?** Total impurity reduction attributed to each feature across all trees.

**35. Which model won and why?** [Your numbers.] Typically the forest by 1–2 F1 points; logistic explains better.

**36. What can the forest learn that logistic cannot?** Interactions: "dots matter only without HTTPS".

**37. What is cross-validation?** k-fold: train on k−1 parts, score on the k-th, rotate, average. For choosing settings.

**38. What is grid search and how many fits did yours run?** Every combination × k folds + refit. [Your count.]

**39. Why `class_weight="balanced"` if the sample is already balanced?** Belt and braces — harmless
when balanced, protective if the sample sizes ever differ.

## 17.5 Evaluation and threshold

**40. Why isn't the threshold 0.5?** Chosen on validation as the highest value with recall ≥ 0.95;
0.5 assumes equal costs. [Your value.]

**41. How would raising the threshold change precision and recall?** Precision up, recall down.

**42. What were your worst mistakes and why?** [From `worst_mistakes` — e.g. long legitimate tracking
URLs; short phishing on hijacked domains.]

**43. What is concept drift and did you measure it?** Attackers change; the model ages. [Your drift test result.]

**44. What is calibration?** Whether "80%" is right ~80% of the time. Logistic regression is usually
well calibrated; forests less so.

**45. Your final numbers?** [Precision, recall, F1, AUC on test; training time; scan time.]

## 17.6 Explanation

**46. How does the explanation work for logistic regression?** `weight × scaled value` per feature,
signed; top 3 toward the verdict.

**47. And for the forest?** Global importance × sign of the scaled value — an approximation; stated honestly.

**48. Why explain at all?** Trust and education: the user learns to spot the trick; and it exposes model errors.

## 17.7 Architecture and code

**49. Patterns used and where?** Pipeline, single-source extractor, Singleton (`Predictor`, `Database`),
Repository, MVC, Strategy-light in `Explainer`, Bundle value object.

**50. What is in the bundle and why together?** Pipeline (scaler + clf), feature names, threshold,
metrics, version. Separated, they silently disagree.

**51. What does `ModelBundle.load` verify?** Feature names equal the extractor's; else `RuntimeError`.

**52. MVC boundary?** Views import no sklearn/SQL; ML/DB import no tkinter; the controller joins them.

**53. Why Singleton for `Predictor`?** Load once. Downside: test isolation — reset in `conftest.py`.

**54. Repository — why?** SQL in one file; the rest uses objects; DB swap = one file.

**55. Describe the schema.** `scans` (url, time, probability, verdict, threshold, features JSON,
model_version, feedback), `models` (version, metrics, threshold). Indexes on time and verdict.

**56. Why no foreign key from scans to models?** History must survive deleting a model; a version string is enough.

**57. SQL injection — how prevented?** `?` placeholders only.

**58. What did you test?** Parser (6), extractor (10), dataset (3), pipeline end-to-end (2),
repositories (4) — 25 given + yours. No GUI tests — manual.

**59. `@contextmanager` in `Database.connection`?** Commit on success, rollback on error, close always.

**60. What happens on `run.py` with no model file?** App opens, warns "run train.py", scanning disabled.

## 17.8 Limits, ethics, future

**61. Can the model be fooled?** Yes — attackers can imitate legitimate structure (short URL on a
hacked domain). URL-only is one layer; page content and domain age are the next.

**62. False alarms — who pays?** Legitimate sites flagged; the user learns to ignore warnings if too
many. That is why precision ≥ 0.90 is a target too.

**63. Privacy?** URLs are scanned locally; nothing is sent anywhere; history is a local file the user controls.

**64. What would you build next?** [Two from the proposal's future work, with reasons.]

**65. Hardest bug?** [Yours — from `TASKS.md`.]

## 17.9 Numbers to know from your runs

**66.** Rows used per class. **67.** Test precision / recall / F1 / AUC. **68.** Chosen threshold.
**69.** Training time; scan time. **70.** Number of features. **71.** Top-3 features by importance.
**72.** Drift-test recall. **73.** Grid-search fit count. **74.** Test count and coverage.
**75.** `feature_means` — three biggest class differences.

# Chapter 17a — "Explain your code" drills

Explain every line out loud: what, why, and what breaks without it.

1. `URLParser.parse` — the scheme fix, the TLD rule, the IP branch.
2. `URLFeatureExtractor.extract` — any three features + the final assert.
3. `shannon_entropy` — the formula line by line.
4. `DatasetLoader.load` — the double split and `stratify`.
5. `ModelTrainer.build_logistic` — every argument of the Pipeline.
6. `ModelTrainer.fit_with_search` — what `GridSearchCV` does inside `fit`.
7. `ModelEvaluator.choose_threshold` — why validation, why "highest".
8. `ModelEvaluator.metrics` — the four numbers from the confusion matrix.
9. `ModelBundle.load` — the check and the error.
10. `Predictor.predict` — the five lines.
11. `Explainer.contributions` — the two branches.
12. `Database.connection` — the four steps.

# Chapter 18 — Glossary

| Term | Short explanation |
|---|---|
| Accuracy | Share of correct answers |
| AUC / ROC | Area under the recall-vs-false-alarm curve |
| Balanced sample | Equal rows per class |
| Bias / variance | Too simple / too sensitive to training data |
| Bootstrap | Random sample with replacement (forest) |
| Bundle | Model + scaler + features + threshold in one file |
| Class weight | Extra cost for the rare class |
| Concept drift | The world changes, the model ages |
| Confusion matrix | TP / FP / FN / TN table |
| Cross-validation | Rotate train/score over k folds |
| Entropy | Randomness of characters |
| F1 | Harmonic mean of precision and recall |
| Feature / feature vector | One number describing a URL / all 20 in order |
| Feature engineering | Choosing and computing the features |
| Feature importance | How much a feature reduced impurity in the forest |
| Gini impurity | How mixed a group is (tree split criterion) |
| Gradient descent | Step weights against the gradient |
| Grid search | Try every setting combination with CV |
| Leakage | Test data influencing a decision |
| Log-loss | Loss for probabilities |
| Logistic regression | Linear model + sigmoid |
| Overfitting | Memorizing instead of generalizing |
| Pipeline | Scaler + classifier as one object |
| Precision / recall | Of alarms, correct / of phishing, caught |
| Random forest | Many trees, majority vote |
| Regularization (C) | Brake on large weights |
| Repository | All SQL in one class |
| Scaling | (x − mean) / std per feature |
| Sigmoid | 1 / (1 + e^−z) |
| Singleton | One instance |
| Stratify | Keep class ratio in every split |
| Subdomain / domain / TLD | Left / middle / right parts of a host |
| Threshold | Probability cut-off for the verdict |
| Train / validation / test | Learn / choose / final score |
| Train/serve skew | Different features in training and scanning |
