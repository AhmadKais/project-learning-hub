# Lesson 24 — Training in practice: augmentation, class weights, label smoothing, early stopping

> **For:** Ryan (FaceEmotion stage 4 — training on the GPU) &nbsp;·&nbsp; **Time:** 45 – 60 min
> **Before:** Lessons 01, 21, 23 &nbsp;·&nbsp; **After this:** the evaluation chapter (Lesson 03 for 7 classes)

## 🎯 By the end, the student can

1. Explain data augmentation and why it is applied to the **training set only**.
2. Compute class weights for FER-2013 and explain what they do to the loss.
3. Compute a label-smoothed target and explain why it makes the model more honest.
4. Read train/validation curves, and explain early stopping with patience and checkpoints.

---

## 1. Data augmentation — more data for free

![augmentation](figs/augmentation.png)

Every epoch, each training face is changed a little at random: **horizontal flip** (a smile is a smile in the mirror),
**rotation up to 10°**, a **small crop**, **random erasing** (a hand, glasses). The network never sees the same picture
twice → hard to memorise → a few percent better on test.

⚠️ Training only. A random flip in `build_eval_transform` would make every validation score different on every run —
and the camera would see "random" pictures.

## 2. Imbalance — class weights

![class weights](figs/class_weights.png)

$$w_i=\frac{\text{total}}{K\cdot \text{count}_i}\qquad\text{happy: }\frac{28709}{7\cdot 7215}=0.57\qquad\text{disgust: }\frac{28709}{7\cdot 436}=9.41$$

Passed to `nn.CrossEntropyLoss(weight=...)`: a mistake on a rare class costs more, so the network "tries" on it. Without
it, the cheapest strategy is to never say *disgust* (F1 ≈ 0.2 on that class). Compare with Seif's alpha correction for
k-NN (Lesson 15) — same problem, different model.

## 3. Label smoothing

![label smoothing](figs/label_smoothing.png)

$$y_i=(1-\varepsilon)\cdot\text{onehot}_i+\frac{\varepsilon}{K}\qquad\varepsilon=0.1,\ K=7\ \Rightarrow\ 0.914\text{ for the true class},\ 0.014\text{ for the others}$$

FER-2013 has noisy labels (some are simply wrong). With a 100 % target the network chases 99.9 % confidence — on wrong
labels too. With the smoothed target the loss is lowest at ≈ 91 %: a more modest model whose shown confidence is closer to
its real accuracy (**calibration**, Lesson 14).

## 4. When to stop — early stopping and checkpoints

![early stopping](figs/early_stopping.gif)

*(Illustration with the project's settings.)* Every epoch: measure validation accuracy. **New best → save the weights**
(`emotion_net_best.pt`). **8 epochs without improvement → stop** (`EARLY_STOPPING_PATIENCE = 8`). Here the best epoch is 22,
training stops at 30, and the file holds epoch 22 — never the over-trained end.

The checkpoint also stores the normalisation numbers, so a model file can never be used with the wrong pre-processing:

```python
torch.save({"model_state": model.state_dict(), "epoch": epoch, "val_acc": val_acc,
            "config": {"image_size": 48, "mean": 0.5013, "std": 0.2916}}, path)
```

## 5. Reading the curves

| you see | it means | do |
|---|---|---|
| both losses fall together | still learning | keep going |
| train ↓, validation ↑ | overfitting | the checkpoint has the best; more augmentation / dropout / weight decay |
| both flat and high | underfitting / lr too small / bug | check lr, check the labels match the pictures |
| loss = `nan` | lr too high, or log(0) | lower lr; check the inputs |
| loss stuck at ln 7 = 1.95 | the network guesses uniformly | it isn't learning at all — a pipeline bug |

## 6. Misconceptions

| Student says | Truth |
|---|---|
| "Augment the test set too, for fairness" | Then you measure on pictures that don't exist. Test = real pictures only. |
| "Early stopping wastes the last epochs" | They made the model worse; the checkpoint keeps the best. |
| "Class weights make the model better at everything" | They trade a little accuracy on big classes for recall on small ones. Report per-class F1. |
| "Label smoothing lowers accuracy" | Usually not; it improves calibration and often generalisation. |

## 7. Activities

1. **Augment by hand (5 min).** Hold a printed face upside down, mirrored, half covered — still the same emotion? Which
   change is *not* allowed? (Upside down is unrealistic for a webcam; vertical flips are not used.)
2. **Weights (10 min).** Compute the 7 class weights from the counts (the chart's numbers).
3. **Be the early-stopping callback (10 min).** Read out a list of 20 validation accuracies; students keep "best" and
   "patience" on paper and shout STOP.

## 8. Check yourself

<details><summary>1. Angry has 3,995 faces. Its class weight?</summary>

28,709 / (7 · 3,995) = **1.03**.
</details>

<details><summary>2. With ε = 0.1 and K = 7, what is the smoothed target of a wrong class?</summary>

0.1 / 7 = **0.014**; the true class gets 0.9 + 0.014 = 0.914.
</details>

<details><summary>3. Validation accuracy: 0.60, 0.62, 0.61, 0.63, then 8 epochs below 0.63. Which epoch is in the file, and when does training stop?</summary>

Epoch 4 (0.63) is saved; training stops at epoch 12.
</details>

## 9. In your project

| Project | Where |
|---|---|
| FaceEmotion | `app/ml/dataset.py` → `build_train_transform` (augmentation), `build_eval_transform`, `compute_class_weights`, `FER2013Dataset.class_counts` · `app/ml/trainer.py` → `fit` (early stopping), `save_checkpoint`, `plot_history` · `config.py` → `LABEL_SMOOTHING = 0.1`, `EARLY_STOPPING_PATIENCE = 8`, `EPOCHS = 50` · theory `13_FaceEmotion/01_theory/06_data_training.md` · notebook `03_training_loop.ipynb` |

## 🎬 Watch & explore

* *Data augmentation explained* — [search on YouTube](https://www.youtube.com/results?search_query=data+augmentation+deep+learning+explained)
* Andrej Karpathy — [A Recipe for Training Neural Networks](https://karpathy.github.io/2019/04/25/recipe/) (a classic checklist)
* Müller, Kornblith, Hinton — [When does label smoothing help? (arXiv)](https://arxiv.org/abs/1906.02629)
