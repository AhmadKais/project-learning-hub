# Lesson 06 — Cleaning text: from a message to a list of terms

> **For:** Laith (SpamClassifier stage 2) · Kosai (ResumeMatch stage 2 — "the gatekeeper") &nbsp;·&nbsp; **Time:** 45 min
> **Before:** basic Python strings and `re` &nbsp;·&nbsp; **After this:** Lesson 07 (TF-IDF)

## 🎯 By the end, the student can

1. Name the steps of their own pipeline **in order**, and say why the order matters.
2. Explain tokenizing, lower-casing, stop-words, stemming and n-grams, each with one example.
3. Explain why the **same** preprocessing must run at training time and at prediction time.

---

## 1. Why this lesson exists

A model can only learn from what the preprocessing lets through. If the tokenizer turns `C++` into `C`, no ranking
algorithm can ever find the C++ developer. **Garbage in, garbage out — silently.**

## 2. Watch the two pipelines

### ResumeMatch (Kosai)

![ResumeMatch pipeline](figs/resume_pipeline.gif)

| Step | Example | Why |
|---|---|---|
| scrub personal data | `noa96@mail.com` → removed | privacy; names must not influence ranking |
| tokenize with `TOKEN_PATTERN` | `C++`, `Node.js`, `.NET` stay whole; `Docker.` → `Docker` | technical words are the whole point |
| lower-case | `Python` = `python` | one term, not two |
| drop stop-words | `in`, `and`, `with` | they are in every CV, they carry no meaning |
| stem (Snowball) | `developed, developing, development` → `develop` | variants match each other |
| add bigrams | `machin learn` | two-word skills become one term |

### SpamClassifier (Laith)

![Spam pipeline](figs/spam_pipeline.gif)

The important difference: **measure before you normalise.** `caps_ratio` and `exclamation_count` are computed on the
**raw** text — after lower-casing, caps_ratio is always 0. Every URL becomes the single token `URLTOKEN` (what transfers
to new spam is "there is a link", not "bit.ly").

## 3. One regular expression decides everything

![tokenizers compared](figs/tokenizers.png)

Read Kosai's pattern piece by piece on the board:

```
\.?                          an optional dot at the start          .NET
[A-Za-z֐-׿]        then a letter (Latin or Hebrew)       never a number like 3.5
[A-Za-z0-9֐-׿+#.]* then letters, digits, + # .           C++, C#, Node.js
(?<!\.)                      may not END with a dot                Docker. → Docker
```

## 4. Why stop-words go — Zipf's law

![Zipf's law](figs/zipf.png)

In any language a few words are everywhere (`i, to, you, a, the`) and most words are rare (half of the SMS words appear
**once**). Words that appear everywhere cannot tell spam from ham or one CV from another — removing them makes the
vectors smaller and the important words louder. (TF-IDF in Lesson 07 does the same thing more gently.)

## 5. Definitions

| Word | Meaning | Example |
|---|---|---|
| **token** | one piece the text is cut into | `free`, `c++` |
| **term** | a token after all the processing (what gets counted) | `develop`, `machin learn` |
| **stop-word** | a very common word with no content | `the`, `and`, `של` |
| **stem** | the word cut to a common root (not always a real word!) | `machin`, `learn` |
| **n-gram** | n adjacent tokens as one term | bigram `click here` |
| **vocabulary** | the list of all terms the model knows | Spam: 5,000 most common by document frequency |

## 6. The contract between training and prediction

The preprocessing is **part of the model**. If training stemmed and the app does not, the app produces terms the model
never saw → zero matches, no error. Defences in the projects:

* Kosai: `TextPreprocessor.fingerprint()` — a hash of the settings (`PIPELINE_VERSION`, stop-word versions) saved in
  the index bundle and checked on load.
* Laith: the feature names and order go into `features.json` in the bundle and are verified on load.

## 7. Misconceptions

| Student says | Truth |
|---|---|
| "Stemming gives real words" | `machin`, `learn`, `compani` — it is a matching key, not a word. That is fine. |
| "Lower-case first, it's simpler" | Not in Spam: you destroy `caps_ratio` before measuring it (`test_parse_measures_caps_before_lowercasing`). |
| "More n-grams = better" | Trigrams multiply the vocabulary for very little gain. Measure it. |
| "`\w+` is a good tokenizer" | See the table above. |

## 8. Activities

1. **Be the pipeline (10 min).** Each student gets one step on a card (tokenize / lower / stop / stem / bigram). Pass a
   paper strip with a sentence around the room; each one applies only their step.
2. **Break the tokenizer (10 min).** Pairs invent words that break `TOKEN_PATTERN` (try `F#`, `R`, `3D`, `Vue.js`, `C`).
   Which ones are a real problem for a CV search? (`R` and `C` are single letters — do they survive the pattern? should they?)
3. **Order matters (5 min).** What happens if you add bigrams **before** removing stop-words? (`machine learning` is
   fine, but you also get `in c++`, `and node.js` — garbage terms.)

## 9. Check yourself

<details><summary>1. Run Laith's pipeline by hand on "Call NOW to claim your £500 prize!! www.cash4u.com"</summary>

caps measured on raw text first; URL → URLTOKEN; lower-case; words `[a-z']+`: call, now, to, claim, your, prize, URLTOKEN
(`£500` has no letters); drop < 3 letters and stop-words: `now`, `to`, `your` go → `call, claim, prize, URLTOKEN`;
bigrams `call claim, claim prize, prize URLTOKEN`.
</details>

<details><summary>2. Why does Kosai strip only ONE Hebrew prefix letter, and only from words longer than 3 letters?</summary>

Hebrew prefixes (ה ו ב ל מ ש כ) are also ordinary first letters. Stripping aggressively merges unrelated words. One
prefix on longer words is a conservative compromise — and a limitation to state in the book.
</details>

<details><summary>3. The app returns no candidates for "Docker" although many CVs mention it. Name two pipeline bugs that cause this.</summary>

The query is not processed with the same pipeline (not lower-cased / not stemmed), or the tokenizer keeps the trailing
dot (`docker.` ≠ `docker`). Check the fingerprint and the TOKEN_PATTERN.
</details>

## 10. In your project

| Project | Where |
|---|---|
| Spam | `spamclassifier/preprocessing/email_parser.py` → `EmailParser.parse` (the 7 steps) · `tokenizer.py` → `Tokenizer.tokenize`, `ngrams` · theory `08_SpamClassifier/01_theory/03_features.md` §3.6–3.9 |
| ResumeMatch | `resumematch/nlp/preprocessor.py` → `TextPreprocessor.process`, `_stem`, `_stem_hebrew`, `_bigrams`, `fingerprint` · `nlp/pii.py` → `PiiScrubber` · theory `31_ResumeMatch/01_theory/04_pipeline.md` |
| Notebook | `31_ResumeMatch/02_examples/01_preprocessing.ipynb` · `08_SpamClassifier/02_examples/01_text_to_numbers.ipynb` |

## 🎬 Watch & explore

* *Stemming vs Lemmatization* — [search on YouTube](https://www.youtube.com/results?search_query=stemming+vs+lemmatization+NLP+explained)
* regex101 — [test TOKEN_PATTERN live](https://regex101.com/) (paste the pattern and a CV line; choose the Python flavour)
* NLTK book, chapter 3 — [Processing Raw Text](https://www.nltk.org/book/ch03.html)
