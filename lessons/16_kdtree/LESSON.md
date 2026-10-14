# Lesson 16 — The kd-tree: skipping work, and when skipping stops working

> **For:** Seif (WineGrader stage 5) &nbsp;·&nbsp; **Time:** 60 min
> **Before:** Lesson 15; recursion; Python's `heapq` &nbsp;·&nbsp; **After this:** the "measure and decide" chapter of the book

## 🎯 By the end, the student can

1. Build a kd-tree by hand on paper (widest axis, middle position, leaf size).
2. Run the search with pruning and explain the **gap test** that makes skipping safe.
3. Explain the max-heap trick with negated keys.
4. Explain the **curse of dimensionality** with two pictures, and defend "I built it and then didn't use it".

---

## 1. The problem

Linear search measures the distance to **every** training wine (~4,250). Can we skip wines that obviously cannot be among
the nearest? Like looking for a house: you don't measure the distance to every house in the country — you go to the right
city, then the right street.

## 2. Building: cut the box in half, again and again

![building the tree](figs/kd_build.gif)

1. If ≤ leaf-size points remain (Seif: 16; here 8 to see it), stop → **leaf**.
2. Choose the axis with the **largest spread** (× its weight — a weight-0 feature is never worth cutting).
3. Sort by it, cut at the **middle position**: first half left, second half right; the value there is the threshold.
4. Recurse on each half.

**Why the middle position, not "< median goes left"?** Repeated values: if 300 wines share the same pH, "< median" can
send them all to one side and the recursion never ends. The middle position *always* halves.

## 3. Searching: go near first, then ask "could the far side matter?"

![search with pruning](figs/kd_search.gif)

Keep the **k best so far** (orange rings; dashed circle = the k-th best distance). At each node:

1. go to the **near** side first (where the query is);
2. coming back, compute the **gap** — the distance from the query to the cutting line along that one axis.
   Every point on the far side is *at least* that far away:

$$\text{gap}=w_{axis}\cdot|q_{axis}-\text{threshold}|^{p}$$

3. if `gap > k-th best distance` → **skip the whole far box** (grey) without measuring anything inside it.

Here: **35 of 160** distances computed for k = 5.

```python
search(near)
gap = w[axis] * abs(diff) ** p
if len(heap) < k or gap <= worst_distance_in_heap:   # <= : ties must still be reachable
    search(far)                                      # otherwise: skipped entirely
```

## 4. The heap trick

We need instant access to the **worst** of the k best (to compare with the gap and to replace it). Python's `heapq` is a
**min**-heap → store `(-distance, -row)`: the smallest negated value is the largest distance, so `heap[0]` is the worst
kept wine. (`-row` makes ties come out like the linear search.)

## 5. Correctness first

A tree that prunes one branch too many still returns k wines — just not the nearest — and **nothing else would notice**.
So `test_kdtree_matches_linear` asks both indexes for 1,000 random queries (uniform and mixed weights including zeros,
p = 1 and 2) and demands **identical** answers.

## 6. The curse of dimensionality

![curse of dimensionality](figs/curse.png)

**Left:** with random points, the farthest point is 10,000× farther than the nearest in 1-D, but only 1.5× in 100-D —
"near" and "far" stop meaning much, so the k-th best distance stays big and the gap test rarely wins.

**Right (real wines, k = 20, leaf 16):** with the 2 features most correlated with quality the tree measures **2 %** of the
wines; with all 11 it measures **59 %**. (Seif's guide: 2 % → 54 % with his 12 features; with Python overhead the tree is
then ~10× *slower* than numpy doing everything at once.)

Two reasons, both for the defence:
1. **Too few cuts per axis** — 4,000 points / leaf 16 ≈ 8 levels ≈ 8 cuts in total. In 2-D that's 4 per axis; in 12-D some
   axes are never cut, the boxes are long slabs, and the "far side" is rarely far.
2. **Distances concentrate** (left panel).

That is why `config.DEFAULT_INDEX = "linear"`: **the measurement decided it.**

❓ *"You built a kd-tree and didn't use it — wasted work?"* No: the claim is "here is how to decide whether it helps". It is
implemented, proven correct, measured, and the dimension curve explains the result. For a 4-feature model the same code
wins by a factor of ten.

## 7. Misconceptions

| Student says | Truth |
|---|---|
| "The kd-tree is approximate" | It is **exact** — pruning only skips boxes that provably can't contain a better point. |
| "A tree is always faster than a list" | Not in high dimensions, and not against vectorised numpy. Measure. |
| "Prune with `<`, it's the same" | `<=` keeps ties reachable so results equal the linear search exactly. |

## 8. Activities

1. **Paper tree (15 min).** 16 dots on squared paper. Students build the tree with leaf size 2 using coloured pencils for
   each level.
2. **Search by hand (10 min).** Mark a query; find the 1-NN. Count how many dots you measured. Who measured fewest?
3. **Measure (10 min).** In `32_WineGrader/02_examples/03_kdtree.ipynb`, change the number of features and time both
   indexes.

## 9. Check yourself

<details><summary>1. The query is at x = 3.0; the cut is at x = 2.0; p = 2, weight 1; the current k-th best power distance is 0.8. Search the far side?</summary>

gap = |3 − 2|² = 1.0 > 0.8 → **skip** it.
</details>

<details><summary>2. Why multiply the spread by the feature weight when choosing the axis?</summary>

A feature with weight 0 adds nothing to any distance, so cutting on it could never prune anything. Weighted spread picks
the axis that matters for the distance.
</details>

<details><summary>3. Why does a heap store (−distance, −row) instead of (distance, row)?</summary>

`heapq` is a min-heap; negating makes `heap[0]` the **largest** distance = the worst of the k best, which is what we compare
and replace.
</details>

## 10. In your project

| Project | Where |
|---|---|
| WineGrader | `winegrader/ml/index.py` → `KDTreeIndex.build`, `_build`, `query` (and `LinearIndex` to compare) · `ml/evaluation.py` → `kdtree_dimension_curve` · theory `32_WineGrader/01_theory/05_kdtree.md` · notebook `03_kdtree.ipynb` |

## 🎬 Watch & explore

* *K-d trees explained (construction and nearest-neighbour search)* — [search on YouTube](https://www.youtube.com/results?search_query=kd+tree+nearest+neighbor+search+explained)
* VisuAlgo — [visualising data structures and algorithms (heaps, BSTs)](https://visualgo.net/en)
* scikit-learn — [Nearest neighbours: KD tree and ball tree](https://scikit-learn.org/stable/modules/neighbors.html#kd-tree)
