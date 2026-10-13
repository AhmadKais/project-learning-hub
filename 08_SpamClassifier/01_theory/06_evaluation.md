# Chapter 6 — Measuring, and choosing the threshold

💡 **In short:** the model gives you a probability; the threshold turns it into a verdict. 0.5 is the wrong default here, because hiding real mail is far worse than letting spam through. You raise the threshold until precision clears a floor, and you report whatever recall that gives you.

## 6.1 The confusion matrix

Four numbers, and the names are worth getting right.

| | predicted ham | predicted spam |
|---|---|---|
| **actually ham** | true ham (TN) | **false spam (FP)** |
| **actually spam** | false ham (FN) | true spam (TP) |

In `entities.py` they are named `true_ham`, `false_spam`, `false_ham`, `true_spam`, in that order — deliberately, so the expensive mistake has a name you cannot misread. `false_spam` is a real message that got hidden.

```
precision = TP / (TP + FP)      of what I called spam, how much really was
recall    = TP / (TP + FN)      of the spam out there, how much I caught
F1        = 2PR / (P + R)
```

❓ **A model marks everything as ham. What are its precision and recall?**

Both are zero: TP = 0, so both fractions are zero. Its *accuracy* is 87%, which is why accuracy is not used in this project. This is the clearest demonstration of why the metric has to match the class balance.

## 6.2 Precision and recall pull against each other

- Lower the threshold → catch more spam (**recall up**), but mislabel more real mail (**precision down**).
- Raise the threshold → fewer real messages hidden (**precision up**), more spam gets through (**recall down**).

You cannot maximise both. You decide which one to constrain, and that decision has to come from the cost of the two mistakes.

## 6.3 The costs are not symmetric

| Mistake | Cost |
|---|---|
| Spam reaches the inbox | one second of annoyance |
| **Real mail hidden** | a missed interview, a missed appointment, a missed deadline |

Not close. So:

- **not** 0.5, which assumes the errors cost the same
- **not** max-F1 either, which also treats them as equal
- instead: require precision ≥ 0.98, and take the best recall available under that constraint

📄 **Stage 6: threshold selection**
```python
def choose_threshold(probabilities, labels, min_precision=None):
    min_precision = min_precision or config.MIN_PRECISION
    best = None
    best_precision_seen = 0.0

    t = config.THRESHOLD_SEARCH_START
    while t <= config.THRESHOLD_SEARCH_STOP:
        m = confusion_at(probabilities, labels, t)
        best_precision_seen = max(best_precision_seen, m.precision)
        if m.precision >= min_precision and (best is None or m.recall > best.recall):
            best = ThresholdChoice(
                threshold=t, precision=m.precision, recall=m.recall,
                rule=f"highest recall subject to precision >= {min_precision}")
        t += config.THRESHOLD_SEARCH_STEP

    if best is None:
        raise ValueError(
            f"no threshold reaches precision {min_precision}; "
            f"best achieved was {best_precision_seen:.3f}")
    return best
```

Note what happens when nothing clears the floor: it **raises**. It does not quietly fall back to 0.5. A model that cannot meet the requirement is a model that is not ready, and hiding that behind a default would mean the UI shows verdicts that nobody ever chose. `test_impossible_floor_raises_rather_than_defaulting` pins this.

## 6.4 Validation only

The threshold is chosen on the **validation** split. The test split stays locked.

Choose it on test, and you have used the test data to make a decision — so the number you then report from that same data is not a measurement of anything. The whole point of a held-out set is that nothing about the model was shaped by it.

`ThresholdChoice` carries a `chosen_on` field that records this, and it gets written into `threshold.json` inside the bundle. Your threshold is a documented decision, not a magic number.

## 6.5 Storing the threshold with every verdict

The `scans` table stores `threshold` next to `probability` on every single row.

This looks redundant until you retrain. Suppose the threshold moves from 0.83 to 0.88. Without the stored value you can no longer explain any past verdict — you know the probability was 0.85, but not whether that counted as spam at the time. With it, every historical decision stays reconstructable, and you can ask how a new threshold *would have* classified old messages.

## 6.6 The success metrics

From the proposal. These go in the project book with a measured number beside each one.

| Metric | Target |
|---|---|
| Precision on spam | ≥ 0.98 |
| Recall on spam | ≥ 0.85 |
| F1 on spam | ≥ 0.90 |
| False positives per 1,000 ham | ≤ 20 |
| Std of F1 across folds | ≤ 0.03 |
| Agreement with scikit-learn | ≤ 1e-9 |
| Time to classify one message | ≤ 50 ms |
| Full training time | ≤ 3 minutes |
| Test coverage of the model layer | ≥ 85% |

💡 A target you missed is written down as missed and discussed in the book. You do not edit the targets afterwards to match what came out — and an examiner who finds that you did will treat it as the most serious problem in the project.

## 6.7 Running the final evaluation

Once. At the end.

```bash
python3 evaluate.py
```

It loads the bundle, rebuilds the test split with the same seed, scores both models, and writes `reports/evaluation.md`.

If you run it, dislike the result, change something and run it again, the test set has quietly become a second validation set. Everything you report from it afterwards is overstated, and you will not be able to tell by how much.

❓ **Why can you only run the final evaluation once?**

Because the test set is only a fair measurement while nothing about the model was influenced by it. The moment you look at the result and change something in response, you have used that data to make a decision, and the next measurement is contaminated in exactly the way a held-out set exists to prevent. Tune against validation as often as you like; measure against test once.
