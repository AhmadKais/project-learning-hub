# Part C — Defend it

# Chapter 18 — Seventy-five questions with answers

Go over these **after** the code works. Answer in two to four sentences and **point at the file and the
function**. "That happens in `hotel_service.py`, in `check_in`, the second `if`" beats any definition.

## 18.1 The project as a whole

**1. What does the system do, in one sentence?** It manages a small hotel's bookings: which rooms are
free on which dates, which room each guest gets, what the stay costs, and the booking's life cycle
from confirmed to checked out with an invoice.

**2. Why is this not a CRUD project?** Because four algorithms decide everything: interval overlap,
room allocation with a cost function, a pricing rule chain and a finite state machine. The forms only
feed them.

**3. Which four algorithms, and where?** `models/date_range.py` (overlap), `booking/allocation.py`
(allocation), `pricing/rules.py` + `engine.py` (pricing), `booking/hotel_service.py` (state machine).

**4. What is the hardest bug this system could have?** A double booking — selling the same room twice.
That is why the overlap rule has its own eight tests.

**5. Who are the users?** The receptionist (bookings, check-in/out) and the manager (rooms, seasons,
reports).

## 18.2 Algorithm 1 — intervals

**6. What does `[3, 7)` mean?** A stay from 3 March to 7 March: the guest sleeps on the 3rd, 4th, 5th
and 6th — four nights — and leaves on the 7th, which is not counted.

**7. How many nights is 10 → 14 March?** Four: 10, 11, 12, 13.

**8. The overlap rule?** `a < d and c < b` — two comparisons for the ranges `[a,b)` and `[c,d)`.

**9. Prove it.** They do not overlap only if `b ≤ c` or `d ≤ a`; negating with De Morgan gives
`b > c and d > a`, which is `c < b and a < d`.

**10. Why `<` and not `<=`?** So a guest may arrive on the day the previous one leaves. With `<=` the
hotel would refuse a legitimate booking every day.

**11. Show the six overlapping cases.** [Draw the diagram from guide 3.4.]

**12. Which two cases are *not* overlaps?** One range ends exactly when the other starts (both directions).

**13. Why is `DateRange` frozen?** It is a value; if the dates could change after an availability check,
the check would become silently wrong. Frozen makes that bug impossible.

**14. Where is an invalid range rejected?** In `__post_init__`, at creation — so no function anywhere
else has to check.

**15. Complexity of one comparison?** O(1).

**16. Complexity of "is this room free?"** O(k), where k is the number of bookings that overlap the
requested period — because `in_period` filters in SQL using the same rule, and the index
`(room_id, check_in, check_out)` makes it a range scan.

**17. What would it be without that query?** O(n) over every booking ever made.

**18. What is Allen's interval algebra?** The 13 possible relations between two intervals (1983); six
of them are overlaps. Our two comparisons decide all 13.

**19. What alternative design did you reject?** One row per night. It costs 14 rows for a 14-night
booking and makes date changes expensive; the interval comparison stores one row and decides in O(1).

**20. Where is the rule used besides availability?** The calendar (`Booking.occupies`) and the SQL in
`in_period`.

## 18.3 Algorithm 2 — allocation

**21. Why not give the couple the family room?** Because the family that calls next has nowhere to
sleep — a lost booking and two wasted beds.

**22. The three strategies?** First-Fit (lowest number), Best-Fit (smallest that fits, then cheaper,
then lower number), Preference (a weighted score of view, floor, type minus wasted beds).

**23. Which does Best-Fit choose from 102 (2 beds), 201 (2 beds), 301 (4 beds) for two guests?** 102 —
same capacity and price as 201, lower number.

**24. What does the key tuple `(capacity, rate, number)` mean?** Compare capacity first; on a tie,
price; on a tie, room number — so every tie has a defined winner.

**25. Why does determinism matter?** Tests can assert a specific room, and two identical requests
never produce different results.

**26. What does `choose` return when nothing fits?** `None` — and `create_booking` turns that into
"No free room for N guests on those dates".

**27. Which pattern is this?** Strategy, with a Factory (`allocation.create`) that turns the config
string into an object.

