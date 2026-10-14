# FaceEmotion — the full checklist

Every function you still have to write in your skeleton: **97**, in the order of `TASKS.md`.
Tick each box when its tests are green. The text after each name is the first line of its TODO —
the full instructions are in the docstring in your code. `HINTS.md` (next to this file) helps with the hard ones.

Generated from your skeleton by `tools/make_checklists.py` — do not edit by hand.

## Stage 1 — Environment and camera

**`app/vision/camera.py`**

- [ ] `CameraService.start()` — 1. self._capture = cv2.VideoCapture(self.camera_index) 2. raise RuntimeError if not self._capture.isOpened() 3. set CAP_PROP_FRAME_WIDTH / CAP_PROP_FRAME_HEIGHT from config 4. self._running = True 5. start self._threa...
- [ ] `CameraService._reader_loop()` — while self._running: read a frame; on success store it under self._lock into self._latest_frame. Never store a failed read.
- [ ] `CameraService.read()` — return a COPY of the latest frame (or None if there is none yet). Return a copy - the reader thread overwrites the buffer while the GUI is still drawing on it.
- [ ] `CameraService.stop()` — set _running False, join the thread (with a timeout), release the capture and drop the buffered frame.

**`train.py`**

- [ ] `print_device_banner()` — print which device will be used, and for CUDA also torch.cuda.get_device_name(0) and the total memory. Print a loud warning when falling back to the CPU - a silent CPU run that takes six hours is a waste of an evening.

> **Exit condition:** a small script of your own opens `CameraService`, reads a frame and shows it with `cv2.imshow` — the video flows without freezing.

## Stage 2 — Face detection

**`app/models/detection.py`**

- [ ] `FaceDetection.area` — return the area of the box (used to pick the main face).  
  ✅ checked by `tests/test_preprocessor.py`
- [ ] `FaceDetection.with_margin(margin, frame_shape)` — return a NEW FaceDetection enlarged by `margin` (0.10 = 10%) on every side, clipped so it never leaves the frame.  
  ✅ checked by `tests/test_preprocessor.py`
- [ ] `FaceDetection.crop(frame)` — return the sub-image frame[y:y+h, x:x+w].  
  ✅ checked by `tests/test_preprocessor.py`

**`app/vision/face_detector.py`**

- [ ] `FaceDetector.detect_largest(frame)` — call self.detect() and return a list with the single biggest face (by FaceDetection.area), or an empty list if none was found. The GUI uses this in single-person mode.
- [ ] `create_detector(name)` — Simple Factory: turn the string in config.DETECTOR into an object.

**`app/vision/haar_detector.py`**

