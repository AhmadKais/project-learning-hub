Run it from the project folder:

```
pytest -q             # 23 passed
python train.py       # on a GPU about 10-20 minutes; on a CPU many hours
python evaluate.py    # accuracy and a confusion matrix on the FER-2013 test set
python run.py         # the camera window
```

What the finished project does:

- the network has 4,900,551 parameters; with the training data, class weights and augmentation it learns the seven emotions (the target is 65% test accuracy)
- the app finds the biggest face with the Haar detector, classifies it, smooths the label over 5 frames, draws the box and the emotion, and plots the seven probabilities live
- Stop saves the session and shows a summary; Export CSV writes every sample for Excel
- the screenshots use a drawn face (FER-2013 pictures may not be shared) and a short test model, so the percentages there are low - your trained model will be far more confident
