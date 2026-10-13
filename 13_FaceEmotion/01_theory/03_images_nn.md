# Chapter 3 — How a computer sees a picture

## 3.1 A picture is a table of numbers

A black-and-white picture is a matrix: in every cell a number from 0 (black) to 255 (white).
A 48×48 picture is 2,304 numbers. A color picture is three such matrices — red, green, blue
(in OpenCV the order is reversed: **BGR**. Common mistake: if colors look strange in the window,
you forgot to convert BGR→RGB before showing it).

📄 **A 4×4 picture as a matrix**
```text
  0   0  255 255
  0  30  200 255
 80 120  120  80
255 255    0   0
```

## 3.2 Normalization — why divide by 255 and subtract the mean

Neural networks learn much better when the input is small numbers around zero, not 0–255.
So before the picture enters the network:

📄 **Normalization**
```text
pixel / 255.0                     -> range 0..1
(x - 0.5013) / 0.2916             -> mean ~0, standard deviation ~1
```

0.5013 and 0.2916 are the mean and standard deviation of all FER-2013 training pixels **after
histogram equalization** (section 3.3 — the network only ever sees equalized faces). They are in
`config.py`. **The same two numbers must be used in training and in real time** — if you
normalize one way in training and another way with the camera, the network gets numbers in a
range it never saw, and accuracy collapses with no error message. This is called
**train/serve skew** and it is the most frustrating bug in the project.

## 3.3 Histogram equalization — why it helps in bad light

`cv2.equalizeHist` stretches the brightness range: if all pixels of a dark face are between 20
and 90, after equalization they spread over 0–255. The face "looks" to the network more like a
well-lit face. One line of code that raises real-time accuracy by a few percent.

⚠️ It is part of the pre-processing, so the train/serve rule of section 3.2 applies to it too: if the
camera path equalizes, the **training** path must equalize as well. That is why `dataset.py` has an
`EqualizeHist` transform used by both `build_train_transform` and `build_eval_transform`, and why
`test_eval_transform_matches_realtime_preprocessing` checks that a face becomes the same numbers on both
paths. Equalize only in real time and the network sees high-contrast faces it was never trained on.

# Chapter 4 — A neural network from zero

## 4.1 The single neuron

A neuron is a small function: it takes a few numbers, multiplies each by a weight, adds them
up, adds a bias, and passes the result through an "activation function".

📄 **A neuron with 3 inputs**
```text
inputs:   x = [0.5, -1.0, 2.0]
weights:  w = [0.8,  0.3, -0.4]
bias:     b = 0.1

sum:   0.5*0.8 + (-1.0)*0.3 + 2.0*(-0.4) + 0.1 = 0.4 - 0.3 - 0.8 + 0.1 = -0.6
ReLU:  max(0, -0.6) = 0        <- the output
```

**ReLU** (Rectified Linear Unit) is the activation function we use: negative becomes 0, positive
stays. Without an activation function, a stack of layers is just one big linear operation — and
it cannot learn things like "a smile". ReLU adds the "non-linearity" that lets the network learn
complex shapes.

## 4.2 Layers

A layer = many neurons that get the same input. A network = layers one after another: the output
of one layer is the input of the next. The first layers learn simple things (lines, edges), the
middle ones combine them into shapes (an eye, a mouth), and the last ones combine shapes into
concepts (a smile). Nobody programs this — it is what comes out of training.

## 4.3 The output layer and Softmax

Our last layer outputs 7 numbers, one per emotion. They are called **logits** and can be any
number. **Softmax** turns them into probabilities: all positive, adding up to 1.

📄 **Softmax**
```text
logits = [2.0, 0.5, -1.0]
e^2.0 = 7.39,  e^0.5 = 1.65,  e^-1.0 = 0.37      sum = 9.41
softmax = [7.39/9.41, 1.65/9.41, 0.37/9.41] = [0.785, 0.175, 0.039]
```

The chosen emotion is the one with the highest probability (`argmax`), and its probability is the
"confidence" shown on screen.

💡 `EmotionNet.forward()` returns logits, **not** probabilities. Reason: PyTorch's loss function
`CrossEntropyLoss` applies Softmax by itself. If you apply Softmax twice, training silently fails.
The test `test_network_returns_logits_not_probabilities` catches this.

