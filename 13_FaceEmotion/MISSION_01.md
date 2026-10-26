# Mission 1 - How a network sees a face

**Student:** Ryan Raed  ·  **Time:** two weeks  ·  **Ends with:** a 10-minute talk in class

You will explain the heart of your project to the class. To explain it you have to understand it, so the
mission has three parts: study, homework, talk.

## Part 1 - Study (first week)

In this order. Keep a notebook: every new word and every formula goes in it.

1. Lesson: [images as numbers](../lessons/19_images_as_numbers/LESSON.md)
2. Lesson: [neurons and softmax](../lessons/20_neurons_softmax/LESSON.md)
3. Lesson: [convolution and pooling](../lessons/22_convolution_pooling/LESSON.md)
4. Theory: [`03_images_nn.md`](01_theory/03_images_nn.md), [`05_cnn.md`](01_theory/05_cnn.md)
5. Notebook [`01_images_and_data.ipynb`](02_examples/01_images_and_data.ipynb): run every cell, then print the 48x48 numbers of one face and count the images of each emotion.
6. Notebook [`02_neurons_to_resnet.ipynb`](02_examples/02_neurons_to_resnet.ipynb): run every cell, then run an edge filter over a face and show the result.

## Part 2 - Homework (hand in before your talk)

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

## Part 3 - The talk (10 minutes + 5 minutes of questions)

Title: **How a network sees a face**. Six slides at most, one idea each:

1. An image is a grid of numbers: one real 48x48 face
2. What a filter does: your paper convolution on the board
3. ReLU and pooling - what they keep and what they throw away
4. From the last layer to probabilities: softmax with your numbers
5. The loss: why the wrong guess costs more
6. Live demo: notebook 02, a filter over a face

Rules: no slide full of text, no code copied from the solution. Draw on the board where you can.
After the talk I ask one question from [`17_exam.md`](05_defence/17_exam.md) and one about
your paper task.

## How it is graded

| Part | Points |
|---|---|
| A. exercises pass and you can explain them | 25 |
| B. paper task correct, every step shown | 25 |
| C. answers in your own words | 10 |
| The talk: correct, clear, on time | 25 |
| Answers to the questions | 15 |
