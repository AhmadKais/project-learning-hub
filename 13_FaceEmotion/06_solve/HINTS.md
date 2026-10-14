# FaceEmotion — hints, checks and traps, stage by stage

Use this file when you are **stuck** on a function of your skeleton. For each hard function:

- **Learn it in** — the theory section, notebook and exercise that teach the idea.
- **Hints** — hidden. Open one at a time: 💡 a nudge, 🔧 the steps.
- **Check yourself** — numbers to compare against before you run the tests.
- **Traps** — the mistakes that make a test fail (or pass while the program is wrong).

`CHECKLIST.md` (next to this file) lists **every** function you have to write. Most docstrings in your skeleton
already contain the code shape; `04_build/10_build_part1.md` and `13_build_part2.md` give every step and
`04_build/16_debugging.md` the common errors. This file is for when those are not enough.

> **The working loop.** One function → run **its** test (`pytest tests/test_preprocessor.py -k margin -v`) →
> green → commit → next. Never start a 50-epoch training run before the shape tests are green.

---

## Stage 1 — Environment and camera

### `CameraService` — a thread that keeps only the newest frame

**Learn it in:** theory `07_detection_realtime` §8.2

<details><summary>🔧 Hint — the reader loop</summary>

```
while self._running:
    ok, frame = self._capture.read()
    if ok:
        with self._lock:
            self._latest_frame = frame
```

`read()` takes the lock too and returns `self._latest_frame.copy()` (or `None`). `stop()`: `_running = False`,
`self._thread.join(timeout=1.0)`, `self._capture.release()`, `self._latest_frame = None`.
</details>

**Traps:** returning the frame itself instead of a copy (the reader overwrites it while you draw) · forgetting
`daemon=True` (the program never exits) · camera index: try 0, then 1, if the laptop has two cameras.

---

## Stage 2 — Face detection

**Learn it in:** theory `07_detection_realtime` §7.1–7.4 · notebook `04_detection_and_realtime` §1–2 · exercise **ex11**

### `FaceDetection.with_margin`

<details><summary>🔧 Hint</summary>

```
frame_h, frame_w = frame_shape[:2]
dx, dy = int(self.w * margin), int(self.h * margin)
x, y = max(0, self.x - dx), max(0, self.y - dy)
w = min(frame_w, self.x + self.w + dx) - x          # the right edge, clipped, minus the new left edge
h = min(frame_h, self.y + self.h + dy) - y
return FaceDetection(x, y, w, h, self.confidence)
```
</details>

**Check yourself** (frame 640 × 480, margin 0.10):

| box (x, y, w, h) | with margin |
|---|---|
| (10, 10, 100, 100) | (0, 0, 120, 120) — clipped at the top-left |
| (600, 400, 100, 100) | (590, 390, 50, 90) — clipped at the right and bottom |

**Traps:** `frame_shape` is **(height, width)** — the other way round from `(x, y)` · `area` is a `@property`:
`detection.area`, not `detection.area()` · a numpy image is indexed `[y, x]`: `frame[y:y+h, x:x+w]`.

### `HaarCascadeDetector`

A wrong cascade path does **not** raise — `CascadeClassifier` just detects nothing. Check `self._cascade.empty()`
and raise. `detectMultiScale` returns an empty **tuple** when there is no face, so `for (x, y, w, h) in boxes:` is
the safe way to loop. Your `requirements.txt` pins OpenCV 4.10 — keep it: OpenCV 5 removed `CascadeClassifier`.

---

## Stage 3 — Data and model

**Learn it in:** theory `03_images_nn` §3.1–3.3, `05_cnn` §5.2–5.6, `06_data_training` §6.1, §6.8 · notebooks
`01_images_and_data`, `02_neurons_to_resnet` · exercises **ex01, ex06, ex07**

### `to_model_input` and the two transforms — the train == serve rule

Real time: grey → resize 48 × 48 → **equalizeHist** → /255 → (x − 0.5013) / 0.2916 → shape (1, 1, 48, 48).
Training: the **same** steps, through torchvision: `Grayscale`, `Resize`, `EqualizeHist`, `ToTensor` (= /255),
`Normalize`. `test_eval_transform_matches_realtime_preprocessing` sends one face through both and compares.

**Check yourself:** `to_model_input` on any 100 × 100 BGR face returns `float32`, shape `(1, 1, 48, 48)`, values
roughly between −1.7 and +1.7 (0 → −0.5013 / 0.2916 = −1.72, 255 → +1.71).

**Trap:** leaving `EqualizeHist` out of the training transforms. Nothing crashes — the model is simply shown
high-contrast faces in real time that it never saw in training, and the accuracy you measured is not the accuracy
you get.

### `FER2013Dataset` — the label remap

ImageFolder numbers the folders **alphabetically** (angry 0, disgust 1, fear 2, happy 3, **neutral 4**, sad 5,
surprise 6); `Emotion` is ANGRY 0 … SAD 4, SURPRISE 5, **NEUTRAL 6**. The docstring builds the lookup list.

**Check yourself:** `class_counts()` on the training folder, in `Emotion` order: angry 3995, disgust 436, fear 4097,
happy 7215, sad 4830, surprise 3171, neutral 4965. If neutral and sad look swapped, the remap is wrong.

### `ResidualBlock` and `EmotionNet`

The docstrings contain every layer. **Check yourself:**

```
EmotionNet().count_parameters()                   4,900,551
ResidualBlock(64, 64, 1)    parameters               73,984     (theory §5.6)
ResidualBlock(64, 128, 2)   parameters              230,144     (with the 1x1 shortcut)
EmotionNet()(torch.randn(4, 1, 48, 48)).shape      torch.Size([4, 7])
```

