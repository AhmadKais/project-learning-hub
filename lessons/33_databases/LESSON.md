# Lesson 33 — The database: constraints, transactions, indexes, parameters

> **For:** Eran (HotelManager) · Liraz (LanGame) · every project with SQLite &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** basic SQL (SELECT, INSERT, WHERE) &nbsp;·&nbsp; **After this:** the database chapter of the book

## The story

> Three bad days at the hotel:
>
> 1. **Monday:** a bug in the program saves a booking that **ends before it starts** (check-out 2 March, check-in 9 March).
>    Reports go crazy.
> 2. **Wednesday:** during a guest's check-out the power goes out. The booking says "checked out", but the invoice has only
>    **half its lines**. The guest is billed wrong.
> 3. **Friday:** the hotel has 100,000 old bookings; checking "is room 5 free?" now takes so long that the receptionist waits.
>
> Plus, a student types `x' OR '1'='1` into the guest search box and sees **every guest's** details. This lesson gives one
> database tool for each problem: **constraints**, **transactions**, **indexes** and **parameters**.

## 🎯 By the end, the student can

1. Explain primary key, foreign key and CHECK constraints, and why the database checks what Python already checks.
2. Explain a transaction (all or nothing) and write one with `with db.connection() as conn:`.
3. Explain what an index is, read `EXPLAIN QUERY PLAN`, and show the speed-up with a measurement.
4. Explain SQL injection and why queries always use `?` parameters.

## Words you need

| word | meaning |
|---|---|
| **table, row, column** | like a spreadsheet: a table of rows (records) and columns (fields) |
| **primary key** | a column with a unique id for each row |
| **foreign key** | a column that must point to an existing row of another table (`room_id` → rooms) |
| **constraint** | a rule the **database itself** enforces: refuse rows that break it |
| **transaction** | a group of changes that happen **all together or not at all** |
| **commit / rollback** | make the group real / throw the whole group away |
| **index** | a sorted copy of some columns, so searches don't read every row |
| **query plan** | how SQLite will run a query: `SCAN` (read everything) or `SEARCH … USING INDEX` |
| **SQL injection** | text typed by a user becomes part of the SQL command |
| **parameter (`?`)** | a placeholder: the value is sent separately and is never treated as SQL |

---

## 1. Constraints — the database says no (Monday's problem)

![constraints](figs/constraints.png)

Every line above is a real `IntegrityError` from this lesson's script: the database **refuses** the bad row.

| constraint | prevents |
|---|---|
| `PRIMARY KEY` | two rows with the same id |
| `UNIQUE` | two rooms called "102", the same guest entered twice |
| `CHECK (check_out > check_in)` | a stay that ends before it starts — Monday's bug |
| `CHECK (status IN (...))` | a typo ("confimed") becoming a state |
| `REFERENCES rooms(id) ON DELETE RESTRICT` | deleting a room that has bookings |
| `ON DELETE CASCADE` | leftover answers / invoice lines when their parent is deleted |

**Why check in the database if Python already checks?** "Defence in depth": the Python check protects the **user**; the
database check protects the **data** — from a future bug, another program, or someone editing the file by hand.

⚠️ **SQLite ships with foreign keys switched OFF.** Every connection must run `PRAGMA foreign_keys = ON`, otherwise RESTRICT and
CASCADE silently do nothing. A favourite examiner question. (`Database.get_connection()` does it.)

## 2. Transactions — all or nothing (Wednesday's problem)

![transaction](figs/transaction.gif)

Check-out = update the booking + insert the invoice + insert its lines: 4 or more changes. If the program stops half-way,
half-written data is **worse than nothing**. A transaction groups them:

```python
@contextmanager
def connection(self):
    conn = self.get_connection()
    try:
        yield conn            # the code inside `with db.connection() as conn:` runs here
        conn.commit()         # finished without an error → make ALL changes real
    except Exception:
        conn.rollback()       # any error → throw ALL changes away
        raise
    finally:
        conn.close()
```

**Analogy:** a bank transfer — take 100 ₪ from account A **and** add 100 ₪ to account B. Never just one of them.

## 3. Indexes — measured (Friday's problem)

![index measured](figs/index.png)

