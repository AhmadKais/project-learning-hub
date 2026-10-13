# Step 6 — Measuring how good the ranking is

## Ranking is not classification

In classification there is one right answer and you are right or wrong. In
ranking there is an **order**, and being nearly right matters.

More importantly: a recruiter reads the **top ten** and stops. Being brilliant
at position 47 is worth nothing. So the metrics must weight the head of the list.

## Precision@k

> Of the top k candidates, how many were genuinely relevant?

```python
def precision_at_k(ranking, relevant, k):
    top = ranking[:k]
    return len([c for c in top if c in relevant]) / k
```

⚠️ Divide by **`k`**, not by `len(top)`. If the ranking is shorter than `k`, the
missing slots count as misses. Dividing by `len(top)` silently inflates your
results, and there is a test that catches it
(`test_precision_denominator_is_k_not_list_length`).

## MRR — Mean Reciprocal Rank

> How high up was the **first** relevant candidate?

```python
def reciprocal_rank(ranking, relevant):
    for position, candidate in enumerate(ranking, start=1):
        if candidate in relevant:
            return 1.0 / position
    return 0.0
```

- first place → 1.0
- second → 0.5
- tenth → 0.1
- never → 0.0

MRR is the average over all jobs.

## Why both

📄 **Worked example** (this is in the tests — verify by hand)

```
ranking  = [C3, C7, C1, C9]
relevant = {C1, C7}

P@2  = 1/2 = 0.50      (of C3, C7 only C7 is relevant)
P@4  = 2/4 = 0.50
RR   = 1/2 = 0.50      (first relevant is at position 2)
```

They measure different things:

- **P@k ignores the order inside the top k.** [C7, C3] and [C3, C7] score the same.
- **MRR ignores everything after the first hit.** One relevant candidate at
  position 1 scores 1.0 even if the other nine are terrible.

Neither alone is enough. Report both.

❓ **What does it mean if P@5 is high but MRR is low?**

The system finds good candidates but does not put the best one first. Worth
saying in your results chapter — it is a real, specific finding.

## The ground truth

Metrics need an answer key. You build it by hand: for ~50 jobs, mark which
candidates are genuinely relevant.

⚠️ **Label before you run the system, and without looking at its rankings.**

If you label afterwards you will unconsciously agree with the machine, and your
measurement becomes meaningless. This is why the database has a
`before_ranking` column — rows without it are excluded from the metrics.

💡 It is tedious. Budget real hours for it in stage 6. The system has a labelling
screen to make it bearable, and the labels are saved so you only do it once.

## Timing

Use the **median**, not the mean:

```python
median_ms = statistics.median(times)
```

The first run pays for cache warm-up and file loading. One slow outlier drags an
average around; the median ignores it.