**28. How would you add a fourth strategy?** One class implementing `choose`, one entry in
`_STRATEGIES`. Nothing else changes — that is the point.

**29. Where else is Best-Fit used in computing?** Memory allocators and bin packing.

**30. What did your experiment measure?** Requests served, average wasted beds and revenue for the same
30 requests under each strategy. [Give your numbers.]

## 18.4 Algorithm 3 — pricing

**31. Why is the price not a column?** Because it depends on the dates, the season, the day of the
week, the length of stay and the extras — and it must be explainable line by line.

**32. The five rules, in order?** Base (× season), weekend surcharge, long-stay discount, extras, VAT.

**33. Why must the discount run after the weekend rule?** It takes 10% of the lines so far; if it ran
first there would be nothing to discount.

**34. Why must VAT be last?** It is charged on everything above it.

**35. Compute a 7-night stay, double 450, Mon 2 → Mon 9 March 2026, 2 guests, breakfast.**
3,150 + 180 − 333 + 770 = 3,767 subtotal; VAT 678.06; total **4,445.06**.

**36. Which nights got the surcharge there, and why?** 6 and 7 March — Friday and Saturday, decided per
night with `weekday() in config.WEEKEND_DAYS`.

**37. How does a season change the price?** It multiplies the room rate for the nights it covers — and
the weekend surcharge is then computed on the seasonal price.

**38. Why is the discount a negative line?** So the invoice adds up exactly as the guest reads it, and
the total is always `sum(lines)`.

**39. What is `lines_so_far` for?** It lets a rule react to what earlier rules produced — the discount
needs it.

**40. What is the open/closed principle, and where do you obey it?** Open for extension, closed for
modification: a new discount is one class plus one line in the rule list.

**41. Complexity?** O(L·S) — nights × rules; at most 150 operations.

**42. What alternative did you reject?** One `calculate_price()` with nested `if`s — unreadable and
unexplainable.

**43. Where does the cancellation fee live and why?** In `PricingEngine.cancellation_fee`, because it is
a price and all prices live in one place.

**44. How are equal nights grouped?** A dict `price → count`, then one line per distinct price.

**45. Why round once?** Rounding in two places makes the lines and the total disagree by agorot.

## 18.5 Algorithm 4 — the state machine

**46. The four states?** CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED.

**47. The three legal transitions and their guards?** [The table in guide 6.2.]

**48. What happens if you check out a booking that was never checked in?** `HotelError("Only a
checked-in booking can be checked out")` — the state guard in `check_out`.

**49. Can you cancel a guest who is already in the room?** No — `cancel` requires CONFIRMED.

**50. How does cancelling free the room?** `BookingStatus.blocks_room` is False for CANCELLED, and
`is_room_free` skips bookings that do not block. One property, no special case.

**51. Why does `check_in` take a `today` parameter?** So tests can simulate a date; the default is the
real today.

**52. What is stamped on each transition?** `checked_in_at` / `checked_out_at`, for the history and the
reports.

**53. Why is the invoice written in one transaction?** So a failure halfway cannot leave an invoice
with missing lines — atomicity.

**54. What is a guard?** The condition that must hold for a transition to be allowed.

**55. Why an FSM instead of `if`s spread around?** Because illegal moves become impossible in one place,
and the diagram in the book matches the code one to one.

## 18.6 Database and architecture

**56. Name three CHECK constraints and what they prevent.** [Guide 7.2.]

**57. RESTRICT vs CASCADE here?** RESTRICT stops deleting a room that has bookings; CASCADE deletes
invoice lines with their invoice.

**58. Why `PRAGMA foreign_keys = ON`?** SQLite disables foreign keys by default, so RESTRICT and
CASCADE would silently do nothing.

**59. Why are dates stored as ISO text?** SQLite has no date type, and ISO text sorts chronologically.

**60. What is the Repository pattern and what does it buy you?** All SQL in one file; the rules are
testable without a database engine; changing database touches one file.

**61. Why `?` placeholders?** Correctness (a name with an apostrophe) and security (SQL injection).

