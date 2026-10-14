# Lesson 19 — How a computer sees a picture: pixels, normalisation, equalisation

> **For:** Ryan (FaceEmotion stages 2–3) &nbsp;·&nbsp; **Time:** 45 – 60 min
> **Before:** Lesson 00 §1–3; Lesson 02 &nbsp;·&nbsp; **After this:** Lessons 20–22

## The story

> Ryan's app watches a face through the laptop camera and says "happy", "sad", "surprised"… In his bright bedroom it
> works well. In the classroom — dim light, a window behind the student — it says "neutral" to everything. Nothing
> crashed. The problem is in **how the computer sees** the picture: for the computer, a picture is just a table of
> numbers, and a dark picture is a table of **small** numbers it was never trained on. This lesson is about that table,
> and the two tricks that make dark and bright faces look alike to the network.

## 🎯 By the end, the student can

1. Explain that a grey picture is a table of numbers 0–255, and a colour picture is three tables.
2. Explain the BGR trap in OpenCV.
3. Normalise a pixel by hand with the project's numbers, and explain why the **same** numbers must be used in training and
   with the camera.
4. Do histogram equalisation by hand on a tiny picture and explain what it does.

## Words you need

| word | meaning |
|---|---|
| **pixel** | one dot of the picture; in grey: a number from 0 (black) to 255 (white) |
| **resolution** | how many pixels: 48 × 48 = 2,304 numbers |
| **channel** | one table of numbers; colour pictures have 3 (red, green, blue) |
| **histogram** | a chart of how many pixels have each brightness |
| **normalisation** | rescaling the numbers so they are small and around 0 (Lesson 02's z-score) |
| **histogram equalisation** | spreading the brightness so a dark picture uses the whole range 0–255 |
| **train/serve skew** | the camera path prepares the picture differently from training → silent wrong answers |

---

## 1. Zoom in until you see numbers

![zooming into a face](figs/zoom.gif)

*(The lessons draw their own faces — FER-2013 pictures may not be shared.)* A 48 × 48 grey face is **2,304 numbers**. The
dark pupil of the eye is a cluster of small numbers (6, 7, 11, 20); the white around it is near 200. The network never
"sees a face" — it sees this table.

## 2. Colour = three tables — and the BGR trap

![RGB channels](figs/channels.png)

A colour picture has three tables: how much **R**ed, **G**reen and **B**lue in each pixel. OpenCV (the camera library)
stores them in the order **B, G, R**. Show a camera frame in a window without `cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)` and
faces turn blue. FaceEmotion turns every face into **one grey table** anyway (`COLOR_BGR2GRAY`): colour doesn't tell the
emotion, and one table is 3× less work.

## 3. Normalisation — small numbers around 0

Networks learn much better with small numbers around 0 than with 0 … 255 (the same reason as Lesson 02 §4). Two steps:

```
step 1:  pixel / 255                      → between 0 and 1
step 2:  (x − 0.5013) / 0.2916            → a z-score: mean ≈ 0, spread ≈ 1
```

**By hand, pixel 200:**

```
200 / 255 = 0.784
(0.784 − 0.5013) / 0.2916 = 0.283 / 0.2916 = 0.97      → "about one step brighter than an average pixel"
```

**Pixel 30:** 30 / 255 = 0.118 → (0.118 − 0.5013) / 0.2916 = −0.383 / 0.2916 = **−1.31** ("1.3 steps darker").

![normalisation](figs/normalise.png)

**Where do 0.5013 and 0.2916 come from?** They are the average and the standard deviation (Lesson 00 §2–3) of **all
pixels of all training faces** (after equalisation, §4). They live in `config.py` and must be used **everywhere** — with
other numbers the camera faces become numbers the network never saw, and accuracy collapses with no error message (the same
bug as Lesson 18 §5).

## 4. Histogram equalisation — make a dark face look normal

A face in dim light has all its pixels squeezed into a narrow, dark range (here 20 … 81). Equalisation **stretches** the
brightness so the picture uses the whole range 0 … 255.

![equalisation](figs/equalize.png)

### By hand on a tiny "picture" of 10 pixels

```
pixels: 20 20 20 20 30 30 30 40 40 50          (all dark)

1. count each grey level:            20: 4     30: 3     40: 2     50: 1
2. running total (cumulative):       20: 4     30: 7     40: 9     50: 10
3. as a share of all 10 pixels:      0.4       0.7       0.9       1.0
4. new grey = round((cdf − cdf_min) / (N − cdf_min) × 255),  cdf_min = 4, N = 10:
      20 → (4 − 4)/6 × 255  =   0
      30 → (7 − 4)/6 × 255  = 127.5 → 128
      40 → (9 − 4)/6 × 255  = 212.5 → 212
      50 → (10 − 4)/6 × 255 = 255
new pixels: 0 0 0 0 128 128 128 212 212 255     (the same picture, but using the whole range)
```

In words: each grey level moves to "the share of pixels darker than or equal to it". Crowded ranges get stretched apart;
empty ranges are skipped. The middle chart in the picture shows this mapping.

⚠️ Equalisation is part of the preparation, so it must happen in **training and with the camera**. That's why Ryan's
`dataset.py` has an `EqualizeHist` step in **both** `build_train_transform` and `build_eval_transform`, and
`test_eval_transform_matches_realtime_preprocessing` checks a face becomes the same numbers on both paths. (This was a real
bug fixed in the project.)

## 5. Common mistakes

| student says | the truth |
|---|---|
| "The network sees the face like we do" | It sees 2,304 numbers. Change the light and every number changes. |
| "Normalise the camera with its own average" | That's skew. Use the saved training numbers. |
| "Equalisation is just to make pictures prettier" | It is part of the input preparation — the model's contract. |

## 6. Activities

1. **Pixel art (10 min).** 8 × 8 squared paper: students write numbers 0–255 to draw a smiley; a neighbour shades it.
2. **By hand (5 min).** Normalise pixels 0, 128, 255 with the project's numbers.
3. **Live:** in `13_FaceEmotion/02_examples/01_images_and_data.ipynb`, darken a face and run `cv2.equalizeHist`.

## 7. Do it yourself

<details><summary>1. Normalise pixels 0, 128 and 255.</summary>

0 → (0 − 0.5013)/0.2916 = **−1.72** · 128 → 0.502 → **0.00** · 255 → 1.0 → (1 − 0.5013)/0.2916 = **1.71**.
</details>

<details><summary>2. Equalise: 10, 10, 60, 60, 60, 60 (6 pixels).</summary>

counts 10: 2, 60: 4 · cumulative 2, 6 · cdf_min 2, N 6 · 10 → 0 · 60 → (6 − 2)/4 × 255 = **255**. A dark/darker picture
becomes black/white.
</details>

<details><summary>3. How many numbers in one 640 × 480 colour camera frame?</summary>

640 × 480 × 3 = **921,600**.
</details>

## 8. In your project

| Project | Where |
|---|---|
| FaceEmotion | `app/vision/preprocessor.py` → `FacePreprocessor.crop_face`, `to_model_input`, `process` · `app/ml/dataset.py` → `EqualizeHist`, `build_train_transform`, `build_eval_transform` · `config.py` → `NORMALIZE_MEAN/STD` · theory `13_FaceEmotion/01_theory/03_images_nn.md` §3 · notebook `01_images_and_data.ipynb` |

## 🎬 Watch & explore

* Computerphile — *Digital images / pixels* — [search on YouTube](https://www.youtube.com/results?search_query=Computerphile+digital+images+pixels)
* Setosa — [Image Kernels explained visually](https://setosa.io/ev/image-kernels/) (also for Lesson 22)
* OpenCV docs — [Histogram equalization](https://docs.opencv.org/4.x/d5/daf/tutorial_py_histogram_equalization.html)
