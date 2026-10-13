# Part B — Build it, step by step

How to use this part: **do not read ahead.** Do one step, run the command it gives you, look at the
result, then do the next. Every step is small. If a step says "you should see X" and you see something
else, stop and fix it before continuing — chapter 17 has the common errors.

Every stage has the same rhythm: **goal → files → steps → check → commit.**

---

# Chapter 10 — Stage 0: get comfortable (30 minutes)

**Step 0.1** — Open the terminal in the project folder. You must see `(.venv)` at the start of the
line; if not, run `.venv\Scripts\activate`.

**Step 0.2** — Run everything:
```
pytest -v
```
You will see a long red list ending with something like `47 failed`. **That is correct** — nothing is
written yet.

**Step 0.3** — Run one file and read one failure:
```
pytest tests/test_date_range.py -v
```
Scroll up to the first failure. Find the line `NotImplementedError`, and above it
`File ".../date_range.py", line NN, in __post_init__`. That is the first function you will write.

**Step 0.4** — Open `hotelmanager/models/date_range.py`. Read the text at the top of the file (it
explains half-open intervals and shows the six cases) and then the docstring inside each function —
the steps are numbered there. **The last line of each function is `raise NotImplementedError`; that is
the line you replace with your code.**

**Step 0.5** — Open `config.py` and read it top to bottom once. You will not change it, but you will
use names from it: `config.MAX_NIGHTS`, `config.WEEKEND_DAYS`, `config.VAT_RATE`, `config.EXTRAS`.

You are ready.

---

# Chapter 11 — Stage 1: the interval algorithm

**Goal:** a `DateRange` that knows how many nights it is and whether it collides with another.
**File:** `hotelmanager/models/date_range.py`, then two small methods in `entities.py`.
**Read first:** guide chapter 3.

## 11.1 `__post_init__` — refuse impossible stays

**Step 1.1** — Delete `raise NotImplementedError` and type:
```python
if self.check_out <= self.check_in:
    raise ValueError("check-out must be after check-in")
if self.nights > config.MAX_NIGHTS:
    raise ValueError(f"a stay cannot be longer than {config.MAX_NIGHTS} nights")
```
*Why `<=` and not `<`:* a booking of zero nights is meaningless — a guest must sleep at least once.

## 11.2 `nights`

**Step 1.2** — One line:
```python
return (self.check_out - self.check_in).days
```
*Why:* subtracting two `date` objects gives a `timedelta`; its `.days` is exactly the number of nights,
because the check-out day is not slept in. No `+1`.

## 11.3 `overlaps` — the rule

**Step 1.3** — One line, and it is the most important line in the project:
```python
return self.check_in < other.check_out and other.check_in < self.check_out
```
Use `<`, never `<=` (guide 3.4, case F).

## 11.4 `contains` and `nights_list`

**Step 1.4** —
```python
return self.check_in <= day < self.check_out        # contains
```
**Step 1.5** — `nights_list` yields one date per night:
```python
day = self.check_in
while day < self.check_out:
    yield day
    day += timedelta(days=1)
```
(`from datetime import timedelta` is already imported at the top.)

**Check:**
```
pytest tests/test_date_range.py -v
```
**You should see 12 passed.** If `test_overlap_cases[other5]` fails ("other starts the day ours ends"),
your `overlaps` uses `<=` somewhere — fix it to `<`.

## 11.5 Two small methods in `entities.py`

**Step 1.6** — `Room.fits`: `return self.active and self.capacity >= guests`
**Step 1.7** — `Booking.occupies`: `return self.status.blocks_room and self.stay.contains(day)`
*Why the status check:* a cancelled booking must not paint the calendar or block the room (guide 6.3).

**Commit:** `git add . && git commit -m "stage 1: date range and overlap" && git push`

---

# Chapter 12 — Stage 2: the database

**Goal:** save and load rooms, guests and bookings.
**Files:** `database/db.py`, `database/repositories.py`. **Read first:** guide chapter 7.

