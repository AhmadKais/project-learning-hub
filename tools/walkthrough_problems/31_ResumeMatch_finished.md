Run it from the project folder:

```
pytest -q                               # 53 passed
python3 build_index.py data/resumes     # machine A: import the CVs, build the index
python3 import_jobs.py data/jobs.csv    # 10 job adverts with their relevant CVs
python3 evaluate.py                     # P@5, P@10 and MRR for both methods
python3 tune.py                         # the k1 / b / n-gram experiments
python3 run.py                          # machine B: check the index, open the app
```

What the finished project does on the 200 synthetic CVs:

- TF-IDF: P@5 0.90, P@10 0.94, MRR 0.78 - BM25: P@5 0.90, P@10 0.92, MRR 0.78
- MRR is the same in every experiment because a few CVs copied a job advert and come first for every setting - the copied-advert warning flags exactly those CVs
- changing one value in `index/preprocess.json` makes `run.py` refuse to start (the two-machine contract)
- the app ranks candidates for a job with the explanation always visible, and the comparison tab plots TF-IDF against BM25
