# Chapter 7 — How the project is put together

💡 **In short:** MVP — the view shows things, the presenter decides things, the model layer does the work. Training and scanning are separate programs sharing one feature implementation. Both of those choices exist so the project can be tested.

## 7.1 The layers

```
views/         Tkinter. No logic, no SQL, no model calls.
   ▲
   │ events down, view-models up
presenters/    Every decision worth testing. No tkinter import, ever.
   ▲
   │
ml/ features/ preprocessing/ database/      The model layer.
```

The rule that keeps it honest: **if you ever import `tkinter` into `presenters/`, something has moved into the wrong layer.**

## 7.2 Why MVP and not MVC

In MVC the view often talks to the model directly. In **MVP** the view is *passive*: it raises events and displays what it is handed, and it never reaches past the presenter.

That one difference is why the test suite runs in under a second with no window. Every decision — what colour the banner is, whether to say "borderline", whether the feedback button is enabled — lives in `AppPresenter`, which is a plain Python object you can construct in a test.

If the view decided any of that, testing it would mean driving a GUI, and in practice that means it would not get tested at all.

📄 **The rule, in code**
```python
# presenters/app_presenter.py  - correct
@staticmethod
def format_verdict(verdict):
    return {
        "label":  "SPAM" if verdict.is_spam else "LEGITIMATE",
        "colour": "red" if verdict.is_spam else "green",
        "confidence": ("borderline" if verdict.confidence < 0.3
                       else "moderate" if verdict.confidence < 0.7
                       else "high"),
    }

# views/check_view.py  - also correct: it only reads the dict
def display_verdict(self, formatted):
    self._banner.config(text=formatted["label"], bg=formatted["colour"])
```

The view asks no questions. It is handed the answers.

## 7.3 Training and scanning are separate programs

`train.py` and `evaluate.py` run from the command line and produce a bundle. `run.py` loads a bundle and never trains.

Two reasons:

1. **The UI must not freeze.** Training takes minutes; a frozen window looks broken and the operating system will say so.
2. **It forces one feature implementation.** Both paths import the same `FeatureEngineer`. There is no second copy to drift out of sync, because there is nowhere for one to live.

That second reason is the important one, and it is a structural answer rather than a disciplinary one. "We were careful" is not an answer; "there is only one implementation and both paths import it" is.

## 7.4 The bundle: the contract

There is no network in this project, so the bundle *is* its protocol — the exact definition of what passes between two pieces of code written weeks apart.

```
models/2026-03-11-a/
    vectorizer.pkl     vocabulary and IDF weights
    nb_model.pkl       log priors and log likelihoods
    svm_model.pkl      the calibrated SVM
    features.json      handcrafted names IN ORDER, plus dimensions
    threshold.json     the chosen threshold and the rule behind it
    metrics.json       both models' scores, mean and std
    version.txt        version id and timestamp
    checksum.txt       SHA-256 of all of the above
```

`features.json` prevents the project's worst failure mode. If the scanner computes features in a different order from the trainer, **nothing raises** — every number is still a float, the model still returns a probability, and every answer is wrong. The load path compares the stored list against `config.HANDCRAFTED_FEATURES` and refuses on any mismatch.

`checksum.txt` is a security control, not housekeeping. `pickle` executes code when it loads, so a swapped file is a way to run someone else's code on your machine. The checksum is verified **before** anything is unpickled — order matters, and getting it backwards defeats the whole measure.

❓ **Why verify the checksum before unpickling rather than after?**

Because unpickling is itself the dangerous operation — `pickle` can execute arbitrary code during load. Checking afterwards would mean the malicious payload has already run and the check reports on something that has already happened.

## 7.5 The five tables

| Table | Holds |
|---|---|
| `scans` | one classification: text excerpt, probability, threshold, verdict, reasons |
| `feedback` | verdicts the user marked wrong, waiting for the next retrain |
| `training_runs` | one row per training run — how each model version came to exist |
| `metrics` | per model, per metric, mean and std |
| `vocabulary_stats` | the most discriminative words of each run |

Three decisions worth defending:

- **Only 500 characters of the body are stored.** Keeping whole messages would build a complete copy of someone's mail in an unencrypted file on disk, for no benefit.
- **The threshold is stored per scan**, so past verdicts stay explainable after it changes (section 6.5).
- **`vocabulary_stats` is not needed for classification at all.** It exists so you can look at what the model considers decisive — the fastest way to notice it has learned a corpus artefact instead of learning spam.

## 7.6 Repositories

Every SQL statement in the project lives in `repositories.py`. None appears in a presenter and certainly none in a view.

This makes the data layer testable against `:memory:` — the tests create a real database, run the real queries, and throw it away, in milliseconds.

It also puts every parameterised query in one auditable file. The body of an email is untrusted input, so this matters:

📄 **Parameterised, always**
```python
# correct
self._conn.execute("INSERT INTO scans (body_excerpt) VALUES (?)", (excerpt,))

# never
self._conn.execute(f"INSERT INTO scans (body_excerpt) VALUES ('{excerpt}')")
```

`test_sql_injection_in_a_body_is_harmless` stores a message whose text is `'); DROP TABLE scans; --` and then checks the table is still there.

## 7.7 The design patterns

| Pattern | Where | What it buys |
|---|---|---|
| Strategy | NB and SVM behind one interface | swap models, no calling code changes |
| Repository | the three repository classes | all SQL in one place, testable |
| MVP | passive views, testable presenter | the suite runs without a window |
| Facade | `SpamFilter` | one call instead of four |
| Builder | `ModelBundle.save` | a half-written bundle never looks loadable |
| Value Object | `Verdict`, `Reason` | frozen, so history cannot be rewritten |
| Dependency Injection | repositories passed into the presenter | tests inject an in-memory database |

Be able to point at the file for each. "We used Strategy" means nothing on its own; "`NaiveBayesClassifier` and `SVMClassifier` both expose `predict_proba`, so `SpamFilter` holds either without knowing which" is an answer.

## 7.8 Threads

Retraining runs on a worker thread so the window stays responsive. One rule:

💡 **Tk is not thread-safe.** Never touch a widget from the worker thread. Post results back with `self.after(0, callback)` and let the main thread do the drawing. Breaking this produces crashes that appear at random and are extremely hard to reproduce.
