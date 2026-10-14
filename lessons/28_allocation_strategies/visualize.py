"""Lesson 28 - which free room to give: First-Fit, Best-Fit, Preference; the Strategy pattern; a simulated month."""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)

with open(data("18_HotelManager", "sample_rooms.csv"), encoding="utf-8") as f:
    ROOMS = [dict(number=int(r["number"]), type=r["room_type"], cap=int(r["capacity"]), floor=int(r["floor"]),
                  view=r["view"], rate=int(r["base_rate"])) for r in csv.DictReader(f)]


def first_fit(cands, guests, pref):
    return min(cands, key=lambda r: r["number"]) if cands else None


def best_fit(cands, guests, pref):
    return min(cands, key=lambda r: (r["cap"], r["rate"], r["number"])) if cands else None


def preference(cands, guests, pref):
    def score(r):
        s = 3 * (pref.get("view") == r["view"]) + 2 * (pref.get("floor") == r["floor"])
        s += 1 * (pref.get("room_type") == r["type"])
        return s - (r["cap"] - guests)
    return max(cands, key=lambda r: (score(r), -r["number"])) if cands else None


STRATS = {"First-Fit": first_fit, "Best-Fit": best_fit, "Preference": preference}


def requests(seed, n=230):
    r = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        g = int(r.choice([1, 2, 2, 2, 3, 4, 4], p=None))
        start = int(r.integers(1, 29))
        out.append(dict(guests=g, start=start, end=min(31, start + int(r.integers(1, 6))),
                        pref={"view": r.choice(["sea", "garden", "city", None]), "floor": None}))
    return out


def simulate(strategy, reqs):
    busy = {r["number"]: np.zeros(32, bool) for r in ROOMS}
    placed, refused, wasted, revenue = [], 0, 0, 0
    for q in reqs:
        cands = [r for r in ROOMS if r["cap"] >= q["guests"] and not busy[r["number"]][q["start"]:q["end"]].any()]
        room = strategy(cands, q["guests"], q["pref"])
        if room is None:
            refused += 1
            placed.append(None)
            continue
        busy[room["number"]][q["start"]:q["end"]] = True
        nights = q["end"] - q["start"]
        wasted += (room["cap"] - q["guests"]) * nights
        revenue += room["rate"] * nights
        placed.append(room["number"])
    return placed, refused, wasted, revenue


# ---------------------------------------------------------------- 1. the guide's worked example
if L.wanted("worked_example"):
    cands = [r for r in ROOMS if r["number"] in (102, 201, 301)]
    cands = [dict(r) for r in cands]
    # the guide's version of the three candidates: 102 (cap 2, 450), 201 (cap 2, 450, sea, floor 2), 301 (cap 4, 620, sea)
    cands = [dict(number=102, type="double", cap=2, floor=1, view="garden", rate=450),
             dict(number=201, type="double", cap=2, floor=2, view="sea", rate=450),
             dict(number=301, type="family", cap=4, floor=3, view="sea", rate=620)]
    pref = {"view": "sea", "floor": 2}
    fig, ax = plt.subplots(figsize=(14, 5.4))
    blank(ax)
    for i, r in enumerate(cands):
        x = 0.05 + i * 0.32
        box(ax, x, 0.55, 0.26, 0.32, f"room {r['number']}\ncapacity {r['cap']} · {r['rate']} ₪\n{r['view']} view, floor {r['floor']}",
            color=INK2, fontsize=12)
    ax.text(0.5, 0.95, "A couple (2 guests) asks for a sea view on floor 2.  Free rooms that fit:", ha="center", fontsize=13,
            weight="bold")
    for j, (name, fn) in enumerate(STRATS.items()):
        ch = fn(cands, 2, pref)
        i = [r["number"] for r in cands].index(ch["number"])
        y = 0.38 - j * 0.15
        ax.text(0.02, y, f"{name}:", fontsize=13, weight="bold", color=SERIES[j])
        why = {"First-Fit": "lowest room number", "Best-Fit": "key (capacity, rate, number) → (2, 450, 102) is the smallest",
               "Preference": "score: 102 → 0,  201 → 3 + 2 = 5,  301 → 3 − 2 wasted beds = 1"}[name]
        ax.text(0.17, y, f"room {ch['number']}   —   {why}", fontsize=12.5)
        ax.add_patch(plt.Rectangle((0.05 + i * 0.32 + 0.005 * j, 0.55 - 0.006 * j), 0.26, 0.32, fill=False,
                                   ec=SERIES[j], lw=3))
    L.save(fig, "worked_example")