## 12.1 `Database` — three methods

**Step 2.1** — `get_connection`:
```python
conn = sqlite3.connect(self.db_path)
conn.row_factory = sqlite3.Row            # rows can be read by column name
conn.execute("PRAGMA foreign_keys = ON")  # SQLite has them OFF by default!
return conn
```
**Step 2.2** — `connection` (copy this shape exactly — it is the transaction, guide 2.7):
```python
conn = self.get_connection()
try:
    yield conn
    conn.commit()
except Exception:
    conn.rollback()
    raise
finally:
    conn.close()
```
**Step 2.3** — `initialize_schema`:
```python
with self.connection() as conn:
    conn.executescript(SCHEMA)
```

## 12.2 `RoomRepository` — write one method fully, then copy the shape

**Step 2.4** — `add` (this is the pattern for every `add` in the project):
```python
with self.db.connection() as conn:
    cursor = conn.execute(
        "INSERT INTO rooms (number, room_type, capacity, floor, view, base_rate, active) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (room.number, room.room_type, room.capacity, room.floor, room.view, room.base_rate, int(room.active)))
    room.id = cursor.lastrowid
    return room.id
```
💡 `int(room.active)` — SQLite has no boolean; `True` becomes 1.

**Step 2.5** — a private helper you will reuse three times:
```python
@staticmethod
def _row_to_room(r):
    return Room(number=r["number"], room_type=r["room_type"], capacity=r["capacity"], floor=r["floor"],
                view=r["view"], base_rate=r["base_rate"], active=bool(r["active"]), id=r["id"])
```
**Step 2.6** — `get`: `SELECT * FROM rooms WHERE id = ?` → `fetchone()` → `None` or `_row_to_room(row)`.
**Step 2.7** — `list_all`: `SELECT * FROM rooms ORDER BY CAST(number AS INTEGER)` (so 9 comes before 101),
optionally `WHERE active = 1`.
**Step 2.8** — `update` and `delete`: one `UPDATE ... WHERE id = ?`, one `DELETE ... WHERE id = ?`.

## 12.3 `GuestRepository`

**Step 2.9** — Same four methods. `search` builds one condition:
```python
like = f"%{text}%"
rows = conn.execute("SELECT * FROM guests WHERE name LIKE ? OR email LIKE ? OR document_id LIKE ? ORDER BY name",
                    (like, like, like)).fetchall()
```

## 12.4 `BookingRepository` — the conversions

**Step 2.10** — `_row` (the only tricky mapping in the project):
```python
stay = DateRange(date.fromisoformat(r["check_in"]), date.fromisoformat(r["check_out"]))
return Booking(room_id=r["room_id"], guest_id=r["guest_id"], stay=stay, guests=r["guests"],
               status=BookingStatus(r["status"]), quoted_total=r["quoted_total"],
               extras=[e for e in r["extras"].split(",") if e],
               created_at=datetime.fromisoformat(r["created_at"]),
               checked_in_at=datetime.fromisoformat(r["checked_in_at"]) if r["checked_in_at"] else None,
               checked_out_at=datetime.fromisoformat(r["checked_out_at"]) if r["checked_out_at"] else None,
               id=r["id"], room_number=r["room_number"], guest_name=r["guest_name"])
```
**Step 2.11** — `add`: store `stay.check_in.isoformat()`, `booking.status.value`,
`",".join(booking.extras)`, `booking.created_at.isoformat()`.
**Step 2.12** — `get` and `list_all` use `self.SELECT` (already written for you — it joins rooms and
guests so the table shows names, not ids).
**Step 2.13** — `in_period` — **this is algorithm 1 in SQL**:
```python
rows = conn.execute(self.SELECT + " WHERE b.check_in < ? AND b.check_out > ? ORDER BY b.check_in",
                    (end.isoformat(), start.isoformat())).fetchall()
```

**Check:** `pytest tests/test_repositories.py -v` → **4 passed**.
Then open `hotel.db` with DB Browser for SQLite (free) and look at your rows — a screenshot for the book.

