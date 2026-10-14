# Lesson 33 — The database: constraints, transactions, indexes, parameters

> **For:** Eran (HotelManager) · Liraz (LanGame) · and every project with SQLite (all seven) &nbsp;·&nbsp; **Time:** 45 – 60 min
> **Before:** basic SQL (SELECT, INSERT, WHERE) &nbsp;·&nbsp; **After this:** the database chapter of the book

## 🎯 By the end, the student can

1. Explain primary keys, foreign keys and CHECK constraints, and why the database checks what Python already checks.
2. Explain a **transaction** (all or nothing) and write one with `with db.connection() as conn:`.
3. Explain what an **index** is, read `EXPLAIN QUERY PLAN`, and show the speed-up with a measurement.
4. Explain SQL injection and why queries always use `?` parameters.

---

## 1. Constraints — the database says no

![constraints](figs/constraints.png)

Every line above is a real `sqlite3.IntegrityError` from this lesson's script. **Defence in depth:** the Python check
(`DateRange`) protects the user; the database check protects the data from any future bug, another program, or a manual
edit.

| constraint | prevents |
|---|---|
| `PRIMARY KEY` | two rows with the same id |
| `UNIQUE` | two rooms called "102", the same guest twice |
| `CHECK (check_out > check_in)` | a stay that ends before it starts |
| `CHECK (status IN (...))` | a typo ("confimed") becoming a state |
| `REFERENCES rooms(id) ON DELETE RESTRICT` | deleting a room that has bookings |
| `ON DELETE CASCADE` | orphan answers / invoice lines when the parent is deleted |

⚠️ **SQLite ships with foreign keys OFF.** Every connection must run `PRAGMA foreign_keys = ON`, or RESTRICT and CASCADE
silently do nothing. A favourite examiner question. (`Database.get_connection()` does it.)

## 2. Transactions — all or nothing

![transaction](figs/transaction.gif)

Check-out = update the booking + insert an invoice + insert its lines. Saving a LanGame game = 1 game + 8 players + 80
answers. If the program dies halfway, half-written data is **worse than nothing**. A transaction groups the writes:
`commit()` makes them all real at once; `rollback()` throws them all away.

```python
@contextmanager
def connection(self):
    conn = self.get_connection()
    try:
        yield conn            # the body of `with` runs here
        conn.commit()         # no exception → everything is saved
    except Exception:
        conn.rollback()       # any exception → nothing is saved
        raise
    finally:
        conn.close()
```

## 3. Indexes — measured

![index measured](figs/index.png)

"Is room 5 free between these dates?" on 20,000 bookings: about **0.9 ms** reading every row (`SCAN`) vs about **0.03 ms**
with an index (`SEARCH … USING INDEX`) — some 35× faster, and the gap grows with the table (100,000 rows: ~4.5 ms vs
~0.12 ms). Your own computer gives other milliseconds; the shape is always the same.

![what an index is](figs/btree.png)

An index is a **sorted copy** of some columns, kept as a tree — like the index at the back of a book. The cost: a little
space, and slightly slower inserts. Put indexes on the columns your important `WHERE` uses: Eran's
`(room_id, check_in, check_out)`, Liraz's `(category, difficulty)`. Put the `EXPLAIN QUERY PLAN` output in the book — it is
proof.

## 4. Parameters, never string formatting

![SQL injection](figs/injection.png)

```python
db.execute(f"SELECT * FROM guests WHERE name = '{text}'")       # WRONG - the text becomes SQL
db.execute("SELECT * FROM guests WHERE name = ?", (text,))      # RIGHT - the text is only a value
```

## 5. Dates as ISO text

`'2026-03-02'` sorts correctly as text (year, month, day), so `check_in < ?` works on strings and the index can use it.
Never `'2/3/2026'`.

## 6. Misconceptions

| Student says | Truth |
|---|---|
| "Python already validates, the CHECKs are redundant" | They guard against every *other* way data gets in. Cheap insurance. |
| "I'll commit after every insert, it's safer" | Then a crash leaves half a game. Commit once per logical operation. |
| "Indexes on every column" | Each index costs space and insert time. Index what you search by. |
| "Foreign keys work by default" | Not in SQLite. `PRAGMA foreign_keys = ON`, every connection. |

## 7. Activities

1. **Break the database (10 min).** Open `sqlite3` (or DB Browser for SQLite) on your project's DB and try the six inserts
   above. Then turn `PRAGMA foreign_keys` off and try again.
2. **Measure (10 min).** `python visualize.py --only index` — then drop the index in your own project and compare
   `EXPLAIN QUERY PLAN` before/after.
3. **Pull the plug (5 min).** In a transaction, insert 3 rows, then `raise Exception` before the end. Count the rows.

## 8. Check yourself

<details><summary>1. A booking with check_out = check_in gets through the Python code by a bug. What happens?</summary>

The `CHECK (check_out > check_in)` constraint raises `IntegrityError`; the row is never stored.
</details>

<details><summary>2. Which rows does `DELETE FROM games WHERE id = 3` remove in LanGame?</summary>

The game and — because of `ON DELETE CASCADE` (with foreign keys ON) — its players and answers. The questions stay.
</details>

<details><summary>3. The query plan says `SCAN bookings`. What does it mean, and what do you do?</summary>

SQLite reads every row. Add an index on the columns of the `WHERE` (room_id, check_in, check_out) and check that the plan
becomes `SEARCH … USING INDEX`.
</details>

## 9. In your project

| Project | Where |
|---|---|
| HotelManager | `hotelmanager/database/db.py` → `get_connection` (PRAGMA), `connection` (transaction), `initialize_schema` · `database/repositories.py` → `BookingRepository.in_period`, `InvoiceRepository.add` · theory `18_HotelManager/01_theory/07_database.md` |
| LanGame | `langame/database/db.py`, `repositories.py` → `GameRepository.save_game` (one transaction) · theory `05_LanGame/01_theory/06_database.md` |
| all the others | `database/db.py` + `repositories.py` in every skeleton: the same three ideas |

## 🎬 Watch & explore

* *Database indexes explained* — [search on YouTube](https://www.youtube.com/results?search_query=database+index+explained+b-tree)
* SQLite docs — [EXPLAIN QUERY PLAN](https://sqlite.org/eqp.html) and [Foreign key support](https://sqlite.org/foreignkeys.html)
* xkcd 327 — [Exploits of a Mom ("Bobby Tables")](https://xkcd.com/327/) — the classic SQL-injection joke
