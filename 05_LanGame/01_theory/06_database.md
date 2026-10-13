# Chapter 6 — The database

## 6.1 Why a database and not a JSON file

Questions, games, players and answers are four kinds of things with relations between them
(an answer belongs to a player *and* a question *and* a game). A relational database keeps the
relations consistent, lets you ask questions like "which question is answered wrong most often",
and survives two programs (server and admin) using it at the same time. SQLite does this in a
single file, with no server to install — the right size for this project.

## 6.2 The schema

Four tables (`langame/database/db.py` → `SCHEMA`):

📄 **Tables and relations**
```text
questions (id, text, option_a..d, correct_index, category, difficulty, created_at)
games     (id, started_at, ended_at, questions_count, time_limit, category, winner_name)
players   (id, game_id -> games, name, address, joined_at, final_score)
answers   (id, game_id -> games, player_id -> players, question_id -> questions,
           chosen_index, is_correct, response_time, points)

games 1 ──▶ * players
games 1 ──▶ * answers
players 1 ──▶ * answers
questions 1 ──▶ * answers
```

- **Primary key** (`id INTEGER PRIMARY KEY AUTOINCREMENT`) — a unique number SQLite assigns.
- **Foreign key** (`game_id REFERENCES games(id)`) — the value must exist in the other table.
- **`ON DELETE CASCADE`** — deleting a game deletes its players and answers automatically.
- **`CHECK (correct_index BETWEEN 0 AND 3)`** — the DB itself refuses bad data.
- **Index** on `(category, difficulty)` — makes "all networks questions" a tree lookup instead of a table scan.

💡 In SQLite, foreign keys are **off** by default. `PRAGMA foreign_keys = ON` must be executed
on every connection, or the cascade silently does nothing. `Database.get_connection()` does it.

## 6.3 Transactions — all or nothing

Saving a finished game means: insert 1 game row, 8 player rows, 80 answer rows. If the process is
killed after 40 answers, you do not want half a game in the database. A **transaction** groups the
writes: `commit()` makes all of them real at once; `rollback()` throws all of them away.

📄 **`Database.connection()` — the context manager**
```python
@contextmanager
def connection(self):
    conn = self.get_connection()
    try:
        yield conn            # the `with` body runs here
        conn.commit()         # body finished -> make it real
    except Exception:
        conn.rollback()       # body raised -> undo everything
        raise
    finally:
        conn.close()
```

`GameRepository.save_game` does everything inside one `with self.db.connection() as conn:` block.
That is the whole trick. `tests/test_repositories.py` checks that a saved game comes back complete.

## 6.4 Threads and SQLite

The server writes from the engine's thread, from the timer thread and (through commands) from the
handler threads. SQLite connections must not be shared between threads — so we never share one:
every operation opens its own short-lived connection through `connection()` and closes it. That is
slightly slower than a pooled connection and completely safe. `check_same_thread=False` is set so
that a connection created in one thread can be closed in another if it ever happens.

## 6.5 Parameters, never string formatting

📄 **The only correct way to put values into SQL**
```python
conn.execute("SELECT id FROM questions WHERE category = ?", (category,))     # correct
conn.execute(f"SELECT id FROM questions WHERE category = '{category}'")      # NEVER
```

With the second form, a category named `x' OR '1'='1` returns every row — this is **SQL injection**.
With `?` placeholders the value is data, never code. An examiner will ask about this.

## 6.6 Useful queries for the results chapter

📄 **Hardest questions**
```sql
SELECT q.text,
       COUNT(a.id)          AS times_asked,
       AVG(a.is_correct)    AS pct_correct,
       AVG(a.response_time) AS avg_seconds
FROM questions q
LEFT JOIN answers a ON a.question_id = q.id
GROUP BY q.id
HAVING times_asked > 0
ORDER BY pct_correct ASC
LIMIT 10;
```

📄 **Average response time per player across all games**
```sql
SELECT p.name, COUNT(a.id) AS answers, AVG(a.response_time) AS avg_seconds, SUM(a.points) AS total
FROM players p JOIN answers a ON a.player_id = p.id
GROUP BY p.name ORDER BY total DESC;
```

These two tables, from real classroom games, are the difference between a results chapter and a
list of features.

## ✅ Check yourself — Chapter 6

1. You delete a game. What happens to its rows in `players` and `answers`, and which two things
   must be true for that to work?
2. `save_game` raises an exception while inserting the 30th answer. How many rows of that game
   are in the database afterwards? Why?
3. A user types the category `networks'; DROP TABLE questions; --` into the admin tool. What
   happens with `?` placeholders? Without them?
4. Why does `QuestionManager` ask for `list_ids()` and not `list_all()` at game start?
5. Write a query that returns the number of games each player name has won.
6. What does `CHECK (correct_index BETWEEN 0 AND 3)` protect against that Python code might not?

## 📚 Further reading — Chapter 6

- **Python docs — sqlite3**: https://docs.python.org/3/library/sqlite3.html — placeholders,
  `row_factory`, transactions, `executemany`.
- **SQLite — Foreign Key Support**: https://www.sqlite.org/foreignkeys.html
- **SQLite — Query Planning (what an index does)**: https://www.sqlite.org/queryplanner.html
- **SQLBolt — interactive SQL lessons**: https://sqlbolt.com/ — lessons 1–12 cover everything used here.
- **DB Browser for SQLite** (to look at your file): https://sqlitebrowser.org/
