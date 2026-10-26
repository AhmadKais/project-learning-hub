# Mission 1 - Reading a URL like an attacker

**Student:** Dani Faris  ·  **Time:** two weeks  ·  **Ends with:** a 10-minute talk in class

You will explain the heart of your project to the class. To explain it you have to understand it, so the
mission has three parts: study, homework, talk.

## Part 1 - Study (first week)

In this order. Keep a notebook: every new word and every formula goes in it.

1. Lesson: [URL features and entropy](../lessons/18_url_features_entropy/LESSON.md)
2. Lesson: [the confusion matrix](../lessons/03_confusion_matrix_metrics/LESSON.md)
3. Lesson: [thresholds and ROC](../lessons/04_threshold_roc/LESSON.md)
4. Theory: [`03_features.md`](01_theory/03_features.md), [`05_evaluation.md`](01_theory/05_evaluation.md)
5. Notebook [`01_url_features.ipynb`](02_examples/01_url_features.ipynb): run every cell, then extract the features of 3 phishing and 3 real URLs and compare them.
6. Notebook [`03_threshold_roc_mistakes.ipynb`](02_examples/03_threshold_roc_mistakes.ipynb): run every cell, then move the threshold and watch precision and recall change.

## Part 2 - Homework (hand in before your talk)

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

## Part 3 - The talk (10 minutes + 5 minutes of questions)

Title: **Reading a URL like an attacker**. Six slides at most, one idea each:

1. The problem: a link arrives - is it phishing? A real example
2. Reading the host from the right: your paper example
3. Five features and why each one catches attackers (entropy with your numbers)
4. Precision and recall in one picture
5. Choosing the threshold: your table on the board
6. Live demo: notebook 01 on a URL from the class

Rules: no slide full of text, no code copied from the solution. Draw on the board where you can.
After the talk I ask one question from [`17_exam.md`](05_defence/17_exam.md) and one about
your paper task.

## How it is graded

| Part | Points |
|---|---|
| A. exercises pass and you can explain them | 25 |
| B. paper task correct, every step shown | 25 |
| C. answers in your own words | 10 |
| The talk: correct, clear, on time | 25 |
| Answers to the questions | 15 |
