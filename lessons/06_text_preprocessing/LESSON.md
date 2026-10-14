# Lesson 06 — Cleaning text: from a message to a list of words the computer can count

> **For:** Laith (SpamClassifier stage 2) · Kosai (ResumeMatch stage 2 — "the gatekeeper") &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 01; Python strings and lists &nbsp;·&nbsp; **After this:** Lesson 07 (TF-IDF)

## The story

> **Hila is a recruiter at a software company.** A job for a "C++ developer" gets 200 CVs. She asks Kosai's program to
> find the CVs that mention C++. The program finds **none** — although she *knows* at least ten do. The reason is not the
> clever ranking maths: it's the very first step, where the program cut the text into words and turned "C++" into "C".
> This lesson is about that first step — the one that decides what the computer is allowed to see.

## 🎯 By the end, the student can

1. Name the steps of their own cleaning pipeline **in order** and say why the order matters.
2. Explain tokenizing, lower-casing, stop-words, stemming and n-grams, each with an example.
3. Read the project's regular expression piece by piece.
4. Explain why the **same** cleaning must happen when training and when the program is used.

## Words you need

| word | meaning | example |
|---|---|---|
| **text** | for the computer: a long string of characters | `"Developed REST APIs in C++"` |
| **token** | one piece the text is cut into | `Developed`, `REST`, `C++` |
| **tokenizing** | cutting text into tokens | |
| **lower-casing** | making every letter small, so "Python" = "python" | |
| **stop-word** | a very common word that carries no meaning on its own | the, and, in, with |
| **stemming** | cutting a word to a common root, so its forms match | developed / developing / development → develop |
| **n-gram** | n neighbouring tokens glued into one term; **bigram** = 2 | "machine learning" |
| **term** | a token after all cleaning — what will be counted | `develop`, `machin learn` |
| **vocabulary** | the list of all different terms | |
| **pipeline** | the fixed order of cleaning steps | |
| **regular expression (regex)** | a mini-language that describes a pattern of characters | `[a-z]+` = "one or more small letters" |

---

## 1. Why cleaning decides everything

The computer cannot read. To compare a CV with a job advert it will **count words** (Lesson 07). So we must turn the
text into a clean list of words, and every decision matters:

* Is "Python" the same word as "python"? (should be)
* Is "developed" the same as "development"? (for search: yes)
* Is "C++" a word? (for Hila: absolutely)
* Do "the" and "and" matter? (no — they are in every CV)

## 2. Watch the two pipelines

### Kosai's CV pipeline

![ResumeMatch pipeline](figs/resume_pipeline.gif)

Step by step on one CV sentence:

| step | what happens | result |
|---|---|---|
| 0. raw | | `Noa Saleh, noa96@mail.com. Developed REST APIs in C++ and Node.js; used Machine Learning with Docker.` |
| 1. scrub personal data | names, e-mails, phones are removed — they must not influence the ranking, and it's private | `Developed REST APIs in C++ and Node.js; used Machine Learning with Docker.` |
| 2. tokenize | cut into tokens with a careful pattern (§3) | `Developed · REST · APIs · in · C++ · and · Node.js · used · Machine · Learning · with · Docker` |
| 3. lower-case | so "Docker" = "docker" | `developed · rest · apis · in · c++ · …` |
| 4. drop stop-words | in, and, with disappear | `developed · rest · apis · c++ · node.js · used · machine · learning · docker` |
| 5. stem | words cut to roots | `develop · rest · api · c++ · node.js · use · machin · learn · docker` |
| 6. add bigrams | every neighbouring pair becomes one more term | `… · machin learn · learn docker · …` |

Notice **"machin"** — stems are not always real words. That's fine: they are only matching keys. What matters is that
"machine", "machines" and "machining" all become the same key.

Why the **bigram** step? A CV with "machine learning" and a CV with "learned to use a machine" both contain *machin* and
*learn*. Only the first contains the term **machin learn**.

### Laith's SMS pipeline

![Spam pipeline](figs/spam_pipeline.gif)

| step | what happens | why |
|---|---|---|
| 1. **measure first** | count capitals (caps_ratio), "!" and links on the **raw** text | after lower-casing, caps_ratio would always be 0 — the signal "SHOUTING" would be lost |
| 2. links → `URLTOKEN` | every URL becomes the same token | "there is a link" is a spam signal; the exact address (bit.ly/x7) never repeats |
| 3. lower-case (keep `URLTOKEN`) | | |
| 4. words = runs of letters `[a-z']+` | | numbers and symbols are dropped |
| 5. drop words < 3 letters and stop-words | "a", "to", "you", "now" go | |
| 6. n-grams (1, 2) | words + neighbouring pairs | "click here" means more than "click" + "here" |

**The order matters:** measure caps **before** lower-casing (`test_parse_measures_caps_before_lowercasing`).

## 3. One regular expression decides whether C++ exists

