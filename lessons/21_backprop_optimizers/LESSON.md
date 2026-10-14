# Lesson 21 — How a network learns: backpropagation, optimisers and the learning-rate schedule

> **For:** Ryan (FaceEmotion stage 4 — the training loop) &nbsp;·&nbsp; **Time:** 3 × 45 min
> **Before:** Lesson 00 §9 (slope); Lessons 12 (gradient descent), 20 &nbsp;·&nbsp; **After this:** Lesson 24

## The story

> Back in Ryan's factory (Lesson 20): a smiling face came in, and the last room shouted "sad". Wrong. Someone has to tell
> **each worker** how to change their habits — but which workers caused the mistake, and by how much? The boss starts at
> the end: *"Sad-shouter, you were too loud. Who gave you your notes? You, and you — your notes pushed toward sad, so
> change them a bit."* Each worker passes the blame **backwards** to whoever fed them, in proportion to how much they
> mattered. That is **backpropagation**. Then every worker adjusts a little — that's one **step** of training. Repeat a
> million times.

## 🎯 By the end, the student can

1. Do a full forward pass, backward pass and update **by hand** on the guide's tiny network.
2. Explain the chain rule with the "gear" analogy.
3. Say what `zero_grad()`, `backward()` and `step()` each do.
4. Explain the learning rate, momentum, Adam, and the warm-up + cosine schedule.

## Words you need

| word | meaning |
|---|---|
| **forward pass** | computing the output from the input, left to right (Lesson 20) |
| **loss** | how wrong the output is (Lessons 12, 20) |
| **gradient / slope / derivative** | for one weight: "if I increase this weight a tiny bit, how much does the loss change?" (Lesson 00 §9) |
| **chain rule** | when A affects B and B affects C: (effect of A on C) = (effect of A on B) × (effect of B on C) |
| **backward pass / backpropagation** | computing every weight's gradient, from the loss back to the input |
| **learning rate (lr)** | how big a step each weight takes |
| **batch, step, epoch** | a group of examples · one update · one pass over all training examples |
| **optimiser** | the rule that turns gradients into weight changes (SGD, momentum, Adam) |

---

## 1. The chain rule — gears

Three gears in a row. Turn gear A once → gear B turns 2 times. Gear B once → gear C turns 3 times. How many times does C
turn when A turns once? **2 × 3 = 6**. Effects along a chain **multiply**. That's the chain rule — the only maths behind
backpropagation.

## 2. Backpropagation with numbers

![backprop animation](figs/backprop.gif)

The guide's network: one input, one hidden ReLU neuron, one output, squared loss L = (y − t)².

### Forward (left to right)

```
x = 2,   w1 = 0.5, b1 = 0,   w2 = −1.0, b2 = 1,   target t = 1
z1 = w1 × x + b1 = 0.5 × 2 + 0 = 1.0
h  = ReLU(z1)    = 1.0
y  = w2 × h + b2 = −1 × 1 + 1  = 0.0
L  = (y − t)²    = (0 − 1)²    = 1.0
```

### Backward (right to left) — "how does L change if I nudge each thing?"

```
dL/dy  = 2 × (y − t) = 2 × (0 − 1) = −2          (from L = (y − t)²: the slope of a square is 2 × the inside)
   → y is too small; raising y would lower the loss

dL/dw2 = dL/dy × h   = −2 × 1.0 = −2              (y = w2·h + b2: nudging w2 changes y by h)
dL/db2 = dL/dy × 1   = −2
dL/dh  = dL/dy × w2  = −2 × (−1) = +2             (nudging h changes y by w2)
dL/dz1 = dL/dh × 1   = +2                         (ReLU's slope is 1 when z1 > 0, else 0)
dL/dw1 = dL/dz1 × x  = 2 × 2 = 4                  (z1 = w1·x + b1: nudging w1 changes z1 by x)
dL/db1 = dL/dz1 × 1  = 2
```

Each line is one gear: "how much the next thing changes" × "how much the loss cares about the next thing".

### Update: step downhill (lr = 0.1)

```
w1 = 0.5 − 0.1 × 4    = 0.1          b1 = 0 − 0.1 × 2     = −0.2
w2 = −1 − 0.1 × (−2)  = −0.8         b2 = 1 − 0.1 × (−2)  = 1.2
```

### Check: forward again

```
z1 = 0.1 × 2 − 0.2 = 0.0     h = 0     y = −0.8 × 0 + 1.2 = 1.2     L = (1.2 − 1)² = 0.04
```

The loss fell from **1.0 to 0.04** in one step. EmotionNet does exactly this — for 4.9 million weights at once, averaged
over 128 faces.

⚠️ Notice h became exactly 0. If z1 goes negative, ReLU's slope is 0 and that neuron stops learning ("dead ReLU") — one
reason for BatchNorm (Lesson 23) and a gentle start (warm-up, §5).

