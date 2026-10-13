"""Automatic checks for exercises.py.   Run:  pytest test_exercises.py -v

Every test is named after its exercise, so  pytest -k ex10  runs just that one.
"""
import importlib
import os
import sqlite3
from datetime import date, datetime

import pytest

ex = importlib.import_module(os.environ.get("EXERCISES", "exercises"))


def d(day, month=3):
    return date(2026, month, day)


def room(number, room_type, capacity, floor, view, rate):
    return {"number": number, "room_type": room_type, "capacity": capacity, "floor": floor, "view": view, "rate": rate}


R101 = room("101", "single", 1, 1, "garden", 320.0)
R102 = room("102", "double", 2, 1, "garden", 450.0)
R104 = room("104", "family", 4, 1, "garden", 620.0)
R106 = room("106", "double", 2, 1, "sea", 450.0)
R206 = room("206", "double", 2, 2, "sea", 450.0)
R305 = room("305", "suite", 3, 3, "sea", 900.0)


def test_ex01_nights():
    assert ex.ex01_nights(d(3), d(7)) == 4
    assert ex.ex01_nights(d(28, 2), d(2)) == 2
    with pytest.raises(ValueError):
        ex.ex01_nights(d(7), d(7))


@pytest.mark.parametrize("c,e,expected", [
    (5, 9, True), (1, 5, True), (4, 6, True), (1, 9, True), (3, 7, True),
    (7, 9, False),        # case F: arrives the morning the other guest leaves
    (1, 3, False), (9, 11, False)])
def test_ex02_all_eight_cases(c, e, expected):
    assert ex.ex02_overlaps(d(3), d(7), d(c), d(e)) is expected
    assert ex.ex02_overlaps(d(c), d(e), d(3), d(7)) is expected       # symmetric


def test_ex03_is_room_free():
    bookings = [{"id": 1, "room": "204", "check_in": d(3), "check_out": d(7), "status": "CONFIRMED"},
                {"id": 2, "room": "204", "check_in": d(10), "check_out": d(12), "status": "CANCELLED"},
                {"id": 3, "room": "205", "check_in": d(1), "check_out": d(20), "status": "CHECKED_IN"}]
    assert ex.ex03_is_room_free("204", d(5), d(9), bookings) is False
    assert ex.ex03_is_room_free("204", d(7), d(9), bookings) is True
    assert ex.ex03_is_room_free("204", d(10), d(12), bookings) is True          # cancelled frees the room
    assert ex.ex03_is_room_free("204", d(4), d(8), bookings, ignore_id=1) is True
    assert ex.ex03_is_room_free("205", d(5), d(6), bookings) is False


def test_ex04_busy_rooms_sql():
    conn = sqlite3.connect(":memory:")
    conn.execute("CREATE TABLE bookings (id INTEGER PRIMARY KEY, room TEXT, check_in TEXT, check_out TEXT, status TEXT)")
    conn.executemany("INSERT INTO bookings VALUES (?, ?, ?, ?, ?)", [
        (1, "101", "2026-03-03", "2026-03-07", "CONFIRMED"),
        (2, "102", "2026-03-07", "2026-03-09", "CONFIRMED"),     # starts the day we leave
        (3, "103", "2026-03-01", "2026-03-04", "CANCELLED"),
        (4, "104", "2026-02-25", "2026-03-04", "CHECKED_IN"),
        (5, "105", "2026-03-01", "2026-03-03", "CHECKED_OUT")])
    assert ex.ex04_busy_rooms_sql(conn, d(3), d(7)) == ["101", "104"]


def test_ex05_first_fit():
    assert ex.ex05_first_fit([R206, R104, R102], 2)["number"] == "102"
    assert ex.ex05_first_fit([R101, R102], 3) is None
    assert ex.ex05_first_fit([], 1) is None


def test_ex06_best_fit_keeps_the_family_room():
    assert ex.ex06_best_fit([R104, R206, R102], 2)["number"] == "102"
    assert ex.ex06_best_fit([R104, R305], 2)["number"] == "305"          # capacity 3 < 4
    assert ex.ex06_best_fit([R104, R102, R101], 1)["number"] == "101"
    assert ex.ex06_best_fit([R101], 2) is None


