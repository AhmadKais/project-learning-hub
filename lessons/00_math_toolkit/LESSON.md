# Lesson 00 — The maths toolkit: all the maths you need, from zero

> **For:** everyone, before any other lesson &nbsp;·&nbsp; **Time:** 2 × 45 min (or one section before each lesson)
> **You need:** a calculator (a phone is fine) and a pencil.

**In one sentence:** the projects only use about ten small pieces of maths — this lesson shows each one with a picture, a
story, and a calculation you can do on paper.

## The story

> **Noor runs the school canteen.** She is curious, so she writes everything down: how many students paid by card, how tall
> they are, how far the canteen is from the gate. Every day she has a new question — and every question needs one small
> maths tool. We follow Noor through her week.

---

## 1. Fractions and percentages — "how many out of how many"

> 📖 **Monday.** 100 students bought lunch. 13 paid by card. Noor wants to tell the principal "how many pay by card" in a
> way that works for any day, big or small.

**The idea:** "13 out of 100" is a **fraction**: 13 / 100.

* Divide → a decimal: 13 ÷ 100 = **0.13**
* Multiply by 100 → a percentage: 0.13 × 100 = **13 %**

![percentages](figs/percent.png)

```
3 out of 4   →  3 ÷ 4 = 0.75   →  75 %
1 out of 8   →  1 ÷ 8 = 0.125  →  12.5 %
```

**In the projects:** "13 % of the SMS are spam". "Precision 0.97" = "97 % of what we flagged was right".

## 2. The average — "a normal value"

> 📖 **Tuesday.** Seven students are in the queue. Noor wants one number for "how tall is a typical student here?".

**The idea:** add everything, then divide by how many there are.

```
heights: 150, 158, 162, 165, 171, 174, 180
step 1 — add them:       150 + 158 + 162 + 165 + 171 + 174 + 180 = 1160
step 2 — count them:     7
step 3 — divide:         1160 ÷ 7 = 165.7 cm
```

![the mean](figs/mean.png)

Picture the heights as weights on a ruler: the average is where the ruler balances. Nobody has to be exactly 165.7.

```python
sum(heights) / len(heights)       # 165.71...
```

## 3. Spread — "how different are they from normal?"

> 📖 **Wednesday.** Two classes visit. Both have an average height of 170 cm. But in class A everyone is about 170, and in
> class B some are 150 and some are 188. Noor wants a number for **how spread out** they are.

![spread](figs/spread.png)

That number is the **standard deviation** ("std"): the typical distance from the average. Small std = everyone close
together. Big std = very different.

**By hand for 4 students: 2, 4, 4, 6** (small numbers to keep it easy):

```
step 1 — the average:               (2 + 4 + 4 + 6) ÷ 4 = 16 ÷ 4 = 4
step 2 — each one's distance:        2−4 = −2     4−4 = 0     4−4 = 0     6−4 = +2
step 3 — square each distance:       4            0           0           4      (squaring removes the minus)
step 4 — average of the squares:     (4 + 0 + 0 + 4) ÷ 4 = 2
step 5 — square root:                √2 = 1.41      ← the standard deviation
```

Why square? Without it, −2 and +2 would cancel and we'd get 0 — "no spread" — which is wrong. The square root at the end
brings us back to normal units (cm).

## 4. Probability — "how likely?"

> 📖 **Thursday.** A bag of 10 sweets at the till: 3 orange, 7 blue. A student takes one without looking. *"What are the
> chances it's orange?"*

**The idea:** probability = **(ways it can happen) ÷ (all possibilities)**. Always between 0 (never) and 1 (always).

![probability](figs/probability.png)

```
P(orange) = 3 ÷ 10 = 0.3        P(blue) = 7 ÷ 10 = 0.7        together 0.3 + 0.7 = 1
```

**"Given that" — the line |.** Of 8 teachers who came, 6 paid by card. P(card | teacher) means "the chance of paying by
card, **counting only the teachers**" = 6 ÷ 8 = 0.75. The line means: first keep only the teachers, then count. (This one
idea is the whole spam filter in Lesson 11.)

## 5. The Σ sign — "add them all up"

> 📖 Noor's receipts: 3, 5, 2, 6 shekels. Her accountant writes Σ on the page. Noor panics. She shouldn't.

![sigma](figs/sigma.png)

Σ (the Greek letter S, for "sum") just means **add them all**: 3 + 5 + 2 + 6 = **16**. In Python it's `sum(...)` or a loop
with `total += x`.

Σ wᵢ · xᵢ means "multiply each pair, then add": w = (2, 1), x = (3, 4) → 2·3 + 1·4 = 6 + 4 = **10**.

## 6. Squares and square roots

> 📖 Noor tiles the canteen floor. A square area 5 tiles wide needs how many tiles?

![powers](figs/powers.png)

* **5²** ("5 squared") = 5 × 5 = **25** tiles — the area of the square.
* **√25** ("square root") goes back: what side gives 25 tiles? **5**.
* 5³ = 5 × 5 × 5 = 125. Anything to the power 0 = 1.

