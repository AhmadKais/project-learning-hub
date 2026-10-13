# Step 8 — The defence

## The 60-second summary

Practise this until it is automatic:

> "ResumeMatch ranks CVs against a job description. Each document becomes a
> vector of TF-IDF weights — frequent in this document, rare across the
> collection. I implemented two ranking methods from scratch: cosine similarity,
> which handles document length through geometry, and BM25, which handles it
> with an explicit parameter and also saturates repeated terms. I compared them
> on 50 manually labelled jobs using Precision@k and MRR. Every score comes with
> an exact breakdown of which terms produced it."

## Questions you will be asked

❓ **Why does IDF use a logarithm?**

Without it the weight scales linearly with rarity, so a term appearing once
would dominate everything. The log compresses the range — importance still
rises with rarity, but gently.

❓ **Explain the two `+1`s in the smoothed IDF.**

`ln((1+N)/(1+df)) + 1`. The one in the denominator prevents division by zero for
an unseen term. The one at the end means a term appearing in every document gets
IDF = 1 instead of 0 — weakened, not deleted.

❓ **Why does BM25 use a different IDF?**

It comes from the probabilistic relevance framework, not the vector space model.
The `+1` inside its log keeps it positive for terms in more than half the
documents — otherwise a common word would subtract from the score.

❓ **Why is `cos(a,b) = a·b` in your code?**

Because both vectors are L2-normalised when the matrix is built, so both norms
are 1 and the denominator vanishes. It is not true in general.

❓ **What does `b = 0` do, and who does it favour?**

It removes length normalisation entirely. Long CVs win, because they contain
more of every term. I ran this experiment — the MRR-vs-`b` chart shows the
effect.

❓ **Why sparse matrices?**

500 documents × 20,000 terms dense is 80 MB, 98.5% zeros. Sparse is 1.8 MB.
At 5,000 documents dense would be 800 MB and would not fit in memory.

❓ **What is an inverted index and what does it save?**

A map from term to the documents containing it. Ranking only touches documents
sharing at least one query term; the rest score 0 without being examined.

❓ **How do you know your explanation is correct and not a guess?**

Because the score *is* a sum of per-term products, so each product is one term's
exact contribution. A unit test sums all of them and asserts equality with the
score to 1e-9.

❓ **What is the silent failure your preprocessing contract prevents?**

If the ranking machine stems differently from the indexing machine, the job's
terms are not in the vocabulary, every score becomes 0.000, and no exception is
raised. The program looks fine and every answer is wrong. So the contract is
verified field by field at load time and the system refuses rather than guessing.

❓ **How could a candidate cheat, and how do you detect it?**

By copying the advert's wording. Text similarity rises but actual skills do not,
so high score with low skill coverage flags it.

❓ **Name three ways this system could be biased.**

Terms correlated with gender, ethnicity or age (names, towns, schools, graduation
years) leaking into the vocabulary; non-standard CV formatting extracting badly;
Hebrew stemming being weaker than English, disadvantaging Hebrew CVs. I remove
identifying terms and report the top contributing terms so bias is inspectable.

❓ **Why not BERT or word embeddings?**

They score better but cannot decompose a score into term contributions. This
system ranks people, so an unexplainable score is not acceptable. I documented
them as future work with that trade-off stated.

❓ **What are the limitations?**

Bag of words ignores word order. Synonyms are not recognised without a manual
dictionary. Hebrew stemming is partial. Scanned PDFs have no text layer and
cannot be processed. All are in the book.

## More questions, by area

### Preprocessing

❓ **Why stem at all? What does it cost you?**

So that "developing", "developer" and "developed" collapse to one term instead of
three, each with a third of the evidence. It costs precision: stemming is
rule-based, not dictionary-based, and it over-stems — "university" and "universe"
can collide. I accepted that trade because splitting one concept across three
terms hurts ranking more than the occasional bad merge.

❓ **Why remove stop words rather than let IDF handle them?**

IDF nearly does handle them — a term in every document gets a weight close to the
floor. But it is not zero, and with 20,000 terms those near-zero weights still add
noise to every similarity computation, and they cost memory and time in the index.
Removing them is cheaper and the effect on ranking is nil.

❓ **Why strip identifying terms before indexing rather than after?**

Because after is too late: once a name or a town is in the vocabulary it has an IDF
weight and it influences every score. Names are rare, so they get *high* IDF — they
would be among the most influential terms in the system. `nlp/pii.py` runs before
the vocabulary is built for exactly that reason.

