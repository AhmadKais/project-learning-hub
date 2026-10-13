# Chapter 3 — The data, and what "similar" means

💡 **In short:** 6,497 wines, 1,177 of them exact copies that must go before any split. The features live on wildly different scales, so without scaling k-NN measures one feature and ignores the rest. Scaling is learned — from training rows only.

## 3.1 The dataset

UCI Wine Quality (Cortez et al., 2009): Portuguese "Vinho Verde" wines, 1,599 red and 4,898 white. Each has 11 lab measurements and a quality score from 0 to 10, the median of at least three tasters.

| Feature | Unit | Typical range |
|---|---|---|
| fixed acidity | g/L | 4 – 16 |
| volatile acidity | g/L | 0.1 – 1.6 |
| citric acid | g/L | 0 – 1.7 |
| residual sugar | g/L | 0.6 – 66 |
| chlorides | g/L | 0.01 – 0.6 |
| free sulfur dioxide | mg/L | 1 – 289 |
| total sulfur dioxide | mg/L | 6 – 440 |
| density | g/cm³ | 0.987 – 1.039 |
| pH | — | 2.7 – 4.0 |
| sulphates | g/L | 0.2 – 2.0 |
| alcohol | % vol | 8 – 15 |

The colour becomes a twelfth feature, `is_red` (1 or 0), because red and white come in separate files.

## 3.2 From scores to three grades

| Score | Grade | Share (after duplicates) |
|---|---|---|
| 3, 4, 5 | low | 37.4% |
| 6 | medium | 43.7% |
| 7, 8, 9 | high | 19.0% |

Why not seven classes? Scores 3 and 9 have a handful of wines each — five wines of score 9 in the whole dataset. No method learns a class from five examples, and a 3-class answer is what a wine maker actually needs.

## 3.3 Checking every value

A file from the internet is input like any other, and `validate_values` checks every wine: twelve values, all finite numbers, each inside a physically possible range (pH between 0 and 14, concentrations not negative), `is_red` exactly 0 or 1.

A bad line is **rejected and reported with its line number**, not fatal and not silently skipped. One typo in five thousand lines is normal; crashing on it is wrong, and dropping it without telling anyone is worse — you would never know the file was damaged.

The same function checks the lab station's form, so a user who types pH 15 sees the same message a broken file would produce.

## 3.4 The duplicate trap

1,177 rows of the dataset are exact copies of other rows — the same twelve measurements and the same score. Leave them in, split into folds at random, and many copies end up with one twin in training and the other in testing.

For k-NN that is fatal in a specific way: the test wine's nearest neighbour is its own twin, at distance **zero**, with the right answer. The model "predicts" perfectly by looking the answer up. The score goes up and nothing was learned.

So `drop_exact_duplicates` runs before any split, and the number dropped is reported. The database keeps the copies, marked with `dup_of`, because the count is a finding for the book.

❓ **Why remove duplicates before splitting, not after?**

After splitting it is too late: a copy in the training set and its twin in the test set are both "unique" within their own part. Only by removing them from the whole dataset first can you guarantee that no wine is tested against its own copy.

## 3.5 Why scaling is not optional

Take two wines that differ by 0.03 g/L of chlorides — a big difference, a whole standard deviation — and by 4 mg/L of total sulfur dioxide, a tiny one. The Euclidean distance between them is about √(0.03² + 4²) ≈ 4.0. The chlorides difference contributes nothing. With raw values, "nearest wine" means "wine with the most similar sulfur dioxide", whatever the other eleven features say.

The measured cost on the real data, k-NN with k = 15:

| Scaling | macro-F1 |
|---|---|
| none | 0.45 |
| z-score | 0.58 |

That table is in your evaluation report as the `knn-unscaled` row. It is the first result of the project and the clearest one.

## 3.6 z-score

For each feature, subtract its mean and divide by its standard deviation:

    z = (x − mean) / std

Now every feature has mean 0 and standard deviation 1, and "one unit" means "one typical difference" for every feature. A constant feature would divide by zero, so its std is set to 1 (the column becomes all zeros and drops out of every distance — correct, it carries no information).

## 3.7 min-max

Map each feature so the training rows run from 0 to 1:

    z = (x − min) / (max − min)

Simple, but one extreme wine controls the whole scale. Total sulfur dioxide reaches 440 in one wine; most are between 50 and 200. min-max squeezes all of them into the bottom third of the range. z-score is hurt far less, and `test_one_outlier_squeezes_minmax_but_not_zscore` shows it with a number. Both are in the hyper-parameter search; the tuning table decides.

## 3.8 The rule that matters

The mean and standard deviation are **learned from data**, so they are model parameters, and they must be learned from the **training rows only**. Then the same numbers transform both training and test rows.

📄 **Right and wrong**
```python
# RIGHT - inside each fold
scaler = StandardScaler().fit(X[train])
Xtr = scaler.transform(X[train])
Xte = scaler.transform(X[test])        # test rows use the TRAINING mean and std

# WRONG - leaks the test rows' statistics into the model
Z = StandardScaler().fit_transform(X)
Xtr, Xte = Z[train], Z[test]
```

The leak is small — means change a little — but it is a leak, and an examiner will ask. `test_fit_uses_only_given_rows` and `test_prepare_folds_scales_with_training_rows_only` exist to catch it.

❓ **At the lab station a single new wine arrives. Which mean and std do you use to scale it?**

The ones saved in the bundle from training — never a new scaler fitted on the new wine or the lab's recent wines. The training wines live in the coordinate system those numbers define; a new wine must be placed in the same one, or every distance to them is meaningless.
