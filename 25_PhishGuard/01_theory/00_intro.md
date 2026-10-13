# How to use this guide

This guide was written for you, Dani, with one assumption: **you have no background in machine
learning.** Every idea is explained from zero, in simple words, with a small number example you
can check by hand.

The guide has three parts:

- **Part A — Understand the problem.** What phishing is, what "learning" means for a computer, how a
  URL becomes numbers, how the two models work, how we measure them honestly, and how the code is
  organized. Read this part **before** you write a single line of code. One or two evenings.
- **Part B — Build the code.** Step by step, file by file, together with `TASKS.md` in the code folder.
- **Part C — Pass the exam.** Questions your supervisor or examiner may ask, with answers.

Two rules for the whole way:

1. **Never copy code you do not understand.** In the defense you will be asked to explain every line.
2. **Every number in the project book comes from a run on your own computer.** Accuracy, recall,
   training time — all from `reports/` on your machine.

Symbols: ❓ possible supervisor question · 💡 tip · 📄 code / example · ✅ check yourself (answers in the appendix).

---

# Part A — Understand the problem

# Chapter 1 — What does the system do?

## 1.1 In one sentence

PhishGuard looks at a web address (URL), and — without visiting it — says whether it is a real site
or a fake one built to steal passwords, with a risk percentage and the reasons.

## 1.2 What phishing is

You get a message: "Your PayPal account is suspended — click here to verify." The link looks like
PayPal. It is not. It goes to `http://paypal.com.secure-login.xyz/verify` — a site owned by the attacker,
that shows a copy of the PayPal login page and records what you type. That is **phishing**: a fake
address pretending to be a trusted one. Millions of such links appear every month, and most of them
live only a day — so lists of "known bad sites" are always behind.

## 1.3 The journey of one URL

1. **The user** pastes a URL into the app.
2. **The parser** splits it into pieces: scheme (`http`), host (`paypal.com.secure-login.xyz`),
   subdomains (`paypal`, `com`), real domain (`secure-login`), ending (`xyz`), path (`/verify`).
3. **The feature extractor** turns the URL into 20 numbers: its length, how many dots, is the host an IP
   address, is there an `@`, does it use HTTPS, how many "suspicious words" (login, verify, secure…),
   is a brand name hiding in the subdomain, and so on.
4. **The model** takes the 20 numbers and returns one number: the probability that this is phishing,
   for example 0.91.
5. **The threshold** turns the probability into a verdict: 0.91 ≥ 0.40 → **phishing**.
6. **The explainer** lists the three features that pushed hardest: "brand name in the subdomain",
   "suspicious ending .xyz", "no HTTPS".
7. **The database** saves the scan with the time; the screen shows the verdict, a red risk meter, and the reasons.

## 1.4 Two programs

- `train.py` — **teaches** the model. Reads ~20,000 labelled URLs, computes their features, fits two
  models, measures them, and saves the better one to `models/phishguard_best.joblib`. Runs in under a minute.
- `run.py` — **uses** the model. Loads the saved file and scans whatever the user pastes.

The app never learns. It only uses what `train.py` learned. Keep this separation in your head — it
is chapter 6 of your book.

## 1.5 Why this is a real problem, not a lookup

A blacklist answers "have we seen this exact URL before?". PhishGuard answers "does this URL *look*
like the fake ones?" — so it works on a link that was created five minutes ago. The whole skill of
the project is deciding what "looks like" means in numbers. That is called **feature engineering**,
and it is chapter 3.
