# Lesson 24 — Training in practice: augmentation, class weights, label smoothing, early stopping

> **For:** Ryan (FaceEmotion stage 4 — training on the GPU) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lessons 01, 21, 23 &nbsp;·&nbsp; **After this:** the evaluation chapter (Lesson 03 for 7 classes)

## The story

> Ryan trains EmotionNet. Three problems show up, one after the other:
>
> 1. After 20 epochs the network is 99 % right on the training faces and only 60 % on new ones — it **memorised**.
> 2. It **never** says "disgust": only 436 of 28,709 training faces are disgust, so ignoring them is the cheapest strategy.
> 3. Some FER-2013 faces are labelled **wrong** (a "sad" face that looks neutral), and the network tries hard to be 100 %
>    sure about them anyway.
>
> Each problem has a standard fix. This lesson explains all four tricks Ryan's trainer uses — with the numbers.

## 🎯 By the end, the student can

1. Explain data augmentation and why it is only for the training set.
2. Compute class weights for FER-2013 and explain what they change.
3. Compute a label-smoothed target and explain why it makes the model more honest.
4. Read training curves and explain early stopping with patience and checkpoints.

## Words you need

| word | meaning |
|---|---|
| **augmentation** | small random changes to each training picture every epoch (flip, rotate, crop, erase) |
| **imbalanced classes** | some answers are much rarer than others |
| **class weight** | a multiplier on the loss: mistakes on rare classes cost more |
| **label smoothing** | the target is "91 % right answer, a little for each other", not "100 %" |
| **training curve** | a chart of the loss / accuracy after every epoch |
| **early stopping** | stop training when the validation score hasn't improved for a while |
| **patience** | how many epochs to wait for an improvement (Ryan: 8) |
| **checkpoint** | a saved copy of the weights — the best ones so far |

---

## 1. Augmentation — more data for free

![augmentation](figs/augmentation.png)

Every epoch, before a face enters the network, it is changed a little at random:

| change | why it's allowed |
|---|---|
| horizontal flip | a smile is still a smile in the mirror |
| rotation up to 10° | people tilt their heads |
| a small crop | the face detector isn't perfectly centred |
| erase a small rectangle | a hand, glasses, hair in front of the face |

The network never sees the exact same picture twice, so memorising becomes hard → typically a few % better on new faces.

⚠️ **Training only.** The validation, test and camera pictures are never changed — otherwise scores change on every run, and
the camera would see "random" faces. That's why `dataset.py` has two separate transforms.

## 2. Imbalance — class weights

![class weights](figs/class_weights.png)

$$\text{weight}_i = \frac{\text{total faces}}{K \times \text{faces of class } i}\qquad K = 7\text{ emotions}$$

```
happy:    28,709 / (7 × 7,215) = 28,709 / 50,505 = 0.57      a mistake is cheap
disgust:  28,709 / (7 × 436)   = 28,709 / 3,052  = 9.41      a mistake costs 16× more
angry:    28,709 / (7 × 3,995) = 28,709 / 27,965 = 1.03      about normal
```

