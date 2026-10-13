# How to use this guide

This guide was written for you, Ryan, with one assumption: **you have no background
in machine learning or deep learning.** Every idea is explained from zero, in simple
words, with a small number example you can check by hand.

The guide has three parts:

- **Part A — Understand the problem.** What the system does, what "learning" means for
  a computer, what a neural network is, how a computer "sees" a picture, and why you
  need a graphics card. Read this part **before** you write a single line of code.
  It takes one or two evenings.
- **Part B — Build the code.** Step by step, file by file: what to write, why, and how
  to know it works. This part goes together with `TASKS.md` in the code folder.
- **Part C — Pass the exam.** A bank of questions your supervisor or examiner may ask,
  with answers. After the code works, go over them until you can answer without looking.

Two rules for the whole way:

1. **Never copy code you do not understand.** In the defense you will be asked to explain
   every line. If you found a solution online or got it from an AI — read it, understand
   it, then write it again in your own words.
2. **Every number in the project book must come from a run on your own computer.** Not
   from this guide, not from a paper. Accuracy, FPS, training time — all from your machine.

Symbols used:

- ❓ **Possible supervisor question** — a question you will probably get, and the answer you should know.
- 💡 **Tip** — a common mistake or a shortcut.
- 📄 **Code** — a code example. Not always complete — sometimes just the idea.
- ✅ **Check yourself** — questions at the end of each chapter. Answers are in the appendix.

---

# Part A — Understand the problem

# Chapter 1 — What does the system do?

## 1.1 In one sentence

FaceEmotion looks through the webcam, finds your face, and says which emotion is on it —
happy, sad, angry, fear, surprise, disgust or neutral — 25 times every second.

## 1.2 The journey of one frame

Everything the system does happens again and again, for every frame (one single picture
from the video). This is the journey:

1. **The camera** gives a color picture, for example 640×480 pixels.
2. **The face detector** scans the picture and returns a rectangle: "there is a face at
   point (210, 140), width 180, height 180". If there is no face — it returns an empty list.
3. **Pre-processing** cuts out the rectangle, turns it to black-and-white, shrinks it to
   48×48 pixels, and normalizes the values. Now we have 2,304 numbers.
4. **The network** takes the 2,304 numbers and returns 7 numbers — a probability for each
   emotion. For example: happy 0.81, neutral 0.10, surprise 0.05, and the other four close to 0.
5. **Smoothing** averages the result with the 4 previous frames, so the label does not jump.
6. **Drawing** adds a colored box and the text "HAPPY 81%" to the picture.
7. **The screen** shows the picture; **the database** saves the result with the time;
   **the chart** adds one point.

Then everything starts again with the next frame. For the video to look smooth, the whole
journey must finish in less than 66 milliseconds (15 times per second).

## 1.3 Two different "brains"

Notice there are two completely different parts here that both do "seeing":

| Part | Question it answers | How it is built |
|---|---|---|
| Face detector (Haar) | **Where** is a face? | A ready algorithm from OpenCV, already trained. You only use it. |
| Emotion classifier (the network) | **What** expression is on the face? | **You** build it and train it on 28,709 pictures. |

Mixing these two up is the first mistake examiners catch. The detector knows nothing about
emotions. The network cannot find a face in a big picture. Each one does one job.

❓ **Possible supervisor question: why not give the network the whole camera picture and let
it find the face by itself?**
Because the network was trained only on pictures of faces, 48×48, centered. A full picture
of a room with a small person in the corner looks nothing like what it saw in training.
Splitting the jobs — first "where", then "what" — makes each job much easier, and lets you
change the detector without training again.

## 1.4 What you are really building

Three programs in one project:

- `train.py` — **trains** the network. Runs once (or a few times when you improve it), takes
  minutes on the graphics card, and creates the file `models/emotion_net_best.pt` — the trained "brain".
- `evaluate.py` — **tests** the brain on pictures it has never seen, and prints a score.
- `run.py` — **the application**. Loads the trained brain and uses it in real time.

This separation matters: the application never learns. It only uses what was learned.
