# Step 1 — Turning text into numbers

## The problem

A computer cannot compare "I know Python" with "Python developer wanted". It
compares numbers. So first we turn every document into a list of numbers.

## Bag of words

The simplest idea: count the words.

```
"python django python"   ->   {python: 2, django: 1}
```

Give every word in the whole collection a column number, and each document
becomes a row of counts:

```
             python  django  java  sql
  doc0  ->      2       1      0    0
  doc1  ->      1       0      1    0
  doc2  ->      0       0      1    1
```

That is a **matrix**. Each row is a document, each column is a word.

❓ **What does this representation throw away?**

Word order. "not good at Python" and "Python, not good at" look identical to it.
That is a real limitation and you must say so in your book. For matching CVs to
jobs it turns out not to matter much — what matters is *which* words appear.

## Why raw counts are not enough

Look at a real CV. The most common words are "and", "the", "experience",
"team", "responsible". Every single CV has them. They tell you nothing about
who to hire.

Meanwhile "Kubernetes" appears in maybe 5 CVs out of 200. That word is
**informative** — it actually separates people.

So we need a weight that says: *common words count less, rare words count more.*

## IDF — inverse document frequency

```
idf(term) = log( N / df(term) )

    N          = how many documents in total
    df(term)   = in how many of them this term appears
```

With 200 CVs:

| term | df | N/df | idf = ln(N/df) |
|---|---|---|---|
| experience | 190 | 1.05 | 0.05 |
| python | 60 | 3.33 | 1.20 |
| kubernetes | 5 | 40 | 3.69 |

"kubernetes" is worth about 70× more than "experience". That is what we wanted.

❓ **Why the logarithm? Why not just N/df?**

Without the log, "kubernetes" would be worth 40× "experience" *linearly*, and a
term appearing once would completely dominate everything else. The log squashes
the scale: importance rises, but slowly. This is a question you will be asked.

## The smoothed version (what you actually implement)

```python
idf = math.log((1 + N) / (1 + df)) + 1
```

Two changes, and you must be able to explain both:

- **`1 +` in the denominator** — never divide by zero if a term is unseen.
- **`+ 1` at the end** — a term appearing in *every* document gets
  `ln(1) + 1 = 1`, not `0`. It is weakened, not deleted.

📄 **Check your implementation against these**

```python
compute_idf(df=2, n_docs=3)  ==  ln(4/3) + 1  ==  1.2877
compute_idf(df=1, n_docs=3)  ==  ln(4/2) + 1  ==  1.6931
compute_idf(df=3, n_docs=3)  ==  ln(4/4) + 1  ==  1.0000
```

## TF-IDF = the two multiplied

```
weight(term, doc) = tf(term, doc) × idf(term)
```

- `tf` — how often this term is in *this* document (local importance)
- `idf` — how rare it is across *all* documents (global importance)

A term scores high only when it is frequent here **and** rare elsewhere. That is
exactly the definition of "this word characterises this document".

💡 One counting mistake ruins everything: **`df` counts documents, not
occurrences.** "python" twice in one CV is still `df = 1` for that CV. There is a
test for this (`test_document_frequency_counts_documents_not_occurrences`)
because it is such an easy bug and it silently corrupts every weight.