**Commit:** `stage 2: database and repositories`

---

# Chapter 13 — Stage 3: availability and allocation

**Goal:** "which rooms are free?" and "which one do we give?"
**Files:** `booking/availability.py`, `booking/allocation.py`. **Read first:** guide chapters 3.5 and 4.

## 13.1 `is_room_free`

**Step 3.1** — The three skips and the comparison (guide 3.5):
```python
for booking in bookings:
    if booking.room_id != room_id:
        continue
    if not booking.status.blocks_room:
        continue
    if ignore_booking_id is not None and booking.id == ignore_booking_id:
        continue
    if booking.stay.overlaps(stay):
        return False
return True
```
*Why `ignore_booking_id`:* when you **edit** a booking's dates, it must not collide with itself.

## 13.2 `free_rooms`

**Step 3.2** —
```python
result = []
for room in rooms:
    if not room.fits(guests):
        continue
    if room_type and room.room_type != room_type:
        continue
    if is_room_free(room.id, stay, bookings):
        result.append(room)
return result
```

## 13.3 The three strategies

**Step 3.3** — `FirstFreeStrategy`: `min(candidates, key=lambda r: int(r.number))` (None if empty).
**Step 3.4** — `BestFitStrategy`: `min(candidates, key=lambda r: (r.capacity, r.rate, int(r.number)))`.
**Step 3.5** — `PreferenceStrategy.score`:
```python
score = 0
if preferences.get("view") and room.view == preferences["view"]:        score += 3
if preferences.get("floor") and room.floor == int(preferences["floor"]): score += 2
if preferences.get("room_type") and room.room_type == preferences["room_type"]: score += 1
score -= (room.capacity - guests)          # penalty for wasted beds
return score
```
and `choose`: `max(candidates, key=lambda r: (self.score(r, guests, preferences), -int(r.number)))`.
*Why the `-int(number)`:* on a tie the **lower** number wins, so the result is deterministic.

**Step 3.6** — `create(name)`:
```python
name = name or config.DEFAULT_ALLOCATION
if name not in _STRATEGIES:
    raise ValueError(f"unknown strategy '{name}'; choose from {list(_STRATEGIES)}")
return _STRATEGIES[name]()
```

**Check:** `pytest tests/test_availability_allocation.py -v` → **12 passed**.
**Commit:** `stage 3: availability and allocation`

---

# Chapter 14 — Stage 4: the pricing engine

**Goal:** a `Quote` whose lines add up to the total and explain it.
**Files:** `models/entities.py` (Quote), `pricing/rules.py`, `pricing/engine.py`. **Read first:** guide chapter 5.

