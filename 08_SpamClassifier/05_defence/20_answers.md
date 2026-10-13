# Chapter 20 — Answers

💡 Short answers to chapter 17. Say them in your own words — a memorised answer sounds memorised.

## The algorithm

**1.** `P(spam|words) = P(words|spam) × P(spam) / P(words)`. `P(words|spam)` is countable from the corpus, `P(spam)` is the share of spam in it, and `P(words)` is identical for both classes so it cancels when comparing.

**2.** The assumption that words are independent given the class, which lets the joint probability become a product of single-word probabilities. It is false — `credit` and `card` travel together.

**3.** Classification needs only the correct ordering of the two scores, not correct probabilities. Correlated words distort both classes in roughly the same direction, so the comparison survives. The absolute probabilities are poorly calibrated, which is a real caveat.

**4.** Multinomial models counts, Bernoulli only presence. In spam, repetition is itself evidence — `FREE FREE FREE` differs from one `free` — so counts carry information worth keeping.

**5.** Adding `alpha` (1) to every count so no probability is ever zero. Without it, one word unseen in a class makes that class's entire product zero, and a single unfamiliar word overrides all other evidence.

**6.** Because you added `alpha` once for each of the `|V|` words in the vocabulary, so the denominator must grow by `alpha × |V|` for the probabilities to still sum to 1.

**7.** A product of ~300 probabilities of around 0.001 underflows to exactly `0.0` — a float cannot go below about 1e-308. `log(a×b) = log(a)+log(b)`, so logs turn the product into a sum and keep everything in range.

**8.** The difference of the two scores is a small, well-behaved number; the scores themselves are large and negative. `exp(score)` on its own underflows to 0.0 for both, giving `0.0/0.0`. Subtracting first and exponentiating once stays inside float range.

**9.** It is skipped. It would contribute the same constant to both classes and so cannot change the outcome, and the vector width is fixed at 5,007 so it cannot be added. The limitation is real: a brand-new word carries no weight until the next retrain.

**10.** `log_odds(w) = log P(w|spam) − log P(w|ham)`, read straight off the trained parameters. Positive pushes towards spam. It is not an approximation — that number *is* how the classifier works.

## Features

**11.** A model multiplies and adds; it cannot take a string. Every message must become a fixed-length list of numbers — the same length every time, or the model cannot consume it.

**12.** TF is how often a word appears here; IDF is how rare it is everywhere else. The product is high exactly when a word is characteristic of this message. TF alone would be dominated by common words like `the`.

**13.** A word repeated 500 times in one message has a total count of 500 but a document frequency of 1 — one person shouting, not a useful feature. Document frequency measures how widespread a word really is.

**14.** It scales every vector to length 1 so long and short messages are comparable. Without it, every component of a long message is larger simply because there is more text, and the model learns to detect length instead of content.

**15.** Bigrams catch meaning that single words miss — `click here`. Trigrams multiply the vocabulary for very little further gain, so `config.yaml` caps the range at 2.

**16.** `caps_ratio` (shouting), `exclamation_count` (`!!!`), `message_length`, `digit_ratio` (prices, "100% FREE"), `url_count`, `trigger_word_count` (ten known lure words), `unique_word_ratio` (repetitive filler).

**17.** Lower-casing destroys the signal. Once `"FREE MONEY"` becomes `"free money"`, `caps_ratio` is 0.0 and the information is gone for good.

**18.** Learning that a specific domain is suspicious is learning the corpus — and every link in real incoming spam is one the model has never seen. What generalises is that a link is present at all.

**19.** They identify particular mail servers. Kept, the model learns "mail from this server is spam", which is true of the corpus and useless on anything else. `Subject` stays because it is content.

**20.** Because a mismatch between training order and scanning order raises **no error** — every number is still a float, the model still returns a probability, and every answer is wrong. `features.json` makes the silent failure a loud one.

## Evaluation

**21.** The corpus is ~13% spam, so a model that always answers "ham" scores 87% accuracy while having learned nothing. Any real model must beat 87% before it has done anything at all.

**22.** Precision: of the messages I called spam, how many really were (`TP/(TP+FP)`). Recall: of the spam that existed, how much I caught (`TP/(TP+FN)`).

**23.** A false positive — real mail hidden. Spam reaching the inbox costs a second of annoyance; a hidden message can mean a missed interview or appointment. Not comparable.

**24.** 0.5 assumes the two errors cost the same. They do not. The threshold is raised until precision on spam clears 0.98, protecting legitimate mail, and the resulting recall is reported.

**25.** F1 is symmetric — it weighs both errors equally, which is exactly what is wrong. It would happily trade away legitimate messages to catch a little more spam.

**26.** Because a measurement is only fair if nothing about the model was shaped by that data. Choosing the threshold on test means test participated in a decision, and the number reported from it is then not a measurement.

**27.** Same reason. The moment you look at the result and change something in response, the test set has become a second validation set, and every later number from it is overstated by an unknown amount.

**28.** Information from the test set reaching the model during training. Concretely: fitting the TF-IDF vectorizer on the whole corpus instead of the training split, so IDF weights are computed partly from test documents. Scores come out several points too high and nothing raises an error.

**29.** One split gives one number that moves depending on which messages happened to land where. Five folds give a mean *and* a spread, so you can tell a real difference from noise.

**30.** No significant difference. The gap (0.014) is smaller than the spread (0.031), so the data does not support a claim that either model is better.

## Architecture and security

**31.** Model-View-Presenter: the view is passive, raising events and displaying what it is handed, never touching the model. Unlike MVC, where the view often reads the model directly. It means every decision lives in the presenter and the whole suite runs in seconds without a window.

**32.** So that training does not freeze the UI, and — more importantly — so both paths import the same `FeatureEngineer`. There is no second implementation to drift out of sync because there is nowhere for one to live.

**33.** The vectorizer, both models, `features.json` (handcrafted names in order), `threshold.json` (the threshold and the rule), `metrics.json`, a version and a checksum. Together they are the contract between training and scanning.

**34.** Nothing would raise. Every value is still a float and the model still returns a probability — every answer would simply be wrong. That is why the contract is verified explicitly on load.

**35.** Because unpickling is itself the dangerous operation — `pickle` executes code during load. Checking afterwards reports on something that has already run.

**36.** To limit how much personal mail ends up in an unencrypted file on disk. Full messages would build a complete copy of the user's inbox for no benefit.

**37.** So a past verdict stays explainable after the threshold changes. Without it you know the probability was 0.85 but not whether that counted as spam at the time.

**38.** Feedback accumulates in a queue with `used_in_training = 0` and never triggers training by itself. The user initiates retraining and sees the metric deltas afterwards. An automatic path would be a direct route into the model.

**39.** `repositories.py` — every query is parameterised with `?` placeholders, none built by string concatenation. `test_sql_injection_in_a_body_is_harmless` stores a body of `'); DROP TABLE scans; --` and checks the table still exists.

**40.** Rendering it would execute scripts, fetch remote images and confirm to the sender that the address is live. Tags are stripped as text and links are replaced with a token before anything else touches the message.
