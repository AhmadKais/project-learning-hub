# Lesson 11 — Naive Bayes from scratch: counting your way to a spam filter

> **For:** Laith (SpamClassifier stage 4 — the heart of the project) &nbsp;·&nbsp; **Time:** 3 × 45 min
> **Before:** Lesson 00 §1, §4, §7 (fractions, probability, logs); Lessons 03, 06 &nbsp;·&nbsp; **After this:** Lessons 04, 14

**In one sentence:** every word in a message is a clue; Naive Bayes counts how often each clue appeared in spam and in
normal messages, and combines the clues into one verdict — and can tell you which clues convinced it.

## 🗺️ The map of this lesson

```mermaid
flowchart LR
    A["1–3 · Bayes:<br/>one word, by counting"] --> B["4 · Many words:<br/>the naive trick"]
    B --> C["5 · Training =<br/>counting"]
    C --> D["6 · Bug 1: zeros<br/>→ smoothing"]
    D --> E["7 · Bug 2: tiny numbers<br/>→ logs"]
    E --> F["8–9 · Classify &<br/>explain (log-odds)"]
```

## The story

> Maya (the phone shop, Lesson 01) asks her nephew: *"How does your filter decide? Explain it to me without computers."*
> He answers with a question: *"If I tell you a message contains the word 'free', how sure are you it's spam?"* — *"Pretty
> sure."* — *"And if it also contains 'prize' and a link?"* — *"Almost certain."* — *"And if instead it says 'see you
> tomorrow'?"* — *"Then it's a customer."* **That's the whole algorithm**: each word is a piece of evidence, and we combine
> the evidence. Naive Bayes does the same thing with counting and probabilities — and can tell you exactly which words
> convinced it.

### 🌍 Real world

* In **2002** the programmer Paul Graham published *"A Plan for Spam"*: count how often each word appears in spam and in good
  mail, combine the evidence with Bayes' rule. It worked so well that within a few years almost every e-mail program had a
  "Bayesian" spam filter. Laith's project is that idea.
* **Doctors** reason the same way: a symptom (the evidence) changes how likely each illness is, starting from how common the
  illness is (the prior).
* **A detective** collects clues; each clue makes some suspects more likely and others less. No single clue decides — the
  combination does.

## Words you need

| word | meaning | Maya's example |
|---|---|---|
| **P(spam)** | the share of all messages that are spam | 13 % → 0.134 — the **prior**: what we believe *before* reading the message |
| **P(free \| spam)** | among spam messages only, the share containing "free" — read the bar as "**given**" or "**among**" | 23 % — the **likelihood** |
| **P(spam \| free)** | among messages containing "free", the share that are spam | 75 % — the **posterior**: what we believe *after* seeing "free" |
| **evidence** | what we observe: the words of the message | |
| **independent** | knowing one thing tells you nothing about the other | two dice |
| **smoothing** | adding a little to every count so nothing is exactly 0 | |
| **log space** | doing the calculation with logs, adding instead of multiplying (Lesson 00 §7) | |
| **log-odds of a word** | how strongly that word pushes toward spam (+) or ham (−) | |

---

## 1. Bayes' theorem — first with counting, no formula

All 5,574 SMS, real counts:

```
all messages: 5,574
   spam: 747              ham (normal): 4,827
messages that contain "free":
   spam with "free": 174   ham with "free":  59
```

**Question:** a new message contains "free". How likely is it spam?

**Answer by counting:** look **only** at the messages that contain "free" — there are 174 + 59 = 233 of them. Of these,
174 are spam:

```
P(spam | free) = 174 / 233 = 0.747      → 75 %
```

That's it. Bayes' theorem is "throw away everything that doesn't match what you saw, then count".

## 2. The same thing as a picture

![Bayes with areas](figs/bayes_square.gif)

1. The square is all 5,574 messages. Spam is the thin strip (13.4 %), ham the rest.
2. Shade the messages that contain "free": 23.3 % of the spam strip, but only 1.2 % of the ham part.
3. We **know** the new message has "free" → only the shaded parts are possible now.
4. Of the shaded area, the orange part is 174 / (174 + 59) = **75 %**.

**The surprise:** "free" appears in only 23 % of spam — yet seeing it raises our belief from 13 % to 75 %. Because it is
**even rarer** in ham.

## 3. The same thing as a formula

$$P(\text{spam}\mid w)=\frac{P(w\mid\text{spam})\times P(\text{spam})}{P(w)}$$

Check it with our numbers, step by step:

```
P(free | spam) = 174 / 747     = 0.233      (likelihood)
P(spam)        = 747 / 5574    = 0.134      (prior)
P(free)        = 233 / 5574    = 0.0418     (all messages with "free")

P(spam | free) = 0.233 × 0.134 / 0.0418 = 0.0312 / 0.0418 = 0.747  ✓ the same 75 %
```