**Step 4.1** — `Quote.total`: `round(sum(line.amount for line in self.lines), 2)`.
**Step 4.2** — `Quote.subtotal`: the same sum **excluding** the VAT line:
```python
return round(sum(l.amount for l in self.lines if not l.description.lower().startswith("vat")), 2)
```
**Step 4.3** — `Season.contains`: `return self.start <= day <= self.end` (inclusive — a season is a
calendar period, not a stay).
**Step 4.4** — `PricingContext.season_for`:
```python
for season in self.seasons:
    if season.contains(day):
        return season
return None
```
**Step 4.5** — `BaseRateRule.lines` — group equal nights (guide 5.4):
```python
prices = {}
for night in context.stay.nights_list():
    season = context.season_for(night)
    price = round(context.room.rate * (season.multiplier if season else 1.0), 2)
    prices[price] = prices.get(price, 0) + 1
return [InvoiceLine(f"{count} night(s) x {context.room.room_type} @ {price:.2f}", count, price)
        for price, count in sorted(prices.items())]
```
**Step 4.6** — `WeekendSurchargeRule.lines`:
```python
total = 0.0
count = 0
for night in context.stay.nights_list():
    if night.weekday() in config.WEEKEND_DAYS:
        season = context.season_for(night)
        total += context.room.rate * (season.multiplier if season else 1.0) * config.WEEKEND_SURCHARGE
        count += 1
if count == 0:
    return []
return [InvoiceLine(f"Weekend surcharge ({count} night(s), +{int(config.WEEKEND_SURCHARGE*100)}%)", 1, round(total, 2))]
```
**Step 4.7** — `LongStayDiscountRule.lines`:
```python
if context.stay.nights < config.LONG_STAY_NIGHTS:
    return []
room_part = sum(line.amount for line in current_lines)
return [InvoiceLine(f"Long stay discount ({context.stay.nights} nights, -{int(config.LONG_STAY_DISCOUNT*100)}%)",
                    1, -round(room_part * config.LONG_STAY_DISCOUNT, 2))]
```
**Step 4.8** — `ExtrasRule.lines`:
```python
lines = []
for name in context.extras:
    if name not in config.EXTRAS:
        continue
    price, per_guest = config.EXTRAS[name]
    quantity = context.stay.nights * (context.guests if per_guest else 1)
    lines.append(InvoiceLine(f"{name} x{quantity}", quantity, price))
return lines
```
**Step 4.9** — `VatRule.lines`: one line, `quantity=1`,
`unit_price = round(sum(l.amount for l in current_lines) * config.VAT_RATE, 2)`, description
`f"VAT {int(config.VAT_RATE*100)}%"`.
**Step 4.10** — `PricingEngine.quote`:
```python
lines = []
for rule in self.rules:
    lines.extend(rule.lines(context, lines))      # every rule sees what came before
return Quote(lines)
```
**Step 4.11** — `cancellation_fee`:
```python
if hours_before_checkin >= config.FREE_CANCELLATION_HOURS:
    return 0.0
for line in quote.lines:
    if "night" in line.description:
        return round(line.unit_price, 2)
return 0.0
```

**Check:** `pytest tests/test_pricing.py -v` → **8 passed**. Now do the 7-night example from guide 5.3
**by hand** and compare with what the program prints. They must agree to the agora.

**Commit:** `stage 4: pricing engine`

---

# Chapter 15 — Stage 5: the rules and the state machine

**Goal:** the whole system works without any window.
**File:** `booking/hotel_service.py`. **Read first:** guide chapter 6.

**Step 5.1** — `add_room`: check `number` not empty, `room_type in config.ROOM_TYPES`,
`capacity > 0`, and that no existing room has the same number; raise `HotelError` with a readable
message; otherwise `return self.rooms.add(room)`.
**Step 5.2** — `add_guest`: name not empty; `"@" in email` and `"." in email.split("@")[-1]`; then save.
**Step 5.3** — `quote_for`:
```python
context = PricingContext(room, stay, guests, list(extras), self.seasons.list_all())
return self.pricing.quote(context)
```
**Step 5.4** — `find_free_rooms`:
```python
bookings = self.bookings.in_period(stay.check_in, stay.check_out)
return availability.free_rooms(self.rooms.list_all(only_active=True), bookings, stay, guests, room_type)
```
💡 `in_period`, not `list_all()` — that is the O(k) from guide 3.6, and the examiner will ask.

