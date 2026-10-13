# Step 4 — Preprocessing: the part that decides everything

This is the most important chapter in the guide. Read it twice.

## Why it decides everything

Every method above compares **term lists**. If the same skill written two ways
does not become the same string here, nothing downstream can match it:

```
CV says:  "פיתחתי אתרים"      -> term: "פיתח"
Job says: "Web Development"    -> term: "web develop"

                  no match. score: 0.000
```

The candidate is perfect and the system never sees it. No ranking algorithm on
earth fixes that — the damage was done before ranking started.

## The pipeline, in order

```
raw text
   -> scrub PII        remove emails, phones, ID numbers
   -> tokenize         split into words (carefully!)
   -> lowercase        Python == python
   -> drop stopwords   "the", "של", "and"
   -> stem             developed/developing/development -> develop
   -> add bigrams      "machine learning" as one term
term list
```

## Tokenizing — where C++ goes to die

The obvious approach:

```python
tokens = re.findall(r"\w+", text)      # DO NOT DO THIS
```

What it does to real CVs:

```
"C++"    ->  ["C"]        the ++ is gone
"C#"     ->  ["C"]        so is the #
".NET"   ->  ["NET"]
"Node.js" -> ["Node", "js"]   split in two
```

You have just lost every C++ and C# developer, and they will never rank for a
C++ job. Silently.

📄 **The pattern that works**

```python
TOKEN_PATTERN = r"[A-Za-z\u0590-\u05FF][A-Za-z0-9\u0590-\u05FF+#.]*"
```

Reading it: start with a letter (Latin **or** Hebrew), then allow letters,
digits, `+`, `#` and `.`. Now `C++`, `C#` and `.NET` survive intact.

💡 There is a test for exactly this (`test_technical_tokens_survive`). It exists
because this bug is invisible — everything *looks* fine.

## Stemming

Reduce words to a common root so variants match:

```
developed, developing, develops, developer, development  ->  develop
```

For English, use NLTK's Snowball stemmer — it is a standard, tested
implementation of Porter's algorithm. Writing your own would add no
understanding, only bugs.

For **Hebrew** there is no ready-made stemmer, because Hebrew morphology is much
harder (root-and-pattern, plus prefix letters like ה, ו, ב, ל, מ, ש, כ). We strip
**one** prefix, and only from words longer than 3 letters:

```python
if len(token) > 3 and token[0] in config.HEBREW_PREFIXES:
    token = token[1:]
```

⚠️ Be conservative. Over-stripping merges unrelated words and quietly wrecks the
ranking. **Write this limitation in your book** — "Hebrew stemming is partial; a
full morphological analyser is the correct solution" is an honest, mature thing
to say, and examiners respect it.

## Bigrams

Some skills are two words:

```
"Machine Learning"    is one thing
"machine" + "learning" would also match "learning to use a machine"
```

So generate pairs of adjacent tokens as extra terms:

```python
bigrams = [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)]
terms = tokens + bigrams
```

Cost: the vocabulary grows a lot. Benefit: two-word skills actually match. Test
it both ways in stage 11 and report the numbers.

## Scrubbing personal data

Remove emails, phone numbers and ID numbers **before** building the vocabulary.
Two independent reasons — give both when asked:

1. **Privacy** — an email address must never appear in the index or in an
   explanation shown on screen.
2. **Quality** — an email appears in exactly one document, so it carries no
   ranking signal anyway. Removing it costs nothing.

⚠️ Replace with a **space**, not an empty string, or two words get glued
together into a fake term.

## The fingerprint — your contract between two machines

This is the subtlest idea in the project, so go slowly.

Machine A builds the index. Machine B ranks with it. If B preprocesses even
slightly differently — different stemmer, different stopword list — then the
job's terms are not in the vocabulary, and:

```
every score = 0.000
no exception
no warning
the program looks like it is working
```

That is a **silent failure**, and it is much more dangerous than a crash.

📄 **The defence**

```python
def fingerprint(self):
    return {
        "lowercase":     config.LOWERCASE,
        "token_regex":   config.TOKEN_PATTERN,
        "stopwords_he":  config.STOPWORDS_HE_VERSION,
        "stopwords_en":  config.STOPWORDS_EN_VERSION,
        "stemmer":       "snowball_english" if self.use_stemming else "none",
        "hebrew_rules":  config.HEBREW_RULES_VERSION,
        "ngram_max":     self.ngram_max,
        "pipeline_version": config.PIPELINE_VERSION,
    }
```

Machine B compares this **field by field** before ranking anything, and refuses
to load if one differs.

❓ **Why refuse instead of continuing?**

Because returning confident, wrong answers is worse than returning none.
A recruiter would act on those rankings.

💡 Demo for your defence: change one value in `index/preprocess.json`, run
`run.py`, and show it refusing with a clear message. Thirty seconds, and it
proves you understand deployment.
