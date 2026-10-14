# ResumeMatch — the full checklist

Every function you still have to write in your skeleton: **73**, in the order of `TASKS.md`.
Tick each box when its tests are green. The text after each name is the first line of its TODO —
the full instructions are in the docstring in your code. `HINTS.md` (next to this file) helps with the hard ones.

Generated from your skeleton by `tools/make_checklists.py` — do not edit by hand.

## Stage 1 — load documents (≈2 weeks)

**`resumematch/nlp/loader.py`**

- [ ] `DocumentLoader.load(path)` — 1. check the file exists, else raise ResumeMatchError("File not found: ...") 2. check size: os.path.getsize(path) <= config.MAX_FILE_MB * 1024 * 1024 A huge file is either a mistake or an attack - refuse it with a mes...
- [ ] `DocumentLoader._load_pdf(path)` — returns (text, page_count). with pdfplumber.open(path) as pdf: refuse if len(pdf.pages) > config.MAX_PDF_PAGES text = "\n".join((page.extract_text() or "") for page in pdf.pages) Wrap the whole thing in try/except Exc...
- [ ] `DocumentLoader._load_docx(path)` — doc = docx.Document(path) paragraphs = [p.text for p in doc.paragraphs] ALSO walk doc.tables - many CVs put half their content in a table, and forgetting this silently loses it. Return (text, 0).
- [ ] `DocumentLoader._load_txt(path)` — with open(path, encoding="utf-8", errors="replace") as f: return f.read(), 0
- [ ] `DocumentLoader._clean(text)` — the fixes that matter on real CVs: 1. join hyphen-broken lines: "develo-\nper" -> "developer" 2. replace any run of whitespace (including \xa0) with a single space 3. drop control characters (ord < 32 except \n)
- [ ] `DocumentLoader.load_directory(directory)` — load every supported file in the directory. One bad file must NOT stop the batch: catch ResumeMatchError per file, collect the failures, and return (documents, failures) so the UI can show "loaded 198 of 200; 2 files...

> **Exit condition:** you load 200 documents and print the failures as a list. **Check by eye:** open three extracted texts and read them. If the columns came out interleaved, fix it now — not after you have blamed the ranking for a week.

## Stage 2 — the preprocessing pipeline (≈3 weeks) ★ the gatekeeper

**`resumematch/nlp/pii.py`**

