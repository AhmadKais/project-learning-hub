# Chapter 13 — Stage 4: training on the GPU and evaluation

## 13.1 `ModelTrainer.__init__`

Four objects: `criterion`, `optimizer`, `scheduler`, `scaler`. The scheduler:

📄 **Warm-up + cosine**
```python
warmup = torch.optim.lr_scheduler.LinearLR(opt, start_factor=0.1, total_iters=config.WARMUP_EPOCHS)
cosine = torch.optim.lr_scheduler.CosineAnnealingLR(opt, T_max=epochs - config.WARMUP_EPOCHS)
self.scheduler = torch.optim.lr_scheduler.SequentialLR(opt, [warmup, cosine], milestones=[config.WARMUP_EPOCHS])
```

Why warm-up: at the start of training the weights are random and the gradients are huge; a full
learning rate from the first step "blows up" the network. Three epochs of a gradually rising rate stabilize it.

## 13.2 The loop — what every examiner will ask about

Six lines you must be able to explain one by one (see the `train_one_epoch` docstring):

1. `optimizer.zero_grad()` — PyTorch **accumulates** gradients. Without resetting, the current step
   is added to the previous one. `set_to_none=True` is faster than resetting to zeros.
2. `outputs = model(images)` — forward: the input passes through all the layers.
3. `loss = criterion(outputs, labels)` — how wrong we were (cross-entropy, section 4.4).
4. `scaler.scale(loss).backward()` — backward: compute the gradient for every weight.
5. `scaler.step(optimizer)` — update the weights (AdamW).
6. `scaler.update()` — adjust the AMP multiplier for the next step.

Accuracy within a batch: `(outputs.argmax(dim=1) == labels).sum().item()`.
`.item()` takes a Python number out of a one-element tensor — without it you accumulate tensors on
the GPU and the memory fills up.

## 13.3 `validate()` — only two differences

`self.model.eval()` and `@torch.no_grad()`. The first turns off Dropout/BatchNorm-training
(section 4.6); the second tells PyTorch not to keep information for backward — saves half the
memory and doubles the speed. No `zero_grad`, no `backward`, no `step`.

## 13.4 `fit()` and early stopping

📄 **Skeleton of the outer loop**
```python
epochs_without_improvement = 0
for epoch in range(1, epochs + 1):
    start = time.perf_counter()
    train = self.train_one_epoch(); val = self.validate(); self.scheduler.step()
    # ... append to history, print one line ...
    if val["acc"] > self.best_val_acc:
        self.best_val_acc = val["acc"]; epochs_without_improvement = 0
        self.save_checkpoint(config.BEST_MODEL_PATH, epoch, val["acc"])
    else:
        epochs_without_improvement += 1
        if epochs_without_improvement >= config.EARLY_STOPPING_PATIENCE:
            print("early stopping"); break
self.save_checkpoint(config.LAST_MODEL_PATH, epoch, val["acc"])
```

The print line for every epoch should contain: epoch number, train loss/acc, val loss/acc, the
current lr (`self.optimizer.param_groups[0]["lr"]`) and time. **Keep this output** — a screenshot
of it goes in the book.

## 13.5 What to expect

A healthy run looks roughly like this: epoch 1 ≈ 35–40% validation, epoch 5 ≈ 55%, epoch 15 ≈ 63%,
then slow improvement to 66–69% around epoch 30–40, then early stopping. If at epoch 3 you are still
at 25% (= always guessing "happy") — check the class mapping and the normalization.
If the loss is `nan` — the learning rate is too high or AMP overflowed; try `--lr 3e-4`.

## 13.6 `ModelEvaluator` and `evaluate.py`

A loop like `validate()` but you collect **all** the predictions into lists `y_true`, `y_pred`, and then:

📄 **Metrics with scikit-learn**
```python
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
names = [e.name for e in Emotion]
report = classification_report(y_true, y_pred, target_names=names, output_dict=True, zero_division=0)
matrix = confusion_matrix(y_true, y_pred, labels=list(range(7)))
```

Normalized matrix: `matrix / matrix.sum(axis=1, keepdims=True)`. Drawing: `plt.imshow` +
`plt.xticks/yticks` with the names + write the value in every cell in a double loop. Save in `reports/`.

**Exit condition:** accuracy ≥ 65% on the test set, and the three `reports/` files exist.
Open the confusion matrix and check: which pair of emotions gets mixed the most? That is a paragraph in the book.

# Chapter 14 — Stage 5: real time

## 14.1 `EmotionPredictor.load_model()`

