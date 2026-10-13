# Appendix — Answers to "Check yourself"

For the supervisor: these need reasoning or arithmetic, not memory. A student who answers 80% of them
understands the project. For the student: try first, then look.

## Chapter 2 — Python

1. `__init__`, `__repr__` and `__eq__` (plus ordering if you ask for it).
2. `DateRange` is a *value* that must never change after an availability check used it; a `Booking` has
   a life cycle — its status and timestamps change on purpose.
3. In `__post_init__`, immediately after the object is built. The benefit: an invalid range cannot exist
   anywhere in the program, so no other function needs to re-check.
4. Enum members are singletons: `is` compares identity and cannot be fooled by a look-alike string, and
   a typo like `"confimed"` fails loudly instead of quietly returning False.
5. Python raises `TypeError: Can't instantiate abstract class ... with abstract method choose` — at
   creation time, not later in the middle of a booking.
6. `list(stay.nights_list())`. It is a generator so that the caller decides whether to loop once
   (pricing) or build a list (calendar), without ever storing 30 dates needlessly, and so the "which
   nights?" logic exists in exactly one place.
7. `conn.rollback()` in the `except`, then `conn.close()` in the `finally`; the first INSERT is undone.
8. `repositories.py`, function `_row`, line 30 — the last line *inside your own code*. The cause is
   above it: the SELECT did not include the `capacity` column.

## Chapter 3 — Intervals

1. Four nights: 10, 11, 12 and 13 March. The room is free again on the 14th.
2. `[10,14)` vs `[14,16)` → `10<16 ✓`, `14<14 ✗` → **free**. vs `[13,20)` → `10<20 ✓`, `13<14 ✓` →
   **collide**. vs `[8,10)` → `10<10 ✗` → **free**.
3. Not overlapping means `b ≤ c` or `d ≤ a`; negating gives `b > c and d > a`, i.e. `c < b and a < d`.
4. Case F would be reported as a collision: a guest arriving the day another leaves would be refused.
   The hotel loses one sale per room per turnover day.
5. Because `BookingStatus.blocks_room` is False for CANCELLED and CHECKED_OUT, and `is_room_free` skips
   those bookings. It is decided in the enum property, used in `availability.py`.
6. One check: O(1). A whole-hotel search: O(rooms × k). It is small because `in_period` returns only the
   bookings overlapping the requested period (the same rule, in SQL, with an index) instead of all n.
7. One row per night. Rejected because a 14-night booking becomes 14 rows, changing dates means
   delete-and-reinsert, and a year of 24 rooms is ~8,760 rows to maintain.

## Chapter 4 — Allocation

1. First-Fit → 101 (lowest number). Best-Fit → 101 (capacity 1 fits one guest and is the smallest).
   Preference → 101 as well, unless the guest asked for something only 102/301 have.
2. The cheaper one; if the price is equal too, the lower room number. There must be a rule so the
   result is deterministic — otherwise two identical requests could give different rooms and no test
   could assert anything.
3. `key=lambda r: (r.rate, r.capacity, int(r.number))`.
4. `None`. `HotelService.create_booking` turns it into `HotelError("No free room for N guest(s) on
   those dates")`, which the UI shows as a message.
5. A new class in `allocation.py` implementing `choose`, plus one entry in `_STRATEGIES`. Nothing else —
   not the service, not the tests of other strategies, not the views.
6. Vary: the strategy. Keep identical: the room list, the 30 requests (fixed random seed), the starting
   empty database. Record: requests served, average wasted beds (capacity − guests), total revenue.

## Chapter 5 — Pricing

1. Thu 5 → Sun 8 March 2026 = 3 nights (5, 6, 7); 6 and 7 are Friday and Saturday.
   Base 3 × 450 = 1,350.00 · Weekend 2 × 450 × 20% = 180.00 · no discount (3 < 7) ·
   Parking 3 × 40 = 120.00 · subtotal 1,650.00 · VAT 18% = 297.00 · **total 1,947.00**.
2. Because it takes a percentage of the lines produced so far. If it ran first, `current_lines` would be
   empty and the discount would be 0.00 — the guest would lose the discount entirely.
3. So that `Quote.total` is simply the sum of the lines and the invoice adds up exactly as printed;
   a hidden subtraction would make the printed lines and the total disagree.
4. Only the Friday and Saturday nights. The rule walks `stay.nights_list()` and tests
   `night.weekday() in config.WEEKEND_DAYS` for each one — per night, not per stay.
5. Open for extension, closed for modification. Obeyed in `PricingEngine.rules` (a new rule is a new
   class plus one list entry) and in `allocation._STRATEGIES`.
6. A new class `ChildrenFreeRule` returning a negative line for guests under 6 (the context would need
   their ages), one line in the engine's rule list, and one test in `test_pricing.py`.

## Chapter 6 — The state machine

1. States CONFIRMED, CHECKED_IN, CHECKED_OUT, CANCELLED; arrows: check-in (guard: today ≥ check-in),
   check-out (from CHECKED_IN, action: invoice), cancel (from CONFIRMED only). Missing on purpose:
   anything out of CHECKED_OUT or CANCELLED — a finished booking is history, not a live object.
2. It is refused: `cancel` requires CONFIRMED, so the guard raises
   `HotelError("Only a confirmed booking can be cancelled")` in `hotel_service.py`.
3. `if not booking.status.blocks_room: continue` in `availability.is_room_free` — CANCELLED returns
   False from `blocks_room`, so the booking becomes invisible to availability.
4. So the tests can pretend it is any date without waiting; production passes nothing and gets
   `date.today()`.
5. Because it is a **price**, and every price is produced by the pricing engine — keeping one kind of
   knowledge in one place.
6. Atomicity: if a line fails halfway, the rollback removes the invoice too. An invoice missing lines
   would be worse than no invoice.

## Chapter 7 — Database

1. `capacity > 0` (a room with no beds), `check_out > check_in` (a booking ending before it starts),
   `status IN (...)` (a typo becoming a state). Also `guests > 0`.
2. RESTRICT on `bookings.room_id`: deleting a room that has bookings is refused (history must survive).
   CASCADE on `invoice_lines.invoice_id`: deleting an invoice removes its lines (they are meaningless alone).
3. They are ignored: RESTRICT does not block, CASCADE does not cascade — silently. Every connection must
   run it.
4. SQLite has no date type. ISO (`YYYY-MM-DD`) sorts chronologically as text, so `ORDER BY` and
   `WHERE date < ?` behave correctly.
5. `conn.execute("SELECT * FROM guests WHERE name = ?", (name,))`. Without it, a name containing a
   quote breaks the statement, and a crafted value can run arbitrary SQL (injection).
6. It **is** the overlap rule, written in SQL: `check_in < :end AND check_out > :start` — the same two
   comparisons, applied by the database so only the relevant rows travel to Python.
