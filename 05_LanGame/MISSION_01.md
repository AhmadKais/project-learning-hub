# Mission 1 - How 8 computers play one quiz

**Student:** Liraz Dakseh  ·  **Time:** two weeks  ·  **Ends with:** your paper task solved at the board

The heart of your project, studied properly: read and run, write the exercises, solve a real example by
hand, and show it at the board.

## Part 1 - Study (first week)

In this order. Keep a notebook: every new word and every formula goes in it.

1. Lesson: [TCP and message framing](../lessons/31_tcp_framing/LESSON.md)
2. Lesson: [threads and locks](../lessons/32_threads_locks/LESSON.md)
3. Lesson: [state machines](../lessons/30_state_machines/LESSON.md)
4. Theory: [`02_networks.md`](01_theory/02_networks.md), [`03_sockets_protocol.md`](01_theory/03_sockets_protocol.md), [`04_threads.md`](01_theory/04_threads.md), [`05_state_machine_scoring.md`](01_theory/05_state_machine_scoring.md)
5. Notebook [`01_tcp_stream_and_framing.ipynb`](02_examples/01_tcp_stream_and_framing.ipynb): run every cell, then send two messages in one `sendall` and watch them arrive glued together.
6. Notebook [`02_threads_and_locks.ipynb`](02_examples/02_threads_and_locks.ipynb): run every cell, then remove the lock and run the counter cell five times.

## Part 2 - Homework (hand in at the end of the two weeks)

**A. Exercises.** In `03_exercises/exercises.py` write `ex01`, `ex02`, `ex06`, `ex07`, `ex12`. Check them:

```bash
cd 05_LanGame/03_exercises
pytest test_exercises.py -k "ex01 or ex02 or ex06 or ex07 or ex12" -v
```

Open `solutions.py` only after your tests pass. In class you will explain one of them line by line.

**B. On paper.** Show every step - a final number alone gets no points. Bring the paper or a photo of it.

**1. Points.** The time limit is 15 seconds, a correct answer is worth at most 1000 points and never
less than 100, a wrong answer is worth 0. Write the formula, then work out the points for: correct after
3.0 s, correct after 7.5 s, correct after 14.5 s, wrong after 1.0 s.

**2. Framing.** Every message ends with a newline (`\n`). The server calls `recv()` twice and gets:

```text
recv 1:  {"type": "ANSWER", "payload": {"question_id": 4, "choice": 2}}\n{"type": "ANS
recv 2:  WER", "payload": {"question_id": 4, "choice": 0}}\n
```

After `recv 1`: how many complete messages can the server read, and what is left in its buffer?
After `recv 2`? Why is `json.loads(data)` on each `recv()` wrong?

**3. A lost update.** `score` starts at 0. Thread A runs `score = score + 800`, thread B runs
`score = score + 500`. Each line is really three steps: read, add, write. Draw a table of the steps
(one row per step, a column per thread) where the final score is 500 instead of 1300. Then show where the
lock goes and why it fixes it.

**4. The game.** Draw the state machine of a game: the states `LOBBY`, `QUESTION`, `SCORING`,
`GAME_OVER`, and every arrow labelled with what makes it happen.

**C. In your own words.** 3-5 sentences each.

1. Why does the game use TCP and not UDP? Give one thing that would go wrong with UDP.
2. Every client gets its own thread on the server. What would happen with one thread for everyone?

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
