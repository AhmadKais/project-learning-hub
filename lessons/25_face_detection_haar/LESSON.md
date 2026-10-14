# Lesson 25 — Finding the face: Haar features, the integral image and the cascade

> **For:** Ryan (FaceEmotion stage 2) &nbsp;·&nbsp; **Time:** 45 min
> **Before:** Lesson 19 &nbsp;·&nbsp; **After this:** Lesson 26 (real time)

## 🎯 By the end, the student can

1. Explain a Haar feature (white sum − black sum) and point at two on a face.
2. Build an integral image by hand and get **any** rectangle's sum with 4 reads.
3. Explain the cascade with its arithmetic (0.995²² vs 0.5²²) and why it is fast.
4. Explain `scaleFactor`, `minNeighbors` and `minSize`.

---

## 1. Two networks, two jobs

The emotion network (Lessons 20–24) needs **a 48 × 48 face**. The camera gives a 640 × 480 room. Step one is to **find**
the face — with an algorithm from 2001 (Viola–Jones) that is still excellent for frontal faces, and runs in milliseconds.

## 2. Haar features

![Haar features](figs/haar_features.png)

A Haar feature = **sum of pixels in the white rectangle − sum in the black rectangle**. "The eye band is darker than the
cheeks" is a two-rectangle feature; "the bridge of the nose is brighter than the eyes" is a three-rectangle feature. One
feature alone is weak — but cheap, and thousands of them, chosen well, are strong.

## 3. The integral image — any rectangle in 4 reads

![integral image](figs/integral_image.gif)

Each cell of the integral image holds the sum of everything above and to the left of it. Then for any rectangle:

$$\text{sum}=I(D)-I(B)-I(C)+I(A)$$

The guide's example: picture `1 2 3 / 4 5 6 / 7 8 9` → integral `1 3 6 / 5 12 21 / 12 27 45`. Rectangle `[5 6; 8 9]`:
45 − 6 − 12 + 1 = **28** ✓ (5 + 6 + 8 + 9). Same cost for a 2 × 2 or a 200 × 200 rectangle — that is what makes the
detector fast.

## 4. Sliding windows and the cascade

![sliding window](figs/sliding_window.gif)

A window slides over the picture (and again at bigger sizes — `scaleFactor = 1.1` grows it 10 % per round). For each
window, the **cascade** asks a few cheap questions first; a window that fails is rejected immediately (red). Only the
survivors are asked more. In this toy run: 1,125 windows → 76 pass stage 1 → 15 reach the end, all on the face.

![cascade arithmetic and minNeighbors](figs/cascade_numbers.png)

```
OpenCV's cascade: ~22 stages, each tuned to keep 99.5 % of faces and drop 50 % of non-faces
    faces surviving all stages:     0.995^22 ≈ 0.90
    non-faces surviving:            0.5^22   ≈ 2.4e-7   →  of 100,000 windows ≈ 0.02 false hits
    work: most windows die in stage 1–2 → ~20–30 features per window instead of 6,000
```

**The idea:** don't make each check more accurate — order the checks so the expensive work only happens on the few that
reach the end. (Which features, in which order: chosen once by **AdaBoost** on thousands of pictures; you get the result as
an XML file.)

## 5. `minNeighbors` — one window is not enough

A real face fires **dozens** of overlapping windows (shift 2 pixels, slightly bigger — still a face). A false hit usually
fires one or two. `detectMultiScale` groups overlapping windows; `minNeighbors = 5` drops groups smaller than 5.

| parameter (config.py) | meaning | too low | too high |
|---|---|---|---|
| `scaleFactor = 1.1` | window grows 10 % per round | slow | misses sizes in between |
| `minNeighbors = 5` | how many windows must agree | false faces | missed faces |
| `minSize = (60, 60)` | ignore smaller faces | slow, far-away noise | misses people far from the camera |

## 6. Misconceptions

| Student says | Truth |
|---|---|
| "Haar is a neural network" | No — hand-designed rectangle features + AdaBoost + a cascade. No training in the project. |
| "It recognises who you are" | It only answers "is there a frontal face here?" |
| "Works for any head angle" | Frontal only — the XML was trained on frontal faces. That's why the DNN detector is the alternative in the book. |
| "Bigger minNeighbors is always safer" | It also drops real faces in bad light. |

## 7. Activities

1. **Integral image by hand (10 min).** 4 × 4 grid of small numbers; compute the integral; get 3 rectangle sums with 4
   reads each; check by adding directly.
2. **Be the cascade (10 min).** 30 photo cut-outs (faces and objects). Stage 1: "two dark spots side by side?" Stage 2:
   "a darker band under them?" Count how many cards each stage removes.
3. **Live:** in `04_detection_and_realtime.ipynb` change `minNeighbors` 1 → 10 on the same image.

## 8. Check yourself

<details><summary>1. With 30 stages of 99 % / 50 %, what share of faces survives?</summary>

0.99³⁰ ≈ **0.74** — a quarter of real faces lost. That's why each stage must keep ~99.5 % or more.
</details>

<details><summary>2. Integral `1 3 6 / 5 12 21 / 12 27 45`. Sum of the bottom row (7 8 9)?</summary>

I(bottom-right) − I(row above it, right) = 45 − 21 = **24** (two reads are enough when the rectangle touches the left edge).
</details>

<details><summary>3. A poster of a face on the wall is detected. Bug?</summary>

No — Haar sees a frontal face pattern; it can't know it's printed. Mention it as a limitation.
</details>

## 9. In your project

| Project | Where |
|---|---|
| FaceEmotion | `app/vision/haar_detector.py` → `HaarCascadeDetector.__init__/detect` (`detectMultiScale`) · `app/vision/face_detector.py` → `FaceDetector.detect_largest`, `create_detector` · `app/models/detection.py` → `FaceDetection.with_margin`, `crop` · `app/vision/dnn_detector.py` (the alternative) · theory `13_FaceEmotion/01_theory/07_detection_realtime.md` §7 · notebook `04_detection_and_realtime.ipynb` |

## 🎬 Watch & explore

* Computerphile — *Detecting Faces (Viola Jones Algorithm)* — [search on YouTube](https://www.youtube.com/results?search_query=Computerphile+Viola+Jones+face+detection)
* OpenCV docs — [Cascade Classifier tutorial](https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html)
* Viola & Jones (2001) — *Rapid Object Detection using a Boosted Cascade of Simple Features* — [search](https://www.google.com/search?q=Viola+Jones+2001+Rapid+Object+Detection+using+a+Boosted+Cascade+of+Simple+Features)
