# Mission 1 - Reading a URL like an attacker

**Student:** Dani Faris  ·  **Time:** two weeks  ·  **Ends with:** your paper task solved at the board

The heart of your project, studied properly: read and run, write the exercises, solve a real example by
hand, and show it at the board.

## Part 1 - Study (first week)

In this order. Keep a notebook: every new word and every formula goes in it.

1. Lesson: [URL features and entropy](../lessons/18_url_features_entropy/LESSON.md)
2. Lesson: [the confusion matrix](../lessons/03_confusion_matrix_metrics/LESSON.md)
3. Lesson: [thresholds and ROC](../lessons/04_threshold_roc/LESSON.md)
4. Theory: [`03_features.md`](01_theory/03_features.md), [`05_evaluation.md`](01_theory/05_evaluation.md)
5. Notebook [`01_url_features.ipynb`](02_examples/01_url_features.ipynb): run every cell, then extract the features of 3 phishing and 3 real URLs and compare them.
6. Notebook [`03_threshold_roc_mistakes.ipynb`](02_examples/03_threshold_roc_mistakes.ipynb): run every cell, then move the threshold and watch precision and recall change.

## Part 2 - Homework (hand in at the end of the two weeks)

**A. Exercises.** In `03_exercises/exercises.py` write `ex01`, `ex03`, `ex10`, `ex11`. Check them:

```bash
cd 25_PhishGuard/03_exercises
pytest test_exercises.py -k "ex01 or ex03 or ex10 or ex11" -v
```

Open `solutions.py` only after your tests pass. In class you will explain one of them line by line.

**B. On paper.** Show every step - a final number alone gets no points. Bring the paper or a photo of it.

**1. Who owns the link?** Split each host into subdomains, domain and TLD (read from the right).
Who really owns it?
- `mail.paypal.com.account-check.xyz`
- `www.bank.co.il`

**2. Entropy.** Compute the Shannon entropy (bits) of `paypal` and of `x7k2q9`. Show the count and the
probability of every character. Which one looks random, and why do attackers' URLs often score high?

**3. The threshold.** A model gave these phishing probabilities (y = 1 means really phishing):

| p | 0.95 | 0.90 | 0.80 | 0.75 | 0.60 | 0.55 | 0.40 | 0.30 | 0.20 | 0.10 |
|---|---|---|---|---|---|---|---|---|---|---|
| y | 1 | 1 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 |

a. At threshold 0.5: recall and precision.
b. The **highest** threshold whose recall is at least 0.8, and the precision there.
c. The highest threshold that catches **every** phishing URL, and the precision there.

**C. In your own words.** 3-5 sentences each.

1. Why is the threshold chosen on the validation split and never on the test split?
2. In PhishGuard, which mistake is worse - a missed phishing link or a false alarm? What does each one cost?

## Part 3 - At the board (5 minutes)

In class you solve your paper task (part B) on the board, in front of everyone, explaining each step.
Then I ask one question from [`17_exam.md`](05_defence/17_exam.md) and the class may ask one.

## How it is graded

| Part | Points |
|---|---|
| A. exercises pass and you can explain them | 30 |
| B. paper task correct, every step shown | 30 |
| C. answers in your own words | 15 |
| At the board: the paper task explained clearly | 15 |
| Answer to the question | 10 |
