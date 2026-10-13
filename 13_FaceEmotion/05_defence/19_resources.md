# Chapter 19 — Reading plan and resources

The order matters: every item assumes the previous ones.

## 19.1 Before stage 1 (first week — understand)

| # | Source | What | Time |
|---|---|---|---|
| 1 | 3Blue1Brown — Neural Networks, parts 1–4 · https://www.3blue1brown.com/topics/neural-networks | Neuron, layers, gradient, backprop — visual | 1 hour |
| 2 | Google ML Crash Course — Classification · https://developers.google.com/machine-learning/crash-course | Accuracy/Precision/Recall, overfitting | 2 hours |
| 3 | CNN Explainer · https://poloclub.github.io/cnn-explainer/ | Play with convolution by hand | 30 min |
| 4 | Chapters 1–5 of this guide | Make sure it all connects | one evening |

## 19.2 Before stage 3 (before writing a network)

| # | Source | What | Time |
|---|---|---|---|
| 5 | PyTorch — 60 Minute Blitz · https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html | Tensors, autograd, first network, first training | 2 hours |
| 6 | Karpathy — micrograd · https://www.youtube.com/watch?v=VMj-3S1tku0 | Backprop from zero in Python. After it section 4.8 is completely clear | 2.5 hours |
| 7 | CS231n notes — Convolutional Networks · https://cs231n.github.io/convolutional-networks/ | Output sizes, parameters, architectures | 1.5 hours |
| 8 | ResNet paper, pp. 1–4 · https://arxiv.org/abs/1512.03385 | The source of the residual block, for the bibliography | 45 min |

## 19.3 Before stage 4 (before full training)

| # | Source | What | Time |
|---|---|---|---|
| 9 | PyTorch — AMP examples · https://pytorch.org/docs/stable/notes/amp_examples.html | The code of `trainer.py` | 30 min |
| 10 | PyTorch — Data tutorial · https://pytorch.org/tutorials/beginner/basics/data_tutorial.html | Dataset / DataLoader | 45 min |
| 11 | CS231n notes — Neural Networks 3 · https://cs231n.github.io/neural-networks-3/ | Learning rate, Adam, how to read training curves | 1 hour |
| 12 | Kaggle FER-2013 + public notebooks · https://www.kaggle.com/datasets/msambare/fer2013 | What others achieved and how | 1 hour |

## 19.4 Before stages 5–6

| # | Source | What | Time |
|---|---|---|---|
| 13 | OpenCV — Cascade Classifier · https://docs.opencv.org/4.x/db/d28/tutorial_cascade_classifier.html | Haar in practice | 30 min |
| 14 | Real Python — GIL · https://realpython.com/python-gil/ | Why a thread for the camera works | 30 min |
| 15 | TkDocs — Event Loop · https://tkdocs.com/tutorial/eventloop.html | `after` | 20 min |
| 16 | Refactoring Guru — Strategy / Singleton / Factory Method · https://refactoring.guru/design-patterns | The patterns with Python examples | 1 hour |
| 17 | Python docs — sqlite3 · https://docs.python.org/3/library/sqlite3.html | `row_factory`, transactions, `executemany` | 45 min |
| 18 | pytest — Getting Started · https://docs.pytest.org/en/stable/getting-started.html | Running and writing tests | 30 min |

## 19.5 Going deeper (if there is time — highly recommended)

- **Michael Nielsen — Neural Networks and Deep Learning** (free book, chapters 1–3, 6):
  http://neuralnetworksanddeeplearning.com/
- **fast.ai — Practical Deep Learning for Coders** (free, practical course): https://course.fast.ai/
- **DeepLearning.AI — Deep Learning Specialization** (Andrew Ng; free to watch): https://www.coursera.org/specializations/deep-learning
- **Stanford CS231n — lectures** (YouTube): https://www.youtube.com/playlist?list=PLC1qU-LWwrF64f4QKQT-Vg5Wr4qEE1Zxk
- **Dive into Deep Learning** (interactive book with PyTorch code): https://d2l.ai/

## 19.6 Papers for the project book bibliography

| Topic | Paper | Link |
|---|---|---|
| FACS | Ekman & Friesen (1978), Facial Action Coding System | https://www.paulekman.com/facial-action-coding-system/ |
| The dataset | Goodfellow et al. (2013), Challenges in Representation Learning | https://arxiv.org/abs/1307.0414 |
| ResNet | He et al. (2016), Deep Residual Learning | https://arxiv.org/abs/1512.03385 |
| Haar | Viola & Jones (2001), Rapid Object Detection | https://www.cs.cmu.edu/~efros/courses/LBMV07/Papers/viola-cvpr-01.pdf |
| BatchNorm | Ioffe & Szegedy (2015) | https://arxiv.org/abs/1502.03167 |
| Dropout | Srivastava et al. (2014) | https://jmlr.org/papers/v15/srivastava14a.html |
| AdamW | Loshchilov & Hutter (2019), Decoupled Weight Decay | https://arxiv.org/abs/1711.05101 |
| Label smoothing | Müller et al. (2019), When Does Label Smoothing Help? | https://arxiv.org/abs/1906.02629 |
| Limitations | Barrett et al. (2019), Emotional Expressions Reconsidered | https://journals.sagepub.com/doi/10.1177/1529100619832930 |
| AMP | Micikevicius et al. (2018), Mixed Precision Training | https://arxiv.org/abs/1710.03740 |

Citation rule: every paper in the bibliography — you read at least its abstract and main figure, and
you can say in one sentence what it contributed to the project. Examiners check this.
