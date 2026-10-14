# Lesson 28 — Which free room to give? First-Fit, Best-Fit, Preference — and the Strategy pattern

> **For:** Eran (HotelManager stage 3) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 27; Python `min`/`max` with `key` &nbsp;·&nbsp; **After this:** the experiment chapter of the book; Lesson 29

## The story

> Friday 2 pm at reception. A young **couple** asks for a room. Free right now: room 102 (a double), room 201 (a double
> with a sea view) and room 301 (a 4-bed family room). The new receptionist gives them **301** — it's the first one she
> sees on the screen. At 6 pm a **family of four** arrives. The family room is taken by two people. No room for them. They
> leave. Nobody did anything "wrong" — but the **rule for choosing the room** cost the hotel a family. This lesson compares
> three rules, measures which is best, and shows how to program them so the rule can be swapped with one line.

## 🎯 By the end, the student can

1. Apply the three strategies by hand to a list of free rooms, including the tie-breaks.
2. Explain why Best-Fit refuses fewer guests, with the timeline picture.
3. Read the 200-month experiment and explain why "best" depends on what you measure.
4. Explain the Strategy pattern and the factory.

## Words you need

| word | meaning |
|---|---|
| **candidates** | the rooms that are free for the dates **and** big enough for the guests |
| **strategy** | a rule for choosing one room from the candidates |
| **capacity** | how many people a room sleeps |
| **wasted beds** | capacity − guests: a couple in a 4-bed room wastes 2 beds |
| **key function** | what Python's `min`/`max` compares; `min(rooms, key=f)` = the room with the smallest f(room) |
| **tuple** | a group of values like (2, 450, 102); Python compares tuples left to right |
| **interface** | a promise: "every strategy has a `choose(...)` method" |
| **factory** | a function that turns a name ("best_fit") into the right object |

---

## 1. The three rules on the story's rooms

![worked example](figs/worked_example.png)

