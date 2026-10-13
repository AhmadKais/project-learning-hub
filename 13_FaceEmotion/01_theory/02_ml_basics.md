# Chapter 2 — What is machine learning?

## 2.1 Normal programming vs. learning

In normal programming you write the rules:

📄 **A hand-written rule — and why it fails**
```python
def is_happy(face):
    if mouth_corners_up(face) and eyes_narrow(face):
        return True
    return False
```

Try to write `mouth_corners_up`. What is "up"? How many pixels? What about a person with a
beard? With glasses? From the side? In the dark? After a hundred rules you will find there are
still expressions the rules miss, and every fix of one rule breaks two others.

Machine learning turns this around: **we do not write rules, we show examples.** We give the
program 28,709 face pictures, each one marked with its emotion, and the program finds the rules
by itself. The rules it finds are not `if` statements — they are millions of numbers (weights)
that were slowly adjusted until the answers came out right.

## 2.2 The basic vocabulary

- **Sample** — one face picture.
- **Label** — the correct answer for a sample: "happy". In code it is a number: `HAPPY = 3`.
- **Dataset** — all the samples with their labels. Ours: FER-2013.
- **Supervised learning** — learning from examples **with** labels. This is what we do.
  (There is also unsupervised learning, without labels — not relevant for us.)
- **Classification** — the task: choose one category from a fixed list. We have 7 categories,
  so it is "multi-class classification".
- **Model** — the program that learns. Ours: a neural network. After training, "the model" is
  also the weights file `emotion_net_best.pt`.
- **Training** — the process where the model adjusts its weights using the examples.
- **Inference** — using a trained model on a new example. This is what happens in real time.

## 2.3 Three groups: train, validation, test

This is where students make the most mistakes, so examiners love to ask about it.

Imagine a teacher gives you 100 questions with solutions to prepare for an exam, and then in
the exam asks exactly the same 100 questions. A score of 100 does not prove you understood
anything — maybe you memorized. To know if you learned, the exam must have questions **you
have not seen**.

Same with a model. We split the dataset:

| Group | Size in FER-2013 | What it is for |
|---|---|---|
| Train | ~25,800 | The model learns **only** from these |
| Validation | ~2,900 (10% of train) | Checked at the end of every epoch; used to decide when to stop and which model to keep |
| Test | 3,589 | Touched **once**, at the end, to report the final score |

💡 If you pick the best model by looking at the test group, the score you report will be too
optimistic — information "leaked" from the test into your choice. That is why the validation
group exists.

❓ **Possible supervisor question: your model gets 95% on train and 64% on test. What happened?**
That is **overfitting**: the model memorized the training examples instead of learning the
general rule. It is excellent on what it saw and bad on what it did not. The solutions in the
project: data augmentation (chapter 6), dropout, weight decay, early stopping and label smoothing.
The opposite — a low score on train too — is called **underfitting**: the model is too small or
trained too little.

## 2.4 How we measure success

**Accuracy** = number of correct answers divided by number of samples. Simple, but misleading
when the categories are not balanced: if 25% of pictures are "happy", a model that always says
"happy" gets 25% without learning anything.

So we also measure each category separately. For the category "fear":

- **Precision** — of all the times the model said "fear", how many were really fear?
- **Recall** — of all the faces that were really fear, how many did the model catch?
- **F1** — the (harmonic) average of the two. One number per category. This is the target in the
  proposal: F1 ≥ 0.55 for every emotion.

📄 **Number example — Precision and Recall**
```text
The test set has 100 "fear" pictures.
The model said "fear" on 80 pictures: 60 of them were really fear, 20 were actually "surprise".

Precision = 60 / 80  = 0.75   (of what it said, how much was right)
Recall    = 60 / 100 = 0.60   (of what exists, how much it caught)
F1        = 2 * 0.75 * 0.60 / (0.75 + 0.60) = 0.667
```

**Confusion matrix** — a 7×7 table: row = the true emotion, column = what the model said. The
diagonal is the correct answers. The cells off the diagonal tell a story: for almost every model
on FER-2013, fear↔surprise and sad↔neutral get mixed up — because humans confuse them too. This
is the most important chart in your results chapter.

## 2.5 Why it is hard: FER-2013

The dataset was built in 2013 from Google image search with words like "angry face", and then
labeled. The result:

- **Noisy labels** — some pictures are labeled wrong. Human accuracy on this dataset: about 65%.
- **Imbalance** — 7,215 "happy" pictures vs. 436 "disgust". The model sees happy 16 times more often.
- **Low quality** — 48×48 pixels, black-and-white, all kinds of lighting and angles.

That is why the target in the proposal is 65% and not 95%. When you reach 66% — you passed human
accuracy on this dataset, and that is an achievement to explain in the book, not to apologize for.

