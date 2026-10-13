# FaceEmotion data

The notebooks read **FER-2013** from `fer2013/` in this folder, with exactly the layout your project uses:

```
fer2013/
    train/  angry/ disgust/ fear/ happy/ neutral/ sad/ surprise/
    test/   angry/ disgust/ fear/ happy/ neutral/ sad/ surprise/
```

Download it from Kaggle (https://www.kaggle.com/datasets/msambare/fer2013) as described in your project's
`data/README.md`, unzip it, and copy (or link) the `train` and `test` folders here. Expected counts:
train 28,709 (angry 3,995 · disgust 436 · fear 4,097 · happy 7,215 · neutral 4,965 · sad 4,830 · surprise 3,171),
test 7,178.

The folder is in `.gitignore`: FER-2013 (Goodfellow et al., 2013) was collected from web image search and its
licence does not allow us to redistribute it in this repo.
