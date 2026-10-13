# Chapter 1a — The Python you need (read before anything else)

You do not need to be a Python expert. You need these ten things, and you need them well. Every
one appears in the skeleton. If any of them is new — stop and try it in a Python shell
(`python` in the terminal, then type the example).

## 1a.1 Strings — the URL is a string

📄 **What you will do to URLs**
```python
url = "http://PayPal.com.secure-login.xyz/verify"
url.lower()                 # 'http://paypal.com.secure-login.xyz/verify'
url.count(".")              # 3
"@" in url                  # False
url.startswith("https")     # False
url.split("/")              # ['http:', '', 'paypal.com.secure-login.xyz', 'verify']
len(url)                    # 43
sum(ch.isdigit() for ch in url)   # how many digits: 0
```

## 1a.2 Lists and dictionaries

📄 **Lists = ordered; dicts = named**
```python
names = ["url_length", "num_dots", "has_https"]      # a list - order matters
names[0]            # 'url_length'
len(names)          # 3

values = {"url_length": 43, "num_dots": 3, "has_https": 0}   # a dict - name -> value
values["num_dots"]  # 3
values["new"] = 1   # add a key
list(values)        # the keys: ['url_length', 'num_dots', 'has_https', 'new']
```

**Why both:** the model needs the numbers in a fixed *order* (a list), but humans want them by
*name* (a dict). `FeatureVector.as_list(names)` converts the dict to the list in the right order:

📄 **The conversion you will write in stage 1**
```python
[values[name] for name in names]      # -> [43, 3, 0]
```

That `[... for ... in ...]` is a **list comprehension**: "build a list by doing this for every item".
Read it as: *for each name in names, take values[name]*.

## 1a.3 Functions and `return`

📄 **A function that returns a number**
```python
def count_dots(url):
    return url.count(".")

count_dots("a.b.c")     # 3
```

Every `TODO` in the skeleton is a function body you fill. Notice the skeleton functions end with
`raise NotImplementedError` — that is a placeholder that says "not written yet". You delete that line
and write the body.

## 1a.4 Classes and `self`

A **class** is a blueprint; an **object** is one thing built from it. `self` is "this object".

📄 **A tiny class**
```python
class Counter:
    def __init__(self, start):     # runs when you create the object
        self.value = start         # self.value belongs to THIS object

    def add(self, n):
        self.value += n
        return self.value

c = Counter(10)
c.add(5)        # 15
c.value         # 15
```

`URLFeatureExtractor`, `Predictor`, `ScanRepository` are classes like this — with a few methods you fill.

## 1a.5 `@dataclass` — a class that is just data

📄 **Instead of writing `__init__` by hand**
```python
from dataclasses import dataclass

@dataclass
class ScanResult:
    url: str
    probability: float
    verdict: str

r = ScanResult("http://x.y", 0.91, "phishing")
r.probability      # 0.91
```

The entities in `phishguard/models/entities.py` are dataclasses. You do not write them — you use them.

## 1a.6 `Enum` — a fixed set of names

📄 **Verdict**
```python
from enum import Enum

class Verdict(str, Enum):
    LEGITIMATE = "legitimate"
    PHISHING = "phishing"

Verdict.PHISHING.value       # 'phishing'   (the string, for the database)
Verdict("phishing")          # Verdict.PHISHING   (from the string, when reading back)
```

## 1a.7 Imports — where things come from

📄 **Reading an import line**
```python
from phishguard.features.extractor import URLFeatureExtractor
#     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^        ^^^^^^^^^^^^^^^^^^^
#     folder/folder/file.py                the class inside it
import config           # the file config.py at the project root
config.DEFAULT_THRESHOLD
```

If you see `ModuleNotFoundError: phishguard`, you ran Python from the wrong folder. Always run
commands from the `PhishGuard` folder (the one with `config.py`).

## 1a.8 `try` / `except` — handling errors on purpose

📄 **Do not let garbage crash the program**
```python
try:
    port = parsed.port          # can raise ValueError on "http://x:abc"
except ValueError:
    port = None
```

## 1a.9 Reading a traceback (the error message)

📄 **A traceback**
```text
Traceback (most recent call last):
  File "train.py", line 41, in main
    split = loader.load()
  File "phishguard/ml/dataset.py", line 62, in load
    X = np.array(self.extractor.extract_many(urls))
  File "phishguard/features/extractor.py", line 71, in extract_many
    return [self.extract(u).as_list(FEATURE_NAMES) for u in urls]
  File "phishguard/models/entities.py", line 30, in as_list
    return [self.values[name] for name in feature_names]
KeyError: 'entropy'
```

Read it **bottom-up**: the last line is *what* went wrong (`KeyError: 'entropy'` — a dict has no key
"entropy"). Then go up to the first line that is in **your** code (`as_list` … `extract`) — that is
*where*. Here: `extract()` forgot to put `entropy` into the dict. The lines above that are just how
Python got there.

## 1a.10 The terminal, the venv, pytest

- The **terminal** in VS Code (Ctrl+`) is where you run everything.
- `.venv\Scripts\activate` — you must see `(.venv)` at the start of the line. If not, packages are missing.
- `pytest -v` runs all tests; `pytest tests/test_extractor.py -v` runs one file;
  `pytest tests/test_extractor.py -k entropy -v` runs only tests with "entropy" in the name.
- A test shows `PASSED` or `FAILED` with an `assert` line. `assert v["num_dots"] == 3` failing with
  `assert 2 == 3` means your code returned 2.

## ✅ Check yourself — Chapter 1a

1. What does `"a.b.c".split(".")` return? And `len("a.b.c")`?
2. Write a list comprehension that gives the lengths of the strings in `["ab", "cde", "f"]`.
3. `d = {"x": 1}`. What happens on `d["y"]`? How do you get `None` instead of an error?
4. In `class A: def __init__(self, n): self.n = n` — what is `A(7).n`?
5. Read this traceback's last line and say which function to open:
   `File "phishguard/features/url_parser.py", line 40, in parse ... AttributeError: 'NoneType' object has no attribute 'lower'`
6. What does `raise NotImplementedError` mean, and what do you do with it?

## 📚 Further reading — Chapter 1a

- **Python official tutorial**, sections 3–5 and 9: https://docs.python.org/3/tutorial/ (strings, lists, dicts, functions, classes)
- **Real Python — Data Classes**: https://realpython.com/python-data-classes/
- **Real Python — Understanding the Python Traceback**: https://realpython.com/python-traceback/
- **pytest — Getting Started**: https://docs.pytest.org/en/stable/getting-started.html
