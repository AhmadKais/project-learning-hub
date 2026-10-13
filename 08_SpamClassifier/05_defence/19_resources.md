# Chapter 19 — Where to read more

💡 **In short:** four papers worth reading, two corpora, and the documentation you will actually open.

## 19.1 The papers that matter

**Sahami, Dumais, Heckerman & Horvitz (1998) — A Bayesian Approach to Filtering Junk E-Mail.**
The paper that started spam filtering as a machine learning problem. Short, readable, and the structure of your project is recognisably theirs.

**Metsis, Androutsopoulos & Paliouras (2006) — Spam Filtering with Naive Bayes: Which Naive Bayes?**
Compares the variants on the same data. Read it if you are asked why multinomial.

**Joachims (1998) — Text Categorization with Support Vector Machines.**
Why linear SVMs are strong on high-dimensional sparse text. The justification for using one as your yardstick.

**Davis & Goadrich (2006) — The Relationship Between Precision-Recall and ROC Curves.**
Why PR is the right curve on imbalanced data. Cite it when you are asked why you did not lead with ROC.

## 19.2 Textbooks

**Manning, Raghavan & Schütze — Introduction to Information Retrieval**, chapters 13 and 14. Free online. Chapter 13 is Naive Bayes for text, chapter 14 is the vector space model and SVMs. The clearest treatment of TF-IDF you will find.

**Mitchell — Machine Learning**, chapter 6. The classic derivation of Bayesian learning. Older, and worth it for the derivation.

## 19.3 Corpora

| Corpus | Size | Notes |
|---|---|---|
| SMS Spam Collection | 5,574, ~13% spam | Small and clean. Start here. |
| Enron-Spam | ~33,000 | Real email with headers. Closer to the real task. |

Both are English. That is a stated limitation of this project, not an oversight — extending to Hebrew needs a different corpus and a different stop-word list, and it is listed under future work.

## 19.4 Documentation you will open

- **scikit-learn** — `MultinomialNB` (your reference implementation), `LinearSVC`, `CalibratedClassifierCV`, `StratifiedKFold`, `TfidfVectorizer`
- **Python** — `collections.Counter`, `math.log`, `math.exp`, `sqlite3`, `dataclasses`
- **SQLite** — the `PRAGMA foreign_keys` page, which explains why it is off by default
- **pytest** — fixtures, `approx`, `raises`, `importorskip`

## 19.5 Things to be careful with online

Most spam-filter tutorials you will find do three things this project deliberately does not:

- they use `sklearn.naive_bayes` instead of implementing it — fine for a tutorial, fatal for your defence
- they report accuracy — which, as chapter 2 showed, is meaningless at 13% spam
- they use a threshold of 0.5 without discussing it

Read them for orientation, not for method. If a tutorial's approach contradicts this guide, this guide is the one matching your proposal.
