# Lesson 01 — What "machine learning" means: data, splits and overfitting

> **For:** Laith (Spam) · Ryan (FaceEmotion) · Dani (PhishGuard) · Seif (WineGrader) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 00 §1, §2, §11 &nbsp;·&nbsp; **After this:** every other ML lesson

## The story

> **Maya has a small phone shop.** Her shop's phone number is on Google, so she gets about 200 SMS a day: customers
> asking about repairs — and **spam**: "WINNER!! Claim your FREE prize now", "Your package is waiting, click here".
> She loses half an hour every morning deleting spam. Her nephew, a programmer, says: *"I'll write a program that
> recognises spam."* This lesson is what he discovers.

## 🎯 By the end, the student can

1. Explain, with Maya's story, the difference between **writing rules** and **learning from examples**.
2. Name the parts of a dataset: example, feature, label.
3. Explain what the **training**, **validation** and **test** sets are for, and why the test set is used only once.
4. Recognise **overfitting** and **underfitting** in a picture and in numbers.

---

## 1. Attempt 1: write the rules yourself

The nephew writes rules:

```python
def is_spam(sms):
    if "FREE" in sms:     return True
    if "WINNER" in sms:   return True
    if "click" in sms:    return True
    return False
```

It works for a day. Then:

* "Is the screen repair **free** if it's under warranty?" → flagged as spam ❌ (a real customer!)
* "Y0u w0n a pr1ze" → not spam ✓?? It *is* spam, but the rule doesn't know "w0n".
* Every week the spammers invent new tricks; every week he adds rules; soon there are 300 rules that contradict each
  other.

**The lesson:** some problems have no clear rules a human can write — spam, faces, phishing sites, wine taste. But
humans **can recognise** the answer when they see one example.

## 2. Attempt 2: let the computer find the rules

![rules vs learning](figs/rules_vs_learning.png)

Maya spends one afternoon marking 5,000 old SMS as "spam" or "not spam". The nephew gives the computer these 5,000
**examples with their answers**, and an algorithm finds the rules by itself — for example: "messages with 'claim',
'prize' and a link are almost always spam; messages with 'tomorrow' and 'ok' almost never". That set of learned rules
is called the **model**.

| | Normal programming | Machine learning |
|---|---|---|
| you give | rules + data | data + correct answers |
| you get | answers | **rules (the model)** |
| good when | the rules are clear (tax, salaries) | the rules are fuzzy (spam, faces, taste) |

## 3. Words you need

Look at the data as a **table** (Lesson 00 §11):

| SMS (the example) | has "free"? | number of "!" | has a link? | length | **label** |
|---|---|---|---|---|---|
| "WINNER!! claim your prize www.x.com" | 0 | 2 | 1 | 35 | **spam** |
| "Is my phone ready tomorrow?" | 0 | 0 | 0 | 27 | **ham** |
| "FREE entry to win £100!!! txt now" | 1 | 3 | 0 | 33 | **spam** |

| word | meaning | in the table |
|---|---|---|
| **example** (row, sample) | one thing we know the answer for | one SMS |
| **feature** | one **number** describing the example | "number of !" = 2 |
| **label** | the correct answer | spam / ham ("ham" = a normal message) |
| **class** | one of the possible answers | the two classes: spam, ham |
| **dataset** | the whole table | Maya's 5,000 SMS |
| **model** | the rules learned from the dataset | "claim + prize + link → spam" |
| **training** | the computer studying the dataset to build the model | `model.fit(features, labels)` |
| **prediction** | the model's answer for a new SMS | `model.predict(new_sms)` → "spam" |

Why must features be **numbers**? Because the computer can only calculate with numbers. "Has a link" becomes 1 or 0.
Turning text, pictures and URLs into good numbers is a big part of every project (Lessons 06, 07, 18, 19).

## 4. How do we know the model is good? — the three piles

Here is the trap: if we test the model on the same 5,000 SMS it studied, it can get 100 % just by **remembering**
them. That says nothing about tomorrow's SMS, which it has never seen. What we really want is called
**generalisation**: doing well on **new** examples.

So before training, we cut the data into three piles:

![train / validation / test](figs/split.png)

| pile | what it is for | school analogy |
|---|---|---|
| **training set** (e.g. 70 %) | the model learns from these | the textbook and homework |
| **validation set** (e.g. 15 %) | we try different settings and keep the best | the mock exam |
| **test set** (e.g. 15 %) | measured **once**, at the very end; this is the number we report | the real exam |

**Why only once?** If you look at the test results, change something, and look again, you are slowly "learning the
test" — like a student who sees the real exam, fails, and gets to retake *the same* exam. His second grade says nothing
about what he knows. This mistake is called **leakage** (Lesson 05).

**Stratified** means each pile gets the same share of each class. Maya's data is 13 % spam. If by bad luck the test
pile got only 2 % spam, its results would be meaningless. Stratifying deals spam and ham into the piles separately,
like dealing a deck of cards suit by suit.

### By hand

Maya has 5,000 SMS, 650 of them spam. Split 70 / 15 / 15, stratified:

```
training:   70 % of 5,000 = 0.70 × 5,000 = 3,500 SMS      of them spam: 0.70 × 650 = 455
validation: 15 % of 5,000 = 0.15 × 5,000 =   750 SMS      of them spam: 0.15 × 650 = 97.5 ≈ 97 or 98
test:       15 % of 5,000 =                  750 SMS      of them spam: ≈ 97 or 98
check: every pile is 650 / 5,000 = 13 % spam
```

## 5. Overfitting — the student who memorised

