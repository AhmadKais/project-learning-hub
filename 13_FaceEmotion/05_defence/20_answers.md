# Appendix — Answers to "Check yourself"

For the supervisor: the questions require calculation or reasoning, not memorization. A student who
answers 80% of them correctly understands what he is building. For the student: do not peek before
you tried. A wrong answer you understood is worth more than a right answer you copied.

## Chapter 2

1. Accuracy = 1,774/3,589 = **0.494**. Recall(happy) = **1.0** (all the happy were caught).
   Precision(happy) = 1,774/3,589 = **0.494**. F1(disgust) = **0** — recall 0, and precision is
   undefined (no "disgust" predictions) and defined as 0 (`zero_division=0`). The conclusion: an
   accuracy of 49% "sounds" reasonable and hides a worthless model; macro-F1 (~0.09) exposes it.
2. Column B is now 10+36+10 = 56. Precision(B) = 36/56 = **0.643**; Recall(B) = 36/40 = **0.900**;
   F1 = 2·0.643·0.9/(1.543) = **0.750**. Accuracy = (50+36+40)/150 = **0.840**.
   Notice: recall rose a lot, precision a little — because B still "absorbs" 20 foreign pictures.
3. The choice was made **using** the test, so the test is no longer independent — that is leakage
   (2.7). Out of 8 experiments, the best on the test is expected to be biased upward even by chance
   (noise ±1%). The right way: choose by validation, then run on the test **once** and report the
   number that comes out — even if it is lower.
4. Both low and close → **underfitting** (high bias). First rule out a pipeline bug (class mapping,
   normalization, a learning rate that vanished — section 16a.1), because 57% after full training is
   too low for this network; then: more epochs, a higher learning rate, and only at the end a bigger network.
5. Without a fixed seed the split is different on every run: (a) the validation accuracy of two
   experiments is not comparable, because it was measured on different pictures; (b) when continuing
   training from a checkpoint, pictures that were in validation move to training — leakage.

## Chapters 3–4

1. 128/255 = 0.502; (0.502 − 0.5077)/0.2550 = **−0.022**. A "middle" pixel becomes almost zero —
   exactly the goal of normalization.
2. z1 = 0.5·(−1)+0 = −0.5; h = ReLU(−0.5) = **0**; y = −1·0+1 = **1**; L = (1−1)² = **0**.
   dL/dz1 = dL/dh · ReLU′(−0.5) = (dL/dy·w2)·**0** = 0 ⇒ dL/dw1 = **0**. Special twice: the loss
   happens to be 0, but even if it were not — the neuron is "dead" (z1<0) and no gradient reaches w1, b1.
   This is the dead ReLU from section 4.8.
3. Uniform softmax: **1/7 = 0.143** for every class. CE = −ln(1/7) = **ln 7 = 1.946** for any label.
   A network before training (small random weights) gives roughly this — so the loss in the first
   iteration should be ≈1.95. If it is 5 or 0.3 — there is a bug. A free sanity check.
4. e³=20.09, e¹=2.72, e⁰=1 ⇒ sum 23.80 ⇒ p = **[0.844, 0.114, 0.042]**. L = −ln(0.844) = **0.170**.
   dL/dz = p − y = **[−0.156, 0.114, 0.042]**. The step w−lr·grad: logit 0 (negative gradient)
   **goes up**, logits 1 and 2 **go down**. The model is already right, so the steps are small.
5. `.grad` **accumulates** (`+=`) in every `backward()`. The order must guarantee that `backward` of
   iteration t does not see leftovers from t−1. "Before backward" makes that guarantee local and
   visible. "After step" works in a simple loop, but breaks when `step` is skipped (GradScaler skips
   when there is an inf) or when you accumulate gradients over several batches on purpose.
6. In AdamW the step is lr·m̂/√v̂ — the gradient is **normalized** by its historical size, so both
   weights move about the same amount (~lr). In SGD the first would move 1,000 times more. This is why
   Adam does not need a learning rate tuned per layer.
7. BatchNorm: in `eval()` it normalizes by `running_mean/var` collected in training instead of by the
   current batch statistics. Dropout: in `eval()` it becomes the identity — no neuron is switched off.

## Chapter 5

1. 4·50 − (10+10+10+10) = 200 − 40 = **160**. On a uniform window: 4·10 − 40 = **0**. This is a
   **Laplacian** kernel — detects a point/edge brighter than its surroundings; zero in smooth areas.
2. 3·3·32·64 = 18,432 + 64 biases = **18,496**. Without bias: **18,432**.
3. ⌊(12+2−3)/2⌋+1 = ⌊5.5⌋+1 = **6**. Without padding: ⌊(12−3)/2⌋+1 = 4+1 = **5**.
4. block1: 64→64, stride 1 ⇒ x and F(x) have the same shape (64×48×48) ⇒ direct addition. block2:
   x is 64×48×48 and F(x) is 128×24×24 ⇒ a 1×1 conv stride 2 is needed to match. Without it:
   `RuntimeError: The size of tensor a (24) must match the size of tensor b (48)`.
5. In `out = F(x)+x`, "do nothing" = F(x)=0 = zero weights — the easiest thing to learn (weight decay
   even pushes there). In `out = F(x)`, "do nothing" = learn the identity function through
   Conv→BN→ReLU→Conv→BN — requires very precise weights, and the network does not find them.