"Is room 5 free between these dates?" on 20,000 bookings: about **0.9 ms** reading every row (`SCAN bookings`) vs about
**0.03 ms** with an index (`SEARCH … USING INDEX`) — some 35× faster, and the gap grows with the table (100,000 rows: ~4.5 ms
vs ~0.12 ms). Other computers give other milliseconds; the shape is always the same.

![what an index is](figs/btree.png)

An index is a **sorted copy** of some columns, kept as a tree — like the index at the back of a book, or a phone book sorted by
name: you don't read every page to find "Cohen". The cost: a little disk space and slightly slower inserts. Put an index on
the columns your important `WHERE` uses: Eran's `(room_id, check_in, check_out)`, Liraz's `(category, difficulty)`. Put the
`EXPLAIN QUERY PLAN` output in the book as proof.

## 4. Parameters, never string formatting (the search box)

![SQL injection](figs/injection.png)

```python
db.execute(f"SELECT * FROM guests WHERE name = '{text}'")       # WRONG — the text becomes part of the SQL
db.execute("SELECT * FROM guests WHERE name = ?", (text,))      # RIGHT — the text is only ever a value
```

With the f-string, `x' OR '1'='1` turns the query into `WHERE name = 'x' OR '1'='1'` — always true → every guest. With `?`,
SQLite looks for a guest literally named `x' OR '1'='1` → none.

## 5. Dates as ISO text

Store dates as `'2026-03-02'` (year-month-day). Text in this format sorts in date order, so `check_in < ?` works and the index
can use it. Never `'2/3/2026'`.

## 6. Common mistakes

| student says | the truth |
|---|---|
| "Python already validates, the CHECKs are extra work" | They guard against every *other* way data gets in. |
| "I'll commit after every INSERT, it's safer" | Then a crash leaves half a game / half an invoice. Commit once per action. |
| "Index every column" | Each index costs space and insert time. Index what you search by. |
| "Foreign keys work by default" | Not in SQLite. `PRAGMA foreign_keys = ON` on every connection. |

## 7. Activities

1. **Break the database (10 min).** Open your project's `.sqlite3` file in DB Browser for SQLite and try the six bad inserts
   from §1. Then switch `PRAGMA foreign_keys` off and try again.
2. **Measure (10 min).** `python visualize.py --only index` — then remove the index in your own project and compare
   `EXPLAIN QUERY PLAN`.
3. **Pull the plug (5 min).** In a transaction, insert 3 rows, then `raise Exception` before the end. Count the rows.

## 8. Do it yourself

<details><summary>1. A bug tries to save a booking with check_out = check_in. What happens?</summary>

`CHECK (check_out > check_in)` fails → `IntegrityError` → the row is never stored.
</details>

<details><summary>2. LanGame: `DELETE FROM games WHERE id = 3`. Which rows disappear?</summary>

The game, and — because of `ON DELETE CASCADE` (with foreign keys ON) — its players and answers. The questions stay.
</details>

<details><summary>3. The query plan says `SCAN bookings`. What does it mean and what do you do?</summary>

SQLite reads every row. Add an index on the `WHERE` columns and check that the plan becomes `SEARCH … USING INDEX`.
</details>

## 9. In your project

| Project | Where |
|---|---|
| HotelManager | `hotelmanager/database/db.py` → `get_connection` (PRAGMA), `connection` (transaction), `initialize_schema` · `database/repositories.py` → `BookingRepository.in_period`, `InvoiceRepository.add` · theory `18_HotelManager/01_theory/07_database.md` |
| LanGame | `langame/database/db.py`, `repositories.py` → `GameRepository.save_game` (one transaction) · theory `05_LanGame/01_theory/06_database.md` |
| all the others | `database/db.py` + `repositories.py` in every skeleton — the same ideas |

## 🎬 Watch & explore

* *Database indexes explained* — [search on YouTube](https://www.youtube.com/results?search_query=database+index+explained+b-tree)
* SQLite docs — [EXPLAIN QUERY PLAN](https://sqlite.org/eqp.html) · [Foreign key support](https://sqlite.org/foreignkeys.html)
* xkcd 327 — [Exploits of a Mom ("Bobby Tables")](https://xkcd.com/327/)