**Traps:** adding the shortcut **after** the last ReLU · a softmax inside `forward` (`test_network_returns_logits`
catches it) · `super().__init__()` must stay the first line of every `__init__`.

---

## Stage 4 — Full training on the GPU, and evaluation

**Learn it in:** theory `06_data_training` §6.2–6.7, §6.10 · notebook `03_training_loop` · exercises **ex02–ex05,
ex08–ex10**

### `compute_class_weights`

**Check yourself** — for the counts above (Emotion order), normalised to mean 1:

```
angry 0.48   disgust 4.40   fear 0.47   happy 0.27   sad 0.40   surprise 0.60   neutral 0.39
```

A mistake on a disgust face costs 16 × more than one on a happy face (4.40 / 0.27).

### `ModelTrainer.__init__` and `fit`

The `__init__` comment now contains the scheduler code (warm-up with `LinearLR`, then `CosineAnnealingLR`, joined
by `SequentialLR`). The learning rate should print as 0.0001, 0.0004, 0.0007, 0.001 in epochs 1–4 and fall to
almost 0 by epoch 50.

<details><summary>🔧 Hint — the bookkeeping in <code>train_one_epoch</code></summary>

```
total_loss, correct, seen = 0.0, 0, 0
... inside the loop, after the optimiser step:
total_loss += loss.item() * labels.size(0)
correct    += (outputs.argmax(1) == labels).sum().item()
seen       += labels.size(0)
return {"loss": total_loss / seen, "acc": correct / seen}
```

`validate` is the same loop inside `with torch.no_grad():`, after `self.model.eval()`, without the three optimiser
lines.
</details>

**Traps:** `model.eval()` forgotten in `validate` (dropout stays on, the validation accuracy jumps around) ·
`scheduler.step()` once per **epoch**, not per batch · use `torch.amp.GradScaler("cuda", ...)` and
`torch.autocast(self.device.type, ...)` — the `torch.cuda.amp` spelling is deprecated · on a CPU-only laptop, train
for 2–3 epochs to test the code, then run the full training on the GPU.

**Check yourself:** within the first three epochs the validation accuracy must climb clearly above 0.25. About 0.25
is what a model gets that answers "happy" for every face (a quarter of FER-2013 is happy) — if it sits there, check
that the class weights reach the loss and that the remap is right.

---

## Stage 5 — Real-time integration

**Learn it in:** theory `07_detection_realtime` §8.1–8.6 · notebook `04` §3–4 · exercise **ex12**

- `Predictor.predict`: `torch.softmax(logits, dim=1)` — the network returns logits. Wrap the call in
  `with torch.no_grad():`.
- `TemporalSmoother.update`: append, `np.mean(self._window, axis=0)`, return `(Emotion(argmax), max)`. **Average
  the probabilities, do not vote** — `test_probabilities_are_averaged_not_voted`.
- `FpsCounter.value` (a property): `(len - 1) / (last - first)`; fewer than two ticks → 0.0.
- `_on_frame`: read → detect → crop → predict → smooth → annotate → show → `self.root.after(config.UI_REFRESH_MS, self._on_frame)`.
  Never `while True` in Tkinter (theory §8.3).

**Check yourself:** `pytest tests/test_smoothing.py -v` → 5 passed. In the app, hold a steady smile: the label
should not change more than twice a second.

---

## Stage 6 — Database, UI and export

**Learn it in:** the docstring at the top of `repositories.py` (four shapes cover every method)

- `SampleRepository`: write one helper that turns a sample into a row tuple
  `(session_id, timestamp.isoformat(), int(emotion), confidence, x, y, w, h, json.dumps(probabilities))` and use it
  in both `add` and `add_many` (`executemany`).
- Read back: `Emotion(r["emotion"])`, `box=(r["box_x"], r["box_y"], r["box_w"], r["box_h"])`,
  `json.loads(r["probabilities"])`.
- `emotion_counts`: `{Emotion(r[0]): r[1] for r in rows}`.
- `delete` on a session removes its samples because of `ON DELETE CASCADE` — **only** if
  `PRAGMA foreign_keys = ON` was run on that connection.

**Check yourself:** `pytest -v` fully green (23 tests).

**Traps:** `json.dumps` of a numpy array fails — convert with `[float(p) for p in probabilities]` · `float32`
confidences from numpy: `float(confidence)` before storing.

---

## Stage 7 — Alternatives, tests, the book

- `DnnFaceDetector`: download the two files listed in `data/README.md`; the boxes come back as fractions (0–1) —
  multiply by `(w, h, w, h)` and convert `(x1, y1, x2, y2)` to `(x, y, width, height)`.
- The Haar vs DNN table: the same 30-second video for both, measuring ms per frame, faces found in profile, faces
  found in dim light.

---

## When nothing works

| Symptom | Likely cause |
|---|---|
| `CUDA out of memory` | `--batch-size 64`; close other GPU programs |
| `loss` is `nan` from epoch 1 | learning rate too high, softmax applied twice, or the `GradScaler` missing |
| validation accuracy stuck at ≈ 0.25 | every face predicted "happy" — class weights not passed to the loss, or the label remap wrong |
| great test accuracy, poor in the app | train/serve skew — compare `to_model_input` with the eval transform (the test does) |
| the box is on the shoulder | `frame[x:..., y:...]` instead of `frame[y:..., x:...]` |
| the window freezes | a `while True` loop or a slow call inside the Tkinter thread |
| `AttributeError: module 'cv2' has no attribute 'CascadeClassifier'` | OpenCV 5 got installed — `pip install -r requirements.txt` again (it pins 4.10) |
| a test passes alone, fails with the others | `Database._instance` left over — see `tests/conftest.py` |