## 4.4 The loss function — how wrong were we

To learn, the network needs one number that says "how far is your answer from the right one".
That is the **loss function**. For classification we use **cross-entropy**:

📄 **Cross-entropy**
```text
true label: happy (index 3)
network said:  P(happy) = 0.80   ->  loss = -ln(0.80) = 0.22   (good)
network said:  P(happy) = 0.10   ->  loss = -ln(0.10) = 2.30   (bad)
network said:  P(happy) = 0.99   ->  loss = -ln(0.99) = 0.01   (excellent)
```

The lower the probability it gave to the right answer — the bigger the loss. The goal of training:
make the average loss over all training examples as small as possible.

## 4.5 How the network learns — gradient descent

We have ~4.9 million weights and one number (the loss) we want to make small. The idea:

1. Push a batch of 128 pictures through the network, compute the loss.
2. For every weight compute: "if I increase you a little, does the loss go up or down, and by how
   much?" — that is the **gradient**. PyTorch computes it automatically (`loss.backward()`) with
   an algorithm called **backpropagation**.
3. Move every weight a little in the direction that lowers the loss: `w = w - lr * gradient`.
4. Repeat with the next batch.

📄 **One step of gradient descent**
```text
current weight:      w = 0.80
gradient:            dL/dw = +2.5      (increasing w increases the loss)
learning rate (lr):  0.01
new weight:          w = 0.80 - 0.01 * 2.5 = 0.775
```

- **Learning rate** — the size of the step. Too big: the network "jumps" past the minimum and never
  settles. Too small: very slow. We use 0.001, with a scheduler that lowers it gradually (cosine
  annealing) — big steps at the start, tiny steps at the end.
- **Epoch** — one pass over the **whole** training set. 50 epochs = the network saw every picture
  50 times (each time with different augmentation, see chapter 6).
- **Batch** — how many pictures go through the network together before one weight update. 128 for us.
  A GPU likes big batches (it computes them in parallel).
- **Optimizer** — the algorithm that does step 3. The basic one is called SGD; we use **AdamW**,
  which adapts the step size for each weight separately and converges faster.

❓ **Possible supervisor question: what is the difference between epoch, batch and iteration?**
Iteration = one weight update, on one batch. Epoch = one pass over all training data. With 25,800
pictures and a batch of 128, there are about 202 iterations in one epoch, and 50 epochs = ~10,100 updates.

## 4.6 Dropout and Batch Normalization

Two "helper" layers that appear in our network:

- **Dropout(0.3)** — during training only, randomly switches off 30% of the neurons in each pass.
  The network cannot rely on a single neuron and is forced to learn a more robust representation.
  Reduces overfitting. During inference (`model.eval()`) it is off — **so you must call `eval()`
  before inference.**
- **BatchNorm** — normalizes the output of every layer (mean 0, std 1) over the batch. Stabilizes
  training and allows a higher learning rate. It also behaves differently in `train()` and `eval()`.

💡 `model.train()` / `model.eval()` does not "train" and does not "evaluate" — it is only a switch
that tells Dropout and BatchNorm which mode to use. Forgetting `eval()` before inference = random
results in real time. You will surely be asked about this.

## 4.7 A full forward pass in a tiny network — with numbers

A network with one input, one hidden neuron and one output. Small enough to compute everything by
hand, and it contains **all** the mechanics of the big network.

📄 **The network and the forward pass**
```text
input x = 2,  target t = 1
hidden layer:  z1 = w1*x + b1 ,  h = ReLU(z1)         w1 = 0.5,  b1 = 0
output layer:  y  = w2*h + b2                          w2 = -1.0, b2 = 1
loss:          L  = (y - t)^2

z1 = 0.5*2 + 0 = 1.0
h  = ReLU(1.0) = 1.0
y  = -1.0*1.0 + 1 = 0.0
L  = (0.0 - 1)^2 = 1.0
```

## 4.8 The backward pass (backpropagation) — the chain rule with numbers

The question for every weight: "if I move you a tiny bit, how much does L change?" — that is a
derivative. When the weight affects L through several steps, we multiply the derivatives along the
chain (**the chain rule**). We go from the end to the start, hence "backward":