### Vocabulary and IDF

❓ **Why is document frequency computed on a set rather than a count?**

Because a CV saying "Python" eleven times should count once towards how common the
term is across the collection. Using the raw count would let one long CV distort
the IDF of a term for every other document. Nothing crashes if you get this wrong —
the weights are simply wrong.

❓ **What happens to a term in the job advert that is not in the vocabulary?**

It contributes nothing and is skipped. It cannot be added, because the vocabulary
is fixed when the index is built. This is a real limitation — a brand-new
technology name carries no weight until the index is rebuilt — and it is in the
book as such.

❓ **Why is the vocabulary built from the CV collection and not from the job?**

Because the job advert is the query, not part of the collection. IDF measures how
rare a term is among the documents being ranked. Including the query would let it
influence the weights used to score itself.

### The comparison

❓ **Both methods rank the same candidate first. Has the project failed?**

No. Agreement on the easy cases is expected — both are term-overlap methods on the
same vectors. The finding is in the disagreements, and the scatter plot is built to
show them: points off the diagonal are where length or repetition pushed the two
apart, and those are the candidates worth discussing.

❓ **Which method is better?**

That is the research question, and the answer is a number from the 50 labelled
jobs, not an opinion. State the Precision@5 and MRR for both. If the gap is small
relative to the variation across jobs, say so — "they are close, and here is the
spread" is a better answer than a winner invented from a one-point difference.

❓ **How did you choose `k1` and `b`?**

By experiment, on the labelled set, sweeping each and plotting MRR. The defaults
in the literature are `k1` around 1.2–2.0 and `b = 0.75`; I report whether my data
agreed. I did not tune them on the same jobs I then reported the final numbers
from.

### Evaluation

❓ **Why Precision@k and MRR rather than precision and recall?**

Because this is ranking, not classification. There is no verdict to be right or
wrong about — a recruiter looks at the top five, so what matters is how much of
what is in the top five is relevant (P@5) and how far down the first relevant
candidate sits (MRR). Recall over all 500 CVs is not a question anyone asks.

❓ **What is MRR, in one sentence?**

The average of 1/rank of the first relevant result, over all queries — so first
place scores 1.0, third place scores 0.33, and a method that buries the right
candidate is punished sharply.

❓ **Where did your 50 labelled jobs come from, and is that enough?**

I labelled them by hand, which is the honest answer and also the limitation: 50 is
small, and I am a single annotator, so my judgement of "relevant" is not
independently checked. I report the number of queries alongside every metric so the
reader can weigh them accordingly.

### Architecture and data

❓ **Why are indexing and ranking separate programs?**

So that building an index over hundreds of CVs does not freeze the interface, and —
more importantly — so both paths import one `Preprocessor`. There is no second
implementation to drift out of sync, because there is nowhere for one to live.

❓ **What is in the index bundle and why is each part there?**

The vocabulary, the IDF table, the document vectors, the average document length
that BM25 needs, the preprocessing contract, and a version. Together they are the
definition of what passes between the two programs.

❓ **Why is all the SQL in the repository classes?**

So the data layer can be tested against an in-memory database, and so every
parameterised query sits in one file that can be audited. A CV is untrusted input —
it is a file somebody sent you — so no query is ever built by string concatenation.

❓ **Your views are Tkinter. How do you test the logic?**

I do not test through the interface. The views are passive: they raise events and
display what the controller hands them. Every decision lives in
`app_controller.py`, which is a plain object a test can construct, so the whole
suite runs in seconds without opening a window.

## Demo plan (5 minutes)

1. Add a job description → show the extracted skills.
2. Rank → show the table.
3. Click a candidate → **the explanation panel**. Spend time here.
4. Switch method → show a candidate who moved, and their CV length.
5. The scatter plot → points off the diagonal are long/short CVs.
6. Break the contract: edit `preprocess.json`, run `run.py`, show the refusal.

Step 6 takes thirty seconds and shows you understand deployment, not just
algorithms. Do not skip it.

## Two habits

💡 When you do not know: *"I did not test that — my guess is X, and I would
check it by Y."* Honest and specific beats confident and wrong every time.

💡 Have numbers ready: vocabulary size, collection size, P@5 for both methods,
ranking time, sparse vs dense memory. A project defended with numbers sounds
finished. One defended with adjectives does not.