- [ ] `HaarCascadeDetector.__init__(cascade_path)` — 1. path = cascade_path or config.HAAR_CASCADE_PATH 2. self._cascade = cv2.CascadeClassifier(path) 3. raise RuntimeError if self._cascade.empty() - a wrong path does NOT raise by itself, it just silently detects nothing.
- [ ] `HaarCascadeDetector.detect(frame)` — 1. gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) 2. cv2.equalizeHist(gray) - helps a lot in poor lighting 3. boxes = self._cascade.detectMultiScale( gray, scaleFactor=config.HAAR_SCALE_FACTOR, minNeighbors=config.HAA...

**`app/vision/preprocessor.py`**

- [ ] `FacePreprocessor.crop_face(frame, detection)` — cut the face out of the frame: box = detection.with_margin(self.margin, frame.shape[:2]) # (height, width) return frame[box.y : box.y + box.h, box.x : box.x + box.w]

> **Exit condition:** a green box around your face in real time (in `cv2.imshow`, before Tkinter); `detect()` is timed and printed — under 30 ms per frame. `pytest tests/test_preprocessor.py -k "area or margin or crop"` green.

## Stage 3 — Data and model

**`app/ml/dataset.py`**

- [ ] `EqualizeHist.__call__(image)` — three lines: array = np.array(image) # PIL 'L' image -> uint8 (H, W) array = cv2.equalizeHist(array) return Image.fromarray(array) # back to PIL for the next transforms
- [ ] `build_train_transform()` — augmentation for the training set only. Grayscale(num_output_channels=1) EqualizeHist() # same lighting correction as the real-time path RandomHorizontalFlip(p=0.5) RandomRotation(10) RandomResizedCrop(config.IMAGE_SI...
- [ ] `build_eval_transform()` — NO augmentation, and exactly the steps of FacePreprocessor.to_model_input(), in the same order: Grayscale(num_output_channels=1) Resize((config.IMAGE_SIZE, config.IMAGE_SIZE)) EqualizeHist() ToTensor() Normalize([conf...  
  ✅ checked by `tests/test_preprocessor.py`
- [ ] `FER2013Dataset.__init__(root, transform)` — three steps: 1. self.folder = torchvision.datasets.ImageFolder(root, transform=transform)
- [ ] `FER2013Dataset.__len__()` — one line - return len(self.folder).
- [ ] `FER2013Dataset.__getitem__(index)` — three lines: image, folder_label = self.folder[index] return image, self.remap[folder_label]
- [ ] `FER2013Dataset.class_counts()` — count how many images each of the 7 emotions has: counts = np.zeros(NUM_CLASSES, dtype=np.int64) for _, folder_label in self.folder.samples: counts[self.remap[folder_label]] += 1 return counts
- [ ] `build_dataloaders(batch_size)` — return (train_loader, val_loader, test_loader).

**`app/ml/network.py`**

- [ ] `ResidualBlock.__init__(in_channels, out_channels, stride)` — create six things, in this order: self.conv1 = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1, bias=False) self.bn1 = nn.BatchNorm2d(out_channels) self.conv2 = nn.Conv2d(out_channels, out...  
  ✅ checked by `tests/test_network.py`
- [ ] `ResidualBlock.forward(x)` — five lines, in this exact order: identity = self.shortcut(x) # save the input FIRST out = self.relu(self.bn1(self.conv1(x))) out = self.bn2(self.conv2(out)) # no ReLU here yet! out = out + identity # the skip connecti...  
  ✅ checked by `tests/test_network.py`
- [ ] `EmotionNet.__init__(num_classes, dropout)` — build three parts. Follow the diagram in the module docstring above; every number there is already decided for you.  
  ✅ checked by `tests/test_network.py`
- [ ] `EmotionNet.forward(x)` — just push x through the parts, in order: x = self.stem(x) x = self.block1(x) x = self.block2(x) x = self.block3(x) x = self.block4(x) return self.head(x)  
  ✅ checked by `tests/test_network.py`

**`app/vision/preprocessor.py`**

- [ ] `FacePreprocessor.to_model_input(face_bgr)` — the full pre-processing chain, in this order: 1. cv2.cvtColor -> grayscale 2. cv2.resize -> (image_size, image_size), interpolation=cv2.INTER_AREA 3. cv2.equalizeHist -> flattens the lighting (the training transforms...  
  ✅ checked by `tests/test_preprocessor.py`
- [ ] `FacePreprocessor.process(frame, detection)` — crop_face() followed by to_model_input().

> **Exit condition:** `pytest tests/test_network.py tests/test_preprocessor.py -v` all green. `EmotionNet().count_parameters()` prints 4,900,551. A short `python train.py --epochs 2` starts (it may crash at the end — no Trainer yet).

## Stage 4 — Full training on the GPU, and evaluation

**`app/ml/dataset.py`**

- [ ] `compute_class_weights(counts)` — FER-2013 is very unbalanced (436 disgust training images vs 7,215 happy). Give rare classes a bigger weight in the loss: weight_i = total / (num_classes * count_i)

**`app/ml/evaluator.py`**

- [ ] `ModelEvaluator.evaluate()` — model.eval(); collect y_true and y_pred over the whole test set, then use sklearn.metrics to build: - accuracy - classification_report(..., target_names=[e.name for e in Emotion], output_dict=True) -> precision/recall...
- [ ] `ModelEvaluator.plot_confusion_matrix(path, normalize)` — matplotlib heat-map of the confusion matrix with the seven emotion names on both axes. Normalise by row so each row sums to 1 - that shows which emotions the model mixes up (fear/surprise and sad/neutral are the class...
- [ ] `ModelEvaluator.save_report(path)` — write the metrics dict to a JSON file under reports/.

**`app/ml/trainer.py`**

- [ ] `ModelTrainer.__init__(model, train_loader, val_loader, class_weights)` — create self.criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=config.LABEL_SMOOTHING) self.optimizer = torch.optim.AdamW(model.parameters(), lr=config.LEARNING_RATE, weight_decay=config.WEIGHT_DECA...
- [ ] `ModelTrainer.train_one_epoch()` — one pass over train_loader.
- [ ] `ModelTrainer.validate()` — same loop over val_loader but with self.model.eval(), no optimiser step and no gradients. Returns {"loss": ..., "acc": ...}.
- [ ] `ModelTrainer.fit(epochs)` — the full run.
- [ ] `ModelTrainer.save_checkpoint(path, epoch, val_acc)` — torch.save a dict - not just the weights: {"model_state": self.model.state_dict(), "optimizer_state": ..., "epoch": ..., "val_acc": ..., "config": {"image_size": ..., "mean": ..., "std": ...}} Storing the pre-processi...
- [ ] `ModelTrainer.plot_history(path)` — two matplotlib subplots - loss and accuracy per epoch.

**`evaluate.py`**

- [ ] `main()` — _, _, test_loader = build_dataloaders(args.batch_size) model = EmotionNet(); load the checkpoint's "model_state"; .to(DEVICE).eval() evaluator = ModelEvaluator(model, test_loader) metrics = evaluator.evaluate() evalua...

**`train.py`**

- [ ] `main()` — wire the pieces together train_loader, val_loader, _ = build_dataloaders(args.batch_size) weights = compute_class_weights(train_loader.dataset.class_counts()) model = EmotionNet().to(config.DEVICE) print(f"parameters:...

> **Exit condition:** `python train.py` finishes 50 epochs (or stops early) in under 20 minutes on the GPU; `models/emotion_net_best.pt` exists; `python evaluate.py` prints **accuracy ≥ 65%** on the test set; `reports/confusion_matrix.png`, `training_curves.png`, `metrics.json` exist. Keep a table of **every** training run (epochs, LR, augmentation, accuracy) — it is the results chapter of your book.

## Stage 5 — Real-time integration

**`app/controllers/app_controller.py`**

- [ ] `AppController.__init__(root)` — create the model-side objects self.camera = CameraService() self.detector = create_detector(config.DETECTOR) self.preprocessor = FacePreprocessor() self.predictor = EmotionPredictor() self.smoother = TemporalSmoother(...
- [ ] `AppController.start()` — show the window and, if a model is missing, warn the user.
- [ ] `AppController.start_capture()` — start the camera, open a new session through SessionController, reset the FPS counter and schedule the first _on_frame. Guard against a double click while already running.
- [ ] `AppController._on_frame()` — one iteration of the cycle documented at the top.
- [ ] `AppController.stop_capture()` — cancel the pending after() job, stop the camera, close the session (which flushes the remaining samples) and show the summary.
- [ ] `AppController.on_close()` — stop everything cleanly, then root.destroy(). Bind it with root.protocol("WM_DELETE_WINDOW", self.on_close).

**`app/ml/predictor.py`**

- [ ] `EmotionPredictor.load_model()` — 1. if the checkpoint file does not exist: print a clear message ("train the model first: python train.py"), leave is_ready False and return - the app must still open and show the camera. 2. checkpoint = torch.load(sel...
- [ ] `EmotionPredictor.predict(model_input)` — one face -> (emotion, confidence, probabilities).

**`app/ml/smoothing.py`**

- [ ] `TemporalSmoother.update(probabilities)` — append the vector, average the whole window along axis 0, and return (Emotion(argmax), float(max)) of the averaged vector.  
  ✅ checked by `tests/test_smoothing.py`
- [ ] `TemporalSmoother.reset()` — clear the window (called when the face is lost).  
  ✅ checked by `tests/test_smoothing.py`
- [ ] `TemporalSmoother.current` — the smoothed emotion right now, or None when empty.  
  ✅ checked by `tests/test_smoothing.py`

**`app/utils/fps.py`**

- [ ] `FpsCounter.tick()` — append time.perf_counter().
- [ ] `FpsCounter.value` — with fewer than 2 timestamps return 0.0, otherwise (len - 1) / (last - first).
- [ ] `FpsCounter.reset()` — clear the deque.

**`app/vision/annotator.py`**

- [ ] `FrameAnnotator.draw_detection(frame, detection, emotion, confidence)` — 1. work on a copy of the frame, never on the original 2. cv2.rectangle in emotion.color_bgr, thickness 2 3. a filled bar just above the box as a background for the text 4. cv2.putText with f"{emotion.name} {confidence...
- [ ] `FrameAnnotator.draw_fps(frame, fps)` — small "FPS: 24.3" caption in the top-left corner.
- [ ] `FrameAnnotator.draw_no_face(frame)` — caption "No face detected" when the list is empty.

> **Exit condition:** `pytest tests/test_smoothing.py -v` green. The camera shows a coloured box + emotion name + percentage, FPS ≥ 15 (target 25 with the GPU), and the label does not flicker when your expression is steady.

## Stage 6 — Database, UI and export

**`app/controllers/app_controller.py`**

- [ ] `AppController.export_session()` — ask SessionController to write the CSV and tell the user where the file was saved.

**`app/controllers/session_controller.py`**

- [ ] `SessionController.start_session(detector_name, model_name)` — build a Session(started_at=datetime.now(), ...), persist it with self.sessions.create(), store the returned id on the object, keep it in self.current and return it.
- [ ] `SessionController.record(emotion, confidence, box, probabilities)` — append an EmotionSample to the buffer, but skip samples whose confidence is below config.MIN_CONFIDENCE_TO_STORE - they are noise and would distort the statistics. Flush when len(buffer) >= FLUSH_EVERY.
- [ ] `SessionController.flush()` — add_many() the buffer, then clear it. Do nothing if empty.
- [ ] `SessionController.end_session(frames_processed, average_fps)` — flush(), call sessions.finish(...), fill ended_at / frames_processed / average_fps on self.current, reload its samples so the summary can be computed, clear self.current and return the finished object.
- [ ] `SessionController.export_csv(session_id)` — delegate to SessionExporter and return the file path.

**`app/database/db.py`**

- [ ] `Database.get_connection()` — conn = sqlite3.connect(self.db_path) conn.row_factory = sqlite3.Row # rows behave like dicts conn.execute("PRAGMA foreign_keys = ON") # off by default in SQLite! return conn
- [ ] `Database.connection()` — context manager that commits on success, rolls back on any exception and always closes the connection: conn = self.get_connection() try: yield conn conn.commit() except Exception: conn.rollback() raise finally: conn.c...
- [ ] `Database.initialize_schema()` — run the SCHEMA script with conn.executescript(SCHEMA).

**`app/database/repositories.py`**

- [ ] `SessionRepository.create(session)` — INSERT a row into sessions and return the new id (cursor.lastrowid). Store datetimes with .isoformat().  
  ✅ checked by `tests/test_repositories.py`
- [ ] `SessionRepository.finish(session_id, ended_at, frames_processed, average_fps)` — UPDATE the closing columns of one session.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `SessionRepository.get(session_id)` — SELECT one session and map the row to a Session object.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `SessionRepository.list_recent(limit)` — the newest sessions first, for the history screen.
- [ ] `SessionRepository.delete(session_id)` — DELETE the session; the FK cascade removes its samples.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `SampleRepository.add(sample)` — INSERT one sample. probabilities is stored as json.dumps(list_of_floats) and read back with json.loads.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `SampleRepository.add_many(samples)` — executemany() for a whole buffer at once.
- [ ] `SampleRepository.list_for_session(session_id)` — all samples of one session, ordered by timestamp.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `SampleRepository.emotion_counts(session_id)` — {Emotion: count} using "SELECT emotion, COUNT(*) FROM emotion_samples WHERE session_id=? GROUP BY emotion". Let SQL do the counting instead of loading every row into Python.  
  ✅ checked by `tests/test_repositories.py`

**`app/models/session.py`**

- [ ] `Session.duration_seconds` — (ended_at - started_at) in seconds, 0.0 while running.  
  ✅ checked by `tests/test_repositories.py`
- [ ] `Session.emotion_distribution()` — return {Emotion: percentage} over self.samples.
- [ ] `Session.dominant_emotion()` — the emotion with the highest percentage, or None.

**`app/utils/exporter.py`**

- [ ] `SessionExporter.export(session_id, directory)` — write the file and return its full path.

**`app/views/chart_frame.py`**

- [ ] `ChartFrame.__init__(parent, history_size)` — Figure, subplot, seven lines (one per emotion, coloured like the boxes), y-limits 0..1, legend, and the FigureCanvasTkAgg.
- [ ] `ChartFrame.push(probabilities)` — append each of the 7 values to its deque and redraw.
- [ ] `ChartFrame.clear()` — empty every deque and redraw an empty chart.

**`app/views/emotion_panel.py`**

- [ ] `EmotionPanel.__init__(parent)` — three widgets: self.name = ttk.Label(self, text="-", font=("Arial", 28, "bold")) self.name.pack()
- [ ] `EmotionPanel.show(emotion, confidence)` — update all three: self.name.config(text=emotion.hebrew, foreground=self._hex(emotion)) self.percent.config(text=f"{confidence * 100:.0f}%") self.bar["value"] = confidence * 100
- [ ] `EmotionPanel.clear()` — no face in the frame: self.name.config(text="-", foreground="grey") self.percent.config(text="") self.bar["value"] = 0

**`app/views/main_window.py`**

- [ ] `MainWindow.__init__(root, on_start, on_stop, on_export, on_detector_change)` — build the toolbar, then the three sub-views: self.video_frame = VideoFrame(self) self.emotion_panel = EmotionPanel(self) self.chart_frame = ChartFrame(self) self.stats_frame = StatsFrame(self) Place them with grid() a...
- [ ] `MainWindow.set_running(running)` — enable/disable buttons so Start cannot be pressed twice.
- [ ] `MainWindow.show_message(title, message)` — messagebox.showinfo wrapper, so controllers never import tkinter.

**`app/views/stats_frame.py`**

- [ ] `StatsFrame.__init__(parent)` — labels for elapsed time, frames processed, current FPS and the dominant emotion so far.
- [ ] `StatsFrame.update_live(elapsed_seconds, frames, fps)` — refresh the three live labels.
- [ ] `StatsFrame.show_summary(session)` — when a session ends, show session.emotion_distribution() as a short "happy 42% | neutral 31% | ..." line plus the duration.

**`app/views/video_frame.py`**

- [ ] `VideoFrame.__init__(parent)` — two lines: self.label = ttk.Label(self) self.label.pack() self._photo = None # see the class docstring - this matters
- [ ] `VideoFrame.show(frame_bgr)` — the four-step conversion from the class docstring: rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB) image = Image.fromarray(rgb) # from PIL photo = ImageTk.PhotoImage(image) # from PIL.ImageTk self.label.config(image=...
- [ ] `VideoFrame.clear()` — self.label.config(image="") and self._photo = None, so the last frame does not stay frozen on screen after stopping.

> **Exit condition:** `pytest -v` **all** green. `python run.py` opens a window with video, emotion panel, live chart and statistics bar; Stop shows a summary; "Export CSV" writes a file in `exports/` that opens in Excel; `faceemotion.db` holds the session and its samples (check with DB Browser for SQLite).

## Stage 7 — Comparing alternatives, tests and documentation

**`app/controllers/app_controller.py`**

- [ ] `AppController.change_detector(name)` — swap self.detector at runtime - this is why the Strategy pattern is there. Works while the camera is running.

**`app/ml/predictor.py`**

- [ ] `EmotionPredictor.predict_batch(model_inputs)` — (optional): stack several faces from the same frame into a single batch with np.concatenate and classify them in one GPU call. With more than one person in view this is much faster than a loop.

**`app/vision/dnn_detector.py`**

- [ ] `DnnFaceDetector.__init__(proto_path, weights_path)` — (optional): self._net = cv2.dnn.readNetFromCaffe(proto, weights) Raise a clear error if either file is missing, telling the user where to download it from.
- [ ] `DnnFaceDetector.detect(frame)` — (optional): 1. h, w = frame.shape[:2] 2. blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0)) 3. self._net.setInput(blob); detections = self._net.forward() 4. for every d...

> **Exit condition:** a complete project book where every number comes from a file in `reports/` or from `pytest` output.
