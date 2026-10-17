# Lesson 29 — What does the stay cost, and why? A chain of pricing rules

> **For:** Eran (HotelManager stage 4) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 00 §1 (percentages); Lesson 27 (nights); Python classes &nbsp;·&nbsp; **After this:** Lesson 30

**In one sentence:** build the price as a chain of small rules — base, weekend, long stay, extras, VAT — each adding
visible invoice lines, and remember that the order of the rules changes the total.

## 🗺️ The map of this lesson

```mermaid
flowchart LR
    C["the stay<br/>(room, dates, guests)"] --> R1["BaseRate"] --> R2["WeekendSurcharge"] --> R3["LongStayDiscount"] --> R4["Extras"] --> R5["Vat"]
    R5 --> INV["invoice:<br/>all lines + total"]
```

## The story

> A guest checks out and gets an invoice: **4,445.06 ₪**. She frowns: *"7 nights at 450 is 3,150. Why 4,445?"* A bad
> program answers "that's what the computer says". Eran's program prints **every line**: the base price, the weekend
> surcharge, the long-stay discount, breakfast, VAT — and she can check each one with a calculator. Building the price as
> a **chain of rules**, each adding visible lines, is the algorithm of this lesson. And it turns out that **the order of
> the rules changes the price**.

### 🌍 Real world

Every bill you get is a chain of rules: a **supermarket receipt** (items, "2 for 1", club discount, VAT), a **phone bill**
(plan, extra minutes, roaming, VAT), an **electricity bill** (fixed charge, usage in tiers, VAT), an **online checkout**
(items, shipping, coupon, tax). The good ones show every line — and in all of them the order matters:

![order matters in a shop](figs/shop_order.png)

## Words you need

| word | meaning |
|---|---|
| **rate** | the room's price per night (room 102: 450 ₪) |
| **surcharge** | an extra amount added: +20 % on Friday and Saturday nights |
| **discount** | an amount taken off: −10 % for stays of 7 nights or more |
| **VAT** | value-added tax: +18 % on everything |
| **invoice line** | one row of the bill: a description and an amount (a discount is a negative amount) |
| **season** | dates with a different price: high season ×1.5 |
| **rule** | a class that looks at the stay and the lines so far and returns new lines |
| **percentage of x** | x × percent / 100: 20 % of 450 = 450 × 0.20 = 90 (Lesson 00 §1) |

---

## 1. The invoice, line by line

First, the price of every night in March for room 102:

![price calendar](figs/price_calendar.png)

![invoice waterfall](figs/waterfall.png)

**Room 102 (450 ₪/night), Monday 2 → Monday 9 March 2026, 2 guests, with breakfast (55 ₪ per person per night).** In
March 2026 the 6th is a Friday and the 7th a Saturday.

```
nights = 9 − 2 = 7                          (the 2nd … 8th — Lesson 27)

1. BASE        7 nights × 450                         = 3,150.00
2. WEEKEND     Friday 6 and Saturday 7 are 2 nights.
               20 % of one night: 450 × 0.20 = 90
               2 nights × 90                          =   180.00
               room part so far: 3,150 + 180          = 3,330.00
3. LONG STAY   7 nights ≥ 7 → 10 % off the lines so far
               10 % of 3,330: 3,330 × 0.10 = 333
                                                      =  −333.00
               room part: 3,330 − 333                 = 2,997.00
4. EXTRAS      breakfast: 7 nights × 2 guests × 55    =   770.00
               subtotal: 2,997 + 770                  = 3,767.00
5. VAT 18 %    3,767 × 0.18                           =   678.06
                                                        ========
               TOTAL: 3,767.00 + 678.06               = 4,445.06
```

The waterfall chart shows the same thing: every bar starts where the previous one ended; the green bar goes down (the
discount); the orange bar is the total.

### With a season

**Thursday 5 → Sunday 8 March, high season 6–10 March (×1.5), no breakfast:**

![seasonal invoice](figs/waterfall_season.png)

```
nights: 5 (Thu), 6 (Fri), 7 (Sat)
1. BASE      5th: 450 (not in season)   6th: 450 × 1.5 = 675   7th: 675     → 450 + 675 + 675 = 1,800.00
2. WEEKEND   Fri and Sat: 20 % of the SEASONAL price → (675 + 675) × 0.20     =   270.00
3. LONG STAY 3 nights < 7 → nothing
5. VAT       (1,800 + 270) × 0.18 = 2,070 × 0.18                               =   372.60
TOTAL        2,070 + 372.60                                                     = 2,442.60
```

`tests/test_pricing.py` checks exactly these two numbers.

## 2. The design — a chain of rules

![rule chain](figs/chain.gif)

```
each rule:   lines(context, lines_so_far)  →  the new lines it adds

engine:      lines = []
             for rule in [BaseRate, WeekendSurcharge, LongStayDiscount, Extras, Vat]:
                 lines += rule.lines(context, lines)
             total = sum(line.amount for line in lines)
```

* Every rule makes **visible invoice lines** — the guest sees why.
* A discount is a **negative line**, not a hidden subtraction; the total is just the sum of all lines.
* Equal nights are grouped: "5 nights × double @ 450.00" instead of five identical lines.

## 3. The order is part of the algorithm

![wrong order](figs/wrong_order.png)

Put the long-stay discount **before** the weekend surcharge:

