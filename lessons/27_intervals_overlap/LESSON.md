# Lesson 27 — Do two stays collide? Half-open intervals and a two-comparison rule

> **For:** Eran (HotelManager stage 1 — "the heart") &nbsp;·&nbsp; **Time:** 45 min
> **Before:** Python `date`, booleans &nbsp;·&nbsp; **After this:** Lesson 28 (allocation), Lesson 33 (the SQL version)

## 🎯 By the end, the student can

1. Explain why a stay is the **half-open** interval [check-in, check-out) and count its nights.
2. Write the overlap rule `a < d and c < b` and **prove** it with De Morgan.
3. Check the rule on all eight cases, and explain why case F breaks careless code.
4. Explain how a booking's **state** decides whether it blocks the room.

---

## 1. Half-open: we sell nights, not days

![half-open stays](figs/half_open.png)

Guest 1 checks in on the 2nd and out on the 9th: nights 2, 3, …, 8 → **7 nights = 9 − 2**. The 9th is not included —
guest 2 can check in that afternoon. Writing a stay as **[a, b)** (a included, b not) makes this automatic:

* nights = b − a, no "+1" anywhere;
* back-to-back stays [2, 9) and [9, 12) don't share anything.

## 2. The rule

$$[a,b)\ \text{and}\ [c,d)\ \text{collide}\iff a<d\ \text{and}\ c<b$$

![sliding stay](figs/overlap_slide.gif)

Watch a 3-night stay slide past ours: both lights must be ✓ to collide. The moment its check-in reaches 7 (our
check-out), `c < b` fails → free.

## 3. All eight cases (from Eran's guide)

![eight cases](figs/eight_cases.png)

**Case F** is the one careless code gets wrong: with `<=` instead of `<`, a guest arriving the day another leaves would
be refused — real lost money. `tests/test_date_range.py` has all eight; F has its own test.

(These are Allen's interval relations, 1983 — 13 possible relations between two intervals; six overlap.)

## 4. The proof — De Morgan

![De Morgan proof](figs/de_morgan.png)

It is easier to say when two stays are **free**: theirs ends before ours starts (d ≤ a) **or** theirs starts after ours
ends (b ≤ c). Negate it: NOT(P or Q) = (NOT P) and (NOT Q) → **a < d and c < b**. Two comparisons replace an `if`-ladder
of eight situations.

## 5. Checked by brute force

![brute force](figs/brute_force.png)

Every pair of stays with dates 1…12: **4,356 pairs, 0 mismatches** between the rule and "do they share a night?". Change
`<` to `<=` in the script and watch case F turn red.

## 6. From one pair to "is the room free?"

```python
def is_room_free(room_id, stay, bookings, ignore_booking_id=None):     # the sketch - write your own
    for booking in bookings:
        if booking.room_id != room_id or booking.id == ignore_booking_id:
            continue
        if not booking.status.blocks_room:     # cancelled / checked-out bookings are invisible
            continue
        if booking.stay.overlaps(stay):
            return False
    return True
```

`blocks_room` is `True` only for CONFIRMED and CHECKED_IN (Lesson 30) — so **cancelling frees the room instantly**, with no
deletion and no special case. In SQL the same rule becomes
`WHERE room_id = ? AND check_in < :d AND :c < check_out AND status IN (...)` — fast with an index (Lesson 33).

## 7. Misconceptions

| Student says | Truth |
|---|---|
| "A 2 → 9 stay is 8 days, so 8 nights" | 7 nights. Half-open: b − a. |
| "I need an if for each of the 8 cases" | Two comparisons cover all of them. |
| "`<=` is safer" | It refuses back-to-back bookings (case F). |
| "Cancel = delete the booking" | Change the state; availability ignores it; history is kept. |

## 8. Activities

1. **Rope timeline (10 min).** Tape a 1–12 line on the floor. Two students hold ropes for two stays; the class says
   collide/free; check with the two comparisons on the board.
2. **Prove it yourselves (10 min).** Give only "free ⇔ d ≤ a or b ≤ c" and De Morgan's law; groups derive the rule.
3. **Break it (5 min).** In `18_HotelManager/02_examples/01_intervals.ipynb` change `<` to `<=` and run the eight cases.

## 9. Check yourself

<details><summary>1. [10, 14) and [13, 20) — collide?</summary>

10 < 20 ✓ and 13 < 14 ✓ → **collide** (the night of the 13th).
</details>

<details><summary>2. How many nights is [28 Feb 2026, 3 Mar 2026)?</summary>

28 Feb, 1 Mar, 2 Mar = **3** (2026 is not a leap year). `(check_out − check_in).days`.
</details>

<details><summary>3. A cancelled booking for room 102 overlaps a new request. Is the room free?</summary>

Yes — `blocks_room` is False for CANCELLED, so availability skips it.
</details>

## 10. In your project

| Project | Where |
|---|---|
| HotelManager | `hotelmanager/models/date_range.py` → `DateRange.__post_init__`, `nights`, `overlaps`, `contains`, `nights_list` · `models/entities.py` → `Booking.occupies` · `booking/availability.py` → `is_room_free`, `free_rooms` · `BookingRepository.in_period` · exercises ex01–ex04 · theory `18_HotelManager/01_theory/03_intervals.md` · notebook `01_intervals.ipynb` |

## 🎬 Watch & explore

* *Check if two intervals overlap — the one-line trick* — [search on YouTube](https://www.youtube.com/results?search_query=check+if+two+intervals+overlap)
* *De Morgan's laws explained* — [search on YouTube](https://www.youtube.com/results?search_query=De+Morgan%27s+laws+explained)
* Wikipedia — [Allen's interval algebra](https://en.wikipedia.org/wiki/Allen%27s_interval_algebra)
