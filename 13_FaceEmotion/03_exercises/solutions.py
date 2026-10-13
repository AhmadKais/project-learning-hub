"""FaceEmotion - solutions to exercises.py.

Try first. Then compare: there is more than one correct way to write each one.
To run the tests against these solutions:  EXERCISES=solutions pytest test_exercises.py
"""
import math
from collections import deque

import numpy as np

MEAN, STD = 0.5077, 0.2550


def ex01_normalize(img):
    return ((img.astype(np.float32) / 255.0) - MEAN) / STD


def ex02_class_weights(counts):
    counts = np.asarray(counts, dtype=float)
    w = counts.sum() / (len(counts) * counts)
    return w / w.mean()


def ex03_smoothed_target(label, n_classes=7, eps=0.1):
    target = np.full(n_classes, eps / n_classes)
    target[label] += 1 - eps
    return target


def ex04_softmax(logits):
    z = np.asarray(logits, dtype=float)
    e = np.exp(z - z.max())
    return e / e.sum()


def ex05_cross_entropy(logits, label):
    z = np.asarray(logits, dtype=float)
    m = z.max()
    log_sum_exp = m + np.log(np.exp(z - m).sum())
    return float(log_sum_exp - z[label])


def ex06_conv2d(image, kernel, stride=1, padding=0):
    img = np.pad(np.asarray(image, dtype=float), padding)
    k = np.asarray(kernel, dtype=float)
    kh, kw = k.shape
    oh = (img.shape[0] - kh) // stride + 1
    ow = (img.shape[1] - kw) // stride + 1
    out = np.zeros((oh, ow))
    for i in range(oh):
        for j in range(ow):
            r, c = i * stride, j * stride
            out[i, j] = (img[r:r + kh, c:c + kw] * k).sum()
    return out


def ex07_make_residual_block(c_in, c_out, stride):
    import torch.nn as nn
    import torch.nn.functional as F

    class ResidualBlock(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv1 = nn.Conv2d(c_in, c_out, 3, stride, 1, bias=False)
            self.bn1 = nn.BatchNorm2d(c_out)
            self.conv2 = nn.Conv2d(c_out, c_out, 3, 1, 1, bias=False)
            self.bn2 = nn.BatchNorm2d(c_out)
            self.shortcut = nn.Identity()
            if stride != 1 or c_in != c_out:
                self.shortcut = nn.Sequential(nn.Conv2d(c_in, c_out, 1, stride, bias=False), nn.BatchNorm2d(c_out))

        def forward(self, x):
            out = F.relu(self.bn1(self.conv1(x)))
            out = self.bn2(self.conv2(out))
            return F.relu(out + self.shortcut(x))

    return ResidualBlock()


def ex08_per_class_f1(y_true, y_pred, n_classes=7):
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    f1 = np.zeros(n_classes)
    for c in range(n_classes):
        tp = np.sum((y_true == c) & (y_pred == c))
        pred_c, true_c = np.sum(y_pred == c), np.sum(y_true == c)
        p = tp / pred_c if pred_c else 0.0
        r = tp / true_c if true_c else 0.0
        f1[c] = 2 * p * r / (p + r) if p + r else 0.0
    return f1


class Ex09EarlyStopping:
    def __init__(self, patience=8):
        self.patience = patience
        self.best = -math.inf
        self.bad_epochs = 0

    def step(self, val_acc):
        if val_acc > self.best:
            self.best, self.bad_epochs = val_acc, 0
            return True, False
        self.bad_epochs += 1
        return False, self.bad_epochs >= self.patience


def ex10_cosine_lr(epoch, total_epochs, lr_max=1e-3, lr_min=0.0):
    return lr_min + (lr_max - lr_min) * (1 + math.cos(math.pi * epoch / total_epochs)) / 2


def ex11_rect_sum(image, top, left, bottom, right):
    I = np.zeros((image.shape[0] + 1, image.shape[1] + 1), dtype=np.int64)
    I[1:, 1:] = np.asarray(image, dtype=np.int64).cumsum(0).cumsum(1)
    return int(I[bottom + 1, right + 1] - I[top, right + 1] - I[bottom + 1, left] + I[top, left])


class Ex12TemporalSmoother:
    def __init__(self, window=5):
        self._window = deque(maxlen=window)

    def update(self, probs):
        self._window.append(np.asarray(probs, dtype=float))
        avg = np.mean(self._window, axis=0)
        return int(avg.argmax()), float(avg.max())
