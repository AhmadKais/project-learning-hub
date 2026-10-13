# Chapter 7 — The database: six tables that cannot hold nonsense

💡 **In short:** the schema is given to you complete. Your job is to understand *why* every constraint
is there, because the examiner will point at one and ask.

## 7.1 The tables

```
rooms ──────┐
            ├──< bookings >── guests
seasons     │        │
            │        └──< invoices ──< invoice_lines
```
- **rooms** — number (UNIQUE), type, capacity, floor, view, base rate, active
- **guests** — name, email (UNIQUE), phone, document id
- **bookings** — room, guest, check-in, check-out, guests, status, quoted total, extras, timestamps
- **seasons** — name, start, end, multiplier
- **invoices** / **invoice_lines** — one invoice per completed stay, many lines per invoice

## 7.2 Every constraint and its reason

| Constraint | Prevents |
|---|---|
| `number TEXT NOT NULL UNIQUE` (rooms) | two rooms called "204" |
| `email ... UNIQUE` (guests) | the same guest entered twice |
| `CHECK (capacity > 0)` | a room with zero beds |
| `CHECK (check_out > check_in)` | a booking that ends before it starts — **even if a Python bug tries** |
| `CHECK (guests > 0)` | a booking for nobody |
| `CHECK (status IN ('confirmed','checked_in','checked_out','cancelled'))` | a typo like "confimed" becoming a state |
| `REFERENCES rooms(id) ON DELETE RESTRICT` | deleting a room that has bookings (history would break) |
| `REFERENCES invoices(id) ON DELETE CASCADE` | orphan invoice lines when an invoice is removed |
| `INDEX (room_id, check_in, check_out)` | slow availability queries (chapter 3.6) |

❓ *Why put `check_out > check_in` in the database when `DateRange` already checks it?* — **defence in
depth**: the Python check protects the user, the database check protects the data from any future code,
another program, or a manual edit. Both are cheap; a corrupt booking is not.

💡 SQLite ships with foreign keys **disabled**. Every connection must run
`PRAGMA foreign_keys = ON` or RESTRICT and CASCADE silently do nothing. That one line is a favourite
examiner question.

## 7.3 Dates are stored as ISO text

SQLite has no date type. We store `'2026-03-07'` because ISO text sorts **chronologically** as text, so
`ORDER BY check_in` and `WHERE check_in < ?` work exactly as expected. Reading back:
`date.fromisoformat(row["check_in"])`.

## 7.4 The Repository pattern

All SQL lives in `database/repositories.py`, one class per table. Everything else in the project works
with objects:

```python
booking = self.bookings.get(7)         # not: SELECT * FROM bookings WHERE id = 7
```
Benefits you can state: the rules are testable without SQL; moving to PostgreSQL touches one file; and
a `SELECT` never appears in a view, so a UI change cannot break the data layer.

**Always use `?` placeholders**, never string formatting:
```python
conn.execute("SELECT * FROM guests WHERE name LIKE ?", (f"%{text}%",))   # correct
conn.execute(f"SELECT * FROM guests WHERE name LIKE '%{text}%'")          # SQL injection
```
A guest called `O'Brien` breaks the second one; a malicious value can delete your tables.

## 7.5 One query worth understanding

`in_period` is the bridge between the database and algorithm 1:

```sql
SELECT b.*, r.number AS room_number, g.name AS guest_name
FROM bookings b
JOIN rooms r  ON r.id = b.room_id
JOIN guests g ON g.id = b.guest_id
WHERE b.check_in < :end AND b.check_out > :start
ORDER BY b.check_in
```
The `WHERE` is the overlap rule in SQL; the `JOIN`s bring the room number and guest name so the table
can be displayed without extra queries (the "N+1 queries" mistake).

## ✅ Check yourself — Chapter 7

1. Name three CHECK constraints and what each prevents.
2. What is the difference between RESTRICT and CASCADE here? Give an example of each.
3. What happens if you forget `PRAGMA foreign_keys = ON`?
4. Why are dates stored as text, and why ISO specifically?
5. Rewrite `f"... WHERE name = '{name}'"` safely and explain the risk.
6. What does the `WHERE` clause of `in_period` have to do with chapter 3?
