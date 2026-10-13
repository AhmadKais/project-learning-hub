# Chapter 5 — The SVM, and comparing honestly

💡 **In short:** the SVM looks for the widest gap between the two classes. You use the library version, not your own, because it is the yardstick and a yardstick should be trusted. Then you compare both models on the same folds and report the spread — and if the gap is smaller than the spread, you say so.

## 5.1 What an SVM does

Picture every message as a point in space, one axis per feature. Spam lands in one region, ham in another. An SVM finds the flat surface — a **hyperplane** — that separates them with the widest possible **margin** to the nearest points of either class.

Those nearest points are the **support vectors**, and they are the only ones that matter: move a point deep inside its own region and the boundary does not shift at all. Move a support vector and it does.

The wide margin is what gives the SVM its reputation for generalising well. A boundary squeezed up against the training points is fragile; one sitting in the middle of a gap has room for error.

## 5.2 Generative versus discriminative

This is the conceptual difference worth being able to state, and it is a common exam question.

| | Naive Bayes | SVM |
|---|---|---|
| Type | **generative** | **discriminative** |
| Asks | how does each class produce words? | where is the boundary? |
| Derives the boundary | indirectly, from the two models | directly |
| Explains one decision | yes, exactly | only approximately |
| Training cost | one counting pass | iterative optimisation |

Naive Bayes builds a model of each class and lets the boundary fall out of the comparison. The SVM ignores how the data was produced and goes straight for the dividing line.

Neither is "better" in general. On high-dimensional text, linear SVMs are famously strong (Joachims, 1998). That is exactly why it makes a demanding yardstick.

## 5.3 Why not write this one from scratch too?

Fair question, and the answer is the point of the whole comparison.

The algorithm you *claim to understand* is implemented by hand — that is Naive Bayes, and your defence rests on it. The algorithm used as a **measuring stick** comes from a standard, well-tested implementation, because a yardstick you built yourself proves nothing: if your hand-rolled SVM scored badly, you would never know whether the algorithm or your code was at fault.

Say exactly that if you are asked. It is not an inconsistency, it is the reason the comparison means anything.

## 5.4 Calibration

`LinearSVC` returns a **signed distance** from the hyperplane, not a probability. A distance of 2.3 means "well inside the spam side", but it is not 2.3-anything, and it cannot be compared with Naive Bayes' 0.94.

Platt scaling fits a sigmoid to turn distances into probabilities:

📄 **Stage 5**
```python
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV

base = LinearSVC(C=self.c, random_state=config.RANDOM_SEED)
self._model = CalibratedClassifierCV(base, method="sigmoid", cv=5)
self._model.fit(vectors, labels)
```

Without this there is no shared threshold, no joint precision-recall curve, and no fair comparison — which is the entire purpose of the class.

## 5.5 The C parameter

`C` controls the trade-off between a wide margin and tolerating training errors.

- **small C** — wide margin, more training mistakes allowed, simpler boundary
- **large C** — narrow margin, fewer training mistakes, risk of overfitting

Choose it by grid search **inside** the cross-validation, never on the test set. Tuning on test and then reporting test numbers measures your tuning, not your model.

## 5.6 Comparing fairly

Four rules, and all four are easy to break by accident:

1. **Same folds.** Both models see exactly the same five divisions of the data.
2. **Same features.** One `FeatureEngineer`, both models.
3. **Refit inside every fold.** Including the feature engineer.
4. **Report the spread**, not just the mean.

Rule 3 is the subtle one:

📄 **Wrong — leaks every fold into every other fold**
```python
engineer.fit(all_messages)              # once, outside the loop
for train_idx, test_idx in folds:
    model.fit(...)
```

📄 **Right**
```python
for train_idx, test_idx in folds:
    engineer = FeatureEngineer(tokenizer).fit(messages[train_idx])
    model = model_factory()             # a FRESH model each fold
    model.fit(...)
```

Note `model_factory()` rather than a model instance. Reusing one object across folds leaves it already fitted on data it is about to be tested on.

## 5.7 Reporting the result

📄 **Stage 5: the honesty rule**
```python
def compare(self, results_a, results_b):
    out = {}
    for metric in {r.metric_name for r in results_a}:
        a = next(r for r in results_a if r.metric_name == metric)
        b = next(r for r in results_b if r.metric_name == metric)
        gap = abs(a.mean - b.mean)
        if gap < max(a.std, b.std):
            out[metric] = "no significant difference"
        else:
            winner = a if a.mean > b.mean else b
            out[metric] = f"{winner.model_name} ({a.mean:.3f} vs {b.mean:.3f})"
    return out
```

If the gap between the means is smaller than the larger standard deviation, the honest answer is **no significant difference**.

Suppose you measure:

```
Naive Bayes   F1 = 0.921 ± 0.031
SVM           F1 = 0.907 ± 0.028
```

The gap is 0.014. The spread is 0.031. Naive Bayes did not win — the two are indistinguishable on this data, and claiming otherwise is reading noise.

💡 Saying "there is no significant difference, and here is why" at a defence is a *stronger* answer than claiming a winner. It shows you understand what the numbers can and cannot support. An examiner who sees a confident claim built on a gap smaller than the spread will go straight for it.

❓ **Your SVM scores higher than your Naive Bayes. Is the project a failure?**

No. The comparison is a finding, not a contest your chosen model has to win. Report it, and discuss it: the SVM optimises the boundary directly and often does better on high-dimensional text, while Naive Bayes was chosen as primary for explainability, which was a stated requirement from the start. If the gap is significant, that is a real and interesting result about the cost of requiring explanations — and saying so is exactly what an honest project looks like.

## 5.8 Which curve to plot

Plot **precision-recall** as the main figure, with ROC secondary.

ROC plots true positive rate against false positive rate. With roughly 13% spam, the ham class dominates the false-positive-rate denominator, so even a mediocre classifier produces a flattering ROC curve. Precision-recall does not have that problem because precision has the predicted-positives in its denominator.

Davis and Goadrich (2006), in your bibliography, is the citation if you are asked.

Mark the chosen threshold on the curve. That single point is where the model actually operates, and it makes the next chapter visible.
