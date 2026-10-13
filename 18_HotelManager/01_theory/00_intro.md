# How to use this guide

This guide was written for you, Eran. It assumes you know basic Python (variables, `if`, loops,
functions, lists) and **nothing else**. Everything the project needs beyond that is explained here.

The guide has three parts:

- **Part A — Understand what you are building** (chapters 1–8). The four algorithms, why each one
  exists, and a worked example for each that you can redo on paper. Read this **before** writing code.
- **Part B — Build it** (chapters 10–17). Numbered steps: what to type, what to run, what you should
  see, and what to do when you do not see it.
- **Part C — Defend it** (chapters 18–20). Seventy-five questions with answers, "explain your code"
  drills, and a glossary.

**Why Part A first.** This project is judged on its *algorithms*. A student who can run the program
but cannot explain why `[3,7)` and `[7,9)` do not collide will fail the defense. A student who
understands the four algorithms can rebuild the program from scratch.

Symbols: ❓ a question the examiner may ask · 💡 a tip or a common trap · 📄 code or a worked example ·
✅ check yourself (answers in the appendix).

Two rules for the whole year:

1. **Never write code you cannot explain.** If you copy something from the internet or from an AI,
   read it, understand it, then write it again in your own words. In the defense you will be asked
   about a random line.
2. **Every number in the project book comes from a run on your computer** — a test output, a report,
   a measurement. Not from this guide.

---

# Part A — Understand what you are building

# Chapter 1 — What the system does

## 1.1 In one sentence

HotelManager is the program at the reception desk of a small hotel: it knows which rooms are free on
which dates, chooses the best room for each guest, calculates the price, and follows the booking from
"confirmed" to "checked out" with an invoice.

## 1.2 One working day

```
09:00  A guest phones: "a double room, 3 to 7 March, two people."
       You type the dates -> the program lists the free doubles WITH the price for those dates.
09:02  You pick room 102 -> Book. The booking is CONFIRMED and the room is taken for those nights.
14:00  The guest arrives -> Check in. The booking becomes CHECKED_IN.
       (If they had arrived on 1 March, the program would refuse: "check-in is on 3 March".)
07/03  The guest leaves -> Check out. An invoice is produced, line by line, and the room is free again.
       The calendar tab shows the whole month: every room a row, every day a square.
```

## 1.3 The four questions behind it

Everything in this project is one of four questions. They are your four algorithms:

| # | Question | Algorithm | Chapter |
|---|---|---|---|
| 1 | Is this room free on these dates? | interval overlap | 3 |
| 2 | Which free room should this guest get? | allocation with a cost function | 4 |
| 3 | What does this stay cost, and why? | a chain of pricing rules | 5 |
| 4 | Which actions are allowed on this booking now? | a finite state machine | 6 |

Everything else — tables, forms, buttons — exists to feed these four and to show their answers.

## 1.4 Why the examiner cares about this distinction

The Ministry rejects final projects that are "a database with forms". Your proposal, section 4, names
the four algorithms, their complexity and the alternatives you rejected. Your job is to be able to
speak that section out loud. That is what Part A of this guide trains.

💡 Write this sentence on the first page of your notebook and use it in the defense:
*"The user interface serves the algorithms; the algorithms are the project."*
