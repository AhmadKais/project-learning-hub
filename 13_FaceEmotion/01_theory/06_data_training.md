# Chapter 6 — Data, training and the GPU

## 6.1 Data augmentation — multiply the dataset for free

In every epoch, before a picture enters the network, we change it a little at random: horizontal
flip (a smile is a smile in the mirror too), rotation up to 10 degrees, a small crop, erasing a
small rectangle (simulates a hand or glasses). The network never sees exactly the same picture
twice, so it is hard for it to memorize. In practice this is worth a few percent of test accuracy.

💡 Augmentation is done **only on the training set**. On validation, test and in real time — never.
That is why there are two separate transforms in `dataset.py`. If you put a random flip in
`build_eval_transform`, your score will change on every run and you will not understand why.

## 6.2 Imbalance and class weights

436 disgust pictures vs. 7,215 happy. Without treatment, the network learns that "disgust" almost
never happens and simply never guesses it — and gets an F1 of 0.2 on that class. The solution: in
the loss function, a mistake on a disgust picture "costs" more than a mistake on a happy picture.

📄 **Computing class weights**
```text
weight_i = total / (num_classes * count_i)

happy:   28709 / (7 * 7215) = 0.57      cheap mistake
disgust: 28709 / (7 * 436)  = 9.41      mistake costs 16x more
```

We pass the vector to `nn.CrossEntropyLoss(weight=...)` and the network starts to "try" on the
rare classes too.

## 6.3 Label smoothing

Instead of telling the network "the answer is happy at 100%", we say "happy at 90%, and 10% spread
over the rest". Why? Because the dataset is noisy — some labels are simply wrong — and a network
that tries to reach 100% confidence on a wrong label learns nonsense. The result: a more "modest"
model, whose shown confidence (81%) is closer to its real accuracy. This is called **calibration**.

## 6.4 When to stop — early stopping and checkpoints

At the end of every epoch we measure accuracy on the validation set. If it is the best so far — we
save the weights to `emotion_net_best.pt`. If 8 epochs pass with no improvement — we stop:
more training would only cause overfitting. So we never use a model that "went bad" at the end.

📄 **What is saved in a checkpoint**
```python
torch.save({
    "model_state": model.state_dict(),     # the weights themselves
    "epoch": epoch, "val_acc": val_acc,
    "config": {"image_size": 48, "mean": 0.5077, "std": 0.2550},
}, path)
```

Saving the normalization constants **inside** the file guarantees a model file is never used
with the wrong normalization.

## 6.5 Why a graphics card, and what is CUDA

One training step on a batch of 128 pictures is mostly **matrix multiplication** — millions of
multiplications and additions that do not depend on each other. A processor (CPU) does them on a
few cores, one after another. A graphics card (GPU) has thousands of small cores that do all of
them **in parallel**. For the same training: ~15 minutes on a laptop GPU, ~6 hours on a CPU.

**CUDA** is NVIDIA's platform that lets PyTorch send computations to the card. In code it looks
like this:

📄 **Moving to the GPU**
```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)             # the weights move to the card's memory
images = images.to(device)           # and every batch too, every step
```

💡 A tensor on the GPU and a tensor on the CPU cannot be computed together. The error
`Expected all tensors to be on the same device` means you forgot `.to(device)` on something.
And to bring a result back to numpy (for example to draw on the frame) you need `.cpu().numpy()`.

## 6.6 Mixed precision (AMP)

Numbers in PyTorch are by default float32 (32 bits). Modern graphics cards compute float16
(16 bits) 2–4 times faster and in half the memory. **AMP** (Automatic Mixed Precision) does most
computations in float16 and keeps the weights and the loss in float32 so no accuracy is lost.
Three lines in `trainer.py`:

📄 **AMP**
```python
scaler = torch.cuda.amp.GradScaler(enabled=use_amp)
with torch.autocast("cuda", enabled=use_amp):
    outputs = model(images)
    loss = criterion(outputs, labels)
scaler.scale(loss).backward()        # multiplies the loss so small gradients do not become zero in float16
scaler.step(optimizer)
scaler.update()
```

❓ **Possible supervisor question: what does the GradScaler do and why is it needed?**
In float16, very small numbers (below 6×10⁻⁸) become zero. Gradients are often that small. The
scaler multiplies the loss by a big number before `backward()` so the gradients "rise" into a safe
range, and then divides back before updating the weights. If it detects an overflow (inf) — it skips
the step and lowers the multiplier.

## 6.7 Label smoothing — the formula

📄 **The smoothed target**
```text
ε = 0.1, K = 7 classes, truth = happy

normal target (one-hot):   [0, 0, 0, 1, 0, 0, 0]
smoothed target:           y_i = (1-ε)*onehot_i + ε/K
                           = [0.014, 0.014, 0.014, 0.914, 0.014, 0.014, 0.014]

L = - Σ y_i * ln(p_i)      (instead of -ln(p_correct) only)
```

Practical effect: the minimum loss is no longer 0. The network "stops trying" when it reaches about
90% confidence — and does not chase 99.9% on labels that are partly wrong. Müller et al. (2019)
showed this also improves calibration: if the model says 80% — it is right about 80% of the time.

