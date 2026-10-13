# Before you start

## What you are building

A program that reads a pile of CVs and a job description, and puts the CVs in
order — best match first. Next to every candidate it shows **why**: which words
mattered, which skills they have, which they are missing.

That "why" is the whole point. A number on its own is useless to a recruiter.

## The one sentence version

> Turn each document into a list of weighted words, then measure how similar
> two lists are — in two different ways, and compare them.

## Why two ways?

Because they disagree, and the disagreement is interesting.

Imagine two candidates, both perfect for the job:

- **Amir** writes a tight 1-page CV.
- **Dana** writes a detailed 9-page CV.

Dana's CV contains the word "Python" eight times simply because it is longer.
A naive system would rank Dana first — not because she is better, but because
she wrote more. That is not fair, and fixing it is a real engineering problem.

The two methods fix it differently:

| | TF-IDF + cosine | BM25 |
|---|---|---|
| Length | handled by geometry (the angle ignores length) | handled by an explicit formula with a knob called `b` |
| Repetition | 10 times counts 10× | 10 times counts only a little more than 2 times |
| Knobs to tune | none | `k1` and `b` |

**Your research question:** which one is fairer here, and by how much?
You will answer it with a number, not an opinion.

## How to use this guide

Read a section, then write that code, then run that test. Do not read the whole
guide first — you will forget it.

💡 The tests are already written. They are your specification. When a test says
`assert precision_at_k(...) == 0.5`, that number was computed by hand — your job
is to make the code agree with it.

## What you need to know already

- Python: functions, classes, lists, dictionaries
- That is genuinely it. Everything else is explained here.

You do **not** need: neural networks, a GPU, or any maths beyond logarithms and
the Pythagorean theorem.