## 2.6 Confusion matrix — a full calculation by hand

Until you calculate it once by hand, these ideas stay just words. An example with 3 classes and
150 test pictures (row = truth, column = prediction):

📄 **3×3 confusion matrix**
```text
                pred A    pred B    pred C   | true total
true A            50        10         0     |   60
true B             5        30         5     |   40
true C             0        10        40     |   50
--------------------------------------------------------
pred total        55        50        45     |  150

Accuracy = (50 + 30 + 40) / 150 = 120 / 150 = 0.800

Class A:  Precision = 50 / 55 = 0.909  (column)   Recall = 50 / 60 = 0.833  (row)
          F1 = 2 * 0.909 * 0.833 / (0.909 + 0.833) = 0.870
Class B:  Precision = 30 / 50 = 0.600             Recall = 30 / 40 = 0.750
          F1 = 0.667
Class C:  Precision = 40 / 45 = 0.889             Recall = 40 / 50 = 0.800
          F1 = 0.842

Macro-F1 = (0.870 + 0.667 + 0.842) / 3 = 0.793
```

Notice: the overall accuracy of 80% hides that class B is a problem — F1 only 0.667. Column B
shows why: 10 pictures of A and 10 of C "spill" into it. The model says B too often.
**This is exactly the analysis you will do on your 7×7 matrix**, and in the book you will write
which pairs get mixed and why.

- **Precision** is read down a **column**: of everything predicted as X.
- **Recall** is read along a **row**: of everything that is really X.
- **Macro-F1** = simple average of F1 over the classes — every class counts the same, no matter
  its size. It is the fair measure for an imbalanced dataset, which is why the proposal sets the
  target per emotion.

## 2.7 Data leakage

The mistake that turns an 80% score into a lie. Leakage = information from the test group
influences training or model selection. Three forms that matter to you:

1. **Choosing the model by the test score** — you ran 10 experiments and picked the one with
   the highest test score. Now the test is no longer "unseen" — it took part in the decision.
   So: choose by **validation**, report test once.
2. **Normalizing using the whole dataset** — if you compute mean and std on train+test together,
   statistics from the test got into the pipeline. Compute on train only.
3. **Augmentation before the split** — if you create augmented pictures and then split, a rotated
   version of a test picture may end up in train. Split first, augment after (the `transform`
   runs at load time, after `random_split` — that is why the order in `build_dataloaders` matters).

## 2.8 Bias and variance

Two sources of error for every model:

- **Bias** — the model is too simple for the problem. Even with infinite data it will not reach
  high accuracy. Sign: low training accuracy. Cure: a bigger/deeper model, more epochs.
- **Variance** — the model is too sensitive to the specific training data. Sign: a big gap between
  train and validation. Cure: more data (augmentation), regularization (dropout, weight decay),
  early stopping.

📄 **Reading training curves**
```text
Epoch   train_acc   val_acc      diagnosis
  5       0.52       0.50        fine - both rising together
 15       0.70       0.64        fine - small gap
 30       0.88       0.66        val stopped, train keeps going: overfitting starts
 45       0.96       0.64        val falling: early stopping should have stopped at ~30
```

Your `training_curves.png` will show exactly this story. Learn to read it out loud.

## ✅ Check yourself — Chapter 2

1. A model that always guesses "happy" on the FER-2013 test set (1,774 happy out of 3,589).
   What is its accuracy? The recall of "happy"? The precision of "happy"? The F1 of "disgust"?
2. In the matrix of section 2.6 you changed the model and now row B is `[2, 36, 2]`. Recompute
   precision, recall and F1 of B, and the overall accuracy.
3. Your friend trained 8 models, tested each on the test set and picked the best — 71%.
   Why is that number not reliable, and what should he have done?
4. Train accuracy 58%, validation accuracy 57%. Overfitting or underfitting? What do you try first?
5. Why must `random_split` get a `generator` with a fixed seed? What happens to your experiments without it?

## 📚 Further reading — Chapter 2

- **Google — Machine Learning Crash Course**, modules "Classification" and "Overfitting":
  https://developers.google.com/machine-learning/crash-course — short, interactive, about two hours. Start here.
- **scikit-learn — Model evaluation** (precision, recall, F1, confusion matrix):
  https://scikit-learn.org/stable/modules/model_evaluation.html — sections 3.4.2–3.4.4, this is what you use in `evaluator.py`.
- **The FER-2013 paper** (Goodfellow et al., 2013), pages 1–4 only: https://arxiv.org/abs/1307.0414
- **Barrett et al. (2019), Emotional Expressions Reconsidered** — abstract only, for the limitations in the book:
  https://journals.sagepub.com/doi/10.1177/1529100619832930
