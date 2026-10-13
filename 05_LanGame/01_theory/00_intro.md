# How to use this guide

This guide was written for you, Liraz, with one assumption: **you have not built a network
program or a multi-threaded program before.** Every idea is explained from zero, in simple
words, with a small example you can check by hand.

The guide has three parts:

- **Part A — Understand the problem.** What the system does, how two computers talk (IP, ports,
  TCP), what a protocol is, what threads are and why they are dangerous, what a state machine
  is, how the score is computed, and how the code is organized. Read this part **before** you
  write a single line of code. It takes one or two evenings.
- **Part B — Build the code.** Step by step, file by file: what to write, why, and how to know it
  works. This part goes together with `TASKS.md` in the code folder.
- **Part C — Pass the exam.** A bank of questions your supervisor or examiner may ask, with
  answers. After the code works, go over them until you can answer without looking.

Two rules for the whole way:

1. **Never copy code you do not understand.** In the defense you will be asked to explain every
   line. If you found a solution online or got it from an AI — read it, understand it, then write
   it again in your own words.
2. **Every number in the project book must come from a run on your own computer.** Latency,
   number of players, test results — all from your machine and your classroom network.

Symbols used:

- ❓ **Possible supervisor question** — a question you will probably get, and the answer you should know.
- 💡 **Tip** — a common mistake or a shortcut.
- 📄 **Code / example** — an example. Not always complete — sometimes just the idea.
- ✅ **Check yourself** — questions at the end of each chapter. Answers are in the appendix.

---

# Part A — Understand the problem

# Chapter 1 — What does the system do?

## 1.1 In one sentence

LanGame is a trivia game: one computer in the room is the **server**, every player runs a
**client**, everybody sees the same question at the same moment, and the fastest correct answer
gets the most points.

## 1.2 The journey of one question

Everything in the game happens in rounds. This is one round:

1. **The server** picks a question from the database and writes down the exact time.
2. **The server** sends the question (text + 4 options, **without** the correct answer) to every
   connected client, in one message each.
3. **Each client** shows the question, four buttons and a time bar.
4. **A player** clicks a button. The client sends one small message to the server: "question 17, choice 2".
5. **The server** receives it, looks at its own clock, computes how long the player took, and stores
   the answer. If a player tries to answer twice — the second one is rejected.
6. When the time limit ends (or everyone answered), **the server** computes points for everyone:
   correct and fast = many points; correct and slow = fewer; wrong = zero.
7. **The server** sends everyone the result (which option was right, who got how many points) and
   the leaderboard.
8. After a short pause — the next question. After the last one — "game over", and the whole game
   is saved to the database.

## 1.3 Who decides? The server, always.

Notice one thing in the journey: **the clients never decide anything.** They do not know the
correct answer. They do not measure time for scoring. They do not compute points. They only show
what the server sends and report what the player clicked.

This is called an **authoritative server**, and it is the most important design decision in the
project. Why:

- If every client computed its own score, two clients could disagree (different clocks, a lost
  message) — and there is no "truth".
- If the client knew the correct answer, a player could modify the client and cheat.
- If the client measured its own time, a player with a slow computer would be penalized for
  something that is not his fault — and a cheater could report "0.001 seconds".

❓ **Possible supervisor question: why does the client have a countdown bar if the server decides
when time is up?**
The bar is only for the player's eyes. It is a *display* of the time limit, started when the
question arrives. The server keeps its own timer, and it is the only one that closes the question.
If the two disagree by a few milliseconds, the server wins. The client never says "time is up" to anyone.

## 1.4 What you are really building

Three programs that share some code:

- `run_server.py` — **the server**. Runs on one machine. Accepts players, runs the game, computes
  scores, saves to the database. It has no window.
- `run_client.py` — **the player's app**. One per player. A Tkinter window that talks to the server.
- `run_admin.py` — **the teacher's tool**. Adds and edits questions, imports a CSV, shows past games.
  Talks to the database only, never to the server.

And the shared part, `langame/common/`: the **protocol** (what a message looks like) and the
**models** (what a question, a player, an answer look like). Both the client and the server import
it — that is how they agree on the language.

## 1.5 Two things that make this hard

Two problems appear the moment more than one player is connected:

- **Networking.** Messages travel as bytes through a cable or Wi-Fi. They can arrive glued together,
  cut in half, or not at all (a player closes the laptop). The program must handle every case.
- **Threads.** The server talks to 8 players at once. Waiting for player A must not block player B.
  So each player gets its own "worker" (a thread) — and 8 workers touching the same score table at
  the same time can corrupt it. The program must protect shared data.

Chapters 2–5 explain exactly these two things.