📄 **Computing the gradients**
```text
dL/dy  = 2*(y - t)        = 2*(0 - 1)     = -2

dL/dw2 = dL/dy * dy/dw2   = -2 * h        = -2 * 1.0 = -2
dL/db2 = dL/dy * dy/db2   = -2 * 1        = -2

dL/dh  = dL/dy * dy/dh    = -2 * w2       = -2 * (-1) = 2
dh/dz1 = 1  (z1 = 1.0 > 0; the derivative of ReLU is 1 for positive, 0 for negative)
dL/dz1 = dL/dh * dh/dz1   = 2 * 1         = 2

dL/dw1 = dL/dz1 * dz1/dw1 = 2 * x         = 2 * 2 = 4
dL/db1 = dL/dz1 * dz1/db1 = 2 * 1         = 2
```

**Update** with learning rate 0.1 (`w = w - lr * grad`):

📄 **One gradient step and its result**
```text
w1 = 0.5  - 0.1*4    = 0.1
b1 = 0    - 0.1*2    = -0.2
w2 = -1.0 - 0.1*(-2) = -0.8
b2 = 1    - 0.1*(-2) = 1.2

new forward pass:
z1 = 0.1*2 - 0.2 = 0.0 ,  h = ReLU(0) = 0 ,  y = -0.8*0 + 1.2 = 1.2
L  = (1.2 - 1)^2 = 0.04        <- from 1.0 to 0.04 in one step
```

This is all that `loss.backward()` and `optimizer.step()` do — on 4.9 million weights instead
of 4, and on a batch of 128 instead of one example (the gradient is the average over the batch).

💡 Look at what happened to h: it became exactly 0. If z1 went below zero, the ReLU derivative
would be 0 and the neuron would stop learning forever ("dead ReLU"). This is one reason for
BatchNorm before ReLU and for a careful learning rate at the start (warm-up).

## 4.9 The gradient of Softmax + Cross-Entropy — the elegant result

It looks complicated: Softmax, then a logarithm, then a derivative. But the result is amazingly
simple, and examiners who know it love to ask:

📄 **dL/dz = p − y**
```text
logits z = [2.0, 0.5, -1.0]        softmax p = [0.785, 0.175, 0.039]
true label: class 1  ->  y = [0, 1, 0]   (one-hot)

L = -ln(p_1) = -ln(0.175) = 1.743

dL/dz = p - y = [0.785 - 0, 0.175 - 1, 0.039 - 0] = [0.785, -0.825, 0.039]
```

Meaning: the gradient **lowers** the logit of the correct class by "how much it is missing to
reach 1", and **raises** the others by the probability they got. The more confident the model is
in a mistake — the bigger the step. This is why the two are joined into one layer
(`CrossEntropyLoss`), and why `forward` returns logits and not probabilities.

## 4.10 AdamW — what exactly happens in `optimizer.step()`

Plain SGD: `w = w - lr * g`. The problem: the same step for every weight, and a noisy gradient.
Adam keeps two moving averages for every weight:

📄 **AdamW — the update formulas**
```text
g   = the current gradient of the weight
m   = β1*m + (1-β1)*g          moving average of the gradient        (β1 = 0.9)   "momentum" - direction
v   = β2*v + (1-β2)*g^2        moving average of the squared gradient (β2 = 0.999) - typical size
m^  = m / (1 - β1^t)           bias correction in the first steps (t = step number)
v^  = v / (1 - β2^t)

w   = w - lr * m^ / (sqrt(v^) + ε)  -  lr * λ * w
           ^^^^^^^^^^^^^^^^^^^^^^^     ^^^^^^^^^^
           normalized step per weight   weight decay (λ = 1e-4)
```

- Dividing by `sqrt(v)` normalizes: a weight with big gradients gets a relatively small step, and
  the other way around. So Adam is "insensitive" to scale and converges fast without fine tuning.
- **Weight decay** pulls every weight a little toward 0 in every step — prevents huge weights that
  memorize. The W in AdamW = "decoupled": the penalty is applied directly and not through the
  gradient. In plain Adam the penalty is swallowed by the normalization and does not work properly
  (Loshchilov & Hutter, 2019).

## 4.11 The learning-rate scheduler — warm-up then cosine

