# Talk for next week - Can a computer taste wine?

**Student:** Seif Ferro  ·  **When:** next week's class  ·  **Length:** 8-10 minutes + questions

**The question your talk answers:** Wine experts grade wine by taste. Can a program predict the grade from a lab test alone?

This talk is the big picture: the real-world problem and what your app will do about it. No formulas and
no code yet - those come in [Mission 1](MISSION_01.md). Talk to the class as if they have never heard of
your project.

## What to cover

1. How wine is graded by human tasters, and why two experts can disagree
2. The data: 6,497 Portuguese Vinho Verde wines (Cortez et al., 2009) - 11 lab measurements and a grade
3. What a few of the measurements mean in plain words: alcohol, acidity, sugar, sulphates
4. The idea of "neighbours": a new wine probably tastes like the wines most similar to it - the same idea recommends films and songs
5. Why most wines are average and very few are great, and what that does to a predictor
6. Your app: enter a wine's lab values, get a grade and the most similar wines

## Get the class involved

Show the class 4 wines as two numbers (alcohol, acidity) and a fifth unknown one - let them guess its grade from its nearest neighbours.

## Where to read

- [Lesson 01 - what is machine learning](../lessons/01_what_is_learning/LESSON.md)
- [Lesson 15 - k-nearest neighbours (the first half is enough)](../lessons/15_knn/LESSON.md)
- [Theory 00 - the intro](01_theory/00_intro.md)
- More sources, already checked: [`19_resources.md`](05_defence/19_resources.md)

## Be ready for these questions

- Can the program be better than the tasters it learned from?
- Why use grades low / medium / high instead of the score 0-10?
- What does "similar" mean for two wines?

## Rules

- 6-8 slides. A picture or a drawing on each slide, not paragraphs.
- Say it in your own words. If you read from the slide, you don't know it yet.
- Any example (message, link, face, CV) you make up yourself - no real people's data, no faces from the dataset.
- Practise once with a timer at home.
