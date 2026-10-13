# Chapter 17 — The defence

💡 **In short:** forty questions of the kind you will be asked. Answers in chapter 20. If you can do these without looking, you are ready.

## 17.1 How it goes

You present for a few minutes, then they ask questions. They are not trying to catch you out — they are checking that the person who wrote the code is the person in the room. The giveaway is never a wrong answer; it is a vague one.

Three habits worth having:

- **Point at the code.** "That's in `naive_bayes.py`, in `predict_proba`" beats any amount of description.
- **Say what you do not know.** "I didn't measure that, but I'd expect X because Y" is a good answer. Guessing confidently is the worst one.
- **Run the tests.** If a claim is in doubt, `pytest tests/test_naive_bayes.py -v` settles it in four seconds.

## 17.2 The algorithm

1. State Bayes' theorem and explain each term in the spam setting.
2. What is "naive" about Naive Bayes? Is the assumption true?
3. If the assumption is false, why does the classifier work?
4. Why multinomial rather than Bernoulli?
5. What is Laplace smoothing and what breaks without it?
6. Why `+ alpha × |V|` in the denominator and not just `+ alpha`?
7. Why work in logarithms? Show the number that forces it.
8. Why convert back using the difference of the scores rather than each one separately?
9. A word in a new message is not in the vocabulary. What happens, and why is that the right choice?
10. How do you get an explanation out of the model? Where does the number come from?

## 17.3 Features

11. Why can you not feed text straight to the model?
12. Explain TF-IDF. Why both halves?
13. Why rank the vocabulary by document frequency rather than total count?
14. What does L2 normalisation do, and what goes wrong without it?
15. Why keep bigrams but not trigrams?
16. Name the seven handcrafted features and say what each one catches.
17. Why must `caps_ratio` be measured before lower-casing?
18. Why are URLs replaced with a single token instead of keeping the domain?
19. Why are the `From` and `To` headers discarded?
20. Why is the handcrafted feature order stored in the bundle?

## 17.4 Evaluation

21. Why is accuracy not an acceptable metric here? Give the number.
22. Define precision and recall in terms of this project.
23. Which of the two errors is more expensive, and by how much?
24. Why is the threshold not 0.5?
25. Why not maximise F1 instead?
26. Why is the threshold chosen on validation rather than test?
27. Why can the final evaluation only be run once?
28. What is leakage? Give a concrete example from this project.
29. Why five-fold cross-validation rather than one split?
30. Your two models differ by 0.014 in F1 and the spread is 0.031. What do you report?

## 17.5 Architecture and security

31. What is MVP, and why not MVC?
32. Why are training and scanning separate programs?
33. What is in the model bundle, and why is each part there?
34. What exactly would go wrong if feature order differed between training and scanning?
35. Why is the checksum verified before unpickling rather than after?
36. Why store only 500 characters of each message?
37. Why is the threshold stored on every scan row?
38. How does your feedback button avoid being a data-poisoning route?
39. Show where SQL injection is prevented, and the test that proves it.
40. Why does the application never render the message as HTML?

## 17.6 The ones they always ask

**"Show me the part you are most proud of."**

Have an answer ready, and make it `naive_bayes.py` — specifically `predict_proba` and the log-space handling, or `explain` and where the weights come from. Open the file.

**"What would you do differently?"**

Have a real answer. Something like: the English-only corpus is a genuine limitation; handling deliberate misspelling (`fr3e`) was left to future work; the handcrafted features were chosen by reasoning rather than by measuring their individual contribution. Naming a real weakness is a strength here.

**"What did you find hardest?"**

Also have a real answer. The underflow problem is a good one — it is concrete, you can show the test, and explaining why `0.001 ** 300` is exactly `0.0` demonstrates that you understand floating point rather than just having copied a formula.

**"Did anything surprise you?"**

If the SVM beat Naive Bayes, say so and explain why that is a finding rather than a failure. If the two were indistinguishable, say that, and say how you know.

## 17.7 The day before

- `pytest -v` — all green
- `python3 run.py` — opens, classifies a message, shows reasons
- `reports/evaluation.md` — exists, every target has a number
- Bayes' theorem — write it from memory
- The worked example in chapter 4.10 — do it on paper
- Open `naive_bayes.py` and read it once, start to finish
