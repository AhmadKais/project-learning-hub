"""HotelManager - solutions to exercises.py.

Try first. Then compare: there is more than one correct way to write each one.
To run the tests against these solutions:  EXERCISES=solutions pytest test_exercises.py
"""
from datetime import date, datetime, timedelta

BLOCKING = ("CONFIRMED", "CHECKED_IN")


def ex01_nights(check_in, check_out):
    if check_out <= check_in:
        raise ValueError("check-out must be after check-in")
    return (check_out - check_in).days


def ex02_overlaps(a_in, a_out, b_in, b_out):
    return a_in < b_out and b_in < a_out


def ex03_is_room_free(room, check_in, check_out, bookings, ignore_id=None):
    for b in bookings:
        if b["room"] != room or b["status"] not in BLOCKING or b["id"] == ignore_id:
            continue
        if ex02_overlaps(b["check_in"], b["check_out"], check_in, check_out):
            return False
    return True


def ex04_busy_rooms_sql(conn, check_in, check_out):
    rows = conn.execute(
        "SELECT DISTINCT room FROM bookings "
        "WHERE check_in < ? AND check_out > ? AND status IN ('CONFIRMED', 'CHECKED_IN') ORDER BY room",
        (check_out.isoformat(), check_in.isoformat()),
    ).fetchall()
    return [r[0] for r in rows]


def _fitting(candidates, guests):
    return [r for r in candidates if r["capacity"] >= guests]


def ex05_first_fit(candidates, guests):
    fit = _fitting(candidates, guests)
    return min(fit, key=lambda r: int(r["number"])) if fit else None


def ex06_best_fit(candidates, guests):
    fit = _fitting(candidates, guests)
    return min(fit, key=lambda r: (r["capacity"], r["rate"], int(r["number"]))) if fit else None


def ex07_preference(candidates, guests, preferences):
    def score(r):
        return (3 * (r["view"] == preferences.get("view"))
                + 2 * (r["floor"] == preferences.get("floor"))
                + 1 * (r["room_type"] == preferences.get("room_type"))
                - (r["capacity"] - guests))
    fit = _fitting(candidates, guests)
    return max(fit, key=lambda r: (score(r), -int(r["number"]))) if fit else None


def _price(rate, night, seasons):
    for start, end, mult in seasons:
        if start <= night < end:
            return round(rate * mult, 2)
    return rate


def _nights(check_in, check_out):
    return [check_in + timedelta(days=i) for i in range(ex01_nights(check_in, check_out))]


def ex08_night_prices(rate, check_in, check_out, seasons):
    prices = {}
    for night in _nights(check_in, check_out):
        p = _price(rate, night, seasons)
        prices[p] = prices.get(p, 0) + 1
    return prices


def ex09_weekend_surcharge(rate, check_in, check_out, seasons, weekend_days=(4, 5), surcharge=0.20):
    weekend = [n for n in _nights(check_in, check_out) if n.weekday() in weekend_days]
    return round(sum(_price(rate, n, seasons) for n in weekend) * surcharge, 2)


def ex10_quote_total(rate, check_in, check_out, guests, breakfast=False, seasons=()):
    nights = ex01_nights(check_in, check_out)
    lines = [round(p * n, 2) for p, n in ex08_night_prices(rate, check_in, check_out, seasons).items()]
    lines.append(ex09_weekend_surcharge(rate, check_in, check_out, seasons))
    if nights >= 7:
        lines.append(-round(sum(lines) * 0.10, 2))
    if breakfast:
        lines.append(round(nights * guests * 55.0, 2))
    lines.append(round(sum(lines) * 0.18, 2))
    return round(sum(lines), 2)


TRANSITIONS = {
    ("CONFIRMED", "check_in"): "CHECKED_IN",
    ("CHECKED_IN", "check_out"): "CHECKED_OUT",
    ("CONFIRMED", "cancel"): "CANCELLED",
}


def ex11_next_state(state, event):
    try:
        return TRANSITIONS[(state, event)]
    except KeyError:
        raise ValueError(f"Cannot {event} a booking that is {state}") from None


def ex12_cancellation_fee(check_in, rate, now):
    arrival = datetime.combine(check_in, datetime.min.time()) + timedelta(hours=14)
    return 0.0 if arrival - now >= timedelta(hours=48) else float(rate)


def ex13_write_invoice(conn, booking_id, lines):
    with conn:                                 # commit on success, rollback on any exception
        cur = conn.execute("INSERT INTO invoices (booking_id, total) VALUES (?, ?)",
                           (booking_id, round(sum(a for _, a in lines), 2)))
        invoice_id = cur.lastrowid
        conn.executemany("INSERT INTO invoice_lines (invoice_id, description, amount) VALUES (?, ?, ?)",
                         [(invoice_id, d, a) for d, a in lines])
    return invoice_id
