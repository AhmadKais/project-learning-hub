# Lessons — every algorithm of the seven projects, taught with pictures

Thirty-three lessons, one per algorithm or idea the projects need. Each lesson is built **around pictures and
animations**: the text only explains what you are looking at. Use them to teach in class (projector), and give the
students the same pages to revise from.

**The quickest way in:** open [`LESSONS.html`](LESSONS.html) in a browser (all 33 lessons in one page, the animations
play) and press F11. Or open any lesson's `LESSON.md` on GitHub / in VS Code.

## What every lesson contains

| Part | What it is for |
|---|---|
| 🎯 **Goals** | 3–5 things the student can do at the end — check them in the defence-style questions |
| **The picture** | every lesson starts from an illustration, never from a formula |
| **Animations** (`figs/*.gif`) | the algorithm *moving*: a filter sliding, a tree growing, a threshold sweeping, a race between threads |
| **Videos** (`videos/*.mp4`) | the same animations for the projector — pause and step with the arrow keys |
| **Definitions** | one table of the words, with the project's own example for each |
| **The maths, by hand** | worked examples with the **projects' real numbers** (4,445.06 · 1.2877 · P(spam\|free) = 0.75 …) |
| **The algorithm** | short pseudocode / Python sketch, the same shape as the skeleton's TODO |
| **Misconceptions** | what students typically believe, the truth, and how to show it |
| **Activities** | unplugged games (human k-NN, paper convolution, be-the-cascade …), predict-then-run, break-it-on-purpose |
| **Check yourself** | questions with hidden answers (click to open) |
| **In your project** | the exact files, functions, tests, exercises and notebooks of the student's skeleton |
| 🎬 **Watch & explore** | short videos (StatQuest, 3Blue1Brown, Computerphile …) and interactive sites |
| `visualize.py` | the code that draws every picture — runnable, and part of the lesson: change a number, run again |

Most pictures use the **projects' real data** (the SMS corpus, the PhishGuard URLs, the 200 CVs, the wines, the hotel's
24 rooms). FER-2013 faces may not be redistributed, so the face lessons draw their own faces.

## The lessons

| # | Lesson | For | The pictures that carry it |
|---|---|---|---|
| | **Unit 1 — machine-learning foundations** | | |
| 01 | [What "learning" means: data, splits, overfitting](01_what_is_learning/LESSON.md) | Laith · Ryan · Dani · Seif | overfitting animation, bias/variance dartboards |
| 02 | [Feature scaling](02_feature_scaling/LESSON.md) | Seif · Dani · Laith · Ryan | neighbours before/after, z-score animation, zig-zag gradient descent |
| 03 | [Confusion matrix, precision, recall, F1](03_confusion_matrix_metrics/LESSON.md) | Laith · Dani · Seif · Ryan | the fishing net, threshold sweep, accuracy trap, macro-F1 |
| 04 | [The threshold, ROC and AUC](04_threshold_roc/LESSON.md) | Laith · Dani | ROC drawn point by point, AUC as pairs, the two threshold rules |
| 05 | [Cross-validation, nested CV, leakage](05_cross_validation_leakage/LESSON.md) | Seif · Laith · Dani | k-fold animation, 89 % on pure noise, the duplicate trap |
| | **Unit 2 — text and search** | | |
| 06 | [Cleaning text](06_text_preprocessing/LESSON.md) | Laith · Kosai | both pipelines step by step, `\w+` vs TOKEN_PATTERN, Zipf |
| 07 | [TF-IDF](07_tfidf/LESSON.md) | Kosai · Laith | the matrix built step by step, the IDF curve, a real CV |
| 08 | [Vectors and cosine similarity](08_vectors_cosine/LESSON.md) | Kosai | arrows, rotating angle, the length trap, a real ranking |
| 09 | [BM25 and the inverted index](09_bm25_inverted_index/LESSON.md) | Kosai | saturation (k1 sweep), the b knob, the index walk, the b = 0 experiment |
| 10 | [P@k and MRR](10_ranking_metrics/LESSON.md) | Kosai | walking down a ranking, TF-IDF vs BM25 on the real data |
| | **Unit 3 — classic models** | | |
| 11 | [Naive Bayes from scratch](11_naive_bayes/LESSON.md) | Laith | Bayes as areas, a message classified word by word, log-odds |
| 12 | [Logistic regression and gradient descent](12_logistic_regression/LESSON.md) | Dani (· Ryan) | sigmoid, log-loss, a boundary learning on real URLs |
| 13 | [Decision trees and random forests](13_trees_forests/LESSON.md) | Dani | Gini, a tree overfitting, a forest voting, importance |
| 14 | [SVM and calibration](14_svm_calibration/LESSON.md) | Laith | the widest street, the C sweep, Platt scaling |
| 15 | [k-nearest neighbours](15_knn/LESSON.md) | Seif | the neighbourhood growing on real wines, k regions, alpha |
| 16 | [The kd-tree and the curse of dimensionality](16_kdtree/LESSON.md) | Seif | building cut by cut, search with pruning, 2 % → 59 % |
| 17 | [Learning feature weights](17_feature_weights/LESSON.md) | Seif | the staircase score, coordinate search live, the incremental update |
| 18 | [URL features and entropy](18_url_features_entropy/LESSON.md) | Dani | URL anatomy, entropy string by string, train/serve skew |
| | **Unit 4 — deep learning and vision** | | |
| 19 | [Images as numbers](19_images_as_numbers/LESSON.md) | Ryan | zoom into pixels, BGR, equalisation, normalisation |
| 20 | [Neurons, layers, softmax](20_neurons_softmax/LESSON.md) | Ryan | a neuron with numbers, a forward pass, softmax training |
| 21 | [Backprop, optimisers, the schedule](21_backprop_optimizers/LESSON.md) | Ryan | backprop step by step, learning rates, SGD vs Adam |
| 22 | [Convolution and pooling](22_convolution_pooling/LESSON.md) | Ryan | a filter sliding with numbers, real filters, receptive field |
| 23 | [ResNet, BatchNorm, Dropout](23_resnet_batchnorm/LESSON.md) | Ryan | EmotionNet's shapes, the residual block, vanishing gradients |
| 24 | [Training in practice](24_training_in_practice/LESSON.md) | Ryan | augmentation, class weights, label smoothing, early stopping |
| 25 | [Face detection: Haar and the cascade](25_face_detection_haar/LESSON.md) | Ryan | Haar features, the integral image, sliding windows |
| 26 | [Real time and smoothing](26_realtime_smoothing/LESSON.md) | Ryan | the frame budget, flicker vs smoothed, the delay |
| | **Unit 5 — systems and business algorithms** | | |
| 27 | [Interval overlap](27_intervals_overlap/LESSON.md) | Eran | nights not days, all eight cases, the De Morgan proof |
| 28 | [Room allocation strategies](28_allocation_strategies/LESSON.md) | Eran | a month filling up, the 200-month experiment |
| 29 | [The pricing rule chain](29_rule_chain_pricing/LESSON.md) | Eran | the invoice waterfall, the chain, the wrong order |
| 30 | [State machines (+ LanGame scoring)](30_state_machines/LESSON.md) | Eran · Liraz | both FSMs animated, the transition table, scoring |
| 31 | [TCP streams and framing](31_tcp_framing/LESSON.md) | Liraz | glued and cut messages, a live socket demo |
| 32 | [Threads, races, locks](32_threads_locks/LESSON.md) | Liraz (· Ryan) | the race step by step, a measured race, deadlock |
| 33 | [Databases: constraints, transactions, indexes](33_databases/LESSON.md) | Eran · Liraz · all | real IntegrityErrors, rollback, the index measured |

