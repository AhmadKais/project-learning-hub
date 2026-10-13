# Chapter 5 — The state machine and the scoring

## 5.1 What a state machine is

A **finite state machine** (FSM) is a way to describe a program that is always in exactly one of a
few *states*, and moves between them only through defined *transitions*. A traffic light: states
red / green / yellow; transitions on a timer; "red → green" is allowed, "red → yellow" is not.

LanGame's server is an FSM with four states:

📄 **The game's states and transitions**
```text
                    START_GAME (host, >= 2 players)
        LOBBY  ───────────────────────────────────▶  QUESTION
          ▲                                             │
          │ reset                    time up / all answered
          │                                             ▼
      GAME_OVER  ◀───── last question ─────────────  SCORING
                                                        │
                                   more questions ──────┘  (back to QUESTION)
```

| State | What is allowed | What is rejected |
|---|---|---|
| LOBBY | JOIN, LEAVE, START_GAME (host) | ANSWER → `not_accepting` |
| QUESTION | ANSWER (once per player), LEAVE | JOIN → `game_started`, second ANSWER → `already_answered` |
| SCORING | LEAVE | ANSWER → `not_accepting` (too late) |
| GAME_OVER | LEAVE | everything else |

## 5.2 Why an FSM makes the server correct and testable

Without the FSM, the rules are scattered `if`s: "if the game started and the question is not
closed and the player has not answered and ...". With the FSM, every command starts with one
question — *"am I allowed in this state?"* — and every transition is one method
(`start_game`, `next_question`, `close_question`, `end_game`). Three benefits:

- **Impossible situations become impossible.** An answer cannot be scored twice because scoring
  only happens on the QUESTION → SCORING transition, which happens once.
- **Tests are simple.** Put the engine in a state, send a command, check the state and the reply.
  `tests/test_game_engine.py` does exactly this — no sockets needed.
- **The diagram in the book is the code.** Every arrow is a method; every box is a value of `GameState`.

❓ **Possible supervisor question: a player's ANSWER arrives 10 ms after the timer closed the
question. What happens?**
The timer moved the state to SCORING. `record_answer` checks `state != QUESTION` first and replies
`ERROR not_accepting`. The answer is not scored — the server's clock is the authority, and "10 ms
late" is late. The client shows "too late". Nothing else changes.

## 5.3 Timing inside a round

📄 **One round on the server's clock**
```text
t = 0.000   next_question(): state = QUESTION, question_sent_at = monotonic(), broadcast QUESTION,
            Timer(15.0, close_question).start()
t = 2.310   ANSWER from A arrives -> response_time = 2.310, stored
t = 5.874   ANSWER from B arrives -> response_time = 5.874, stored
t = 5.874   all connected players answered -> close_question() early; timer.cancel()
            state = SCORING, score_round(), broadcast RESULT + LEADERBOARD
            Timer(4.0, next_question).start()
t = 9.874   next_question() ...
```

If B never answers, the 15-second timer calls `close_question()` at t = 15.000 and B gets 0.

## 5.4 The scoring formula

📄 **Points for a correct answer**
```text
points = round( MAX_POINTS * (time_limit - response_time) / time_limit )
         but never less than MIN_POINTS_CORRECT (100) for a correct answer
wrong answer or no answer: 0

with MAX_POINTS = 1000, time_limit = 15:
   response 0.0 s  ->  1000 * 15.0 / 15 = 1000
   response 3.0 s  ->  1000 * 12.0 / 15 =  800
   response 7.5 s  ->  1000 *  7.5 / 15 =  500
   response 14.9 s ->  1000 *  0.1 / 15 =    7  ->  raised to 100
   wrong           ->                            0
```

Why linear: simple to explain and to feel — "every second costs about 67 points". Why the
minimum of 100: a correct answer should always beat a wrong one, even a slow correct answer.
Why clamp `response_time` to `[0, time_limit]`: a late answer that somehow slips through must not
produce negative points.

💡 A common bug: computing with integer division or forgetting `round()`, so 800.0 becomes 800
in one place and 799 in another. `tests/test_score_engine.py` pins the exact numbers.

## 5.5 The leaderboard

Sort players by score, highest first; ties broken by name so the order is stable between
broadcasts (a leaderboard that reorders tied players every round looks broken). Rank is the
position, starting at 1. Disconnected players stay on the board — they played.

## 5.6 Picking questions without repeats — and efficiently

The naive way, `SELECT * FROM questions ORDER BY RANDOM() LIMIT 1`, has two problems: it can pick
the same question twice in a game, and with thousands of rows it sorts the whole table for every
question.

The efficient way (`QuestionManager`): at game start, `SELECT id FROM questions WHERE category=?`
— just the ids, a few KB even for 10,000 questions. Shuffle the list in Python (`random.shuffle`),
keep the first N. For each round, `SELECT ... WHERE id=?` — a primary-key lookup, microseconds.
No repeats by construction, and the DB does one cheap query per round.

## ✅ Check yourself — Chapter 5

1. Compute the points for a correct answer at 6.0 s, 12.0 s and 15.0 s (time limit 15).
2. The host presses Start with only one player connected. Which state is the engine in
   afterwards, and what does the host receive?
3. Player C disconnects during QUESTION, before answering. List what changes in the engine and
   what the other players see. Does the round close early? Under what condition?
4. Draw (or list) the sequence of states for a 2-question game from the first JOIN to the reset.
5. Why is `close_question` scheduled with a `Timer` instead of a `time.sleep(15)` inside
   `next_question`?
6. The DB has 6 questions in category "networks" and the game needs 10. What should `prepare()`
   do, and why is doing it at game start better than discovering it at question 7?

## 📚 Further reading — Chapter 5

- **Refactoring Guru — State pattern**: https://refactoring.guru/design-patterns/state — the OOP
  version of a state machine; ours is the simpler enum + methods form, but the idea is the same.
- **Python docs — enum**: https://docs.python.org/3/library/enum.html
- **Python docs — time.monotonic**: https://docs.python.org/3/library/time.html#time.monotonic
- **Python docs — random.shuffle**: https://docs.python.org/3/library/random.html#random.shuffle
