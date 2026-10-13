# Chapter 5 — Evaluating honestly: threshold, ROC, mistakes, drift

💡 **In short:** the model outputs a probability; we choose the cut-off (threshold) on the validation set so that recall is at least 95%. We report the final numbers on the test set once. Then we look at the URLs it got wrong, and we check it on this week's phishing to see if it aged.


## 5.1 The threshold is a decision, not a default

The model gives a probability. *You* decide where to cut. Lower the threshold and you catch more
phishing (recall up) but raise more false alarms (precision down). Raise it and the opposite.

📄 **The same model, three thresholds (validation set, 3,000 URLs)**
```text
threshold   TP    FN    FP    recall   precision   F1
  0.70     1380  120    25    0.920     0.982     0.950
  0.50     1440   60    55    0.960     0.963     0.961
  0.30     1478   22   140    0.985     0.913     0.948
```

Our rule (`ModelEvaluator.choose_threshold`): on the **validation** split, take the *highest*
threshold whose recall ≥ 0.95 — here 0.50 — so we catch 95% while keeping false alarms as low as
that allows. Then report the metrics on the **test** split at that threshold. The test split never
votes on the threshold.

❓ **Possible supervisor question: why not just use 0.5 like everyone?**
Because 0.5 assumes both mistakes cost the same. Missing a phishing site costs more than a false
alarm, so we deliberately buy recall with a little precision — and we can *show the table* of what
each threshold buys. A number chosen from a table is a design decision; 0.5 is a habit.

## 5.2 The ROC curve and AUC

Sweep the threshold from 1 to 0 and plot recall (true-positive rate) against the false-alarm rate
(FP / all good). A perfect model hugs the top-left corner; a coin-flip is the diagonal. **AUC**
(area under the curve) summarizes it in one number: 0.5 = random, 1.0 = perfect. It does not depend
on any threshold, so it is the fairest single number to compare two models. Target: ≥ 0.97.

`reports/roc_curve.png` shows both models on one axis with their AUC in the legend.

## 5.3 Cross-validation vs. the final test

Cross-validation scores (chapter 4.7) are for *choosing* settings. The final numbers in your book
come from the test split, once. If they are lower than the CV scores by a few tenths of a percent,
that is normal; if they are much lower, something leaked or the sample was too small.

## 5.4 Look at the mistakes — `worst_mistakes`

Numbers tell you *how much* the model is wrong; the actual URLs tell you *why*. Print the 10 false
positives with the highest probability and the 10 false negatives with the lowest. Typical findings:

- False positives: long legitimate URLs with many parameters and digits (a tracking link from a real
  shop), legitimate sites on cheap TLDs.
- False negatives: short phishing URLs on hijacked legitimate domains (`goodsite.com/wp-content/x/login`) —
  the structure looks fine because the domain *is* fine. This is the honest limit of URL-only detection;
  it goes in "limitations" and motivates "page content" as future work.

## 5.5 Concept drift — the model ages

Attackers adapt. A model trained on 2019 URLs sees 2026 tricks it never met. Your stage-7 experiment:
collect 30 phishing URLs from **this week** on PhishTank and scan them. If recall drops from 95% to
80%, you have *measured* drift — a great paragraph, and the reason the app stores user feedback for
future retraining.

## 5.6 The experiments table

One table saves you the whole results chapter:

| # | Setup | CV F1 | Test precision | Test recall | Test F1 | AUC | Train time |
|---|---|---|---|---|---|---|---|
| 1 | logistic, no class weights, threshold 0.5 | | | | | | |
| 2 | logistic, class_weight=balanced | | | | | | |
| 3 | logistic, tuned C, chosen threshold | | | | | | |
| 4 | forest, unlimited depth | | | | | | |
| 5 | forest, grid-searched, chosen threshold | | | | | | |
| 6 | best model, 2k / 10k / 20k per class | | | | | | |

Row 1 is deliberately naive so rows 2–5 tell a story ("class weights added 4 points of recall").

## ✅ Check yourself — Chapter 5

1. From the table in 5.1, compute precision and recall at threshold 0.70 yourself and check the numbers.
2. At which threshold in that table is F1 highest? Which threshold does our rule pick, and why are they different?
3. A model has AUC 0.99 but at threshold 0.5 recall is 0.80. Is the model bad? What should you do?
4. You computed the ROC curve on the training split and got AUC 1.00. Is the model perfect?
5. Give one realistic false positive and one realistic false negative for a URL-only detector, and
   say which feature is "fooled" in each.
6. Design the drift experiment: what data, what metric, what result would confirm drift?

## 📚 Further reading — Chapter 5

- **Google ML Crash Course — Classification: ROC and AUC**: https://developers.google.com/machine-learning/crash-course/classification/roc-and-auc
- **scikit-learn — Precision-Recall and ROC examples**: https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html · https://scikit-learn.org/stable/auto_examples/model_selection/plot_roc.html
- **StatQuest — ROC and AUC clearly explained**: https://www.youtube.com/watch?v=4jRBRDbJemM
- **PhishTank** (fresh URLs for the drift test): https://phishtank.org/
