# Part B — Build the code

The next chapters follow `TASKS.md`. For every stage: what to write, the pieces worth knowing,
and how to check. The skeleton code already has, in every function, the list of steps — here is
the **why**, and the details that are easy to trip on.

Working rule: open the file, read the docstring, write, run the stage's test, and only then
continue. Do not write five files and then run.

# Chapter 10 — Stage 1: environment and camera

## 10.1 Installation and GPU check

After installing according to `README.md`, run:

📄 **GPU check**
```python
import torch
print(torch.__version__)                 # for example 2.4.0+cu121  <- the "cu" means CUDA
print(torch.cuda.is_available())         # must be True
print(torch.cuda.get_device_name(0))     # the card's name
print(torch.cuda.get_device_properties(0).total_memory // 2**20, "MB")
```

If `False`: you installed the CPU version of torch (no `+cu` in the version). Uninstall and
reinstall with the `--index-url` from the README. This is `print_device_banner()` in `train.py` —
write it first, it will serve you in every run.

## 10.2 `CameraService` — `app/vision/camera.py`

The idea is in section 8.2. Points for the implementation:

- `start()` — after `VideoCapture(index)` you **must** check `isOpened()`. A camera taken by Zoom
  does not raise an error — it just returns `False` on every read.
- `_reader_loop()` — `ok, frame = self._capture.read()`; only if `ok`, inside `with self._lock:`
  store the frame. Never store `None`.
- `read()` — inside the lock: `return None if self._latest_frame is None else self._latest_frame.copy()`.
- `stop()` — first `_running = False`, then `join(timeout=1.0)`, and only then `release()`.
  In the opposite order the thread will try to read from a closed camera.
- `daemon=True` on the thread — otherwise closing the window leaves the program hanging.

📄 **Manual check (a temporary script, not part of the project)**
```python
from app.vision.camera import CameraService
import cv2
cam = CameraService(); cam.start()
while True:
    frame = cam.read()
    if frame is not None:
        cv2.imshow("test", frame)
    if cv2.waitKey(1) == 27: break        # ESC
cam.stop(); cv2.destroyAllWindows()
```

# Chapter 11 — Stage 2: face detection

## 11.1 `FaceDetection` — `app/models/detection.py`

- `with_margin()` — notice the function returns a **new** object and does not change the existing
  one (immutable style). Clipping to the frame: `new_w = min(w + 2*dx, frame_w - new_x)`.
  The test `test_margin_is_clipped_to_the_frame` catches going outside the frame.
- `crop()` — numpy: `frame[y:y+h, x:x+w]`. **Rows first, columns second** — y before x.
  This is the classic OpenCV mistake.

## 11.2 `HaarCascadeDetector` — `app/vision/haar_detector.py`

- `cv2.CascadeClassifier(path)` with a wrong path **does not raise an error**. Check
  `self._cascade.empty()` and raise `RuntimeError` yourself, otherwise you will waste an hour on
  "why does it not find faces".
- `detectMultiScale` returns a numpy array of rows `[x, y, w, h]` — or an empty tuple. Convert
  every value with `int()` before creating `FaceDetection`; numpy int64 will cause problems in SQLite later.

## 11.3 `detect_largest()` and `create_detector()` — `face_detector.py`

- `max(detections, key=lambda d: d.area)` — and do not forget the empty case.
- In `create_detector`, import the concrete classes **inside** the function. If you import at the
  top, `haar_detector.py` imports `face_detector.py` which imports `haar_detector.py` — a circular
  import, and Python fails with a confusing message.

**Exit condition:** a green box around the face in `cv2.imshow`, and a time measurement:

📄 **Measuring detection time**
```python
import time
t = time.perf_counter()
faces = detector.detect(frame)
print(f"{(time.perf_counter() - t) * 1000:.1f} ms")
```

Write the number down. It goes in the book.

# Chapter 12 — Stage 3: data and network

## 12.1 `FacePreprocessor.to_model_input()`

The order from chapter 3: grayscale → `resize` to 48×48 with `INTER_AREA` (best for shrinking) →
`equalizeHist` → `/255` → `(x-mean)/std` → `reshape(1, 1, 48, 48)`.
`astype(np.float32)` **before** the division — otherwise numpy divides in uint8 and gets zeros.

`build_eval_transform()` in `dataset.py` must do the very same steps (Grayscale → Resize → `EqualizeHist`
→ ToTensor → Normalize), and `build_train_transform()` must equalize too. The new test
`test_eval_transform_matches_realtime_preprocessing` feeds one face through both paths and demands the
same numbers — it is your protection against train/serve skew (section 3.2).

## 12.2 `dataset.py` — the class-order trap

`torchvision.datasets.ImageFolder` numbers folders alphabetically:
`angry=0, disgust=1, fear=2, happy=3, neutral=4, sad=5, surprise=6`.
Our `Emotion`: `sad=4, surprise=5, neutral=6`. Three classes are **swapped**.

📄 **Index remapping in `FER2013Dataset`**
```python
self._folder = ImageFolder(root, transform=transform)
# ImageFolder index -> Emotion value
self._remap = {idx: Emotion[name.upper()].value
               for name, idx in self._folder.class_to_idx.items()}

def __getitem__(self, index):
    image, folder_label = self._folder[index]
    return image, self._remap[folder_label]
```

`Emotion[name.upper()]` finds the member by its name — `Emotion["HAPPY"]` — so the mapping is
correct even if someone adds a folder. If you skip this step, the model will "train great" and then
call every sad face "neutral". No test catches this — only eyes.

## 12.3 `build_dataloaders()`

- `random_split` with `generator=torch.Generator().manual_seed(config.RANDOM_SEED)` — otherwise the
  split is different on every run and experiments cannot be compared.
- The validation set needs the **eval** transform, not the one with augmentation. With `random_split`
  both parts share the same `Dataset`; the simple solution: build **two** `FER2013Dataset` on the same
  folder (one per transform), do `random_split` on indices, and make a `Subset` from each.
- `pin_memory=True` only when CUDA is available; `num_workers=4` — on Windows this requires the main
  code to be under `if __name__ == "__main__":` (already so in `train.py`).

## 12.4 `network.py`

Follow the table in section 5.5. `nn.Conv2d(in, out, kernel_size=3, stride=stride, padding=1, bias=False)`
— `bias=False` because the BatchNorm after it cancels it anyway. `padding=1` keeps the size when
stride=1. The shortcut: an empty `nn.Sequential()` when the shapes are equal, otherwise
`Conv2d(in, out, 1, stride, bias=False)` + `BatchNorm2d(out)`.

**Exit condition:** `pytest tests/test_network.py tests/test_preprocessor.py -v` all green.
`EmotionNet().count_parameters()` = 4,900,551. Write the number down — it goes in the architecture chapter.