- [ ] `PiiScrubber.scrub(text)` — apply the four patterns above, in this order: URL first (a URL can contain an email-looking string), then EMAIL, then LONG_ID, then PHONE. Replace each match with " " (a space, not an empty string - otherwise two word...
- [ ] `PiiScrubber.find(text)` — return {"emails": n, "phones": n, "ids": n, "urls": n} without changing the text. The loading screen shows this so the user can see that scrubbing actually happened.

**`resumematch/nlp/preprocessor.py`**

- [ ] `TextPreprocessor.__init__(use_stemming, ngram_max)` — self.use_stemming = config.USE_STEMMING if use_stemming is None else use_stemming self.ngram_max = config.NGRAM_MAX if ngram_max is None else ngram_max self.scrubber = PiiScrubber() self.token_re = re.compile(config.T...
- [ ] `TextPreprocessor.process(text)` — the full pipeline. Returns the final list of terms. 1. text = self.scrubber.scrub(text) 2. tokens = self.token_re.findall(text) 3. if config.LOWERCASE: tokens = [t.lower() for t in tokens] 4. tokens = [t for t in toke...  
  ✅ checked by `tests/test_preprocessor.py`
- [ ] `TextPreprocessor._is_stopword(token)` — True if the token is in either stopword list.
- [ ] `TextPreprocessor._stem(token)` — two different languages, two different treatments: if the token is Hebrew (any char in ֐-׿): return self._stem_hebrew(token) else: return self.stemmer.stem(token)
- [ ] `TextPreprocessor._stem_hebrew(token)` — deliberately conservative rule-based stripping: if len(token) > 3 and token[0] in config.HEBREW_PREFIXES: token = token[1:] Do NOT strip more than one prefix and do NOT touch short words - over-stripping merges unrela...
- [ ] `TextPreprocessor._bigrams(tokens)` — return ["machine learning", "learning engineer", ...] i.e. [f"{tokens[i]} {tokens[i+1]}" for i in range(len(tokens) - 1)] Why this matters: "Machine Learning" is ONE skill. Matching "machine" and "learning" separately...
- [ ] `TextPreprocessor.fingerprint()` — the preprocessing contract, written into the index bundle.  
  ✅ checked by `tests/test_preprocessor.py`

> **Exit condition:** all 12 tests green, especially `test_stemming_unifies_variants`.

## Stage 3 — vocabulary and IDF (≈2 weeks)

**`resumematch/nlp/vocabulary.py`**

- [ ] `VocabularyBuilder.__init__(min_df, max_df)` — self.min_df = config.MIN_DF if min_df is None else min_df self.max_df = config.MAX_DF if max_df is None else max_df  
  ✅ checked by `tests/test_bm25.py`, `tests/test_tfidf.py`, `tests/test_vocabulary.py`
- [ ] `VocabularyBuilder.build(processed_docs)` — returns (vocabulary, idf, doc_freq). vocabulary : {term -> column index}, indices 0..V-1 idf : list of floats, idf[column] for each term doc_freq : {term -> in how many documents it appears}  
  ✅ checked by `tests/test_bm25.py`, `tests/test_tfidf.py`, `tests/test_vocabulary.py`
- [ ] `VocabularyBuilder.compute_idf(df, n_docs)` — the SMOOTHED idf, matching scikit-learn: idf = ln( (1 + n_docs) / (1 + df) ) + 1  
  ✅ checked by `tests/test_vocabulary.py`

> **Exit condition:** the formulas match the hand-computed values in the tests.

## Stage 4 — TF-IDF + cosine (≈2 weeks)

**`resumematch/rank/base.py`**

- [ ] `Ranker._normalise(scores)` — shared helper, so both methods normalise identically.

**`resumematch/rank/tfidf.py`**

- [ ] `TfidfRanker.fit(processed_docs, vocabulary, idf)` — build the sparse TF-IDF matrix. 1. store vocabulary, np.array(idf), and [d.doc_id for d in processed_docs] 2. build three parallel lists for the COO constructor: rows, cols, values for row, doc in enumerate(processed_...  
  ✅ checked by `tests/test_tfidf.py`
- [ ] `TfidfRanker._l2_normalise_rows(m)` — divide each row by its own L2 norm. norms = np.sqrt(m.multiply(m).sum(axis=1)).A.ravel() norms[norms == 0] = 1.0 # an empty document must not divide by 0 return sparse.diags(1.0 / norms) @ m After this every row has l...
- [ ] `TfidfRanker._vectorise_job(job_terms)` — put the job description in the SAME vector space. q = np.zeros(len(self.vocabulary)) for term in job_terms: if term in self.vocabulary: q[self.vocabulary[term]] += 1 q = q * self.idf # the collection's idf, NOT a new...  
  ✅ checked by `tests/test_tfidf.py`
- [ ] `TfidfRanker.rank(job_terms, top_k)` — 1. q = self._vectorise_job(job_terms) 2. scores = self.matrix @ q # the whole ranking, one product 3. order = np.argsort(-scores)[:top_k] 4. for each index in order, build a RankResult: score = scores[i] (already 0..1...  
  ✅ checked by `tests/test_tfidf.py`
- [ ] `TfidfRanker.explain(doc_row, q)` — the decomposition that makes the score defensible.

> **Exit condition:** `test_explanation_sums_to_the_score` passes.

## Stage 5 — BM25 (≈2 weeks)

**`resumematch/nlp/vocabulary.py`**

- [ ] `VocabularyBuilder.compute_idf_bm25(df, n_docs)` — BM25 uses a DIFFERENT idf, the probabilistic one: idf = ln( (n_docs - df + 0.5) / (df + 0.5) + 1 )  
  ✅ checked by `tests/test_vocabulary.py`

**`resumematch/rank/bm25.py`**

- [ ] `Bm25Ranker.fit(processed_docs, vocabulary, idf)` — build the INVERTED INDEX, not a matrix. 1. self.doc_refs = [d.doc_id for d in processed_docs] 2. self.doc_len = [d.term_count for d in processed_docs] 3. self.avgdl = sum(self.doc_len) / len(self.doc_len) 4. for row,...  
  ✅ checked by `tests/test_bm25.py`
- [ ] `Bm25Ranker.rank(job_terms, top_k)` — accumulate scores only over documents that can score. scores = defaultdict(float) contributions = defaultdict(list) for term in set(job_terms): if term not in self.inverted: continue idf = self.idf[term] for doc_row,...  
  ✅ checked by `tests/test_bm25.py`
- [ ] `Bm25Ranker._term_score(tf, doc_length, idf)` — the BM25 formula for ONE term in ONE document: tf * (k1 + 1) idf * --------------------------------------- tf + k1 * (1 - b + b * doc_length/avgdl)  
  ✅ checked by `tests/test_bm25.py`

> **Exit condition:** all BM25 tests green, including `test_b_zero_disables_length_normalisation`.

## Stage 6 — skills, explanation and metrics (≈2 weeks)

**`evaluate.py`**

- [ ] `main()` — load the index, get the labelled jobs and their relevant sets for each ranker: result = evaluate(ranker, jobs, relevant, preprocessor) print a comparison table save each result to eval_runs refuse to run if fewer than...

**`resumematch/eval/metrics.py`**

- [ ] `precision_at_k(ranking, relevant, k)` — top = ranking[:k] return len([c for c in top if c in relevant]) / k  
  ✅ checked by `tests/test_metrics.py`
- [ ] `reciprocal_rank(ranking, relevant)` — for position, candidate in enumerate(ranking, start=1): if candidate in relevant: return 1.0 / position return 0.0 First place -> 1.0, second -> 0.5, tenth -> 0.1, none found -> 0.0  
  ✅ checked by `tests/test_metrics.py`
- [ ] `mean_reciprocal_rank(rankings, relevant)` — average reciprocal_rank over every labelled job. rankings: {job_id -> [candidate_ref, ...]} relevant: {job_id -> {candidate_ref, ...}} Only average over jobs that HAVE labels - a job with no labels would count as 0.0...  
  ✅ checked by `tests/test_metrics.py`
- [ ] `evaluate(ranker, jobs, relevant, preprocessor, k_values)` — the full evaluation loop. Returns an EvalResult. for each labelled job: terms = preprocessor.process(job.description) t0 = perf_counter(); results = ranker.rank(terms, top_k=max(k_values)) record the elapsed ms rankin...

**`resumematch/rank/explainer.py`**

- [ ] `RankExplainer.to_lines(result)` — return a list of display strings, e.g. "matched because of: python (0.31), django (0.19), postgresql (0.12)" "skills found: Python, Django, PostgreSQL" "skills missing: Kubernetes" "3 of 4 required skills (75%)" Keep...
- [ ] `RankExplainer.warning_for(result, coverage)` — return a warning string, or "" when nothing is wrong. if result.score > 0.6 and coverage < 0.35: return ("High text similarity but few matching skills - the wording " "may have been copied from the advert. Review manu...

**`resumematch/rank/skills.py`**

- [ ] `SkillExtractor.__init__(preprocessor)` — self.preprocessor = preprocessor self.skills = {} # normalised form -> canonical display name self.by_category = {}
- [ ] `SkillExtractor.load(csv_path)` — read data/skills.csv (columns: skill,category,aliases). For every skill AND every alias: words = [t for t in self.preprocessor.process(name) if " " not in t] normalised = " ".join(words) # "Machine Learning" -> "machi...
- [ ] `SkillExtractor.extract(terms)` — find every skill present in this term list. found = set() for t in terms: # terms already include bigrams if t in self.skills: found.add(self.skills[t]) return sorted(found) Because the preprocessor already produced b...
- [ ] `SkillExtractor.compare(job_skills, resume_skills)` — return (matched, missing). matched = sorted(set(job_skills) & set(resume_skills)) missing = sorted(set(job_skills) - set(resume_skills)) This pair is what the UI shows next to every candidate.
- [ ] `SkillExtractor.coverage(matched, required)` — len(matched) / len(required), or 0.0 if required is empty.

## Stage 7 — the index bundle and two machines (≈1 week)

**`build_index.py`**

- [ ] `main(argv)` — directory = argv[1] if len(argv) > 1 else config.RESUME_DIR controller = AppController() summary = controller.import_resumes(directory) print loaded / failed / flagged counts stats = controller.build_index() print voc...

**`resumematch/rank/bundle.py`**

- [ ] `IndexBundle.save(directory)` — 1. os.makedirs(directory, exist_ok=True) 2. vocabulary.json : json.dump(self.vocabulary) 3. idf.npy : np.save(...) 4. matrix.npz : scipy.sparse.save_npz(...) 5. preprocess.json : the preprocessor's fingerprint() dict...
- [ ] `IndexBundle.load(directory, local_fingerprint)` — verify BEFORE trusting anything: 1. every file in cls.FILES exists, else IndexContractError 2. meta["code_version"] == config.CODE_VERSION, else refuse 3. sha256 of matrix.npz matches meta["sha256"], else "index was m...
- [ ] `IndexBundle._sha256(path)` — h = hashlib.sha256() with open(path, "rb") as f: for chunk in iter(lambda: f.read(65536), b""): h.update(chunk) return h.hexdigest()

> **Exit condition:** editing one value in `preprocess.json` makes `run.py` refuse with a clear message.

## Stage 8 — database (≈1 week)

**`resumematch/database/db.py`**

- [ ] `Database.__new__(path)` — classic singleton. if cls._instance is None: cls._instance = super().__new__(cls) cls._instance._init(path or config.DB_PATH) return cls._instance
- [ ] `Database._init(path)` — self.path = path self.conn = sqlite3.connect(path, check_same_thread=False) self.conn.row_factory = sqlite3.Row # rows behave like dicts self.conn.execute("PRAGMA foreign_keys = ON") # OFF by default! self.conn.execut...
- [ ] `Database.reset()` — close and clear _instance. The tests need this between cases.

**`resumematch/database/repositories.py`**

- [ ] `JobRepository.add(title, description, processed_terms, skills, company)` — INSERT and return the new id. Parameterised query.
- [ ] `JobRepository.get(job_id)` — SELECT one job, or raise ResumeMatchError if missing.
- [ ] `JobRepository.all_labelled()` — SELECT * FROM jobs WHERE is_labelled = 1 - the eval set.
- [ ] `ResumeRepository.add(processed_doc, source_file, file_type, is_synthetic)` — INSERT one resume. candidate_ref must be anonymous: "candidate_0142", never the person's name. Store the PROCESSED text only - the scrubbed version, with no email or phone number in it.
- [ ] `ResumeRepository.set_matrix_row(resume_id, row)` — UPDATE resumes SET matrix_row = ? WHERE id = ?
- [ ] `ResumeRepository.all_active()` — SELECT * FROM resumes WHERE extraction_ok = 1 ORDER BY id.
- [ ] `ResumeRepository.delete_completely(resume_id)` — the right to be forgotten, done properly: 1. read source_file, then delete that file from disk 2. DELETE FROM resumes WHERE id = ? (CASCADE removes rankings+labels) 3. signal the caller that the index must be REBUILT...
- [ ] `RankingRepository.save_many(job_id, method, results, run_id)` — executemany() over the RankResult list. Serialise top_terms with json.dumps([[t.term, t.contribution], ...]). One executemany beats a loop of execute calls by an order of magnitude.
- [ ] `RankingRepository.for_job(job_id, method)` — SELECT ... ORDER BY score DESC - uses idx_rank_lookup.
- [ ] `RankingRepository.method_disagreement(job_id)` — the research query. Returns the candidates the two methods rank most differently, with each one's term_count, so you can show that the disagreement follows document length. The SQL is in the proposal, chapter 11.
- [ ] `LabelRepository.set_label(job_id, resume_id, is_relevant, labeller, before_ranking)` — INSERT OR REPLACE into relevance_labels.
- [ ] `LabelRepository.relevant_for(job_id)` — the set of relevant candidate_refs, before_ranking = 1 only.

## Stage 9 — controller and GUI (≈3 weeks)

**`resumematch/controllers/app_controller.py`**

- [ ] `AppController.__init__()` — wire everything together, once. self.db = Database() self.preprocessor = TextPreprocessor() self.skills = SkillExtractor(self.preprocessor); self.skills.load() self.loader = DocumentLoader() self.job_repo / self.resum...
- [ ] `AppController.import_resumes(directory)` — load a folder, preprocess each document, store it. Return a summary dict for the UI: {"loaded": n, "failed": [(file, reason)], "flagged_short": [refs]} A document with fewer than config.MIN_TERMS_PER_RESUME terms is a...
- [ ] `AppController.build_index()` — 1. refuse if fewer than config.MIN_COLLECTION_SIZE documents - the idf values would be meaningless and every ranking would be noise 2. build vocabulary + idf 3. fit both rankers 4. write each resume's matrix_row back...
- [ ] `AppController.load_index()` — (machine B): IndexBundle.load(INDEX_DIR, self.preprocessor.fingerprint()) Let IndexContractError propagate - the UI shows it as a clear message. Refusing to rank is correct here; ranking with a mismatched pipeline wou...
- [ ] `AppController.rank_job(job_id, method, top_k)` — job = self.job_repo.get(job_id) terms = self.preprocessor.process(job.description) results = self.rankers[method].rank(terms, top_k or config.DEFAULT_TOP_K) attach skills matched/missing to each result if every score...
- [ ] `AppController.compare_methods(job_id)` — run both rankers on the same job and return {"tfidf": [...], "bm25": [...], "disagreement": [...]} The disagreement list is what the comparison screen plots.

## Stage 10 — controller and GUI (≈3 weeks)

**`resumematch/views/candidates_view.py`**

- [ ] `CandidatesView.__init__(parent, controller)` — "choose folder" button, a Treeview of candidates (ref, file type, term count, skills found), and a "build index" button.

**`resumematch/views/comparison_view.py`**

- [ ] `ComparisonView.__init__(parent, controller)` — for a chosen job, show both rankings side by side and a matplotlib scatter plot (x = cosine score, y = BM25 score, one dot per candidate, dot size = term_count).

**`resumematch/views/jobs_view.py`**

- [ ] `JobsView.__init__(parent, controller)` — title entry, company entry, a multi-line Text for the description, a Save button, and a Treeview listing saved jobs. After saving, show the extracted skills so the user can see immediately whether the preprocessing un...

**`resumematch/views/main_window.py`**

- [ ] `MainWindow.__init__(controller)` — super().__init__() self.title("ResumeMatch") self.geometry("1100x700") notebook = ttk.Notebook(self) add JobsView, CandidatesView, RankingView, ComparisonView as tabs add a status bar at the bottom for messages and wa...
- [ ] `MainWindow.show_error(message)` — messagebox.showerror("ResumeMatch", message) Every controller call is wrapped in try/except ResumeMatchError and ends here. A traceback must never reach the user.

**`resumematch/views/ranking_view.py`**

- [ ] `RankingView.__init__(parent, controller)` — job dropdown, method dropdown, "rank" button, and a Treeview: position | candidate | score | skills matched | coverage.

**`run.py`**

- [ ] `main()` — controller = AppController() try: controller.load_index() except IndexContractError as err: print("Cannot start:", err) print("Rebuild the index with: python3 build_index.py") return 1 MainWindow(controller).mainloop(...

## Stage 11 — experiments and the book (≈2 weeks)

**`tune.py`**

- [ ] `main()` — for k1 in (0.5, 1.2, 1.5, 2.0): for b in (0.0, 0.25, 0.5, 0.75, 1.0): build/refit, evaluate, save the row CHECKPOINT: remember the params with the best MRR EARLY STOP: if k1 has not improved for two consecutive values...
