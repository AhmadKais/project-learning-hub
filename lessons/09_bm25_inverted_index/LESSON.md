# Lesson 09 — BM25 and the inverted index: how search engines rank

> **For:** Kosai (ResumeMatch stage 5 — the comparison that *is* his project) &nbsp;·&nbsp; **Time:** 60 min
> **Before:** Lessons 07, 08 &nbsp;·&nbsp; **After this:** Lesson 10 (measuring the ranking)

## 🎯 By the end, the student can

1. Name the two things TF-IDF gets wrong (repetition, length) and show how BM25 fixes each, with the picture.
2. Explain what `k1` and `b` do, and predict what `b = 0` will do to the ranking.
3. Compute one BM25 term score by hand, with the **BM25 IDF** (not the TF-IDF one).
4. Explain the inverted index and why it makes search fast.

---

## 1. The formula, piece by piece

$$\text{score}(d,q)=\sum_{t\in q}\ \text{idf}_{bm25}(t)\cdot\frac{tf\,(k_1+1)}{tf+k_1\left(1-b+b\,\frac{|d|}{avgdl}\right)}$$

Do **not** start with the whole formula. Build it from two problems.

## 2. Problem 1 — repetition counts too much → saturation

![saturation](figs/saturation.gif)

In TF-IDF "python" ×20 counts 10× more than "python" ×2. BM25's factor $\frac{tf(k_1+1)}{tf+k_1}$ climbs fast and
then flattens at the ceiling $k_1+1$. With the project's $k_1 = 1.5$:

| tf | 1 | 2 | 5 | 20 | ∞ |
|---|---|---|---|---|---|
| factor | 1.00 | 1.43 | 1.92 | 2.33 | 2.50 |

The animation sweeps $k_1$: small $k_1$ → "mentioned at all" is all that matters; large $k_1$ → almost linear like TF-IDF.
(The project's data has "keyword stuffers" who repeat one skill 15 times — saturation stops them.)

## 3. Problem 2 — length → the `b` knob

![length normalisation](figs/length_b.png)

$|d|/avgdl$ = "how long is this CV compared to an average CV". A long CV mentions many things just by being long, so
the same tf is worth less. `b` says how strongly to correct: **0 = ignore length, 1 = full, 0.75 = standard**.

### The experiment on the project's data

![b experiment](figs/b_experiment.png)

With `b = 0` the top-10 CVs are on average **136 terms** long (average CV: 100). With `b = 0.75` they are 79. On this
data P@10 barely changes (0.86–0.88) — the human labels are by role, and long CVs of the right role are still relevant.
**That is a result too.** Kosai reports both charts and explains them; he does not hide the flat one.

## 4. BM25 has its own IDF

![BM25 idf](figs/bm25_idf.png)

$$\text{idf}_{bm25}(t)=\ln\left(\frac{N-df+0.5}{df+0.5}+1\right)$$

Without the `+1` inside the log, a word in more than half of the CVs gets a **negative** IDF and *lowers* the score of
everyone who mentions it. Using the TF-IDF formula here instead is a **silent** bug — nothing crashes, the ranking is just
worse.

## 5. One term by hand

N = 200, df(python) = 60, avgdl = 100. CV with tf = 2, |d| = 150. $k_1 = 1.5$, $b = 0.75$.

```
idf   = ln((200 − 60 + 0.5) / (60 + 0.5) + 1) = ln(2.322 + 1) = ln(3.322) = 1.2006
norm  = 1 − 0.75 + 0.75 × 150/100           = 0.25 + 1.125  = 1.375
part  = 2 × 2.5 / (2 + 1.5 × 1.375)         = 5 / 4.0625    = 1.2308
score = 1.2006 × 1.2308                                        = 1.4777
```

Same CV but average length (|d| = 100): norm = 1, part = 5 / 3.5 = 1.4286, score = 1.7151 — more, because it is shorter.

## 6. The inverted index

![inverted index](figs/inverted_index.gif)

Instead of a matrix with a row per CV, keep **for every term the list of CVs that contain it** (with tf) — like the
index at the back of a book. To rank a job, walk only the lists of the job's terms. A CV that shares no word with the job
is **never touched**: its score is 0 without looking at it.

![final state](figs/inverted_index_final.png)

```python
for term in set(job_terms):
    if term not in self.inverted:
        continue
    for doc_row, tf in self.inverted[term]:
        scores[doc_row] += self._term_score(tf, self.doc_len[doc_row], idf[term])
```

This is how Google ranks billions of pages in milliseconds. **Put "documents touched / total" in the book** — direct
evidence that the index works.

## 7. Comparing BM25 with cosine fairly

Cosine is in [0, 1]; BM25 is unbounded (3.7 or 41.2 depending on the job). Normalise by the top score of the ranking
(`Ranker._normalise`) — this makes scores comparable **within one ranking only**. To compare the methods, compare **rank
positions** and P@k / MRR (Lesson 10), not raw numbers.

## 8. Misconceptions

| Student says | Truth |
|---|---|
| "BM25 uses the same IDF as TF-IDF" | No — see §4. Separate function: `compute_idf_bm25`. |
| "b = 0.75 is magic" | It's a widely used default from the literature. The project measures it instead of trusting it. |
| "The index changes the scores" | It changes only *which documents are looked at*. Same scores as checking every CV. |
| "A BM25 score of 12 is better than 8 in another job" | Scores across jobs are not comparable. |

## 9. Activities

1. **Book index (5 min).** Open any textbook's index. Find "loop" — how many pages did you *not* read? That's the inverted index.
2. **Human BM25 (15 min).** Cards with 5 tiny CVs. Groups build the inverted index on paper, then score the job
   "python sql" with tf saturation only (no idf). Then add `b`.
3. **Live sliders.** `python visualize.py --live` — change `k1`, see the ceiling move.
4. **Predict-then-run.** Before running Kosai's `b = 0` experiment: "Will long CVs go up or down?"

## 10. Check yourself

<details><summary>1. With k1 = 1.5, what is the most one term can contribute (ignoring idf and length)?</summary>

k1 + 1 = **2.5**, reached only as tf → ∞.
</details>

<details><summary>2. b = 0. Does the CV's length still matter at all?</summary>

No: the bracket becomes $1 - 0 + 0 = 1$, so $|d|$ disappears from the formula.
</details>

<details><summary>3. N = 200, df = 150. Compute idf with and without the +1.</summary>

Without: ln(50.5/150.5) = ln(0.3355) = **−1.09** (negative!). With: ln(0.3355 + 1) = ln(1.3355) = **0.289**.
</details>

## 11. In your project

| Project | Where |
|---|---|
| ResumeMatch | `resumematch/nlp/vocabulary.py` → `compute_idf_bm25` · `resumematch/rank/bm25.py` → `Bm25Ranker.fit` (inverted index, `doc_len`, `avgdl`), `rank`, `_term_score` · config `BM25_K1 = 1.5`, `BM25_B = 0.75` · theory `31_ResumeMatch/01_theory/03_bm25.md` · notebook `03_bm25.ipynb` |

## 🎬 Watch & explore

* *BM25 explained* — [search on YouTube](https://www.youtube.com/results?search_query=BM25+ranking+function+explained)
* Stanford IR book (Manning et al.), §11.4.3 — [Okapi BM25](https://nlp.stanford.edu/IR-book/html/htmledition/okapi-bm25-a-non-binary-model-1.html)
* Stanford IR book, ch. 1 — [An example information retrieval problem (the inverted index)](https://nlp.stanford.edu/IR-book/html/htmledition/an-example-information-retrieval-problem-1.html)
