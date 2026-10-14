# %% [markdown]
# # 01 · Preprocessing — the part that decides everything
#
# **Read first:** `01_theory/04_pipeline.md` (read it twice — it says so itself)
#
# Every method later compares **term lists**. If the same skill written two ways does not become the same
# string here, nothing downstream can match it. In this notebook:
#
# 1. scrub personal data (emails, phones)
# 2. tokenize **without killing C++, C# and .NET**
# 3. lower-case, stop words, stemming, bigrams
# 4. run the pipeline on the 200 synthetic CVs
# 5. normalise the skills dictionary with the **same** pipeline

# %%
import csv
import re
from collections import Counter
from pathlib import Path

from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

resumes = list(csv.DictReader(open(Path("../data/resumes.csv"), encoding="utf-8")))
jobs = list(csv.DictReader(open(Path("../data/jobs.csv"), encoding="utf-8")))
print(len(resumes), "CVs (synthetic - real CVs are personal data),", len(jobs), "jobs")
print(resumes[5]["text"][:400])

# %% [markdown]
# ## 1. Scrub personal data — with a SPACE
#
# Two reasons: **privacy** (an email must never appear in an explanation on screen) and **quality** (an email
# appears in one document only, so it carries no ranking signal). Replace with a space, or two words get glued.

# %%
EMAIL_RE = re.compile(r"\S+@\S+\.\w+")
PHONE_RE = re.compile(r"\+?\d[\d\-\s]{7,}\d")
ID_RE = re.compile(r"\b\d{9}\b")

def scrub(text):
    for pattern in (EMAIL_RE, PHONE_RE, ID_RE):
        text = pattern.sub(" ", text)
    return text

print(scrub("Noa Cohen. Email noa12@mail.com, phone 054-1234567. ID 123456789. Skills: Python."))

# %% [markdown]
# ## 2. Tokenizing — where C++ goes to die
#
# The obvious regex `\w+` silently destroys the most important tokens in a tech CV:

# %%
text = "Skills: C++, C#, .NET, Node.js and Python 3."
print(r"\w+      ->", re.findall(r"\w+", text))

SIMPLE = re.compile(r"[A-Za-z֐-׿][A-Za-z0-9֐-׿+#.]*")
print("letters  ->", SIMPLE.findall(text))

# %% [markdown]
# Better — `C++`, `C#` and `Node.js` survive — but two new problems: `.NET` lost its dot (a token must start with a
# letter), and a word that ends a sentence keeps the full stop: `Python.` would become a different term from
# `Python`. Your project's `config.TOKEN_PATTERN` adds two small pieces:
#
# | piece | means |
# |---|---|
# | `\.?` at the start | an optional leading dot → `.NET` keeps it |
# | `(?<!\.)` at the end | the token may not **end** with a dot → `Python.` becomes `Python`; `Node.js` keeps its inner dot |

# %%
TOKEN_PATTERN = re.compile(r"\.?[A-Za-z֐-׿][A-Za-z0-9֐-׿+#.]*(?<!\.)")    # = config.TOKEN_PATTERN

def tokenize(text):
    return TOKEN_PATTERN.findall(text)

print(tokenize("I know C++, C#, .NET and Node.js. I love Python."))

# %% [markdown]
# Your project's tests decide the exact rules (`test_technical_tokens_survive`). The lesson is the method:
# **write down the tricky tokens first, then make the pattern keep them.**
#
# ## 3. Lower-case, stop words, stemming, bigrams
#
# * stop words: words in every CV that separate nobody ("the", "and", "with")
# * stemming (NLTK Snowball): developed / developing / development → `develop`
# * bigrams: "machine learning" as one extra term

# %%
stemmer = SnowballStemmer("english")
STOP = ENGLISH_STOP_WORDS

def process(text, use_stemming=True, bigrams=True):
    tokens = [t.lower() for t in tokenize(scrub(text))]
    tokens = [t for t in tokens if t not in STOP and len(t) > 1 or t in ("c", "go", "r")]
    if use_stemming:
        tokens = [stemmer.stem(t) for t in tokens]
    if bigrams:
        tokens = tokens + [f"{a} {b}" for a, b in zip(tokens, tokens[1:])]
    return tokens

print(process("Developed machine learning models; developing the Development team's skills in C++."))

# %% [markdown]
# Look at the bigrams: `machin learn` is now one term. It matches "Machine Learning" in a job advert but not
# "learning to use a machine". Some bigrams are noise (`model develop`) — that is the price.
#
# ## 4. The whole collection

# %%
docs = [process(r["text"]) for r in resumes]
lengths = [len(d) for d in docs]
df = Counter(t for d in docs for t in set(d))
print(f"terms per CV: min {min(lengths)}, median {sorted(lengths)[100]}, max {max(lengths)}")
print("distinct terms:", len(df))
print("in the most CVs:", df.most_common(12))

# %% [markdown]
# Words like `work` and `respons` are in almost every CV — they will get a low IDF in notebook 02. Skills like
# `kubernet` are in few — a high IDF.
#
# **Check that no personal data survived:**

# %%
leaks = [t for d in docs for t in d if "@" in t or re.search(r"\d{6,}", t)]
print("personal data left in the index:", leaks[:5] or "none")

# %% [markdown]
# ## 5. The skills dictionary — the same pipeline, or no match
#
# If the dictionary says "Machine Learning" and the CV became `machin learn`, a plain string comparison never
# matches. So every skill goes through **the same** `process()`; we keep the normalised form for matching and
# the original for display.

# %%
SKILLS = ["Python", "Machine Learning", "C++", "C#", ".NET", "Django", "Kubernetes", "REST APIs", "SQL Server"]

def normalise_skill(skill):
    terms = process(skill, bigrams=False)
    return " ".join(terms)

skill_index = {normalise_skill(s): s for s in SKILLS}
print(skill_index)

def skills_in(doc_terms):
    terms = set(doc_terms)
    return sorted(display for norm, display in skill_index.items() if norm in terms)

print("R000:", skills_in(docs[0]))
print("R005:", skills_in(docs[5]))

# %% [markdown]
# Two-word skills match for free, because the documents already contain bigrams. Three-word skills would
# need trigrams — a limitation worth one sentence in your book.
#
# ## ✍️ Try it yourself
#
# 1. Run `process` with `\w+` instead of `tokenize`. How many CVs still contain the term `c++`?
# 2. Turn stemming off. How many distinct terms are there now? Which skills stop matching?
# 3. Add a Hebrew sentence to a CV (`פיתחתי אתרים ב-Python`). What do the tokens look like? Why is Hebrew
#    stemming hard? (theory: one prefix letter, only for words longer than 3 letters)
#
# Then solve exercises 1–4 in `03_exercises/`.