Candidates for the couple (2 guests, they'd like a sea view on floor 2):

```
room 102:  capacity 2, 450 ₪, garden view, floor 1
room 201:  capacity 2, 450 ₪, sea view,    floor 2
room 301:  capacity 4, 620 ₪, sea view,    floor 3
```

### First-Fit — "the lowest room number"

```
min(candidates, key=room number)  →  102
```

Simple and predictable.

### Best-Fit — "the smallest room that fits"

The key is a **tuple**: (capacity, price, number). Python compares the first values; only on a tie, the second; and so on.

```
102 → (2, 450, 102)
201 → (2, 450, 201)
301 → (4, 620, 301)

compare first values: 2, 2, 4   → 301 is out (4 is bigger)
tie between 102 and 201 → compare second values: 450, 450 → still a tie
compare third values: 102 < 201  → 102 wins
```

The family room stays free for the family.

### Preference — "the best match for what they asked"

Score = +3 if the view matches, +2 if the floor matches, +1 if the room type matches, −1 for every wasted bed:

```
102: view garden ≠ sea → 0;   floor 1 ≠ 2 → 0;   wasted 2 − 2 = 0   → score 0
201: view sea ✓ → +3;          floor 2 ✓ → +2;     wasted 0           → score 5   ← chosen
301: view sea ✓ → +3;          floor 3 ≠ 2 → 0;    wasted 4 − 2 = 2   → 3 − 2 = 1
```

The −1 per wasted bed stops this strategy from giving the big suite to everyone who wants a sea view.

### Python details to explain on the board

```python
min(cands, key=lambda r: int(r.number))                       # First-Fit
min(cands, key=lambda r: (r.capacity, r.rate, int(r.number))) # Best-Fit
max(cands, key=lambda r: (score(r), -int(r.number)))          # Preference
```

* `int(...)`: as text, "10" < "9" (characters are compared one by one, and "1" < "9").
* `-int(r.number)` inside `max`: for equal scores we want the **smaller** number; −101 is bigger than −102.
* Every strategy returns **None** for an empty list — the hotel's way of saying "no room".

## 2. Watch a month fill up

![a month of bookings](figs/month.gif)

The 24 real rooms of the sample data (capacity in brackets), the same 230 random requests, two strategies. **Green** = the
room fits exactly; **orange** = a bigger room than needed. First-Fit hands the big rooms to couples early in the month; later
families arrive and there's no 4-bed room left — refused. Best-Fit keeps the big rooms for those who need them.

**Analogy — packing a car boot:** put small bags in small gaps, so the big gap stays free for the suitcase.

## 3. The experiment — 200 simulated months

![experiment](figs/experiment.png)

| | refused / month | wasted bed-nights / month | income / month |
|---|---|---|---|
| First-Fit | 51.3 | 106 | **278,783 ₪** |
| Best-Fit | **48.1** | **37** | 274,381 ₪ |
| Preference | 52.1 | 78 | 269,652 ₪ |

Best-Fit refuses the fewest guests and wastes the fewest beds — but **First-Fit earns the most**. Why? The price is per
**room**: a couple in the 620 ₪ family room pays more than in a 450 ₪ double. Which strategy is "best" is a **business
decision**; the measurement gives the manager the facts. (This is exactly the discussion Eran's book needs.)

Why 200 months and not 1? One random month is luck (Lesson 05).

## 4. The Strategy pattern — swap the rule with one line

![strategy pattern](figs/strategy_pattern.png)

`HotelService` holds **an** `AllocationStrategy` and calls `choose(candidates, guests, preferences)` — it doesn't know which
one. A factory `create("best_fit")` turns the name from the config file into the right object. Adding a fourth strategy
("lowest floor first") = writing **one** new class; nothing else changes. This is the **open/closed principle**: open to
extension, closed to modification.

## 5. Common mistakes

| student says | the truth |
|---|---|
| "Best-Fit is always best" | Best for guests and beds, not for income. Measure, then decide. |
| "Sort the rooms first" | `min`/`max` with a key is one pass over the list. |
| "Return the first room if the list is empty" | Return None — "no room" is a normal answer. |

## 6. Activities

1. **Play hotel (15 min).** Cards = rooms (capacity 1, 2, 2, 4). Read requests aloud (2, 2, 4, 1, 4 …). Half the class
   uses First-Fit, half Best-Fit. Who refused fewer?
2. **Tie-breaks (5 min).** Rooms 203 (2, 450), 106 (2, 450), 104 (4, 620); 2 guests → Best-Fit? (106.)
3. **Design a 4th strategy (10 min).** "Cheapest first" — write its key function.

## 7. Do it yourself

<details><summary>1. Free: 301 (cap 4, 620, city view, floor 3), 206 (cap 2, 450, sea, floor 2), 101 (cap 1). 2 guests want sea, floor 2. Each strategy?</summary>

101 doesn't fit. First-Fit → **206** (206 < 301). Best-Fit → **206** (capacity 2). Preference → **206**: 3 + 2 − 0 = 5 vs
301: 0 + 0 − 2 = −2.
</details>

<details><summary>2. Why the tuple (capacity, rate, number) and not just capacity?</summary>

So ties are always decided the same way → the same request always gets the same room → reliable tests.
</details>

<details><summary>3. Which strategy would you recommend to the hotel, and why?</summary>

There is no single right answer: Best-Fit if the hotel values serving every guest (and its reputation); First-Fit if
short-term income matters most. Say which, and show the numbers.
</details>

## 8. In your project

| Project | Where |
|---|---|
| HotelManager | `hotelmanager/booking/allocation.py` → `FirstFreeStrategy`, `BestFitStrategy`, `PreferenceStrategy.score/choose`, `create` · `booking/availability.py` → `free_rooms` · `HotelService.create_booking` · exercises ex05–ex07 · theory `18_HotelManager/01_theory/04_allocation.md` · notebook `02_allocation.ipynb` |

## 🎬 Watch & explore

* Refactoring Guru — [The Strategy pattern](https://refactoring.guru/design-patterns/strategy)
* *First fit, best fit — memory allocation* — [search on YouTube](https://www.youtube.com/results?search_query=first+fit+best+fit+worst+fit+memory+allocation)