## 6.8 Computing the mean and standard deviation of the dataset

The numbers 0.5077 and 0.2550 in `config.py` did not come from thin air. This is how to compute
them (on the training set only — section 2.7):

📄 **Computing mean/std — one-time script**
```python
loader = DataLoader(FER2013Dataset(train_dir, transform=ToTensorOnly()), batch_size=512)
total, total_sq, count = 0.0, 0.0, 0
for images, _ in loader:                 # images: (B, 1, 48, 48) in range 0..1
    total += images.sum().item()
    total_sq += (images ** 2).sum().item()
    count += images.numel()
mean = total / count
std = (total_sq / count - mean ** 2) ** 0.5
print(mean, std)                         # ~0.5077  ~0.2550
```

Run it once and make sure you get the same numbers. If your dataset is different (another version
of FER-2013) — update `config.py`. This is a point an examiner who understands will ask: "where do
the numbers come from?"

## 6.9 Determinism — why a seed, and what it does not guarantee

`torch.manual_seed(42)` fixes the starting point of the random number generator: weight
initialization, shuffle order, augmentation — all repeat exactly. Without it, two identical runs
give accuracy that differs by ±1%, and you cannot know whether a change you made helped or it is noise.

What the seed does **not** guarantee: some GPU operations (cuDNN) are non-deterministic by nature
for speed. `torch.backends.cudnn.benchmark = True` (which speeds us up) increases this. So: a fixed
seed + compare experiments that differ by more than 0.5% — otherwise it is noise.

## 6.10 DataLoader — what happens under the hood

- **`num_workers=4`** — four processes (not threads) load and augment pictures in parallel while
  the GPU computes the previous batch. Without it the GPU "waits for the disk" and its utilization
  drops to 30%. On Windows every worker re-imports the script — so `if __name__ == "__main__":` is a must.
- **`pin_memory=True`** — the batch's memory is "locked" in RAM (cannot be swapped) so the copy to
  the GPU is a direct DMA. Together with `.to(device, non_blocking=True)` the copy overlaps with computation.
- **`shuffle=True`** only in training — so every epoch sees different batches. In evaluation the order does not matter.
- **`drop_last`** — not needed for us; BatchNorm copes with a small last batch.

## 6.11 What to record for every experiment

One table that will save you the whole results chapter:

| Experiment | Change | Epochs until stop | Val acc | Test acc | Macro-F1 | Time |
|---|---|---|---|---|---|---|
| 1 | baseline, no augmentation | | | | | |
| 2 | + augmentation | | | | | |
| 3 | + class weights | | | | | |
| 4 | + label smoothing | | | | | |
| 5 | Haar → DNN (real time) | — | — | — | — | FPS |

Experiment 1 is "weak" on purpose — so you have something to compare against. A results chapter
without a comparison is a list of numbers; with a comparison it is a story: "augmentation added
3.1%, class weights raised the F1 of disgust from 0.31 to 0.58".

## ✅ Check yourself — Chapter 6

1. Compute the class weight for all 7 classes using the counts in `data/README.md`, then normalize
   so the mean is 1.0. Which class gets the highest weight and what is its value?
2. With label smoothing ε=0.1 and K=7: what is the lowest possible loss (when the model outputs
   exactly the smoothed target)? Compare with 0 without smoothing.
3. Your friend suggests "filling up" the disgust class by copying every picture 16 times in training.
   Is this equivalent to class weights? What is the risk?
4. You added `RandomHorizontalFlip` to `build_eval_transform` by mistake. What happens to the test
   score in two consecutive runs of `evaluate.py`? And why does it not necessarily lower the accuracy?
5. Your training shows GPU utilization of 25% and CPU of 100%. What is the bottleneck and which parameter do you change?
6. On a computer with 4GB of GPU memory the training crashes with `CUDA out of memory`. Give three
   solutions ordered from cheapest to most expensive in terms of accuracy.

## 📚 Further reading — Chapter 6

- **PyTorch — Automatic Mixed Precision examples**: https://pytorch.org/docs/stable/notes/amp_examples.html
  The code in `trainer.py` comes from here. Read "Typical Mixed Precision Training".
- **PyTorch — CUDA semantics**: https://pytorch.org/docs/stable/notes/cuda.html — `pin_memory`, `non_blocking`, memory.
- **PyTorch — Datasets & DataLoaders tutorial**: https://pytorch.org/tutorials/beginner/basics/data_tutorial.html
- **torchvision — ImageFolder**: https://pytorch.org/vision/stable/generated/torchvision.datasets.ImageFolder.html —
  see `class_to_idx`, the source of the class-order trap.
- **torchvision — Transforms**: https://pytorch.org/vision/stable/transforms.html
- **When Does Label Smoothing Help?** (Müller, Kornblith, Hinton, 2019): https://arxiv.org/abs/1906.02629 — pages 1–3.
- **Kaggle FER-2013**: https://www.kaggle.com/datasets/msambare/fer2013 — also the public notebooks there, to see what others achieved (and why 65–70% is the range).
