# Mission 1 - Never double-book a room

**Student:** Eran Nijm  ·  **Time:** two weeks  ·  **Ends with:** a 10-minute talk in class

You will explain the heart of your project to the class. To explain it you have to understand it, so the
mission has three parts: study, homework, talk.

## Part 1 - Study (first week)

In this order. Keep a notebook: every new word and every formula goes in it.

1. Lesson: [intervals and overlap](../lessons/27_intervals_overlap/LESSON.md)
2. Lesson: [allocation strategies](../lessons/28_allocation_strategies/LESSON.md)
3. Lesson: [state machines](../lessons/30_state_machines/LESSON.md)
4. Theory: [`03_intervals.md`](01_theory/03_intervals.md), [`04_allocation.md`](01_theory/04_allocation.md), [`05_pricing.md`](01_theory/05_pricing.md), [`06_fsm.md`](01_theory/06_fsm.md)
5. Notebook [`01_intervals.ipynb`](02_examples/01_intervals.ipynb): run every cell, then try the four ways two stays can touch and print overlap for each.
6. Notebook [`02_allocation.ipynb`](02_examples/02_allocation.ipynb): run every cell, then run first-fit and best-fit on the same requests and compare.

## Part 2 - Homework (hand in before your talk)

**A. Exercises.** In `03_exercises/exercises.py` write `ex01`, `ex02`, `ex03`, `ex05`, `ex06`, `ex11`. Check them:

```bash
cd 18_HotelManager/03_exercises
pytest test_exercises.py -k "ex01 or ex02 or ex03 or ex05 or ex06 or ex11" -v
```

Open `solutions.py` only after your tests pass. In class you will explain one of them line by line.

**B. On paper.** Show every step - a final number alone gets no points. Bring the paper or a photo of it.

The hotel (rates per night: single 320, double 450, family 620, suite 900):

| room | type | capacity | booked |
|---|---|---|---|
| 101 | single | 1 | 3 Nov - 5 Nov 2026 |
| 102 | double | 2 | 4 Nov - 6 Nov 2026 |
| 201 | family | 4 | 8 Nov - 10 Nov 2026 |
| 202 | suite | 3 | 1 Nov - 4 Nov 2026 |

A request: **2 guests, check-in Thursday 5 Nov, check-out Sunday 8 Nov 2026.**

1. For every room, write the overlap test with the real dates and say if it is free. Which rooms can take
   the request?
2. Which room does **first-fit** choose, and which does **best-fit** choose? Which one is better for the hotel?
3. The guests take room 202 with breakfast. Rules: Friday and Saturday nights cost 20% more, breakfast is 55
   per guest per night, VAT is 18%. Write the invoice line by line and the total.
4. They cancel on 3 Nov at 10:00 - what is the fee? And on 4 Nov at 09:00? (Free until 48 hours before 14:00
   on the check-in day, otherwise one night.) Can a booking that is already CHECKED_OUT be cancelled?

**C. In your own words.** 3-5 sentences each.

1. Why are stays stored as half-open ranges [check-in, check-out)? What goes wrong with closed ranges?
2. Why is the price built from a chain of small rules instead of one big function?

## Part 3 - The talk (10 minutes + 5 minutes of questions)

Title: **Never double-book a room**. Six slides at most, one idea each:

1. The problem: what a double booking costs a hotel
2. Half-open intervals and the two-comparison overlap test - the paper example
3. First-fit against best-fit: same request, different room
4. The pricing chain: your invoice, rule by rule
5. The booking state machine and the cancellation rule
6. Live demo: notebook 01 or 02

Rules: no slide full of text, no code copied from the solution. Draw on the board where you can.
After the talk I ask one question from [`18_exam.md`](05_defence/18_exam.md) and one about
your paper task.

## How it is graded

| Part | Points |
|---|---|
| A. exercises pass and you can explain them | 25 |
| B. paper task correct, every step shown | 25 |
| C. answers in your own words | 10 |
| The talk: correct, clear, on time | 25 |
| Answers to the questions | 15 |
