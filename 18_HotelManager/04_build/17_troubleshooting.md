# Chapter 17 — When something breaks

| You see | What it means | Fix |
|---|---|---|
| `NotImplementedError` | that function is not written yet | read the traceback: which file, which function |
| `ModuleNotFoundError: hotelmanager` | you are in the wrong folder | `cd` to the folder that contains `config.py` |
| `ModuleNotFoundError: matplotlib` | the venv is not active | `.venv\Scripts\activate`, then `pip install -r requirements.txt` |
| `test_overlap_cases[other5]` fails | `<=` instead of `<` in `overlaps` | guide 3.4, case F |
| `ValueError: check-out must be after check-in` in a test that should pass | your `__post_init__` uses `<` instead of `<=` | zero-night stays must also be refused |
| `sqlite3.IntegrityError: UNIQUE constraint failed: rooms.number` | you added the same room number twice | catch it in `add_room` and raise a readable `HotelError` |
| `sqlite3.IntegrityError: CHECK constraint failed` | a value the database refuses (status, capacity, dates) | print the object before saving; the Python-side check is missing |
| `sqlite3.IntegrityError: FOREIGN KEY constraint failed` | a room_id or guest_id that does not exist | you saved a booking before its room/guest, or used the wrong id |
| deleting a room does nothing / no error | `PRAGMA foreign_keys = ON` missing | it must run on **every** connection |
| `TypeError: 'NoneType' object is not subscriptable` after `get()` | the row was not found and you used the result anyway | check for `None` and raise `HotelError("... not found")` |
| `KeyError: 'room_number'` in `_row` | you used a plain `SELECT *` instead of `self.SELECT` (which joins) | use `self.SELECT` |
| dates come back as strings | you forgot `date.fromisoformat(...)` in `_row` | convert in one place only — the repository |
| the total is a few agorot off | rounding in two places | round **once**, in `InvoiceLine.amount` and in `Quote.total` |
| `test_long_stay_discount` fails | your discount rule runs before the weekend rule, or is positive | order in `PricingEngine.rules`; the amount must be negative |
| the booking list is empty although rows exist | `list_all` filtered by a status that is `None` vs `""` | pass `None`, not `""` |
| `_tkinter.TclError: image doesn't exist` / grey window | a widget referenced after `destroy` | rebuild the tab instead of reusing dead widgets |
| the window opens and closes instantly | an exception in `AppController.__init__` | run `python run.py` from the terminal and read the traceback |
| the calendar is empty | `calendar_matrix` returned bookings whose status does not block the room | check `Booking.occupies` |
| everything is slow with many bookings | you used `list_all()` where `in_period()` belongs | guide 3.6 |

**The method, always:** last line of the traceback = *what*; first line inside your own file = *where*;
`print(type(x), x)` just above it; reproduce with one test instead of the whole app; and write every
bug that cost you more than half an hour into `TASKS.md` — that list becomes chapter 4 of the book
("challenges") and the answer to "what was the hardest part?"
