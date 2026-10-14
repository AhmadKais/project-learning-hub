# Lesson 00 — The maths toolkit: every piece of maths the projects use, from zero

> **For:** everyone, before any other lesson &nbsp;·&nbsp; **Time:** 2 × 45 min (or one section at the start of each lesson)
> **You need:** a calculator (the phone is fine) and a pencil. Nothing else.

## Why this lesson exists

The projects use maybe ten pieces of maths. None of them is hard **when you see what it means**. This lesson shows each
one with a picture, a story, a calculation done step by step, and the one line of Python that does it for you.
Whenever another lesson says "see 00 §4", it means section 4 here.

## The story for this lesson

> **Noor runs the school canteen.** Every day she writes down what happens: how many sandwiches she sold, how tall the
> students in the queue are (she's curious), how many paid by card. She wants to answer simple questions —
> *"what is a normal day?"*, *"how likely is it that the next student pays by card?"*, *"how far is the canteen from
> the gate?"* — and each question needs one small tool.

---

## 1. Fractions and percentages — "how many out of how many"

![percentages](figs/percent.png)

**In words:** a fraction `k / n` means "**k out of n**". To turn it into a decimal number, divide. To turn the decimal
into a percentage, multiply by 100.

**Noor's example:** 100 students came today, 13 paid by card.

```
13 out of 100     →   13 / 100   =  0.13     →   0.13 × 100  =  13 %
3 out of 4        →    3 / 4     =  0.75     →   75 %
1 out of 8        →    1 / 8     =  0.125    →   12.5 %
```

**Why the projects care:** "13 % of the SMS messages are spam", "precision = 0.97 = 97 % of what we flagged was right".

```python
13 / 100          # 0.13
round(0.125 * 100, 1)   # 12.5
```

## 2. The average (mean) — "a normal value"

![the mean](figs/mean.png)

**In words:** add all the numbers, then divide by **how many** numbers there are. The average is the point where a ruler
with the values on it would balance.

**Noor's example — 7 students in the queue (cm):** 150, 158, 162, 165, 171, 174, 180.

```
step 1  add them:      150 + 158 + 162 + 165 + 171 + 174 + 180 = 1160
step 2  count them:    7 numbers
step 3  divide:        1160 / 7 = 165.7
```

The average height is **165.7 cm**. (No student is exactly 165.7 — that's fine; it's the balance point.)

```python
heights = [150, 158, 162, 165, 171, 174, 180]
sum(heights) / len(heights)        # 165.71...
```

## 3. Spread — the standard deviation, "how far from normal is typical?"

![spread](figs/spread.png)

Two classes can have the **same average** but be very different: in class A everyone is about 170 cm, in class B there
are very short and very tall students. The **standard deviation** (std) measures the typical distance from the average.

**Step by step, for 4 numbers: 2, 4, 4, 6**

```
step 1  average:                         (2 + 4 + 4 + 6) / 4 = 16 / 4 = 4
step 2  distance of each from 4:         2−4 = −2,   4−4 = 0,   4−4 = 0,   6−4 = +2
step 3  square each (removes the minus): 4, 0, 0, 4
step 4  average of the squares:          (4 + 0 + 0 + 4) / 4 = 2          ← this is called the VARIANCE
step 5  square root (undo step 3):       √2 = 1.41                        ← the STANDARD DEVIATION
```

**Why square and then root?** Without squaring, −2 and +2 would cancel to 0 and we'd think there's no spread at all.

**Where it is used:** the z-score (Lesson 02): "this wine is 1.5 standard deviations above average".

```python
import numpy as np
np.std([2, 4, 4, 6])       # 1.414...
```

## 4. Probability — "counting what could happen"

![probability](figs/probability.png)

**In words:** probability = **(the ways the thing can happen) / (all the ways)**. It is always between **0** (never) and
**1** (always). We write P(thing).

**Noor's bag:** 10 balls, 3 orange, 7 blue. Close your eyes, take one.

```
P(orange) = 3 / 10 = 0.3       (30 %)
P(blue)   = 7 / 10 = 0.7       (70 %)
P(orange) + P(blue) = 1        (you surely get one of them)
```

**"Given that" — the vertical bar |**: P(card | teacher) = "probability of paying by card, **looking only at the
teachers**". If 8 teachers came and 6 paid by card: P(card | teacher) = 6 / 8 = 0.75. The bar means: **first throw away
everyone who is not a teacher, then count.** (This is the whole idea of Naive Bayes, Lesson 11.)

## 5. The Σ sign — "add them all up"

![sigma](figs/sigma.png)

When a formula has **Σ**, don't panic: it is just a `for` loop that adds.

```python
x = [3, 5, 2, 6]
total = 0
for value in x:         # Σ
    total += value
print(total)            # 16
```

Σ wᵢ · xᵢ means "multiply each pair and add": with w = (2, 1) and x = (3, 4): 2·3 + 1·4 = 6 + 4 = **10**.

## 6. Powers and square roots

![powers](figs/powers.png)

* **x²** ("x squared") = x × x. Picture: the area of a square with side x. 5² = 25.
* **√x** ("square root") goes back: which side gives this area? √25 = 5.
* **x³** = x × x × x. **xⁿ** = x multiplied by itself n times. Anything to the power 0 is 1.
* **x^(1/2)** is another way to write √x.

```python
5 ** 2          # 25
25 ** 0.5       # 5.0
import math; math.sqrt(25)   # 5.0
```

## 7. Logarithms — "how many times do I multiply?"

![logarithms](figs/log.png)

**In words:** log₁₀(1000) asks: *how many times do I multiply 10 to get 1000?* 10 × 10 × 10 = 1000 → **3**.

```
log₁₀(10)      = 1        log₁₀(100) = 2        log₁₀(1) = 0         log₁₀(0.01) = −2
```

The projects use **ln** ("natural log", the same idea with the number e ≈ 2.718 instead of 10). You never compute it by
hand — use the calculator's `ln` button or `math.log(x)`.

**Two facts you need:**

1. **log grows slowly.** ln(10) = 2.3, ln(100) = 4.6, ln(1000) = 6.9. Going ×10 only adds 2.3. That is why TF-IDF uses a
   log: a rare word should matter more — but not 1,000 times more (Lesson 07).
2. **log turns × into +:**

![log rule](figs/log_rule.png)

The computer cannot store a number like 0.000…0001 with 900 zeros: it becomes **exactly 0**. But its log is just −2072,
an ordinary number. So when we must multiply hundreds of tiny probabilities (Naive Bayes), we **add their logs**
instead.

```python
import math
math.log(1000, 10)    # 3.0  (log base 10)
math.log(10)          # 2.302...  (ln)
math.log(0.001) + math.log(0.001)  ==  math.log(0.001 * 0.001)   # True (up to rounding)
```

## 8. e and eˣ — "the opposite of ln"

![exp](figs/exp.png)

e ≈ 2.718 is a special number (like π). **eˣ** is always positive; it grows faster and faster. e⁻ˣ = 1 / eˣ shrinks
toward 0. And ln **undoes** it: ln(eˣ) = x. You'll meet eˣ in the **sigmoid** (Lesson 12) and **softmax** (Lesson 20).

```python
math.exp(1)     # 2.718...
math.exp(-2)    # 0.135...
```

## 9. Slope — "which way is downhill?"

![slope](figs/slope.gif)

Imagine walking on the curve with your eyes closed. Under your feet you feel the **slope**: negative = the ground goes
down to the right, positive = it goes up, **0 = you are at the bottom**. Machine learning finds the best settings by
always stepping downhill (gradient descent, Lessons 12 and 21). The slope has a fancy name — the **derivative** — but
the idea is just "steepness".

**By numbers:** slope ≈ (how much f changes) / (how much x changes). Between x = 4 and x = 5 on f(x) = x²:
(25 − 16) / (5 − 4) = **9**: going right one step raises f by about 9.

## 10. Points, arrows and distance

![distance](figs/distance.png)

A pair of numbers (x, y) is a **point**: Noor's canteen at (1, 1), the school gate at (4, 5). The **distance** between
them is Pythagoras: walk 3 across, 4 up, the straight line is √(3² + 4²) = √(9 + 16) = √25 = **5**.

With more than 2 numbers (a wine has 11 measurements) it's the same formula with more squares inside the root. We can't
draw 11-D, but the computer doesn't care. An arrow from (0, 0) to a point is called a **vector** (Lesson 08).

```python
import math
math.dist((1, 1), (4, 5))     # 5.0
```

## 11. Data is a table

![a data table](figs/table.png)

Every ML project starts with a table: **one row per example** (a wine, an SMS, a URL), **one column per feature** (a
measured number), and usually **one column with the right answer** (the label). Keep this picture in mind for every
lesson.

---

## Do it yourself (answers hidden — try first!)

<details><summary>1. 45 of 360 SMS are spam. What fraction, decimal and percentage?</summary>

45 / 360 = 0.125 = **12.5 %**.
</details>

<details><summary>2. Average and standard deviation of 1, 3, 5.</summary>

Average (1 + 3 + 5) / 3 = 3. Distances −2, 0, 2. Squares 4, 0, 4. Average of squares 8 / 3 = 2.67. √2.67 = **1.63**.
</details>

<details><summary>3. In a box of 20 sweets, 5 are red. P(red)? P(not red)?</summary>

5 / 20 = **0.25**; 1 − 0.25 = **0.75**.
</details>

<details><summary>4. log₁₀(10,000)? And why is log₁₀(0.1) negative?</summary>

**4** (10·10·10·10). 0.1 is 10 *divided* once → −1.
</details>

<details><summary>5. Distance between (2, 3) and (5, 7)?</summary>

Across 3, up 4 → √(9 + 16) = **5**.
</details>

## Activities

1. **Human average (5 min).** 7 students stand in height order along a rope; find the balance point.
2. **Probability bag (5 min).** A real bag of coloured counters; predict P(red), then draw 20 times and count.
3. **Log ladder (5 min).** Students fold a paper in half again and again: 1, 2, 4, 8 … layers. "How many folds for 1,000
   layers?" → log₂(1000) ≈ 10. That's a logarithm.
4. **Blindfold slope (5 min).** On a slightly tilted table, roll a marble: it always goes downhill. That's gradient descent.

## 🎬 Watch & explore

* Khan Academy — *Intro to logarithms* — [search on YouTube](https://www.youtube.com/results?search_query=Khan+Academy+intro+to+logarithms)
* StatQuest — *Mean, variance and standard deviation* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+mean+variance+standard+deviation)
* Seeing Theory — [Basic probability, interactive](https://seeing-theory.brown.edu/basic-probability/index.html)
* 3Blue1Brown — *The paradox of the derivative* — [search on YouTube](https://www.youtube.com/results?search_query=3Blue1Brown+paradox+of+the+derivative)
