# %% [markdown]
# # 02 · Algorithm 2 — which free room to give
#
# **Read first:** `01_theory/04_allocation.md`
#
# 1. three strategies behind one interface (Strategy pattern) + a Factory
# 2. the worked examples from the theory chapter
# 3. **the experiment for your book:** replay the same requests with each strategy and measure

# %%
import csv
import random
from dataclasses import dataclass
from pathlib import Path
from statistics import mean

# %%
@dataclass(frozen=True)
class Room:
    number: str
    room_type: str
    capacity: int
    floor: int
    view: str
    rate: float

with open(Path("../data/sample_rooms.csv"), encoding="utf-8") as f:
    ROOMS = [Room(r["number"], r["room_type"], int(r["capacity"]), int(r["floor"]), r["view"], float(r["base_rate"]))
             for r in csv.DictReader(f)]
print(len(ROOMS), "rooms:", sorted({(r.room_type, r.capacity) for r in ROOMS}, key=lambda t: t[1]))

# %% [markdown]
# ## 1. The strategies
#
# `min(..., key=tuple)` compares the first element and only looks at the next one on a tie — so the key tuple
# **is** the sentence "smallest that fits, then cheapest, then lowest number".

# %%
class AllocationStrategy:
    name = "base"
    def choose(self, candidates, guests, preferences):
        raise NotImplementedError

class FirstFit(AllocationStrategy):
    name = "first_fit"
    def choose(self, candidates, guests, preferences):
        return min(candidates, key=lambda r: int(r.number)) if candidates else None

class BestFit(AllocationStrategy):
    name = "best_fit"
    def choose(self, candidates, guests, preferences):
        return min(candidates, key=lambda r: (r.capacity, r.rate, int(r.number))) if candidates else None

class Preference(AllocationStrategy):
    """score = 3*view + 2*floor + 1*type - wasted beds; ties -> lower number."""
    name = "preference"
    def score(self, room, guests, pref):
        s = 3 * (room.view == pref.get("view")) + 2 * (room.floor == pref.get("floor")) + (room.room_type == pref.get("type"))
        return s - (room.capacity - guests)
    def choose(self, candidates, guests, preferences):
        if not candidates:
            return None
        return max(candidates, key=lambda r: (self.score(r, guests, preferences), -int(r.number)))

STRATEGIES = {s.name: s for s in (FirstFit, BestFit, Preference)}

def create(name):                     # the Factory: the service never names a concrete class
    return STRATEGIES[name]()

# %% [markdown]
# ## 2. The worked examples

# %%
by_no = {r.number: r for r in ROOMS}
free = [by_no["102"], by_no["206"], by_no["104"]]      # double garden fl.1, double sea fl.2, family fl.1
for name in STRATEGIES:
    room = create(name).choose(free, 2, {"view": "sea", "floor": 2})
    print(f"couple, wants sea view on floor 2 -> {name:10s} gives {room.number} ({room.room_type}, {room.view}, floor {room.floor})")

single = [by_no["101"], by_no["102"], by_no["104"]]
for name in STRATEGIES:
    print(f"single traveller -> {name:10s} gives {create(name).choose(single, 1, {}).number}")

# %% [markdown]
# ## 3. The experiment
#
# A month in an empty hotel. Requests arrive in random order (guests 1–4, 1–7 nights, random wishes). Each
# strategy handles the **same** list. We record how many are served, the wasted beds, and the revenue.

# %%
def overlaps(a, b):
    return a[0] < b[1] and b[0] < a[1]

def simulate(strategy, requests):
    taken = {r.number: [] for r in ROOMS}            # room -> list of (start, end)
    served = wasted = revenue = 0
    for guests, start, nights, pref in requests:
        stay = (start, start + nights)
        candidates = [r for r in ROOMS if r.capacity >= guests and not any(overlaps(stay, s) for s in taken[r.number])]
        room = strategy.choose(candidates, guests, pref)
        if room is None:
            continue
        taken[room.number].append(stay)
        served += 1
        wasted += room.capacity - guests
        revenue += room.rate * nights
    return served, wasted / max(served, 1), revenue

def make_requests(rng, n):
    out = []
    for _ in range(n):
        guests = rng.choices([1, 2, 3, 4], weights=[2, 5, 2, 2])[0]
        pref = {"view": rng.choice(["sea", "garden", "city", None]), "floor": rng.choice([1, 2, 3, 4, None])}
        out.append((guests, rng.randrange(0, 30), rng.randint(1, 7), pref))
    return out

results = {name: [] for name in STRATEGIES}
for seed in range(200):                              # 200 different months, same requests per strategy
    reqs = make_requests(random.Random(seed), 160)
    for name in STRATEGIES:
        results[name].append(simulate(create(name), reqs))

print(f"{'strategy':12s} {'served':>8s} {'wasted beds':>12s} {'revenue':>10s}   (average of 200 months, 160 requests each)")
for name, rows in results.items():
    print(f"{name:12s} {mean(r[0] for r in rows):8.1f} {mean(r[1] for r in rows):12.2f} {mean(r[2] for r in rows):10.0f}")

# %% [markdown]
# Best-Fit keeps the big rooms for big families, so it serves the most requests and wastes the fewest beds.
# Preference makes guests happier (they get their view) but pays for it in capacity.
#
# But look at the revenue column: **First-Fit earns the most**. The price is per room, not per guest, so giving
# a couple a family room earns more per booking — even though fewer guests are served. Which strategy is
# "best" depends on what the hotel wants to maximise. That is a real finding: write it in the book, and say
# which objective your project chose and why. **A table you produced yourself turns
# "I wrote three strategies" into "I measured three strategies and here is the hotel's best choice".**
#
# ## ✍️ Try it yourself
#
# 1. Add a strategy "cheapest first, then smallest". Where does it land in the table?
# 2. Make the hotel busier (240 requests). Does the gap between First-Fit and Best-Fit grow?
# 3. Why must every strategy break ties deterministically? What would a test look like otherwise?
#
# Then solve exercises 5–7 in `03_exercises/`.
