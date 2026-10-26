# 13 · FaceEmotion — start here

**Student:** Ryan Raed  ·  **Field:** deep learning and computer vision  ·  **Core algorithms:** a convolutional network with residual blocks (EmotionNet), its training loop, Haar-cascade face detection, temporal smoothing

> **Next week:** a talk in class - [Can a computer read emotions from a face?](PRESENTATION_01.md).
>
> **Your current mission:** [Mission 1](MISSION_01.md) - study, homework and a 10-minute talk in class (two weeks).

## The problem in one paragraph

The camera sees a face; your program says which of 7 emotions it shows — **live, at 15–25 frames per second**.
Three parts: **find the face** (Haar cascade — a 2001 algorithm that is still fast enough for real time),
**prepare it exactly as in training** (grey, equalise, 48×48, normalise with the training numbers — any
difference silently ruins accuracy), and **classify it** with EmotionNet — a mini-ResNet of 4,900,551 weights
that you build and train yourself on FER-2013. Then make it pleasant: smooth the probabilities over a few frames
so the label does not flicker, and keep the camera in its own thread so the window never freezes.

## What is in this folder

| Folder | What it is | How to use it |
|---|---|---|
| `01_theory/` | Images, neural networks from zero, CNNs and ResNet, data and training, detection | Read one chapter before each notebook |
| `02_examples/` | Runnable notebooks — they run on any laptop (CPU); notebook 03 trains a small net in a few minutes | Run every cell, then change things and run again. **Run 03 before 04** (it saves the model) |
| `03_exercises/` | 12 exercises (17 tests) + `solutions.py` | Write, run `pytest`, only then look at the solution |
| `04_build/` | Architecture, the two build chapters, debugging | Use it next to `TASKS.md` in your project |
| `05_defence/` | Exam-style questions, answers, resources | Before the defence — and test yourself every few weeks |
| `06_solve/` | `CHECKLIST.md`: all 97 functions of your skeleton, stage by stage, with the test that checks each · `HINTS.md`: hidden hints, numbers to check against and the common traps for the hard ones · `WALKTHROUGH.md`: every function explained - the problem, the finished code and its test - and the finished project with screenshots | Tick the checklist as you go; open a hint only after you tried |
| `data/fer2013/` | **You put FER-2013 here** (same layout as your project) — see `data/README.md` | It is not in Git: we may not redistribute it |

## Setup (once)