In words: **posterior = likelihood × prior / evidence**. Or: *what we believe after = how typical the word is for spam ×
what we believed before*.

**Classroom puzzle — the doctor's test:** a disease affects 1 in 1,000 people. A test catches 99 % of sick people, but
also says "sick" for 5 % of healthy people. You test positive. Chance you're sick? (Most people say 99 %.) Count with
100,000 people: 100 sick → 99 positive; 99,900 healthy → 4,995 positive. P(sick | positive) = 99 / (99 + 4,995) =
**1.9 %**. The **prior** (1 in 1,000) matters enormously.

## 4. Many words — the "naive" part

A message has many words: "free", "prize", "claim". We'd need P(free **and** prize **and** claim | spam) — but most
combinations of words never appear even once in 5,574 messages. So we make a simplifying assumption:

> **Naive assumption:** within one class, the words are independent — like separate dice.

Then the probability of all the words together is the **product** of their separate probabilities:

$$P(w_1, w_2, w_3\mid\text{spam}) \approx P(w_1\mid\text{spam})\times P(w_2\mid\text{spam})\times P(w_3\mid\text{spam})$$

It is false — some words travel together. On the real spam SMS:

![words that travel together](figs/naive_pairs.png)

"claim" and "prize" appear together in 6.4 % of spam, four times more than the naive guess (1.6 %). But for **choosing**
between two classes it works very well anyway, because the mistakes push both scores in a similar way — and the **order**
(spam above ham) is all we need.

So, to classify, compute two scores and compare:

```
score(spam) = P(spam) × P(w1|spam) × P(w2|spam) × …
score(ham)  = P(ham)  × P(w1|ham)  × P(w2|ham)  × …
the bigger score wins
```

## 5. Training = counting (a worked example to do on the board)

Four training messages (already cleaned):

```
spam:  [free, money, now]          [free, prize, winner]
ham:   [meeting, tomorrow, office] [project, meeting, notes]
```

**Priors:** 2 of 4 messages are spam → P(spam) = 2/4 = 0.5; P(ham) = 0.5.

**Vocabulary** (all different words): free, meeting, money, notes, now, office, prize, project, tomorrow, winner →
**|V| = 10** words.

**Counts inside each class:**

```
spam words: free 2, money 1, now 1, prize 1, winner 1           → total 6
ham words:  meeting 2, tomorrow 1, office 1, project 1, notes 1  → total 6
```

**Probability of a word inside a class** — at first: count / total. P(free | spam) = 2 / 6 = 0.333.

## 6. Bug 1 — zeros → Laplace smoothing

"free" never appears in ham → P(free | ham) = 0 / 6 = **0**. Then *any* message containing "free" gets score(ham) =
… × 0 × … = **0**, whatever else it says — even "free parking at tomorrow's meeting". One unseen word kills a whole class.

![smoothing](figs/smoothing.png)

**Laplace smoothing:** pretend every word was seen **once more** than it was (add α = 1 to every count). To keep the
probabilities adding up to 1, add |V| (once for each of the 10 words) to the total:

$$P(w\mid c)=\frac{\text{count}(w, c)+1}{\text{total}(c)+|V|}$$

```
P(free | spam) = (2 + 1) / (6 + 10) = 3 / 16 = 0.1875
P(free | ham)  = (0 + 1) / (6 + 10) = 1 / 16 = 0.0625        ← small, but not zero
```

## 7. Bug 2 — underflow → work with logs

A long message has 300 words. Multiplying 300 numbers like 0.001 gives 10⁻⁹⁰⁰. The computer can't store anything below
about 10⁻³⁰⁸ — it becomes **exactly 0.0** for both classes, and the comparison is meaningless.

![underflow](figs/underflow.png)

**Fix:** use the log rule (Lesson 00 §7): log(a × b) = log(a) + log(b). Instead of multiplying the probabilities, **add
their logs**:

$$\text{score}(c) = \ln P(c) + \sum_{w} \ln P(w\mid c)$$

Logs of numbers below 1 are negative, so the scores are negative numbers like −47 and −52 — **closer to 0 = more likely**.
They never underflow.

### Classify "free money" by hand (the toy model)

```
spam:  ln(0.5) + ln P(free|spam) + ln P(money|spam)
       = ln(0.5) + ln(3/16) + ln(2/16)
       = −0.693 + (−1.674) + (−2.079) = −4.446

ham:   ln(0.5) + ln(1/16) + ln(1/16)
       = −0.693 + (−2.773) + (−2.773) = −6.239

spam's score is closer to 0  →  SPAM
```

### From two scores back to a probability

The app shows "92 % spam", not "−4.446". The safe way (never leaving log space until the end):