`torch.load(path, map_location=self.device)` — `map_location` lets you load a model trained on a
GPU on a computer without a GPU. After `load_state_dict`: `.to(device)` and then `.eval()`.
**Without `eval()` — random predictions** (section 4.6). If the file is missing: a clear message,
`is_ready = False`, and the application still opens and shows the camera.

## 14.2 `predict()`

`torch.from_numpy(arr).to(device)` → `model(...)` → `softmax(dim=1)[0]` → `.cpu().numpy()`.
Note that pre-processing already returned shape `(1,1,48,48)` — a batch of one.
`probs.argmax()` returns a numpy int — wrap it in `int()` before `Emotion(...)`.

## 14.3 `TemporalSmoother.update()`

`self._window.append(probs)`; `mean = np.mean(np.stack(self._window), axis=0)`;
`return Emotion(int(mean.argmax())), float(mean.max())`. The `deque(maxlen=N)` drops the old ones
by itself. The tests in `test_smoothing.py` define the behavior exactly.

## 14.4 `FrameAnnotator`

`cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)`; for the text background a filled rectangle
(`thickness=-1`) above the box; `cv2.putText(img, text, (x, y-8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)`.
Work on `frame.copy()` — the original frame stays clean.

## 14.5 `AppController._on_frame()` — first version

At this stage it is fine to show with `cv2.imshow` and not in Tkinter. The goal: the full pipeline
works and you measure FPS. `FpsCounter.tick()` on every frame; `value` = `(len-1)/(last-first)`.

**Exit condition:** `pytest tests/test_smoothing.py` green, FPS ≥ 15 shown on the frame, and the
label is stable. Record a short video — you now have a demo for an emergency in the defense.

# Chapter 15 — Stage 6: database, UI, export

## 15.1 `Database`

The code in the docstring is almost complete. Two things: `row_factory = sqlite3.Row` gives access
`row["emotion"]` instead of `row[3]`; `@contextmanager` turns a function with `yield` into something
you can write as `with db.connection() as conn:` — everything after the `yield` runs when leaving the block.

## 15.2 Repositories

- Always `?` placeholders: `conn.execute("INSERT ... VALUES (?, ?)", (a, b))`. Never an f-string
  with values — that is SQL injection, and you will be asked about it.
- `datetime` → `isoformat()` when writing, `datetime.fromisoformat()` when reading.
- `probabilities` → `json.dumps(list(map(float, probs)))` — numpy float32 is not JSON-serializable without `float()`.
- `emotion` is stored as `int(emotion)` and read as `Emotion(row["emotion"])`.
- The function that maps `Row` → `Session` will appear in 3 places. Write it once (`_row_to_session`).

## 15.3 Views

- `VideoFrame.show()`: `cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)` → `Image.fromarray` →
  `ImageTk.PhotoImage` → `label.configure(image=photo)` → **`self._photo = photo`**.
  The last line: without a live reference, Python frees the image and the label shows nothing.
- `ChartFrame`: create the 7 `Line2D` once in `__init__` (`ax.plot([], [], color=..., label=...)`).
  In `push()`: `line.set_data(range(len(dq)), list(dq))`, `ax.set_xlim(0, history_size)`,
  `canvas.draw_idle()`. And only every third frame — matplotlib is slow.
- Tk color from BGR: `"#%02x%02x%02x" % (b_g_r[2], b_g_r[1], b_g_r[0])`.
- Buttons: `state="disabled"`/`"normal"` in `set_running()`.

## 15.4 `SessionController` and `SessionExporter`

`record()` filters by `MIN_CONFIDENCE_TO_STORE` and then collects; `flush()` at 60 and also in
`end_session()`. The CSV: open with `encoding="utf-8-sig"` — the BOM makes Excel recognize Hebrew.
The sample rows, an empty line, then a summary block.

**Exit condition:** `pytest -v` all green; the full application; the CSV opens in Excel; in DB Browser
you see a session with samples.

# Chapter 16 — Stage 7: alternatives, tests, documentation

- `DnnFaceDetector` — following the docstring. Then **your own comparison table**: Haar vs. DNN —
  time per frame, face in profile (yes/no), low light, glasses. 4 rows you measured. That is the
  "alternatives analysis" chapter with data, not opinions.
- Your own tests: `FpsCounter`, `Session.emotion_distribution`, `SessionExporter`.
  A good test = a name that explains what is tested + one clear `assert`.
- UML according to `docs/UML.md`, the book according to `docs/PROJECT_BOOK_MAP.md`.

💡 At the end of every stage: `git commit -m "stage N: ..."`. The Git history is proof that you wrote
the code over time, and did not receive it ready.
