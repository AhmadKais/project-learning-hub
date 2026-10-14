"""Lesson 33 - the database: tables and constraints, transactions (all or nothing), indexes (measured), injection."""
import random
import sqlite3
import sys
import time
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)

SCHEMA = """
CREATE TABLE rooms (id INTEGER PRIMARY KEY, number TEXT NOT NULL UNIQUE, capacity INTEGER CHECK (capacity > 0));
CREATE TABLE bookings (
    id INTEGER PRIMARY KEY, room_id INTEGER NOT NULL REFERENCES rooms(id) ON DELETE RESTRICT,
    check_in TEXT NOT NULL, check_out TEXT NOT NULL, status TEXT NOT NULL,
    CHECK (check_out > check_in),
    CHECK (status IN ('confirmed', 'checked_in', 'checked_out', 'cancelled')));
"""
AVAIL = """SELECT COUNT(*) FROM bookings
           WHERE room_id = ? AND check_in < ? AND ? < check_out AND status IN ('confirmed', 'checked_in')"""


def make_db(n_bookings, index):
    db = sqlite3.connect(":memory:")
    db.executescript(SCHEMA)
    db.executemany("INSERT INTO rooms (number, capacity) VALUES (?, ?)", [(str(100 + i), 2) for i in range(60)])
    r = random.Random(1)
    start = date(2024, 1, 1)
    rows = []
    for _ in range(n_bookings):
        a = start + timedelta(r.randrange(900))
        rows.append((r.randrange(1, 61), a.isoformat(), (a + timedelta(r.randrange(1, 8))).isoformat(),
                     r.choice(["confirmed", "checked_out", "cancelled", "checked_in"])))
    db.executemany("INSERT INTO bookings (room_id, check_in, check_out, status) VALUES (?, ?, ?, ?)", rows)
    if index:
        db.execute("CREATE INDEX idx_booking_room_dates ON bookings (room_id, check_in, check_out)")
    return db


def time_query(db, reps=300):
    r = random.Random(2)
    t0 = time.perf_counter()
    for _ in range(reps):
        a = date(2024, 1, 1) + timedelta(r.randrange(900))
        db.execute(AVAIL, (r.randrange(1, 61), (a + timedelta(3)).isoformat(), a.isoformat())).fetchone()
    return (time.perf_counter() - t0) / reps * 1000


# ---------------------------------------------------------------- 1. index: measured + the query plan
if L.wanted("index"):
    sizes = [1_000, 5_000, 20_000, 50_000, 100_000]
    no_idx = [time_query(make_db(n, False)) for n in sizes]
    idx = [time_query(make_db(n, True)) for n in sizes]
    db_a, db_b = make_db(20_000, False), make_db(20_000, True)
    plan_a = " ".join(r[-1] for r in db_a.execute("EXPLAIN QUERY PLAN " + AVAIL, (5, "2024-03-10", "2024-03-07")))
    plan_b = " ".join(r[-1] for r in db_b.execute("EXPLAIN QUERY PLAN " + AVAIL, (5, "2024-03-10", "2024-03-07")))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5), gridspec_kw={"width_ratios": [1.2, 1]})
    a1.plot(sizes, no_idx, "o-", color=RED, label="no index: read every row")
    a1.plot(sizes, idx, "s-", color=GREEN, label="index on (room_id, check_in, check_out)")
    a1.set_xlabel("bookings in the table")
    a1.set_ylabel("ms per availability query")
    a1.set_title("Is room 5 free from … to …? — measured with SQLite")
    a1.legend()
    blank(a2)
    a2.text(0.02, 0.85, "EXPLAIN QUERY PLAN  (20,000 bookings)", fontsize=13, weight="bold")
    a2.text(0.02, 0.68, "without the index:", fontsize=12, color=RED)
    a2.text(0.02, 0.58, plan_a, fontsize=12, family="monospace")
    a2.text(0.02, 0.4, "with the index:", fontsize=12, color=GREEN)
    a2.text(0.02, 0.22, plan_b.replace(" USING", "\nUSING").replace(" (", "\n("), fontsize=11.5, family="monospace")
    print("  sizes", sizes, "\n  no index ms", np.round(no_idx, 3), "\n  index ms", np.round(idx, 3))
    print("  plans:", plan_a, "|", plan_b)
    L.save(fig, "index")

# ---------------------------------------------------------------- 2. what an index is: a sorted lookup
if L.wanted("btree"):
    fig, ax = plt.subplots(figsize=(14, 5.4))
    blank(ax)
    box(ax, 0.42, 0.78, 0.16, 0.12, "room ≤ 30 ?", color=VIOLET, weight="bold")
    for i, (x, label) in enumerate([(0.18, "room ≤ 15 ?"), (0.66, "room ≤ 45 ?")]):
        box(ax, x, 0.52, 0.16, 0.12, label, color=VIOLET)
        arrow(ax, (0.5, 0.78), (x + 0.08, 0.64))
    leaves = [(0.02, "rooms 1-15"), (0.24, "rooms 16-30"), (0.52, "rooms 31-45"), (0.76, "rooms 46-60")]
    for x, label in leaves:
        box(ax, x, 0.22, 0.2, 0.14, f"{label}\nsorted by check_in\n→ row ids", color=AQUA, fontsize=10.5)
    for (x1, _), (x2, _) in zip([(0.18, 0), (0.18, 0), (0.66, 0), (0.66, 0)], leaves):
        arrow(ax, (x1 + 0.08, 0.52), (x2 + 0.1, 0.36), color=MUTED)
    ax.add_patch(plt.Rectangle((0.02, 0.2), 0.2, 0.18, fill=False, ec=ORANGE, lw=3))
    ax.text(0.5, 0.06, "room 5, March 2024:  2 questions down the tree, then read only the few rows of room 5 "
                       "around that date - instead of all 20,000", ha="center", fontsize=12)
    ax.set_title("An index = a sorted copy of some columns, kept as a tree (like the index at the back of a book)")
    L.save(fig, "btree")

