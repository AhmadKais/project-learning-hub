Run it from the project folder:

```
pytest -q                     # 26 passed
python train.py --sample      # quick check on the 60-row sample
python train.py               # the real training, about 6 minutes
python evaluate.py            # metrics on the test split
python evaluate.py --url "http://paypal.com.secure-login.xyz/verify"
python run.py                 # the app
```

What the finished project does on the Kaggle file in `data/` (549,346 URLs; 30,000 of each class are used):

- three models are compared: logistic regression and random forest on the 20 features, and the n-gram model on the URL text
- the n-gram model wins; its threshold (0.40) is chosen on validation for recall 0.96
- on the test split (9,000 URLs): precision 0.956, recall 0.957, F1 0.957, AUC 0.99 - both goals of stage 4 are met
- the 20 features alone reach precision 0.75 at the same recall - keep that number for the "alternatives" chapter
- `train.py` also prints the URLs the model got most wrong - read them, they show its limits
- the app scans a URL, shows the verdict, a risk meter and three reasons, keeps a history with feedback and CSV export, and a statistics tab
