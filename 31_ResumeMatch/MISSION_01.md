# Mission 1 - From text to a ranking

**Student:** Kosai Badreih  ·  **Time:** two weeks  ·  **Ends with:** a 10-minute talk in class

You will explain the heart of your project to the class. To explain it you have to understand it, so the
mission has three parts: study, homework, talk.

## Part 1 - Study (first week)

In this order. Keep a notebook: every new word and every formula goes in it.

1. Lesson: [text preprocessing](../lessons/06_text_preprocessing/LESSON.md)
2. Lesson: [TF-IDF](../lessons/07_tfidf/LESSON.md)
3. Lesson: [vectors and cosine](../lessons/08_vectors_cosine/LESSON.md)
4. Theory: [`01_vectors.md`](01_theory/01_vectors.md), [`02_cosine.md`](01_theory/02_cosine.md), [`03_bm25.md`](01_theory/03_bm25.md)
5. Notebook [`01_preprocessing.ipynb`](02_examples/01_preprocessing.ipynb): run every cell, then run one real CV through the pipeline and print every step.
6. Notebook [`02_tfidf_cosine.ipynb`](02_examples/02_tfidf_cosine.ipynb): run every cell, then rank the CVs for one job and look at the top term of each.

## Part 2 - Homework (hand in before your talk)

**A. Exercises.** In `03_exercises/exercises.py` write `ex02`, `ex05`, `ex06`, `ex07`, `ex12`. Check them:

```bash
cd 31_ResumeMatch/03_exercises
pytest test_exercises.py -k "ex02 or ex05 or ex06 or ex07 or ex12" -v
```

Open `solutions.py` only after your tests pass. In class you will explain one of them line by line.

**B. On paper.** Show every step - a final number alone gets no points. Bring the paper or a photo of it.

Three CVs, already preprocessed, and a job:

```text
CV1: python sql python
CV2: java sql
CV3: python django
job: python sql
```

1. The document frequency of every term, and its IDF with your project's formula
   `idf = ln((1 + N) / (1 + df)) + 1`.
2. The TF-IDF vector of each CV and of the job (count x idf), made unit length. The cosine of the job with
   each CV. The ranking.
3. BM25 (k1 = 1.5, b = 0.75, BM25 idf = `ln((N - df + 0.5) / (df + 0.5) + 1)`): the score of the term
   `python` in CV1 and in CV3. Why is CV1's score not twice CV3's even though it says python twice?
4. A ranking for one job is `C4, C1, C7, C2, C9` and the relevant CVs are {C1, C2, C3}. Precision at 3?
   Three jobs had their first relevant CV at positions 2, 1 and 3 - the mean reciprocal rank?

**C. In your own words.** 3-5 sentences each.

1. Why does IDF make `python` count less than `django` here? When is that a good thing?
2. Why are the vectors made unit length? What would long CVs do to the ranking otherwise?

## Part 3 - The talk (10 minutes + 5 minutes of questions)

Title: **From text to a ranking**. Six slides at most, one idea each:

1. The problem: 200 CVs, one job - who first?
2. The pipeline: one CV, step by step (scrub, tokens, stopwords, stems)
3. TF-IDF: why rare words weigh more - your IDF numbers
4. Cosine: your ranking on the board
5. BM25 in one sentence: repeats help less and less
6. Live demo: notebook 02, the top CVs and their top terms

Rules: no slide full of text, no code copied from the solution. Draw on the board where you can.
After the talk I ask one question from [`08_exam.md`](05_defence/08_exam.md) and one about
your paper task.

## How it is graded

| Part | Points |
|---|---|
| A. exercises pass and you can explain them | 25 |
| B. paper task correct, every step shown | 25 |
| C. answers in your own words | 10 |
| The talk: correct, clear, on time | 25 |
| Answers to the questions | 15 |
