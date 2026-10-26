# Talk for next week - How a classroom quiz game works over a network

**Student:** Liraz Dakseh  ·  **When:** next week's class  ·  **Length:** 8-10 minutes + questions

**The question your talk answers:** When 8 phones answer a Kahoot-style question at the same moment, how does one computer know who was first?

This talk is the big picture: the real-world problem and what your app will do about it. No formulas and
no code yet - those come in [Mission 1](MISSION_01.md). Talk to the class as if they have never heard of
your project.

## What to cover

1. Client and server: who talks to whom, and why one computer must be the judge
2. IP addresses and ports - find your own with `ipconfig` (Windows) or `ip a` (Linux) and show it
3. TCP and UDP in plain words: a phone call against a postcard. Which one fits a quiz, which one fits a shooter game?
4. Lag and fairness: if one player's network is slower, is time-based scoring still fair?
5. What happens when a player's Wi-Fi drops in the middle of a game
6. Your app: the screens of LanGame and what the server does in one round

## Get the class involved

Ask two classmates to `ping` your computer and read the times out loud - that number is lag.

## Where to read

- [Lesson 31 - TCP and framing (the first half is enough)](../lessons/31_tcp_framing/LESSON.md)
- [Theory 00 - the intro](01_theory/00_intro.md)
- [Theory 02 - networks](01_theory/02_networks.md)
- More sources, already checked: [`19_resources.md`](05_defence/19_resources.md)

## Be ready for these questions

- Why can't the clients just tell each other their own scores?
- What is a port, and why does the server need a fixed one?
- What would a cheater try, and how does the server stop it?

## Rules

- 6-8 slides. A picture or a drawing on each slide, not paragraphs.
- Say it in your own words. If you read from the slide, you don't know it yet.
- Any example (message, link, face, CV) you make up yourself - no real people's data, no faces from the dataset.
- Practise once with a timer at home.
