# Lesson 08 — Documents as arrows: dot product and cosine similarity

> **For:** Kosai (ResumeMatch stage 4) · useful for Laith and Seif (vectors, distances) &nbsp;·&nbsp; **Time:** 45 min
> **Before:** Lesson 07 &nbsp;·&nbsp; **After this:** Lesson 09 (BM25), Lesson 10 (P@k, MRR)

## 🎯 By the end, the student can

1. Draw two documents as arrows and explain similarity as the **angle** between them.
2. Compute a dot product, a vector length and a cosine by hand.
3. Explain why cosine (not distance) is used for text, and why after L2 normalisation **cosine = dot product**.

---

## 1. A document is an arrow

![documents as arrows](figs/arrows.png)

With only two terms (`python`, `sql`) every document is a point / an arrow in 2-D. With 5,000 terms it is an arrow in
5,000-D — we cannot draw it, but the maths is identical.

* CV A = (2, 1) and CV B = (4, 2): B is A "said twice". **Same direction**, same cosine 0.949.
* CV C = (0, 3) only talks about `sql`: a bigger angle, cosine 0.707.

## 2. The formulas

$$a\cdot b=\sum_i a_i b_i\qquad \|a\|=\sqrt{\sum_i a_i^2}\qquad \cos(a,b)=\frac{a\cdot b}{\|a\|\,\|b\|}$$

By hand, job J = (1, 1) and CV A = (2, 1):

```
dot    = 1·2 + 1·1           = 3
|J|    = √(1 + 1)            = 1.414
|A|    = √(4 + 1)            = 2.236
cos    = 3 / (1.414 · 2.236) = 0.949        angle = arccos(0.949) ≈ 18°
```

## 3. Watch the angle

![rotating arrow](figs/rotate.gif)

| cosine | angle | meaning |
|---|---|---|
| 1 | 0° | same proportions of words |
| 0 | 90° | no word in common |
| < 0 | > 90° | impossible with word counts — all values are ≥ 0 |

So for text, cosine is always between 0 and 1 — a nice score to show a recruiter.

## 4. Why not just measure the distance?

![length trap](figs/length_trap.png)

Euclidean distance punishes the CV that is just longer: "same CV × 5" is the *farthest*. Cosine looks only at the
direction, so length stops mattering. This is the same reason as L2 normalisation (Lesson 07).

**The trick that makes Kosai's code simple:** if every row is already divided by its length, then $\|a\|=\|b\|=1$ and

$$\cos(a,b)=a\cdot b$$

Ranking 200 CVs = one matrix × vector product.

## 5. On the real data — and a surprise

![real ranking](figs/real_ranking.png)

Job J1 against all 200 CVs. 8 of the top 10 are CVs a human marked relevant (P@10 = 0.8, Lesson 10). But the **top two
are wrong**: CVs that **pasted the job advert** into their text. Cosine measures *word overlap*, not skill. This is why
Kosai's system has a **reliability check** (`RankExplainer.warning_for`): a CV that matches the advert's sentences but
not its skills gets a warning.

## 6. Algorithm (ResumeMatch's `rank`)

```
fit:   for every CV: counts → tf × idf → divide by the row length   (store the matrix)
rank:  job text → same preprocessing → tf × idf → normalise
       score[i] = dot(row_i, job_vector)        for every CV i
       sort by score, highest first
```

## 7. Misconceptions

| Student says | Truth |
|---|---|
| "Cosine 0.6 means 60 % match" | It is an angle measure, not a percentage of skills. Explain it as "similarity of word use". |
| "A bigger dot product = more similar" | Only after normalising. Without it, long documents win. |
| "Cosine understands synonyms" | `postgres` and `postgresql` are different axes → 0 overlap. |
| "The top result is always right" | See the advert copiers above. |

## 8. Activities

1. **Arrows on the floor (10 min).** Tape two axes on the floor (python / sql). Students stand at their "CV" position;
   a rope from the origin is the job. Who has the smallest angle?
2. **Compute (10 min).** J = (1, 0, 1), A = (2, 0, 2), B = (1, 1, 0), C = (0, 3, 0). Rank by cosine. (A = 1, B = 0.5, C = 0)
3. **Cheat the system (10 min).** In the notebook, paste the job text into a bad CV and watch it jump to rank 1. How
   would you detect this? (→ skills check, reliability warning)

## 9. Check yourself

<details><summary>1. a = (3, 4), b = (4, 3). cos?</summary>

dot = 12 + 12 = 24; |a| = |b| = 5 → cos = 24 / 25 = **0.96**.
</details>

<details><summary>2. Why can cosine never be negative for TF-IDF vectors?</summary>

All components are ≥ 0, so every product in the dot product is ≥ 0.
</details>

<details><summary>3. Two CVs: one has every word of the job once, one has only "python" 50 times. Which has the higher cosine with "python django rest"?</summary>

The first: it points in the same direction as the job. The second points almost only along `python` (angle ≈ 55°,
cos ≈ 0.58). Repetition does not help cosine — which is good.
</details>

## 10. In your project

| Project | Where |
|---|---|
| ResumeMatch | `resumematch/rank/tfidf.py` → `TfidfRanker._l2_normalise_rows`, `_vectorise_job`, `rank`, `explain` · `rank/base.py` → `Ranker._normalise` · `rank/explainer.py` → `RankExplainer.warning_for` · theory `31_ResumeMatch/01_theory/02_cosine.md` · notebook `02_tfidf_cosine.ipynb` |

## 🎬 Watch & explore

* 3Blue1Brown — *Dot products and duality* (Essence of Linear Algebra, ch. 9) — [search on YouTube](https://www.youtube.com/results?search_query=3Blue1Brown+dot+products+and+duality)
* StatQuest — *Cosine Similarity, Clearly Explained* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+cosine+similarity)
* Khan Academy — [Vectors](https://www.khanacademy.org/math/linear-algebra/vectors-and-spaces)
