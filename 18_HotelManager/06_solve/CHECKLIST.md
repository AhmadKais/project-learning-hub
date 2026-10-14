# HotelManager — the full checklist

Every function you still have to write in your skeleton: **113**, in the order of `TASKS.md`.
Tick each box when its tests are green. The text after each name is the first line of its TODO —
the full instructions are in the docstring in your code. `HINTS.md` (next to this file) helps with the hard ones.

Generated from your skeleton by `tools/make_checklists.py` — do not edit by hand.

## Stage 1 — The interval algorithm (the heart)

**`hotelmanager/models/date_range.py`**

- [ ] `DateRange.__post_init__()` — reject impossible stays the moment one is created: if self.check_out <= self.check_in: raise ValueError("check-out must be after check-in") if self.nights > config.MAX_NIGHTS: raise ValueError(f"a stay cannot be longe...  
  ✅ checked by `tests/test_availability_allocation.py`, `tests/test_date_range.py`, `tests/test_hotel_service.py`, `tests/test_pricing.py`, `tests/test_repositories.py`
- [ ] `DateRange.nights` — one line: return (self.check_out - self.check_in).days  
  ✅ checked by `tests/test_date_range.py`, `tests/test_pricing.py`, `tests/test_repositories.py`
- [ ] `DateRange.overlaps(other)` — THE most important line in the project: return self.check_in < other.check_out and other.check_in < self.check_out  
  ✅ checked by `tests/test_date_range.py`, `tests/test_repositories.py`
- [ ] `DateRange.contains(day)` — one line: return self.check_in <= day < self.check_out  
  ✅ checked by `tests/test_date_range.py`
- [ ] `DateRange.nights_list()` — walk day by day from check_in up to (not including) check_out: day = self.check_in while day < self.check_out: yield day day = day + timedelta(days=1)  
  ✅ checked by `tests/test_date_range.py`

**`hotelmanager/models/entities.py`**

- [ ] `Room.fits(guests)` — one line: return self.active and self.capacity >= guests  
  ✅ checked by `tests/test_availability_allocation.py`
- [ ] `Booking.occupies(day)` — two conditions: return self.status.blocks_room and self.stay.contains(day)

> **Exit condition:** 12 tests green, including all eight overlap cases. Draw the six cases on paper and be able to explain why `[3,7)` and `[7,9)` do **not** collide.

## Stage 2 — The database

**`hotelmanager/database/db.py`**

- [ ] `Database.get_connection()` — conn = sqlite3.connect(self.db_path) conn.row_factory = sqlite3.Row # rows behave like dicts conn.execute("PRAGMA foreign_keys = ON") # OFF by default in SQLite! return conn
- [ ] `Database.connection()` — commit on success, rollback on any exception, always close: conn = self.get_connection() try: yield conn conn.commit() except Exception: conn.rollback() raise finally: conn.close()
- [ ] `Database.initialize_schema()` — run the SCHEMA script with conn.executescript(SCHEMA).

**`hotelmanager/database/repositories.py`**

- [ ] `RoomRepository.add(room)` — shape 1 in the header, written out for you there in full. Columns: number, room_type, capacity, floor, view, base_rate, active. Remember int(room.active) - SQLite has no boolean type.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `RoomRepository.update(room)` — shape 2. Same seven columns as add(), plus room.id as the LAST parameter because WHERE id = ? comes last in the statement.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `RoomRepository.delete(room_id)` — shape 3, one line.
- [ ] `RoomRepository.get(room_id)` — shape 4 (the "get one" half). Returns None when there is no such row, never raises. Write the _row_to_room helper shown in the header now - every other method here uses it.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `RoomRepository.list_all(only_active)` — shape 4 (the "list" half), with two extras: sql = "SELECT * FROM rooms" if only_active: sql += " WHERE active = 1" sql += " ORDER BY CAST(number AS INTEGER)"  
  ✅ checked by `tests/test_repositories.py`
- [ ] `GuestRepository.add(guest)` — shape 1. Columns: name, email, phone, document_id, notes. All five are plain text - no conversions needed. The UNIQUE e-mail is enforced by the database: a second guest with the same e-mail raises sqlite3.IntegrityErr...  
  ✅ checked by `tests/test_repositories.py`
- [ ] `GuestRepository.update(guest)` — shape 2. Same columns as add(), guest.id goes last.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `GuestRepository.delete(guest_id)` — shape 3. Like rooms, the FK RESTRICT refuses when the guest has bookings. Let the error surface.
- [ ] `GuestRepository.get(guest_id)` — shape 4. Write _row_to_guest the same way you wrote _row_to_room: Guest(name=r["name"], email=r["email"], phone=r["phone"] or "", document_id=r["document_id"] or "", notes=r["notes"] or "", id=r["id"]). (`or ""` becau...  
  ✅ checked by `tests/test_repositories.py`
- [ ] `GuestRepository.search(text)` — free-text search across three columns: if not text: sql, params = "SELECT * FROM guests ORDER BY name", () else: pattern = f"%{text}%" # build the pattern in PYTHON sql = ("SELECT * FROM guests WHERE name LIKE ? OR em...  
  ✅ checked by `tests/test_repositories.py`
- [ ] `BookingRepository._row(r)` — build a Booking from a row. stay = DateRange(date.fromisoformat(r["check_in"]), date.fromisoformat(r["check_out"])) status = BookingStatus(r["status"]) extras = [e for e in r["extras"].split(",") if e] the three times...
- [ ] `BookingRepository.add(booking)` — shape 1, but this one has four type conversions. Go slowly and use the TYPES list in the header: booking.stay.check_in.isoformat() date -> TEXT booking.stay.check_out.isoformat() date -> TEXT booking.status.value Enum...  
  ✅ checked by `tests/test_repositories.py`
- [ ] `BookingRepository.update(booking)` — shape 2. Update: check_in, check_out, guests, status, quoted_total, extras, checked_in_at, checked_out_at. booking.id last.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `BookingRepository.get(booking_id)` — shape 4, but use the class constant self.SELECT defined at the top of this class instead of "SELECT *": sql = self.SELECT + " WHERE b.id = ?"  
  ✅ checked by `tests/test_repositories.py`
- [ ] `BookingRepository.list_all(status, search)` — optional WHERE b.status = ? and/or (g.name LIKE ? OR r.number LIKE ?); ORDER BY b.check_in DESC. Build the WHERE from a list of conditions + params.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `BookingRepository.in_period(start, end)` — every booking that overlaps [start, end) - the calendar and the availability check only need these, not the whole table: WHERE b.check_in < ? AND b.check_out > ? (the same two comparisons!)  
  ✅ checked by `tests/test_repositories.py`
- [ ] `BookingRepository.count_by_status()` — (tests/test_repositories.py checks it; the reports screen uses it in stage 7): SELECT status, COUNT(*) AS n FROM bookings GROUP BY status -> {"confirmed": 3, "cancelled": 1, ...}  
  ✅ checked by `tests/test_repositories.py`

> **Exit condition:** 4 tests green. Open `hotel.db` in DB Browser for SQLite and see your rows.

## Stage 3 — Availability and allocation

**`hotelmanager/booking/allocation.py`**

- [ ] `FirstFreeStrategy.choose(candidates, guests, preferences)` — two lines: if not candidates: return None return min(candidates, key=lambda room: int(room.number))  
  ✅ checked by `tests/test_availability_allocation.py`
- [ ] `BestFitStrategy.choose(candidates, guests, preferences)` — if not candidates: return None return min(candidates, key=lambda room: (room.capacity, room.rate, int(room.number)))  
  ✅ checked by `tests/test_availability_allocation.py`
- [ ] `PreferenceStrategy.score(room, guests, preferences)` — add up the four rules from the class docstring: total = 0 if preferences.get("view") == room.view: total += 3 if preferences.get("floor") == room.floor: total += 2 if preferences.get("room_type") == room.room_type: to...
- [ ] `PreferenceStrategy.choose(candidates, guests, preferences)` — if not candidates: return None return max(candidates, key=lambda room: (self.score(room, guests, preferences), -int(room.number)))  
  ✅ checked by `tests/test_availability_allocation.py`
- [ ] `create(name)` — the Factory. Turns a string from the config file into a real strategy object: name = name or config.DEFAULT_ALLOCATION if name not in _STRATEGIES: raise ValueError(f"unknown allocation strategy '{name}'. " f"Valid: {'...  
  ✅ checked by `tests/test_availability_allocation.py`

**`hotelmanager/booking/availability.py`**

- [ ] `is_room_free(room_id, stay, bookings, ignore_booking_id)` — for every booking in `bookings`: skip it if b.room_id != room_id skip it if not b.status.blocks_room (cancelled / checked out do not block) skip it if b.id == ignore_booking_id (when EDITING a booking, ignore itself)...  
  ✅ checked by `tests/test_availability_allocation.py`
- [ ] `free_rooms(rooms, bookings, stay, guests, room_type)` — every room that (a) is active and fits `guests`, (b) matches `room_type` when one is given, and (c) is free for `stay` by is_room_free.  
  ✅ checked by `tests/test_availability_allocation.py`

> **Exit condition:** 12 tests green. You can explain why a cancelled booking does not block a room and why Best-Fit gives a couple the double room and not the family room.

## Stage 4 — The pricing engine

**`hotelmanager/models/entities.py`**

- [ ] `Quote.subtotal` — everything before tax: return round(sum(line.amount for line in self.lines if not line.description.lower().startswith("vat")), 2)  
  ✅ checked by `tests/test_pricing.py`
- [ ] `Quote.total` — the amount the guest actually pays: return round(sum(line.amount for line in self.lines), 2)  
  ✅ checked by `tests/test_hotel_service.py`, `tests/test_pricing.py`

**`hotelmanager/pricing/engine.py`**

- [ ] `PricingEngine.quote(context)` — lines = [] for rule in self.rules: lines.extend(rule.lines(context, lines)) # each rule sees what came before return Quote(lines)  
  ✅ checked by `tests/test_pricing.py`

**`hotelmanager/pricing/rules.py`**

- [ ] `Season.contains(day)` — start <= day <= end (this one IS inclusive - it is a calendar period, not a stay).
- [ ] `PricingContext.season_for(day)` — the first season that contains `day`, or None.
- [ ] `BaseRateRule.lines(context, current_lines)` — for each night in context.stay.nights_list(): price = context.room.rate * (season.multiplier if a season contains the night else 1.0) count how many nights have each price (a dict price -> count) return one InvoiceLin...  
  ✅ checked by `tests/test_hotel_service.py`, `tests/test_pricing.py`
- [ ] `WeekendSurchargeRule.lines(context, current_lines)` — count the nights whose .weekday() is in config.WEEKEND_DAYS. The surcharge is per weekend night: room.rate x season multiplier x WEEKEND_SURCHARGE. Return one line (or none when there are no weekend nights).  
  ✅ checked by `tests/test_hotel_service.py`, `tests/test_pricing.py`
- [ ] `LongStayDiscountRule.lines(context, current_lines)` — if stay.nights < config.LONG_STAY_NIGHTS: return []. Otherwise sum the amounts of the lines added so far (base + weekend), and return one line with a NEGATIVE unit_price of that sum x LONG_STAY_DISCOUNT. (This is why...  
  ✅ checked by `tests/test_hotel_service.py`, `tests/test_pricing.py`
- [ ] `ExtrasRule.lines(context, current_lines)` — for each name in context.extras that exists in config.EXTRAS: price, per_guest = config.EXTRAS[name] quantity = stay.nights * (guests if per_guest else 1) one InvoiceLine(f"{name} x{quantity}", quantity, price) Unknow...  
  ✅ checked by `tests/test_hotel_service.py`, `tests/test_pricing.py`
- [ ] `VatRule.lines(context, current_lines)` — one line 'VAT 18%' with quantity 1 and unit_price = sum(current amounts) * config.VAT_RATE.  
  ✅ checked by `tests/test_hotel_service.py`, `tests/test_pricing.py`

> **Exit condition:** 10 tests green — including the 7-night stay with a weekend, a season and a discount, matching a calculation you did by hand (see `docs/ALGORITHMS.md` §3).

## Stage 5 — The rules and the state machine

**`hotelmanager/booking/hotel_service.py`**

- [ ] `HotelService.add_room(room)` — validate before saving - number not empty; room_type in config.ROOM_TYPES; capacity > 0; the number is not already taken (look in list_all). Raise HotelError with a clear message, otherwise self.rooms.add(room).  
  ✅ checked by `tests/test_hotel_service.py`
- [ ] `HotelService.add_guest(guest)` — check before saving: if not guest.name.strip(): raise HotelError("guest name cannot be empty") email = guest.email.strip() if "@" not in email or "." not in email.split("@")[-1]: raise HotelError("that does not look l...  
  ✅ checked by `tests/test_hotel_service.py`
- [ ] `HotelService.quote_for(room, stay, guests, extras)` — gather what the pricing rules need, then hand it over: context = PricingContext(room=room, stay=stay, guests=guests, extras=extras, seasons=self.seasons.list_all()) return self.pricing.quote(context)
- [ ] `HotelService.find_free_rooms(stay, guests, room_type)` — availability.free_rooms(all rooms, bookings that overlap the stay, stay, guests, room_type). Use self.bookings.in_period(stay.check_in, stay.check_out) - not every booking ever made.  
  ✅ checked by `tests/test_hotel_service.py`
- [ ] `HotelService.create_booking(guest_id, stay, guests, extras, room_type, preferences, strategy_name, room_id)` — the most important method in the project. In this order: 1. the guest exists -> "Guest not found" 2. guests >= 1 and stay.nights <= MAX_NIGHTS (DateRange already checks the dates) 3. if room_id was given: that room ex...  
  ✅ checked by `tests/test_hotel_service.py`
- [ ] `HotelService.check_in(booking_id, today)` — allowed only from CONFIRMED and only when today >= stay.check_in ("Too early - check-in is on 2026-03-03"). Set status CHECKED_IN and checked_in_at = now, save, return the booking.  
  ✅ checked by `tests/test_hotel_service.py`
- [ ] `HotelService.check_out(booking_id)` — allowed only from CHECKED_IN. Rebuild the quote (prices may have been agreed at booking time - use booking.quoted_total for the totals but the quote lines for the invoice), create the Invoice with its lines in ONE tra...  
  ✅ checked by `tests/test_hotel_service.py`
- [ ] `HotelService.cancel(booking_id, when)` — allowed only from CONFIRMED ("Cannot cancel a guest who already checked in"). hours_before = (check_in at 00:00 - when).total_seconds() / 3600 fee = self.pricing.cancellation_fee(quote, hours_before) Set status CANCEL...  
  ✅ checked by `tests/test_hotel_service.py`

**`hotelmanager/database/repositories.py`**

- [ ] `SeasonRepository.add(season)` — shape 1. Columns: name, start_date, end_date, multiplier. Both dates are date objects -> .isoformat().  
  ✅ checked by `tests/test_repositories.py`
- [ ] `SeasonRepository.list_all()` — shape 4, ORDER BY start_date. Convert each row back with date.fromisoformat for both dates.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `SeasonRepository.delete(season_id)` — shape 3, one line.
- [ ] `InvoiceRepository.add(invoice)` — ONE transaction - insert the invoice, then every line with the new invoice id (executemany). If a line fails, nothing is written: that is what `with self.db.connection()` gives you.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `InvoiceRepository.get_for_booking(booking_id)` — two queries inside one connection: with self.db.connection() as conn: head = conn.execute("SELECT * FROM invoices WHERE booking_id = ?", (booking_id,)).fetchone() if head is None: return None lines = conn.execute("SEL...
- [ ] `InvoiceRepository.mark_paid(invoice_id)` — UPDATE invoices SET paid = 1 WHERE id = ?.

**`hotelmanager/pricing/engine.py`**

- [ ] `PricingEngine.cancellation_fee(quote, hours_before_checkin)` — free cancellation up to config.FREE_CANCELLATION_HOURS before check-in -> 0.0. Later: one night's worth of the room part, i.e. the FIRST base line's unit_price (rounded to 2 decimals).  
  ✅ checked by `tests/test_pricing.py`

> **Exit condition:** all 49 tests green. Without any window, you can book a room, check the guest in, check them out with an invoice, and be refused when you try an illegal move.

## Stage 6 — The user interface

**`hotelmanager/booking/availability.py`**

- [ ] `occupancy_on(day, rooms, bookings)` — (for the calendar): {room_id: Booking or None} - which booking holds each room on `day`. Use Booking.occupies.

**`hotelmanager/booking/hotel_service.py`**

- [ ] `HotelService.calendar_matrix(year, month)` — what CalendarView draws - {"days": [date, ...], "rooms": [Room, ...], "cells": {(room_id, date): Booking or None}} Fetch the bookings of the month once with self.bookings.in_period, then fill the cells.

**`hotelmanager/booking/importer.py`**

- [ ] `import_rooms(service, path)` — read the CSV (columns: number, room_type, capacity, floor, view, base_rate) and call service.add_room for each row. Count the successes; collect "line 7: <message>" for the failures (an existing number, a bad type...)...
- [ ] `import_guests(service, path)` — same shape, columns name, email, phone, document_id.

**`hotelmanager/controllers/app_controller.py`**

- [ ] `AppController.__init__(root)` — build the window and hand it the callbacks: self.view = MainWindow(root, dict( room_types=list(config.ROOM_TYPES), views=list(config.VIEWS), extras=list(config.EXTRAS), strategies=["first_free", "best_fit", "preferenc...
- [ ] `AppController.start()` — load the four tabs (rooms, guests, bookings, calendar) and the dashboard.
- [ ] `AppController._guard(fn, *args, **kwargs)` — call fn(*args); on HotelError show the message in the view and return None. Every button handler goes through this, so a broken rule is a polite message and never a crash.
- [ ] `AppController.refresh_rooms()` — self.view.rooms.show_rows(self.service.rooms.list_all()).
- [ ] `AppController.add_room(fields)` — build a Room from the form strings (int(capacity), int(floor), float(base_rate or 0)); catch ValueError -> "Capacity and floor must be numbers"; then self._guard(self.service.add_room, room) and refresh.
- [ ] `AppController.update_room(room_id, fields)` — .
- [ ] `AppController.delete_room(room_id)` — ask the view to confirm, then delete; a room with bookings raises (FK RESTRICT) - show it.
- [ ] `AppController.search_guests(text)` — .
- [ ] `AppController.add_guest(fields)` — Guest(name, email, phone, document_id) -> service.add_guest -> refresh.
- [ ] `AppController.update_guest(guest_id, fields)` — .
- [ ] `AppController._parse_stay(check_in, check_out)` — date.fromisoformat on both strings (the UI uses YYYY-MM-DD); a bad format or an impossible range must become a HotelError with a readable message, not a ValueError traceback.
- [ ] `AppController.search_free_rooms(check_in, check_out, guests, room_type)` — parse the stay and the guest count, call self.service.find_free_rooms(...), and give the view the list plus a one-line quote for each room (self.service.quote_for(...).total) so the clerk sees availability and price t...
- [ ] `AppController.preview_quote(room_id, check_in, check_out, guests, extras)` — quote_for the chosen room and show every line in the view (this is the 'why' of the price).
- [ ] `AppController.create_booking(guest_id, room_id, check_in, check_out, guests, extras, strategy)` — service.create_booking(...) through _guard; on success show "Booking #7 created - room 204, 4 nights, 2,124.00" and refresh the bookings list and the calendar.
- [ ] `AppController.refresh_bookings(status, search)` — service.bookings.list_all(status or None, search) -> view.
- [ ] `AppController.check_in(booking_id)` — _guard(service.check_in, booking_id) -> refresh + message.
- [ ] `AppController.check_out(booking_id)` — booking, invoice = service.check_out(id); show the invoice lines in a window and offer importer.export_invoice(...) to write the CSV.
- [ ] `AppController.cancel(booking_id)` — confirm, then booking, fee = service.cancel(id); tell the user the fee (0 or one night).
- [ ] `AppController.calendar(year, month)` — self.view.calendar.draw(self.service.calendar_matrix(year, month)).
- [ ] `AppController.import_sample()` — importer.import_rooms + import_guests, then refresh and report how many were added.

**`hotelmanager/views/bookings_view.py`**

- [ ] `BookingsView.__init__(parent, cb)` — build the two halves described above. Dates are typed as YYYY-MM-DD (keep it simple - a date picker is future work). The extras are Checkbuttons built from cb["extras"].
- [ ] `BookingsView.show_free_rooms(rooms_with_prices)` — [(room, total_price), ...] -> the small table of candidates.
- [ ] `BookingsView.show_quote(lines, total)` — one row per invoice line (description, quantity, unit price, amount) + the total.
- [ ] `BookingsView.show_rows(bookings)` — the bookings table. Colour the rows by status with tags: confirmed = normal, checked_in = green, checked_out = grey, cancelled = red.
- [ ] `BookingsView.selected_booking_id()`

**`hotelmanager/views/calendar_view.py`**

- [ ] `CalendarView.__init__(parent, cb)` — month/year chooser (two Comboboxes + "Show"), a Canvas, and a small legend explaining the colours.
- [ ] `CalendarView.draw(matrix)` — matrix = {"days": [...], "rooms": [...], "cells": {(room_id, day): booking or None}}

**`hotelmanager/views/guests_view.py`**

- [ ] `GuestsView.__init__(parent, cb)` — a search Entry + button calling cb["on_search_guests"], a TableFrame ("name", "email", "phone", "document"), a form and Add/Update buttons.
- [ ] `GuestsView.show_rows(guests)`
- [ ] `GuestsView.clear_form()`

**`hotelmanager/views/main_window.py`**

- [ ] `MainWindow.__init__(root, cb)` — self.dashboard = ttk.Label(self, ...) (one line, big font) notebook = ttk.Notebook(self) self.rooms = RoomsView(notebook, cb); self.guests = GuestsView(notebook, cb) self.bookings = BookingsView(notebook, cb); self.ca...
- [ ] `MainWindow.show_error(text)` — messagebox.showerror - the only place the views talk to the user about failures.
- [ ] `MainWindow.show_info(text)`
- [ ] `MainWindow.confirm(text)`

**`hotelmanager/views/rooms_view.py`**

- [ ] `RoomsView.__init__(parent, cb)` — THIS IS THE WORKED EXAMPLE TAB. Build this one first; guests_view and the others are the same shape with different columns.
- [ ] `RoomsView.show_rows(rooms)` — turn Room objects into table rows: self.rooms = {room.id: room for room in rooms} rows = [(room.id, (room.number, room.room_type, room.capacity, room.floor, room.view, f"{room.base_rate:.2f}", "yes" if room.active els...
- [ ] `RoomsView.clear_form()` — for var in self.form.values(): var.set("")

**`hotelmanager/views/widgets.py`**

- [ ] `make_form(parent, fields)` — Build a label+entry (or combobox) grid and return {key: tk variable}. fields: [(key, label, "entry"|"combo", options_or_None), ...]
- [ ] `TableFrame.__init__(parent, columns, widths, height)` — written out in full, because all five tabs use it: self.tree = ttk.Treeview(self, columns=columns, show="headings", height=height) for name, width in zip(columns, widths): self.tree.heading(name, text=name.replace("_"...
- [ ] `TableFrame.fill(rows)` — replace everything in the table: for item in self.tree.get_children(): self.tree.delete(item) for row_id, values, tag in rows: self.tree.insert("", "end", iid=str(row_id), values=values, tags=(tag,) if tag else ())
- [ ] `TableFrame.selected_id()` — which row is selected, as an int: selection = self.tree.selection() return int(selection[0]) if selection else None

> **Exit condition:** `python run.py` opens; *Load sample data* fills 24 rooms and 10 guests; you can search free rooms for a date range, see the price, book, check in, check out and cancel; the calendar shows the month with coloured cells.

## Stage 7 — Reports, export and the book

**`hotelmanager/booking/availability.py`**

- [ ] `occupancy_rate(rooms, bookings, month_start, month_end)` — (for the report): occupied nights / (number of active rooms x nights in the period).

**`hotelmanager/booking/hotel_service.py`**

- [ ] `HotelService.occupancy_for_month(year, month)` — first and last day of the month -> availability.occupancy_rate.
- [ ] `HotelService.dashboard(today)` — numbers for the top of the screen - arrivals today, departures today, in-house guests, free rooms today, occupancy this month.

**`hotelmanager/booking/importer.py`**

- [ ] `export_invoice(invoice, booking, guest, room, directory)` — write exports/invoice_<id>_<date>.csv with a small header (hotel, guest, room, dates, nights), then one row per line (description, quantity, unit price, amount), then subtotal / VAT / total. encoding="utf-8-sig" so it...

**`hotelmanager/controllers/app_controller.py`**

- [ ] `AppController.reports()` — occupancy per month (service.occupancy_for_month for the last 6 months), revenue per month (bookings.revenue_by_month) and the status counts -> self.view.reports.show(...).

**`hotelmanager/database/repositories.py`**

- [ ] `BookingRepository.revenue_by_month()` — {'2026-03': 12345.0, ...} from invoices: SELECT substr(i.issued_at, 1, 7) AS month, SUM(i.total) ... GROUP BY month

**`hotelmanager/views/main_window.py`**

- [ ] `MainWindow.show_dashboard(numbers)` — "Arrivals today: 3 Departures: 2 In-house: 11 Free rooms: 7 Occupancy: 68%".

**`hotelmanager/views/reports_view.py`**

- [ ] `ReportsView.__init__(parent, cb)` — a Figure with two subplots (occupancy %, revenue), a FigureCanvasTkAgg, a "Refresh" button, and a small table of status counts.
- [ ] `ReportsView.show(occupancy, revenue, status_counts)` — bar chart of occupancy per month (0-100%), bar chart of revenue per month, and the counts. Build the Figure once in __init__ and only clear and redraw the axes here (ax.clear(), ax.bar(...), canvas.draw_idle()).

> **Exit condition:** a complete project book in which every number comes from a run on your computer.