**Step 5.5** — `create_booking`, in this exact order:
```python
guest = self.guests.get(guest_id)
if guest is None:
    raise HotelError("Guest not found")
if guests < 1:
    raise HotelError("A booking needs at least one guest")

if room_id is not None:
    room = self.rooms.get(room_id)
    if room is None or not room.fits(guests):
        raise HotelError("That room does not exist or is too small")
    if not availability.is_room_free(room_id, stay, self.bookings.in_period(stay.check_in, stay.check_out)):
        raise HotelError(f"Room {room.number} is not free on those dates")
else:
    candidates = self.find_free_rooms(stay, guests, room_type)
    room = allocation.create(strategy_name).choose(candidates, guests, preferences or {})
    if room is None:
        raise HotelError(f"No free room for {guests} guest(s) on those dates")

quote = self.quote_for(room, stay, guests, extras or [])
booking = Booking(room.id, guest_id, stay, guests, BookingStatus.CONFIRMED, quote.total, list(extras or []))
booking.id = self.bookings.add(booking)
return self.bookings.get(booking.id)
```
**Step 5.6** — `check_in`: copy the guarded-transition shape from guide 6.4 exactly.
**Step 5.7** — `check_out`:
```python
booking = self.bookings.get(booking_id)
if booking is None or booking.status is not BookingStatus.CHECKED_IN:
    raise HotelError("Only a checked-in booking can be checked out")
room = self.rooms.get(booking.room_id)
quote = self.quote_for(room, booking.stay, booking.guests, booking.extras)
invoice = Invoice(booking.id, datetime.now(), quote.lines, quote.subtotal,
                  round(quote.total - quote.subtotal, 2), quote.total)
invoice.id = self.invoices.add(invoice)          # one transaction, lines included
booking.status = BookingStatus.CHECKED_OUT
booking.checked_out_at = datetime.now()
self.bookings.update(booking)
return booking, invoice
```
**Step 5.8** — `cancel`:
```python
booking = self.bookings.get(booking_id)
if booking is None or booking.status is not BookingStatus.CONFIRMED:
    raise HotelError("Only a confirmed booking can be cancelled")
when = when or datetime.now()
hours = (datetime.combine(booking.stay.check_in, datetime.min.time()) - when).total_seconds() / 3600
room = self.rooms.get(booking.room_id)
fee = self.pricing.cancellation_fee(self.quote_for(room, booking.stay, booking.guests, booking.extras), hours)
booking.status = BookingStatus.CANCELLED
self.bookings.update(booking)
return booking, fee
```

**Check:**
```
pytest -v
```
**All 47 tests must pass.** This is the moment the project exists: book, check in, check out, cancel,
and every illegal move refused — all without a single window.

**Commit:** `stage 5: rules and state machine`

---

# Chapter 16 — Stages 6 and 7: the interface, the reports, the experiment

The UI is the easy part now; the rules are done. Build it **one tab at a time**, running `python run.py`
after each.

**Step 6.1** — `views/widgets.py`: `make_form` (labels + entries in a grid, return the dict of
StringVars) and `TableFrame` (a `ttk.Treeview` with `show="headings"`, a scrollbar, `fill(rows)` and
`selected_id()`). Every tab uses them, so write them once and well.
**Step 6.2** — `MainWindow`: a `ttk.Notebook`, the five views, and the dashboard label.
**Step 6.3** — `RoomsView` + the controller's room methods → run the app, press *Load sample data*,
see 24 rooms.
**Step 6.4** — `GuestsView` + its controller methods.
**Step 6.5** — `BookingsView`: the top half (dates → *Search free rooms* → pick → *Quote* → *Book*)
and the bottom half (the list + *Check in* / *Check out* / *Cancel*). Dates are typed as `YYYY-MM-DD`.
**Step 6.6** — `CalendarView.draw` — rectangles on a Canvas (guide: `calendar_view.py` docstring):
rooms are rows, days are columns, colour by status, click to select.
**Step 6.7** — `HotelService.calendar_matrix` feeds it: fetch the month's bookings **once**, then fill
`{(room_id, day): booking}`.

**Stage 7:**
**Step 7.1** — `availability.occupancy_rate` (occupied nights ÷ rooms × days) and
`HotelService.occupancy_for_month`, `dashboard`.
**Step 7.2** — `revenue_by_month`, `count_by_status`, `ReportsView.show`.
**Step 7.3** — `importer.export_invoice` → a CSV the hotel can print.
**Step 7.4 — the experiment for the book.** Write a small script (not part of the app) that:
```
for strategy in ("first_free", "best_fit", "preference"):
    empty the database, import the sample rooms
    replay the SAME 30 random requests (fixed seed!)
    count: how many were served, average wasted beds, total revenue
print a table
```
Put that table in chapter 18 of your book. It is the difference between "I implemented three
strategies" and "I measured them".

**Commit after every step.**
