# Glossary — every word in the lessons, in plain language

Each word: what it means in everyday words, an example, and the lesson where it is explained in depth.
If a lesson uses a word you don't know, look here first.

## Machine learning — the basic words

| Word | Plain meaning | Everyday example | Lesson |
|---|---|---|---|
| **machine learning (ML)** | instead of writing the rules yourself, you give the computer many examples with the right answers and it finds the rules | a child learns what a dog is by seeing many dogs, not by reading a definition | 01 |
| **example / sample / row** | one thing we know the answer for | one SMS, one wine, one URL, one face | 01 |
| **feature** | one number that describes an example | the alcohol of a wine; how many dots a URL has | 01 |
| **label** | the correct answer for an example | "spam" / "ham"; "high quality" | 01 |
| **class** | one of the possible answers | spam and ham are the two classes | 01 |
| **dataset** | the whole table of examples | 5,574 SMS messages with their labels | 01 |
| **model** | the rules the computer learned — a function from features to an answer | a doctor's experience: symptoms in, diagnosis out | 01 |
| **training / fitting** | the computer looking at the examples and building the model | studying for an exam | 01 |
| **prediction** | the model's answer for a new example | the forecast "70 % rain" | 01 |
| **classifier** | a model whose answer is a class | the spam filter | 01 |
| **parameter** | a number inside the model that training sets | the weights of logistic regression | 12 |
| **hyper-parameter** | a setting **you** choose before training | k in k-NN, the learning rate | 01 |
| **training set** | the examples the model learns from | the textbook and homework | 01 |
| **validation set** | examples kept aside to choose settings | the mock exam | 01 |
| **test set** | examples kept aside until the very end, used once | the real exam | 01 |
| **generalisation** | doing well on examples never seen before | understanding, not memorising | 01 |
| **overfitting** | the model memorised the training examples (including their noise) and fails on new ones | memorising last year's exam answers | 01 |
| **underfitting** | the model is too simple to learn the pattern | answering "C" to every question | 01 |
| **noise** | random errors in the data that no rule can explain | a taster who had a cold that day | 01 |
| **bias (of a model)** | being wrong in the same direction every time | a scale that always shows +2 kg | 01 |
| **variance (of a model)** | giving very different answers depending on which examples it saw | a moody judge | 01 |
| **baseline** | the simplest possible "model", to beat | always answer "ham" | 03, 15 |
| **imbalanced data** | one class is much rarer than another | 13 % spam, 87 % ham | 03 |
| **stratified split** | splitting so that each part keeps the same share of each class | dealing cards suit by suit | 01, 05 |
| **cross-validation** | testing k times, each time on a different slice, and averaging | several mock exams instead of one | 05 |
| **leakage** | information from the test set sneaks into training — the score becomes falsely good | seeing the exam before the exam | 05 |
| **pipeline** | the fixed chain of steps from raw input to answer | wash → cut → cook | 06 |
| **train/serve skew** | the app prepares the input differently from training — silent wrong answers | studying in English, exam in Hebrew | 18, 19 |
| **learning curve** | a chart of how good the model gets as it sees more examples | 10 SMS → 87 %, 3,901 SMS → 98 % | 01 |
| **lazy learner** | a model that only stores the examples and does the work when asked | k-NN | 15 |
| **domain shift** | the new examples look different from the training examples | a network trained on photos shown a drawing | 19, 23 |

## Measuring

| Word | Plain meaning | Example | Lesson |
|---|---|---|---|
| **accuracy** | share of all answers that were right | 95 of 100 correct = 0.95 | 03 |
| **confusion matrix** | a table: truth (rows) × prediction (columns) | 187 spam caught, 5 real messages hidden … | 03 |
| **true positive (TP)** | said "yes", and it was yes | spam caught | 03 |
| **false positive (FP)** | said "yes", but it was no — a false alarm | a real message sent to spam | 03 |
| **false negative (FN)** | said "no", but it was yes — a miss | spam that reached the inbox | 03 |
| **true negative (TN)** | said "no", and it was no | a real message delivered | 03 |
| **precision** | of everything I flagged, how much was right | of 10 fish in my net, 9 were the kind I wanted | 03 |
| **recall** | of everything I should have flagged, how much I caught | I caught 9 of the 12 fish in the lake | 03 |
| **F1** | one number combining precision and recall; high only if both are high | | 03 |
| **macro-F1** | the F1 of each class, averaged — small classes count equally | | 03 |
| **threshold** | the cut-off: above it → "yes" | flag as spam if probability ≥ 0.7 | 04 |
| **ROC curve** | recall vs false-alarm rate for every threshold | | 04 |
| **AUC** | area under the ROC curve; chance a random positive scores above a random negative | 0.5 = coin flip, 1 = perfect | 04 |
| **calibration** | when the model says 70 %, it is right about 70 % of the time | a weather forecaster you can trust | 14, 24 |
| **P@k (precision at k)** | of the first k results, how many are right | 8 of the top 10 CVs are good → 0.8 | 10 |
| **MRR** | how high the first good result is, on average (1/position) | first good result at position 2 → 0.5 | 10 |
| **base rate** | how common the positive class is before any test | 1 in 100 people has the disease | 03 |
| **harmonic mean** | a strict average that is pulled down by the weakest value | F1 of precision and recall | 03 |
| **calibration / reliability** | when the model says 70 %, it is right 70 % of the time | an honest weather forecaster | 14 |

