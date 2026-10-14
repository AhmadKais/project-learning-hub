# Lesson 21 — How a network learns: backpropagation, optimisers, the learning-rate schedule

> **For:** Ryan (FaceEmotion stage 4 — the training loop) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lessons 12 (gradient descent), 20 &nbsp;·&nbsp; **After this:** Lesson 24 (training in practice)

## 🎯 By the end, the student can

1. Do a full forward pass, backward pass (chain rule) and update **by hand** on the guide's tiny network.
2. Say what `loss.backward()`, `optimizer.step()` and `optimizer.zero_grad()` each do.
3. Explain the effect of the learning rate with the animation.
4. Explain momentum and Adam(W) in one sentence each, and the warm-up + cosine schedule.

---

## 1. Backpropagation with numbers

![backprop animation](figs/backprop.gif)

The guide's network: one input, one hidden ReLU neuron, one output, squared loss.

```
FORWARD     x = 2, w1 = 0.5, b1 = 0, w2 = −1, b2 = 1, target t = 1
            z1 = 0.5·2 + 0 = 1.0     h = ReLU(1.0) = 1.0     y = −1·1 + 1 = 0.0     L = (0 − 1)² = 1.0

BACKWARD    dL/dy  = 2(y − t)  = −2
            dL/dw2 = −2 · h    = −2         dL/db2 = −2
            dL/dh  = −2 · w2   =  2
            dL/dz1 = 2 · 1     =  2         (ReLU's slope is 1 because z1 > 0)
            dL/dw1 = 2 · x     =  4         dL/db1 = 2

UPDATE      lr = 0.1:  w1 = 0.1, b1 = −0.2, w2 = −0.8, b2 = 1.2
            new forward: y = 1.2, L = 0.04          ← from 1.0 to 0.04 in one step
```

**The chain rule in one sentence:** how much L changes when w1 moves = (how L changes with y) × (how y changes with h)
× (how h changes with z1) × (how z1 changes with w1). Backprop computes these products from the end to the start, reusing
each one — that's why it's fast even for 4.9 million weights.

**In PyTorch** — the three lines of every training step:

```python
optimizer.zero_grad()      # forget the previous batch's gradients (they ADD UP otherwise)
loss.backward()            # backprop: fill .grad of every weight
optimizer.step()           # update: w = w − lr · (something made from .grad)
```

⚠️ Notice h became exactly 0 after the update. If z1 goes negative, ReLU's slope is 0 and that neuron stops learning
("dead ReLU") — one reason for BatchNorm before ReLU and a gentle start (warm-up).

## 2. The learning rate

![learning rate](figs/learning_rate.gif)

Too small: crawls (wasted epochs). Good: walks into a valley and settles. Too big: jumps over valleys, the loss goes up
and down — or explodes to `nan`. Also note: gradient descent finds **a** valley, not necessarily the deepest one. In big
networks that turns out to matter much less than you'd fear.

## 3. Better than plain steps: momentum and Adam

![optimisers](figs/optimizers.gif)

A long narrow valley with noisy gradients (each mini-batch gives a slightly different gradient):

| optimiser | idea | in the animation |
|---|---|---|
| SGD | `w −= lr·g` | crawls along the valley floor |
| momentum | keep a running average of the gradients — a heavy ball keeps rolling | overshoots, then speeds along |
| **Adam** | momentum **and** divide each weight's step by its typical gradient size | heads for the minimum; every weight gets a sensible step |

AdamW (Ryan's optimiser) = Adam + **weight decay** applied directly (`w −= lr·λ·w`, λ = 1e-4): pulls every weight a little
toward 0 each step, against memorising.

## 4. The learning-rate schedule

![schedule](figs/schedule.png)

```
warm-up (epochs 1–3):    lr = lr_max · (0.1 + 0.9 · t/3)
cosine (epochs 4–50):    lr = 0.5 · lr_max · (1 + cos(π · t/47))
```

At the start the weights are random and the gradients wild — small steps avoid wrecking them (and dead ReLUs). In the
middle, big steps cover distance. At the end, tiny steps settle into the minimum instead of shaking around it. Cosine is
smooth: no "when to drop" hyper-parameter.

## 5. Mini-batches and epochs

| word | meaning (FaceEmotion) |
|---|---|
| batch | 128 faces; the gradient is the **average** over them |
| step | one `zero_grad → backward → step` |
| epoch | one pass over all 28,709 training faces ≈ 225 steps |

Why not the whole dataset per step? Too slow and too much memory. Why not one face? Too noisy. A batch is the compromise —
and its noise even helps escape bad valleys.

## 6. Misconceptions

| Student says | Truth |
|---|---|
| "`backward()` updates the weights" | It only computes gradients. `step()` updates. |
| "I can skip `zero_grad()`" | Gradients accumulate → each step uses the sum of all previous batches. |
| "Loss went to `nan`, the data is broken" | Usually the learning rate is too high (or a log of 0). Lower it first. |
| "Adam doesn't need a learning rate" | It does; it's just less sensitive to it. |

## 7. Activities

1. **The chain on paper (20 min).** Repeat the worked example with x = 1 (everything else the same). (z1 = 0.5, h = 0.5,
   y = 0.5, L = 0.25; dL/dy = −1, dL/dw2 = −0.5, dL/dw1 = 1·1·x = 1 …)
2. **Heavy ball (5 min).** Roll a marble and a ball bearing down a bent ruler — which one gets past a small bump? That's
   momentum.
3. **Break it (10 min).** In `13_FaceEmotion/02_examples/03_training_loop.ipynb`: set lr = 1.0, remove `zero_grad()`,
   forget `eval()` — observe each failure.

## 8. Check yourself

<details><summary>1. In the worked example, why is dL/dh = −2 · w2?</summary>

y = w2·h + b2, so dy/dh = w2. Chain rule: dL/dh = dL/dy · dy/dh = −2 · (−1) = 2.
</details>

<details><summary>2. The training loss goes down, the validation loss goes up. Is the optimiser broken?</summary>

No — that's overfitting (Lessons 01, 24). The optimiser is doing its job on the training data too well.
</details>

<details><summary>3. Why does Adam divide by sqrt(v)?</summary>

v tracks each weight's typical squared gradient. Dividing normalises the step: weights with huge gradients get relatively
small steps and vice versa — so one global lr works for all 4.9 M weights.
</details>

## 9. In your project

| Project | Where |
|---|---|
| FaceEmotion | `app/ml/trainer.py` → `ModelTrainer.__init__` (AdamW, scheduler), `train_one_epoch` (the 3 lines), `validate`, `fit`, `plot_history` · theory `13_FaceEmotion/01_theory/03_images_nn.md` §4.5, 4.7–4.11 · notebook `03_training_loop.ipynb` |
| PhishGuard | the same gradient step, by hand: exercise `ex07_gradient`, `ex08_fit_logistic` (Lesson 12) |

## 🎬 Watch & explore

* 3Blue1Brown — *Gradient descent, how neural networks learn* and *Backpropagation calculus* — [search on YouTube](https://www.youtube.com/results?search_query=3Blue1Brown+backpropagation+calculus)
* Distill — [Why Momentum Really Works](https://distill.pub/2017/momentum/) (interactive)
* Andrej Karpathy — *The spelled-out intro to neural networks and backpropagation: building micrograd* — [search on YouTube](https://www.youtube.com/results?search_query=Karpathy+micrograd+spelled-out+intro)
