# Chapter 5 — Algorithm 3: what does the stay cost, and why?

💡 **In short:** the price is not a column; it is a calculation made of independent **rules** applied
in order, each one adding an explained line to the invoice. Adding a rule never changes an old one.

## 5.1 The problem

A guest asks "why 4,445?" You must answer line by line. And the rules interact: the weekend surcharge
applies to the *seasonal* price; the long-stay discount applies to the room part *including* the
surcharge but *excluding* breakfast; VAT applies to everything. One long formula would be unreadable
and unchangeable.

## 5.2 The design

Each rule is a class with one method:

```
rule(context, lines_so_far)  ->  the lines this rule adds
```
`context` = room, stay, guests, extras, seasons. `lines_so_far` = what the earlier rules produced.
The engine runs them in a **fixed order** and collects the lines:

```
1. BaseRateRule          price per night = room rate x season multiplier, grouped
2. WeekendSurchargeRule  +20% for each Friday / Saturday night
3. LongStayDiscountRule  −10% of the lines so far, from 7 nights        <- must come after 1 and 2
4. ExtrasRule            breakfast per guest per night, parking per night, ...
5. VatRule               18% of everything above                         <- must be last
```

**The order is part of the algorithm.** Rule 3 reads `lines_so_far`, so it cannot run first; rule 5
sums everything, so it cannot run earlier. Say this sentence in the defense.

## 5.3 The full worked example — do it by hand

**Room 102 (double, 450/night), Mon 2 March 2026 → Mon 9 March 2026, 2 guests, breakfast.**
In March 2026 the 6th is a Friday and the 7th a Saturday.

```
nights = 9 − 2 = 7          (2, 3, 4, 5, 6, 7, 8 March)

1. Base        7 × 450                                    =  3,150.00
2. Weekend     2 nights (Fri 6, Sat 7) × 450 × 20%        =    180.00
                                                             ---------
               room part so far                              3,330.00
3. Long stay   7 ≥ 7 nights → −10% × 3,330.00             =   −333.00
                                                             ---------
               room part                                     2,997.00
4. Extras      breakfast: 7 nights × 2 guests × 55        =    770.00
                                                             ---------
               subtotal                                      3,767.00
5. VAT 18%     3,767.00 × 0.18                            =    678.06
                                                             =========
               TOTAL                                         4,445.06
```
`tests/test_pricing.py` asserts exactly these numbers. Copy this table into your project book.

**With a season.** Thu 5 → Sun 8 March, high season 6–10 March ×1.5:
```
1. Base     5 Mar 450 + 6 Mar 675 + 7 Mar 675       = 1,800.00
2. Weekend  (675 + 675) × 20%                       =   270.00      <- on the SEASONAL price
            subtotal 2,070.00   VAT 372.60   TOTAL 2,442.60
```

## 5.4 The three tricky pieces of code

**Group equal nights into one invoice line:**
```python
prices = {}                                     # price -> number of nights at that price
for night in context.stay.nights_list():
    season = context.season_for(night)
    price = round(context.room.rate * (season.multiplier if season else 1.0), 2)
    prices[price] = prices.get(price, 0) + 1
```
so the invoice says "5 nights × double @ 450.00" instead of five identical lines.

**A discount is a negative line, not a hidden subtraction:**
```python
room_part = sum(line.amount for line in current_lines)      # base + weekend
return [InvoiceLine("Long stay discount 10%", 1, -round(room_part * 0.10, 2))]
```
Then `Quote.total = sum(line.amount)` — the invoice adds up on the page exactly as the guest reads it.
**Never** compute the total twice in two different ways.

**Weekend is decided per night:** `night.weekday() in config.WEEKEND_DAYS` (Monday = 0 … Friday = 4,
Saturday = 5). Changing country = changing one tuple in `config.py`.

## 5.5 The principle this design demonstrates

> **Open/Closed principle** — open for extension, closed for modification.

Adding "returning guests −5%" is: one new class, one line in the engine's rule list. No existing rule,
no existing test, no other file. You can **prove** it in the defense: ask the examiner to invent a
discount and add it live in two minutes.

Complexity: **O(L·S)** — L nights × S rules; with L ≤ 30 and S = 5 that is at most 150 operations.

## 5.6 The alternative you rejected

One `calculate_price()` with nested `if`s. Works today; unmaintainable next month; and no line of the
invoice can be explained to the guest. Compare the two designs in chapter 8 of the book.

## ✅ Check yourself — Chapter 5

1. Compute the price of 3 nights, Thu 5 → Sun 8 March 2026, double 450, 2 guests, parking. (Show every line.)
2. Why must the long-stay rule run after the weekend rule? What number would change if it ran first?
3. Why is the discount a negative line?
4. Which nights get the weekend surcharge in a stay from Wed to Wed? How does the code decide?
5. State the open/closed principle and show where your code obeys it.
6. Add "children under 6 sleep free" out loud: which class, which line, which test?

## 📚 Further reading

- Meyer, B. (1988). *Object-Oriented Software Construction* — the open/closed principle.
- Fowler, M. (2002). *Patterns of Enterprise Application Architecture* — Money, Service Layer.
