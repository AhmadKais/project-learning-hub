# Chapter 0 — How to use this guide

💡 **In short:** this guide takes you from "I have an empty project" to "I can defend it". Read a chapter, write the code it describes, run the tests, move on. Do not read the whole thing first.

## 0.1 What you are building

SpamClassifier takes an email message and answers two questions:

1. Is this spam?
2. **Why?**

The second question is the one that makes this a project rather than an exercise. Any library can give you the first answer in four lines. Being able to say *"I marked this as spam mainly because of the words winner, free and urgent"* is what you will be defending in June.

## 0.2 The shape of the work

There are eight stages in `TASKS.md`, and they are in order for a reason: each one is tested by the stage before it. You cannot sensibly build features before you can clean text, and you cannot evaluate a model before you have one.

| Stage | What you build | Tests that must go green |
|---|---|---|
| 1 | Loading and splitting the corpus | `test_dataset.py` |
| 2 | Cleaning and tokenizing | `test_email_parser.py`, `test_tokenizer.py` |
| 3 | TF-IDF and the seven handcrafted features | `test_feature_engineer.py` |
| 4 | **Naive Bayes, from scratch** | `test_naive_bayes.py` |
| 5 | SVM and the comparison | — |
| 6 | Threshold and model bundle | `test_threshold.py` |
| 7 | Database, UI, explanation | `test_repositories.py`, `test_pipeline.py` |
| 8 | Train, measure, write the book | — |

Stage 4 is the heart. Everything before it is preparation and everything after it is packaging.

## 0.3 The tests are the specification

Open the project and run:

```bash
pytest -v
```

Ninety-one tests fail with `NotImplementedError`. That is correct. The tests were written before the code, and each one describes exactly what a function has to do. When you are not sure what `caps_ratio` should return for an empty string, do not guess — read `test_caps_ratio_counts_letters_only`. The answer is there.

💡 This is the single most useful habit you can build this year: when stuck, read the test, not the docstring.

## 0.4 How to read a chapter

Each chapter has the same shape:

- a **💡 In short** box — the whole chapter in three lines
- the explanation, with code
- **❓ question boxes** — the kind of thing an examiner asks, with the answer underneath

The question boxes are not decoration. Chapter 17 collects them all into a mock exam, and chapter 20 has the answers. If you can answer every box without looking, you are ready.

## 0.5 What you need to know already

Python: functions, classes, dictionaries, list comprehensions, `for` loops. If `{k: v for k, v in pairs}` is unfamiliar, read chapter 1 first.

Maths: what a logarithm is, and that `log(a*b) = log(a) + log(b)`. That single identity is most of chapter 4.

You do **not** need to know statistics, linear algebra, or any machine learning. That is what chapters 2 to 5 are for.

## 0.6 A warning about shortcuts

`scikit-learn` has a `MultinomialNB` class. It is four lines to use, and using it would be a reasonable engineering decision in a real job.

It would also end your project. The whole claim of this work is *"I understand this algorithm, and here is my implementation to prove it"*. You import scikit-learn's version for exactly one purpose: `test_matches_sklearn` compares your output against it to within one part in a billion. It is your proof of correctness, not your implementation.

The SVM is the opposite case — there you use the library, because the SVM is the yardstick and a yardstick should be a trusted one. Chapter 5 explains why that is not a contradiction.
