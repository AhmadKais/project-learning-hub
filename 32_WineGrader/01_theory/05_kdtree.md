# Chapter 5 — The kd-tree, and the curse of dimensionality

💡 **In short:** a kd-tree cuts the space in half again and again, so a search can skip whole halves that cannot contain a closer wine. It is exact and, in 2–4 dimensions, it skips almost everything. In 12 dimensions it skips almost nothing — and in Python it is then slower than plain numpy. You will build it, prove it correct, measure it, and explain why it lost. That is a result, not a failure.

## 5.1 The problem

Linear search computes the distance from the new wine to all ~4,000 training wines. For one wine at the lab station that is under a millisecond with numpy — fine. But it grows with the data, and the question "can we avoid looking at every wine?" is one of the classic questions of computer science.

## 5.2 Building the tree

1. If 16 or fewer points are left, stop: this is a **leaf**.
2. Otherwise choose the feature with the largest spread (max − min, times its weight).
3. Sort the points by that feature and cut at the **middle position**: the first half goes left, the second half right. The value at the cut is the node's **threshold**.
4. Repeat on each half.

Every left point has a value ≤ threshold on that axis, every right point ≥ threshold.

❓ **Why cut at the middle position instead of "less than the median goes left"?**

Because of repeated values. If 300 wines share the same pH, "less than the median" can send every one of them to the same side; the split does nothing and the recursion never ends. Cutting at the middle position always halves the points. The price is that a value equal to the threshold can be on either side — and the search below is written so that this does not matter.

Why multiply the spread by the weight? A feature with weight 0 adds nothing to any distance, so splitting on it could never prune anything.

## 5.3 Searching

Keep the k best wines found so far. Start at the root:

1. At a leaf: compute the distance to every point in it and update the k best.
2. At a node: go first to the side the query wine is on (the **near** side).
3. Coming back, ask: **could anything on the far side be closer than my current k-th best?**

Every point on the far side is at least `|query[axis] − threshold|` away *along this one axis*. Its full power distance is therefore at least

    gap = w[axis] · |query[axis] − threshold|ᵖ

whatever the other axes contribute (they only add). If `gap` is already larger than the k-th best distance found so far, nothing on the far side can get in, and the **whole far subtree is skipped** without computing a single distance. That is pruning, and it is where all the saving comes from.

📄 **The pruning step**
```python
search(near)
gap = w[axis] * abs(diff) ** p
if len(heap) < k or gap <= worst_distance_in_heap:
    search(far)          # otherwise: skipped entirely
```

Why `<=` and not `<`? A far point at exactly the k-th distance with a smaller row number must still be reachable, or ties would come out differently from the linear search. The equivalence test checks this.

## 5.4 The heap

The k best are kept in a heap. Python's `heapq` is a *min*-heap, but we need instant access to the *worst* of the k best (to compare with `gap` and to replace it). The trick: store negated keys, `(-distance, -row)`. The smallest negated key is the largest distance — so `heap[0]` is always the worst kept wine.

## 5.5 Correctness first

A kd-tree that prunes one branch too many still returns k wines — just not the nearest ones — and nothing else in the program would ever notice. So `test_kdtree_matches_linear` asks both indexes for the neighbours of **1,000 random queries**, with uniform and with mixed weights (including zeros), for p = 1 and p = 2, and demands identical answers. It is the blocking test of stage 5.

## 5.6 The measurement

Your evaluation report measures the tree on the real data. With the tuned model (k ≈ 20, 12 features):

| Index | Distances computed per wine | Time per wine |
|---|---|---|
| linear | ~4,250 (all) | ~0.8 ms |
| kd-tree | ~4,200 (99%) | ~9 ms |

The tree computes almost every distance anyway, and the Python overhead of walking it makes it ten times slower than numpy doing all the work in one vectorised step.

Then the experiment that explains it — keep only the d features most correlated with quality and measure what share of the wines the tree looks at:

| Features | Share measured |
|---|---|
| 2 | ~2% |
| 4 | ~9% |
| 6 | ~18% |
| 8 | ~26% |
| 12 | ~54% |

## 5.7 The curse of dimensionality

Why does the tree fall apart as dimensions grow? Two reasons, both worth being able to explain:

1. **Too few cuts per axis.** 4,000 points with leaves of 16 gives a tree about 8 levels deep — 8 cuts in total. In 2 dimensions that is 4 cuts per axis, a fine grid. In 12 dimensions some axes are never cut at all, so the cells are long thin slabs and the "far side" is rarely far.
2. **Distances concentrate.** In many dimensions, the nearest and the farthest points are not that different in distance. The k-th best distance stays large, so `gap` is rarely bigger than it, and pruning rarely happens.

The 2-to-12 table above is this effect, measured on your own data. That is why `config.DEFAULT_INDEX` is `"linear"`: the measurement decided it.

❓ **You built a kd-tree and then did not use it. Was that wasted work?**

No. The project's claim is not "a kd-tree makes this fast" but "here is how to decide whether it does". The tree is implemented, proven correct against the reference, and measured; the measurement showed it does not pay in 12 dimensions with Python's overhead, and the dimension curve shows why. A decision taken from a measurement is worth more than one taken from a textbook — and for a 4-feature model the same code would win by a factor of ten.

❓ **What would you try for a much larger dataset?**

Approximate methods that give up exactness for speed — locality-sensitive hashing, or a Ball tree, which copes better with higher dimensions than a kd-tree. Or reduce the dimensions first, since the curve shows how much the tree gains with fewer features.
