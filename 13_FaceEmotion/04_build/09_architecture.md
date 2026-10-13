# Chapter 9 — The architecture: OOP, MVC and design patterns

The Ministry of Education requires OOP, a design pattern and a database. In this project they are
not "extra points" — they are what lets you test every part separately and replace a component
without breaking the rest.

## 9.1 MVC — three layers

- **Model** — everything the system *knows and does*: entities (`Emotion`, `Session`), computer
  vision (`vision/`), learning (`ml/`), data (`database/`). No file here imports `tkinter`.
- **View** — everything the user *sees*: `views/`. Only Tkinter. No file here imports `cv2`,
  `torch` or `sqlite3`. The View gets ready data and shows it.
- **Controller** — the middleman: `controllers/`. Gets events from the View ("Start was clicked"),
  runs the Model, and updates the View with the result.

📄 **Quick check that your MVC is real**
```bash
grep -r "import tkinter" app/models app/vision app/ml app/database   # must be empty
grep -r "import cv2\|import torch\|sqlite3" app/views                 # must be empty
```

❓ **Possible supervisor question: what is the concrete benefit of this separation in your project?**
Three examples from the code: (1) `tests/` test smoothing, pre-processing and the database without
opening a window and without a camera; (2) `train.py` uses `ml/` without any GUI component;
(3) Tkinter could be replaced by a web UI in the future without touching one line of ML.

## 9.2 Strategy — `FaceDetector`

An abstract class `FaceDetector` with a method `detect(frame)`. Two implementations:
`HaarCascadeDetector` and `DnnFaceDetector`. The Controller holds `self.detector` and does not know
which one it is. Switching at runtime: `self.detector = create_detector("dnn")`.

## 9.3 Factory — `create_detector()`

A function that gets a string ("haar"/"dnn") and returns the matching object. The only place in
the code that knows the concrete class names. Adding a third detector = one line here.

## 9.4 Singleton — `Database` and `EmotionPredictor`

Loading the model to the GPU takes a second and takes memory. If everyone who needs a prediction
creates a new `EmotionPredictor()` — disaster. Singleton guarantees that a second call to
`EmotionPredictor()` returns **the same** object. The implementation: override `__new__` and keep
the instance in `_instance`.

💡 In tests a Singleton is annoying — an instance from one test "leaks" into the next. That is why
`conftest.py` resets `Database._instance = None` before every test. Remember to explain this if
you are asked about the downside.

## 9.5 Repository — `SessionRepository`, `SampleRepository`

All the SQL in one file. The Controller says `sessions.create(session)` and gets an `int`; it does
not know what `INSERT` is. If tomorrow you move to PostgreSQL, you change one file.

## 9.6 The database

Three tables (`app/database/db.py` → `SCHEMA`): `sessions` (one run), `emotion_samples` (one
observation — foreign key to the session), `models` (a record of training versions).

❓ **Possible supervisor question: why `PRAGMA foreign_keys = ON`?**
In SQLite foreign keys are **off** by default, for historical compatibility reasons. Without the
PRAGMA, `ON DELETE CASCADE` simply does not work, and deleting a session leaves orphan samples.
`tests/test_repositories.py::test_delete_cascades_to_samples` checks this.

❓ **Possible supervisor question: why not write every sample to the DB immediately?**
25 disk writes per second slow down the GUI. `SessionController` collects 60 samples in memory and
writes them in one `executemany`. This is called batching and it appears in training too (batch)
for exactly the same reason.

## 9.7 The Python mechanisms behind the patterns

**Abstract class** — `class FaceDetector(ABC)` with `@abstractmethod def detect`. Python refuses to
create an instance of a class that did not implement all the abstract methods: `FaceDetector()` →
`TypeError`. So you cannot "forget" to implement `detect` in a new detector. The method
`detect_largest` is **not** abstract — it is implemented once in the base and works on every
implementation. That is the difference between an interface (what you must do) and shared code
(what you get by inheritance).

**Singleton through `__new__`** — `__new__` is the function that creates the object, **before**
`__init__` initializes it. We override it: if `_instance` already exists — return it. `__init__`
still runs on every call, so `EmotionPredictor` checks `if self._loaded: return`. An examiner will
ask: "what happens on the second `EmotionPredictor()`?" — the answer: the same object, `__init__`
runs but exits immediately, the model is not loaded again.