📄 **The formulas**
```text
Warm-up (first 3 epochs):   lr_t = lr_max * (0.1 + 0.9 * t / 3)         rises 0.1→1.0 of lr_max
Cosine  (remaining 47):     lr_t = 0.5 * lr_max * (1 + cos(π * t / 47))  falls smoothly from lr_max to 0

example with lr_max = 1e-3:
Epoch  1:  ~4e-4      Epoch 3: 1e-3     Epoch 15: ~8.4e-4
Epoch 27: ~5e-4       Epoch 40: ~1.5e-4  Epoch 50: ~0
```

Why not constant: at the start, big steps cross the distance quickly; at the end, tiny steps
"settle" inside the minimum instead of shaking around it. Why cosine and not steps: a continuous
decrease, without a hyper-parameter for "when to drop".

## 4.12 BatchNorm and Dropout — the formulas and what changes in `eval()`

📄 **BatchNorm**
```text
training (on a batch of 128):
    μ_B = mean of the channel over the batch,   σ²_B = variance of the channel over the batch
    x^  = (x - μ_B) / sqrt(σ²_B + ε)         ε = 1e-5 prevents division by zero
    y   = γ * x^ + β                          γ, β are learned - the network can "undo" the normalization if needed
    also: running_mean = 0.9*running_mean + 0.1*μ_B   (same for the variance)

inference (eval):
    y = γ * (x - running_mean) / sqrt(running_var + ε) + β
```

Why the difference: in real time **one** picture passes — there is no "batch" to average over.
We use the averages collected during training. If you forget `eval()`, BatchNorm normalizes
by one picture — zero variance — and the output is meaningless.

📄 **Dropout (inverted)**
```text
training:   for each neuron, with probability p=0.3 -> 0 ; otherwise -> x / (1-p) = x / 0.7
inference:  x  (unchanged)
```

Dividing by 0.7 in training keeps the same average output, so at inference nothing needs to change.
Number of parameters of Dropout: 0. It is only a random mask.

## ✅ Check yourself — Chapters 3–4

1. A 48×48 picture where every pixel is 128. After `/255` and after `(x-0.5013)/0.2916` — what is the value of every pixel?
2. In the tiny network of section 4.7, change the input to x = −1 (everything else the same). Compute z1, h, y, L,
   and dL/dw1. What is special about the result and why?
3. logits = [0, 0, 0, 0, 0, 0, 0]. What is the Softmax? What is the cross-entropy for any label? What does this say about a network before training?
4. logits = [3, 1, 0], truth = class 0. Compute p, L, and dL/dz. Which logit goes down and which goes up in the next step?
5. Why must `optimizer.zero_grad()` come **before** `backward()` and not after `step()`?
   (Hint: what happens between two iterations?)
6. In AdamW, two weights: one has gradients of size ~10 all the time, the other ~0.01.
   Which one moves more in each step? Why is this different from SGD?
7. Explain in one sentence each: what `model.eval()` changes in BatchNorm, and what in Dropout.

## 📚 Further reading — Chapters 3–4

- **3Blue1Brown — Neural Networks** (4 videos, ~1 hour): https://www.3blue1brown.com/topics/neural-networks
  The best visual explanation of a neuron, the gradient and backpropagation. Must watch.
- **Andrej Karpathy — "The spelled-out intro to neural networks and backpropagation"** (2.5 hours):
  https://www.youtube.com/watch?v=VMj-3S1tku0 — builds backprop from zero in Python. After it, section 4.8 is trivial.
- **Michael Nielsen — Neural Networks and Deep Learning**, chapters 1–3 (free):
  http://neuralnetworksanddeeplearning.com/ — the classic text; chapter 2 = backprop, chapter 3 = cross-entropy.
- **CS231n notes — Optimization** (SGD, momentum, Adam): https://cs231n.github.io/neural-networks-3/
- **PyTorch — Deep Learning in 60 Minutes**: https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html
  Tensors, autograd, first network. Do it before stage 3.
- Papers (for the bibliography, read abstract + figures): **BatchNorm** https://arxiv.org/abs/1502.03167 ·
  **Dropout** https://jmlr.org/papers/v15/srivastava14a.html · **AdamW** https://arxiv.org/abs/1711.05101
