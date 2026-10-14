# HotelManager — hints, checks and traps, stage by stage

Use this file when you are **stuck** on a function of your skeleton. For each hard function:

- **Learn it in** — the theory section, notebook and exercise that teach the idea.
- **Hints** — hidden. Open one at a time: 💡 a nudge, 🔧 the steps.
- **Check yourself** — numbers to compare against before you run the tests.
- **Traps** — the mistakes that make a test fail (or pass while the program is wrong).

`CHECKLIST.md` (next to this file) lists **every** function you have to write. Most docstrings in your skeleton
already contain the code shape; the build chapter `04_build/10_build.md` gives every step. This file is for when
those are not enough.

> **The working loop.** One function → run **its** test (`pytest tests/test_date_range.py -v`) → green →
> commit → next. If a test is red, read the *last* lines of the error first: they say which line and why.

---

## Stage 1 — The interval algorithm

**Learn it in:** theory `03_intervals` §3.2–3.5 · notebook `01_intervals` · exercises **ex01–ex03**

### `DateRange.overlaps`

<details><summary>💡 Hint</summary>

Two stays do **not** collide when one ends before (or on the day) the other begins. Write that, then negate it
(De Morgan) — or write the docstring's line directly and check it against all eight cases in theory §3.4.
</details>

**Check yourself:**

| A | B | overlap? | why |
|---|---|---|---|
| [3, 7) | [7, 9) | **no** | the changeover day: one leaves on the 7th, one arrives on the 7th |
| [3, 7) | [6, 9) | yes | the night of the 6th |
| [3, 7) | [1, 3) | no | B leaves the day A arrives |
| [3, 7) | [4, 5) | yes | B is inside A |
| [3, 7) | [1, 10) | yes | A is inside B |

**Traps:** `<=` instead of `<` blocks every changeover day · `nights` with a `+1` (3 → 7 March is **4** nights) ·
`nights_list` building a list instead of `yield` is fine for the tests, but the docstring asks for a generator —
be ready to explain the difference.

---

## Stage 2 — The database

**Learn it in:** theory `07_database` §7.1–7.4 · the long docstring at the top of `repositories.py` · exercise **ex04**

- Every method is one of the four shapes in the header. Write `RoomRepository` completely first, run the test, then
  copy the shape for the other tables.
- `_row_to_room` / `_row_to_guest` / `BookingRepository._row`: write each **once**, use it in every read.
- `count_by_status` is tested here too: `{r["status"]: r["n"] for r in rows}` with `COUNT(*) AS n`.

<details><summary>🔧 Hint — <code>in_period</code> is the overlap rule in SQL</summary>

A booking overlaps `[start, end)` exactly when `check_in < end AND check_out > start` — the same two comparisons as
`overlaps`. Pass `(end.isoformat(), start.isoformat())` in **that** order. ISO dates (`2026-03-07`) compare
correctly as text, which is why we store dates that way (theory §7.3).
</details>

**Check yourself:** `pytest tests/test_repositories.py -v` → 4 passed. Then open `hotel.db` in DB Browser for
SQLite — dates look like `2026-03-07`, statuses like `confirmed`, extras like `breakfast,parking`.

**Traps:** `int(room.active)` on the way in and `bool(r["active"])` on the way out · the booking `_row` must turn
`""` into an empty extras list (`[e for e in s.split(",") if e]`) · `PRAGMA foreign_keys = ON` on **every**
connection — it is off by default, and without it deleting a room with bookings silently succeeds.

---

## Stage 3 — Availability and allocation

**Learn it in:** theory `04_allocation` §4.2–4.3 · notebook `02_allocation` · exercises **ex05–ex07**

### `is_room_free` and `free_rooms`

Skip a booking if it is for another room, if its status does not block the room (cancelled / checked out), or if it
is the booking being edited. Any remaining overlap → `False`.

### The three strategies

<details><summary>💡 Hint — why tuples</summary>

`min(rooms, key=lambda r: (r.capacity, r.rate, int(r.number)))` compares capacity first, then the rate, then the
number. One line gives "smallest room that fits, cheapest of those, lowest number of those", and the answer is
always the same room — that is what makes the tests reliable.
</details>

**Check yourself** — free rooms 101 (double, cap 2), 102 (double, cap 2), 201 (family, cap 4); a couple:

| strategy | room | why |
|---|---|---|
| `first_free` | 101 | lowest number |
| `best_fit` | 101 | capacity 2 beats 4; equal rates; lower number |
| `preference` with `{"view": "sea"}`, and only 201 has a sea view | 201 | score 3 − (4 − 2) = 1 beats 101's 0 − 0 = 0: the view is worth 3, the two empty beds cost 2 |

**Traps:** comparing room numbers as text (`"10" < "9"`) — always `int(room.number)` · forgetting to return `None`
for an empty list · `create("bestfit")` must raise a `ValueError` that **lists** the valid names.

---

## Stage 4 — The pricing engine

**Learn it in:** theory `05_pricing` §5.2–5.4 (do §5.3 by hand first) · notebook `03_pricing` · exercises **ex08–ex10**

### The five rules

<details><summary>💡 Hint — the order is the design</summary>

`PricingEngine.quote` runs the rules in a fixed order and gives each rule the lines added **so far**. That is why the
long-stay discount can take 10% of *base + weekend* only (the extras come after it), and why VAT is 18% of
everything before it.
</details>

<details><summary>🔧 Hint — the weekend rule</summary>