```
1. BASE        3,150.00
3. LONG STAY   10 % of 3,150 = −315.00        (the weekend isn't there yet!)
2. WEEKEND     +180.00
4. EXTRAS      +770.00                         subtotal 3,150 − 315 + 180 + 770 = 3,785.00
5. VAT         3,785 × 0.18 = 681.30
TOTAL          4,466.30                         ≠ 4,445.06
```

The same rules, another order → 21.24 ₪ more. The long-stay rule reads "the lines so far", so it must come **after** base and
weekend; VAT adds 18 % of everything, so it must be **last**. Say this sentence in the defence: *"The order of the rules is
part of the algorithm."*

## 4. Open / closed

Adding "returning guests −5 %" = one new class + one line in the engine's list. No other rule, test or file changes.

**Money:** round each line to the agora (2 decimals) and then add. Eran's code uses `round(x, 2)`; this lesson's script uses
Python's `Decimal`, which avoids float surprises like 0.1 + 0.2 = 0.30000000000000004.

## 🧪 Worked example: a rule chain in 30 lines

```python
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

def money(x):
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

@dataclass
class Stay:
    check_in: date
    check_out: date
    rate: Decimal
    guests: int
    breakfast: bool

    def nights(self):
        return [self.check_in + timedelta(days=i) for i in range((self.check_out - self.check_in).days)]

def base(s, lines):      return [("base", money(len(s.nights()) * s.rate))]
def weekend(s, lines):   return [("weekend +20%", money(sum(s.rate * Decimal("0.2") for n in s.nights() if n.weekday() in (4, 5))))]
def long_stay(s, lines): return [("long stay -10%", money(-sum(a for _, a in lines) * Decimal("0.1")))] if len(s.nights()) >= 7 else []
def extras(s, lines):    return [("breakfast", money(len(s.nights()) * s.guests * 55))] if s.breakfast else []
def vat(s, lines):       return [("VAT 18%", money(sum(a for _, a in lines) * Decimal("0.18")))]

def quote(stay, rules):
    lines = []
    for rule in rules:
        lines += rule(stay, lines)
    return lines, sum(a for _, a in lines)

stay = Stay(date(2026, 3, 2), date(2026, 3, 9), Decimal(450), 2, True)
lines, total = quote(stay, [base, weekend, long_stay, extras, vat])
for name, amount in lines:
    print(f"{name:15s} {amount:>9}")
print("TOTAL", total)                                                    # 4445.06
print("wrong order:", quote(stay, [base, long_stay, weekend, extras, vat])[1])   # 4466.30
```

## 5. Common mistakes

| student says | the truth |
|---|---|
| "One formula: rate × nights × factors" | Nobody can see why, and every new rule means editing the formula. |
| "Order doesn't matter, adding is commutative" | The rules take **percentages of different things**. |
| "The weekend surcharge is on the normal rate" | It's on that night's price — 675, not 450, in high season. |
| "Use float for money" | 0.1 + 0.2 = 0.30000000000000004. Round each line, or use `Decimal`. |

## 📝 Summary

> * The price is a **chain of rules**; each reads the stay and the lines so far and **adds visible lines**.
> * Example 1: 3,150 + 180 − 333 + 770 + 678.06 = **4,445.06**. Example 2 (season): **2,442.60**.
> * A discount is a **negative line**; total = sum of all lines.
> * **Order matters**: long stay after base + weekend, VAT last — otherwise 4,466.30.
> * **Open/closed**: a new rule = a new class + one line in the list.

## 6. Activities

1. **Be the engine (15 min).** 5 students are the 5 rules, each with a card. Pass the "invoice" sheet down the row; each
   adds their line. Then swap students 2 and 3 and run again.
2. **New rule live (10 min).** "Children under 12: −50 % on breakfast" — where in the chain, and what does it read?
3. **Check by hand (10 min).** §7 question 2.

## 7. Do it yourself

<details><summary>1. 8 nights, Sun 1 → Mon 9 March (one Friday, one Saturday), 450 ₪, no extras, no season. Total?</summary>

base 8 × 450 = 3,600 · weekend 2 × 90 = 180 · room part 3,780 · long stay 10 % = −378 → 3,402 · VAT 3,402 × 0.18 = 612.36 ·
total **4,014.36**.
</details>

<details><summary>2. Mon 9 → Wed 11 March, 1 guest, no breakfast, no season.</summary>

nights 9 (Mon), 10 (Tue) → base 900 · no weekend · no long stay · VAT 162 · total **1,062.00**.
</details>

<details><summary>3. Why must VAT be the last rule?</summary>

VAT is 18 % of everything the guest pays. Any line added after it would not be taxed.
</details>

## 8. In your project

| Project | Where |
|---|---|
| HotelManager | `hotelmanager/pricing/rules.py` → `Season.contains`, `PricingContext.season_for`, `BaseRateRule`, `WeekendSurchargeRule`, `LongStayDiscountRule`, `ExtrasRule`, `VatRule` (each `.lines`) · `pricing/engine.py` → `PricingEngine.quote`, `cancellation_fee` · `models/entities.py` → `Quote.subtotal/total` · exercises ex08–ex10 · theory `18_HotelManager/01_theory/05_pricing.md` · notebook `03_pricing.ipynb` |

## 🎬 Watch & explore

* Refactoring Guru — [Chain of Responsibility](https://refactoring.guru/design-patterns/chain-of-responsibility)
* *Open/Closed principle (SOLID)* — [search on YouTube](https://www.youtube.com/results?search_query=open+closed+principle+SOLID+explained)
* Python docs — [`decimal`](https://docs.python.org/3/library/decimal.html)
