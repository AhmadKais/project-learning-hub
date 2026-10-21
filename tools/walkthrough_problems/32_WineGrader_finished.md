Run it from the project folder:

```
pytest -q             # 158 passed (with the real data in data/corpus)
python analyse.py     # statistics and histograms of the data
python train.py       # imports the wines, tunes k-NN, learns the weights - about 30 seconds
python evaluate.py    # the honest comparison table, about 2 minutes
python run.py         # the lab station
```

What the finished project does on the 5,320 unique wines:

- macro-F1: majority guess 0.20, nearest centroid 0.49, k-NN without scaling 0.45, k-NN tuned with nested cross-validation 0.58
- scaling the values matters more than any other choice - compare the unscaled row
- the lab station grades a wine, shows the five most similar wines and what makes each one different, and keeps a history
