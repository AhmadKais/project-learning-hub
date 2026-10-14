# Lesson 22 — Convolution: a small filter that slides over the picture

> **For:** Ryan (FaceEmotion — EmotionNet) &nbsp;·&nbsp; **Time:** 45 – 60 min
> **Before:** Lessons 19, 20 &nbsp;·&nbsp; **After this:** Lesson 23 (ResNet)

## 🎯 By the end, the student can

1. Compute a convolution by hand (one output number = 9 products added up).
2. Say what a feature map is, and what output size a 3 × 3 filter gives (with and without padding, with stride 2).
3. Explain max-pooling, and why CNNs use far fewer weights than a dense layer.
4. Explain the receptive field and why deep layers "see" whole expressions.

---

## 1. Why not a normal (dense) layer?

![dense vs conv](figs/why_conv.png)

A dense layer from 2,304 pixels to 512 neurons has **1.2 million** weights and must learn "an eye" separately for every
position. A convolution filter is **shared** over the whole picture: one 3 × 3 eye-corner detector (9 weights) works
everywhere.

## 2. Watch a filter slide

![convolution](figs/conv_slide.gif)

At each position: multiply the 9 pixels under the filter by the 9 weights, add them up, write **one** number. The filter
(−1 0 +1 in each row) answers "is it brighter on the right than on the left?" → big numbers exactly along the vertical
edge, 0 on flat areas.

By hand, top-left of the edge: pixels `0 0 9 / 0 0 9 / 0 0 9`, filter `−1 0 1` ×3 →
(0·−1 + 0·0 + 9·1) × 3 rows = **27**.

| sizes | 48 × 48 input, 3 × 3 filter |
|---|---|
| no padding | 46 × 46 (we lose a border) |
| `padding=1` (EmotionNet) | 48 × 48 — same size |
| `stride=2` | 24 × 24 — the filter jumps 2 pixels; halves the size |

## 3. What filters find

![filters](figs/filters.png)

Edge filters light up outlines (eyes, mouth, face contour); blur averages; sharpen exaggerates differences. In a CNN
nobody writes these by hand — the first layer of EmotionNet has **64 filters learned by gradient descent**, and they turn out
to look much like edge and blob detectors.

With several input channels (e.g. 64 feature maps in), each filter is 3 × 3 × 64 and sums over all of them.

## 4. Pooling and stride — making the picture smaller

![max pooling](figs/pooling.png)

Max-pool keeps the strongest response in each 2 × 2 block: 4× fewer numbers, and a feature that moves by one pixel gives
the same answer. EmotionNet shrinks with **stride-2 convolutions** instead (48 → 24 → 12 → 6), then **global average
pooling** at the end (each of 512 maps → one number).

## 5. The receptive field

![receptive field](figs/receptive_field.png)

One unit in a deep layer depends on a growing window of the input: 3, 5, 7 … pixels with plain 3 × 3 layers, much faster
with stride 2. Early layers see edges; middle layers see eyes, mouth corners; the last layers see the **whole face** — an
expression.

## 6. Misconceptions

| Student says | Truth |
|---|---|
| "Each position has its own filter" | One filter, shared everywhere — that's the point. |
| "The CNN looks for faces I programmed" | It learns its filters from data. |
| "Pooling loses information, so it's bad" | It deliberately throws away exact positions to gain tolerance and speed. |
| "A 3 × 3 filter only sees 3 × 3" | In layer 1. Stacked layers see more (receptive field). |

## 7. Activities

1. **Paper convolution (15 min).** Print a 6 × 6 grid of numbers and a 3 × 3 card with a hole pattern (the filter). Slide
   it, compute the 4 × 4 output. Swap filter: horizontal edges.
2. **Setosa (10 min).** [Image Kernels](https://setosa.io/ev/image-kernels/): try *outline*, *sharpen*, *custom*.
3. **CNN Explainer (15 min).** [poloclub.github.io/cnn-explainer](https://poloclub.github.io/cnn-explainer/): click a
   neuron to see the convolution happen on a real network.

## 8. Check yourself

<details><summary>1. A 12 × 12 map, a 3 × 3 filter, padding 1, stride 2. Output size?</summary>

(12 + 2·1 − 3) / 2 + 1 = 5.5 → **6 × 6** (PyTorch rounds down: ⌊11/2⌋ + 1 = 6).
</details>

<details><summary>2. How many weights in one conv layer: 64 maps in, 128 filters out, 3 × 3, no bias?</summary>

3 · 3 · 64 · 128 = **73,728**.
</details>

<details><summary>3. Why does EmotionNet end with global average pooling instead of flattening 512 × 6 × 6?</summary>

512·6·6 = 18,432 inputs to the last layer would need many more weights and overfit; averaging each map to one number
(512) is cheap and keeps "is this feature present somewhere", which is what an expression needs.
</details>

## 9. In your project

| Project | Where |
|---|---|
| FaceEmotion | `app/ml/network.py` → the stem `Conv3x3 → BN → ReLU`, `ResidualBlock` (stride 2 to downsample), `GlobalAvgPool` · theory `13_FaceEmotion/01_theory/05_cnn.md` §5.1–5.3, 5.7 · notebook `02_neurons_to_resnet.ipynb` |

## 🎬 Watch & explore

* CNN Explainer — [interactive visualisation of a CNN](https://poloclub.github.io/cnn-explainer/)
* 3Blue1Brown — *But what is a convolution?* — [search on YouTube](https://www.youtube.com/results?search_query=3Blue1Brown+but+what+is+a+convolution)
* Setosa — [Image Kernels explained visually](https://setosa.io/ev/image-kernels/)
