# Lesson 10 — Is the ranking good? Precision@k and MRR

> **For:** Kosai (ResumeMatch stage 6) &nbsp;·&nbsp; **Time:** 30 – 45 min
> **Before:** Lessons 03, 08, 09 &nbsp;·&nbsp; **After this:** the experiments chapter of the book

## 🎯 By the end, the student can

1. Explain why a ranking needs different metrics from a classifier.
2. Compute P@k and reciprocal rank by hand, and MRR over several jobs.
3. Read a ranking that is good by one metric and bad by the other, and say what it means.

---

## 1. Ranking is not classification

A recruiter reads the **top ten** and stops. Position 47 is worth nothing. So the metrics only look at the head of the
list: **how many of the first k are right** (P@k) and **how high is the first right one** (RR).

## 2. Precision@k — walk down the list

![P@k walking down a ranking](figs/pk_walk.gif)

$$P@k=\frac{\#\text{relevant among the first }k}{k}$$

⚠️ Divide by **k**, even if the list is shorter than k (missing places count as misses) —
`test_precision_denominator_is_k_not_list_length`.

## 3. Reciprocal rank and MRR

$$RR=\frac{1}{\text{position of the first relevant}}\qquad(0\text{ if none})\qquad\qquad MRR=\text{average of RR over all jobs}$$

| first relevant at | 1 | 2 | 3 | 10 | never |
|---|---|---|---|---|---|
| RR | 1.0 | 0.5 | 0.33 | 0.1 | 0 |

The worked example from Kosai's tests (do it on the board): ranking `[C3, C7, C1, C9]`, relevant `{C1, C7}` →
P@2 = 1/2 = **0.50**, P@4 = 2/4 = **0.50**, RR = 1/2 = **0.50**.

## 4. Why report both

![P@5 vs RR](figs/p_vs_rr.png)

* Ranking A: four good candidates in the top 5, but not the first → high P@5, RR 0.5.
* Ranking B: the best one first, then nothing → P@5 0.2, RR 1.0.

**P@k ignores order inside the top k. MRR ignores everything after the first hit.** Neither alone is enough.

## 5. On the project's data

![TF-IDF vs BM25](figs/compare.png)

Simple versions of both methods on the 200 CVs: P@5 = 0.80 for both, P@10 = 0.90 (TF-IDF) vs 0.88 (BM25), MRR 0.57 for
both. Why is MRR so low when P@10 is so high? Because an **advert copier** (Lesson 08) takes position 1 in four of the five
jobs — a precise, explainable finding for the book, and the reason for the reliability check.

## 6. The golden rule of labelling

The "relevant" lists must be made **before** looking at the system's rankings, by a human, from the CV text. Labelling
after seeing the ranking makes the system's mistakes look correct.

## 7. Misconceptions

| Student says | Truth |
|---|---|
| "P@10 = 0.9 means 90 % accuracy" | It means 9 of the first 10 are relevant — nothing about the other 190. |
| "Divide by the number of results returned" | Divide by k. |
| "MRR of 0.57 means the first hit is at position 0.57" | MRR is an average of 1/position: 0.57 is "between 1st and 2nd on average". |

## 8. Activities

1. **Be the search engine (10 min).** Read 8 short "CVs"; each student ranks them for one job. Swap papers; the
   neighbour computes P@3 and RR using the teacher's labels.
2. **Design a bad ranking (5 min).** Make one with P@5 = 1.0 and MRR = 1.0 — easy. Now one with P@5 = 0.6 and RR = 0.2.
3. **Find the copier.** In Kosai's comparison tool, sort by the methods' disagreement (`RankingRepository.method_disagreement`).

## 9. Check yourself

<details><summary>1. Ranking [R4, R1, R9, R2, R7], relevant {R2, R7, R8}. P@3, P@5, RR?</summary>

P@3 = 0/3 = 0 · P@5 = 2/5 = 0.4 · RR = 1/4 = 0.25.
</details>

<details><summary>2. Three jobs have RR 1, 0.5 and 0. MRR?</summary>

(1 + 0.5 + 0) / 3 = **0.5**.
</details>

<details><summary>3. P@5 is high but MRR is low. What do you write in the book?</summary>

The system finds good candidates but does not put the best one first — something specific pushes wrong candidates
to the top (here: copied advert text). Then show which candidates and why.
</details>

## 10. In your project

| Project | Where |
|---|---|
| ResumeMatch | `resumematch/eval/metrics.py` → `precision_at_k`, `reciprocal_rank`, `mean_reciprocal_rank`, `evaluate` · `evaluate.py` · `LabelRepository` · theory `31_ResumeMatch/01_theory/06_evaluate.md` · notebook `04_evaluate.ipynb` |

## 🎬 Watch & explore

* *Evaluation metrics for information retrieval (precision@k, MRR, MAP)* — [search on YouTube](https://www.youtube.com/results?search_query=information+retrieval+evaluation+precision+at+k+MRR)
* Stanford IR book, ch. 8 — [Evaluation of ranked retrieval results](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)
