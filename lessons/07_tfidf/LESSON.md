# Lesson 07 — TF-IDF: turning text into numbers that mean something

> **For:** Kosai (ResumeMatch stages 3–4) · Laith (SpamClassifier stage 3) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 00 §7 (logarithms), §10; Lesson 06 &nbsp;·&nbsp; **After this:** Lessons 08, 09, 11

## The story

> Hila the recruiter (Lesson 06) now has clean word lists. She asks: *"Which words describe each candidate?"* Counting
> words is the obvious answer — but in every CV the most common words are "experience", "team", "worked". Those tell her
> nothing. What she wants are the words that make a CV **different**: "kubernetes", "figma". TF-IDF is the arithmetic
> for exactly that idea: **a word is important for a document if it is frequent in it and rare in the others.**

## 🎯 By the end, the student can

1. Build a bag-of-words table by hand.
2. Compute TF, DF, IDF and TF-IDF for a small example, with their project's exact formula, every step written out.
3. Explain each `+1` in the IDF formula and why there is a log.
4. Explain L2 normalisation and why a long document must not win just by being long.

## Words you need

| word | meaning |
|---|---|
| **document** | one text: one CV, one SMS |
| **collection / corpus** | all the documents: 200 CVs |
| **term** | one cleaned word (Lesson 06) |
| **TF — term frequency** | how many times the term is in **this** document |
| **DF — document frequency** | in how many **documents** the term appears (each document counts once) |
| **N** | the number of documents |
| **IDF — inverse document frequency** | a weight: big for rare terms, small for common ones |
| **TF-IDF** | TF × IDF |
| **vector** | the row of numbers describing one document (Lesson 00 §10) |
| **L2 normalisation** | dividing a vector by its length so that its length becomes 1 |

---

## 1. Bag of words — just count

Three tiny CVs (already cleaned):

```
CV 1:  python python sql docker
CV 2:  java sql spring
CV 3:  python sql pandas
```

Make a table: one **row per CV**, one **column per term**, and in each cell **how many times** the term appears.

![bag of words](figs/bag_of_words.png)

That's a **bag of words**: like pouring the words into a bag and counting them — the order is forgotten. Each CV is now a
row of numbers, which the computer can compare.

**The problem:** `sql` is in every CV. It describes *none* of them better than the others. We want it to weigh **less**.

## 2. TF-IDF, step by step

![TF-IDF step by step](figs/tfidf_build.gif)

### Step 1 — TF: count in this document

`python` appears 2 times in CV 1 → TF = 2. (Kosai uses the raw count; Laith divides by the message length, §5.)

### Step 2 — DF: in how many documents?

Count each **document** once, no matter how many times the word appears in it:

```
python: CV 1, CV 3          → DF = 2
sql:    CV 1, CV 2, CV 3    → DF = 3
docker: CV 1                → DF = 1     (java, spring, pandas: also 1)
```

### Step 3 — IDF: rare → big weight

Kosai's formula (N = 3 documents):

$$\text{idf} = \ln\frac{1+N}{1+\text{DF}} + 1$$

Read it in three parts:

1. **N / DF** — "one in how many documents has this word?" Rare word → big number.
2. **ln( … )** — shrink it so it grows slowly (Lesson 00 §7). Without the log, a word in 1 of 200 CVs would weigh 200×
   more than a word in all of them — far too much.
3. **+1** in two places — explained below.

```
python:  (1 + 3) / (1 + 2) = 4 / 3 = 1.333    ln(1.333) = 0.2877    + 1  →  idf = 1.2877
sql:     (1 + 3) / (1 + 3) = 4 / 4 = 1        ln(1)     = 0         + 1  →  idf = 1.0000
docker:  (1 + 3) / (1 + 1) = 4 / 2 = 2        ln(2)     = 0.6931    + 1  →  idf = 1.6931
```

(`ln` on the calculator, or `math.log(...)` in Python.)

**The two `+1`s:**
* `1 +` inside: avoids dividing by zero, and smooths the numbers a little.
* `+ 1` at the end: a word in *every* document gets 1, not 0 — it is **weakened, not deleted**.

### Step 4 — TF × IDF

```
CV 1:   python 2 × 1.2877 = 2.58     sql 1 × 1.0 = 1.00     docker 1 × 1.6931 = 1.69
```

Read it: *"`docker` describes CV 1 better than `sql`, even though each appears once — because docker is rare."*

### Step 5 — L2 normalisation: make every CV the same length

The **length** of a row of numbers is Pythagoras (Lesson 00 §10): the root of the sum of the squares.