$$P(\text{spam}) = \frac{1}{1 + e^{\,\text{score(ham)} - \text{score(spam)}}}$$

```
difference = −6.239 − (−4.446) = −1.793
e^(−1.793) = 0.166
P(spam) = 1 / (1 + 0.166) = 1 / 1.166 = 0.857      → 86 %
```

(Don't compute e^score for each class separately — that's the underflow again. And if the difference is above 700, the
answer is simply 0 or 1: `math.exp(710)` crashes.)

## 8. Watch a real message being classified

![word by word](figs/word_race.gif)

"URGENT! You have won a free prize. Call now to claim your cash award" → cleaned to `urgent free prize call claim cash
award`. Each word adds its log-probability to both scores (bars grow left); the gap between them is the evidence. Below:
each word's **vote**.

### Like a detective's belief meter

Here is P(spam) recomputed after **each** word, for a real spam SMS and a real customer SMS. Before any word, the belief is
the prior (13 %). Each clue moves it:

![belief after each word](figs/belief_meter.gif)

"winner" alone moves the spam message from 13 % to 87 %; by "network" it's certain. In the customer's message, "call" pushes
up a little (spam says "call" a lot!) — but "sorry", "later", "meeting" pull it straight back down.

## 9. The explanation comes for free — log-odds

Each word's vote is its **log-odds**:

$$\text{log-odds}(w) = \ln P(w\mid\text{spam}) - \ln P(w\mid\text{ham})$$

```
toy model:  log-odds(free) = ln(0.1875) − ln(0.0625) = −1.674 − (−2.773) = +1.10   → pushes to SPAM
            log-odds(meeting) = ln(1/16) − ln(3/16) = −1.10                           → pushes to HAM
```

![log-odds of words](figs/log_odds.png)

On the real data: *claim*, *prize*, *URLTOKEN* push hardest to spam; *later*, *lor*, *ask* to ham. These numbers **are**
the model — so the app can say *"flagged because of: claim (+5.6), prize (+5.4), a link (+4.5)"*. That's why Naive Bayes
is Laith's **main** model, even if the SVM (Lesson 14) were slightly more accurate.

## 10. How good is it on SMS it never saw?

Trained on 70 % of the real SMS and tested on the other 30 %:

![Naive Bayes on unseen SMS](figs/nb_result.png)

About **98 %** of unseen SMS are classified correctly at the 0.5 line. Notice the shape: almost every SMS is pushed to 0 or
to 1 — Naive Bayes is **over-confident** (the naive assumption counts "claim" and "prize" as two independent proofs). The
**order** is excellent; the exact percentages are not to be trusted, so Laith chooses the line on validation (Lesson 04).

## 11. Proving it is right

`test_matches_sklearn` trains scikit-learn's `MultinomialNB(alpha=1.0)` on the same data and demands the same answer to
9 decimal places.

| symptom | likely cause |
|---|---|
| way off everywhere | smoothing added on top but not at the bottom |
| right order, wrong values | forgot `+ α·|V|`, or the wrong |V| |
| right for short messages, wrong for long | left log space too early |
| wrong only with unknown words | smoothing unknown words at prediction time — skip them instead |

## 12. Common mistakes

| student says | the truth |
|---|---|
| "P(free \| spam) is the chance a 'free' message is spam" | That's P(spam \| free). The bar is not symmetric — remember the doctor. |
| "Unknown words should get a probability at prediction time" | Skip them: they'd add the same amount to both classes. |
| "NB's percentages are exact" | They are extreme (99.99 %) because of the naive assumption. The **order** is good; the threshold is chosen on validation (Lesson 04). |
| "Naive means stupid" | It means "makes a simplifying assumption". It's fast, explainable and hard to beat on short texts. |

## 🧪 Worked example: the toy model in Python

```python
import math
from collections import Counter

train = [(["free", "money", "now"], "spam"), (["free", "prize", "winner"], "spam"),
         (["meeting", "tomorrow", "office"], "ham"), (["project", "meeting", "notes"], "ham")]
vocab = {w for doc, _ in train for w in doc}
V, alpha = len(vocab), 1.0

log_prior, loglik = {}, {}
for c in ("spam", "ham"):
    docs = [d for d, y in train if y == c]
    log_prior[c] = math.log(len(docs) / len(train))
    counts = Counter(w for d in docs for w in d)
    total = sum(counts.values())
    loglik[c] = {w: math.log((counts[w] + alpha) / (total + alpha * V)) for w in vocab}   # Laplace

def scores(words):
    return {c: log_prior[c] + sum(loglik[c][w] for w in words if w in vocab) for c in ("spam", "ham")}

s = scores(["free", "money"])
print({c: round(v, 3) for c, v in s.items()})            # {'spam': -4.447, 'ham': -6.238}
print("P(spam) =", round(1 / (1 + math.exp(s["ham"] - s["spam"])), 3))   # 0.857
print("log-odds(free) =", round(loglik["spam"]["free"] - loglik["ham"]["free"], 2))   # 1.1
```

