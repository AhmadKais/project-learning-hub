# %% [markdown]
# # 03 · The game engine — state machine, scoring, leaderboard
#
# **Read first:** `01_theory/05_state_machine_scoring.md`
#
# The whole game logic **without any sockets** — which is exactly why it is easy to test.
#
# 1. the scoring formula — the table of theory §5.4
# 2. picking questions with no repeats (and failing early when there are not enough)
# 3. a `GameEngine` with four states, one `RLock`, and a reply for every illegal move
# 4. a full game, driven by hand
# 5. 8 threads answering at the same instant — every answer recorded

# %%
import random
import sqlite3
import threading
import time
from dataclasses import dataclass, field

MAX_POINTS, MIN_POINTS_CORRECT, MIN_PLAYERS = 1000, 100, 2

# %% [markdown]
# ## 1. Scoring

# %%
def points_for(is_correct, response_time, time_limit=15.0):
    if not is_correct:
        return 0
    t = min(max(response_time, 0.0), time_limit)          # clamp: a late answer must not go negative
    return max(MIN_POINTS_CORRECT, round(MAX_POINTS * (time_limit - t) / time_limit))

for rt in (0.0, 3.0, 7.5, 14.9, 20.0):
    print(f"correct after {rt:4.1f} s -> {points_for(True, rt)}")
print("wrong              ->", points_for(False, 1.0))

# %% [markdown]
# ## 2. Questions — no repeats, and fail early
#
# At game start: fetch only the ids, shuffle in Python, keep N. Then one primary-key lookup per round.

# %%
db = sqlite3.connect(":memory:", check_same_thread=False)
db.execute("CREATE TABLE questions (id INTEGER PRIMARY KEY, category TEXT, text TEXT, options TEXT, correct_index INTEGER)")
for i in range(1, 13):
    db.execute("INSERT INTO questions VALUES (?, ?, ?, ?, ?)",
               (i, "networks" if i <= 6 else "python", f"Question {i}?", "A|B|C|D", i % 4))

def prepare(category, n, rng=random):
    ids = [r[0] for r in db.execute("SELECT id FROM questions WHERE category = ?", (category,))]
    if len(ids) < n:
        raise ValueError(f"category '{category}' has {len(ids)} questions, the game needs {n}")
    rng.shuffle(ids)
    return ids[:n]

print(prepare("python", 5, random.Random(1)))
try:
    prepare("networks", 10)
except ValueError as e:
    print("refused at game start:", e)

# %% [markdown]
# ## 3. The engine
#
# Every public method takes the **one** lock first. Every command starts with "am I allowed in this state?".
# Replies are returned as `(recipient, type, payload)` tuples — the server would send them; here we just print.

# %%
@dataclass
class PlayerState:
    name: str
    score: int = 0
    connected: bool = True