**In PyTorch** — the three lines of every training step:

```python
optimizer.zero_grad()      # erase last step's gradients (otherwise they ADD UP)
loss.backward()            # backpropagation: fill in every weight's gradient
optimizer.step()           # move every weight a little downhill
```

## 3. The learning rate

![learning rate](figs/learning_rate.gif)

Too small: crawls. Good: walks into a valley and settles. Too big: jumps over valleys, the loss goes up and down — or
becomes `nan`. Also: gradient descent finds **a** valley, not necessarily the deepest one.

## 4. Better steps: momentum and Adam

![optimisers](figs/optimizers.gif)

A long narrow valley, with noisy gradients (each batch gives a slightly different slope):

| optimiser | idea | analogy |
|---|---|---|
| **SGD** | w = w − lr × gradient | a careful walker: crawls along the valley floor |
| **momentum** | keep a running average of the gradients | a heavy ball: keeps rolling, smooths the noise |
| **Adam** | momentum **and** each weight gets its own step size | a ball that also adjusts its speed per direction |

**AdamW** (Ryan's optimiser) = Adam + **weight decay**: every step, pull each weight a tiny bit toward 0 (w = w − lr × λ ×
w, λ = 0.0001) — a brake against memorising, like C in Lesson 12.

## 5. The learning-rate schedule — warm-up, then cosine

![schedule](figs/schedule.png)

```
epochs 1–3 (warm-up):     lr = lr_max × (0.1 + 0.9 × t / 3)          rises from 10 % to 100 % of 0.001
epochs 4–50 (cosine):     lr = 0.5 × lr_max × (1 + cos(π × t / 47))  falls smoothly to 0
```

Start gently (random weights → wild gradients); big steps in the middle to travel; tiny steps at the end to settle into
the bottom instead of shaking around it.

## 6. Batches, steps, epochs

| word | FaceEmotion |
|---|---|
| batch | 128 faces; the gradient is the **average** over them |
| step | one `zero_grad → backward → step` |
| epoch | one pass over all 28,709 training faces ≈ 225 steps |

## 7. Common mistakes

| student says | the truth |
|---|---|
| "`backward()` updates the weights" | It only computes gradients. `step()` updates. |
| "I can skip `zero_grad()`" | Gradients pile up — each step uses the sum of all previous batches. |
| "Loss became `nan`, the data is broken" | Usually the learning rate is too high. Lower it first. |

## 8. Activities

1. **Gears (5 min).** Real gears or drawn ones: count turns; multiply ratios.
2. **The chain on paper (20 min).** Repeat §2 with x = 1 (everything else the same).
3. **Heavy ball (5 min).** A marble and a heavier ball down a bent ruler with a small bump: which one gets past? (momentum)
4. **Break it (10 min).** In `03_training_loop.ipynb`: lr = 1.0; remove `zero_grad()`; forget `eval()`.

## 9. Do it yourself

<details><summary>1. §2 with x = 1: forward pass and the gradient of w1.</summary>

z1 = 0.5 · h = 0.5 · y = −0.5 + 1 = 0.5 · L = 0.25 · dL/dy = 2(0.5 − 1) = −1 · dL/dh = −1 × (−1) = 1 · dL/dz1 = 1 ·
dL/dw1 = 1 × x = **1**.
</details>

<details><summary>2. Training loss goes down, validation loss goes up. Is the optimiser broken?</summary>

No — overfitting (Lessons 01, 24). It's doing its job on the training data too well.
</details>

<details><summary>3. Warm-up at epoch 2 with lr_max = 0.001?</summary>

0.001 × (0.1 + 0.9 × 2/3) = 0.001 × 0.7 = **0.0007**.
</details>

## 10. In your project

| Project | Where |
|---|---|
| FaceEmotion | `app/ml/trainer.py` → `ModelTrainer.__init__` (AdamW, scheduler), `train_one_epoch` (the 3 lines), `validate`, `fit`, `plot_history` · theory `13_FaceEmotion/01_theory/03_images_nn.md` §4.5, 4.7–4.11 · notebook `03_training_loop.ipynb` |
| PhishGuard | the same step by hand: exercises `ex07_gradient`, `ex08_fit_logistic` (Lesson 12) |

## 🎬 Watch & explore

* 3Blue1Brown — *Gradient descent* and *Backpropagation calculus* — [search on YouTube](https://www.youtube.com/results?search_query=3Blue1Brown+backpropagation+calculus)
* Distill — [Why Momentum Really Works](https://distill.pub/2017/momentum/)
* Andrej Karpathy — *building micrograd* — [search on YouTube](https://www.youtube.com/results?search_query=Karpathy+micrograd+spelled-out+intro)