```
length of CV 1 = √(2.58² + 1.00² + 1.69²) = √(6.66 + 1.00 + 2.86) = √10.52 = 3.24
divide every number by 3.24:   python 2.58 / 3.24 = 0.79    sql 0.31    docker 0.52
check: √(0.79² + 0.31² + 0.52²) = √(0.62 + 0.10 + 0.27) = √0.99 ≈ 1 ✓
```

![final matrix](figs/tfidf_final.png)

**Why?** A CV that pastes the same paragraph four times would have 4× bigger numbers everywhere and win every comparison.
After dividing by the length, only the **proportions** remain — which words, in what mix — not how much text there is.

## 3. The IDF curve

![idf curve](figs/idf_curve.png)

With 200 CVs: "kubernetes" (in 5 CVs) gets a big weight, "python" (60) a medium one, "experience" (190) almost the
minimum. The curve drops fast and then flattens — that's the log.

## 4. On the project's real CVs

![real CV](figs/real_cv.png)

Left: the words this CV repeats. Right: the words with the highest TF-IDF — the ones that make it **different**: skills
like `figma`, `webpack` — and the candidate's **name** (rare!). The name is not a skill — it's exactly why Kosai's
pipeline removes personal data **before** counting (Lesson 06).

## 5. ⚠️ The two projects use slightly different formulas

| | TF | IDF | check values |
|---|---|---|---|
| ResumeMatch (Kosai) | raw count | `ln((1 + N) / (1 + df)) + 1` | N = 3: df 2 → 1.2877, df 1 → 1.6931, df 3 → 1.0000 |
| SpamClassifier (Laith) | count ÷ number of terms in the message | `ln(N / (1 + df)) + 1` | N = 1000: "the" (1000) ≈ 1.0, "meeting" (100) ≈ 3.3, "viagra" (5) ≈ 6.1 |

Laith's "meeting", step by step: N / (1 + df) = 1000 / 101 = 9.90 → ln(9.90) = 2.29 → + 1 = **3.29**.

Use your own project's formula exactly — the tests check the numbers.

## 6. The bug everyone makes once

```python
df = Counter()
for doc in docs:
    df.update(set(doc))      # set() !  — each term counts ONCE per document
```

Without `set()`, a word shouted 500 times in one e-mail gets DF = 500 and looks "common everywhere". Tests:
`test_document_frequency_counts_documents_not_occurrences` (Kosai), the vocabulary test (Laith).

## 7. Common mistakes

| student says | the truth |
|---|---|
| "IDF is per document" | IDF is per **term**, computed once over the whole training collection. TF is per document. |
| "Compute IDF with the test documents too" | Leakage (Lesson 05). Fit on training; reuse for new documents. |
| "TF-IDF understands meaning" | It counts. "java" (coffee) = "java" (language). |

## 8. Activities

1. **Paper TF-IDF (20 min).** 4 short job ads on cards. Groups compute DF and IDF (calculator: `ln`), then TF-IDF for one
   ad, then its length and the normalised row.
2. **Guess the weight (5 min).** 6 words from the CV data — the class orders them by IDF before seeing the DF counts.
3. **Break it (5 min).** Remove `set()` in the notebook and see how the weights change.

## 9. Do it yourself

<details><summary>1. N = 5 CVs, "docker" in 1 of them. Kosai's IDF, every step.</summary>

(1 + 5) / (1 + 1) = 6 / 2 = 3 → ln(3) = 1.0986 → + 1 = **2.0986**.
</details>

<details><summary>2. CV 3 = "python sql pandas". Its TF-IDF row and normalised row.</summary>

python 1 × 1.2877 = 1.29 · sql 1.00 · pandas 1.69 · length √(1.66 + 1 + 2.86) = √5.52 = 2.35 → 0.55, 0.43, 0.72.
</details>

<details><summary>3. Normalise the row (3, 4).</summary>

length √(9 + 16) = 5 → **(0.6, 0.8)**.
</details>

## 10. In your project

| Project | Where |
|---|---|
| ResumeMatch | `resumematch/nlp/vocabulary.py` → `VocabularyBuilder.build`, `compute_idf` · `rank/tfidf.py` → `TfidfRanker.fit`, `_l2_normalise_rows` · theory `31_ResumeMatch/01_theory/01_vectors.md` · notebook `02_tfidf_cosine.ipynb` |
| Spam | `spamclassifier/features/feature_engineer.py` → `fit`, `transform`, `idf_value`, `l2_normalise` · theory `08_SpamClassifier/01_theory/03_features.md` §3.3–3.5 |

## 🎬 Watch & explore

* *TF-IDF explained* — [search on YouTube](https://www.youtube.com/results?search_query=TF-IDF+explained+simply)
* Stanford IR book — [Inverse document frequency](https://nlp.stanford.edu/IR-book/html/htmledition/inverse-document-frequency-1.html)
