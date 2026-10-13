# Part C — Pass the exam

# Chapter 17 — Question and answer bank

Go over the questions **after** the code works. Every answer is 2–4 sentences, at the level expected
from you. When you answer — point at the file and the line in your code. Examiners are impressed by
"this happens in `trainer.py` at the `scaler.step` line" much more than by a definition from a book.

## 17.1 The problem and the data

**1. What does the system do, in one sentence?** It recognizes in real time the emotion on a face
from the camera — one of seven — using a convolutional network I trained on FER-2013, and records
the results over time.

**2. What is FER-2013?** A dataset of 35,887 face pictures, 48×48, grayscale, labeled with seven
emotions, from an ICML 2013 competition. Known as hard: noisy labels, imbalance (436 disgust vs.
7,215 happy), and human accuracy of about 65%.

**3. Why exactly 7 emotions?** According to Ekman (1978) — seven basic emotions whose expression is
universal across cultures: happy, sad, angry, fear, surprise, disgust and neutral. The dataset is built on them.

**4. What is the difference between a facial expression and an emotion?** An expression is what you
see on the face; an emotion is what the person feels. Barrett (2019) showed the link between them is
weaker than people thought — a person can smile out of politeness. The system recognizes
**expressions**; saying "emotion" is a shortcut. This is a declared limitation in the book.

**5. Why is the expected accuracy only 65%?** Because that is roughly human accuracy on this
dataset. Above it — the model is better than the labelers. Reasons: small and noisy pictures, wrong
labels, and emotions that look alike (fear/surprise).

**6. What is multi-class classification?** Choosing one category out of more than two. The output is
a probability vector of length 7 that sums to 1, and we choose the maximum.

## 17.2 Machine learning — basics

**7. What is the difference between normal programming and machine learning?** In programming I
write the rules; in learning I give examples with answers and the algorithm finds the rules as
numeric weights.

**8. What is supervised learning?** Learning from labeled examples — every picture has a correct
answer. This is the kind of learning in the project.

**9. Why split into train/validation/test?** Train — to learn. Validation — to decide when to stop
and which model to keep. Test — a final score on data that influenced no decision. If you choose a
model by the test, the score is biased upward.

**10. What is overfitting and how did you recognize it?** The model memorizes the training data and
does not generalize: high train accuracy, validation low and falling. You see it in
`training_curves.png` when the curves separate. Treatment: augmentation, dropout, weight decay,
early stopping, label smoothing.

**11. What is underfitting?** The model does not even learn the training data — too small, wrong
learning rate, or too few epochs.

**12. What is the difference between accuracy and F1 and why did you measure F1 too?** Accuracy
measures total correctness and hides rare classes. F1 per class combines precision (of what I
said — how much was right) and recall (of what exists — how much I caught). Without F1 I would not
have seen that disgust is recognized badly.

**13. What is a confusion matrix and what did you learn from it?** A truth×prediction table. The
diagonal is correct, the rest are mistakes. In mine [name the pair that got mixed — usually
fear↔surprise and sad↔neutral].

**14. What is data augmentation and why only in training?** Random changes (flip, rotation, crop)
that prevent memorization and simulate different shooting conditions. In evaluation and real time
we want a deterministic result of the real picture.

**15. What are class weights?** A weight in the loss function inverse to the class frequency, so a
mistake on "disgust" costs ~16 times more than on "happy". Balances an imbalanced dataset without
throwing data away.

**16. What is label smoothing?** A target of 0.9 instead of 1.0 for the correct class. Prevents
over-confidence, is robust to wrong labels, and improves calibration — the shown confidence is
close to the real accuracy.

## 17.3 Neural networks

**17. What is a neuron?** A weighted sum of the inputs plus a bias, through an activation function.
`ReLU(w·x + b)`.

**18. Why do you need an activation function?** Without non-linearity, all the layers collapse into
one linear operation that cannot learn complex patterns.

**19. What is ReLU and why it and not Sigmoid?** `max(0,x)`. Cheap to compute and does not suffer
from the vanishing gradient like Sigmoid, whose derivative is close to zero over most of its range.

**20. What is Softmax and where is it in your code?** Turns logits into probabilities that sum to 1.
**Not** in `forward()` — `CrossEntropyLoss` applies it in training, and I apply it explicitly in
`EmotionPredictor.predict()`.