## The order for each student

Teach the lesson **before** the student starts that stage of the skeleton (`TASKS.md`).

| Student | Project | Lessons, in order (→ skeleton stage) |
|---|---|---|
| Laith | SpamClassifier | 01 → 06 (st. 2) → 07 (st. 3) → 11 (st. 4) → 02, 05, 14 (st. 5) → 03, 04 (st. 6) → 33 (st. 7) |
| Ryan | FaceEmotion | 01 → 19, 25 (st. 2) → 20, 22, 23 (st. 3) → 21, 24, 03 (st. 4) → 26, 32 (st. 5) → 33 (st. 6) |
| Eran | HotelManager | 27 (st. 1) → 33 (st. 2) → 28 (st. 3) → 29 (st. 4) → 30 (st. 5) |
| Dani | PhishGuard | 01 → 18 (st. 1–2) → 02, 12 (st. 3) → 13, 05, 03, 04 (st. 4) → 33 (st. 6) |
| Kosai | ResumeMatch | 06 (st. 2) → 07 (st. 3) → 08 (st. 4) → 09 (st. 5) → 10 (st. 6) → 33 (st. 8) |
| Seif | WineGrader | 01 → 02 (st. 3) → 03, 15 (st. 4) → 16 (st. 5) → 05, 17 (st. 6) → 33 (st. 7) |
| Liraz | LanGame | 31 (st. 1–2) → 32 (st. 2) → 33 (st. 3) → 30 (st. 4) |

Lessons 01, 02, 03, 05 and 33 are shared by four or more students — teach them to the whole group together.

## How to teach a lesson (a 45-minute plan that works for all of them)

1. **Hook (3 min)** — the question at the top of the lesson, or the first picture with no explanation: *"what do you see?"*
2. **Predict (2 min)** — before playing the animation, students guess on paper what will happen.
3. **Watch (10 min)** — play the GIF / MP4; pause at each step and let a student say the numbers aloud.
4. **By hand (10 min)** — the worked example on the board, then a second one in pairs (in *Activities*).
5. **Unplugged (10 min)** — one activity from the lesson: students *are* the algorithm.
6. **Misconceptions (5 min)** — read the table; ask who believed which one.
7. **Exit ticket (5 min)** — one *Check yourself* question on paper; the answers tell you what to repeat.

Homework: the matching notebook in `NN_Project/02_examples/` and exercises in `03_exercises/`, then the skeleton stage.

## Running the pictures yourself

```bash
pip install -r requirements.txt           # numpy, matplotlib, scikit-learn, nltk ... (+ ffmpeg for the MP4s)
cd lessons/15_knn
python visualize.py                       # redraw this lesson's figs/ and videos/
python visualize.py --live                # the interactive version with a slider (lessons 01, 02, 03, 04, 09, 15)
python visualize.py --only knn_query      # just one picture
```

Live demos that run real code in class: `31_tcp_framing/demo_socket.py` (TCP gluing and cutting messages) and
`32_threads_locks/race_demo.py` (a real race condition, then the lock).

**For the teacher — rebuilding everything:** `python tools/build_lessons.py` redraws every lesson and rebuilds
`LESSONS.html` (needs pandoc; `--no-video` skips the MP4s, `--html-only` only rebuilds the HTML). Edit a lesson's
`LESSON.md` or `visualize.py`, never the generated files. Shared drawing code (colours, the drawn faces, the PhishGuard
features) is in `_viz/common.py`.
