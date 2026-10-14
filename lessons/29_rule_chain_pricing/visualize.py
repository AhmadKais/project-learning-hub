"""Lesson 29 - what does the stay cost, and why? A chain of pricing rules, each adding an explained invoice line."""
import sys
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)
D = lambda x: Decimal(str(x))
money = lambda x: x.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def price(check_in, check_out, rate, guests, breakfast=55, seasons=(), order=("base", "weekend", "long", "extras", "vat")):
    """A small rule chain like Eran's: every rule reads the context and the lines so far, and adds lines."""
    nights = [check_in + timedelta(d) for d in range((check_out - check_in).days)]

    def nightly(day):
        m = D(1)
        for (s, e, mult) in seasons:
            if s <= day < e:
                m = D(mult)
        return D(rate) * m

    rules = {
        "base": lambda lines: [("base", f"{len(nights)} nights", sum(nightly(n) for n in nights))],
        "weekend": lambda lines: [("weekend", "+20% Fri/Sat",
                                   sum(nightly(n) * D("0.20") for n in nights if n.weekday() in (4, 5)))],
        "long": lambda lines: ([("long stay", "−10% of the lines so far", -D("0.10") * sum(v for _, _, v in lines))]
                               if len(nights) >= 7 else []),
        "extras": lambda lines: [("breakfast", f"{len(nights)} × {guests} × {breakfast}", D(len(nights) * guests * breakfast))],
        "vat": lambda lines: [("VAT 18%", "of everything above", D("0.18") * sum(v for _, _, v in lines))],
    }
    lines = []
    for name in order:
        lines += [(a, b, money(v)) for a, b, v in rules[name](lines)]
    return lines


EX1 = price(date(2026, 3, 2), date(2026, 3, 9), 450, 2)
EX2 = price(date(2026, 3, 5), date(2026, 3, 8), 450, 2, breakfast=0, seasons=[(date(2026, 3, 6), date(2026, 3, 11), 1.5)])
EX2 = [l for l in EX2 if l[0] != "breakfast"]
WRONG = price(date(2026, 3, 2), date(2026, 3, 9), 450, 2, order=("base", "long", "weekend", "extras", "vat"))
total = lambda lines: sum(v for _, _, v in lines)
print(f"  example 1: {total(EX1)}   example 2: {total(EX2)}   wrong order: {total(WRONG)}")


def waterfall(ax, lines, title):
    run = Decimal(0)
    for i, (name, why, v) in enumerate(lines):
        col = GREEN if v < 0 else (VIOLET if name.startswith("VAT") else BLUE)
        ax.bar(i, float(abs(v)), bottom=float(run + v if v < 0 else run), color=col, width=0.6)
        ax.text(i, float(run + max(v, 0)) + 60, f"{'+' if v > 0 and i else ''}{v:,.2f}", ha="center", fontsize=11.5)
        ax.text(i, -330, why, ha="center", fontsize=9.5, color=INK2)
        run += v
    ax.bar(len(lines), float(run), color=ORANGE, width=0.6)
    ax.text(len(lines), float(run) + 60, f"{run:,.2f}", ha="center", fontsize=13, weight="bold")
    ax.set_xticks(range(len(lines) + 1), [l[0] for l in lines] + ["TOTAL"])
    ax.set_ylim(-450, float(run) * 1.12)
    ax.axhline(0, color=INK, lw=1)
    ax.set_ylabel("₪")
    ax.set_title(title, fontsize=13)


# ---------------------------------------------------------------- 1. the invoice as a waterfall
if L.wanted("waterfall"):
    fig, ax = plt.subplots(figsize=(13, 5.6))
    waterfall(ax, EX1, "Room 102 (450 ₪), Mon 2 → Mon 9 March 2026, 2 guests with breakfast")
    L.save(fig, "waterfall")
    fig, ax = plt.subplots(figsize=(10, 5.2))
    waterfall(ax, EX2, "Thu 5 → Sun 8 March, high season 6–10 March ×1.5 (no breakfast)")
    L.save(fig, "waterfall_season")

# ---------------------------------------------------------------- 2. the chain, animated
if L.wanted("chain"):
    rules = ["BaseRateRule", "WeekendSurchargeRule", "LongStayDiscountRule", "ExtrasRule", "VatRule"]
    fig, ax = plt.subplots(figsize=(15, 6.4))

    def upd(f):
        k = min(f, 5)
        blank(ax)
        box(ax, 0.01, 0.78, 0.17, 0.16, "PricingContext\nroom 102 · 7 nights\n2 guests · extras", color=INK2, fontsize=10.5)
        for i, r in enumerate(rules):
            y = 0.8 - i * 0.15
            active = i == k - 1
            done = i < k
            box(ax, 0.24, y - 0.11, 0.24, 0.1, r, color=ORANGE if active else (BLUE if done else GRID),
                fill=LIGHT_ORANGE if active else PAPER, weight="bold" if active else "normal", fontsize=11.5)
            if i:
                arrow(ax, (0.36, y + 0.04), (0.36, y - 0.005), color=GRID if not done else INK2)
        arrow(ax, (0.18, 0.86), (0.24, 0.75))
        ax.text(0.58, 0.93, "INVOICE  (lines_so_far)", fontsize=13, weight="bold")
        shown = [l for l in EX1 if [n for n in ("base", "weekend", "long stay", "breakfast", "VAT 18%")].index(l[0]) < k]
        for j, (name, why, v) in enumerate(shown):
            ax.text(0.58, 0.83 - j * 0.08, f"{name:<11} {why:<26} {v:>10,.2f}", fontsize=12, family="monospace",
                    color=ORANGE if j == len(shown) - 1 and k <= 5 else INK)
        if k == 5:
            ax.plot([0.58, 0.97], [0.39, 0.39], color=INK)
            ax.text(0.58, 0.33, f"{'TOTAL':<38} {total(EX1):>10,.2f}", fontsize=13, family="monospace", weight="bold")
        ax.text(0.5, 0.04, "each rule = one class with lines(context, lines_so_far);  the engine runs them in a FIXED order",
                ha="center", fontsize=12, color=INK2)
    L.animate(fig, upd, 9, "chain", fps=1)

# ---------------------------------------------------------------- 3. why the order is part of the algorithm
if L.wanted("wrong_order"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, 5.4), sharey=True)
    waterfall(a1, EX1, "RIGHT order: base → weekend → long stay → extras → VAT")
    waterfall(a2, WRONG, "WRONG: discount BEFORE the weekend surcharge")
    caption(fig, f"Same stay, same rules, another order: {total(EX1):,.2f} vs {total(WRONG):,.2f}.  "
                 "The long-stay rule reads lines_so_far - so it must run after base and weekend, and VAT must be last.")
    L.save(fig, "wrong_order")
