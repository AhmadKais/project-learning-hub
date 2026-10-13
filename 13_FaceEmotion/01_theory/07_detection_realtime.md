# Chapter 7 — Face detection

## 7.1 Haar Cascade (Viola–Jones, 2001)

The detector we use is from 2001 — and still works great on frontal faces, because of three ideas:

1. **Haar features** — simple black and white rectangles. "The eye area is darker than the cheeks
   below it" is a two-rectangle feature. "The bridge of the nose is brighter than both sides" is a
   three-rectangle feature. The sum of pixels in the white rectangle minus the sum in the black one.
2. **Integral image** — a table where every cell holds the sum of all pixels above it and to its left.
   With it, the sum of **any** rectangle is computed with 4 memory reads, no matter its size. This is
   what makes the detector fast.
3. **Cascade** — instead of checking 6,000 features on every window, check the first 2 features.
   If the window fails — it is not a face, move on. Only windows that passed are checked on 10 features,
   then 25, then 50... Most of the picture (wall, hair, shirt) is rejected in the first stage within
   microseconds. Which features and in what order — was chosen with the **AdaBoost** algorithm on
   thousands of pictures, once, by the OpenCV developers. You get the result as an XML file.

📄 **Integral image — rectangle sum with 4 reads**
```text
picture:           integral (sum up to each cell):
 1 2 3             1  3  6
 4 5 6             5 12 21
 7 8 9            12 27 45

sum of rectangle [5 6; 8 9] = I(D) - I(B) - I(C) + I(A)
                            = 45 - 6 - 12 + 1 = 28   (check: 5+6+8+9 = 28)
```

The parameters in `config.py`:

- `scaleFactor=1.1` — the detector looks for faces of different sizes; each round it enlarges the window by 10%.
- `minNeighbors=5` — how many overlapping windows must "agree" for it to count as a face. Low = more
  false detections, high = misses faces.
- `minSize=(60,60)` — faces smaller than this are ignored. Saves time.

## 7.2 The alternative: a DNN detector

OpenCV also comes with a small network (SSD on ResNet-10) trained for face detection. It is 2–3
times slower than Haar but catches faces in profile, with sunglasses, in side lighting. In the
project both detectors inherit from the same abstract class `FaceDetector`, so switching between
them is one line in `config.py` — and in the project book this is the "alternatives analysis"
with a comparison table you measured yourself.

## 7.3 The cascade — why it is so fast, in numbers

A 640×480 picture with a window scanned at 3 sizes in steps of 2 pixels has about 100,000 candidate
windows. Checking 6,000 features on each = 600 million checks per frame. Impossible in real time.

📄 **The cascade arithmetic**
```text
OpenCV's cascade: ~22 stages. Every stage is tuned so that:
    - 99.5% of real faces pass it
    - 50% of non-faces are rejected in it

overall face detection:     0.995^22 ≈ 0.90      (90% of faces survive the whole cascade)
overall false detection:    0.5^22   ≈ 2.4e-7    (out of 100,000 windows - about 0.02 false detections)

average features checked per window: most windows fail at stage 1-2 (2-10 features)
                                     -> in practice ~20-30 features per window instead of 6,000
```

This is the Viola–Jones idea: do not improve the accuracy of each check, but order the checks so
the heavy work is done only on the few that reach the end.

**AdaBoost** — how the features were chosen: start with all training pictures at equal weight.
Pick the single feature that best separates faces from non-faces. Increase the weight of the
pictures it got wrong, and pick the next feature — the one that fixes the previous one's mistakes.
Repeat. The final classifier is a weighted sum of "weak classifiers", each of which is almost
worthless alone. That is what is inside the XML.

## 7.4 `minNeighbors` — why one window is not enough

The detector returns "face" on every window that passed the cascade. A real face triggers **dozens**
of overlapping windows (shift by 2 pixels, slightly different size — still a face). A false detection
usually triggers one or two windows. `detectMultiScale` groups overlapping windows, and
`minNeighbors=5` says: a group with fewer than 5 windows — throw it away. This is a simple form of
**non-maximum suppression**, the same idea the DNN detector implements with confidence scores.

# Chapter 8 — Real time

## 8.1 The time budget

15 frames per second = 66 milliseconds per frame. Into that must fit: camera read, detection,
pre-processing, inference, drawing, display. Typical measurement on a laptop with a GPU:

| Step | Time |
|---|---|
| Haar detection | 8–20 ms |
| Pre-processing | < 1 ms |
| Inference on GPU | 2–4 ms |
| Drawing + conversion for display | 3–6 ms |

What is not in the table — and what kills the FPS — is **reading the camera** (`cap.read()`), which
blocks until the camera delivers a frame, 30–40 ms. That is why it runs in a separate thread.

## 8.2 The camera thread and "latest frame only"