## 7. Logarithms — "how many times do I multiply?"

> 📖 **Friday.** Noor reads that a rumour doubles every day: 1 person, 2, 4, 8 … *"After how many days have 1,000 people
> heard it?"* She needs the opposite of "multiply again and again". That's a logarithm.

![logarithms](figs/log.png)

**The idea:** log₁₀(1000) asks "how many times do I multiply 10 to get 1000?" → 10 × 10 × 10 → **3**. (For the rumour:
log₂(1000) ≈ 10 days.)

```
log₁₀(10) = 1      log₁₀(100) = 2      log₁₀(1) = 0      log₁₀(0.01) = −2
```

The projects use **ln** — the same idea with the number e ≈ 2.718. You never compute it by hand: press **ln** on the
calculator, or `math.log(x)` in Python.

**Two things to remember:**

1. **log grows slowly.** ln(10) = 2.3, ln(100) = 4.6, ln(1000) = 6.9. Ten times bigger only adds 2.3. (Used in TF-IDF,
   Lesson 07.)
2. **log turns × into +:**

![log rule](figs/log_rule.png)

A computer can't store a number with 900 zeros after the decimal point — it becomes 0. But its log is an ordinary number
(about −2072). So instead of multiplying many tiny numbers, we **add their logs** (the spam filter, Lesson 11).

## 8. e and eˣ — the opposite of ln

![exp](figs/exp.png)

eˣ is always positive and grows faster and faster. ln undoes it: ln(eˣ) = x. You'll see eˣ inside the **sigmoid**
(Lesson 12) and **softmax** (Lesson 20) — always just "press the eˣ button".

## 9. Slope — "which way is downhill?"

> 📖 Noor walks down a dark hill to the school at night, without a torch. She feels the slope under her feet and always
> steps downhill. Eventually she reaches the bottom.

![slope](figs/slope.gif)

The **slope** says how steep the ground is: negative = it goes down to the right; positive = it goes up; **0 = you're at the
bottom**. Machine learning finds its best settings exactly like Noor in the dark: always step downhill (Lessons 12, 21). The
fancy name for slope is **derivative** or **gradient** — same idea.

## 10. Points and distance

> 📖 The canteen is at (1, 1) on the school map, the gate at (4, 5). How far is it in a straight line?

![distance](figs/distance.png)

Walk 3 across and 4 up. The straight line is **Pythagoras**: √(3² + 4²) = √(9 + 16) = √25 = **5**.

With more than two numbers (a wine has 11 measurements) it's the same: square every difference, add them all, square root.
A list of numbers drawn as an arrow is called a **vector** (Lesson 08).

```python
import math
math.dist((1, 1), (4, 5))     # 5.0
```

## 11. Data is a table

> 📖 At the end of the week Noor puts everything in one table: one row per student, one column per thing she measured.

![a data table](figs/table.png)

Every project starts like this: **one row per example** (a wine, an SMS, a URL), **one column per feature** (a measured
number), and one column with **the right answer** (the label). Keep this picture in mind for every lesson.

---

## Try it yourself (answers hidden — try first!)

<details><summary>1. 45 of 360 SMS are spam. Decimal and percentage?</summary>

45 ÷ 360 = 0.125 = **12.5 %**.
</details>

<details><summary>2. Average and standard deviation of 1, 3, 5.</summary>

Average 9 ÷ 3 = 3 · distances −2, 0, 2 · squares 4, 0, 4 · average 8 ÷ 3 = 2.67 · √2.67 = **1.63**.
</details>

<details><summary>3. 20 sweets, 5 red. P(red)? P(not red)?</summary>

5 ÷ 20 = **0.25** · 1 − 0.25 = **0.75**.
</details>

<details><summary>4. log₁₀(10,000)?</summary>

**4** (10 × 10 × 10 × 10).
</details>

<details><summary>5. Distance from (2, 3) to (5, 7)?</summary>

3 across, 4 up → √(9 + 16) = **5**.
</details>

## Class activities

1. **Human average (5 min).** 7 students stand in height order along a rope; find the balance point.
2. **Sweet bag (5 min).** Guess P(red), then draw 20 times and count.
3. **Paper folding (5 min).** Fold a paper again and again: 1, 2, 4, 8 … layers. "How many folds for 1,000 layers?" (≈ 10 —
   that's log₂.)
4. **Marble downhill (5 min).** A marble on a slightly tilted tray always rolls down — that's gradient descent.

## 🎬 Watch & explore

* Khan Academy — *Intro to logarithms* — [search on YouTube](https://www.youtube.com/results?search_query=Khan+Academy+intro+to+logarithms)
* StatQuest — *Mean, variance and standard deviation* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+mean+variance+standard+deviation)
* Seeing Theory — [Basic probability](https://seeing-theory.brown.edu/basic-probability/index.html)