class GameEngine:
    def __init__(self, questions, time_limit=15.0, clock=time.monotonic):
        self._lock = threading.RLock()
        self.state = "LOBBY"
        self.players = {}
        self.host = None
        self.questions = questions            # list of (id, text, options, correct_index)
        self.index = -1
        self.answers = {}                     # name -> (choice, response_time)
        self.time_limit, self.clock = time_limit, clock
        self.sent_at = None

    def join(self, name):
        with self._lock:
            if self.state != "LOBBY":
                return [(name, "ERROR", {"code": "game_started"})]
            if not name or len(name) > 16 or name in self.players:
                return [(name, "ERROR", {"code": "name_taken" if name in self.players else "bad_name"})]
            self.players[name] = PlayerState(name)
            self.host = self.host or name
            return [(name, "WELCOME", {"name": name, "is_host": name == self.host}),
                    ("ALL", "LOBBY_UPDATE", {"players": list(self.players)})]

    def start_game(self, name):
        with self._lock:
            if self.state != "LOBBY" or name != self.host:
                return [(name, "ERROR", {"code": "not_allowed"})]
            if len(self.players) < MIN_PLAYERS:
                return [(name, "ERROR", {"code": "not_enough_players"})]
            return self.next_question()

    def next_question(self):
        with self._lock:
            self.index += 1
            if self.index >= len(self.questions):
                self.state = "GAME_OVER"
                return [("ALL", "GAME_OVER", {"entries": self.leaderboard()})]
            self.state, self.answers, self.sent_at = "QUESTION", {}, self.clock()
            qid, text, options, _ = self.questions[self.index]
            return [("ALL", "QUESTION", {"question_id": qid, "text": text, "options": options})]   # NO answer inside!

    def record_answer(self, name, question_id, choice):
        with self._lock:
            if self.state != "QUESTION":
                return [(name, "ERROR", {"code": "not_accepting"})]
            if question_id != self.questions[self.index][0]:
                return [(name, "ERROR", {"code": "wrong_question"})]
            if name in self.answers:
                return [(name, "ERROR", {"code": "already_answered"})]
            if not isinstance(choice, int) or not 0 <= choice <= 3:
                return [(name, "ERROR", {"code": "bad_choice"})]
            self.answers[name] = (choice, self.clock() - self.sent_at)
            connected = [p for p in self.players.values() if p.connected]
            if len(self.answers) == len(connected):
                return self.close_question()          # RLock: taking the lock again is fine
            return []

    def close_question(self):
        with self._lock:
            if self.state != "QUESTION":
                return []                             # idempotent
            self.state = "SCORING"
            correct = self.questions[self.index][3]
            results = []
            for name, (choice, rt) in self.answers.items():
                pts = points_for(choice == correct, rt, self.time_limit)
                self.players[name].score += pts
                results.append({"name": name, "choice": choice, "points": pts})
            return [("ALL", "RESULT", {"correct_index": correct, "answers": results}),
                    ("ALL", "LEADERBOARD", {"entries": self.leaderboard()})]

    def leaderboard(self):
        ranked = sorted(self.players.values(), key=lambda p: (-p.score, p.name))
        return [(i + 1, p.name, p.score) for i, p in enumerate(ranked)]

# %% [markdown]
# ## 4. A full game, by hand — with a fake clock so the times are exact

# %%
now = [0.0]
questions = [(q, f"Question {q}?", ["A", "B", "C", "D"], q % 4) for q in prepare("python", 2, random.Random(1))]
game = GameEngine(questions, clock=lambda: now[0])

def show(replies):
    for r in replies:
        print("  ->", r)

print("ANSWER in the lobby:");      show(game.record_answer("liraz", 1, 0))
print("JOIN liraz, dana:");          show(game.join("liraz")); show(game.join("dana"))
print("JOIN dana again:");           show(game.join("dana"))
print("dana tries to start:");       show(game.start_game("dana"))
print("liraz starts:");              show(game.start_game("liraz"))
q1, correct1 = questions[0][0], questions[0][3]
now[0] = 3.0;  print("liraz answers right after 3 s:");   show(game.record_answer("liraz", q1, correct1))
print("liraz answers again:");        show(game.record_answer("liraz", q1, correct1))
now[0] = 7.5;  print("dana answers wrong after 7.5 s (last player -> round closes):"); show(game.record_answer("dana", q1, (correct1 + 1) % 4))
print("late answer after closing:"); show(game.record_answer("dana", q1, correct1))

# %% [markdown]
# Every illegal move got a clear error code, and the state never changed because of one.
#
# ## 5. Eight threads, one instant

# %%
names = [f"p{i}" for i in range(8)]
game = GameEngine([(1, "Q?", ["A", "B", "C", "D"], 2), (2, "Q2?", ["A", "B", "C", "D"], 0)])
for n in names:
    game.join(n)
game.start_game("p0")

barrier = threading.Barrier(8)
def answer(n):
    barrier.wait()                         # all 8 threads release at the same moment
    game.record_answer(n, 1, 2)
threads = [threading.Thread(target=answer, args=(n,)) for n in names]
for t in threads: t.start()
for t in threads: t.join()
print("answers recorded:", len(game.answers), " state:", game.state)
print("leaderboard:", game.leaderboard()[:3], "...")

# %% [markdown]
# All 8 recorded, the round closed exactly once (the 8th answer closed it), and every player was scored. That is
# your project's `test_concurrent_answers_are_all_recorded`.
#
# ## ✍️ Try it yourself
#
# 1. Compute by hand the points at 6.0 s, 12.0 s and 15.0 s, then check with `points_for`.
# 2. Make a player disconnect during QUESTION (`game.players["p3"].connected = False`) before the others answer.
#    Does the round still close early? Why?
# 3. Replace the `RLock` with a `Lock`. Which line deadlocks, and when?
#
# Then solve exercises 7–10 in `03_exercises/`.