**21. What is a loss function and which did you choose?** A number that measures the distance from
the correct answer. Cross-entropy: `-log(p_correct)` — strongly penalizes high confidence in a wrong answer.

**22. What is a gradient?** For every weight: in which direction and by how much the loss changes if
you move it. PyTorch computes it in `loss.backward()` using backpropagation.

**23. What is backpropagation?** An algorithm that computes the gradient of all the weights in one
backward pass through the network, using the chain rule.

**24. What does the optimizer do?** Updates weights according to the gradient. AdamW adapts the step
per weight and adds weight decay (a penalty on big weights).

**25. What is the learning rate and what happens if it is too big/small?** The step size. Too big —
the loss jumps or becomes `nan`; too small — slow and stuck. Hence warm-up and then cosine.

**26. Epoch, batch, iteration?** Epoch — all the training data once. Batch — 128 pictures for one
update. Iteration — one update. ~202 iterations per epoch for me.

**27. Why a batch and not picture by picture?** The GPU computes in parallel; a batch uses it. And a
gradient over 128 pictures is less noisy than over one.

**28. What is dropout and why is it off in `eval()`?** Randomly switching off neurons in training
so the network does not depend on a single neuron. In inference we want the whole network, deterministic.

**29. What is BatchNorm?** Normalizing a layer's output over the batch. Stabilizes training and allows
a higher learning rate. In `eval()` it uses averages collected during training.

**30. What is the difference between `model.train()` and `model.eval()`?** A mode switch for Dropout
and BatchNorm. It does not train and does not evaluate. Forgetting `eval()` before inference = random results.

**31. What does `torch.no_grad()` do?** Disables recording the graph for gradient computation. Saves
memory and time in inference. Complements `eval()`, does not replace it.

**32. How many weights in your network?** 4,900,551 — and break it down by layer (section 5.6).

## 17.4 CNN and ResNet

**33. What is a convolution?** A small kernel (3×3) that slides over the picture and computes a sum of
products at every position. Produces a feature map that lights up where the pattern appears. The
network learns the kernel.

**34. Why a CNN and not a dense network for pictures?** Weight sharing (a pattern is learned once for
all positions) and locality (every output depends on a small neighborhood). Far fewer parameters and
robustness to shifts.

**35. What does stride=2 do?** The kernel jumps 2 pixels — the output is 2× smaller in each axis.
For me 48→24→12→6 while the channels go 64→512: less "where", more "what".

**36. What is global average pooling?** The average of every feature map into one number.
512 maps → 512 numbers → the output layer. Replaces a big Flatten and reduces overfitting.

**37. What is a residual block and why?** `out = F(x) + x`. Solves the vanishing gradient in deep
networks: the gradient flows through the shortcut, and the block learns only a "correction". He et al. 2016.

**38. What happens in the shortcut when the shapes are not equal?** A 1×1 convolution with the same
stride and BatchNorm, which only matches channels and resolution.

**39. What is the vanishing gradient?** The gradient gets weaker at every layer backward and reaches
almost zero at the first layers, which then do not learn. ResNet solves this.

**40. Describe your network layer by layer.** [The table in section 5.5 — know it by heart.]

## 17.5 Face detection

**41. How does a Haar cascade work?** Rectangle features (dark eyes vs. cheeks), an integral image
for fast computation, AdaBoost to choose features, and a cascade that rejects background early.

**42. What is an integral image?** Every cell = the sum of all pixels above it and to its left. The
sum of any rectangle in 4 reads, regardless of size.

**43. What does `minNeighbors` do?** How many overlapping windows must agree. Low — false detections;
high — misses. I chose 5 [or whatever you tuned].

**44. Why also a DNN detector?** Haar misses profiles and side lighting. The DNN is more robust but
2–3 times slower. I compared by measurement [your table]. Both inherit from `FaceDetector`.

**45. Why not give the network the whole frame?** The network was trained on centered 48×48 faces.
Separating "where" from "what" makes each task easy and allows changing the detector without retraining.

## 17.6 Real time

**46. What is the time budget per frame?** 66 ms for 15 FPS. For me: detection ~X ms, inference ~Y ms,
total Z FPS [your numbers].

**47. Why is the camera in a separate thread?** `cap.read()` blocks 30–40 ms. In the main thread it
would freeze the GUI. The thread keeps only the latest frame — no queue builds up.

