"""FaceEmotion - exercises.

Fill in every function marked TODO. Use numpy (and torch where the docstring says so).
Check yourself after each exercise:

    pytest test_exercises.py -k ex01 -v        # one exercise
    pytest test_exercises.py -v                # all of them

Stuck for more than 20 minutes? Re-read the theory section named in the
docstring, look at the notebook, and only then open solutions.py.
"""
from collections import deque

import numpy as np

MEAN, STD = 0.5077, 0.2550


# ---------------------------------------------------------------- images and data (notebook 01)

def ex01_normalize(img):
    """uint8 image (any shape) -> float32 array: (img / 255 - MEAN) / STD.  Theory 3.2"""
    raise NotImplementedError("TODO ex01")


def ex02_class_weights(counts):
    """weight_i = total / (K * count_i), then divided by the mean of the weights (so the mean is 1).
    counts: list or array of K counts. Returns a float numpy array. Theory 6.2
    """
    raise NotImplementedError("TODO ex02")


def ex03_smoothed_target(label, n_classes=7, eps=0.1):
    """The label-smoothing target vector: (1 - eps) on the true class + eps / K on EVERY class.
    (So the true class gets 1 - eps + eps/K.) Sums to 1. Theory 6.7
    """
    raise NotImplementedError("TODO ex03")


# ---------------------------------------------------------------- neurons and CNNs (notebook 02)

def ex04_softmax(logits):
    """Numerically stable softmax of a 1-D array: subtract the max before exp. Theory 4.3
    Must work for logits like [1000, 1001, 1002] (plain exp would overflow).
    """
    raise NotImplementedError("TODO ex04")


def ex05_cross_entropy(logits, label):
    """-log(softmax(logits)[label]), computed stably (log-sum-exp). Theory 4.4"""
    raise NotImplementedError("TODO ex05")


def ex06_conv2d(image, kernel, stride=1, padding=0):
    """2-D convolution (really cross-correlation, like PyTorch) of a 2-D numpy image with a 2-D kernel.

    Pad with zeros, slide the kernel with the given stride, multiply element by element and sum.
    Output size: (n + 2p - k) // s + 1 in each direction. Must equal torch.nn.functional.conv2d. Theory 5.2, 5.7
    """
    raise NotImplementedError("TODO ex06")


def ex07_make_residual_block(c_in, c_out, stride):
    """Return a torch.nn.Module implementing the residual block of theory 5.4:

        conv3x3(c_in->c_out, stride, padding 1, bias=False) -> BN -> ReLU
        -> conv3x3(c_out->c_out, padding 1, bias=False) -> BN
        + shortcut(x)  -> ReLU
    shortcut = identity, or conv1x1(stride, bias=False) + BN when the stride or the channels change.
    Hint: define a class inside this function (or at module level) and return an instance.
    """
    raise NotImplementedError("TODO ex07")


# ---------------------------------------------------------------- training (notebook 03)

def ex08_per_class_f1(y_true, y_pred, n_classes=7):
    """F1 for every class, as a numpy array. 0/0 counts as 0. Theory 6.x (evaluation)"""
    raise NotImplementedError("TODO ex08")


class Ex09EarlyStopping:
    """Watch the validation accuracy after every epoch.

    step(val_acc) -> (is_best, should_stop):
      is_best      True if val_acc is strictly higher than every earlier value (save the checkpoint!)
      should_stop  True once `patience` epochs in a row brought no new best
    Theory 6.4
    """

    def __init__(self, patience=8):
        raise NotImplementedError("TODO ex09")

    def step(self, val_acc):
        raise NotImplementedError("TODO ex09")


def ex10_cosine_lr(epoch, total_epochs, lr_max=1e-3, lr_min=0.0):
    """Cosine annealing: lr_min + (lr_max - lr_min) * (1 + cos(pi * epoch / total_epochs)) / 2
    epoch 0 -> lr_max, epoch total_epochs -> lr_min.  Theory 4.5
    """
    raise NotImplementedError("TODO ex10")


# ---------------------------------------------------------------- detection and real time (notebook 04)

def ex11_rect_sum(image, top, left, bottom, right):
    """Sum of image[top:bottom+1, left:right+1] (INCLUSIVE corners) using an integral image and at most 4 reads.

    Build the integral image with one extra row and column of zeros at the top/left - then no special cases
    are needed at the border. Theory 7.1
    """
    raise NotImplementedError("TODO ex11")


class Ex12TemporalSmoother:
    """Average the PROBABILITY VECTORS of the last `window` frames (not the labels).
    update(probs) -> (label_index, confidence) of the average. Theory 8.4
    """

    def __init__(self, window=5):
        raise NotImplementedError("TODO ex12")

    def update(self, probs):
        raise NotImplementedError("TODO ex12")
