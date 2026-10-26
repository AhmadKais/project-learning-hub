# Talk for next week - Spam: why it exists and how computers learned to catch it

**Student:** Laith Halabi  ·  **When:** next week's class  ·  **Length:** 8-10 minutes + questions

**The question your talk answers:** Why does spam still reach us, and how did filters go from hand-written rules to learning from examples?

This talk is the big picture: the real-world problem and what your app will do about it. No formulas and
no code yet - those come in [Mission 1](MISSION_01.md). Talk to the class as if they have never heard of
your project.

## What to cover

1. What spam and smishing (SMS phishing) are, with 2-3 real-looking examples (make them up, no real numbers)
2. Why sending spam pays: it costs almost nothing to send a million messages
3. Rule-based filters ("block every message with FREE!!!") and why spammers beat them in a week
4. The learning idea: show the computer thousands of labelled messages - Paul Graham's "A Plan for Spam" (2002) made it famous
5. The two mistakes: spam in the inbox against a real message in the spam folder - which one hurts more?
6. Your data and your app: the SMS Spam Collection (5,574 messages, about 13% spam) and what SpamClassifier will show

## Get the class involved

Show 6 messages and let the class vote spam or ham before you reveal the labels - then count how many the class got wrong.

## Where to read

- [Lesson 01 - what is machine learning](../lessons/01_what_is_learning/LESSON.md)
- [Lesson 03 - the two kinds of mistakes](../lessons/03_confusion_matrix_metrics/LESSON.md)
- [Theory 00 - the intro](01_theory/00_intro.md)
- More sources, already checked: [`19_resources.md`](05_defence/19_resources.md)

## Be ready for these questions

- Why not just keep a list of bad words?
- Your corpus is English. What would break with Hebrew or Arabic messages?
- Who decides what counts as spam?

## Rules

- 6-8 slides. A picture or a drawing on each slide, not paragraphs.
- Say it in your own words. If you read from the slide, you don't know it yet.
- Any example (message, link, face, CV) you make up yourself - no real people's data, no faces from the dataset.
- Practise once with a timer at home.
