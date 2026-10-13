# %% [markdown]
# # 03 · Algorithm 3 — what does the stay cost, and why?
#
# **Read first:** `01_theory/05_pricing.md`
#
# 1. a chain of rules, each adding explained lines to the invoice
# 2. the two worked examples: **4,445.06** and **2,442.60** — to the agorot
# 3. why the order of the rules is part of the algorithm
# 4. Open/Closed: add a new discount without touching any existing rule

# %%
from dataclasses import dataclass, field
from datetime import date, timedelta

WEEKEND_DAYS = (4, 5)          # Friday, Saturday (Monday = 0)
WEEKEND_SURCHARGE = 0.20
LONG_STAY_NIGHTS, LONG_STAY_DISCOUNT = 7, 0.10
BREAKFAST_PER_GUEST_NIGHT = 55.0
PARKING_PER_NIGHT = 40.0
VAT = 0.18

# %%
@dataclass
class Season:
    start: date
    end: date               # half-open, like a stay
    multiplier: float

@dataclass
class Context:
    rate: float
    room_type: str
    check_in: date
    check_out: date
    guests: int
    extras: tuple = ()
    seasons: list = field(default_factory=list)

    def nights_list(self):
        return [self.check_in + timedelta(days=i) for i in range((self.check_out - self.check_in).days)]

    def season_for(self, night):
        return next((s for s in self.seasons if s.start <= night < s.end), None)

    def price_of(self, night):
        s = self.season_for(night)
        return round(self.rate * (s.multiplier if s else 1.0), 2)

@dataclass
class Line:
    description: str
    quantity: int
    amount: float

# %% [markdown]
# ## 1. The rules
#
# Each rule: `rule(context, lines_so_far) -> new lines`.

# %%
def base_rate_rule(ctx, lines):
    prices = {}                                   # price -> number of nights at that price
    for night in ctx.nights_list():
        p = ctx.price_of(night)
        prices[p] = prices.get(p, 0) + 1
    return [Line(f"{n} night{'s' if n > 1 else ''} x {ctx.room_type} @ {p:.2f}", n, round(n * p, 2)) for p, n in prices.items()]

def weekend_rule(ctx, lines):
    weekend = [n for n in ctx.nights_list() if n.weekday() in WEEKEND_DAYS]
    if not weekend:
        return []
    extra = round(sum(ctx.price_of(n) for n in weekend) * WEEKEND_SURCHARGE, 2)
    return [Line(f"Weekend surcharge 20% ({len(weekend)} nights)", len(weekend), extra)]

def long_stay_rule(ctx, lines):
    if len(ctx.nights_list()) < LONG_STAY_NIGHTS:
        return []
    room_part = sum(l.amount for l in lines)      # base + weekend: reads the lines so far!
    return [Line("Long stay discount 10%", 1, -round(room_part * LONG_STAY_DISCOUNT, 2))]

def extras_rule(ctx, lines):
    n = len(ctx.nights_list())
    out = []
    if "breakfast" in ctx.extras:
        out.append(Line(f"Breakfast {n} nights x {ctx.guests} guests", n * ctx.guests, round(n * ctx.guests * BREAKFAST_PER_GUEST_NIGHT, 2)))
    if "parking" in ctx.extras:
        out.append(Line(f"Parking {n} nights", n, round(n * PARKING_PER_NIGHT, 2)))
    return out

def vat_rule(ctx, lines):
    return [Line("VAT 18%", 1, round(sum(l.amount for l in lines) * VAT, 2))]

RULES = [base_rate_rule, weekend_rule, long_stay_rule, extras_rule, vat_rule]

def quote(ctx, rules=RULES):
    lines = []
    for rule in rules:
        lines += rule(ctx, lines)
    return lines

def show(lines):
    for l in lines:
        print(f"  {l.description:40s} {l.amount:10,.2f}")
    print(f"  {'TOTAL':40s} {sum(l.amount for l in lines):10,.2f}")

# %% [markdown]
# ## 2. Worked example 1 — Room 102, Mon 2 → Mon 9 March 2026, 2 guests, breakfast

# %%
ctx = Context(450, "double", date(2026, 3, 2), date(2026, 3, 9), 2, extras=("breakfast",))
print("Friday and Saturday:", [n.isoformat() for n in ctx.nights_list() if n.weekday() in WEEKEND_DAYS])
lines = quote(ctx)
show(lines)
assert round(sum(l.amount for l in lines), 2) == 4445.06

# %% [markdown]
# ## 3. Worked example 2 — with a high season (6–10 March ×1.5), Thu 5 → Sun 8 March

# %%
ctx2 = Context(450, "double", date(2026, 3, 5), date(2026, 3, 8), 2,
               seasons=[Season(date(2026, 3, 6), date(2026, 3, 10), 1.5)])
lines2 = quote(ctx2)
show(lines2)
assert round(sum(l.amount for l in lines2), 2) == 2442.60

# %% [markdown]
# Notice the weekend surcharge is 20% of the **seasonal** price (675), not of 450 — because it reads
# `price_of(night)`.
#
# ## 4. The order is part of the algorithm
#
# Run the long-stay discount **before** the weekend surcharge and the discount no longer includes the surcharge:

# %%
wrong_order = [base_rate_rule, long_stay_rule, weekend_rule, extras_rule, vat_rule]
print("right order:", round(sum(l.amount for l in quote(ctx)), 2))
print("wrong order:", round(sum(l.amount for l in quote(ctx, wrong_order)), 2))

# %% [markdown]
# 21.24 more for the guest, and nobody would notice — unless a test pins the exact number.
#
# ## 5. Open/Closed: add "returning guest −5%" without touching any rule

# %%
def returning_guest_rule(ctx, lines):
    room_part = sum(l.amount for l in lines if not l.description.startswith(("Breakfast", "Parking")))
    return [Line("Returning guest 5%", 1, -round(room_part * 0.05, 2))]

with_loyalty = [base_rate_rule, weekend_rule, long_stay_rule, returning_guest_rule, extras_rule, vat_rule]
show(quote(ctx, with_loyalty))

# %% [markdown]
# One new function, one new entry in the list. No existing rule, test or file changed. That is the open/closed
# principle — and you can demonstrate it live in the defence.
#
# ## ✍️ Try it yourself
#
# 1. Price 3 nights Thu 5 → Sun 8 March 2026, double 450, 2 guests, **parking**, no season. Do it by hand first.
# 2. Which nights get the surcharge in a stay Wed 4 → Wed 11 March? Check with `nights_list()`.
# 3. Write "children under 6 sleep free" as a rule. Where in the list must it go, and why?
#
# Then solve exercises 8–10 in `03_exercises/`.
