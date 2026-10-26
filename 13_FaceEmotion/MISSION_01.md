# Mission 1 - How a network sees a face

**Student:** Ryan Raed  ·  **Time:** two weeks  ·  **Ends with:** your paper task solved at the board

The heart of your project, studied properly: read and run, write the exercises, solve a real example by
hand, and show it at the board.

## Part 1 - Study (first week)

In this order. Keep a notebook: every new word and every formula goes in it.

1. Lesson: [images as numbers](../lessons/19_images_as_numbers/LESSON.md)
2. Lesson: [neurons and softmax](../lessons/20_neurons_softmax/LESSON.md)
3. Lesson: [convolution and pooling](../lessons/22_convolution_pooling/LESSON.md)
4. Theory: [`03_images_nn.md`](01_theory/03_images_nn.md), [`05_cnn.md`](01_theory/05_cnn.md)
5. Notebook [`01_images_and_data.ipynb`](02_examples/01_images_and_data.ipynb): run every cell, then print the 48x48 numbers of one face and count the images of each emotion.
6. Notebook [`02_neurons_to_resnet.ipynb`](02_examples/02_neurons_to_resnet.ipynb): run every cell, then run an edge filter over a face and show the result.

## Part 2 - Homework (hand in at the end of the two weeks)

**A. Exercises.** In `03_exercises/exercises.py` write `ex01`, `ex04`, `ex05`, `ex06`. Check them:

```bash
cd 13_FaceEmotion/03_exercises
pytest test_exercises.py -k "ex01 or ex04 or ex05 or ex06" -v
```

Open `solutions.py` only after your tests pass. In class you will explain one of them line by line.

**B. On paper.** Show every step - a final number alone gets no points. Bring the paper or a photo of it.

**1. Convolution by hand.** Stride 1, no padding.

```text
image                kernel
1  2  0  1           1  0  -1
0  1  3  1           1  0  -1
2  1  0  0           1  0  -1
1  0  1  2
```

Compute the output (what size is it?), then apply ReLU, then a 2x2 max pool. What kind of pattern does this
kernel react to?

**2. Sizes.** A face is 48x48. A convolution with a 3x3 kernel, padding 1, stride 1 - what size comes out?
Then a 2x2 max pool with stride 2? Repeat conv + pool three times starting from 48x48: what is the final size?
Write the formula you used.

**3. Softmax.** The network outputs the logits `[2.0, 1.0, 0.1]` for (happy, sad, neutral). Compute the three
probabilities. Compute the cross-entropy loss if the true emotion is happy, and if it is neutral. Which loss is
bigger, and why does that make sense?

**C. In your own words.** 3-5 sentences each.

1. Why use convolution instead of connecting every one of the 2304 pixels to every neuron?
2. Why do we subtract the largest logit before computing softmax? Give logits where it matters.

## Part 3 - At the board (5 minutes)

In class you solve your paper task (part B) on the board, in front of everyone, explaining each step.
Then I ask one question from [`17_exam.md`](05_defence/17_exam.md) and the class may ask one.

## How it is graded

| Part | Points |
|---|---|
| A. exercises pass and you can explain them | 30 |
| B. paper task correct, every step shown | 30 |
| C. answers in your own words | 15 |
| At the board: the paper task explained clearly | 15 |
| Answer to the question | 10 |
