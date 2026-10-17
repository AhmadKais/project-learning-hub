# Lessons — every algorithm of the seven projects, taught with pictures

Thirty-four lessons: a maths toolkit (Lesson 00) and one lesson per algorithm or idea the projects need. They assume the
students **know no machine learning and are weak in maths**: every lesson starts from a **story** (a person with a real
problem), defines every word before using it, and does every calculation step by step, saying *why* each step is done. Each lesson is built **around pictures and
animations**: the text only explains what you are looking at. Every lesson is also written so a student can **learn it alone**: real-world examples, a runnable worked example, checked videos and graded exercises with answers. Use them to teach in class (projector), and give the
students the same pages to revise from.

**Two helpers for every lesson:** [Lesson 00 — the maths toolkit](00_math_toolkit/LESSON.md) (percentages, averages,
probability, Σ, powers, logarithms, eˣ, slope, distance — with pictures) and the [glossary](GLOSSARY.md) (every term in plain
words).

**The quickest way in:** open [`LESSONS.html`](LESSONS.html) in a browser (all 34 lessons in one page, the animations
play) and press F11. Or open any lesson's `LESSON.md` on GitHub / in VS Code.

## What every lesson contains

| Part | What it is for |
|---|---|
| **In one sentence** | the whole lesson in one line — read it first, and again at the end |
| 🗺️ **The map** | a diagram of the lesson's parts, so you always know where you are |
| **The story** | a person with a real problem (a shop owner, a recruiter, a bank clerk …) that the algorithm solves — it returns in every part (📖) |
| **Words you need** | every new term defined *before* it is used, with the story's example |
| 🌍 **Real world** | where you already meet this idea: Gmail, Netflix, face unlock, banks, maps, a supermarket receipt … |
| **Parts, one idea each** | the idea in plain words (🧠), a picture or animation (🖼️), a calculation by hand (✍️), and a quick check with a hidden answer (✅) |
| **Animations** (`figs/*.gif`) | the algorithm *moving*: a filter sliding, a tree growing, a threshold sweeping, a race between threads |
| **Videos** (`videos/*.mp4`) | the same animations for the projector — pause and step with the arrow keys |
| **Diagrams** | flow charts, state diagrams, sequence diagrams and tables drawn with Mermaid (they render on GitHub and in `LESSONS.html`) |
| **Real data** | most pictures and numbers come from the projects' own data: the SMS, the URLs, the CVs, the wines, the trained face network |
| 🧪 **Worked example** | a short, **runnable** program that does the lesson's calculation — every printed number was checked |
| **Try it yourself** | 🟢 easy → 🟡 medium → 🔴 hard questions, answers hidden (click to open) |
| **Common mistakes** | what students typically believe, and the truth |
| 📝 **Summary** | the whole lesson on one card — for revision before the defence |
| **Class activities** | unplugged games (human k-NN, paper convolution, be-the-cascade …), predict-then-run, break-it-on-purpose |
| **In your project** | the exact files, functions, tests, exercises and notebooks of the student's skeleton |
| 🎬 **Watch & explore** | real, checked videos (StatQuest, 3Blue1Brown, Computerphile …) with thumbnails, and interactive sites |
| 🎓 **For the defence** | the advanced material, folded away until you need it |
| `visualize.py` | the code that draws every picture — runnable, and part of the lesson: change a number, run again |

## Learning alone? Follow this route for every lesson

1. Read **In one sentence** and **the map**. Don't worry if it isn't clear yet.
2. Read **the story** and the **Words you need** table.
3. For each Part: read the idea, **watch the animation twice**, do the ✍️ calculation yourself on paper **before** reading
   the solution, then open the ✅ quick check.
4. Watch the first video in 🎬 *Watch & explore*.
5. Run the 🧪 worked example; then change one number and predict the new output before running it again.
6. Do *Try it yourself* — all the 🟢, then the 🟡. Leave the 🔴 for a second reading.
7. Read the 📝 summary. Can you explain each line to a friend without looking? If not, go back to that Part.
8. Only then open your skeleton's stage (`TASKS.md`) and the matching notebook.

Most pictures use the **projects' real data** (the SMS corpus, the PhishGuard URLs, the 200 CVs, the wines, the hotel's
24 rooms). FER-2013 faces may not be redistributed, so the face lessons draw their own faces.

## The lessons

| # | Lesson | For | The pictures that carry it |
|---|---|---|---|
| 00 | [The maths toolkit](00_math_toolkit/LESSON.md) | everyone, first | percentages, average, spread, probability, logs, slope, distance |
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

Start every student with Lesson 00 (or the sections of it their lessons point to). Lessons 01, 02, 03, 05 and 33 are shared by four or more students — teach them to the whole group together.

## How to teach a lesson (a 45-minute plan that works for all of them)

1. **Story (3 min)** — tell the lesson's story; ask the class how *they* would solve it before any algorithm.
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
