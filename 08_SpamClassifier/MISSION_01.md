# Mission 1 - How a computer decides that a message is spam

**Student:** Laith Halabi  ·  **Time:** two weeks  ·  **Ends with:** a 10-minute talk in class

You will explain the heart of your project to the class. To explain it you have to understand it, so the
mission has three parts: study, homework, talk.

## Part 1 - Study (first week)

In this order. Keep a notebook: every new word and every formula goes in it.

1. Lesson: [text preprocessing](../lessons/06_text_preprocessing/LESSON.md)
2. Lesson: [TF-IDF](../lessons/07_tfidf/LESSON.md)
3. Lesson: [Naive Bayes](../lessons/11_naive_bayes/LESSON.md)
4. Theory: [`03_features.md`](01_theory/03_features.md), [`04_naive_bayes.md`](01_theory/04_naive_bayes.md)
5. Notebook [`01_text_to_numbers.ipynb`](02_examples/01_text_to_numbers.ipynb): run every cell, then tokenize three real messages from the data and print the tokens.
6. Notebook [`02_naive_bayes_from_scratch.ipynb`](02_examples/02_naive_bayes_from_scratch.ipynb): run every cell, then find the 10 words that push hardest toward spam.

## Part 2 - Homework (hand in before your talk)

**A. Exercises.** In `03_exercises/exercises.py` write `ex03`, `ex05`, `ex08`, `ex09`, `ex10`. Check them:

```bash
cd 08_SpamClassifier/03_exercises
pytest test_exercises.py -k "ex03 or ex05 or ex08 or ex09 or ex10" -v
```

Open `solutions.py` only after your tests pass. In class you will explain one of them line by line.

**B. On paper.** Show every step - a final number alone gets no points. Bring the paper or a photo of it.

Train Naive Bayes by hand on four tiny messages (already tokenized), with Laplace alpha = 1:

| message | label |
|---|---|
| free win cash | spam |
| win prize now | spam |
| meet me now | ham |
| lunch now | ham |

1. How many different words are in the vocabulary? How many tokens in each class?
2. The prior of each class.
3. P(win | spam), P(now | spam), P(win | ham), P(now | ham) - with the formula written out.
4. The log score of each class for the new message **"win now"**, and P(spam).
5. Now the message is **"win now now"**. Does P(spam) go up or down? Explain why without computing first,
   then compute it.

**C. In your own words.** 3-5 sentences each.

1. Why is the method called *naive*? Give an example of two words where the naive idea is clearly false.
2. What happens to "win now" if alpha = 0? Why do we add up logs instead of multiplying probabilities?

## Part 3 - The talk (10 minutes + 5 minutes of questions)

Title: **How a computer decides that a message is spam**. Six slides at most, one idea each:

1. The problem and the data: how many messages, how many spam
2. From text to tokens to counts - one real message on the slide
3. Bayes' rule in one picture, and the naive assumption
4. Your paper example, worked on the board
5. Laplace smoothing and logs - what breaks without them
6. Live demo: notebook 02, the top spam words

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
