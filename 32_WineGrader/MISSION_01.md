# Mission 1 - Judging a wine by its neighbours

**Student:** Seif Ferro  ·  **Time:** two weeks  ·  **Ends with:** a 10-minute talk in class

You will explain the heart of your project to the class. To explain it you have to understand it, so the
mission has three parts: study, homework, talk.

## Part 1 - Study (first week)

In this order. Keep a notebook: every new word and every formula goes in it.

1. Lesson: [feature scaling](../lessons/02_feature_scaling/LESSON.md)
2. Lesson: [k-nearest neighbours](../lessons/15_knn/LESSON.md)
3. Theory: [`03_data_scaling.md`](01_theory/03_data_scaling.md), [`04_knn.md`](01_theory/04_knn.md)
4. Notebook [`01_data_and_scaling.ipynb`](02_examples/01_data_and_scaling.ipynb): run every cell, then print the range of every column before and after scaling.
5. Notebook [`02_knn_from_scratch.ipynb`](02_examples/02_knn_from_scratch.ipynb): run every cell, then change k from 1 to 25 and plot the accuracy.

## Part 2 - Homework (hand in before your talk)

**A. Exercises.** In `03_exercises/exercises.py` write `ex03`, `ex05`, `ex06`, `ex07`, `ex08`. Check them:

```bash
cd 32_WineGrader/03_exercises
pytest test_exercises.py -k "ex03 or ex05 or ex06 or ex07 or ex08" -v
```

Open `solutions.py` only after your tests pass. In class you will explain one of them line by line.

**B. On paper.** Show every step - a final number alone gets no points. Bring the paper or a photo of it.

Five wines with two features (grade 0 = low, 1 = medium, 2 = high):

| wine | alcohol | volatile acidity | grade |
|---|---|---|---|
| W1 | 9.0 | 0.70 | 0 |
| W2 | 10.0 | 0.60 | 1 |
| W3 | 11.0 | 0.40 | 1 |
| W4 | 12.0 | 0.30 | 2 |
| W5 | 13.0 | 0.50 | 2 |

A new wine: alcohol 11.5, volatile acidity 0.45.

1. The z-score parameters: the mean and the standard deviation of each column (divide by n, like numpy).
2. Scale the five wines and the new one. The Euclidean distance from the new wine to each.
3. The 3 nearest neighbours. Each one votes 1 / distance. Which grade wins? What would a plain majority
   vote say?
4. True grades `0 0 1 1 1 1 2 2`, predicted `0 1 1 1 0 1 2 1`. Draw the confusion matrix and compute the
   macro-F1.

**C. In your own words.** 3-5 sentences each.

1. Why must the features be scaled before k-NN? What would volatile acidity count for without scaling?
2. k-NN is called a *lazy* learner. What does it do when it trains, and what does it pay for that later?

## Part 3 - The talk (10 minutes + 5 minutes of questions)

Title: **Judging a wine by its neighbours**. Six slides at most, one idea each:

1. The problem: grade a wine from its chemistry - the data
2. Distance between two wines, and why scaling comes first
3. Your paper example on the board: neighbours and the weighted vote
4. Choosing k: too small, too big
5. Measuring it honestly: the confusion matrix and macro-F1
6. Live demo: notebook 02, accuracy against k

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