## 📝 Summary

> * **Bayes** = keep only the cases that match what you saw, then count: P(spam | free) = 174 ÷ 233 = 75 %.
> * posterior = likelihood × prior ÷ evidence — the **prior** matters (the doctor's test).
> * **Naive**: treat the words as independent → multiply their probabilities (wrong, but works for choosing).
> * **Training is counting**; **Laplace** (+1) stops one unseen word from killing a class.
> * Work in **logs**: add instead of multiply, so nothing underflows to 0.
> * Each word's **log-odds** is its vote — the model explains itself.

## 13. Activities

1. **The doctor (10 min).** Ask for guesses first, then count with 100,000 people on the board.
2. **Paper Naive Bayes (25 min).** 6 tiny messages (3 spam, 3 ham). Groups: priors, counts, smoothing, then classify
   "free meeting now" in log space with a calculator.
3. **Break it (10 min).** In the notebook: α = 0 and a message with one ham-only word; then multiply 300 probabilities
   without logs.
4. **Explain a verdict (5 min).** Pick a real SMS, read its top 3 log-odds as a sentence for Maya.

## 14. Do it yourself

<details><summary>1. Prior spam 0.2. "win" is in 30 % of spam and 2 % of ham. P(spam | win)? (Count with 1,000 messages.)</summary>

200 spam → 60 with "win"; 800 ham → 16 with "win". P = 60 / (60 + 16) = **0.79**.
</details>

<details><summary>2. Toy model: classify "meeting notes" (log space, every step).</summary>

spam: ln 0.5 + ln(1/16) + ln(1/16) = −0.693 − 2.773 − 2.773 = −6.239 · ham: ln 0.5 + ln(3/16) + ln(2/16) = −0.693 −
1.674 − 2.079 = −4.446 → **ham**.
</details>

<details><summary>3. Scores: ham −52.3, spam −47.1. P(spam)?</summary>

difference = −52.3 − (−47.1) = −5.2 · e^(−5.2) = 0.0055 · 1 / 1.0055 = **0.9945**.
</details>

<details><summary>4. 🟢 In the toy model, P(meeting | ham) with Laplace smoothing?</summary>

meeting appears 2 times in ham, total 6, |V| = 10 → (2 + 1) ÷ (6 + 10) = **3/16 = 0.1875**.
</details>

<details><summary>5. 🟡 The toy model sees "free lunch" — "lunch" is not in the vocabulary. What happens to "lunch"?</summary>

It is **skipped** — it would add the same amount to both classes anyway. The message is classified on "free" alone →
spam (log-odds +1.10).
</details>

<details><summary>6. 🟡 Log-odds of "winner" in the toy model?</summary>

spam: (1 + 1) ÷ 16 = 0.125 → ln = −2.079. ham: (0 + 1) ÷ 16 = 0.0625 → ln = −2.773. Log-odds = −2.079 + 2.773 = **+0.69** →
pushes to spam.
</details>

<details><summary>7. 🔴 Why doesn't Naive Bayes need feature scaling (Lesson 02)?</summary>

It never measures distances or walks downhill — it only counts words and compares probabilities. Multiplying all counts by
10 wouldn't change any probability.
</details>

## 15. In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/ml/naive_bayes.py` → `fit`, `predict_log_scores`, `predict_proba`, `predict`, `log_odds`, `explain`, `most_discriminative`, `to_dict/from_dict` · `ml/explainer.py` · config `laplace_alpha: 1.0` · theory `08_SpamClassifier/01_theory/04_naive_bayes.md` · notebook `02_naive_bayes_from_scratch.ipynb` |

## 🎬 Watch & explore

| | |
|---|---|
| <a href="https://www.youtube.com/watch?v=HZGCoVF3YvM"><img src="https://img.youtube.com/vi/HZGCoVF3YvM/mqdefault.jpg" width="240" alt="video"></a> | **3Blue1Brown — Bayes theorem, the geometry of changing beliefs** (15 min). The square picture of Part 2, beautifully animated. Watch first. |
| <a href="https://www.youtube.com/watch?v=O2L2Uv9pdDA"><img src="https://img.youtube.com/vi/O2L2Uv9pdDA/mqdefault.jpg" width="240" alt="video"></a> | **StatQuest — Naive Bayes, Clearly Explained!!!** (15 min). A spam filter with "Dear" and "Friend" — exactly Laith's model. |

**Play with it:**
* Seeing Theory — [Bayesian inference, interactive](https://seeing-theory.brown.edu/bayesian-inference/index.html)
* At home: run the worked example, add a third spam message and watch the log-odds change.
