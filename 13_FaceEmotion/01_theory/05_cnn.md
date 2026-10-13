# Chapter 5 — Convolutional networks (CNN) and ResNet

## 5.1 Why not a "normal" network for pictures

In a normal (fully connected) network, every neuron of the first layer is connected to all 2,304
pixels. With 512 neurons that is 1.2 million weights **in the first layer alone**, and with no
idea that pixel (10,10) is next to pixel (10,11). The network would have to learn "an eye"
separately for every position in the picture.

## 5.2 Convolution — a small filter that slides over the picture

Instead, we take a small **kernel** — say 3×3 = 9 weights — and slide it over the whole picture.
At every position we multiply element by element and add up. The result is a new picture called a
**feature map**: it "lights up" where the kernel's pattern appears.

📄 **3×3 convolution — one cell by hand**
```text
window from the picture:    kernel (detects a vertical line):
  10  10  200                 -1   0   1
  10  10  200                 -1   0   1
  10  10  200                 -1   0   1

result = 10*(-1) + 10*0 + 200*1
       + 10*(-1) + 10*0 + 200*1
       + 10*(-1) + 10*0 + 200*1  = -30 + 600 = 570   -> a strong vertical edge here
```

On a flat area (all values 10) the result is 0 — no edge. This kernel is a "vertical line
detector". In the network, **the network learns the 9 numbers of the kernel by itself**. A layer
with 64 kernels learns 64 different detectors: lines, corners, dots, brightness changes.

Two huge advantages:

- **Weight sharing** — the same 9 numbers are used everywhere in the picture. "An eye" is learned
  once and recognized at every position. Far fewer weights.
- **Locality** — every output depends only on its small neighborhood, like real vision.

## 5.3 Reducing resolution — stride and pooling

After a few layers we want to "step back": let the network look at bigger areas. We do this with
**stride=2** (the kernel jumps two pixels each step, the output is 2× smaller in each axis) or with
**pooling** (take the max/average of every 2×2 square).

This is exactly what happens in our network: 48×48 → 24×24 → 12×12 → 6×6, while the number of
feature maps **grows**: 64 → 128 → 256 → 512. Less "where", more "what".

At the end, **global average pooling** averages every 6×6 map into one number — 512 numbers remain,
and they go into the output layer Linear(512 → 7).

## 5.4 ResNet — the jump that made deep networks possible

Until 2015 people found something strange: a network with 56 layers was **worse** than one with
20 layers, even on the training data. Not overfitting — simply hard to train. The reason: the
**vanishing gradient** — the gradient computed at the end of the network gets weaker at every
layer it passes backward, and almost zero reaches the first layers. They do not learn.

The solution by He and others (2016), the **residual block**: add a "shortcut" (skip connection)
that connects the input of the block directly to its output:

📄 **Residual block**
```text
normal:    out = F(x)             the block must learn the whole function
residual:  out = F(x) + x         the block learns only the "correction" (the residual) on x

implementation:
    identity = x
    out = relu(bn1(conv1(x)))
    out = bn2(conv2(out))
    out = out + identity        <- the jump
    out = relu(out)
```

Why it helps: if the layer does not need to change anything, the easiest thing for it is to learn
F(x)=0 — then out=x exactly. And the gradient flows backward through the shortcut without
weakening. With this trick people trained networks of 152 layers.

💡 When the block reduces resolution (stride=2) or changes the number of channels (64→128), you
cannot add `x` to `F(x)` — the shapes differ. So the shortcut becomes a 1×1 convolution with the
same stride, which only "matches the shape". That is the `shortcut` in `ResidualBlock.__init__`.
The test `test_residual_block_halves_with_stride_two` checks exactly this.

## 5.5 Our network — Mini-ResNet

📄 **EmotionNet — the flow**
```text
input           1 x 48 x 48        (one picture, one channel)
stem   Conv3x3 -> BN -> ReLU        64 x 48 x 48
block1 Residual(64 -> 64,  s=1)     64 x 48 x 48
block2 Residual(64 -> 128, s=2)    128 x 24 x 24
block3 Residual(128 -> 256, s=2)   256 x 12 x 12
block4 Residual(256 -> 512, s=2)   512 x  6 x  6
GlobalAvgPool                      512
Dropout(0.3)                       512
Linear(512 -> 7)                     7   (logits)
```

About 4.9 million weights (exact calculation in section 5.6). Small enough to run 25 times per
second, big enough for 65%+.

❓ **Possible supervisor question: why not take a ready ResNet-50 from the internet?**
You could, and it is a legitimate alternative for the "alternatives" chapter. But: (1) ResNet-50 is
built for 224×224 color pictures — on 48×48 black-and-white most of its depth is wasted;
(2) 25 million weights slow down real time; (3) the project requires you to **understand** the
architecture, and a residual block you wrote yourself in 20 lines proves it better than one import line.

## 5.6 Counting parameters — layer by layer

An examiner who asks "how many parameters" and hears "4.9 million" will immediately ask "how did
you compute it?". The formulas:

📄 **Formulas**
```text
Conv2d(in, out, k×k, bias=False):   parameters = k * k * in * out
BatchNorm2d(c):                     parameters = 2 * c          (γ and β per channel)
Linear(in, out):                    parameters = in * out + out (weights + bias)
ReLU, pooling, dropout:             0
```

📄 **EmotionNet — the full calculation**
```text
stem    Conv 3x3, 1→64        9*1*64            =       576
        BN(64)                                   =       128
block1  Conv 3x3, 64→64       9*64*64           =    36,864
        BN(64)                                   =       128
        Conv 3x3, 64→64                          =    36,864
        BN(64)                                   =       128
        shortcut: identity                       =         0        block total:    73,984
block2  Conv 3x3, 64→128      9*64*128          =    73,728
        BN(128)                                  =       256
        Conv 3x3, 128→128     9*128*128         =   147,456
        BN(128)                                  =       256
        shortcut Conv 1x1, 64→128  1*1*64*128   =     8,192
        BN(128)                                  =       256        block total:   230,144
block3  Conv 128→256          9*128*256         =   294,912
        BN(256)                                  =       512
        Conv 256→256          9*256*256         =   589,824
        BN(256)                                  =       512
        shortcut 1x1, 128→256                    =    32,768
        BN(256)                                  =       512        block total:   919,040
block4  Conv 256→512          9*256*512         = 1,179,648
        BN(512)                                  =     1,024
        Conv 512→512          9*512*512         = 2,359,296
        BN(512)                                  =     1,024
        shortcut 1x1, 256→512                    =   131,072
        BN(512)                                  =     1,024        block total: 3,673,088
head    Linear(512→7)         512*7 + 7         =     3,591
--------------------------------------------------------------------------
total                                            = 4,900,551
```

Two things to notice: (1) 75% of the parameters are in the last block — the deeper you go, the
more channels, and convolutions get "expensive"; (2) the output layer is amazingly cheap thanks to
global average pooling — with Flatten we would get Linear(512*6*6=18,432 → 7) = 129,031.
Your `count_parameters()` must print exactly 4,900,551; if not — something in the architecture is different.

## 5.7 Receptive field and padding

**Receptive field** = how many pixels of the original picture a neuron in some layer "sees".
First 3×3 convolution: 3×3. A second one on top: 5×5. Every extra 3×3 adds 2, and stride 2
doubles the rate. After stem + block1 (five 3×3 convolutions): 11×11 pixels — still "an eye".
After block4: the field is bigger than 48 — every neuron sees the **whole** face. This is why the
deep layers can recognize "smile + narrowed eyes = happy" and not just lines.

**Padding=1** (a frame of zeros, width 1) keeps 48×48 after a 3×3 convolution. Without padding
the picture shrinks by 2 in every layer, and the border pixels are seen fewer times than the
center ones. With stride=2 and padding=1: `out = floor((48 + 2*1 - 3)/2) + 1 = 24`. Check it
yourself for 24→12 and 12→6.

## 5.8 Why `bias=False` in the convolutions

BatchNorm after the convolution subtracts the mean. Any bias the convolution would add — is erased
by that subtraction, and its role is taken by the β of the BatchNorm. The bias is useless, so we
turn it off. Fewer parameters, and zero difference in expressiveness.

## ✅ Check yourself — Chapter 5

1. The kernel `[[0,-1,0],[-1,4,-1],[0,-1,0]]` on the window `[[10,10,10],[10,50,10],[10,10,10]]`.
   What is the result? And on a window that is all 10? What does this kernel detect?
2. A layer Conv2d(32→64, 3×3, bias=True). How many parameters? And with bias=False?
3. Input 12×12, 3×3 convolution with stride=2 and padding=1. What is the output size? And with padding=0?
4. Why is there no 1×1 convolution in the shortcut of block1, but there is one in block2? What happens in the code if you leave it out in block2?
5. Explain in your own words why `out = F(x) + x` is easier to learn than `out = F(x)` when the layer "does not need to do anything".
6. Suggest one change to the network that would cut the parameter count roughly in half, and explain what could get worse.

## 📚 Further reading — Chapter 5

- **CNN Explainer** (interactive — drag a kernel over a picture and see the feature map): https://poloclub.github.io/cnn-explainer/
- **CS231n notes — Convolutional Networks**: https://cs231n.github.io/convolutional-networks/
  The chapter that explains output size, padding, stride, parameters — with the same formulas as section 5.6.
- **3Blue1Brown — But what is a convolution?**: https://www.youtube.com/watch?v=KuXjwB4LzSA
- **The ResNet paper** (He et al., 2016): https://arxiv.org/abs/1512.03385 — pages 1–4 and figure 2. The source of section 5.4.
- **CS231n lectures** (Stanford, YouTube): https://www.youtube.com/playlist?list=PLC1qU-LWwrF64f4QKQT-Vg5Wr4qEE1Zxk — lectures 5 and 9 (CNN, architectures).
