# Lesson 18 — A URL as numbers: feature engineering and Shannon entropy

> **For:** Dani (PhishGuard stage 1 — the heart of the project) &nbsp;·&nbsp; **Time:** 45 – 60 min
> **Before:** Python strings, Lesson 01 &nbsp;·&nbsp; **After this:** Lessons 12, 13 (the models that use these numbers)

## 🎯 By the end, the student can

1. Take a URL apart (scheme, host, subdomains, domain, TLD, port, path, query) and say who really owns it.
2. Compute the hand-made features of a URL on paper.
3. Compute Shannon entropy for a short string and explain what it measures.
4. Explain train/serve skew and the three guards against it.

---

## 1. Anatomy of a URL

![URL anatomy](figs/anatomy.png)

**The trick attackers use:** the real owner of a host is the part just **before the TLD** (`secure-login.xyz`). Everything
to its left is a subdomain the attacker chose freely — so `paypal.com.secure-login.xyz` belongs to *secure-login.xyz*, not
PayPal. That's the feature `brand_in_subdomain`.

## 2. Features computed by hand (from Dani's guide)

| feature | `https://www.google.com/search?q=x` | `http://paypal.com.secure-login.xyz/verify/account` |
|---|---|---|
| url_length | 33 | 49 |
| host_length | 14 | 27 |
| num_dots | 2 | 3 |
| num_hyphens | 0 | 1 |
| num_subdomains | 1 (www) | 2 (paypal, com) |
| has_https | 1 | 0 |
| suspicious_word_count | 0 | 5 (paypal, secure, login, verify, account) |
| suspicious_tld | 0 | 1 (xyz) |
| entropy | 4.19 | 4.40 |
| brand_in_subdomain | 0 | 1 |

**Why by hand and not a neural network on raw text?** Each number has a meaning a human can read — so the model's
decision can be explained ("this URL has a brand name in a subdomain").

## 3. What the features look like on real data

![feature distributions](figs/distributions.png)

11,430 real URLs. Phishing URLs are longer, have more digits, slashes and query parameters — but every distribution
**overlaps**. No single feature decides; each shifts the odds a little and the model combines them (Lessons 12, 13).
**Always look at the data before training a model** (Dani's stage 2).

## 4. Shannon entropy — how unpredictable is a string?

![entropy](figs/entropy.gif)

$$H=-\sum_{c}p(c)\log_2 p(c)\qquad p(c)=\frac{\text{count}(c)}{\text{length}}$$

| string | H | why |
|---|---|---|
| `aaaa` | 0 | totally predictable |
| `aaab` | 0.811 | ¾ a, ¼ b |
| `abab` | 1.0 | a fair coin: one bit per character |
| `abcdefgh` | 3.0 | 8 equally likely → log₂ 8 |
| `/signin` | 2.24 | a human word |
| `/8fa9q2z7x` | 3.32 | machine-generated: every character different |

By hand for `aaab`: −(¾·log₂ ¾ + ¼·log₂ ¼) = −(¾·(−0.415) + ¼·(−2)) = 0.311 + 0.5 = **0.811**.

**Meaning:** "how many yes/no questions per character to guess the next one". Random tokens from phishing kits push it
up. Weak alone, useful in combination.

## 5. Train/serve skew — the bug with no error message

![train/serve skew](figs/skew.png)

If `train.py` counted dots in the whole URL and the app counted them in the host only, the model would get numbers from a
different distribution and give **confident, wrong** answers — no crash, no warning. Guards in PhishGuard:

1. **one class**, `URLFeatureExtractor`, used by both training and scanning;
2. the **feature names and order** saved inside the model bundle;
3. a **check on load** (`ModelBundle.load`) — plus `test_same_url_same_features`.

## 6. Misconceptions

| Student says | Truth |
|---|---|
| "HTTPS means safe" | Most phishing sites today have HTTPS too. It's one weak feature. |
| "The domain is the part after `www.`" | It's the part before the TLD — read from the right. |
| "High entropy = phishing" | It raises the odds a little. Many legitimate URLs have IDs and hashes. |
| "I can compute features slightly differently in the app, it's close enough" | That's skew. Same code, always. |

## 7. Activities

1. **Who owns it? (10 min).** Write 8 URLs on the board (`login.microsoft.com`, `microsoft.com.login-check.ru`,
   `bit.ly/3xYz`, `paypal-support.help`…). Students circle the real domain. Then list which features fire.
2. **Entropy by hand (10 min).** Compute H for `abba`, `banana`, `x7k2`. (1.0, 1.459, 2.0)
3. **Feature table (15 min).** Do the guide's exercise `http://amazon.com@203.0.113.55/prize/claim` (answer in the guide's
   appendix). What does the `@` do in a browser?

## 8. Check yourself

<details><summary>1. In `http://amazon.com@203.0.113.55/prize`, where does the browser actually go?</summary>

To `203.0.113.55` — everything before `@` is treated as a user name. `has_at_symbol = 1`, `has_ip_host = 1`.
</details>

<details><summary>2. H("aabb")?</summary>

p(a) = p(b) = ½ → H = 1.0.
</details>

<details><summary>3. Why must the feature ORDER be saved with the model?</summary>

The model's weights are per position. If the app builds the vector in another order, weight 3 multiplies the wrong
feature — again without any error.
</details>

## 9. In your project

| Project | Where |
|---|---|
| PhishGuard | `phishguard/features/url_parser.py` → `URLParser.parse` · `features/extractor.py` → `shannon_entropy`, `URLFeatureExtractor.extract`, `extract_many` · `models/entities.py` → `FeatureVector.as_list` · exercises ex01–ex04 · theory `25_PhishGuard/01_theory/03_features.md` · notebook `01_url_features.ipynb` |

## 🎬 Watch & explore

* *Information entropy* (Khan Academy, Information theory) — [search on YouTube](https://www.youtube.com/results?search_query=Khan+Academy+information+entropy)
* *How to spot a phishing link* — [search on YouTube](https://www.youtube.com/results?search_query=how+to+spot+a+phishing+URL+domain)
* Google — [Phishing quiz](https://phishingquiz.withgoogle.com/) (great as a class warm-up)
