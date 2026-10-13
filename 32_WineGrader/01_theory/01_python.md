# Chapter 1 — The Python and numpy you need

💡 **In short:** arrays, shapes, slicing with masks, broadcasting, `argsort`, and dataclasses. Type every example into a Python shell — reading numpy is not the same as using it.

## 1.1 An array is a table of numbers

The whole dataset is one numpy array: one row per wine, one column per feature.

📄 **Shapes**
```python
import numpy as np

X = np.array([[7.4, 0.70, 9.4],
              [7.8, 0.88, 9.8],
              [11.2, 0.28, 9.8]])

X.shape          # (3, 3)   - 3 wines, 3 features
X[0]             # the first wine: array([7.4, 0.7, 9.4])
X[:, 2]          # the third column (alcohol) of every wine
X[1, 2]          # one number: 9.8
X.mean(axis=0)   # the mean of each COLUMN  -> 3 numbers
X.mean(axis=1)   # the mean of each ROW     -> 3 numbers
```

`axis=0` means "go down the rows" — so you get one answer per column. You will write `X.mean(axis=0)` and `X.std(axis=0)` in the scaler. Get the axis wrong and the tests catch it at once.

## 1.2 Masks — selecting rows by a condition

📄 **Boolean masks**
```python
y = np.array([0, 1, 1, 2, 1])

y == 1                   # array([False, True, True, False, True])
X[y == 1]                # only the rows of class 1
np.flatnonzero(y == 1)   # their row numbers: array([1, 2, 4])
np.sum(y == 1)           # how many: 3  (True counts as 1)
```

`X[y == c].mean(axis=0)` is the centroid of class `c` — that one line is most of `CentroidClassifier.fit`.

## 1.3 Broadcasting — the loop you do not write

When numpy combines arrays of different shapes, it stretches the smaller one to fit.

📄 **Distance from one wine to all wines, in one line**
```python
v = np.array([7.0, 0.5, 10.0])        # shape (3,)
X - v                                 # shape (3, 3): v subtracted from EVERY row
np.abs(X - v).sum(axis=1)             # Manhattan distance to every wine: 3 numbers
```

This is `power_to_many` in `metrics.py`. Write it as a `for` loop first so you understand it, then replace it with this — it is roughly a hundred times faster, and that speed is what makes the evaluation in chapter 7 take seconds instead of hours.

❓ **What is the shape of `Q[:, j, None] - X[None, :, j]` if Q is (100, 12) and X is (4000, 12)?**

(100, 4000). `Q[:, j, None]` is a column of 100 numbers, `X[None, :, j]` is a row of 4,000, and broadcasting builds every difference between them. That is one feature's contribution to the full distance matrix in `power_matrix`.

## 1.4 Sorting by position — argsort

📄 **argsort gives the ORDER, not the values**
```python
d = np.array([3.2, 0.5, 9.1, 0.5])
np.sort(d)                       # array([0.5, 0.5, 3.2, 9.1])
np.argsort(d, kind="stable")     # array([1, 3, 0, 2])  - row numbers, nearest first
np.argsort(d)[:2]                # the 2 nearest rows
```

k-NN needs the row numbers of the nearest wines, not just their distances, so `argsort` is the function you want. `kind="stable"` keeps equal values in their original order — the two 0.5s come out as 1 then 3. That is the tie rule the tests expect.

`np.argpartition(d, k-1)[:k]` finds the k smallest *without sorting the rest*. With 4,000 wines and k = 23, that saves most of the work. You will use it in `query_batch`.

## 1.5 Random numbers you can repeat

📄 **A seeded generator**
```python
rng = np.random.default_rng(42)
rows = np.arange(10)
rng.shuffle(rows)          # same shuffle every time with seed 42
```

Every random choice in the project — the folds above all — uses a seeded generator. Two models compared on different random folds are not compared fairly.

## 1.6 Dataclasses

📄 **A frozen dataclass**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Neighbour:
    index: int
    label: int
    distance: float

n = Neighbour(118, 2, 0.41)
n.distance          # 0.41
n.distance = 1.0    # error - frozen: a fact about the past cannot be edited
```

`entities.py` is all dataclasses, already written. Read it before stage 4: `Prediction`, `Neighbour`, `FoldResult` and `Params` travel between every layer of the project.

## 1.7 Reading a CSV by hand

📄 **The csv module with a semicolon**
```python
import csv

with open(path, newline="", encoding="utf-8") as fh:
    reader = csv.reader(fh, delimiter=";")
    header = next(reader)                 # the first line
    for line_no, row in enumerate(reader, start=2):
        numbers = [float(x) for x in row]
```

`enumerate(..., start=2)` gives you the real line number in the file (the header is line 1), so an error message can say "line 832" and someone can find it.

❓ **Why not pandas?**

Because the project needs to read one simple format and check every value, and the csv module does that in ten lines you can explain completely. pandas would be one more dependency doing work the loader has to re-check anyway.
