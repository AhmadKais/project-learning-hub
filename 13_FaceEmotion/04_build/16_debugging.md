# Chapter 16a — Troubleshooting: the error, the cause, the fix

Every error here will happen to you. The table saves hours — but read the "why" too, because in
the defense "what was the hardest problem and how did you solve it" is a standard question.

## 16a.1 PyTorch / GPU errors

| Message | Cause | Fix |
|---|---|---|
| `torch.cuda.is_available()` returns `False` | The CPU version of torch was installed (no `+cu` in the version), or an old driver | Reinstall with `--index-url .../cu121`; update the NVIDIA driver |
| `Expected all tensors to be on the same device` | The model is on the GPU and the batch on the CPU (or the opposite) | `.to(device)` on **every** tensor that enters the model, including `class_weights` |
| `CUDA out of memory` | Batch too big for the card's memory | `--batch-size 64`; make sure AMP is on; close other programs using the GPU |
| `mat1 and mat2 shapes cannot be multiplied (Nx18432 and 512x7)` | You forgot global average pooling — Flatten on 512×6×6 | `nn.AdaptiveAvgPool2d(1)` before the Flatten |
| `The size of tensor a (24) must match ... (48)` inside `ResidualBlock` | Identity shortcut when the shapes differ | 1×1 convolution with stride in the shortcut (section 5.4) |
| `loss` is `nan` from the first epoch | Learning rate too high / AMP overflow / `log(0)` | `--lr 3e-4`; check there is no double Softmax; make sure `GradScaler` is used |
| Accuracy stuck at ~25% (= frequency of "happy") | The network guesses one class: wrong label mapping, wrong normalization, or lr=0 | Print `dataset._remap`; check `mean/std`; print `optimizer.param_groups[0]["lr"]` |
| Train accuracy 95%, validation 60% | Overfitting | Make sure augmentation runs **in training** (print an example), Dropout exists, early stopping works |
| Validation accuracy great, in real time everything is "neutral" | Train/serve skew: different pre-processing, or you forgot `eval()` | Compare `to_model_input` and `build_eval_transform` line by line; `model.eval()` |
| `RuntimeError: DataLoader worker ... exited unexpectedly` (Windows) | `num_workers>0` without `if __name__ == "__main__"` | Main code under the guard; or `NUM_WORKERS=0` for debugging |
| Training is slow and `nvidia-smi` shows 20% utilization | The GPU waits for data loading | `num_workers=4`, `pin_memory=True`; make sure the dataset is on an SSD |
| `KeyError: 'model_state'` on load | An old/other checkpoint file, or you saved the `state_dict` directly | Always save the dictionary from section 6.4; load by key |

## 16a.2 OpenCV / camera errors

| Message / symptom | Cause | Fix |
|---|---|---|
| `cap.read()` always returns `(False, None)` | The camera is taken (Zoom/Teams), or wrong index | Close applications; try `CAMERA_INDEX=1` |
| The detector "finds nothing" with no error | Wrong XML path — `CascadeClassifier` is silent | Check `cascade.empty()` and raise an error yourself |
| `error: (-215:Assertion failed) !ssize.empty()` in `resize` | Empty crop — the box is outside the picture or w/h=0 | `with_margin` must clip to the borders; skip empty boxes |
| Colors in the Tk window are "blue" | BGR shown as RGB | `cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)` before `Image.fromarray` |
| `putText` shows `????` | OpenCV does not render Hebrew | English on the frame, Hebrew in the Tk label |
| `crop` gives a "strange" picture | x/y swapped — numpy is `[rows, columns]` | `frame[y:y+h, x:x+w]` |
| Division gives zeros in pre-processing | Division of `uint8` | `astype(np.float32)` **before** `/255` |

## 16a.3 Tkinter errors

| Symptom | Cause | Fix |
|---|---|---|
| The label is gray, no video, no error | The `PhotoImage` was collected by the GC | `self._photo = photo` after `configure(image=...)` |
| The window freezes when you click "Start" | A `while` loop or `sleep` in Tk's thread | `root.after(30, ...)` |
| `RuntimeError: main thread is not in main loop` | Updating a widget from the camera thread | The camera thread only stores a frame; only `_on_frame` (via `after`) touches the GUI |
| The chart causes 3 FPS | `canvas.draw()` on every frame + recreating the Figure | Lines created once; `set_data` + `draw_idle` every third frame |
| Closing the window leaves a hanging process | Non-daemon thread / camera not released | `daemon=True`; `WM_DELETE_WINDOW` → `on_close` → `camera.stop()` |

## 16a.4 SQLite / test errors

| Message | Cause | Fix |
|---|---|---|
| `sqlite3.InterfaceError: Error binding parameter` | numpy int64 / float32 in the parameters | `int()`, `float()`, `json.dumps(list(map(float, ...)))` |
| `FOREIGN KEY constraint failed` | A `session_id` that does not exist, or wrong write order | Create the session before the samples; make sure the id comes back from `lastrowid` |
| Deleting a session leaves samples | `PRAGMA foreign_keys` was not turned on | In `get_connection()` on **every** connection |
| `database is locked` | Two connections open at the same time | Always through `with db.connection()`; do not leave a connection open |
| A test passes alone and fails with the others | A Singleton leaks between tests | `Database._instance = None` in the fixture (already in `conftest.py`) |
| `ModuleNotFoundError: app` in pytest | Running from the wrong folder | Run `pytest` from the project root; `conftest.py` adds the path |

## 16a.5 A general debugging method

1. **Read the last line** of the traceback, and then the first line **that is in your code** (not in a library).
2. **Print shapes**: `print(x.shape, x.dtype, x.min(), x.max())` at the entry and exit of every step.
   90% of ML bugs are an unexpected shape, type or range.
3. **Isolate**: run the problematic step alone on one fixed input (a saved picture, not the camera).
4. **Shrink**: `--epochs 1`, `batch_size=8`, 100 pictures. A bug found in 10 seconds and not in 10 minutes.
5. **Document**: every bug that took you more than half an hour — one line in `TASKS.md`: what it was,
   how you found it, what you learned. This is the "challenges" chapter in the book, and the answer to
   "what was the hardest part".
