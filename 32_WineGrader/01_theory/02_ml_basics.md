# Chapter 2 — Machine learning in one chapter

💡 **In short:** learn from labelled examples, measure on examples the model has never seen, and never let the test data influence any decision. Almost every mistake in this field breaks that last rule.

## 2.1 Supervised classification

You have examples whose answer is known: 5,320 wines, each with 12 measurements and a grade given by tasters. You want a function that takes the 12 measurements of a *new* wine and returns its grade.

- the 12 measurements are the **features**, `X` — a (5320, 12) array
- the grades are the **labels**, `y` — 0 (low), 1 (medium), 2 (high)
- "learning" means using `X` and `y` to build the function

Three possible grades makes it **multi-class** classification.

## 2.2 Generalisation — the only thing that counts

A model that memorises its training wines perfectly can still be useless on new ones. The question is never "how well does it do on what it has seen?" but "how well will it do on wines it has never seen?". That is called **generalisation**, and it can only be measured on wines that played no part in building the model.

That gives the most important rule in the project:

**Test data must not influence anything: not the model, not the scaling, not the choice of k, not the weights. Nothing.**

When it does, it is called **data leakage**, and the score you report is better than the truth. Chapter 7 is entirely about this, and four of your tests exist only to catch it.

## 2.3 Train, validate, test

- **Training** rows build the model.
- **Validation** rows choose between models — which k, which scaling.
- **Test** rows measure the final choice, once.

Validation and test must be different, because choosing *is* a form of learning: if you try 150 configurations and keep the one that scored best on some rows, that score is optimistic for those rows. Nested cross-validation (chapter 7) is the rigorous version of this idea.

## 2.4 Lazy and eager learners

An **eager** learner (logistic regression, a neural network, a decision tree) studies the training data once, summarises it into parameters, and could then throw the data away.

A **lazy** learner — k-NN — does nothing at training time. It keeps all the data and does all the work when asked a question: find the most similar stored examples and let them vote.

| | Eager | Lazy (k-NN) |
|---|---|---|
| Training | slow | instant |
| Answering | fast | slow — compares with every example |
| Memory | parameters only | the whole dataset |
| Adding an example | retrain | just store it |
| Explaining an answer | often hard | show the neighbours |

❓ **If k-NN does not train, what does your model learn?**

Three things, all from training rows only: the scaling parameters (mean and standard deviation of every feature), the class priors used in the imbalance correction, and — the real learning — a weight for each feature, chosen by coordinate search to maximise the cross-validated score. Plus the hyper-parameters k, p, alpha and the scaling method, chosen by grid search. The stored wines are the model's memory; the weights decide what "similar" means.

## 2.5 Accuracy is not enough

44% of the wines are medium. A program that ignores its input and always answers "medium" is 44% accurate. So 50% accuracy is not "half right" — it is barely better than doing nothing.

That is why the project's main measure is **macro-F1** (chapter 7): it averages the F1 of the three grades without weighting by size, so the small high-quality class counts as much as the large medium one. The always-medium program scores about 0.20 on it.

## 2.6 Baselines

A number means nothing without something to compare it to. Every result in the project is reported next to two baselines, measured on exactly the same folds:

- **Majority** — always answers the most common grade. The floor.
- **Centroid** — computes the average wine of each grade and answers with the nearest average. The simplest real model.

If k-NN cannot beat the centroid clearly, the complexity is not earning its keep.

## 2.7 Hyper-parameters

Parameters the algorithm does not learn by itself, which you choose: k (how many neighbours), p (which distance), alpha (how strongly to correct for imbalance), the scaling method. They are chosen by trying many values and keeping the best — on validation data only.

❓ **What is the difference between a parameter and a hyper-parameter in your project?**

Parameters are learned by the algorithm from training data: the scaler's means and standard deviations, the class priors, and the feature weights. Hyper-parameters are choices made from outside by search: k, p, alpha and the scaling method. Both come from training data only — the difference is who chooses them.
