# Chapter 17 — The defence

💡 **In short:** forty questions of the kind you will be asked. Short answers in chapter 20. If you can answer these without looking, you are ready.

## 17.1 How it goes

You present for a few minutes, then they ask. They are not trying to catch you out — they are checking that the person who wrote the code is the person in the room. The giveaway is never a wrong answer; it is a vague one.

Three habits worth having:

- **Point at the code.** "That's in `classifiers.py`, in `vote`, this line" beats any description.
- **Say what you do not know.** "I didn't measure that, but I'd expect X because Y" is a good answer. Guessing confidently is the worst one.
- **Run the tests.** If a claim is in doubt, `pytest tests/test_index.py -v` settles it in seconds.

## 17.2 The algorithm

1. Explain k-NN in two sentences. Why is it called a lazy learner?
2. Write the weighted Minkowski distance. What do p = 1 and p = 2 give?
3. Why can the search skip the root `^(1/p)`? When *is* the root taken?
4. Why is the vote weighted by 1/distance? What goes wrong without it?
5. Write the imbalance correction. What do alpha = 0 and alpha = 1 do?
6. Why is the prior of an absent class set to 1 and not 0?
7. How are ties broken, and why not simply `argmax`?
8. What happens with k = 1? With k = 500?
9. What does the model actually learn, if k-NN has no training step?
10. Show the test that proves your k-NN is correct.

## 17.3 Data

11. Why are 3, 4, 5 grouped as "low" and 7, 8, 9 as "high"?
12. Why must duplicates be removed before splitting? What would the score do otherwise?
13. Why does k-NN suffer from duplicates more than most models?
14. Why is scaling necessary for k-NN? Give the measured numbers.
15. z-score or min-max — which, and why? What does one extreme wine do to min-max?
16. Why must the scaler be fitted on training rows only?
17. At the lab station, which scaler scales a new wine?
18. A line of the CSV has pH = 19. What happens, and why not crash?

## 17.4 The kd-tree

19. How is the tree built? Why split by position and not by "< median"?
20. Why multiply the spread by the feature's weight?
21. Prove that `gap = w · |diff|ᵖ` is a safe bound for pruning.
22. Why `<=` and not `<` in the pruning test?
23. Why store `(-distance, -row)` in the heap?
24. Show how you know the tree returns exactly the right neighbours.
25. In 12 dimensions the tree measured 99% of the wines. Why?
26. You built the tree and then did not use it. Defend that.

## 17.5 Tuning and weights

27. How does the grid search avoid computing neighbours 192 times?
28. What is your rule for choosing a configuration? Why not just the highest macro-F1?
29. Why coordinate search for the weights and not gradient descent?
30. Explain the incremental update of the distance matrix. How do you know it is correct?
31. What does the 0.002 tolerance protect against?
32. The learned weights did not beat uniform weights. Why, and why keep them?
33. Name your three callbacks and say what each is for.

## 17.6 Evaluation

34. Why is accuracy not the main metric? What does always-medium score on each?
35. Define precision, recall, F1 and macro-F1 for a three-class problem.
36. Why stratified folds?
37. What problem does nested cross-validation solve? How do you prove nothing leaks?
38. Why run `evaluate.py` only once?

## 17.7 Architecture and security

39. What exactly happens if the two machines list the features in a different order? What stops it?
40. Name four threats to the system and the defence against each.
