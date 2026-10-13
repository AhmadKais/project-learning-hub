# Chapter 4 — Naive Bayes, from scratch

💡 **In short:** count how often each word appears in spam and in ham, add 1 to every count so nothing is ever zero, take logarithms so nothing underflows, and add them up. That is the whole algorithm. This chapter is the heart of your project.

## 4.1 Bayes' theorem

```
P(A | B) = P(B | A) × P(A) / P(B)
```

In words: the probability of A given B, in terms of the probability of B given A.

For us:

```
P(spam | words) = P(words | spam) × P(spam) / P(words)
```

- `P(spam | words)` — what we want: is this message spam, given what it says?
- `P(words | spam)` — countable: how often do these words show up in spam?
- `P(spam)` — countable: what fraction of the corpus is spam?
- `P(words)` — awkward, and **it cancels**.

It cancels because we are comparing two classes over the same message. `P(words)` is identical in both, so it has no effect on which is larger. We only ever compare, so we can drop it.

```
score(spam) ∝ P(words | spam) × P(spam)
score(ham)  ∝ P(words | ham)  × P(ham)
```

Whichever is bigger wins.

## 4.2 The naive assumption

`P(words | spam)` is still not countable. "These exact 60 words in this exact order" has appeared in your corpus zero times.

So we assume the words are **independent given the class**:

```
P(w1, w2, ..., wn | spam) = P(w1|spam) × P(w2|spam) × ... × P(wn|spam)
```

This is the "naive" in Naive Bayes, and it is **false**. `credit` and `card` obviously travel together. Nobody pretends otherwise.

It is used anyway, for two reasons. First, it turns an unmeasurable quantity into a product of single-word counts, which is the difference between impossible and instant. Second — and this is the part worth saying at a defence — the individual probabilities come out wrong, but they come out wrong *in roughly the same direction for both classes*, so the comparison usually survives. We need the ranking, not the number.

❓ **The independence assumption is false. Why is the classifier still good?**

Because classification only needs the correct *ordering* of the two class scores, not correct probabilities. Correlated words cause the same kind of over-counting on both sides, so the comparison is largely preserved even though the absolute values are distorted. It is a well-documented empirical result — Naive Bayes routinely outperforms what its assumptions deserve. You should also say the honest part: the probabilities it outputs are poorly calibrated, which is why 0.94 should not be read as "94% certain".

## 4.3 Multinomial, and why

There are several Naive Bayes variants. The multinomial one models **counts**: a word appearing four times contributes four times.

The alternative, Bernoulli, models only presence or absence. For spam, repetition is itself evidence — `FREE FREE FREE` is not the same signal as one `free` — so multinomial is the right choice. Metsis et al. (2006), in your bibliography, compared the variants on exactly this task.

## 4.4 Training: just counting

```
prior[c]     = count(messages in class c) / N

count[c][w]  = total occurrences of w across class c
total[c]     = sum of all counts in class c

P[c][w]      = count[c][w] / total[c]
```

That is it. One pass over the data. No iterations, no learning rate, no convergence. This is why retraining is cheap enough to offer as a button in the UI.

But two things break if you stop here.

## 4.5 Problem one: zeros

A word that never appears in ham gets `P[ham][w] = 0`. One zero in a product makes the whole product zero — so a single unseen word would make the message infinitely spammy, regardless of everything else in it.

**Laplace smoothing**: add `alpha` (we use 1) to every count.

```
P[c][w] = (count[c][w] + alpha) / (total[c] + alpha × |V|)
```

The `alpha × |V|` in the denominator keeps the probabilities summing to 1 across the vocabulary — `|V|` being the vocabulary size, because you added alpha once for every word in it.

📄 **Stage 4: training**
```python
def fit(self, documents, labels):
    from collections import Counter

    self._vocabulary = sorted({t for doc in documents for t in doc})
    v_size = len(self._vocabulary)
    n = len(documents)

    for c in (HAM, SPAM):
        docs_c = [d for d, y in zip(documents, labels) if y == c]
        self._log_prior[c] = math.log(len(docs_c) / n)

        counts = Counter(t for d in docs_c for t in d)
        total = sum(counts.values())

        self._log_likelihood[c] = {
            w: math.log((counts[w] + self.alpha) / (total + self.alpha * v_size))
            for w in self._vocabulary
        }

    self._fitted = True
    return self
```

❓ **What exactly goes wrong without smoothing?**

Any message containing a word that never appeared in one class gets probability exactly zero for that class, no matter what else it contains. A legitimate message with one unusual word would be classified as spam with complete confidence. Smoothing gives unseen words a small probability instead of none, so one unfamiliar word can no longer override all the other evidence.

## 4.6 Problem two: underflow

Multiply 300 probabilities of around 0.001:

```python
0.001 ** 300     # 0.0
```

Not approximately zero — exactly zero. A `float` cannot represent anything below about 1e-308. Both class scores become 0.0, the comparison becomes meaningless, and every long message gets the same answer.

**The fix:** work in logarithms throughout, so the product becomes a sum.

```
log score(c) = log P(c) + Σ log P(w | c)
```

That is why `fit` stores `math.log(...)` rather than the raw probability. You never leave log space during the calculation.

📄 **Stage 4: scoring**
```python
def predict_log_scores(self, tokens):
    scores = {}
    for c in (HAM, SPAM):
        score = self._log_prior[c]
        for t in tokens:
            if t in self._log_likelihood[c]:       # skip unknown words
                score += self._log_likelihood[c][t]
        scores[c] = score
    return scores
```

