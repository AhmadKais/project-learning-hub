# Chapter 2 — What machine learning is, and why spam needs it

💡 **In short:** you cannot write rules for spam, because the people sending it read your rules and change. Instead you show the computer thousands of labelled messages and it works out how much each word matters. You hide some messages to check it really learned. And you never measure with accuracy, because 87% of the corpus is legitimate mail.

## 2.1 Why rules fail

The obvious first attempt:

📄 **A hand-written rule — and why it does not survive**
```python
BANNED = {"free", "winner", "viagra", "prize"}

def is_spam(message):
    return any(word in message.lower() for word in BANNED)
```

Three things go wrong, and all three are fatal:

1. **It is trivially evaded.** `fr3e` is not `free`. One character, and your filter is blind.
2. **It blocks real mail.** "The event is free for students" is a perfectly normal sentence.
3. **It never ends.** Every new trick means a new rule, each rule interacts with the last, and after fifty of them nobody can say what the filter does any more.

The deeper problem is that this is an *adversarial* setting. Spammers read filters and adapt. A fixed rule written in October is working against someone who gets to see it and respond.

Machine learning inverts the approach: **do not write the rules, supply the examples.** Give the program 5,000 messages labelled spam or ham, and it works out for itself how much evidence each word carries — as numbers, derived from counting.

## 2.2 Vocabulary

- **Sample** — one message.
- **Label** — the right answer: `ham` (0) or `spam` (1). In this project 1 means spam.
- **Corpus** — all the labelled samples. Ours: SMS Spam Collection or Enron-Spam.
- **Feature** — one number describing a sample, e.g. `caps_ratio = 0.81`.
- **Feature vector** — all the numbers for one sample, in a fixed order.
- **Supervised learning** — learning from labelled examples. What we do.
- **Binary classification** — two classes. Spam or ham.
- **Model** — the thing that learns. Ours: Naive Bayes and an SVM.
- **Training** — fitting the model to examples. **Inference** — using it on a new message.
- **Probability** — the model's output, between 0 and 1. **Threshold** — the cut-off that turns it into a verdict.

## 2.3 Train, validation, test

If a teacher hands you 100 solved problems and the exam is those same 100, full marks proves only that you can memorise. The same is true of a model, so the corpus is split three ways.

| Split | Share | Used for |
|---|---|---|
| Train | 70% | the model learns from these, and **only** these |
| Validation | 15% | choosing settings: which model, which threshold |
| Test | 15% | touched **once**, at the very end, to report the final score |

The test set is locked. `train.py` never opens it. `evaluate.py` opens it once.

💡 If you pick the threshold by looking at the test set, the number you report is not a measurement — the test set took part in the decision. That is **leakage**, and validation exists precisely so you never have to do it.

## 2.4 Stratified splitting

Our corpus is roughly 13% spam. A plain random split can easily hand the validation set 8% spam and the test set 19%, purely by chance — and then the two measurements are not comparable with each other.

A **stratified** split preserves the ratio in every part. `test_split_preserves_class_ratio` checks this.

📄 **Stage 1: `dataset.py`**
```python
from sklearn.model_selection import train_test_split

train_texts, temp_texts, train_y, temp_y = train_test_split(
    texts, labels, test_size=0.30, stratify=labels, random_state=seed)

val_texts, test_texts, val_y, test_y = train_test_split(
    temp_texts, temp_y, test_size=0.50, stratify=temp_y, random_state=seed)
```

`random_state=seed` makes the split reproducible. Without it, every run gives different numbers and no before-and-after comparison in your project book means anything.

## 2.5 Leakage, the quiet project-killer

Leakage is when information from the test set reaches the model during training. It does not crash. It does not warn. Your scores simply come out better than they should, you write them in the book, and at the defence someone asks where you fitted the vectorizer.

The commonest form in this project:

📄 **Wrong, and it will not look wrong**
```python
engineer.fit(all_messages)              # includes validation and test
```

