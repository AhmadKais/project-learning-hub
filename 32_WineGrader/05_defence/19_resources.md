# Chapter 19 — Where to read more

💡 **In short:** the dataset paper, the two classic k-NN papers, the kd-tree papers, and two chapters of one textbook.

## 19.1 The papers that matter

**Cortez, Cerdeira, Almeida, Matos & Reis (2009) — Modeling Wine Preferences by Data Mining from Physicochemical Properties.** *Decision Support Systems 47(4).*
Where your dataset comes from. Read the description of how the wines were scored and which features they found most important — then compare with your correlation table.

**Cover & Hart (1967) — Nearest Neighbor Pattern Classification.** *IEEE Transactions on Information Theory.*
The "at most twice the best possible error" result. You do not need the proof; you should be able to state the result.

**Bentley (1975) — Multidimensional Binary Search Trees Used for Associative Searching.** *Communications of the ACM.*
The kd-tree. Short and readable.

**Friedman, Bentley & Finkel (1977) — An Algorithm for Finding Best Matches in Logarithmic Expected Time.**
The nearest-neighbour search with pruning that you implemented.

**Wettschereck, Aha & Mohri (1997) — A Review and Empirical Evaluation of Feature Weighting Methods for a Class of Lazy Learning Algorithms.**
Feature weighting for k-NN, and when it helps. Useful for explaining why it did not help much on your data.

**Varma & Simon (2006) — Bias in Error Estimation When Using Cross-Validation for Model Selection.**
The paper to cite for nested cross-validation.

## 19.2 Textbook

**Hastie, Tibshirani & Friedman — The Elements of Statistical Learning**, sections 13.3 (k-NN) and 7.10 (cross-validation, including "the wrong and the right way to do cross-validation"). Free online from the authors. Section 7.10.2 is exactly the leakage argument of chapter 7.

## 19.3 The data

| Source | Notes |
|---|---|
| https://archive.ics.uci.edu/dataset/186/wine+quality | the official page, licence CC BY 4.0 |
| `data/sample/` | 120 real wines, for running the code before downloading |

## 19.4 Documentation you will actually open

- numpy: indexing, broadcasting, `argsort`, `argpartition` — numpy.org/doc
- Python: `heapq`, `csv`, `sqlite3`, `dataclasses` — docs.python.org
- matplotlib: the `Figure` object interface and `FigureCanvasTkAgg`
- pytest: `-k`, `-v`, fixtures — docs.pytest.org