**48. Why a `Lock` and why `copy()`?** Two threads on the same variable — the lock prevents reading in
the middle of a write. The copy prevents drawing from changing the buffer the thread writes to.

**49. Why `root.after` and not `while True`?** Tkinter is single-threaded; my own loop freezes the
window. `after` schedules one frame and frees Tk between frames.

**50. What does temporal smoothing do and why on the vectors?** A moving average of 5 probability
vectors. Prevents flickering on a borderline expression. On the vectors and not the labels because the
average respects each frame's confidence (example in section 8.4).

**51. What is train/serve skew and how did you prevent it?** Different pre-processing in training and
in real time. I prevented it: the same steps and the same normalization constants from `config.py`
in both pipelines, and the constants are also saved inside the checkpoint.

## 17.7 GPU and PyTorch

**52. Why a GPU?** Training is parallel matrix multiplications; thousands of GPU cores do them in
parallel. For me: [time on GPU] vs. [estimate for CPU].

**53. What is CUDA?** NVIDIA's platform for running general computation on the card. PyTorch uses
it through `.to("cuda")`.

**54. What is a tensor?** A multi-dimensional array like numpy, but it can sit on a GPU and track
gradients. My picture: `(1, 1, 48, 48)` — batch, channel, height, width.

**55. What is AMP and what is the GradScaler?** Computing in float16 for speed and memory. The
scaler multiplies the loss so small gradients do not become zero in float16, and divides back before the update.

**56. What happens if there is no GPU?** `config.DEVICE` falls back to CPU, AMP is off. The code runs — slowly.

**57. What is saved in a checkpoint?** `state_dict` (the weights), epoch, validation accuracy, and the
normalization constants — so a model is not used with the wrong normalization.

**58. Why `map_location` in `torch.load`?** A model saved from a GPU loads on a CPU without an error.

## 17.8 Architecture and software

**59. What is MVC in your project?** Model — `models/ vision/ ml/ database/` (no tkinter);
View — `views/` (only tkinter); Controller — `controllers/` in between. Can be proven with grep.

**60. Which design pattern is in `FaceDetector`?** Strategy — one interface, two implementations,
switching at runtime. And `create_detector` is a Factory.

**61. Why a Singleton in `EmotionPredictor`?** Expensive loading to the GPU once. Downside: makes tests
harder — that is why `conftest.py` resets `_instance`.

**62. What is a Repository?** All the SQL in one class; the rest of the code works with objects.
Changing the DB = one file.

**63. Why SQLite?** A single file, no server, built into Python, enough for tens of thousands of
samples. PostgreSQL would be operational overhead with no benefit for a desktop application.

**64. Describe the schema.** `sessions` 1→* `emotion_samples` (FK with CASCADE), and `models` for
recording experiments. Indexes on `session_id` and `timestamp`.

**65. Why `PRAGMA foreign_keys=ON`?** In SQLite foreign keys are off by default; without it CASCADE does not work.

**66. How did you prevent SQL injection?** Always `?` placeholders, never string concatenation.

**67. Why `executemany` and a buffer of 60?** Writing on every frame slows the GUI. Batching — the
same principle as a batch in training.

**68. What did you test in `tests/` and why exactly that?** Pure logic without hardware: smoothing, box
geometry, pre-processing, network shapes, DB repositories on a temporary file. The camera and the GUI I
tested manually — they depend on hardware.

**69. What is `@contextmanager`?** Turns a function with `yield` into a `with` block: what is before the
`yield` runs on entry, what is after — on exit (commit/rollback/close).

**70. Why `daemon=True` on the camera thread?** So closing the window ends the program even if the thread is still running.

## 17.9 Ethics and limitations

**71. What are the privacy issues?** Filming faces is biometric data. In mine: local processing only,
no pictures are saved — only emotion, confidence and box. This can be documented as a non-functional requirement.

**72. What bias is in the dataset?** FER-2013 was collected from the internet with no demographic
balance; the model may be less accurate on some groups. I did not measure by group — a declared limitation.

**73. Possible misuse?** Monitoring employees/students without consent. The system is intended for
self-aware use, and does not measure "real emotion" — only expression.

**74. What would you improve with another month?** [Pick 2 from "future development" in the proposal,
and explain why those.]

**75. What was the hardest problem and how did you solve it?** [Yours. Write it down now in `TASKS.md`
when it happens — in the defense you will not remember.]

