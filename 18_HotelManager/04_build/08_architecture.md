# Chapter 8 — How the code is organised, and your work plan

## 8.1 The layers

```
      views/            Tkinter only. No rules, no SQL, no prices.
         ▲  ▼           (plain values in, ready objects out)
   controllers/         AppController: button -> service -> screen
         ▲  ▼
   booking/hotel_service.py     ALL the rules + the state machine     (Facade)
      ├── booking/availability.py + models/date_range.py   [algorithm 1]
      ├── booking/allocation.py                            [algorithm 2]
      ├── pricing/engine.py + pricing/rules.py             [algorithm 3]
      └── database/repositories.py  -> database/db.py (SQLite)
```

**The rule that keeps it honest:** a view never imports `HotelService` or a repository, and the service
never imports `tkinter`. That is why `pytest` can drive the entire system with no window open — and why
you can answer "how did you test a GUI application?" with "I did not need to; the rules are separate".

Check it yourself at any time:
```
grep -rn "tkinter" hotelmanager/booking hotelmanager/pricing hotelmanager/database   (must print nothing)
grep -rn "hotel_service\|repositories" hotelmanager/views                            (must print nothing)
```

## 8.2 Every file in one sentence, in the order you will write them

| Stage | File | One sentence |
|---|---|---|
| — | `config.py` | Every number the hotel might change. Complete — read it once. |
| 1 | `models/date_range.py` | The stay and the overlap rule. **Start here.** |
| 1 | `models/entities.py` | Room, Guest, Booking, statuses, invoice lines. Mostly given. |
| 2 | `database/db.py` | Connection, transaction, schema. |
| 2 | `database/repositories.py` | All the SQL, one class per table. |
| 3 | `booking/availability.py` | Is a room free? Which rooms are free? |
| 3 | `booking/allocation.py` | Three strategies + the factory. |
| 4 | `pricing/rules.py` | One class per pricing rule. |
| 4 | `pricing/engine.py` | Runs the rules in order → `Quote`. |
| 5 | `booking/hotel_service.py` | All the rules + the state machine. The centre of the project. |
| 6 | `views/*.py` | Five tabs + shared widgets. |
| 6 | `controllers/app_controller.py` | Connects them. |
| 6 | `booking/importer.py` | CSV import / invoice export. |
| 7 | reports, occupancy, the experiment | Numbers for the book. |

## 8.3 The routine for every stage

1. Open `TASKS.md` and read the stage.
2. Open this guide at the matching chapter in Part B.
3. Open the first file. Read the class docstring, then the function docstring — the steps are numbered there.
4. Delete `raise NotImplementedError` and write the body. **Two lines, then run the test.**
5. Red? Read the traceback bottom-up (chapter 2.8), fix, run again.
6. Green? `git add . && git commit -m "stage N: ..." && git push`, and send Ahmad the `pytest` output.

## 8.4 A realistic timetable (about 8–9 weeks, 4–6 hours each)

| Week | Do | Done when |
|---|---|---|
| 1 | Install everything. Read Part A (chapters 1–8). Answer the ✅ questions. | You can draw the eight overlap cases from memory. |
| 2 | Stage 1 — `DateRange`, `Room.fits`, `Booking.occupies`. | `test_date_range.py` green (12 tests). |
| 3 | Stage 2 — database + repositories. | `test_repositories.py` green; you can see rows in DB Browser. |
| 4 | Stage 3 — availability + allocation. | `test_availability_allocation.py` green (12 tests). |
| 5 | Stage 4 — the pricing engine. | `test_pricing.py` green (8); your hand calculation matches. |
| 6 | Stage 5 — the service and the state machine. | `pytest -v` all 49 green. |
| 7–8 | Stage 6 — the five tabs and the calendar. | `python run.py` does a full booking cycle. |
| 9 | Stage 7 — reports, the allocation experiment, UML, the book. | Every number in the book comes from your computer. |

If a week slips, it slips. **Never** skip a stage's exit condition to catch up — a skipped test comes
back as a bug you cannot find.

## 8.5 When you are stuck (in this order)

1. Read the traceback bottom-up: which file, which line, which error?
2. Print the thing: `print(type(x), x)` on the line before the failure.
3. Chapter 17 of this guide — the troubleshooting table.
4. Re-read the function's docstring slowly; the steps are numbered.
5. Search the **exact** error text (without your file names) on Google.
6. Ask Ahmad — with the traceback and what you already tried. "It doesn't work" gets nothing;
   "line 44 raises KeyError 'capacity', my SELECT is `SELECT id, number FROM rooms`, here is the code"
   gets an answer in two minutes.
