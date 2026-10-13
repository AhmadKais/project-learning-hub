"""Automatic checks for exercises.py.   Run:  pytest test_exercises.py -v

Every test is named after its exercise, so  pytest -k ex06  runs just that one.
"""
import importlib
import math
import os

import numpy as np
import pytest

ex = importlib.import_module(os.environ.get("EXERCISES", "exercises"))
rng = np.random.default_rng(13)
COUNTS = [3995, 436, 4097, 7215, 4965, 4830, 3171]          # FER-2013 train: angry..surprise (alphabetical)


def test_ex01_normalize():
    img = np.array([[0, 255], [130, 65]], dtype=np.uint8)
    out = ex.ex01_normalize(img)
    assert out.dtype == np.float32 and out.shape == (2, 2)
    assert out[0, 0] == pytest.approx(-0.5077 / 0.2550, abs=1e-5)
    assert out[0, 1] == pytest.approx((1 - 0.5077) / 0.2550, abs=1e-5)


def test_ex02_class_weights():
    w = ex.ex02_class_weights(COUNTS)
    assert w.mean() == pytest.approx(1.0)
    assert np.argmax(w) == 1 and np.argmin(w) == 3                 # disgust highest, happy lowest
    assert w[1] / w[3] == pytest.approx(7215 / 436)


def test_ex03_smoothed_target():
    t = ex.ex03_smoothed_target(3, 7, 0.1)
    assert t.sum() == pytest.approx(1.0)
    assert t[3] == pytest.approx(0.9 + 0.1 / 7)
    assert t[0] == pytest.approx(0.1 / 7)
    assert np.allclose(ex.ex03_smoothed_target(2, 7, 0.0), np.eye(7)[2])


def test_ex04_softmax():
    assert np.allclose(ex.ex04_softmax([2.0, 0.5, -1.0]), [0.786, 0.175, 0.039], atol=1e-3)
    big = ex.ex04_softmax([1000.0, 1001.0, 1002.0])
    assert np.all(np.isfinite(big)) and big.sum() == pytest.approx(1.0)
    assert np.allclose(big, ex.ex04_softmax([0.0, 1.0, 2.0]))


def test_ex05_cross_entropy():
    assert ex.ex05_cross_entropy([0.0, 0.0], 0) == pytest.approx(math.log(2))
    logits = [2.0, 0.5, -1.0]
    assert ex.ex05_cross_entropy(logits, 0) == pytest.approx(-math.log(ex.ex04_softmax(logits)[0]))
    assert math.isfinite(ex.ex05_cross_entropy([1000.0, -1000.0], 1))
    torch = pytest.importorskip("torch")
    z = rng.normal(size=7)
    ref = torch.nn.functional.cross_entropy(torch.tensor(z)[None], torch.tensor([4])).item()
    assert ex.ex05_cross_entropy(z, 4) == pytest.approx(ref)


def test_ex06_conv2d_theory_example():
    window = [[10, 10, 200], [10, 10, 200], [10, 10, 200]]
    kernel = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
    assert ex.ex06_conv2d(window, kernel).tolist() == [[570.0]]


@pytest.mark.parametrize("n,stride,padding", [(8, 1, 0), (8, 1, 1), (9, 2, 1), (12, 2, 0), (48, 2, 1)])
def test_ex06_conv2d_matches_torch(n, stride, padding):
    torch = pytest.importorskip("torch")
    img, k = rng.normal(size=(n, n)), rng.normal(size=(3, 3))
    ref = torch.nn.functional.conv2d(torch.tensor(img)[None, None], torch.tensor(k)[None, None],
                                     stride=stride, padding=padding)[0, 0].numpy()
    got = ex.ex06_conv2d(img, k, stride, padding)
    assert got.shape == ref.shape
    assert np.allclose(got, ref)


def test_ex07_residual_block_shapes_and_parameters():
    torch = pytest.importorskip("torch")
    same = ex.ex07_make_residual_block(64, 64, 1)
    down = ex.ex07_make_residual_block(64, 128, 2)
    x = torch.randn(2, 64, 48, 48)
    assert tuple(same(x).shape) == (2, 64, 48, 48)
    assert tuple(down(x).shape) == (2, 128, 24, 24)                 # halves with stride two
    count = lambda m: sum(p.numel() for p in m.parameters())
    assert count(same) == 73_984                                    # theory 5.6, block1
    assert count(down) == 230_144                                   # theory 5.6, block2
    assert (same(x) >= 0).all()                                     # ReLU after the addition


def test_ex08_per_class_f1():
    metrics = pytest.importorskip("sklearn.metrics")
    a, b = rng.integers(0, 7, 300), rng.integers(0, 7, 300)
    assert np.allclose(ex.ex08_per_class_f1(a, b), metrics.f1_score(a, b, average=None, labels=range(7), zero_division=0))
    f1 = ex.ex08_per_class_f1([0, 0, 1], [0, 0, 0], 3)
    assert f1[2] == 0.0 and not np.isnan(f1).any()


def test_ex09_early_stopping():
    es = ex.Ex09EarlyStopping(patience=3)
    assert es.step(0.40) == (True, False)
    assert es.step(0.45) == (True, False)
    assert es.step(0.45) == (False, False)          # equal is not better
    assert es.step(0.44) == (False, False)
    assert es.step(0.46) == (True, False)           # a new best resets the count
    assert es.step(0.40) == (False, False)
    assert es.step(0.40) == (False, False)
    assert es.step(0.40) == (False, True)           # 3 epochs without a new best


def test_ex10_cosine_lr():
    assert ex.ex10_cosine_lr(0, 50) == pytest.approx(1e-3)
    assert ex.ex10_cosine_lr(25, 50) == pytest.approx(5e-4)
    assert ex.ex10_cosine_lr(50, 50) == pytest.approx(0.0)
    lrs = [ex.ex10_cosine_lr(e, 50) for e in range(51)]
    assert all(a >= b for a, b in zip(lrs, lrs[1:]))


def test_ex11_rect_sum():
    img = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    assert ex.ex11_rect_sum(img, 1, 1, 2, 2) == 28                  # theory 7.1
    assert ex.ex11_rect_sum(img, 0, 0, 2, 2) == 45
    assert ex.ex11_rect_sum(img, 0, 0, 0, 0) == 1
    big = rng.integers(0, 256, (50, 60))
    for _ in range(50):
        t, b = sorted(rng.integers(0, 50, 2)); l, r = sorted(rng.integers(0, 60, 2))
        assert ex.ex11_rect_sum(big, t, l, b, r) == big[t:b + 1, l:r + 1].sum()


def test_ex12_smoother_averages_vectors():
    sm = ex.Ex12TemporalSmoother(window=3)
    assert sm.update([0.0, 0.51, 0.49]) == (1, pytest.approx(0.51))
    label, conf = sm.update([0.0, 0.49, 0.51])
    assert label == 1 and conf == pytest.approx(0.50)              # (0.51 + 0.49) / 2 for class 1, tie -> first
    sm.update([0.0, 0.2, 0.8]); sm.update([0.0, 0.2, 0.8])
    assert sm.update([0.0, 0.2, 0.8]) == (2, pytest.approx(0.8))  # only the last 3 frames count