Unknown tokens are skipped rather than smoothed at prediction time. They would contribute the same constant to both classes, so they cannot change the outcome — adding them is work with no effect.

## 4.7 Getting a probability back

The UI needs a number between 0 and 1. The conversion has to stay in log space until the last moment:

```
P(spam) = 1 / (1 + exp( score[ham] − score[spam] ))
```

This is the sigmoid of the *difference* of the two scores.

📄 **Stage 4: the conversion, done safely**
```python
def predict_proba(self, tokens):
    scores = self.predict_log_scores(tokens)
    difference = scores[HAM] - scores[SPAM]

    if difference > 700:        # exp(709) overflows float64
        return 0.0
    if difference < -700:
        return 1.0
    return 1.0 / (1.0 + math.exp(difference))
```

📄 **The mistake this avoids**
```python
# WRONG - underflows to 0.0 for any message longer than a sentence
p_spam = math.exp(scores[SPAM])
p_ham  = math.exp(scores[HAM])
return p_spam / (p_spam + p_ham)       # 0.0 / 0.0  ->  ZeroDivisionError
```

Exponentiating each score on its own walks straight back into the underflow the logs were protecting you from. `test_no_underflow_on_long_document` feeds the classifier 300 repeated tokens for exactly this reason.

The `±700` clamps matter too: `math.exp(710)` raises `OverflowError`. At that distance the answer is 0 or 1 to far more precision than anyone needs.

❓ **Why the difference of the scores rather than each score separately?**

Because the difference is a small, well-behaved number while the scores themselves are large and negative. Subtracting first and exponentiating once keeps everything inside the range a float can hold; exponentiating each score separately does not.

## 4.8 Explanation — why this model is the primary one

Here is the payoff, and the reason the project uses Naive Bayes as its main model even though the SVM may score higher.

For any word:

```
log_odds(w) = log P(w | spam) − log P(w | ham)
```

Positive means the word pushes towards spam; negative, towards ham. It is read **straight off the trained parameters**. No separate explanation model, no approximation, no post-hoc estimation — this number *is* how the classifier works.

📄 **Stage 4: explanation**
```python
def log_odds(self, token):
    if token not in self._log_likelihood[SPAM]:
        return 0.0                  # never seen: it tells us nothing
    return self._log_likelihood[SPAM][token] - self._log_likelihood[HAM][token]

def explain(self, tokens, top_n=None):
    top_n = top_n or config.TOP_REASONS
    seen = {}
    for t in tokens:
        if t not in seen:
            seen[t] = self.log_odds(t)
    ranked = sorted(seen.items(), key=lambda kv: abs(kv[1]), reverse=True)
    return [Reason(tok, w) for tok, w in ranked[:top_n]]
```

Two details with reasons behind them:

- **De-duplicate.** A word repeated five times is one reason, not five. The user wants distinct explanations.
- **Rank by absolute value.** That lets a strong *ham* signal appear too. "Why was this not spam?" is a real question, and the UI asks it whenever the probability sits near the threshold.

❓ **Why is Naive Bayes the primary model if the SVM might be more accurate?**

Because the project requires an explanation for every verdict, and in Naive Bayes the explanation is exact: each word's contribution is a parameter of the model. The SVM, after sigmoid calibration, no longer has that clean correspondence between a coefficient and the final probability, so any explanation from it is an approximation. A spam filter that hides a message without being able to say why is not usable — the person cannot judge whether to trust it. Accuracy was never the only requirement.

## 4.9 Proving it is right

`test_matches_sklearn` is the blocking test. It trains scikit-learn's `MultinomialNB` with `alpha=1.0` on the same data and requires agreement to within `1e-9`.

They are the same estimator, so they must produce the same posterior. If they do not, the bug is in one of three places, and the gap usually tells you which:

| Symptom | Likely cause |
|---|---|
| Way off on every input | smoothing applied to the numerator but not the denominator |
| Right ordering, wrong values | forgot `+ alpha × |V|`, or used the wrong `|V|` |
| Correct for short, wrong for long | left log space too early |
| Fails only on unseen words | unknown tokens being smoothed at predict time instead of skipped |

💡 Do not "fix" this test by loosening the tolerance. It is the evidence that your implementation is correct, and it is the first thing an examiner will ask you to run.

## 4.10 Worked example

Four documents, two per class:

```
spam:  ["free", "money", "now"]       ["free", "prize", "winner"]
ham:   ["meeting", "tomorrow", "office"]  ["project", "meeting", "notes"]
```

Vocabulary: `free, meeting, money, notes, now, office, prize, project, tomorrow, winner` — 10 words.

Priors: two documents each, so `P(spam) = P(ham) = 0.5`, and `log(0.5) ≈ −0.693`.

Spam counts: `free` 2, `money` 1, `now` 1, `prize` 1, `winner` 1 — total 6.

With `alpha = 1` and `|V| = 10`:

```
P(free | spam)  = (2 + 1) / (6 + 10) = 3/16 = 0.1875
P(free | ham)   = (0 + 1) / (6 + 10) = 1/16 = 0.0625
log_odds(free)  = log(0.1875) − log(0.0625) = log(3) ≈ 1.10
```

Positive, so `free` pushes towards spam — and notice it is finite rather than infinite, which is smoothing doing its job: `free` never appears in ham, and without smoothing that would be `log(0)`.

Work this through by hand before the defence. Being able to produce these numbers on paper is the difference between having implemented the algorithm and having understood it.
