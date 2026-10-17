# Lesson 23 — EmotionNet: residual blocks, BatchNorm, Dropout, and `train()` vs `eval()`

> **For:** Ryan (FaceEmotion stage 3 — `network.py`) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lessons 20–22 &nbsp;·&nbsp; **After this:** Lessons 24, 26

**In one sentence:** EmotionNet stacks residual blocks — layers that only learn a *correction* and pass their input
around them on a shortcut — plus BatchNorm (a z-score inside the network) and Dropout (random switch-offs), and the switch
`eval()` tells the last two to behave when the model is used.

## 🗺️ The map of this lesson

```mermaid
flowchart LR
    A["1 · The whole<br/>network & shapes"] --> B["2 · The problem:<br/>vanishing gradients"]
    B --> C["3 · The fix:<br/>out = F(x) + x"]
    C --> D["4 · BatchNorm"]
    D --> E["5 · Dropout"]
    E --> F["6 · train() vs eval()"]
```

## The story

> The class plays **"broken telephone"**: a sentence is whispered through 20 students. At the end it's nonsense. Now
> change the rule: every student also gets **a copy of the original note**, and only whispers what they want to *add or
> correct*. The message survives 20 people. Deep networks had exactly this problem until 2015 — the learning signal got
> lost on its way back through many layers — and the fix, **ResNet**, is exactly the "copy of the note": a shortcut around
> every block. This lesson builds Ryan's network, EmotionNet, piece by piece, and explains the two switches every student
> forgets: `train()` and `eval()`.

### 🌍 Real world

* **ResNet** (Microsoft Research, 2015) won the big ImageNet picture contest with a network of **152 layers** — before it,
  networks deeper than ~20 layers trained badly. Its paper became one of the most cited scientific papers of all time.
* The same **shortcut idea** (add the input back) is inside every modern network, including the Transformers behind
  ChatGPT and Claude.
* **Dropout** is like a sports team that trains with random players sitting out: everyone must learn to play every role, so
  the team doesn't collapse when one star is missing.

## Words you need

| word | meaning |
|---|---|
| **block** | a small group of layers used as one unit |
| **residual block** | a block whose output = (what the layers computed) + (the original input) |
| **shortcut / skip connection** | the path that carries the input around the layers |
| **vanishing gradient** | the learning signal (Lesson 21) shrinks layer by layer until the first layers learn nothing |
| **BatchNorm (BN)** | a z-score (Lesson 02) inside the network, for each channel, over the current batch |
| **Dropout** | in training, randomly switch off some neurons |
| **`model.train()` / `model.eval()`** | switches that tell BatchNorm and Dropout whether we are training or using the model |

---

## 1. The whole network

![architecture](figs/architecture.png)

```
input           1 × 48 × 48        (a grey face: 1 channel, 48 × 48)
stem            Conv3x3 → BN → ReLU         64 × 48 × 48
block1          Residual(64 → 64,  stride 1)   64 × 48 × 48
block2          Residual(64 → 128, stride 2)  128 × 24 × 24
block3          Residual(128 → 256, stride 2) 256 × 12 × 12
block4          Residual(256 → 512, stride 2) 512 ×  6 ×  6
GlobalAvgPool                                 512
Dropout(0.3) → Linear(512 → 7)                  7 logits (one per emotion)
```

Read the shapes as "**channels × height × width**". The picture gets **smaller** (48 → 6) and **deeper** (1 → 512): fewer
positions, many more kinds of features. Total ≈ **4.9 million** weights: small enough for 25 pictures per second, big enough
for 65 %+ accuracy.

### Counting one block (block 2) — be ready in the defence

```
conv 3×3, 64 → 128:        3 × 3 × 64 × 128  = 73,728    (each of 128 filters is 3 × 3 × 64)
BatchNorm(128):            2 × 128           =    256    (γ and β per channel, §4)
conv 3×3, 128 → 128:       3 × 3 × 128 × 128 = 147,456
BatchNorm(128):                                   256
shortcut 1×1, 64 → 128:    1 × 1 × 64 × 128  =  8,192
BatchNorm(128):                                   256
total                                           230,144
```

(The convolutions have `bias=False` because the BatchNorm right after them has its own shift β.)

## 2. The problem: vanishing gradients

![gradient flow](figs/gradient_flow.png)

Backpropagation (Lesson 21) multiplies one factor per layer on its way back. If many factors are below 1, the product
shrinks fast: 0.5 × 0.5 × … (40 times) ≈ 0.000000000001. The first layers get (almost) **no** signal and stop learning
(red line). Before 2015, a 56-layer network trained **worse** than a 20-layer one — even on its training data.

