# Chapter 3 — A URL as numbers: feature engineering

💡 **In short:** a model reads numbers, not text. We turn every URL into 20 numbers (length, dots, `@`, HTTPS, suspicious words…). Choosing those numbers well is the main skill of this project. The same code must compute them in training and in the app.


## 3.1 The anatomy of a URL

📄 **The pieces**
```text
https://www.mail.paypal.com/signin?country=il#top
^^^^^   ^^^^^^^^^^^^^^^^^^^        ^^^^^^ ^^^^^^^^^^ ^^^
scheme  host                       path   query      fragment

host = www.mail.paypal.com
       ^^^ ^^^^ ^^^^^^ ^^^
       subdomains  domain tld       (read from the RIGHT: tld, then domain, then subdomains)
```

The part that matters for trust is the **registered domain** = domain + TLD, read from the right:
`paypal.com`. Everything to the left of it is a subdomain that the *owner of paypal.com* controls.
Now the attacker's trick:

📄 **Reading a phishing host from the right**
```text
paypal.com.secure-login.xyz
                        ^^^   tld = xyz
           ^^^^^^^^^^^^       domain = secure-login       <- the real owner
^^^^^^ ^^^                    subdomains = paypal, com    <- just names the attacker chose
```

Humans read from the left and see "paypal.com". Browsers (and our parser) read from the right and
see `secure-login.xyz`. Nearly every phishing trick is a way to make the left look trustworthy:

| Trick | Example | Feature that catches it |
|---|---|---|
| Brand in the subdomain | `paypal.com.secure-login.xyz` | `brand_in_subdomain`, `num_subdomains` |
| `@` — the browser ignores everything before it | `http://amazon.com@203.0.113.55/` | `has_at_symbol` |
| IP address instead of a name | `http://192.168.4.77/login` | `has_ip_host` |
| Look-alike letters | `paypa1.com`, `g00gle.com` | `num_digits`, `digit_ratio` |
| Cheap endings | `.xyz .tk .ml .top .click` | `suspicious_tld` |
| Urgency words | `verify`, `suspended`, `urgent` | `suspicious_word_count` |
| Hyphen chains | `secure-account-update-now.com` | `num_hyphens` |
| Hiding behind a shortener | `bit.ly/3xk9Qz2` | `is_shortener` |
| No HTTPS | `http://…` | `has_https` |
| Random junk | `/8fa9q2z7` | `entropy` |

## 3.2 What a feature is, and why we compute them by hand

A model cannot read text. It reads numbers. A **feature** is one number that describes one property
of the URL. **Feature engineering** is choosing which properties, and writing the code that computes
them. In text classification (spam, fake news) the features are "which words appear" — thousands of
them, chosen automatically. Here we choose ~20 by thinking about *how attackers work*. That thinking is
the algorithmic content of your project, and it is what the examiner will probe.

## 3.3 Two URLs computed by hand

📄 **Feature vectors**
```text
feature                 https://www.google.com/search?q=x    http://paypal.com.secure-login.xyz/verify/account
url_length                        33                               49
host_length                       14   (www.google.com)            27   (paypal.com.secure-login.xyz)
path_length                        7   (/search)                   15   (/verify/account)
num_dots                           2                                3
num_hyphens                        0                                1
num_underscores                    0                                0
num_slashes (after ://)            1                                2
num_digits                         0                                0
digit_ratio                        0.000                            0.000
num_subdomains                     1   (www)                        2   (paypal, com)
num_query_params                   1   (q=x)                        0
has_ip_host                        0                                0
has_at_symbol                      0                                0
has_https                          1                                0
has_port                           0                                0
suspicious_word_count              0                                4   (secure, login, verify, account)
suspicious_tld                     0   (com)                        1   (xyz)
is_shortener                       0                                0
entropy                            4.19                             4.41
brand_in_subdomain                 0                                1   ("paypal" in subdomains, not in domain)
```

Do this exercise yourself for `http://amazon.com@203.0.113.55/prize/claim` before looking at the
answer (appendix). If you can fill the table by hand, you understand the extractor.

## 3.4 The one rule that makes or breaks the project

The **same code** must compute the features in training and at scan time. If `train.py` computed
`num_dots` on the whole URL and the app computed it on the host only, the model would receive numbers
in a range it never saw — and give confident, wrong answers with no error message. This is
**train/serve skew**. Our defense: one class, `URLFeatureExtractor`, used by both; the feature
*names and order* saved inside the model file; and a check on load that they match
(`ModelBundle.load`). The test `test_same_url_same_features` pins it.

## 3.5 Entropy — measuring "randomness"

Attackers generate paths like `/8fa9q2z7` automatically. Humans write `/signin`. **Shannon entropy**
measures how unpredictable the characters are:

📄 **Entropy**
```text
H = - sum over characters c of  p(c) * log2(p(c))      p(c) = count(c) / length

"aaaa"      p(a)=1                     H = 0                     (totally predictable)
"aaab"      p(a)=3/4, p(b)=1/4         H = 0.811
"abab"      p(a)=1/2, p(b)=1/2         H = 1.0
"abcdefgh"  8 different, each 1/8      H = 3.0                   (maximum for 8 characters)
```

A URL made of English words sits around 3.8–4.3; random tokens push it higher. It is a weak feature
alone but a useful one in combination.

## 3.6 Looking at the features before any model

Before training anything, compute the average of every feature per class
(`DatasetLoader.feature_table` → `groupby("label").mean()`). You will see things like:

📄 **What you should find (roughly)**
```text
feature                 good     bad
has_https               0.85     0.30
num_dots                2.1      3.4
suspicious_word_count   0.2      1.6
num_subdomains          1.1      2.0
brand_in_subdomain      0.00     0.12
url_length              45       62
```

This table goes in your book *before* the model results: it shows the features carry signal, and it
lets you explain the model's later choices ("it learned what the table already shows").

## ✅ Check yourself — Chapter 3

1. Split `http://secure-bankhapoalim.co.il.account-update.top/login?id=7731` into scheme, subdomains,
   domain, TLD, path, query. Who owns this site?
2. Fill the 20-feature table for `http://amazon.com@203.0.113.55/prize/claim`.
3. Compute the entropy of `"aabb"` and of `"abcd"`.
4. Why does the extractor compute `has_https` from the *scheme* and not from searching "https" inside
   the URL string? Give a URL where the difference matters.
5. Suggest one new feature that would catch `paypa1.com`-style look-alikes, and say how you would compute it.
6. Explain train/serve skew to a friend in three sentences, using `num_dots` as the example.

## 📚 Further reading — Chapter 3

- **RFC 3986 — URI syntax** (section 3 only): https://www.rfc-editor.org/rfc/rfc3986#section-3
- **Python docs — urllib.parse**: https://docs.python.org/3/library/urllib.parse.html
- **Sahingoz et al. (2019), Machine learning based phishing detection from URLs** — table 2 lists 40
  URL features; compare with ours: https://doi.org/10.1016/j.eswa.2018.09.029
- **PhishTank** — live verified phishing URLs for your drift test: https://phishtank.org/
- **APWG Phishing Trends Report** (numbers for the introduction): https://apwg.org/trendsreports/
