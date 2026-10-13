# %% [markdown]
# # 01 · Algorithm 1 — do two stays collide?
#
# **Read first:** `01_theory/03_intervals.md`
#
# 1. half-open stays `[check_in, check_out)` and why nights = check_out − check_in
# 2. the rule `a < d and c < b` — all eight cases, then a **brute-force proof** over every small interval
# 3. "is the room free?" — three skips and one comparison
# 4. complexity: O(n) in Python vs O(k) with an SQL query and an index

# %%
from dataclasses import dataclass
from datetime import date, timedelta
import random
import sqlite3
import time

# %% [markdown]
# ## 1. A stay is half-open

# %%
@dataclass(frozen=True)
class Stay:
    check_in: date
    check_out: date

    def __post_init__(self):
        if self.check_out <= self.check_in:
            raise ValueError("check-out must be after check-in")

    @property
    def nights(self):
        return (self.check_out - self.check_in).days

    def nights_list(self):
        return [self.check_in + timedelta(days=i) for i in range(self.nights)]

    def overlaps(self, other):
        return self.check_in < other.check_out and other.check_in < self.check_out

s = Stay(date(2026, 3, 3), date(2026, 3, 7))
print("nights:", s.nights)
print("slept in:", [d.isoformat() for d in s.nights_list()], " <- the 7th is NOT a night")

# %% [markdown]
# ## 2. The eight cases from the theory chapter
#
# Ours is `[3, 7)`. Case F — a guest arriving the morning the previous one leaves — is the one careless code
# gets wrong.

# %%
def d(day):
    return date(2026, 3, day)

ours = Stay(d(3), d(7))
cases = {"A [5,9)": (5, 9), "B [1,5)": (1, 5), "C [4,6)": (4, 6), "D [1,9)": (1, 9),
         "E [3,7)": (3, 7), "F [7,9)": (7, 9), "G [1,3)": (1, 3), "H [9,11)": (9, 11)}
for name, (c, e) in cases.items():
    other = Stay(d(c), d(e))
    bar = "".join("█" if c <= day < e else "." for day in range(1, 12))
    print(f"{name:9s} {bar}   {'COLLIDE' if ours.overlaps(other) else 'free'}")

# %% [markdown]
# What if we had written `<=`? Case F would collide — the hotel refuses a booking every time one guest leaves
# and another arrives on the same day.

# %%
def overlaps_wrong(a, b):
    return a.check_in <= b.check_out and b.check_in <= a.check_out

print("case F with <= :", "COLLIDE (wrong!)" if overlaps_wrong(ours, Stay(d(7), d(9))) else "free")

# %% [markdown]
# ## 3. Proof by checking every case
#
# The theory chapter proves the rule with De Morgan. Here we check it against the **definition** — "they share
# at least one night" — for **every** pair of stays inside a 12-day window. 4,356 pairs, no exceptions allowed.

# %%
pairs = mismatches = 0
for a in range(1, 13):
    for b in range(a + 1, 13):
        for c in range(1, 13):
            for e in range(c + 1, 13):
                x, y = Stay(d(a), d(b)), Stay(d(c), d(e))
                share_a_night = bool(set(x.nights_list()) & set(y.nights_list()))
                pairs += 1
                mismatches += share_a_night != x.overlaps(y)
print(f"{pairs} pairs checked, {mismatches} mismatches")

# %% [markdown]
# A brute-force check is not a proof for *all* dates — but it is a great way to catch a wrong rule, and it is
# exactly how you would write a strong unit test.
#
# ## 4. Is the room free?

# %%
@dataclass
class Booking:
    id: int
    room: str
    stay: Stay
    status: str = "CONFIRMED"           # CONFIRMED / CHECKED_IN / CHECKED_OUT / CANCELLED

BLOCKS_ROOM = {"CONFIRMED", "CHECKED_IN"}

def is_room_free(room, stay, bookings, ignore_id=None):
    for b in bookings:
        if b.room != room:
            continue                    # another room
        if b.status not in BLOCKS_ROOM:
            continue                    # cancelled / checked out - frees the room for free
        if b.id == ignore_id:
            continue                    # the booking we are editing
        if b.stay.overlaps(stay):
            return False
    return True

bookings = [Booking(1, "204", Stay(d(3), d(7))), Booking(2, "204", Stay(d(10), d(12)), status="CANCELLED")]
print("204 for 5-9 March: ", is_room_free("204", Stay(d(5), d(9)), bookings))
print("204 for 7-9 March: ", is_room_free("204", Stay(d(7), d(9)), bookings))
print("204 for 10-12 March:", is_room_free("204", Stay(d(10), d(12)), bookings), "(the booking there was cancelled)")
print("move booking 1 to 4-8 March:", is_room_free("204", Stay(d(4), d(8)), bookings, ignore_id=1))

# %% [markdown]
# ## 5. Complexity: 20,000 old bookings
#
# The loop above is **O(n)** in all bookings ever made. The project asks the database only for bookings that
# touch the period, with the **same rule** in SQL, and an index makes it a range scan: **O(k)**.

# %%
rng = random.Random(1)
ROOMS = [f"{f}0{r}" for f in range(1, 5) for r in range(1, 7)]
start = date(2020, 1, 1)
many = []
for i in range(20_000):
    ci = start + timedelta(days=rng.randrange(0, 2300))
    many.append(Booking(i, rng.choice(ROOMS), Stay(ci, ci + timedelta(days=rng.randint(1, 10)))))

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE bookings (id INTEGER PRIMARY KEY, room TEXT, check_in TEXT, check_out TEXT, status TEXT)")
db.executemany("INSERT INTO bookings VALUES (?,?,?,?,?)",
               [(b.id, b.room, b.stay.check_in.isoformat(), b.stay.check_out.isoformat(), b.status) for b in many])
db.execute("CREATE INDEX idx_room_dates ON bookings (room, check_in, check_out)")

want = Stay(date(2026, 3, 3), date(2026, 3, 7))
SQL = "SELECT id FROM bookings WHERE room = ? AND check_in < ? AND check_out > ? AND status IN ('CONFIRMED','CHECKED_IN')"

t0 = time.perf_counter()
free_py = [r for r in ROOMS if is_room_free(r, want, many)]
t_py = time.perf_counter() - t0

t0 = time.perf_counter()
free_sql = [r for r in ROOMS if not db.execute(SQL, (r, want.check_out.isoformat(), want.check_in.isoformat())).fetchall()]
t_sql = time.perf_counter() - t0

print(f"python loop: {t_py * 1000:.1f} ms    sql + index: {t_sql * 1000:.1f} ms    same answer: {free_py == free_sql}")
print(db.execute("EXPLAIN QUERY PLAN " + SQL, ("101", "2026-03-07", "2026-03-03")).fetchall())

# %% [markdown]
# `SEARCH ... USING INDEX idx_room_dates` — SQLite jumps straight to the room and the dates instead of reading
# every row. Note that ISO dates (`2026-03-07`) compare correctly **as text** — that is why the project stores
# them in this format.
#
# ## ✍️ Try it yourself
#
# 1. Decide by hand, then check in code: `[10,14)` vs `[14,16)`, `[10,14)` vs `[13,20)`, `[10,14)` vs `[8,10)`.
# 2. Run the brute-force proof on `overlaps_wrong`. How many mismatches, and which kind?
# 3. Drop the index (`DROP INDEX idx_room_dates`) and run the timing again. What does EXPLAIN say now?
#
# Then solve exercises 1–4 in `03_exercises/`.
