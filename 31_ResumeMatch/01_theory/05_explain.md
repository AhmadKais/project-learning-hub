# Step 5 — Explaining the score

## Why this is not optional

You are ranking **people**. "Candidate 142: 0.83" is not usable:

- The recruiter cannot tell whether to trust it.
- They cannot justify the decision to anyone.
- Nobody can check the system for bias.

So every score must come apart into the reasons that made it.

## The score is already a sum

With cosine similarity on L2-normalised vectors:

```
score = Σ  resume[t] × job[t]
        t
```

Look at that carefully. It is a **sum over terms**. So each product
`resume[t] × job[t]` *is* one term's exact contribution.

To explain: compute every product, sort, take the top five.

📄 **Implementation**

```python
row = self.matrix.getrow(doc_row)
contributions = []
for c in row.indices:
    if q[c] > 0:
        contributions.append((term_at(c), row[0, c] * q[c]))
contributions.sort(key=lambda x: -x[1])
return contributions[:config.TOP_TERMS_IN_EXPLANATION]
```

💡 This is a **decomposition**, not an approximation. The test
`test_explanation_sums_to_the_score` adds up *every* contribution and asserts it
equals the score to within `1e-9`. If that passes, your explanation is provably
honest.

That is a strong claim to make in the defence, and it is the main reason this
project uses classical methods instead of neural embeddings — with BERT, no such
decomposition exists.

## What the recruiter sees

```
Candidate 0142    cosine 0.71    bm25 0.83

  matched because of:
     python       0.31
     django       0.19
     postgresql   0.12
     docker       0.06
     backend      0.03

  skills found   : Python, Django, PostgreSQL, Docker
  skills missing : (none)
  coverage       : 4 of 4 required skills (100%)
```

Keep it factual. Never write "excellent candidate" — the system measures text
similarity, it does not judge people. That distinction matters ethically and the
examiner may well probe it.

## Skills: the dictionary trap

Skills are matched against a dictionary. And here is the trap:

```
dictionary has:  "Machine Learning"
document has:    "machin learn"        (after stemming)

                 no match
```

The dictionary must go through **the same preprocessing** as the documents. That
is what the `normalised` key of `self.skills` is for:

```python
words = [t for t in self.preprocessor.process(skill) if " " not in t]
normalised = " ".join(words)           # "Machine Learning" -> "machin learn"
self.skills[normalised] = skill        # map back to the pretty display name
```

Store the normalised form for matching, the original for display.

⚠️ Why `if " " not in t`: `process()` also appends the bigrams, so "Machine Learning"
comes back as `["machin", "learn", "machin learn"]`. Joining all three would store
`"machin learn machin learn"` — a key no CV can ever contain. Joining only the single
words gives `"machin learn"`, exactly the bigram the CV's own `process()` produced.

💡 Because the preprocessor already emits bigrams, two-word skills match for
free. You built that machinery in step 4 and now it pays off twice. A skill of
**three** words ("Test Driven Development") cannot match — the pipeline stops at
bigrams — which is why `skills.csv` gives it the alias `tdd`. That is a limitation
to write in the book.

## The reliability check

Here is a real failure mode. A candidate copies phrases from the job advert into
their CV without having the skills. Text similarity goes up. They rank high.

You can catch it:

```
high score  +  low skill coverage  =  suspicious
```

```python
if result.score > 0.6 and coverage < 0.35:
    warn("High text similarity but few matching skills — "
         "the wording may have been copied from the advert. Review manually.")
```

❓ **Why does this work?**

Because copying wording moves the *text* similarity but not the *skills*. The
two signals are independent, so disagreement between them is informative.

This is the kind of thinking that turns a school project into a real system, and
it is worth a paragraph in your book.