# ---------------------------------------------------------------- 2. one simulated month, the timeline filling up
if L.wanted("month"):
    reqs = requests(7)
    fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharey=True)
    results = {n: simulate(fn, reqs) for n, fn in [("First-Fit", first_fit), ("Best-Fit", best_fit)]}
    order = [r["number"] for r in ROOMS]
    steps = list(range(0, len(reqs) + 1, 6)) + [len(reqs)] * 3

    def upd(f):
        k = steps[f]
        for ax, (name, (placed, refused, wasted, revenue)) in zip(axes, results.items()):
            ax.clear()
            ref = 0
            for q, room in zip(reqs[:k], placed[:k]):
                if room is None:
                    ref += 1
                    continue
                y = order.index(room)
                cap = next(r["cap"] for r in ROOMS if r["number"] == room)
                ax.add_patch(plt.Rectangle((q["start"], y - 0.4), q["end"] - q["start"], 0.8,
                                           color=GREEN if cap == q["guests"] else ORANGE, alpha=0.85, ec=PAPER))
            ax.set_xlim(1, 31)
            ax.set_ylim(-0.7, len(order) - 0.3)
            ax.set_yticks(range(len(order)), [f"{r['number']} ({r['cap']})" for r in ROOMS], fontsize=8.5)
            ax.set_xlabel("day of the month")
            ax.set_title(f"{name}: request {k} of {len(reqs)} — refused so far: {ref}", fontsize=12.5)
            ax.invert_yaxis()
        axes[0].set_ylabel("room (capacity)")
        fig.suptitle("green = the room fits exactly · orange = a bigger room than needed (wasted beds)", fontsize=12)
    L.animate(fig, upd, len(steps), "month", fps=3)

# ---------------------------------------------------------------- 3. the experiment: 200 simulated months
if L.wanted("experiment"):
    agg = {n: np.array([simulate(fn, requests(s))[1:] for s in range(200)]) for n, fn in STRATS.items()}
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    for ax, j, title in zip(axes, range(3), ["requests REFUSED per month (lower = better)",
                                             "wasted bed-nights per month (lower = better)",
                                             "revenue per month, ₪ (higher = better)"]):
        means = [agg[n][:, j].mean() for n in STRATS]
        ax.bar(range(3), means, color=SERIES[:3])
        for i, m in enumerate(means):
            ax.text(i, m * 1.01, f"{m:,.0f}" if m > 100 else f"{m:.1f}", ha="center", fontsize=12)
        ax.set_xticks(range(3), list(STRATS))
        ax.set_title(title, fontsize=12)
        lo = min(means)
        ax.set_ylim(lo * 0.9 if lo > 1000 else 0, max(means) * 1.08)
    caption(fig, "Same 200 random months of requests for each strategy (this lesson's simple simulation).  "
                 "Eran's own experiment is in his book - compare!")
    for n in STRATS:
        print(f"  {n}: refused {agg[n][:, 0].mean():.1f}  wasted {agg[n][:, 1].mean():.0f}  revenue {agg[n][:, 2].mean():,.0f}")
    L.save(fig, "experiment")

# ---------------------------------------------------------------- 4. the Strategy pattern
if L.wanted("strategy_pattern"):
    fig, ax = plt.subplots(figsize=(14, 5.6))
    blank(ax)
    box(ax, 0.02, 0.4, 0.2, 0.2, "HotelService\n.create_booking()", color=INK2, weight="bold")
    box(ax, 0.36, 0.62, 0.28, 0.24, "«interface»\nAllocationStrategy\nchoose(candidates, guests, prefs)", color=VIOLET,
        weight="bold")
    for i, (name, rule) in enumerate([("FirstFreeStrategy", "lowest number"), ("BestFitStrategy", "smallest that fits"),
                                      ("PreferenceStrategy", "highest score")]):
        x = 0.24 + i * 0.26
        box(ax, x, 0.08, 0.22, 0.2, f"{name}\n{rule}", color=SERIES[i], fontsize=11.5)
        arrow(ax, (x + 0.11, 0.28), (0.5, 0.62), style="-|>", color=INK2)
    arrow(ax, (0.22, 0.5), (0.36, 0.7), text="holds one,\ndoesn't know which", fontsize=11)
    box(ax, 0.76, 0.62, 0.22, 0.24, "create(name)\nfactory: name → object\n(from config)", color=AQUA)
    ax.set_title("Strategy pattern: swap the rule without touching the service.  A 4th strategy = one new class.")
    L.save(fig, "strategy_pattern")
