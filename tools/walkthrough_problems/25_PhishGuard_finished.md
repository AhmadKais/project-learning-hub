Run it from the project folder:

```
pytest -q                     # 26 passed
python train.py --sample      # quick check on the 60-row sample
python train.py               # the real training, about 35 seconds
python evaluate.py            # metrics on the test split
python evaluate.py --url "http://paypal.com.secure-login.xyz/verify"
python run.py                 # the app
```

What the finished project does on the dataset in `data/` (11,430 URLs, half phishing):

- the random forest wins; its threshold is chosen on validation (0.22) so recall stays at 0.95
- on the test split: accuracy 0.81, precision 0.74, recall 0.95, F1 0.83, AUC 0.94
- `train.py` also prints the URLs the model got most wrong - read them, they show its limits
- the app scans a URL, shows the verdict, a risk meter and three reasons, keeps a history with feedback and CSV export, and a statistics tab
