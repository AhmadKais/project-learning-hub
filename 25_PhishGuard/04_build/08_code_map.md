# Chapter 7 — A map of the code, and a week-by-week plan

## 7.1 Every file in one sentence, in the order you will touch them

| Stage | File | One sentence |
|---|---|---|
| — | `config.py` | All settings. Complete. Read it once. |
| — | `phishguard/models/entities.py` | The data shapes (`ParsedURL`, `ScanResult`…). Given; one tiny TODO. |
| 1 | `phishguard/features/url_parser.py` | String → the parts of the URL. |
| 1 | `phishguard/features/extractor.py` | Parts → 20 numbers. **The heart.** |
| 2 | `phishguard/ml/dataset.py` | CSV → balanced, split X/y. |
| 3 | `phishguard/ml/trainer.py` | X/y → a fitted model. |
| 3 | `phishguard/ml/bundle.py` | Save/load the model with its features and threshold. |
| 3–4 | `train.py` | Runs the pipeline; writes `reports/`. |
| 4 | `phishguard/ml/evaluator.py` | Metrics, threshold, charts. |
| 5 | `phishguard/ml/predictor.py` | One URL → probability + verdict (loads the bundle once). |
| 5 | `phishguard/ml/explainer.py` | Why: the three strongest features, in words. |
| 5 | `evaluate.py` | Terminal scanning. |
| 6 | `phishguard/database/db.py`, `repositories.py` | SQLite: save and list scans. |
| 6 | `phishguard/controllers/app_controller.py` | Buttons → ML/DB → screens. |
| 6 | `phishguard/views/*.py` | The three Tkinter tabs. |
| 6 | `phishguard/utils/exporter.py` | History → CSV. |
| — | `tests/*.py` | Already written. They tell you when a stage is done. |

## 7.2 How a stage goes — the routine

1. Open `TASKS.md`, read the stage.
2. Open the guide chapter for that stage (Part B).
3. Open the first file. Read the class docstring, then the function docstring — it lists the steps.
4. Delete `raise NotImplementedError`, write the body. Small steps: write two lines, run the test, repeat.
5. Run the stage's test command. Red → read the traceback bottom-up (chapter 1a.9), fix, run again.
6. Green → `git add . && git commit -m "stage N: ..." && git push`. Send Ahmad the `pytest` output.

## 7.3 Week by week (about 8 weeks of 4–6 hours)

| Week | Do | Done when |
|---|---|---|
| 1 | Install (START_HERE). Read guide chapters 1–3. Answer ✅ of ch. 1a, 2, 3. Watch the StatQuest videos (ch. 19). | You can fill the feature table of ch. 3.3 by hand. |
| 2 | Stage 1: parser + extractor. | `test_parser`, `test_extractor` green. |
| 3 | Read ch. 4–5. Stage 2: dataset. Download the Kaggle file. | `test_dataset` green; `feature_means.csv` written and you wrote 3 sentences about it. |
| 4 | Stage 3: logistic model, bundle, `train.py`. | `python train.py --model logistic` prints > 90%. |
| 5 | Stage 4: forest, grid search, evaluator, charts. | `reports/` has 4 files; recall ≥ 0.95. |
| 6 | Read ch. 6. Stage 5: predictor, explainer, `evaluate.py`. | `test_pipeline` green; 20 URLs scanned from the terminal. |
| 7 | Stage 6: database + UI. | `pytest -v` all green; the app works end to end. |
| 8 | Stage 7: experiments table, drift test, UML, start the book. | Every number in the book has a file behind it. |

If a week slips, it slips — but never skip a stage's exit condition to "catch up". A skipped test
comes back as a bug you cannot find.

## 7.4 When you are stuck (in this order)

1. Read the traceback bottom-up. Which file, which line, which error?
2. Print the thing: `print(type(x), x)` right before the failing line.
3. Guide chapter 16a — the troubleshooting table.
4. The docstring of the function — re-read it slowly; the steps are numbered.
5. Search the exact error text (without your file names) on Google — the first StackOverflow answer is usually it.
6. Ask Ahmad — with the traceback and what you already tried. "It doesn't work" gets no help; "line 40 gives KeyError 'entropy', I checked that extract adds it, here is the code" gets help in two minutes.