A **regular expression** describes what a token looks like. The obvious one, `\w+`, means "one or more letters, digits
or underscores". Here is what it does to technical words:

![tokenizers compared](figs/tokenizers.png)

`C++` → `C`. `.NET` → `NET`. `Node.js` → two tokens. Hila's C++ developers vanish. Kosai's pattern, piece by piece:

```
\.?                          maybe one dot at the very start            → keeps .NET
[A-Za-z֐-׿]        then one letter, English or Hebrew         → a token never starts with a digit, so 3.5 isn't a word
[A-Za-z0-9֐-׿+#.]* then any number of letters, digits, + # .  → C++, C#, Node.js, ASP.NET stay whole
(?<!\.)                      the token may NOT end with a dot           → "Docker." at the end of a sentence becomes Docker
```

Small regex vocabulary: `[abc]` = one of these characters · `*` = zero or more times · `+` = one or more · `?` = maybe ·
`\.` = a real dot (a plain `.` means "any character").

## 4. Why stop-words go — Zipf's law

![Zipf's law](figs/zipf.png)

Count every word in the 5,574 SMS and sort them. A handful of words (`i, to, you, a, the`) appear **thousands** of times;
**half** of all different words appear only **once**. This shape appears in every language and is called **Zipf's law**.
Words that are everywhere cannot tell spam from ham, or one CV from another — so we drop them, and the important words
become louder.

## 5. The contract: the same cleaning, always

The cleaning is **part of the model**. Suppose the model was trained on stemmed words (`develop`) but the app forgets to
stem the job advert (`developing`): zero matches, and **no error message**. The projects protect against this:

* Kosai: `TextPreprocessor.fingerprint()` — a code made from all cleaning settings, saved with the index and checked when
  loading.
* Laith: the feature names and order are saved in `features.json` and checked when loading.

## 6. Common mistakes

| student says | the truth |
|---|---|
| "Stemming gives real words" | `machin`, `learn`, `compani` — matching keys, not words. Fine. |
| "Lower-case first, it's simpler" | Not in Spam: you destroy `caps_ratio` before measuring it. |
| "More n-grams = better" | Trigrams multiply the vocabulary for little gain. Measure it. |
| "`\w+` is a good tokenizer" | See the table in §3. |

## 7. Activities

1. **Be the pipeline (10 min).** Each student gets one step on a card. Pass a paper strip with a sentence around; each
   student applies only their step, out loud.
2. **Break the tokenizer (10 min).** Pairs try words like `F#`, `R`, `3D`, `Vue.js`, `C` on regex101.com with Kosai's
   pattern. Which ones are a real problem for a CV search?
3. **Order matters (5 min).** What if bigrams are added **before** removing stop-words? (You get junk terms like
   `in c++`, `and node.js`.)

## 8. Do it yourself

<details><summary>1. Run Laith's pipeline on: "Call NOW to claim your £500 prize!! www.cash4u.com"</summary>

1. measure: caps_ratio from "C" + "NOW" (4 capitals of all letters), 2 "!", 1 link. 2. → `… prize!! URLTOKEN`.
3. lower-case. 4. words: call, now, to, claim, your, prize, URLTOKEN (£500 has no letters). 5. drop "to" (short) and
"now", "your" (stop-words) → `call, claim, prize, URLTOKEN`. 6. bigrams: `call claim, claim prize, prize URLTOKEN`.
</details>

<details><summary>2. Stem with Snowball: "running", "runs", "runner". Do they all match?</summary>

`run`, `run`, `runner` — the first two match; "runner" stays different (a person, not an action). Stemmers are rough.
</details>

<details><summary>3. The app finds no CV for "Docker" although many mention it. Two possible pipeline bugs?</summary>

The job text is not cleaned with the same pipeline (not lower-cased / not stemmed), or the tokenizer keeps the trailing
dot (`docker.` ≠ `docker`).
</details>

## 9. In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/preprocessing/email_parser.py` → `EmailParser.parse` · `tokenizer.py` → `Tokenizer.tokenize`, `ngrams` · theory `08_SpamClassifier/01_theory/03_features.md` §3.6–3.9 · notebook `01_text_to_numbers.ipynb` |
| ResumeMatch | `resumematch/nlp/preprocessor.py` → `TextPreprocessor.process`, `_stem`, `_stem_hebrew`, `_bigrams`, `fingerprint` · `nlp/pii.py` → `PiiScrubber` · theory `31_ResumeMatch/01_theory/04_pipeline.md` · notebook `01_preprocessing.ipynb` |

## 🎬 Watch & explore

* *Stemming vs lemmatization* — [search on YouTube](https://www.youtube.com/results?search_query=stemming+vs+lemmatization+NLP+explained)
* *Regular expressions for beginners* — [search on YouTube](https://www.youtube.com/results?search_query=regular+expressions+tutorial+for+beginners)
* regex101 — [test TOKEN_PATTERN live](https://regex101.com/) (choose the Python flavour)
