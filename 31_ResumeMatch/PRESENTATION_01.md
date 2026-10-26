# Talk for next week - How companies pick 10 CVs out of 500

**Student:** Kosai Badreih  ·  **When:** next week's class  ·  **Length:** 8-10 minutes + questions

**The question your talk answers:** When hundreds of people apply for one job, how does software decide which CVs a human reads first?

This talk is the big picture: the real-world problem and what your app will do about it. No formulas and
no code yet - those come in [Mission 1](MISSION_01.md). Talk to the class as if they have never heard of
your project.

## What to cover

1. Applicant tracking systems: what happens to a CV after you press "send"
2. Keyword matching and its problems: "Python developer" against "programmed in Python"
3. The idea of TF-IDF in one sentence: a word that every CV has tells you nothing
4. Search engines do the same thing: BM25 is the default ranking in Elasticsearch and Lucene
5. Fairness and privacy: why ResumeMatch removes e-mails, phone numbers and ID numbers before matching
6. Your app: one job, a ranked list, and the words that explain each score

## Get the class involved

Give the class a short job ad and 4 short CVs and let them rank the CVs - then compare with how keyword counting ranks them.

## Where to read

- [Lesson 06 - text preprocessing](../lessons/06_text_preprocessing/LESSON.md)
- [Lesson 07 - TF-IDF (the first half is enough)](../lessons/07_tfidf/LESSON.md)
- [Theory 00 - the intro](01_theory/00_intro.md)
- More sources, already checked: [`09_resources.md`](05_defence/09_resources.md)

## Be ready for these questions

- Can a candidate cheat the ranking by repeating keywords?
- Should a computer be allowed to reject a CV without a human looking?
- Why remove the phone number - it has nothing to do with skills?

## Rules

- 6-8 slides. A picture or a drawing on each slide, not paragraphs.
- Say it in your own words. If you read from the slide, you don't know it yet.
- Any example (message, link, face, CV) you make up yourself - no real people's data, no faces from the dataset.
- Practise once with a timer at home.