For each night in `stay.nights_list()` whose `.weekday()` is in `config.WEEKEND_DAYS` (Friday = 4, Saturday = 5):
add `room.rate × (season multiplier or 1.0) × config.WEEKEND_SURCHARGE`. Return **one** line with quantity 1 and the
rounded total as the unit price — or `[]` when there were no weekend nights.
</details>

**Check yourself** — room `double` (450.00 a night), 2 guests:

```
2 → 4 March (Mon–Wed), nothing else:
    2 night(s) x double @ 450.00        900.00
    VAT 18%                             162.00         total 1,062.00

2 → 9 March (Mon–Mon), breakfast — the worked example of theory §5.3:
    7 night(s) x double @ 450.00      3,150.00
    Weekend surcharge (2 nights)        180.00
    Long stay discount                 -333.00         (10% of 3,150 + 180)
    breakfast x14                       770.00         (7 nights x 2 guests x 55)
    VAT 18%                             678.06         subtotal 3,767.00, total 4,445.06

5 → 8 March, high season 6–10 March x1.5     subtotal 2,070.00, total 2,442.60
```

### `Quote.subtotal` and `cancellation_fee`

- `subtotal` = every line except the VAT line (its description starts with `"VAT"`); `total` = every line.
- `cancellation_fee`: `0.0` when `hours_before >= config.FREE_CANCELLATION_HOURS` (48); otherwise the **first**
  line's unit price — one night of the room. For 2 → 4 March: 72 hours before → 0.00; 10 hours before → 450.00.

**Traps:** `Season.contains` is **inclusive** at both ends (a calendar period), unlike `DateRange.contains` (a stay)
· the discount line holds a **negative** unit price, so `total` is always just the sum · round each line to 2
decimals, not only the total — otherwise the invoice on paper does not add up.

---

## Stage 5 — The rules and the state machine

**Learn it in:** theory `06_fsm` §6.2–6.4 · notebook `04_state_machine` · exercises **ex11–ex13**

**First:** `SeasonRepository` and `InvoiceRepository` (build chapter step 5.0) — `quote_for` reads the seasons and
`check_out` writes the invoice.

### `create_booking`

Follow the six steps of the docstring **in order** and raise `HotelError` with the exact message at each refusal.
With `room_id` given, check the room exists, fits, and is free — with `is_room_free` on
`self.bookings.in_period(...)`, never on `list_all()`.

### `check_in / check_out / cancel` — the state machine

<details><summary>🔧 Hint — the shape of every transition</summary>

```
booking = self.bookings.get(booking_id)
if booking is None or booking.status is not <the one allowed state>:
    raise HotelError("<why not, in words the receptionist understands>")
<the extra guard, e.g. too early to check in>
booking.status = <the new state>; booking.<timestamp> = datetime.now()
self.bookings.update(booking)
return booking
```
</details>

**Check yourself:** `cancel` turns a check-in date into a time with `datetime.combine(check_in, datetime.min.time())`
(00:00 that day) before subtracting. Cancelling the 2 → 4 March booking (check-in 2 March, 00:00):

| cancelled at | hours before | fee |
|---|---|---|
| 27 Feb, 10:00 | 62 | 0.00 |
| 28 Feb, 10:00 | 38 | 450.00 — already inside the 48 hours |
| 1 Mar, 10:00 | 14 | 450.00 |

**Traps:** `invoice.total` must equal `booking.quoted_total` (the test checks it) — build the invoice from the
**same** quote · `vat = round(quote.total - quote.subtotal, 2)` · save the invoice and its lines in **one**
`with self.db.connection()` block, so a failure leaves nothing half-written.

---

## Stage 6 — The user interface

Views draw and call the controller; the controller calls `HotelService` through `_guard`; the service raises
`HotelError`. That chain is why a broken rule becomes a polite message instead of a crash.

- `_guard`: `try: return fn(*args, **kwargs)` / `except HotelError as e: self.view.show_error(str(e)); return None`.
- `_parse_stay`: `date.fromisoformat(...)` raises `ValueError` on `2026-3-7`; `DateRange` raises `ValueError` on an
  impossible range. Turn both into `HotelError("Dates must look like 2026-03-07")` etc.
- `calendar_matrix`: fetch the month's bookings **once** (`in_period`), then fill `cells[(room.id, day)]` with
  `next((b for b in bookings if b.room_id == room.id and b.occupies(day)), None)`.

If a button "does nothing", the exception went to the terminal — look there first.

---

## Stage 7 — Reports, export and the experiment

- `occupancy_rate`: occupied nights inside `[month_start, month_end)` ÷ (active rooms × days in the period).
- The allocation experiment: the **same** 30 random requests (fixed `random.seed`) for each strategy. Count the
  requests that got a room and the average wasted beds (capacity − guests). Best-Fit should waste the fewest beds
  — if it does not, check that all three strategies really received the same requests.

---

## When nothing works

| Symptom | Likely cause |
|---|---|
| `sqlite3.IntegrityError: FOREIGN KEY constraint failed` | a booking for a room/guest id that does not exist — or deleting a room that has bookings (that one is *correct*: show it to the user) |
| `sqlite3.IntegrityError: UNIQUE constraint failed: guests.email` | two guests with the same e-mail — the database protecting you |
| a room is sold twice | `<=` in `overlaps`, or `is_room_free` forgot to skip *other* rooms only |
| a cancelled booking still blocks the room | `blocks_room` not checked in `is_room_free` / `occupies` |
| the invoice total ≠ the quoted total | the invoice was built from a different quote (different extras or seasons) |
| `NameError: config` | add `import config` at the top of the file you are in |
| a test passes alone, fails with the others | a leftover singleton — see `tests/conftest.py` |