### Measured, not drawn

A 30-layer network (sigmoid neurons), the learning signal arriving at each layer after one backward pass, computed by
PyTorch:

![measured gradients](figs/measured_gradients.png)

Plain: from about 10² at the last layer down to about **10⁻¹⁶** at the first — a million billion times smaller. The first
layers effectively learn nothing. Residual: the signal stays the same size all the way back.

## 3. The residual block

![residual block](figs/residual_block.png)

$$\text{out} = \text{ReLU}\big(F(x) + x\big)$$

* **x** goes around the layers (the shortcut) and is **added** at the end.
* The layers only need to learn **F(x) — the correction** to x. If no correction is needed, F(x) = 0 and x passes through
  unchanged.
* On the way back, the gradient also flows through the "+ x" path untouched → the first layers keep getting a signal
  (green line).

When a block halves the picture (stride 2) or changes the number of channels (64 → 128), x has the wrong shape to be added.
Then the shortcut becomes a **1 × 1 convolution with stride 2 (+ BN)** that only reshapes it
(`test_residual_block_halves_with_stride_two`).

```python
identity = self.shortcut(x)            # nn.Identity() or a 1×1 conv + BN
out = F.relu(self.bn1(self.conv1(x)))
out = self.bn2(self.conv2(out))
out = F.relu(out + identity)           # the shortcut
```

## 4. BatchNorm — a z-score inside the network

![batchnorm](figs/batchnorm.png)

For each channel, over the 128 faces of the batch:

```
1. average of the channel over the batch:  μ      2. standard deviation: σ       (Lesson 00 §2–3)
3. x̂ = (x − μ) / σ                          → average 0, spread 1               (Lesson 02's z-score)
4. y = γ × x̂ + β                            → γ, β are LEARNED: the network can undo the normalisation if useful
```

Small example — one channel, a batch of 4 values 2, 4, 4, 6: μ = 4, σ = 1.41 → x̂ = −1.41, 0, 0, 1.41 → with γ = 1, β = 0.5:
−0.91, 0.5, 0.5, 1.91.

It keeps every layer's numbers in a healthy range → faster, more stable training. During training it also keeps **running
averages** of μ and σ for later.

## 5. Dropout

![dropout](figs/dropout.gif)

In training, every batch randomly switches off 30 % of the neurons before the last layer (the others are multiplied by
1 / 0.7 so the total stays the same). No neuron can rely on one particular partner → the network learns several ways to
recognise each emotion → less overfitting. **0 weights.**

## 6. `model.train()` vs `model.eval()` — the most-asked question

| | `train()` | `eval()` |
|---|---|---|
| Dropout | random 30 % off | everyone on |
| BatchNorm | normalises with **this batch's** μ, σ and updates the running averages | uses the **saved running** averages |

### On the project's real trained network

The small network trained in the FaceEmotion notebook (`_smallnet.pt`), shown the **same** drawn face five times in each
mode:

![train vs eval](figs/train_vs_eval.png)

* `train()`: the answer changes every time (Dropout is random, and BatchNorm normalises this one face by itself) — 4 times
  "disgust", once "angry".
* `eval()`: identical every time.

