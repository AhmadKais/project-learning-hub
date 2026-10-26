# Talk for next week - Phishing: how a single link steals a password

**Student:** Dani Faris  ·  **When:** next week's class  ·  **Length:** 8-10 minutes + questions

**The question your talk answers:** How do attackers make a fake link look real, and how can a program spot it without opening the page?

This talk is the big picture: the real-world problem and what your app will do about it. No formulas and
no code yet - those come in [Mission 1](MISSION_01.md). Talk to the class as if they have never heard of
your project.

## What to cover

1. What phishing is: e-mail, SMS (smishing), fake login pages - one made-up example of each
2. The tricks inside a link: a real brand in the subdomain, look-alike letters, `@`, an IP address instead of a name, link shorteners
3. Reading a host from the right: who really owns `paypal.com.secure-login.xyz`?
4. How browsers protect you today: block lists such as Google Safe Browsing - and why a brand-new link is not on the list yet
5. The learning idea: learn what phishing links look like from about half a million labelled links
6. Your app: paste a link into PhishGuard, get a verdict and three reasons

## Get the class involved

Show 6 made-up links and let the class vote real or fake, then take them apart on the board.

## Where to read

- [Lesson 18 - URL features](../lessons/18_url_features_entropy/LESSON.md)
- [Lesson 01 - what is machine learning](../lessons/01_what_is_learning/LESSON.md)
- [Theory 00 - the intro](01_theory/00_intro.md)
- More sources, already checked: [`19_resources.md`](05_defence/19_resources.md)

## Be ready for these questions

- Why not just open the page and look at it?
- If your program says "safe", can the user stop being careful?
- What would an attacker change after reading your project?

## Rules

- 6-8 slides. A picture or a drawing on each slide, not paragraphs.
- Say it in your own words. If you read from the slide, you don't know it yet.
- Any example (message, link, face, CV) you make up yourself - no real people's data, no faces from the dataset.
- Practise once with a timer at home.