Why this formula? If every class had the same number of faces (28,709 / 7 = 4,101 each), every weight would be exactly 1.
Rare classes get more than 1, common ones less. The weights go into the loss: `nn.CrossEntropyLoss(weight=...)`. Now
ignoring "disgust" is expensive, and the network starts trying. (The same problem as Seif's alpha, Lesson 15.)

## 3. Label smoothing — don't demand 100 % certainty

![label smoothing](figs/label_smoothing.png)

$$y_i = (1 - \varepsilon)\times\text{onehot}_i + \frac{\varepsilon}{K}\qquad \varepsilon = 0.1$$

**Step by step (truth = happy):**

```
normal target ("onehot"):   [0, 0, 0, 1, 0, 0, 0]                       100 % happy
(1 − ε) × onehot:           [0, 0, 0, 0.9, 0, 0, 0]
ε / K = 0.1 / 7 = 0.014    → add to every position:
smoothed target:            [0.014, 0.014, 0.014, 0.914, 0.014, 0.014, 0.014]     (adds up to 1)
```

The loss becomes Σ yᵢ × (−ln pᵢ) — a bit of loss for every class. The right panel: with the normal target the loss is lowest
at 100 % (it never stops pushing); with smoothing the loss is lowest at about **91 %**. The network stops chasing certainty on
labels that may be wrong, and its shown confidence ("81 % happy") becomes more honest.

## 4. When to stop — early stopping and checkpoints

![early stopping](figs/early_stopping.gif)

*(Illustration with the project's settings.)* After every epoch, measure accuracy on the **validation** faces:

```
new best?  → save the weights to emotion_net_best.pt, reset the counter to 0
no?        → counter + 1
counter reaches 8 (patience) → stop
```

Here the best epoch is 22, training stops at 30, and the saved file holds **epoch 22** — never the over-trained end. The
checkpoint also stores the normalisation numbers, so a model file can never be used with the wrong preparation:

```python
torch.save({"model_state": model.state_dict(), "epoch": epoch, "val_acc": val_acc,
            "config": {"image_size": 48, "mean": 0.5013, "std": 0.2916}}, path)
```

## 5. Reading training curves

| you see | it means | do |
|---|---|---|
| both losses fall together | still learning | continue |
| training ↓, validation ↑ | overfitting | the checkpoint keeps the best; more augmentation / dropout |
| both flat and high | not learning: lr too small, or a bug | check lr; check labels match pictures |
| loss = `nan` | lr too high, or ln(0) | lower lr |
| loss stuck at 1.95 (= ln 7) | the network guesses uniformly | a pipeline bug |

## 6. Common mistakes

| student says | the truth |
|---|---|
| "Augment the test set too" | Then you measure on pictures that don't exist. |
| "Early stopping wastes the last epochs" | Those epochs made it worse; the checkpoint keeps the best. |
| "Class weights make everything better" | They trade a bit of accuracy on common classes for recall on rare ones. Report per-class F1. |

## 7. Activities

1. **Augment by hand (5 min).** Hold a printed face mirrored, tilted, half-covered: still the same emotion? Which change is
   *not* allowed? (Upside down — webcams don't see that.)
2. **Weights (10 min).** Compute all 7 class weights from the chart's counts.
3. **Be the early-stopping helper (10 min).** Read 20 validation accuracies aloud; students track "best" and "patience" and
   shout STOP.

## 8. Do it yourself

<details><summary>1. Sad has 4,830 faces. Its class weight?</summary>

28,709 / (7 × 4,830) = 28,709 / 33,810 = **0.85**.
</details>

<details><summary>2. With ε = 0.2 and K = 4, the smoothed target for the true class and for the others?</summary>

others 0.2 / 4 = **0.05** · true class 0.8 + 0.05 = **0.85** (check: 0.85 + 3 × 0.05 = 1).
</details>

<details><summary>3. Validation: 0.60, 0.62, 0.61, 0.63, then 8 epochs below 0.63. Which epoch is saved, and when does training stop?</summary>

Epoch 4 (0.63) is saved; training stops after epoch 12.
</details>

## 9. In your project

| Project | Where |
|---|---|
| FaceEmotion | `app/ml/dataset.py` → `build_train_transform`, `build_eval_transform`, `compute_class_weights`, `FER2013Dataset.class_counts` · `app/ml/trainer.py` → `fit`, `save_checkpoint`, `plot_history` · `config.py` → `LABEL_SMOOTHING = 0.1`, `EARLY_STOPPING_PATIENCE = 8`, `EPOCHS = 50` · theory `13_FaceEmotion/01_theory/06_data_training.md` · notebook `03_training_loop.ipynb` |

## 🎬 Watch & explore

* *Data augmentation explained* — [search on YouTube](https://www.youtube.com/results?search_query=data+augmentation+deep+learning+explained)
* Andrej Karpathy — [A Recipe for Training Neural Networks](https://karpathy.github.io/2019/04/25/recipe/)
