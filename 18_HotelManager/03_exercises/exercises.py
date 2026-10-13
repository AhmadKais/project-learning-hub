"""HotelManager - exercises.

Fill in every function marked TODO. Use only the standard library (datetime, sqlite3).
Check yourself after each exercise:

    pytest test_exercises.py -k ex01 -v        # one exercise
    pytest test_exercises.py -v                # all of them

Stuck for more than 20 minutes? Re-read the theory section named in the
docstring, look at the notebook, and only then open solutions.py.

Rooms are dicts:     {"number": "102", "room_type": "double", "capacity": 2, "floor": 1, "view": "garden", "rate": 450.0}
Bookings are dicts:  {"id": 1, "room": "102", "check_in": date, "check_out": date, "status": "CONFIRMED"}
"""
from datetime import date, datetime, timedelta

BLOCKING = ("CONFIRMED", "CHECKED_IN")


# ---------------------------------------------------------------- algorithm 1: intervals (notebook 01)

def ex01_nights(check_in, check_out):
    """Number of nights of the half-open stay [check_in, check_out). check_out <= check_in -> ValueError.
    Theory 3.2
    """
    raise NotImplementedError("TODO ex01")


def ex02_overlaps(a_in, a_out, b_in, b_out):
    """True if the half-open stays [a_in, a_out) and [b_in, b_out) share at least one night.
    Two comparisons. Theory 3.3
    """
    raise NotImplementedError("TODO ex02")


def ex03_is_room_free(room, check_in, check_out, bookings, ignore_id=None):
    """True if no booking BLOCKS the room for that stay.

    Skip bookings of other rooms, bookings whose status does not block (CANCELLED, CHECKED_OUT), and the booking
    with id == ignore_id (the one being edited). Theory 3.5
    """
    raise NotImplementedError("TODO ex03")


def ex04_busy_rooms_sql(conn, check_in, check_out):
    """The sorted list of room numbers that have a blocking booking overlapping [check_in, check_out).

    Table: bookings(id, room TEXT, check_in TEXT 'YYYY-MM-DD', check_out TEXT, status TEXT).
    Do the filtering IN SQL with the same rule as ex02 (ISO dates compare correctly as text), using ? parameters.
    Theory 3.6
    """
    raise NotImplementedError("TODO ex04")


# ---------------------------------------------------------------- algorithm 2: allocation (notebook 02)

def ex05_first_fit(candidates, guests):
    """The room with the lowest number among those with capacity >= guests. None if there is none."""
    raise NotImplementedError("TODO ex05")


def ex06_best_fit(candidates, guests):
    """Among rooms that fit: smallest capacity, then lowest rate, then lowest number. None if none fits.
    Theory 4.3 - one min() with a key tuple.
    """
    raise NotImplementedError("TODO ex06")


def ex07_preference(candidates, guests, preferences):
    """Among rooms that fit, the highest score; ties -> lowest number. None if none fits.

    score = 3 * (view matches) + 2 * (floor matches) + 1 * (room_type matches) - (capacity - guests)
    preferences is a dict that may contain "view", "floor", "room_type" (missing key = no wish).
    Theory 4.2
    """
    raise NotImplementedError("TODO ex07")


# ---------------------------------------------------------------- algorithm 3: pricing (notebook 03)

def ex08_night_prices(rate, check_in, check_out, seasons):
    """{price: number_of_nights} - one entry per distinct nightly price.

    seasons: list of (start, end, multiplier), half-open like stays. A night inside a season costs
    round(rate * multiplier, 2); otherwise rate. Theory 5.4 "group equal nights"
    """
    raise NotImplementedError("TODO ex08")


def ex09_weekend_surcharge(rate, check_in, check_out, seasons, weekend_days=(4, 5), surcharge=0.20):
    """20% of the (seasonal) price of every night that is a Friday (4) or Saturday (5). Rounded to 2 decimals.
    Theory 5.3 - note: the surcharge is on the SEASONAL price.
    """
    raise NotImplementedError("TODO ex09")


def ex10_quote_total(rate, check_in, check_out, guests, breakfast=False, seasons=()):
    """The total of the five rules in order (theory 5.2), every line rounded to 2 decimals:
        1. base (ex08)   2. weekend (ex09)   3. long stay: -10% of (1+2) if nights >= 7
        4. breakfast: nights * guests * 55 if breakfast   5. VAT: 18% of everything above
    Room 102, Mon 2 -> Mon 9 March 2026, 2 guests, breakfast  ->  4445.06
    """
    raise NotImplementedError("TODO ex10")


# ---------------------------------------------------------------- algorithm 4: the state machine (notebook 04)

def ex11_next_state(state, event):
    """The state after `event`, or ValueError with a message naming the state and the event.

    CONFIRMED --check_in--> CHECKED_IN --check_out--> CHECKED_OUT;  CONFIRMED --cancel--> CANCELLED.
    Theory 6.2
    """
    raise NotImplementedError("TODO ex11")


def ex12_cancellation_fee(check_in, rate, now):
    """0.0 if `now` is at least 48 hours before arrival (14:00 on the check-in day), otherwise one night (rate).
    check_in is a date, now is a datetime. Theory 6.5
    """
    raise NotImplementedError("TODO ex12")


def ex13_write_invoice(conn, booking_id, lines):
    """Insert one row in invoices(id, booking_id, total) and one row per line in
    invoice_lines(invoice_id, description, amount) - ALL OR NOTHING (one transaction).

    lines: list of (description, amount). Returns the new invoice id. If any insert fails, nothing may remain
    and the exception must propagate. Theory 6.5 (atomicity)
    """
    raise NotImplementedError("TODO ex13")