(And notice the answer: "neutral" for a drawn smile. The network learned from **photos**; a cartoon is outside what it has
seen — Lesson 19's lesson again: inputs must look like the training data.)

`eval()` doesn't evaluate anything — it's a switch. Forget it with the camera and: Dropout makes every frame random, and
BatchNorm normalises **one face by itself** (σ = 0) → nonsense. Always: `model.eval()` + `torch.no_grad()` before using the
model.

## 🧪 Worked example: a residual block in PyTorch, and the shapes

```python
import torch
from torch import nn
import torch.nn.functional as F

class ResidualBlock(nn.Module):
    def __init__(self, c_in, c_out, stride=1):
        super().__init__()
        self.conv1 = nn.Conv2d(c_in, c_out, 3, stride, 1, bias=False)
        self.bn1 = nn.BatchNorm2d(c_out)
        self.conv2 = nn.Conv2d(c_out, c_out, 3, 1, 1, bias=False)
        self.bn2 = nn.BatchNorm2d(c_out)
        self.shortcut = nn.Identity() if (stride == 1 and c_in == c_out) else nn.Sequential(
            nn.Conv2d(c_in, c_out, 1, stride, bias=False), nn.BatchNorm2d(c_out))

    def forward(self, x):
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.bn2(self.conv2(out))
        return F.relu(out + self.shortcut(x))           # F(x) + x

block2 = ResidualBlock(64, 128, stride=2)
x = torch.randn(8, 64, 48, 48)                          # a batch of 8 maps from block 1
print(block2(x).shape)                                  # torch.Size([8, 128, 24, 24])
print(sum(p.numel() for p in block2.parameters()))      # 230144 - the count of Part 1
```

## 7. Common mistakes

| student says | the truth |
|---|---|
| "Deeper is always better" | Not without shortcuts — the 2015 surprise. |
| "`eval()` turns off gradients" | That's `torch.no_grad()`. Use both. |
| "Why not download ResNet-50?" | Built for 224 × 224 colour photos; 25 M weights slow down real time; and the project requires understanding the architecture. |
| "The shortcut skips learning" | The layers still learn — only the *correction*; the shortcut keeps the signal alive. |

## 📝 Summary

> * EmotionNet: stem → 4 residual blocks (48 → 6 pixels, 1 → 512 channels) → global average pool → Dropout → 7 logits.
> * Deep plain networks suffer **vanishing gradients**: the signal shrinks layer by layer on its way back.
> * **Residual block**: out = ReLU(F(x) + x) — learn a correction, keep a shortcut. 1 × 1 conv when shapes change.
> * **BatchNorm**: z-score per channel over the batch, then γ, β (learned); keeps running averages for later.
> * **Dropout**: randomly switch off 30 % in training only.
> * **`eval()`**: Dropout off, BatchNorm uses the saved averages. With `torch.no_grad()`, always, before using the model.

## 8. Activities

1. **Broken telephone (10 min).** 10 students whisper a sentence; then again with the original note travelling along.
2. **Count (10 min).** Pairs compute block 3's weights with the formulas (answer: 919,040).
3. **Break it (10 min).** Predict the same face 5 times with `train()` and 5 times with `eval()`.

## 9. Do it yourself

<details><summary>1. Block 4 input 256 × 12 × 12, stride 2, 512 filters. Output shape?</summary>

512 × 6 × 6.
</details>

<details><summary>2. BatchNorm of the batch 1, 3, 5 (γ = 2, β = 0).</summary>

μ = 3 · σ = √((4 + 0 + 4)/3) = 1.63 · x̂ = −1.22, 0, 1.22 · y = **−2.45, 0, 2.45**.
</details>

<details><summary>3. The camera always says "neutral 31 %", whatever the face. Two likely causes?</summary>

`model.eval()` forgotten, or a preparation mismatch (Lesson 19). Also check that the weights file really loaded.
</details>

## 10. In your project

| Project | Where |
|---|---|
| FaceEmotion | `app/ml/network.py` → `ResidualBlock.__init__/forward`, `EmotionNet.__init__/forward` · `app/ml/predictor.py` → `load_model` (calls `eval()`) · theory `13_FaceEmotion/01_theory/05_cnn.md` §5.4–5.8, `03_images_nn.md` §4.6, 4.12 · notebook `02_neurons_to_resnet.ipynb` |

## 🎬 Watch & explore

| | |
|---|---|
| <a href="https://www.youtube.com/watch?v=o_3mboe1jYI"><img src="https://img.youtube.com/vi/o_3mboe1jYI/mqdefault.jpg" width="240" alt="video"></a> | **ResNet (actually) explained in under 10 minutes**. The 2015 paper, animated. |
| <a href="https://www.youtube.com/watch?v=Gey9CG6R6w8"><img src="https://img.youtube.com/vi/Gey9CG6R6w8/mqdefault.jpg" width="240" alt="video"></a> | **DataMListic — Why residual connections work**. The gradient view of Part 3. |
| <a href="https://www.youtube.com/watch?v=dXB-KQYkzNU"><img src="https://img.youtube.com/vi/dXB-KQYkzNU/mqdefault.jpg" width="240" alt="video"></a> | **deeplizard — Batch Normalization explained**. Part 4. |
| <a href="https://www.youtube.com/watch?v=CPOGlwvVv6o"><img src="https://img.youtube.com/vi/CPOGlwvVv6o/mqdefault.jpg" width="240" alt="video"></a> | **Dropout — theory + PyTorch code**. Part 5, with the train/eval difference in code. |

**Read more:**
* He et al. 2016 — [Deep Residual Learning (arXiv)](https://arxiv.org/abs/1512.03385)
