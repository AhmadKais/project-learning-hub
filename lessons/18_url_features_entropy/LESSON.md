# Lesson 18 — A URL as numbers: feature engineering and Shannon entropy

> **For:** Dani (PhishGuard stage 1 — the heart of the project) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Lesson 00 §1, §4, §7; Lesson 01; Python strings &nbsp;·&nbsp; **After this:** Lessons 12, 13

## The story

> Dani's grandmother gets an SMS: *"Your PayPal account is locked. Verify here: http://paypal.com.secure-login.xyz/verify"*.
> She asks Dani: *"It says PayPal — is it real?"* Dani looks and says *"No! The real owner of this address is
> 'secure-login.xyz', not PayPal."* How did he know so fast? He looked at **clues**: where "paypal" appears, the strange
> ending ".xyz", the words "verify" and "login", no HTTPS. A model can't "look" — it needs each clue as a **number**.
> Turning a URL into well-chosen numbers is called **feature engineering**, and it decides how good PhishGuard can be.

## 🎯 By the end, the student can

1. Take a URL apart and say who really owns it.
2. Compute the main features of a URL by hand.
3. Compute Shannon entropy for a short string, step by step, and explain what it measures.
4. Explain train/serve skew and the three guards against it.

## Words you need

| word | meaning | example |
|---|---|---|
| **URL** | a web address | `http://paypal.com.secure-login.xyz/verify` |
| **scheme** | how to connect: http or https (secure) | `http` |
| **host** | the server's name | `paypal.com.secure-login.xyz` |
| **TLD** | the last part of the host | `xyz` |
| **domain** | the part just before the TLD — the **real owner** | `secure-login.xyz` |
| **subdomain** | anything to the left of the domain — the owner can write anything here | `paypal.com` |
| **path** | what comes after the host | `/verify` |
| **query** | after `?`: extra parameters | `?id=77` |
| **feature** | one number describing the URL (Lesson 01) | `num_dots = 3` |
| **entropy** | how unpredictable the characters are | `aaaa` → 0, `x7k2` → 2 |

---

## 1. Anatomy of a URL — read the host from the right

![URL anatomy](figs/anatomy.png)

**The trick attackers use:** whoever owns `secure-login.xyz` can create **any** subdomain: `paypal.com.secure-login.xyz`,
`bank.secure-login.xyz`, anything. People read from the left and see "paypal"; the real owner is just before the TLD —
read the host **from the right**. That's the feature `brand_in_subdomain`: a brand name appears in the subdomain but not in
the real domain.

## 2. Features computed by hand (Dani's guide)

| feature | `https://www.google.com/search?q=x` | `http://paypal.com.secure-login.xyz/verify/account` |
|---|---|---|
| url_length (characters) | 33 | 49 |
| host_length | 14 (`www.google.com`) | 27 |
| num_dots | 2 | 3 |
| num_hyphens | 0 | 1 |
| num_subdomains | 1 (www) | 2 (paypal, com) |
| has_https | 1 | 0 |
| suspicious_word_count | 0 | 5 (paypal, secure, login, verify, account) |
| suspicious_tld | 0 (com) | 1 (xyz) |
| entropy | 4.19 | 4.40 |
| brand_in_subdomain | 0 | 1 |

**Why hand-made features and not a neural network on the raw text?** Each number has a meaning a person can read — so the
model's decision can be **explained**: "flagged because a brand name is in the subdomain".

## 3. Look at the data before any model

![feature distributions](figs/distributions.png)

11,430 real URLs, blue = legitimate, orange = phishing. Phishing URLs tend to be longer, with more digits, slashes and
query parameters — but **every** distribution overlaps. No single feature decides; each one moves the odds a little, and
the model combines them (Lessons 12, 13).

## 4. Shannon entropy — how unpredictable is a string?

Attackers' tools create random paths like `/8fa9q2z7x`. Humans write `/signin`. **Entropy** measures this randomness.

**The idea first:** imagine guessing the next character of a string with yes/no questions. In `aaaa` you never need to
ask — it's always "a" → 0 questions. In `abab`, one question ("is it a?") → 1. In a string where all 8 characters are
different, you need 3 questions (8 → 4 → 2 → 1). Entropy = the average number of yes/no questions per character.