From the repo's root folder:

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows   (Linux/macOS: source .venv/bin/activate)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121     # your GPU build first
pip install -r requirements.txt
```

Check: `python -c "import torch; print(torch.cuda.is_available())"` should print `True` on your laptop. Then copy
FER-2013 into `13_FaceEmotion/data/fer2013/` (see `data/README.md`), open a notebook from `02_examples/`, choose
the `.venv` kernel, **Run All**.

## Your lessons — see it before you build it

Illustrated lessons, each built around a **story**, **real-world examples**, pictures and animations from your own
data, diagrams, a **runnable worked example**, checked **videos** and exercises with answers (all lessons:
[`lessons/`](../lessons/README.md), or open `lessons/LESSONS.html` in a browser). Study each one **before** the stage it
belongs to. Studying alone? Follow the 8-step route in the
[lessons README](../lessons/README.md#learning-alone-follow-this-route-for-every-lesson).

| # | Lesson | In one sentence | Inside | Before your skeleton's … |
|---|---|---|---|---|
| 0 | [Lesson 00 — The maths toolkit: all the maths you need, from zero](../lessons/00_math_toolkit/LESSON.md) and the [glossary](../lessons/GLOSSARY.md) | the projects only use about twelve small pieces of maths — this lesson shows each one with a story, a picture, an everyday example, and a calculation you can do on paper. | 4 animations, 3 videos | before everything — and whenever a word or a formula is new |
| 1 | [Lesson 01 — What is "machine learning"?](../lessons/01_what_is_learning/LESSON.md) | instead of writing the rules yourself, you show the computer many examples **with the right answers**, and it finds the rules by itself. | 4 animations, 4 videos | before you start |
| 2 | [Lesson 19 — How a computer sees a picture: pixels, normalisation, equalisation](../lessons/19_images_as_numbers/LESSON.md) | for a computer a picture is a table of brightness numbers — and before the network sees it, we stretch the brightness (equalisation) and shrink the numbers around 0 (normalisation), in exactly the same way every time. | 2 animations, 2 videos | stage 2 |
| 3 | [Lesson 25 — Finding the face: Haar features, the integral image and the cascade](../lessons/25_face_detection_haar/LESSON.md) | to find a face fast, check simple light/dark patterns (computed in 4 reads each thanks to the integral image) in a chain of quick tests that throws away almost every non-face window at the first steps. | 2 animations, 3 videos | stage 2 |
| 4 | [Lesson 20 — A neural network from zero: neurons, layers, softmax, cross-entropy](../lessons/20_neurons_softmax/LESSON.md) | a neural network is many tiny "multiply, add, bend" units arranged in layers, each layer building more complex clues from the one before, ending in one score per class that softmax turns into probabilities. | 3 animations, 3 videos | stage 3 |
| 5 | [Lesson 22 — Convolution: a small stencil that slides over the picture](../lessons/22_convolution_pooling/LESSON.md) | instead of one giant layer looking at all pixels at once, a CNN slides small stencils (filters) over the picture, making maps of where each pattern appears — and stacks of such layers see edges, then face parts, then expressions. | 2 animations, 2 videos | stage 3 |
| 6 | [Lesson 23 — EmotionNet: residual blocks, BatchNorm, Dropout, and `train()` vs `eval()`](../lessons/23_resnet_batchnorm/LESSON.md) | EmotionNet stacks residual blocks — layers that only learn a *correction* and pass their input around them on a shortcut — plus BatchNorm (a z-score inside the network) and Dropout (random switch-offs), and the switch `eval()` tells the last two to behave when the model is used. | 1 animation, 4 videos | stage 3 |
| 7 | [Lesson 21 — How a network learns: backpropagation, optimisers and the learning-rate schedule](../lessons/21_backprop_optimizers/LESSON.md) | after each wrong answer, backpropagation passes the blame backwards through the network to find how every weight should change, and the optimiser moves every weight a small step in that direction — a million times. | 3 animations, 4 videos | stage 4 |
| 8 | [Lesson 24 — Training in practice: augmentation, class weights, label smoothing, early stopping](../lessons/24_training_in_practice/LESSON.md) | four standard tricks — change the training pictures a little every time, make mistakes on rare emotions cost more, don't demand 100 % certainty, and keep the best epoch — turn a network that memorises into one that generalises. | 2 animations, 2 videos | stage 4 |
| 9 | [Lesson 03 — Is the model good? Counting its right and wrong answers](../lessons/03_confusion_matrix_metrics/LESSON.md) | sort every answer into four boxes (caught, false alarm, missed, correct "no"), and from those four counts compute numbers that answer different questions: *can I trust it when it says yes?* and *does it catch everything?* | 2 animations, 2 videos | stage 4 |
| 10 | [Lesson 26 — Real time: the frame budget, the camera thread, and a label that doesn't flicker](../lessons/26_realtime_smoothing/LESSON.md) | read the camera in its own thread and always show the newest frame, and average the last few frames' probabilities so the label stays calm — accepting a tiny delay. | 2 animations | stage 5 |
| 11 | [Lesson 32 — Threads, race conditions and locks](../lessons/32_threads_locks/LESSON.md) | when several threads change the same data, their read–change–write steps can interleave and lose work; a lock lets only one thread at a time into that critical section — use one lock, with `with`, and hold it briefly. | 1 animation | stage 5 |
| 12 | [Lesson 33 — The database: constraints, transactions, indexes, parameters](../lessons/33_databases/LESSON.md) | let the database itself refuse bad rows (constraints), group changes so they happen all-or-nothing (transactions), find rows without reading them all (indexes), and never paste user text into SQL (parameters). | 1 animation, 1 video | stage 6 |

## Where to start — the learning path

Do the rows **in order**. Each row ends with something you can show your supervisor.

| # | Read (`01_theory/`) | Run (`02_examples/`) | Solve (`03_exercises/`) | Then in your project |
|---|---|---|---|---|
| 0 | `00_intro`, `02_ml_basics` | — | — | install (GPU!), open the skeleton, run `pytest` (red — normal) |
| 1 | `03_images_nn` §3, `06_data_training` §6.1–6.2 | `01_images_and_data` | ex01 – ex03 | stages 1–2 — camera, face detection |
| 2 | `03_images_nn` §4, `05_cnn` — count the 4,900,551 by hand | `02_neurons_to_resnet` | ex04 – ex07 | stage 3 — dataset and `EmotionNet` |
| 3 | `06_data_training` | `03_training_loop` | ex08 – ex10 | stage 4 — full training on the GPU, evaluation |
| 4 | `07_detection_realtime` | `04_detection_and_realtime` | ex11 – ex12 | stage 5 — real time, smoothing |
| 5 | `04_build/*` | — | — | stages 6–7 — database, UI, Haar vs DNN, the book |
| 6 | `05_defence/*` | re-run the notebooks and explain every number aloud | — | the defence |

## How to work with the exercises

```bash
cd 13_FaceEmotion/03_exercises
pytest test_exercises.py -k ex07 -v      # one exercise
pytest test_exercises.py -v              # everything
```

ex06 (your own convolution in numpy) must match PyTorch's `conv2d` for every stride and padding. ex07 (the
residual block) must have exactly the parameter counts of theory §5.6: 73,984 and 230,144.

## When you are stuck on your project

1. Find the function in `06_solve/CHECKLIST.md` — it names the stage and the test that checks it.
2. Read its docstring in your code again, slowly, and the matching step in `04_build/`.
3. Open `06_solve/HINTS.md` at that function: the 💡 hint first, the 🔧 steps only if you need them.
   Compare your output with the "check yourself" numbers.
4. Still stuck, or finished and want to compare? `06_solve/WALKTHROUGH.md` has the problem and the full solution of every function.
5. Still red after 30 honest minutes? Send your supervisor the test name and the last 10 lines of the error.

## The rule

The notebooks show **one** way to write each piece. Your project has its own structure (detector classes,
predictor, controller, views) — **type your project code yourself, do not paste from the notebooks.** In the
defence you will be asked to explain and change any line, and you can only do that with code you wrote.

## The numbers you should be able to explain

| | |
|---|---|
| FER-2013 pixel mean / std (training set, after equalizeHist) | 0.5013 / 0.2916 — measured in notebook 01 (raw: 0.5077 / 0.2551) |
| class weights (mean 1) | disgust highest (~16× happy) |
| EmotionNet parameters | 4,900,551 — 75% of them in block4 |
| convolution by hand | 570 for the vertical-edge example |
| a small CPU network (390k parameters), 8 epochs, ~65 s each | 42% test accuracy — your GPU EmotionNet target is ≥ 65% |
| …and its disgust class | recall 0.75 but precision 0.05: the ×4.4 class weight makes a young model over-call it |
| Haar on FER faces | 71 of 120 found as tight crops, 95 of 120 with a 30% border |
| smoothing over 5 frames | half the label flips, still follows a real change within a few frames |
