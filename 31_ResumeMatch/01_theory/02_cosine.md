# Step 2 — Measuring similarity with an angle

## Documents as arrows

If a document is a row of numbers, it is a **point in space**. With 3 words it
is a point in 3D. With 20,000 words it is a point in 20,000 dimensions — which
you cannot picture, but the maths does not care.

Now: how similar are two documents? Two options:

- **Distance** between the points — bad idea, see below.
- **Angle** between the arrows from the origin — this is what we use.

## Why the angle, not the distance

Take a CV and paste it twice. Every count doubles. The arrow gets twice as long
but points in **exactly the same direction**.

```
  short CV  ->  (2, 1)
  same CV x2 -> (4, 2)        same direction, double the length
```

Distance says they are far apart. Angle says they are identical — which is the
right answer, because they say the same thing.

**This is how cosine similarity handles document length for free.** No parameter,
no tuning. It falls out of the geometry.

## The formula

```
                 A · B
cos(A, B) = ---------------
              ||A|| × ||B||

    A · B    = a1*b1 + a2*b2 + ... (the dot product)
    ||A||    = sqrt(a1² + a2² + ...) (Pythagoras, in n dimensions)
```

The result is between 0 and 1 when all weights are non-negative (ours are):

- **1.0** — same direction, same relative mix of words
- **0.0** — no word in common at all

## The trick that makes it fast

If we divide every row by its own length **in advance**, then every row has
length exactly 1. And if `||A|| = ||B|| = 1`, the formula collapses:

```
cos(A, B) = (A · B) / (1 × 1) = A · B
```

Just a dot product. No square roots at ranking time.

📄 **L2 normalisation — do this once, when building the matrix**

```python
norms = np.sqrt(m.multiply(m).sum(axis=1)).A.ravel()
norms[norms == 0] = 1.0            # an empty doc must not divide by zero
matrix = sparse.diags(1.0 / norms) @ m
```

Now ranking the **entire collection** is one line:

```python
scores = self.matrix @ q           # (n_docs × vocab) @ (vocab,) -> (n_docs,)
```

That single matrix-vector product is why search engines feel instant.

## Putting the job in the same space

The job description must become a vector **in the same space, with the same
IDF values**:

```python
q = np.zeros(len(vocabulary))
for term in job_terms:
    if term in vocabulary:
        q[vocabulary[term]] += 1
q = q * self.idf                   # the COLLECTION's idf
q = q / np.linalg.norm(q)
```

❓ **Why not compute the IDF from the job description itself?**

Because IDF means "how rare is this across the collection", and one document is
not a collection — every term would have `df = 1`. Worse, the job would live in
a *different* space from the CVs and the dot product would be meaningless.

Expect this question. It separates people who understand the vector space model
from people who copied it.

## Sparse matrices — why you must

500 CVs, 20,000 distinct terms. A full matrix:

```
500 × 20,000 × 8 bytes = 80 MB       ... of which 98.5% are zeros
```

A typical CV has ~300 distinct terms out of 20,000. So store only what exists:

```
500 × 300 × 12 bytes = 1.8 MB        ~44× smaller
```

With 5,000 CVs the dense version is 800 MB and simply does not fit. Sparse is
not an optimisation you add later — it is the only way this works at all.
