# Lesson 20 — A neural network from zero: neurons, layers, softmax, cross-entropy

> **For:** Ryan (FaceEmotion stage 3) &nbsp;·&nbsp; useful background for everyone &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lessons 12 (sigmoid, log-loss), 19 &nbsp;·&nbsp; **After this:** Lesson 21 (how it learns), 22 (convolution)

## 🎯 By the end, the student can

1. Compute one neuron's output by hand (weights, bias, ReLU).
2. Explain why a network needs **layers** and a **non-linear** activation between them.
3. Compute softmax and the cross-entropy loss for 3 classes by hand.
4. Explain why `forward()` returns **logits** and not probabilities.

---

## 1. One neuron

![a neuron](figs/neuron.png)

Ryan's guide, by hand: inputs (0.5, −1.0, 2.0), weights (0.8, 0.3, −0.4), bias 0.1 →
z = 0.4 − 0.3 − 0.8 + 0.1 = **−0.6** → ReLU(−0.6) = **0**. It is logistic regression (Lesson 12) with a different
squash at the end.

## 2. Activation functions

![activations](figs/activations.png)

A layer is "weights × inputs + bias". Two layers in a row without anything between them = one bigger linear function — no
gain. A **non-linear** activation between layers is what lets the network bend its decisions. EmotionNet uses **ReLU**:
cheap, and its slope is just 1 (positive) or 0 (negative).

## 3. Why layers?

![one neuron vs layers](figs/why_layers.png)

One neuron can only draw a straight line. A hidden layer of 4 ReLU neurons can draw a few straight pieces; two layers
of 32 can follow a curve. **Each layer builds new features from the previous layer's features** — in a face network:
edges → eyes and mouth corners → whole expressions (Lesson 22).

## 4. Watch a forward pass

![forward pass](figs/forward_pass.gif)

Numbers flow left to right. Each circle = weighted sum of the previous layer + bias, then ReLU (many become exactly 0).
The last layer gives one number per class; softmax turns them into probabilities that add up to 1.

## 5. Softmax — from scores to probabilities

$$p_i=\frac{e^{z_i}}{\sum_j e^{z_j}}$$

![softmax example](figs/softmax_example.png)

The guide's example: z = (2.0, 0.5, −1.0) → e^z = (7.39, 1.65, 0.37), sum 9.41 → **p = (0.785, 0.175, 0.039)**.

* exponentiate → everything positive, bigger scores grow much faster;
* divide by the sum → the numbers add up to 1.

## 6. Cross-entropy — how wrong were we?

$$L=-\ln p_{\text{true class}}$$

Truth = class 1 → L = −ln 0.175 = **1.743**. If the network had said 0.9 → L = 0.105. It is the multi-class version of
Dani's log-loss (Lesson 12).

![softmax and loss during training](figs/softmax.gif)

During training the "happy" logit is pushed up, its probability rises, the loss falls toward 0.

**The elegant result (for the defence):** for softmax + cross-entropy, the gradient with respect to the logits is simply

$$\frac{\partial L}{\partial z}=p-y\qquad\text{e.g. }(0.785,\,0.175-1,\,0.039)=(0.785,\,-0.825,\,0.039)$$

That is why PyTorch joins them in one layer (`nn.CrossEntropyLoss` takes **logits**) and why Ryan's `forward()` returns
logits; the predictor applies softmax only for display.

## 7. Misconceptions

| Student says | Truth |
|---|---|
| "Softmax in `forward()` and `CrossEntropyLoss` — double safe" | Double softmax: wrong loss, slow learning. `CrossEntropyLoss` applies it itself. |
| "A probability of 0.9 means the model is right 90 % of the time" | Only if it is calibrated (Lessons 14, 24). |
| "More neurons = always better" | More capacity = more overfitting risk and slower real time (EmotionNet: 4.9 M weights, chosen for 25 fps). |
| "ReLU(−0.6) is −0.6" | 0. Negative in → 0 out. |

## 8. Activities

1. **Human neurons (15 min).** 3 "input" students hold numbers; 2 "hidden" students each have weight cards, compute the
   sum, apply ReLU and pass it on; 1 "output" student adds up. Change one weight — what changes downstream?
2. **Softmax by hand (10 min).** z = (1, 0, −1) → e^z = (2.72, 1, 0.37), sum 4.09, p = (0.665, 0.245, 0.090).
3. **TensorFlow Playground (10 min).** Spiral dataset: 0 hidden layers vs 2 hidden layers of 8 neurons; ReLU vs linear.

## 9. Check yourself

<details><summary>1. Inputs (1, 2), weights (0.5, −1), bias 0.5. Output after ReLU?</summary>

0.5 − 2 + 0.5 = −1 → ReLU = **0**.
</details>

<details><summary>2. Logits (3, 3, 3). Softmax? Loss if the truth is class 0?</summary>

(⅓, ⅓, ⅓); loss = −ln ⅓ = **1.099** — the loss of pure guessing among 3 classes. For 7 emotions: ln 7 = 1.946 (a useful
number to recognise at the start of training).
</details>

<details><summary>3. Why can't we stack linear layers without an activation?</summary>

W₂(W₁x + b₁) + b₂ = (W₂W₁)x + (W₂b₁ + b₂) — one linear layer again.
</details>

## 10. In your project

| Project | Where |
|---|---|
| FaceEmotion | `app/ml/network.py` → `EmotionNet.forward` (returns logits) · `app/ml/predictor.py` → `EmotionPredictor.predict` (softmax for display) · `trainer.py` → `nn.CrossEntropyLoss` · theory `13_FaceEmotion/01_theory/03_images_nn.md` §4.1–4.4, 4.9 · notebook `02_neurons_to_resnet.ipynb` |

## 🎬 Watch & explore

* 3Blue1Brown — *But what is a neural network?* (Deep learning, chapter 1) — [search on YouTube](https://www.youtube.com/results?search_query=3Blue1Brown+but+what+is+a+neural+network)
* TensorFlow Playground — [playground.tensorflow.org](https://playground.tensorflow.org/) (interactive)
* 3Blue1Brown — [Neural networks lessons page](https://www.3blue1brown.com/topics/neural-networks)
