# Chapter 4 — Algorithm 2: which free room to give

💡 **In short:** several rooms are free; you must pick one. "Smallest room that still fits" (Best-Fit)
keeps the big rooms for big families and fills the hotel better. Three strategies, one interface, and
you *measure* which is best.

## 4.1 The problem, in money again

```
Free for the dates:   102 (double, 2 beds)   201 (double, 2 beds, sea)   301 (family, 4 beds)
A couple books.
Give them 301  ->  an hour later a family of four calls  ->  nothing left  ->  lost booking.
Give them 102  ->  the family gets 301.  Both served.
```
This is a **resource allocation** problem with an objective function. The same problem appears in
operating systems (which block of memory to give a program) and in logistics (bin packing).

## 4.2 The three strategies

| Strategy | Rule | Chooses (for a couple, above) |
|---|---|---|
| **First-Fit** | lowest room number | 102 |
| **Best-Fit** | smallest capacity that fits; tie → cheaper → lower number | 102 |
| **Preference** | highest score for what the guest asked for | 201, if they asked for a sea view |

**Best-Fit worked example**
```
candidates (must fit 2):   102 (cap 2, 450)   201 (cap 2, 450)   301 (cap 4, 620)
key = (capacity, rate, number)
   102 -> (2, 450, 102)     201 -> (2, 450, 201)     301 -> (4, 620, 301)
min  -> (2, 450, 102)  =  room 102        the family room stays free
```

**Preference worked example** — guest asked `view=sea, floor=2`; score = 3·view + 2·floor + 1·type − wasted beds:
```
102  garden, floor 1, wasted 0  ->  0 + 0 + 0 − 0 = 0
201  sea,    floor 2, wasted 0  ->  3 + 2 + 0 − 0 = 5      <- chosen
301  sea,    floor 3, wasted 2  ->  3 + 0 + 0 − 2 = 1
```

## 4.3 How it is programmed

```python
class BestFitStrategy(AllocationStrategy):
    name = "best_fit"
    def choose(self, candidates, guests, preferences):
        if not candidates:
            return None
        return min(candidates, key=lambda r: (r.capacity, r.rate, int(r.number)))
```
`min(..., key=tuple)` compares the first element and only looks at the second on a tie. So the tuple
`(capacity, rate, number)` *is* the sentence "smallest that fits, then cheapest, then lowest number".

Two properties you should name in the defense:
- **Deterministic**: the same input always gives the same room — that is why a test can assert "room 102".
- **Open for extension**: `allocation.create(name)` is a Factory; a fourth strategy is one class and one
  dictionary entry. `HotelService` never mentions a concrete strategy class.

## 4.4 Complexity and the experiment that goes in your book

Each strategy is one pass over the free rooms: **O(n)**, n ≤ number of rooms. Speed is not the
interesting part — **quality** is, and you measure it in stage 7:

```
Replay the SAME 30 random requests on an empty hotel, once per strategy. Record:

 strategy      requests served    average wasted beds    revenue
 first_fit          ...                 ...                ...
 best_fit           ...                 ...                ...
 preference         ...                 ...                ...
```
Expected: Best-Fit serves the most and wastes the least; Preference makes guests happier but wastes
capacity. A table you produced yourself turns "I wrote three strategies" into "I measured three
strategies and here is the hotel's best choice".

❓ *Why not always give the biggest free room?* — the lost-family example above, with numbers.
❓ *Where else is Best-Fit used?* — memory allocators, bin packing, shelf/warehouse assignment.

## ✅ Check yourself — Chapter 4

1. Free: 101 (1 bed), 102 (2), 301 (4). A single traveller books. What does each strategy choose?
2. Two rooms with the same capacity and price — which does Best-Fit take, and why must there be a rule?
3. Write the key tuple for a strategy "cheapest first, then smallest".
4. What does `choose` return when nothing is free, and who handles that?
5. Which files change if you add a "prefer the room cleaned longest ago" strategy?
6. Design the measurement experiment: what do you vary, what do you record?

## 📚 Further reading

- Best-fit / first-fit allocation: any operating-systems textbook (Silberschatz, *Operating System
  Concepts*, memory allocation chapter).
- Refactoring Guru — Strategy pattern: https://refactoring.guru/design-patterns/strategy
