# Chapter 7 — Measuring without fooling yourself

💡 **In short:** confusion matrix → precision, recall, F1 per grade → macro-F1. Stratified folds keep the grade mix in every fold. Nested cross-validation keeps the test folds out of every decision. Report the mean and the spread, every time.

## 7.1 The confusion matrix

Rows are the true grade, columns the predicted grade. `cm[true][pred]` counts the wines.

📄 **An example**
```
                 predicted
              low  medium  high
true  low      1      1      0
      medium   1      3      0
      high     0      1      3
```

The diagonal is the correct answers: 7 of 10. Off the diagonal, the *kind* of mistake: here no low wine was called high or the reverse — the model only confuses neighbouring grades, which is the gentle kind of error.

## 7.2 Precision, recall, F1

For each grade:

- **precision** = of the wines *called* this grade, how many were? (diagonal ÷ column sum)
- **recall** = of the wines that *were* this grade, how many were found? (diagonal ÷ row sum)
- **F1** = 2·P·R / (P + R) — high only when both are high

In the example, for "high": precision 3/3 = 1.0, recall 3/4 = 0.75, F1 = 0.857.

If a grade is never predicted, its precision is 0/0. The project defines that as 0 — never `nan` — exactly as scikit-learn does with `zero_division=0`.

## 7.3 Macro-F1

The plain average of the three F1 values. "Plain" matters: the high class, with 19% of the wines, counts exactly as much as medium with 44%. A model that ignores the high class cannot hide behind a good score on medium.

| Model | Accuracy | Macro-F1 |
|---|---|---|
| always medium | 0.44 | 0.20 |
| k-NN | 0.59 | 0.58 |

## 7.4 Cross-validation

One random 80/20 split gives one number, and a different random split gives a different one. With 5-fold cross-validation the data is cut into 5 parts; each part is the test set once while the other 4 train. Every wine is tested exactly once, and you get 5 numbers — so you can report a mean **and** a standard deviation.

Always report both. "0.583 against 0.579" means nothing when the folds themselves disagree by 0.018.

## 7.5 Stratified folds

Plain k-fold shuffles and cuts. By bad luck one fold can get far fewer high-quality wines than the others, and its F1 then measures the cut, not the model. **Stratified** k-fold deals each grade out separately, like dealing cards:

📄 **stratified_kfold, the core**
```python
rng = np.random.default_rng(seed)
fold_of = np.empty(len(y), dtype=int)
for c in np.unique(y):
    rows = np.flatnonzero(y == c)
    rng.shuffle(rows)
    fold_of[rows] = np.arange(len(rows)) % folds      # 0,1,2,3,4,0,1,...
```

Every fold now has the same mix as the whole dataset, within one wine. `test_folds_keep_the_class_mix` checks ±1%.

## 7.6 The problem nested cross-validation solves

Suppose you try 192 configurations with 5-fold cross-validation and report the score of the best one. That score is optimistic: the configuration was chosen *because* it scored well on exactly those folds. Some of its advantage is real, and some is luck that will not repeat on new wines. You cannot tell which.

## 7.7 Nested cross-validation

Two loops:

- The **outer** loop: 5 folds. Each outer test fold is held out and touched by **nothing** until the very end.
- The **inner** loop: on the outer *training* rows only, a full grid search with 3-fold cross-validation, then weight learning. It produces one configuration and one set of weights.
- That model is scored **once** on the outer test fold.

The reported number is the average of the 5 outer scores. Each outer fold may choose different parameters — the book shows them in a table — because what is being evaluated is the whole *procedure* "tune, then learn the weights", not one fixed model.

📄 **The shape of nested_cv**
```python
for train, test in outer_splits:
    inner  = stratified_kfold(y[train], 3)
    tuned  = grid_search(X[train], y[train], inner)
    w      = learn_weights(X[train], y[train], tuned.best, inner).weights
    result = evaluate_split(model_with(tuned.best, w), X, y, train, test, ...)
```

❓ **How do you prove the outer test fold really was never seen?**

`test_nested_never_sees_outer_test` scrambles the labels of the outer test rows and runs the procedure again. If nothing leaks, the parameters and weights chosen in each fold must be **identical** to the clean run — the procedure cannot react to labels it never looked at. Only the final score changes, because it is computed on those labels.

## 7.8 What the report shows

On the real data the inner (optimistic) and outer (honest) scores are very close — 0.585 against 0.583 for uniform weights — which says this tuning is not badly overfitted. For learned weights the gap is a little larger, 0.588 against 0.579: the weights fitted the inner folds a little. Both facts belong in the book.

## 7.9 Leakage — the four guards

| Leak | Guard | Test |
|---|---|---|
| a duplicate wine on both sides | remove duplicates before any split | `test_drop_exact_duplicates_keeps_order_and_counts` |
| scaler fitted on test rows | fit inside each fold, on training rows | `test_prepare_folds_scales_with_training_rows_only` |
| parameters chosen on test rows | nested CV | `test_nested_never_sees_outer_test` |
| looking at the final result and trying again | run `evaluate.py` **once** | your discipline |

The last one has no test. If you run the final evaluation, dislike the number, change something and run it again, the outer folds have become one more validation set, and the honest number is no longer honest.
