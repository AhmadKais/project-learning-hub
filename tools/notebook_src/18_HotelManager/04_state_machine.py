# %% [markdown]
# # 04 · Algorithm 4 — the booking's life cycle
#
# **Read first:** `01_theory/06_fsm.md`
#
# 1. a finite state machine: 4 states, 3 legal transitions, each with a guard
# 2. illegal moves give a clear error saying **why**
# 3. the state drives availability — cancelling frees the room with no extra code
# 4. the cancellation fee, and writing an invoice in **one transaction** (atomicity)

# %%
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from enum import Enum

# %% [markdown]
# ## 1. States and transitions

# %%
class Status(Enum):
    CONFIRMED = "confirmed"
    CHECKED_IN = "checked_in"
    CHECKED_OUT = "checked_out"
    CANCELLED = "cancelled"

    @property
    def blocks_room(self):
        return self in (Status.CONFIRMED, Status.CHECKED_IN)

TRANSITIONS = {                          # (from, event) -> to
    (Status.CONFIRMED, "check_in"): Status.CHECKED_IN,
    (Status.CHECKED_IN, "check_out"): Status.CHECKED_OUT,
    (Status.CONFIRMED, "cancel"): Status.CANCELLED,
}

for (src, event), dst in TRANSITIONS.items():
    print(f"{src.name:11s} --{event:9s}--> {dst.name}")
print("\nevery other (state, event) pair is illegal:",
      sum(1 for s in Status for e in ("check_in", "check_out", "cancel") if (s, e) not in TRANSITIONS), "pairs")

# %% [markdown]
# ## 2. Guarded transitions — always the same shape
#
# load → check the state → check the business condition → change → stamp the time → save → return.

# %%
class HotelError(Exception):
    pass

@dataclass
class Booking:
    id: int
    room: str
    check_in: date
    check_out: date
    rate: float
    status: Status = Status.CONFIRMED
    checked_in_at: datetime = None

def check_in(b, today):
    if b.status is not Status.CONFIRMED:
        raise HotelError(f"Cannot check in a booking that is {b.status.value}")
    if today < b.check_in:
        raise HotelError(f"Too early - check-in is on {b.check_in}")
    b.status = Status.CHECKED_IN
    b.checked_in_at = datetime.combine(today, datetime.min.time())
    return b

def check_out(b):
    if b.status is not Status.CHECKED_IN:
        raise HotelError(f"Cannot check out a booking that is {b.status.value}")
    b.status = Status.CHECKED_OUT
    return b

def cancellation_fee(b, now):
    """Free up to 48 hours before arrival (14:00 on the check-in day), otherwise one night."""
    arrival = datetime.combine(b.check_in, datetime.min.time()) + timedelta(hours=14)
    return 0.0 if arrival - now >= timedelta(hours=48) else b.rate

def cancel(b, now):
    if b.status is not Status.CONFIRMED:
        raise HotelError(f"Cannot cancel a booking that is {b.status.value}")
    fee = cancellation_fee(b, now)
    b.status = Status.CANCELLED
    return fee

b = Booking(1, "204", date(2026, 3, 3), date(2026, 3, 7), 620)
for action in (lambda: check_in(b, date(2026, 3, 1)),     # too early
               lambda: check_out(b),                        # never arrived
               lambda: check_in(b, date(2026, 3, 3)),       # OK
               lambda: cancel(b, datetime(2026, 3, 4)),     # already sleeping in the room
               lambda: check_out(b),                        # OK
               lambda: check_in(b, date(2026, 3, 8))):      # CHECKED_OUT is final
    try:
        action()
        print("OK     ->", b.status.name)
    except HotelError as e:
        print("REFUSE ->", e)

# %% [markdown]
# Every refusal says **why** — the receptionist knows what to do next.
#
# ## 3. The fee

# %%
b2 = Booking(2, "102", date(2026, 3, 10), date(2026, 3, 12), 450)
for now in (datetime(2026, 3, 7, 12), datetime(2026, 3, 8, 14), datetime(2026, 3, 9, 9)):
    print(f"cancel at {now:%d/%m %H:%M} -> fee {cancellation_fee(b2, now):.0f}")

# %% [markdown]
# ## 4. The state drives availability
#
# The availability check (notebook 01) asks only `status.blocks_room`. So cancelling frees the room instantly
# — no deletion, history kept.

# %%
def overlaps(a_in, a_out, b_in, b_out):
    return a_in < b_out and b_in < a_out

def is_room_free(room, ci, co, bookings):
    return not any(x.room == room and x.status.blocks_room and overlaps(x.check_in, x.check_out, ci, co) for x in bookings)

b3 = Booking(3, "305", date(2026, 4, 1), date(2026, 4, 5), 900)
print("305 free for 2-4 April?", is_room_free("305", date(2026, 4, 2), date(2026, 4, 4), [b3]))
cancel(b3, datetime(2026, 3, 1))
print("after cancelling:      ", is_room_free("305", date(2026, 4, 2), date(2026, 4, 4), [b3]), "  status:", b3.status.name)

# %% [markdown]
# ## 5. One transaction: all of the invoice or none of it
#
# The invoice row and all its lines are written inside one transaction. If line 3 fails, the rollback removes
# the whole invoice. A half-invoice would be worse than none — atomicity, the **A** of ACID.

# %%
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE invoices (id INTEGER PRIMARY KEY, booking_id INTEGER, total REAL);
CREATE TABLE invoice_lines (invoice_id INTEGER, description TEXT NOT NULL, amount REAL);
""")

def write_invoice(db, booking_id, lines):
    with db:                                   # BEGIN ... COMMIT, or ROLLBACK on an exception
        cur = db.execute("INSERT INTO invoices (booking_id, total) VALUES (?, ?)", (booking_id, sum(a for _, a in lines)))
        for desc, amount in lines:
            db.execute("INSERT INTO invoice_lines VALUES (?, ?, ?)", (cur.lastrowid, desc, amount))

write_invoice(db, 1, [("4 nights", 2480.0), ("VAT", 446.4)])
try:
    write_invoice(db, 2, [("2 nights", 900.0), (None, 50.0), ("VAT", 171.0)])   # line 2 breaks NOT NULL
except sqlite3.IntegrityError as e:
    print("failed:", e)
print("invoices:", db.execute("SELECT * FROM invoices").fetchall())
print("lines:   ", db.execute("SELECT * FROM invoice_lines").fetchall())

# %% [markdown]
# Invoice 2 left **nothing** behind — not even its first line.
#
# ## ✍️ Try it yourself
#
# 1. Draw the machine on paper with the guards. Which transitions are deliberately missing?
# 2. Add a "no_show" transition (CONFIRMED → NO_SHOW, guard: today > check-in date). Does it block the room?
# 3. Remove `with db:` from `write_invoice` and run section 5 again. What is left in the tables?
#
# Then solve exercises 11–13 in `03_exercises/`.
