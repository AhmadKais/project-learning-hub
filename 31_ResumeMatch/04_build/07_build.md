# Step 7 — The order to build it in

Eleven stages. Do them in order. Each one makes a test file go green.

| Stage | What | Test |
|---|---|---|
| 1 | Load PDF / DOCX / TXT | check by eye |
| **2** | **Preprocessing pipeline** | `test_preprocessor.py` |
| 3 | Vocabulary + IDF | `test_vocabulary.py` |
| 4 | TF-IDF + cosine | `test_tfidf.py` |
| 5 | BM25 | `test_bm25.py` |
| 6 | Skills, explanation, metrics | `test_metrics.py` |
| 7 | Index bundle, two machines | manual contract demo |
| 8 | Database | — |
| 9–10 | Controller + GUI | full run |
| 11 | Experiments + book | the results chapter |

## Stage 2 is the gatekeeper

Do not move past it until all 12 preprocessing tests pass. Everything after
depends on it being right, and a bug there looks like a ranking bug — you will
waste days.

## How to work each stage

1. Run the test file. Read the **first** failure.
2. Open the skeleton method. Read the `TODO` — it lists the steps.
3. Write it.
4. Run again. Repeat.

```bash
pytest tests/test_preprocessor.py -v        # one file
pytest tests/test_preprocessor.py::test_technical_tokens_survive -v   # one test
```

💡 Commit to git after every green test file. If you break something later,
`git diff` shows you exactly what changed.

## The experiments (stage 11)

This is where a working program becomes a **project**. Sweep the parameters and
record every run:

```python
for k1 in (0.5, 1.2, 1.5, 2.0):
    for b in (0.0, 0.25, 0.5, 0.75, 1.0):
        # rebuild, evaluate, save a row to eval_runs
```

**The `b` sweep is the one that matters.** Plot MRR against `b` from 0.0 to 1.0.
That chart answers your research question with evidence.

Also sweep:
- stemming on/off → how much does it help? how much does the vocabulary shrink?
- unigrams only vs unigrams+bigrams → worth the vocabulary growth?
- `min_df` and `max_df` → how much can you filter before quality drops?

💡 All of this runs from the command line with no GUI. That is only possible
because `rank/` never imports Tkinter — a design decision paying off. Say so.

## Figures for the book

1. Document-length histogram — motivates why `b` exists
2. Vocabulary size before/after filtering
3. **Scatter: cosine score vs BM25 score**, one dot per candidate, size = length
4. Bar chart: P@5 / P@10 / MRR, both methods
5. **Line: MRR against `b`** ← the key figure
6. Heat map: skills × jobs
7. Screenshot: a ranking with the explanation panel open

Figures 3 and 5 are your defence. Figure 3 shows *that* the methods disagree;
figure 5 shows *why*.