$$H = -\sum_{c} p(c)\,\log_2 p(c)\qquad p(c) = \frac{\text{how many times } c \text{ appears}}{\text{length}}$$

(log₂ = "how many times do I multiply 2" — Lesson 00 §7. log₂(½) = −1, log₂(¼) = −2. The minus sign in front makes the
result positive.)

**Step by step for `aaab`:**

```
1. count:         a: 3,  b: 1,  length 4
2. probabilities: p(a) = 3/4 = 0.75      p(b) = 1/4 = 0.25
3. logs (base 2): log₂(0.75) = −0.415    log₂(0.25) = −2
4. multiply:      0.75 × (−0.415) = −0.311     0.25 × (−2) = −0.5
5. add and flip the sign:   −(−0.311 + −0.5) = 0.811
```

![entropy](figs/entropy.gif)

| string | H | why |
|---|---|---|
| `aaaa` | 0 | totally predictable |
| `aaab` | 0.811 | mostly a |
| `abab` | 1.0 | a fair coin: one question per character |
| `abcdefgh` | 3.0 | 8 equally likely → log₂ 8 |
| `/signin` | 2.24 | a human word |
| `/8fa9q2z7x` | 3.32 | machine-made: every character different |

Normal URLs land around 3.8–4.3; random tokens push it up. A weak clue alone, useful together with the others.

## 5. Train/serve skew — the bug with no error message

![train/serve skew](figs/skew.png)

If training counted dots in the **whole URL** and the app counts them in the **host only**, the model gets numbers from a
different distribution and gives **confident, wrong** answers — no crash, no warning. PhishGuard's guards:

1. **one class** (`URLFeatureExtractor`) computes the features for training **and** for the app;
2. the feature **names and order** are saved inside the model file;
3. a **check when loading** (`ModelBundle.load`) — plus `test_same_url_same_features`.

## 6. Common mistakes

| student says | the truth |
|---|---|
| "HTTPS means safe" | Most phishing sites have HTTPS today. One weak clue. |
| "The domain is right after www." | It is just before the TLD — read from the right. |
| "High entropy = phishing" | Raises the odds a little; many real URLs have IDs. |
| "A slightly different calculation in the app is fine" | That's skew. Same code, always. |

## 7. Activities

1. **Who owns it? (10 min).** 8 URLs on the board (`login.microsoft.com`, `microsoft.com.login-check.ru`, `bit.ly/3xYz`,
   `paypal-support.help` …). Students circle the real domain and list the clues.
2. **Entropy by hand (10 min).** `abba`, `banana`, `x7k2`.
3. **Google's phishing quiz** — [phishingquiz.withgoogle.com](https://phishingquiz.withgoogle.com/) as a warm-up.

## 8. Do it yourself

<details><summary>1. Entropy of "abba", step by step.</summary>

a 2, b 2 → p = 0.5 each → log₂ 0.5 = −1 → 0.5 × (−1) + 0.5 × (−1) = −1 → H = **1.0**.
</details>

<details><summary>2. Entropy of "banana".</summary>

a 3, n 2, b 1 of 6 → p = 0.5, 0.333, 0.167 → logs −1, −1.585, −2.585 → products −0.5, −0.528, −0.431 → H = **1.459**.
</details>

<details><summary>3. In `http://amazon.com@203.0.113.55/prize`, where does the browser really go?</summary>

To `203.0.113.55` — everything before `@` is treated as a user name. Features: `has_at_symbol = 1`, `has_ip_host = 1`.
</details>

## 9. In your project

| Project | Where |
|---|---|
| PhishGuard | `phishguard/features/url_parser.py` → `URLParser.parse` · `features/extractor.py` → `shannon_entropy`, `URLFeatureExtractor.extract`, `extract_many` · `models/entities.py` → `FeatureVector.as_list` · exercises ex01–ex04 · theory `25_PhishGuard/01_theory/03_features.md` · notebook `01_url_features.ipynb` |

## 🎬 Watch & explore

* *Information entropy* (Khan Academy) — [search on YouTube](https://www.youtube.com/results?search_query=Khan+Academy+information+entropy)
* *How to spot a phishing link* — [search on YouTube](https://www.youtube.com/results?search_query=how+to+spot+a+phishing+URL+domain)
* Google — [Phishing quiz](https://phishingquiz.withgoogle.com/)
