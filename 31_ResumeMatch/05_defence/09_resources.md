# Where to read more

## The textbook — free and online

**Introduction to Information Retrieval**, Manning, Raghavan & Schütze
https://nlp.stanford.edu/IR-book/

The standard reference for this entire project.

- Ch. 6 — term weighting and the vector space model
- Ch. 8 — evaluation (Precision@k, MRR)
- Ch. 11 — the probabilistic model behind BM25

## The original papers

- Salton & Buckley (1988) — *Term-Weighting Approaches in Automatic Text Retrieval*
- Robertson & Zaragoza (2009) — *The Probabilistic Relevance Framework: BM25 and Beyond*
- Porter (1980) — *An Algorithm for Suffix Stripping*

Read the abstract and the formulas. Citing a paper you have actually opened
sounds different from citing one you have not.

## Documentation

- scikit-learn, text feature extraction —
  https://scikit-learn.org/stable/modules/feature_extraction.html
  Read the TF-IDF section. It documents the exact smoothed formula you implement.
- NLTK — https://www.nltk.org/
- pdfplumber — https://github.com/jsvine/pdfplumber
- SciPy sparse — https://docs.scipy.org/doc/scipy/reference/sparse.html

## On bias in hiring systems

- Dastin (2018), Reuters — Amazon scrapped an AI recruiting tool that
  discriminated against women.
- Raghavan et al. (2020) — *Mitigating Bias in Algorithmic Hiring*

Read at least the Reuters piece. It is short, and it is the reason the
explainability and bias chapters of your project exist. Examiners notice when a
student can name a real case.

## Useful to try

Implement TF-IDF with `sklearn.feature_extraction.text.TfidfVectorizer` on your
own collection and compare the weights to yours. They should agree to about six
decimal places. That is your proof the implementation is correct — and it is a
strong thing to show in the defence.