**`@dataclass`** — automatically generates `__init__`, `__repr__` and `__eq__` from the fields.
`Session` and `EmotionSample` are "entities" — data with a little behavior.
`field(default_factory=list)` instead of `= []` because a list as a default value is shared by all
instances (a classic Python bug).

## 9.8 SQLite — transactions, ACID and indexes

**Transaction** = a group of operations that are all done or not done at all. Our `connection()`:
`commit()` at the end of the block, `rollback()` on error. If `add_many` fails in the middle of 60
samples — none is written; there is no "half batch" in the DB.

**ACID** — the four promises: Atomicity (all or nothing), Consistency (constraints like FK are
kept), Isolation (two transactions do not see each other's half-work), Durability (after commit —
on the disk). SQLite keeps all of them on a single file.

**Index** — a search tree on a column. `idx_samples_session` turns `WHERE session_id=?` from a scan
of the whole table (O(n)) into a tree search (O(log n)). With 100,000 samples that is the difference
between 50 ms and 0.1 ms. The price: slightly slower writes, so we do not index every column.

**Why `timestamp` as ISO text** — `'2026-03-04T10:15:30'` sorts alphabetically exactly like
chronologically (year, month, day, hour — from big to small). `ORDER BY timestamp` works without a
date type, which SQLite does not have anyway.

## 9.9 The full flow — from a click to a row in the DB

📄 **"Start" → frame → DB**
```text
1. the user clicks "Start"                        [View]      MainWindow -> self.on_start()
2. AppController.start_capture()                  [Controller]
3.    CameraService.start()                       [Model/vision]   the camera thread starts
4.    SessionController.start_session()           [Controller]
5.       SessionRepository.create(Session)        [Model/database] INSERT -> id=7
6.    root.after(30, _on_frame)                   [Controller]   the first scheduling
7. _on_frame():
8.    frame = camera.read()                       [Model/vision]
9.    faces = detector.detect_largest(frame)      [Model/vision]   Strategy
10.   x = preprocessor.process(frame, face)       [Model/vision]
11.   probs = predictor.predict(x)                [Model/ml]       GPU
12.   emotion, conf = smoother.update(probs)      [Model/ml]
13.   session_controller.record(...)              [Controller]     to the buffer; every 60 -> add_many
14.   view.video_frame.show(annotated)            [View]
15.   view.emotion_panel.show(emotion, conf)      [View]
16.   root.after(30, _on_frame)                   [Controller]     and on
```

Notice: the View does not appear between lines 8–13, and the Model does not appear in lines 14–15.
That is the separation. The sequence diagram in the book is exactly this list.

## ✅ Check yourself — Chapter 9

1. Another student put `import cv2` in `views/video_frame.py` to convert BGR→RGB. Does this break MVC?
   What is the alternative, and what is its cost?
2. What happens if you delete `@abstractmethod` from `detect` and create `FaceDetector()` directly?
   And what happens when you call `detect_largest` on it?
3. Write what this prints: `a = Database(); b = Database(); print(a is b)`. And what about
   `SessionRepository(a) is SessionRepository(b)`? Why the difference?
4. `add_many` fails at sample 40 of 60 because of a `None` value. How many samples were written to the DB? Why?
5. The query `SELECT * FROM emotion_samples WHERE confidence > 0.9` — do the existing indexes help it?
   What would you add if it becomes frequent?
6. Suggest how to add a third detector (for example MediaPipe) — which files change and which do not.
   This is the real test of the Strategy pattern.

## 📚 Further reading — Chapter 9

- **Refactoring Guru — Design Patterns** (visual explanations, Python examples):
  Strategy https://refactoring.guru/design-patterns/strategy ·
  Singleton https://refactoring.guru/design-patterns/singleton ·
  Factory Method https://refactoring.guru/design-patterns/factory-method
- **Python — abc** (abstract classes): https://docs.python.org/3/library/abc.html
- **Python — dataclasses**: https://docs.python.org/3/library/dataclasses.html
- **Python — sqlite3** (including `row_factory`, transactions): https://docs.python.org/3/library/sqlite3.html
- **SQLite — Foreign Key Support** (why the PRAGMA is needed): https://www.sqlite.org/foreignkeys.html
- **SQLite — Query Planning** (what an index does): https://www.sqlite.org/queryplanner.html
- **pytest — Getting Started** and **fixtures**: https://docs.pytest.org/en/stable/getting-started.html ·
  https://docs.pytest.org/en/stable/how-to/fixtures.html
- **Real Python — MVC in Python** (short explanation with an example): https://realpython.com/lessons/mvc-summary/