To *see* overfitting we use a simple picture. The blue dots are measurements that follow a wave, plus some random
errors (**noise** — e.g. a measuring mistake). We ask the computer to draw a curve through them. The **degree** is how
bendy the curve may be: degree 1 = a straight line, degree 15 = a curve that can bend 15 times.

![overfitting](figs/overfitting.gif)

*(Projector: `videos/overfitting.mp4`. With a slider: `python visualize.py --live`.)*

Watch the left side as the degree grows:

| degree | what happens | name |
|---|---|---|
| 0 – 2 | a flat or gently bent line: misses the wave completely | **underfitting** — too simple, like answering "C" to every question |
| 3 – 6 | follows the wave, ignores the small errors | **a good fit** |
| 7 – 15 | wiggles through **every** blue dot — including the errors — and goes crazy between them | **overfitting** — memorised the noise |

![final frame](figs/overfitting_final.png)

**The right side is the most important picture of the whole course.** The **error** is how far the curve is from the
dots (we'll compute errors exactly in later lessons).

* Blue line — error on the **training** dots: it only goes **down**. A bendier curve can always pass closer to the dots
  it has seen.
* Orange line — error on **new** dots it never saw: it goes down, then **up**.

The best model is at the **bottom of the orange line** — and we can only see that line using data the model did *not*
train on. That's the whole reason for the validation set.

**Analogy:** Two students prepare for a maths exam using last year's exam. Dana memorises the 20 answers: on last year's
exam she gets 100, on this year's exam (different numbers) she gets 40. Omar learns the *methods*: 85 on last year's,
82 on this year's. Dana **overfitted**.

## 6. Bias and variance — two kinds of mistake

![bias and variance](figs/bias_variance.png)

Imagine training the same kind of model 12 times, each time on a different random sample of Maya's SMS. Each dart is
one trained model; the bullseye is the truth.

* **Bias** = the darts land in the wrong place **on average**. The model is too simple (underfitting).
* **Variance** = the darts are **scattered**: a small change in the data changes the model a lot (overfitting).

| you see | it means | what to try |
|---|---|---|
| training score low **and** validation score low | high bias (underfitting) | more/better features, a more flexible model |
| training score high, validation score much lower | high variance (overfitting) | more data, a simpler model, a stronger "brake" |
| both high and close together | 🎉 good | stop tuning |

## 7. Common mistakes

| student says | the truth |
|---|---|
| "99 % on the training data — my model is great!" | That number says nothing about new data. Look at validation. |
| "I'll check the test set a few times while tuning" | Each look leaks. The final number becomes too optimistic. |
| "A more complex model is always better" | Only until the orange line turns up. |
| "Accuracy is enough" | With 87 % ham, "always say ham" gets 87 % and catches nothing (Lesson 03). |

## 8. Activities

1. **Write the rules (10 min).** Read 15 real SMS from `08_SpamClassifier/data/sms_spam.csv` aloud. Groups write rules on
   paper. Then read 10 *new* SMS: how many rules broke?
2. **Predict, then watch (5 min).** Before the overfitting animation: "draw on paper what degree 15 will look like".
3. **Human overfitting (10 min).** 6 cards with invented fruit (colour, size → sweet / sour), one card wrong on purpose.
   Groups write a rule that fits *all 6*. Then test on 4 new cards — the rule that "fit the wrong card" fails.
4. **Which pile? (5 min).** "Choose k for k-NN" (validation) · "the number in the book" (test) · "count the words of each
   class" (training) · "choose the spam threshold" (validation).

## 9. Do it yourself

<details><summary>1. 2,000 wines, 19 % "high quality". Split 60 / 20 / 20, stratified. How many wines and high wines in each pile?</summary>

training 0.6 × 2,000 = 1,200 wines, of them 0.19 × 1,200 = 228 high · validation 400 wines, 76 high · test 400 wines,
76 high. (Each pile: 19 %.)
</details>

<details><summary>2. Training accuracy 0.99, validation 0.71. Diagnose and give two things to try.</summary>

Overfitting (high variance): it memorised. Try a simpler model or a stronger brake (bigger α, smaller C, more dropout),
more data, or augmentation (FaceEmotion).
</details>

<details><summary>3. Why can't Laith choose his spam threshold on the test set?</summary>

Choosing is learning. If the test set helped choose, the test score is no longer a fair exam on unseen data.
</details>

## 10. In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/ml/dataset.py` → `stratified_split` (**70 / 15 / 15**), `assert_no_leakage` · theory `08_SpamClassifier/01_theory/02_ml_basics.md` |
| FaceEmotion | FER-2013 comes with train/test; `app/ml/dataset.py` → `build_dataloaders` cuts validation from train · `13_FaceEmotion/01_theory/02_ml_basics.md` |
| PhishGuard | `phishguard/ml/dataset.py` → `DatasetLoader` · `25_PhishGuard/01_theory/02_ml_basics.md` §2.3 |
| WineGrader | `winegrader/ml/folds.py` → `stratified_kfold`, then nested CV (Lesson 05) · `32_WineGrader/01_theory/02_ml_basics.md` |

## 🎬 Watch & explore

* StatQuest — *A Gentle Introduction to Machine Learning* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+gentle+introduction+to+machine+learning)
* StatQuest — *Machine Learning Fundamentals: Bias and Variance* — [search on YouTube](https://www.youtube.com/results?search_query=StatQuest+Machine+Learning+Fundamentals+Bias+and+Variance)
* MLU-Explain — [Train, Test, and Validation Sets](https://mlu-explain.github.io/train-test-validation/) (interactive)
* R2D3 — [A visual introduction to machine learning](https://r2d3.us/visual-intro-to-machine-learning-part-1/)