## Maths words (all explained in Lesson 00)

| Word | Plain meaning | Example |
|---|---|---|
| **average / mean** | add all, divide by how many | (2+4+6)/3 = 4 |
| **standard deviation (std)** | the typical distance from the average | heights within about ±7 cm |
| **probability P(x)** | how likely, between 0 and 1 | P(heads) = 0.5 |
| **P(A \ | B)** — e.g. probability of A, counting only the cases where B is true | P(spam \ |
| **Σ (sigma)** | add them all up | Σ of 3, 5, 2 = 10 |
| **x²**, **√x** | x times x; and the opposite | 5² = 25, √25 = 5 |
| **log / ln** | how many times you multiply; turns × into + | ln(e) = 1, log₁₀(1000) = 3 |
| **eˣ** | the opposite of ln; always positive | e¹ = 2.718 |
| **slope / derivative / gradient** | how steep; which way is downhill | |
| **vector** | a list of numbers = an arrow / a point | (3, 4) |
| **matrix** | a table of numbers | the dataset |
| **dot product** | multiply matching numbers and add | (1,2)·(3,4) = 3 + 8 = 11 |
| **distance** | how far apart two points are (Pythagoras) | (0,0) to (3,4) = 5 |
| **cosine similarity** | how much two arrows point the same way, 0 … 1 for text | 1 = same direction |
| **median** | the middle value after sorting (Lesson 00) | the middle salary, not pulled up by one millionaire |
| **variance** | the average squared distance from the average (std²) (Lesson 00) | (4 + 0 + 0 + 4) ÷ 4 = 2 |
| **cumulative** | adding up as you go (Lesson 19) | the share of pixels darker than or equal to each grey level |
| **half-open interval [a, b)** | from a, up to but not including b (Lesson 27) | a hotel stay: nights, not days; Python's `range(a, b)` |

## Text and search

| Word | Plain meaning | Lesson |
|---|---|---|
| **token / term** | one word-piece of a text after cleaning | 06 |
| **tokenizing** | cutting text into tokens | 06 |
| **stop-word** | a very common word with no meaning of its own ("the", "and") | 06 |
| **stemming** | cutting words to a common root (developed → develop) | 06 |
| **n-gram / bigram** | n neighbouring words as one term ("machine learning") | 06 |
| **vocabulary** | the list of all terms the model knows | 06, 07 |
| **bag of words** | count every word; forget the order | 07 |
| **TF (term frequency)** | how often a word is in this document | 07 |
| **DF (document frequency)** | in how many documents a word appears | 07 |
| **IDF** | rare across documents → big weight | 07 |
| **TF-IDF** | TF × IDF: frequent here and rare elsewhere = important | 07 |
| **normalisation (L2)** | dividing a vector by its length so long and short texts compare fairly | 07, 08 |
| **BM25** | a better TF-IDF: repetition and length are corrected | 09 |
| **inverted index** | for each word, the list of documents that contain it — like a book's index | 09 |
| **ranking** | ordering results from best to worst | 08–10 |

## Models

| Word | Plain meaning | Lesson |
|---|---|---|
| **Naive Bayes** | counts which words appear in each class and combines the evidence with probabilities | 11 |
| **Laplace smoothing** | add 1 to every count so nothing has probability 0 | 11 |
| **log-odds** | how strongly one word pushes toward spam (+) or ham (−) | 11 |
| **logistic regression** | weighted vote of the features, squashed into a probability | 12 |
| **sigmoid** | the S-curve that turns any number into 0 … 1 | 12 |
| **weight** | how much one feature counts in the vote | 12 |
| **bias (term)** | the starting point of the vote, before any feature | 12 |
| **loss / log-loss** | a number measuring how wrong the model is; training makes it small | 12 |
| **gradient descent** | improve the weights by stepping downhill on the loss | 12, 21 |
| **learning rate** | how big each downhill step is | 12, 21 |
| **regularisation / C** | a brake that keeps weights small to avoid overfitting | 12, 14 |
| **decision tree** | a flow chart of yes/no questions learned from data | 13 |
| **Gini impurity** | how mixed a group is (0 = pure) | 13 |
| **random forest** | many trees, each trained on a random sample, voting | 13 |
| **SVM** | finds the widest street between two classes | 14 |
| **support vectors** | the examples on the edge of the street | 14 |
| **k-NN** | answer like the k most similar known examples | 15 |
| **scaling / z-score** | putting every feature on the same scale | 02 |
| **kd-tree** | a structure that splits space so a search can skip far regions | 16 |
| **feature weight (k-NN)** | how much a feature counts in the distance | 17 |
| **entropy** | how unpredictable a string is | 18 |
| **bootstrap sample** | a random sample drawn with replacement — some rows twice, some never — e.g. each tree of a forest gets its own | 13 |
| **wisdom of the crowd** | the average of many independent guesses beats most single guesses — e.g. the forest's vote | 13 |
| **support vector** | an example on the edge of the SVM's street; only these decide the fence | 14 |

## Deep learning and vision

| Word | Plain meaning | Lesson |
|---|---|---|
| **pixel** | one dot of a picture, a number 0 (black) … 255 (white) | 19 |
| **channel** | one colour table (R, G or B) | 19 |
| **histogram equalisation** | stretching the brightness so dark pictures look normal | 19 |
| **neuron** | weighted sum + bias, then an activation | 20 |
| **activation (ReLU)** | a bend after each neuron; ReLU = max(0, x) | 20 |
| **layer** | a group of neurons working side by side | 20 |
| **neural network** | layers connected one after the other | 20 |
| **logits** | the network's raw scores before softmax | 20 |
| **softmax** | turns scores into probabilities that add to 1 | 20 |
| **cross-entropy** | the loss for many classes: −ln(probability of the right class) | 20 |
| **backpropagation** | computing every weight's slope, from the loss backwards (chain rule) | 21 |
| **epoch** | one pass over all training examples | 21 |
| **batch** | the group of examples used for one step | 21 |
| **optimiser (SGD, Adam)** | the rule that uses the slopes to change the weights | 21 |
| **convolution / filter / kernel** | a small window of weights sliding over the picture | 22 |
| **feature map** | the output picture of one filter | 22 |
| **pooling / stride** | making the picture smaller | 22 |
| **CNN** | a network made of convolutions | 22 |
| **residual block / ResNet** | layers with a shortcut: output = F(x) + x | 23 |
| **BatchNorm** | z-score inside the network, per batch | 23 |
| **dropout** | randomly switching off neurons during training | 23 |
| **augmentation** | random small changes to training pictures | 24 |
| **class weights** | rare classes cost more when wrong | 24 |
| **label smoothing** | target 91 % instead of 100 % | 24 |
| **early stopping / checkpoint** | stop when validation stops improving; keep the best weights | 24 |
| **Haar feature, integral image, cascade** | the fast face detector | 25 |
| **temporal smoothing** | averaging the last few frames' answers | 26 |
| **dead ReLU** | a neuron whose input stays negative, so its slope is 0 and it stops learning | 21 |
| **weight decay** | pulling every weight a little toward 0 each step — a brake against memorising — e.g. AdamW | 21 |
| **receptive field** | how much of the original picture one number of a layer depends on — e.g. 3 × 3 → 5 × 5 → 7 × 7 | 22 |
| **filter / stencil** | a small table of weights slid over the picture — e.g. a vertical-edge detector | 22 |

## Systems

| Word | Plain meaning | Lesson |
|---|---|---|
| **interval [a, b)** | from a, up to but not including b | 27 |
| **strategy pattern** | interchangeable rules behind one interface | 28 |
| **finite state machine (FSM)** | the program is always in one state; only allowed arrows move it | 30 |
| **guard** | a condition that must be true for a transition | 30 |
| **client / server** | the program that asks / the program that answers and decides | 31 |
| **socket, IP, port** | the phone line, the building's address, the apartment number | 31 |
| **TCP** | reliable, ordered stream of bytes | 31 |
| **framing** | marking where one message ends | 31 |
| **protocol** | the agreed messages and their meaning | 31 |
| **thread** | a part of the program running at the same time as other parts | 32 |
| **race condition** | the result depends on which thread happens to run first | 32 |
| **lock (mutex)** | a token only one thread can hold | 32 |
| **deadlock** | two threads each wait for the other — forever | 32 |
| **primary key, foreign key** | a row's unique id; a column that must point to an existing row | 33 |
| **constraint** | a rule the database enforces itself | 33 |
| **transaction** | a group of changes that happen all together or not at all | 33 |
| **index** | a sorted copy of some columns for fast search | 33 |
| **SQL injection** | user text becoming part of the SQL command | 33 |
| **Observer pattern** | an object announces events; listeners decide what to do — e.g. callbacks after every pass | 17 |
| **critical section** | code that only one thread may run at a time — e.g. read–add–write a shared score | 32 |
| **UDP** | single packets that may be lost or arrive out of order — no connection — e.g. video calls | 31 |
| **ER diagram** | a drawing of the tables and how they point at each other — e.g. rooms → bookings → invoices | 33 |