**62. What is `HotelService`?** A Facade: the UI calls one method and the service performs the checks in
the right order.

**63. How do you prove the layers are separated?** `grep` for tkinter in the logic packages and for the
service in the views — both print nothing.

**64. Why can you test a GUI application with pytest?** Because none of the rules live in the GUI; the
tests drive `HotelService` directly.

**65. Where is the Singleton and why?** `Database` — one connection factory and one file path for the
whole program.

**66. What does `in_period` return and why not `list_all`?** Only the bookings overlapping the period —
the O(k) optimisation.

**67. Why does the booking SELECT join rooms and guests?** So the table can display names without one
extra query per row (the N+1 problem).

**68. What is `config.py` for?** Every business number in one place: rates, VAT, policies, weekend days.

## 18.7 Testing, limits and the future

**69. How many tests, and what do they cover?** 47: the interval rule (8 cases), repositories,
availability and the three strategies, the pricing numbers, and the whole life cycle including illegal
moves.

**70. Which test is the most important, and why?** The overlap cases — they prevent double bookings.

**71. What is *not* tested automatically, and how did you check it?** The Tkinter screens and the
calendar drawing; tested by hand, with screenshots in the book.

**72. Name three limitations of the system.** Single user on one computer; no online payments; seasons
and rules are entered by hand.

**73. What would you build next?** [Two items from the proposal's future work, with reasons.]

**74. What was the hardest problem, and how did you solve it?** [Yours — from `TASKS.md`.]

**75. If the hotel doubled to 200 rooms, what would you change?** Nothing structural: allocation is
O(n) over rooms, availability is O(k) thanks to the index; only the calendar drawing would need paging.

---

# Chapter 19 — "Explain your code" drills

They will open a file and say "explain". Practise out loud on these twelve; for every line say *what it
does, why it is there, and what breaks without it*.

1. `DateRange.__post_init__` + `overlaps` — the rule and both validations.
2. `Booking.occupies` — why the status check is there.
3. `availability.is_room_free` — the three skips.
4. `availability.free_rooms` — the order of the filters.
5. `BestFitStrategy.choose` — the key tuple and the `None` case.
6. `PreferenceStrategy.score` — every weight and the penalty.
7. `allocation.create` — Factory + the error message.
8. `BaseRateRule.lines` — grouping and the season multiplier.
9. `LongStayDiscountRule.lines` — why it needs `current_lines`, why negative.
10. `PricingEngine.quote` — the three-line loop and why the order matters.
11. `HotelService.create_booking` — the order of the checks and what each protects.
12. `HotelService.check_in` / `check_out` — guards, stamps, and the invoice transaction.

💡 Record yourself explaining three of them. If you hear "basically" more than twice a sentence, you
are not sure yet — go back to the chapter.

---

# Chapter 20 — Glossary

| Term | Meaning here |
|---|---|
| ACID / atomicity | a transaction happens completely or not at all |
| Allen's interval algebra | the 13 relations between two intervals |
| Best-Fit | choose the smallest resource that still fits |
| CHECK constraint | a rule the database itself enforces |
| Determinism | the same input always gives the same output |
| Facade | one class that offers a simple front to a complex subsystem |
| Factory | a function that turns a name into an object |
| FSM (finite state machine) | fixed states + allowed transitions with guards |
| Guard | the condition that must hold for a transition |
| Half-open interval | `[start, end)` — start included, end excluded |
| Index (database) | a structure that turns a scan into a lookup |
| MVC | Model / View / Controller separation |
| N+1 queries | one query per row instead of one join — a performance mistake |
| Open/Closed principle | open for extension, closed for modification |
| Overlap rule | `a < d and c < b` |
| Placeholder (`?`) | the safe way to put a value into SQL |
| RESTRICT / CASCADE | refuse the delete / delete the children too |
| Repository | a class that hides all SQL for one table |
| Rule chain | independent rules applied in order, each adding a line |
| Singleton | exactly one instance in the program |
| Strategy | one interface, several interchangeable implementations |
| Transaction | a group of writes that commit or roll back together |
| Value object | a small immutable object compared by its value (`DateRange`) |