📄 **Right**
```python
engineer.fit(train_messages)            # train only
```

Why it matters: `fit` builds the vocabulary and the IDF weights. Fitting on everything lets words that only ever appear in the test set into the vocabulary, and lets test documents influence every IDF weight. The model has then been shaped by data it is about to be scored on.

`assert_no_leakage` checks the cruder version — the same text appearing in two splits — and `train.py` calls it on every run, not just once while you were developing.

❓ **Give a concrete example of leakage and what it would do to your results.**

Fitting the TF-IDF vectorizer on the full corpus instead of the training split. The IDF weight of every term is then computed partly from the test documents, so the representation itself has seen the answers. Reported precision and recall come out several points higher than the model would really achieve on new mail, and nothing anywhere raises an error.

## 2.6 Why accuracy is not allowed here

Accuracy is the fraction of correct answers. It sounds like the obvious metric and it is useless on this data.

Our corpus is about 13% spam. Consider this model:

📄 **The 87% model**
```python
def predict(message):
    return "ham"          # always
```

It is 87% accurate. It has learned nothing — it does not even look at the message. Any real model has to beat 87% before it has done anything at all, and "we got 91%" tells you almost nothing about whether it works.

So this project measures on the spam class only:

| Metric | Question it answers | Formula |
|---|---|---|
| **Precision** | of the messages I called spam, how many really were? | TP / (TP + FP) |
| **Recall** | of the spam that existed, how much did I catch? | TP / (TP + FN) |
| **F1** | the two combined | 2PR / (P + R) |

The always-ham model scores precision 0 and recall 0. The metric catches it immediately, which is exactly what accuracy failed to do.

## 2.7 The two mistakes are not equal

This is the most important idea in the project, and it is the one examiners push on.

| Mistake | Name | What it costs |
|---|---|---|
| Spam reaches the inbox | false negative | one second of annoyance |
| **Real mail is hidden** | **false positive** | a missed job interview |

They are not remotely comparable. One is a nuisance; the other means a message from a school, a hospital or an employer sits in a folder nobody opens.

Everything downstream follows from this:

- the threshold is **not** 0.5 (chapter 6)
- it is not tuned for F1 either, because F1 treats both errors as equal
- it is pushed up until precision clears a floor, and the recall that results is reported rather than chased

❓ **Why not simply maximise F1?**

Because F1 is symmetric: it weighs a false positive exactly as heavily as a false negative. In spam filtering they differ by orders of magnitude. Maximising F1 optimises for the wrong thing — it will happily trade away several legitimate messages to catch a little more spam. Constraining precision and then taking the best available recall encodes the real cost structure instead.

## 2.8 Overfitting

A model overfits when it memorises the training data instead of learning a general rule. It scores brilliantly on what it has seen and poorly on anything new.

Three defences are built into this project:

1. **Capped vocabulary** — 5,000 features, so the model cannot memorise rare quirks of the corpus.
2. **Cross-validation** — five different train/test divisions, so a single lucky split cannot fool you.
3. **A locked test set** — the final number comes from data that took no part in any decision.

💡 A sign of overfitting you can spot by eye: look at `most_discriminative(50)`. If the most "decisive" words are things like `enron` or a specific person's name, the model has learned your corpus rather than learned spam.

## 2.9 Cross-validation

One split gives one number, and that number moves depending on which messages happened to land where. Five-fold cross-validation gives five numbers, so you can report a mean *and* a spread.

```
fold 1:  train on 2,3,4,5   test on 1
fold 2:  train on 1,3,4,5   test on 2
...
result:  mean ± standard deviation
```

The standard deviation is not decoration. If Naive Bayes scores F1 = 0.921 and the SVM scores 0.907, that gap looks real — until you see the fold-to-fold spread is ±0.03, at which point the honest conclusion is **no significant difference**. `ModelComparator.compare` implements exactly that rule, and saying so at the defence is a stronger answer than claiming a winner.