# Chapter 17a — "Explain your code": line-by-line drills

In the defense they will open a random file and ask "explain". Practice on **your** code — for every
section below, explain out loud (or in writing) every line: what it does, why it is there, and what
would happen without it. If for any line the answer is "that is how it works" — you are not done yet.

1. **`ResidualBlock.forward`** — 5 lines. You must mention: the order Conv→BN→ReLU, why the addition
   is before the last ReLU, when `shortcut` is the identity.
2. **`ModelTrainer.train_one_epoch`** — the inner loop. The 6 lines from section 13.2, including
   `non_blocking`, `set_to_none`, and what `autocast` wraps and what it does not (the `backward` is outside!).
3. **`FacePreprocessor.to_model_input`** — 6 steps. For every step: what happens in real time if I skip
   it? (grayscale → channel error; resize → shape error; equalizeHist → low accuracy in bad light;
   /255 → huge values; normalize → skew; reshape → batch error).
4. **`FER2013Dataset.__getitem__`** — why there is `_remap`, and what would happen without it
   (demonstrate on "sad": folder 5 → Emotion 4).
5. **`EmotionPredictor.__new__` and `__init__`** — what happens on the first call, what on the second.
6. **`TemporalSmoother.update`** — why `np.stack`, why `axis=0`, what `deque(maxlen)` does when full.
7. **`Database.connection`** — the order `yield / commit / rollback / close`, and what happens in each
   of the three scenarios: success, exception, exception inside the `except`.
8. **`CameraService._reader_loop` + `read`** — who holds the Lock when, and why `copy()`.
9. **`AppController._on_frame`** — the flow from section 9.9, including what happens when there is no
   face (`smoother.reset()` — why?).
10. **`compute_class_weights`** — the formula, the normalization, and why the result goes through `.to(device)`.
11. **`build_dataloaders`** — why two `FER2013Dataset` on the same folder, how the `Subset` guarantees
    no overlap, and what the `generator` is.
12. **`SCHEMA`** — every column: type, why, and what `ON DELETE CASCADE` is.

💡 Record yourself explaining 3 of the sections. Listen. If you say "actually" more than twice per
sentence — you are not sure. Go back to the matching chapter.

# Chapter 18 — Glossary

| Term | Short explanation |
|---|---|
| Accuracy | Percentage of correct answers |
| AMP | Mixed precision: compute in float16, keep in float32 |
| Augmentation | Random changes to training pictures |
| Backpropagation | Computing gradients backward through the network |
| Batch | A group of samples for one update |
| BatchNorm | Normalizing a layer's output |
| Checkpoint | A file of weights + metadata |
| Class weights | Compensation for imbalance |
| CNN | Convolutional network: a network for pictures with sliding kernels |
| Confusion matrix | Truth vs. prediction table |
| Cross-entropy | Loss function for classification |
| CUDA | NVIDIA's platform for computing on the GPU |
| Dropout | Randomly switching neurons off in training |
| Early stopping | Stopping when validation stops improving |
| Epoch | One pass over all the training data |
| F1 | Harmonic mean of precision and recall |
| Feature map | Output of a convolution kernel |
| FPS | Frames per second: the processing rate |
| Gradient | Direction and size of the change in loss |
| Haar cascade | The Viola–Jones detector |
| Inference | Using a trained model |
| Integral image | Cumulative sums for rectangle computation |
| Kernel | A small filter in a convolution |
| Label | The correct answer |
| Label smoothing | A target of 0.9 instead of 1.0 |
| Learning rate | The size of the update step |
| Logits | Raw output before Softmax |
| Loss | The measure of error |
| MVC | Separation of Model / View / Controller |
| Optimizer | Updates the weights (AdamW) |
| Overfitting | Memorizing instead of generalizing |
| Precision / Recall | Per-class measures |
| ReLU | Activation function max(0,x) |
| Repository | A data-access class |
| Residual block | A block with a shortcut |
| Singleton | Only one instance |
| Softmax | Logits → probabilities |
| Strategy | One interface, several implementations |
| Stride | The kernel's jump |
| Supervised | Learning from labeled examples |
| Tensor | PyTorch's multi-dimensional array |
| Train/Val/Test | The three data groups |
| Vanishing gradient | A gradient that weakens in deep layers |
| Weight | A learned parameter |