A background thread reads from the camera in an endless loop and stores the latest frame in one
variable. The main loop (Tkinter) takes "whatever is there now" — it never waits for the camera,
and old frames never pile up in a queue. If the GUI is slow, we simply skip frames.

💡 Two threads touching the same variable = you need `threading.Lock`. Without the lock, the GUI
might read a frame while the thread is in the middle of writing it. And `read()` must return a
**copy** (`frame.copy()`), otherwise drawing on the frame corrupts the buffer.

## 8.3 Why not a `while True` loop in Tkinter

Tkinter is single-threaded: it draws, responds to clicks and runs your code **in the same** thread.
A loop of your own blocks it — the window "freezes". Instead we use `root.after(30, func)`: "run
`func` in 30 milliseconds". `func` processes one frame and asks for `after` again. So Tkinter stays
free between frames.

## 8.4 Temporal smoothing — why the label jumps

The model looks at every frame on its own. In a borderline expression — say 0.51 happy / 0.49
neutral — one pixel of noise flips the label. On screen it looks like flickering. The solution: a
moving average over the **probability vectors** of the last 5 frames, and only then `argmax`.

📄 **Why average the vectors and not "vote" on labels**
```text
3 frames:   [0.6 happy, 0.4 sad], [0.6 happy, 0.4 sad], [0.0 happy, 1.0 sad]
voting:     happy, happy, sad  -> happy (2 against 1)
average:    happy = 0.4,  sad = 0.6  -> sad

The third frame was very confident. The average respects confidence; voting ignores it.
```

This is what `tests/test_smoothing.py::test_probabilities_are_averaged_not_voted` checks.
The price: a delay of 2–3 frames (about 100 ms) before the label changes. Not noticeable.

## 8.5 The GIL, and why a thread helps anyway

In Python (CPython) there is the **GIL** — Global Interpreter Lock — which lets only one thread run
Python code at any moment. So how does the camera thread speed anything up?

Because `cap.read()` is OpenCV's C code, which releases the GIL while it waits for the hardware.
During that wait — 30 milliseconds — the GUI thread runs freely. Threads in Python are good for
I/O (camera, disk, network), not for computation. For parallel computation we use **processes** —
and that is exactly what `DataLoader(num_workers=4)` does.

📄 **Race condition — why you need a Lock**
```text
without a Lock, two threads on self._latest_frame:

time   camera thread                     GUI thread
t1     starts writing a new frame to the buffer
t2                                       reads the buffer  <- half old frame, half new
t3     finishes writing

with a Lock: the GUI waits until t3, or the camera waits until the GUI finished reading.
the wait - microseconds. the frame - always whole.
```

## 8.6 How much delay smoothing adds

A moving average over N frames = the label reflects the "center" of the window — about N/2 frames
back. With N=5 and 25 FPS: 2.5 frames = 100 milliseconds. Humans do not notice a delay below ~150 ms.
With N=15 it is already 300 ms and noticeable. That is why 5. If you measure "more than two label
changes per second" (the success metric) — raise to 7, not to 15.

## ✅ Check yourself — Chapters 7–8

1. Integral image: for the picture `[[2,1],[3,4]]` compute the integral table, then the sum of the
   whole picture using only the last cell.
2. A cascade of 10 stages, each passing 98% of faces and rejecting 60% of non-faces. What are the
   overall detection rate and false-detection rate? Is it better than 22 stages of 99.5%/50%?
3. You lowered `minNeighbors` to 1. What will you see on screen? You raised it to 15 — what will you see?
4. Detection 20 ms, inference 4 ms, drawing 5 ms, and `cap.read()` 35 ms. What is the maximum FPS if
   everything is in one thread? And if the camera is in a separate thread?
5. Why does `CameraService.read()` return a `copy()` and not the buffer itself, even with a Lock?
6. Smoothing works on 5 frames. The expression changes from neutral to happy at frame 100. At about
   which frame will the label switch if the model is 0.9 confident in every frame? Show the calculation for frames 101–103.

## 📚 Further reading — Chapters 7–8

- **OpenCV — Cascade Classifier tutorial**: https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html
- **Viola & Jones (2001), Rapid Object Detection** — sections 1–3 and figure 1:
  https://www.cs.cmu.edu/~efros/courses/LBMV07/Papers/viola-cvpr-01.pdf
- **OpenCV — DNN face detector sample** (the source of the DNN files): https://github.com/opencv/opencv/tree/4.x/samples/dnn/face_detector
- **Python — threading** (Lock, daemon): https://docs.python.org/3/library/threading.html
- **Real Python — What Is the Python GIL?**: https://realpython.com/python-gil/
- **TkDocs — The Event Loop** (why `after` and not `while`): https://tkdocs.com/tutorial/eventloop.html
- **OpenCV — Video capture**: https://docs.opencv.org/4.x/dd/d43/tutorial_py_video_display.html
