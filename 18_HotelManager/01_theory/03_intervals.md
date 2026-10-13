# Chapter 3 — Algorithm 1: do two stays collide?

💡 **In short:** a stay is `[check-in, check-out)` — the last day is *not* slept in. Two stays collide
exactly when `a < d and c < b`. Two comparisons decide everything, including the tricky case where one
guest leaves on the morning another arrives.

## 3.1 The problem, in money

Room 204 is booked 3–7 March. A guest wants it 5–9 March. If your program says "free", the hotel sells
the same bed twice and someone sleeps in the lobby. If it says "taken" for 7–9 March, the hotel loses
a sale **every single day**. This one comparison is the difference between a working hotel and an angry one.

## 3.2 Half-open intervals — why the last day is not counted

```
booking 3 -> 7 March

     3 Mar    4 Mar    5 Mar    6 Mar    7 Mar
     ███████  ███████  ███████  ███████  (free)
     night 1  night 2  night 3  night 4   guest leaves in the morning

nights = 7 − 3 = 4
```
Written `[3, 7)`: the 3rd is **in**, the 7th is **out**. Subtracting two dates gives exactly the number
of nights — no "+1" anywhere. And the room is available to a new guest arriving on the 7th.

💡 Every off-by-one bug in booking systems comes from mixing this up. Say "half-open" in the defense
and show the drawing.

## 3.3 The rule and its proof

```
[a, b)  and  [c, d)  overlap   ⇔   a < d  and  c < b
```

**Proof.** They do *not* overlap only if one finishes before or exactly when the other begins:
`b ≤ c` (ours ends first) or `d ≤ a` (theirs ends first). Negate it:

```
not (b ≤ c  or  d ≤ a)
  = (b > c) and (d > a)        (De Morgan: not(P or Q) = notP and notQ)
  = (c < b) and (a < d)                                              ∎
```
Write this derivation in chapter 6 of your book. It takes four lines and it shows you did not copy a rule.

## 3.4 All eight cases

Ours is `[3, 7)`:

```
          1 2 3 4 5 6 7 8 9 10 11
ours      . . ███████ . . . .

A [5,9)   . . . . ███████ .      3<9 ✓  5<7 ✓  ->  COLLIDE  (overlaps on the right)
B [1,5)   ███████ . . . . . .    3<5 ✓  1<7 ✓  ->  COLLIDE  (overlaps on the left)
C [4,6)   . . . ███ . . . . .    3<6 ✓  4<7 ✓  ->  COLLIDE  (inside ours)
D [1,9)   ███████████████ . .    3<9 ✓  1<7 ✓  ->  COLLIDE  (contains ours)
E [3,7)   . . ███████ . . . .    3<7 ✓  3<7 ✓  ->  COLLIDE  (identical)
F [7,9)   . . . . . . ███ . .    3<9 ✓  7<7 ✗  ->  free     *** the important one ***
G [1,3)   ███ . . . . . . . .    3<3 ✗         ->  free
H [9,11)  . . . . . . . . ███    3<11 ✓ 9<7 ✗  ->  free
```

**Case F** is where careless code fails: with `<=` instead of `<`, the program would refuse a booking
that starts the day the previous guest leaves. `tests/test_date_range.py` has all eight; F has its own
test with a comment saying exactly this.

📚 These are Allen's 13 interval relations (1983) — six overlap, seven do not. Cite it in the book.

## 3.5 From one pair to "is the room free?"

```
is_room_free(room, stay, bookings):
    for every booking b:
        if b is for a different room      -> skip
        if b.status does not block a room -> skip      (cancelled / checked out)
        if b is the booking we are editing-> skip
        if b.stay overlaps stay           -> return False
    return True
```
Three skips and one comparison. Notice the second skip: **cancelling a booking frees the room with no
extra code** — the state machine (chapter 6) and this algorithm meet in that one line.

## 3.6 Complexity — and the index that saves you

One comparison: **O(1)**.
Checking one room against **all** bookings ever made: **O(n)**. A hotel with 20,000 old bookings and
24 rooms would do ~480,000 comparisons to draw one search screen.

The fix (`BookingRepository.in_period`): ask the database only for bookings that touch the period,
using the **same rule** in SQL:

```sql
SELECT ... FROM bookings WHERE check_in < :end AND check_out > :start
```
With the index `(room_id, check_in, check_out)` SQLite jumps straight to them. Now the check is
**O(k)** where k = the few bookings overlapping that month.

❓ *What is the complexity of your availability check?* — "O(k) where k is the number of bookings that
overlap the requested period, because the repository filters by the same interval rule in SQL and the
index makes it a range scan; the in-memory part is a single pass with an O(1) comparison each."

## 3.7 The design you rejected (for chapter 8)

| | interval comparison (chosen) | one row per night |
|---|---|---|
| storage for a 14-night booking | 1 row | 14 rows |
| "is it free?" | 2 comparisons per candidate | index lookup for a duplicate |
| change the dates | update 2 fields | delete 14 rows, insert new ones |
| a year of 24 rooms | hundreds of rows | ~8,760 rows |
| protection from double booking | the algorithm | a UNIQUE index |

Both work. Say which you chose **and why** — that is what chapter 8 is for.

## ✅ Check yourself — Chapter 3

1. A booking is 10 → 14 March. How many nights? Which nights exactly? When is the room free again?
2. Decide with the rule: `[10,14)` vs `[14,16)`; `[10,14)` vs `[13,20)`; `[10,14)` vs `[8,10)`.
3. Prove the rule with De Morgan, in your own handwriting.
4. What would break if the code used `<=` instead of `<`? Give the business consequence.
5. Why do cancelled bookings not block a room, and where is that decided?
6. What is the complexity of one check? Of a whole-hotel search? What made it small?
7. Name the alternative design and one reason you rejected it.

## 📚 Further reading

- Allen, J. F. (1983). *Maintaining Knowledge about Temporal Intervals*, CACM 26(11) — the 13 relations.
- Python docs — `datetime`: https://docs.python.org/3/library/datetime.html
- SQLite — *Query Planning* (how an index turns a scan into a lookup): https://www.sqlite.org/queryplanner.html
