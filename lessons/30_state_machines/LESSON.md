# Lesson 30 — Finite state machines: making illegal moves impossible

> **For:** Eran (the booking life cycle) · Liraz (the game server + scoring) &nbsp;·&nbsp; **Time:** 45 – 60 min
> **Before:** Python `Enum`, classes &nbsp;·&nbsp; **After this:** Lesson 32 (Liraz: the FSM under threads), Lesson 33 (transactions)

## 🎯 By the end, the student can

1. Define state, event, transition and guard, and draw the FSM of their own project.
2. Fill a transition table (state × event → new state or error), and write one guarded transition in code.
3. Explain why an FSM makes the program correct **and** testable.
4. (Liraz) Compute the time-based score; (Eran) explain how the state drives availability.

---

## 1. What a state machine is

A program that is always in **exactly one** of a few **states**, and moves between them only through defined
**transitions**, triggered by **events**, sometimes only if a **guard** (condition) is true.

**Analogy — a traffic light:** red → green → yellow → red. "Red → yellow" does not exist. Nobody needs to remember to
check it; there is simply no such arrow.

## 2. Eran: a booking's life cycle

![booking FSM](figs/booking_fsm.gif)

| from | event | guard | action | to |
|---|---|---|---|---|
| CONFIRMED | check in | today ≥ check-in date | stamp the time | CHECKED_IN |
| CHECKED_IN | check out | — | build the invoice (one transaction) | CHECKED_OUT |
| CONFIRMED | cancel | before check-in | compute the fee (0 or 1 night) | CANCELLED |

Anything else → a clear error saying **why** ("Cannot cancel: the guest has already checked in").

**The elegant part:** `BookingStatus.blocks_room` is True only for CONFIRMED and CHECKED_IN, and availability (Lesson 27)
asks nothing else. **Cancelling frees the room instantly** — no deletion, no special case, history kept.

## 3. Liraz: the game server

![game FSM](figs/game_fsm.gif)

![transition table](figs/transition_table.png)

Every command handler starts with one question — *"is this allowed in the current state?"* — and every arrow is one
method: `start_game`, `next_question`, `close_question`, `end_game`.

❓ *A player's ANSWER arrives 10 ms after the timer closed the question.* The timer already moved the state to SCORING →
`record_answer` replies `ERROR not_accepting`. The server's clock is the authority; 10 ms late is late.

## 4. A guarded transition in code

```python
def check_in(self, booking_id, today):
    booking = self._bookings.get(booking_id)
    if booking.status is not BookingStatus.CONFIRMED:                    # is this arrow allowed from here?
        raise BookingError(f"Cannot check in: the booking is {booking.status.value}")
    if today < booking.stay.check_in:                                    # the guard
        raise BookingError("Cannot check in before the arrival date")
    booking.status = BookingStatus.CHECKED_IN                            # the transition
    ...
```

(A sketch — your skeleton's docstrings define the exact names and messages.)

## 5. Why it makes the program correct and testable

* **Impossible situations become impossible:** an answer can't be scored twice — scoring only happens on the
  QUESTION → SCORING transition, which happens once.
* **Tests are simple:** put the engine in a state, send an event, check the new state and the reply. No sockets, no GUI.
* **The diagram in the book *is* the code:** every box is an `Enum` value, every arrow a method.

## 6. Liraz: time-based scoring

![scoring](figs/scoring.png)

```
points = round(1000 × (15 − t) / 15),  never below 100 for a correct answer;  wrong / none → 0
0 s → 1000      3 s → 800      7.5 s → 500      14.9 s → 7 → raised to 100
```

`t` is clamped to [0, 15] (a late answer that slips through must not give negative points) and measured with the
server's `time.monotonic()`. Leaderboard: sort by score, highest first; ties broken by **name** so the order doesn't jump
between broadcasts.

## 7. Misconceptions

| Student says | Truth |
|---|---|
| "I'll just use booleans: is_started, is_finished, …" | 3 booleans = 8 combinations, most of them nonsense ("finished but not started"). An enum has exactly the legal ones. |
| "Cancel = delete the row" | Change the state; history and invoices stay. |
| "The client knows when time is up" | The server decides; client clocks differ and can cheat. |
| "`round()` doesn't matter" | 800.0 in one place and 799 in another — `test_score_engine.py` pins exact numbers. |

## 8. Activities

1. **Human FSM (10 min).** Students hold state cards (LOBBY / QUESTION / SCORING / GAME_OVER). The teacher calls events;
   the "current state" student either passes the token along an arrow or shouts the error code.
2. **Fill the table (10 min).** Eran: draw the table for 4 states × 3 events (check in / check out / cancel) — which cells are
   errors, and what does each error say?
3. **Score by hand (5 min).** Correct at 1.5 s, 6 s, 12 s, wrong at 2 s → 900, 600, 200, 0.

## 9. Check yourself

<details><summary>1. A booking is CHECKED_OUT. The receptionist clicks "cancel". What happens and why?</summary>

Error: there is no arrow from CHECKED_OUT. The message says the stay is already finished. Nothing changes.
</details>

<details><summary>2. Correct answer at 13.2 s. Points?</summary>

1000 × 1.8 / 15 = 120 → **120** (above the floor of 100).
</details>

<details><summary>3. Why does cancelling need no change to the availability code?</summary>

Availability ignores bookings whose `status.blocks_room` is False — and CANCELLED is one of them.
</details>

## 10. In your project

| Project | Where |
|---|---|
| HotelManager | `hotelmanager/models/entities.py` → `BookingStatus.blocks_room`, `Booking.occupies` · `booking/hotel_service.py` → `create_booking`, `check_in`, `check_out`, `cancel` · `PricingEngine.cancellation_fee` · exercises ex11–ex13 · theory `18_HotelManager/01_theory/06_fsm.md` · notebook `04_state_machine.ipynb` |
| LanGame | `langame/server/game_engine.py` → `start_game`, `next_question`, `record_answer`, `close_question`, `end_game` · `server/score_engine.py` → `ScoreEngine.points_for`, `score_round` · `common/models.py` → `build_leaderboard` · theory `05_LanGame/01_theory/05_state_machine_scoring.md` · notebook `03_game_engine.ipynb` |

## 🎬 Watch & explore

* Computerphile — *Finite State Automata* — [search on YouTube](https://www.youtube.com/results?search_query=Computerphile+finite+state+automata)
* Refactoring Guru — [The State pattern](https://refactoring.guru/design-patterns/state)
* Game Programming Patterns (free online book) — [State](https://gameprogrammingpatterns.com/state.html)