# ---------------------------------------------------------------- 3. a transaction: all or nothing
if L.wanted("transaction"):
    steps = [("UPDATE bookings SET status = 'checked_out'", True), ("INSERT INTO invoices …", True),
             ("INSERT INTO invoice_lines …  (base)", True), ("INSERT INTO invoice_lines …  (weekend)", True),
             ("✗ POWER CUT / exception here", False)]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5.2))
    frames = list(range(len(steps) + 1)) + [len(steps) + 1] * 3

    def panel(ax, k, with_tx):
        blank(ax)
        for i, (sql, ok) in enumerate(steps[:min(k, len(steps))]):
            y = 0.82 - i * 0.12
            col = INK if ok else RED
            ax.text(0.03, y, ("✓ " if ok else "") + sql, fontsize=11.5, family="monospace" if ok else None, color=col)
        if k > len(steps):
            if with_tx:
                ax.text(0.5, 0.12, "ROLLBACK → the database is exactly as before\n(the booking is still CHECKED_IN, no half invoice)",
                        ha="center", fontsize=12.5, color=GREEN, weight="bold")
            else:
                ax.text(0.5, 0.12, "the first 4 writes STAY: a checked-out booking\nwith half an invoice - corrupt data",
                        ha="center", fontsize=12.5, color=RED, weight="bold")
        ax.set_title("WITH a transaction (with db.connection() as conn:)" if with_tx else "WITHOUT a transaction",
                     fontsize=13)

    L.animate(fig, lambda f: (panel(a1, frames[f], False), panel(a2, frames[f], True)), len(frames), "transaction", fps=1)

# ---------------------------------------------------------------- 4. SQL injection: f-string vs parameter
if L.wanted("injection"):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE guests (name TEXT)")
    db.executemany("INSERT INTO guests VALUES (?)", [("Dana",), ("Omar",), ("Lior",)])
    evil = "x' OR '1'='1"
    unsafe_sql = f"SELECT name FROM guests WHERE name = '{evil}'"
    unsafe = [r[0] for r in db.execute(unsafe_sql)]
    safe = [r[0] for r in db.execute("SELECT name FROM guests WHERE name = ?", (evil,))]
    fig, ax = plt.subplots(figsize=(14, 4.8))
    blank(ax)
    ax.text(0.02, 0.88, f"someone types into the search box:   {evil}", fontsize=13, weight="bold")
    ax.text(0.02, 0.68, "WRONG  f-string:", fontsize=12.5, color=RED, weight="bold")
    ax.text(0.2, 0.68, unsafe_sql, fontsize=11.5, family="monospace")
    ax.text(0.2, 0.58, f"→ returns {unsafe}  (every guest!)", fontsize=12, color=RED)
    ax.text(0.02, 0.38, "RIGHT  parameter:", fontsize=12.5, color=GREEN, weight="bold")
    ax.text(0.2, 0.38, 'execute("SELECT name FROM guests WHERE name = ?", (text,))', fontsize=11.5, family="monospace")
    ax.text(0.2, 0.28, f"→ returns {safe}  (the text is only ever a VALUE, never SQL)", fontsize=12, color=GREEN)
    ax.text(0.02, 0.08, "With ; DROP TABLE … the f-string version could delete data.  Parameters always.",
            fontsize=12, color=INK2)
    L.save(fig, "injection")

# ---------------------------------------------------------------- 5. constraints: the database says no
if L.wanted("constraints"):
    db = sqlite3.connect(":memory:")
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript(SCHEMA)
    db.execute("INSERT INTO rooms (number, capacity) VALUES ('102', 2)")
    db.execute("INSERT INTO bookings (room_id, check_in, check_out, status) VALUES (1, '2026-03-02', '2026-03-09', 'confirmed')")
    tries = [("INSERT INTO rooms (number, capacity) VALUES ('102', 2)", "two rooms called 102"),
             ("INSERT INTO rooms (number, capacity) VALUES ('999', 0)", "a room with zero beds"),
             ("INSERT INTO bookings (room_id, check_in, check_out, status) VALUES (1, '2026-03-09', '2026-03-02', 'confirmed')",
              "a stay that ends before it starts"),
             ("INSERT INTO bookings (room_id, check_in, check_out, status) VALUES (1, '2026-04-01', '2026-04-03', 'confimed')",
              "a typo becoming a state"),
             ("INSERT INTO bookings (room_id, check_in, check_out, status) VALUES (77, '2026-04-01', '2026-04-03', 'confirmed')",
              "a booking for a missing room"),
             ("DELETE FROM rooms WHERE number = '102'", "deleting a room that has bookings")]
    fig, ax = plt.subplots(figsize=(15, 5.4))
    blank(ax)
    for i, (sql, what) in enumerate(tries):
        try:
            db.execute(sql)
            res, col = "accepted?!", RED
        except sqlite3.IntegrityError as e:
            res, col = f"IntegrityError: {e}", GREEN
        y = 0.88 - i * 0.15
        ax.text(0.01, y, f"✗ {what}", fontsize=12.5, weight="bold")
        ax.text(0.33, y, res, fontsize=11.5, color=col, family="monospace")
    ax.set_title("Constraints: the database refuses nonsense even if a Python bug tries  (PRAGMA foreign_keys = ON!)",
                 fontsize=13)
    L.save(fig, "constraints")