6. For example half the channels (32-64-128-256): parameters ≈ 4.9M/4 ≈ 1.2M (quadratic in channels);
   or removing block4 → ~1.2M. The risk: less "capacity" for subtle expressions (disgust, fear) ⇒ a
   drop of 1–3% in accuracy and in the F1 of the small classes; the benefit: higher FPS. A legitimate
   experiment for the alternatives chapter.

## Chapter 6

1. total/(7·count): angry 1.026, disgust 9.408, fear 1.001, happy 0.568, neutral 0.826, sad 0.849,
   surprise 1.293. Mean = 2.139 ⇒ normalized: angry 0.48, **disgust 4.40**, fear 0.47, happy 0.27,
   neutral 0.39, sad 0.40, surprise 0.60. Highest: disgust, 4.40.
2. The smoothed target: 0.9143 for the correct class, 0.01429 for each of the 6 others.
   L_min = −Σ y·ln y = −[0.9143·ln 0.9143 + 6·0.01429·ln 0.01429] = −[−0.0819 − 0.3642] = **0.446**.
   Without smoothing the minimum is 0. So with label smoothing the loss "does not go below 0.45" —
   and that is normal, not a bug.
3. In expectation, copying ×16 is equivalent to a weight of 16 in the loss (same contribution to the
   gradient). The difference: the copies are identical ⇒ the network sees the same 436 pictures 16
   times per epoch and memorizes them (overfitting on the class), and the epoch gets longer. Class
   weights are free. Copying becomes reasonable only together with random augmentation — then every copy is different.
4. Two runs will give slightly different scores (non-deterministic evaluation) — that alone makes it
   unfit for reporting. The accuracy does not necessarily drop: a horizontally flipped face is still a
   valid face the model saw in training. The problem is **reproducibility**, not accuracy.
5. The CPU is saturated and the GPU waits ⇒ loading/augmentation is the bottleneck. Raise
   `num_workers` (4→8 if there are cores), make sure `pin_memory=True`, and make sure the dataset is on an SSD.
6. (a) `--batch-size 64` — almost free (a slightly noisier gradient; you can lower lr accordingly);
   (b) make sure AMP is on — saves ~40% memory, free; (c) shrink the network (channels) — costs accuracy.
   Another option: accumulate gradients over 2 batches of 64 ⇒ an "effective batch" of 128.

## Chapters 7–8

1. Integral: [[2, 3], [5, 10]]. Sum of the whole picture = the last cell = **10** (= 2+1+3+4).
2. Detection: 0.98¹⁰ = **0.817**; false: 0.4¹⁰ = **1.05×10⁻⁴** ⇒ ~10 false detections per 100,000
   windows. Worse than 22 stages of 99.5%/50% (0.90 and 2.4×10⁻⁷) on both measures. Many "soft"
   stages beat a few "hard" ones — that is the cascade insight.
3. `minNeighbors=1`: boxes on hands, shirt folds, wall patterns; flickering. `15`: real faces
   disappear when you turn the head a little or move away (fewer windows agree).
4. One thread: 20+4+5+35 = 64 ms ⇒ **15.6 FPS**. Camera in a separate thread: 29 ms ⇒ theoretically
   34 FPS, in practice limited by the camera (30 FPS) and by `after(30)` ⇒ **~30 FPS**.
5. The Lock protects only the moment of swapping the reference. The GUI keeps using the array
   **after** the lock is released — and meanwhile the camera thread (and OpenCV, which recycles its
   internal buffer) writes the next frame into the same memory. `copy()` separates the lifetime of the
   GUI's array from the buffer's lifetime.
6. neutral = [N 0.9, H 0.1], happy = [H 0.9, N 0.1]. Frame 100 (4N+1H): H = (4·0.1+0.9)/5 = 0.26 ⇒
   neutral. 101 (3N+2H): H = (0.3+1.8)/5 = 0.42 ⇒ neutral. 102 (2N+3H): H = (0.2+2.7)/5 =
   **0.58 ⇒ happy**. The label switches at frame 102, two frames after the change (~80 ms at 25 FPS).

## Chapter 9

1. Formally yes — the View knows OpenCV's channel order. Alternative: the Controller (or
   `FrameAnnotator`) returns a ready RGB/PIL image, and the View only displays. The cost: one more
   conversion in the controller and a View dependency on PIL. Both approaches are accepted — the
   point is that you can explain the choice and the boundary.
2. Without `@abstractmethod`, `FaceDetector()` is created successfully; `detect` (body = docstring
   only) returns `None`; `detect_largest` will crash at `max(None)` — a `TypeError` **at runtime**, on
   the first frame. With the abstract, the error is at creation time, with a clear message. "Fail early".
3. `a is b` ⇒ **True** (Singleton). `SessionRepository(a) is SessionRepository(b)` ⇒ **False** — a
   normal class, a new object on every call (but both wrap the same `Database`).
4. **Zero.** `executemany` runs inside one transaction in `with db.connection()`; the exception
   triggers `rollback()`. Atomicity — all or nothing.
5. No — there are indexes only on `session_id` and `timestamp` ⇒ a full scan. If the query is
   frequent: `CREATE INDEX idx_samples_conf ON emotion_samples(confidence)`. And check:
   `EXPLAIN QUERY PLAN SELECT ...` shows `SCAN` vs. `SEARCH USING INDEX`.
6. Changes: a new file `app/vision/mediapipe_detector.py` (inherits `FaceDetector`, implements
   `detect`), one line in `create_detector`, a new value in `config.DETECTOR` and the option in the
   View's combobox. **Does not** change: `AppController._on_frame`, `FacePreprocessor`,
   `EmotionPredictor`, the DB, the tests. If you had to touch the controller — your Strategy is not real.