def test_ex07_preference():
    assert ex.ex07_preference([R102, R206, R104], 2, {"view": "sea", "floor": 2})["number"] == "206"
    assert ex.ex07_preference([R102, R106], 2, {})["number"] == "102"                 # tie -> lower number
    assert ex.ex07_preference([R104, R106], 2, {"view": "garden"})["number"] == "104"  # 3 - 2 = 1 > 0
    assert ex.ex07_preference([R101], 2, {}) is None


def test_ex08_night_prices():
    assert ex.ex08_night_prices(450.0, d(2), d(9), []) == {450.0: 7}
    seasons = [(d(6), d(10), 1.5)]
    assert ex.ex08_night_prices(450.0, d(5), d(8), seasons) == {450.0: 1, 675.0: 2}


def test_ex09_weekend_surcharge():
    assert ex.ex09_weekend_surcharge(450.0, d(2), d(9), []) == pytest.approx(180.0)
    assert ex.ex09_weekend_surcharge(450.0, d(5), d(8), [(d(6), d(10), 1.5)]) == pytest.approx(270.0)
    assert ex.ex09_weekend_surcharge(450.0, d(2), d(5), []) == 0.0


def test_ex10_the_worked_examples():
    assert ex.ex10_quote_total(450.0, d(2), d(9), 2, breakfast=True) == pytest.approx(4445.06)
    assert ex.ex10_quote_total(450.0, d(5), d(8), 2, seasons=[(d(6), d(10), 1.5)]) == pytest.approx(2442.60)


def test_ex11_next_state():
    assert ex.ex11_next_state("CONFIRMED", "check_in") == "CHECKED_IN"
    assert ex.ex11_next_state("CHECKED_IN", "check_out") == "CHECKED_OUT"
    assert ex.ex11_next_state("CONFIRMED", "cancel") == "CANCELLED"
    for state, event in [("CHECKED_IN", "cancel"), ("CONFIRMED", "check_out"), ("CHECKED_OUT", "check_in"),
                         ("CANCELLED", "check_in")]:
        with pytest.raises(ValueError) as err:
            ex.ex11_next_state(state, event)
        assert state in str(err.value)


def test_ex12_cancellation_fee():
    assert ex.ex12_cancellation_fee(d(10), 450.0, datetime(2026, 3, 7, 12)) == 0.0
    assert ex.ex12_cancellation_fee(d(10), 450.0, datetime(2026, 3, 8, 14)) == 0.0      # exactly 48 h
    assert ex.ex12_cancellation_fee(d(10), 450.0, datetime(2026, 3, 8, 14, 1)) == 450.0
    assert ex.ex12_cancellation_fee(d(10), 450.0, datetime(2026, 3, 9, 9)) == 450.0


def _invoice_db():
    conn = sqlite3.connect(":memory:")
    conn.executescript("""
        CREATE TABLE invoices (id INTEGER PRIMARY KEY, booking_id INTEGER, total REAL);
        CREATE TABLE invoice_lines (invoice_id INTEGER, description TEXT NOT NULL, amount REAL);""")
    return conn


def test_ex13_write_invoice():
    conn = _invoice_db()
    inv = ex.ex13_write_invoice(conn, 7, [("4 nights", 2480.0), ("VAT", 446.4)])
    assert conn.execute("SELECT booking_id, total FROM invoices WHERE id = ?", (inv,)).fetchone() == (7, 2926.4)
    assert conn.execute("SELECT COUNT(*) FROM invoice_lines WHERE invoice_id = ?", (inv,)).fetchone()[0] == 2


def test_ex13_all_or_nothing():
    conn = _invoice_db()
    with pytest.raises(sqlite3.IntegrityError):
        ex.ex13_write_invoice(conn, 8, [("2 nights", 900.0), (None, 50.0)])
    assert conn.execute("SELECT COUNT(*) FROM invoices").fetchone()[0] == 0
    assert conn.execute("SELECT COUNT(*) FROM invoice_lines").fetchone()[0] == 0
