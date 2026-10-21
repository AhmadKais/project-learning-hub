Run it from the project folder:

```
pytest -q            # 91 passed
python3 train.py     # about 20 seconds on the SMS Spam Collection
python3 evaluate.py  # PASS/FAIL for every target of the proposal
python3 run.py       # the app
```

What the finished project does on the locked test split (776 messages):

- Naive Bayes (threshold 0.86) passes all 8 targets: precision 0.988, recall 0.857, F1 0.918, 1.5 false alarms per 1,000 real messages, under 1 ms per message
- the SVM is the yardstick; it lands just under the precision and recall targets (0.976 and 0.847) and the report says so
- the app checks a message with its reasons, takes "mark as wrong" feedback, retrains in the background, and compares both models with their spread
