# %% [markdown]
# # 02 · Threads, locks and race conditions
#
# **Read first:** `01_theory/04_threads.md`
#
# 1. make a race condition **happen** and lose points
# 2. fix it with a lock
# 3. `Lock` vs `RLock` — the deadlock against yourself
# 4. copy under the lock, work outside it
# 5. a timer and an idempotent `close_question`
# 6. producer / consumer with a `queue.Queue` — how the client keeps Tkinter safe

# %%
import queue
import threading
import time

# %% [markdown]
# ## 1. A race condition you can see
#
# `score += points` is really **read → add → write**. We make the gap between read and write visible with a tiny
# `time.sleep(0)` — it lets another thread run exactly there, the way a real thread switch sometimes does.

# %%
class Player:
    def __init__(self):
        self.score = 0

def add_points_unsafe(player, points):
    current = player.score          # read
    time.sleep(0)                   # <- a thread switch can happen here
    player.score = current + points # write

def run(add, n_threads=8, n_times=200):
    p = Player()
    threads = [threading.Thread(target=lambda: [add(p, 10) for _ in range(n_times)]) for _ in range(n_threads)]
    for t in threads: t.start()
    for t in threads: t.join()
    return p.score

expected = 8 * 200 * 10
for attempt in range(3):
    print(f"expected {expected}, got {run(add_points_unsafe)}")

# %% [markdown]
# Points vanish, and a different amount every time. In the real server the gap is tiny, so it happens maybe once
# in a thousand games — the worst kind of bug: tests pass, the classroom demo fails.
#
# ## 2. The fix: a lock around the critical section

# %%
lock = threading.Lock()

def add_points_safe(player, points):
    with lock:                          # only one thread at a time inside
        current = player.score
        time.sleep(0)
        player.score = current + points

for attempt in range(3):
    print(f"expected {expected}, got {run(add_points_safe)}")

# %% [markdown]
# ## 3. Lock vs RLock
#
# `record_answer()` holds the lock and may call `close_question()`, which takes the lock **again**. With a plain
# `Lock` the thread waits for itself — forever. We use `acquire(timeout=1)` so the notebook does not hang:

# %%
def close_question(lk):
    got = lk.acquire(timeout=1)
    if not got:
        return "DEADLOCK: waited 1 s for a lock I already hold"
    lk.release()
    return "closed"

def record_answer(lk):
    with lk:
        return close_question(lk)

print("Lock :", record_answer(threading.Lock()))
print("RLock:", record_answer(threading.RLock()))

# %% [markdown]
# ## 4. Do not hold the lock while doing slow things
#
# One client on bad Wi-Fi takes 0.5 s to receive. Holding the lock while sending to all 8 freezes the game for
# everyone; copying the list under the lock and sending outside it does not.

# %%
handlers_lock = threading.Lock()
handlers = ["fast"] * 7 + ["slow"]

def send(h):
    time.sleep(0.5 if h == "slow" else 0.001)

def broadcast_bad():
    with handlers_lock:
        for h in handlers:
            send(h)

def broadcast_good():
    with handlers_lock:
        targets = list(handlers)        # fast: copy
    for h in targets:                   # slow: no lock held
        send(h)

for broadcast in (broadcast_bad, broadcast_good):
    t = threading.Thread(target=broadcast); t.start()
    time.sleep(0.05)
    t0 = time.perf_counter()
    with handlers_lock:                 # a player tries to JOIN during the broadcast
        waited = time.perf_counter() - t0
    t.join()
    print(f"{broadcast.__name__:15s} a JOIN had to wait {waited * 1000:.0f} ms")

# %% [markdown]
# ## 5. Timers, and why `close_question` must be idempotent
#
# The 15-second timer and "the last player just answered" can both call `close_question` — maybe at the same
# moment, from two threads. The second call must do nothing.

# %%
class Round:
    def __init__(self, time_limit):
        self._lock = threading.RLock()
        self.state = "QUESTION"
        self.closed_count = 0
        self.timer = threading.Timer(time_limit, self.close_question)
        self.timer.start()

    def close_question(self):
        with self._lock:
            if self.state != "QUESTION":        # already closed: do nothing (idempotent)
                return
            self.state = "SCORING"
            self.closed_count += 1
            self.timer.cancel()

r = Round(time_limit=0.2)
threading.Thread(target=r.close_question).start()   # "all players answered" at the same time
time.sleep(0.4)                                      # ... and the timer fires too
print("state:", r.state, "  times scored:", r.closed_count)

# %% [markdown]
# ## 6. Producer / consumer — the client's queue
#
# Tkinter widgets may be touched **only** from the Tkinter thread. The reader thread puts messages into a
# thread-safe `queue.Queue`; the window takes them every 50 ms with `root.after(50, poll)`. Here the "window" is a
# simple loop:

# %%
inbox = queue.Queue()

def reader_thread():                     # the producer: imagine recv() + from_wire() here
    for i in range(5):
        inbox.put({"type": "LOBBY_UPDATE", "players": i + 1})
        time.sleep(0.03)
    inbox.put({"type": "GAME_OVER"})

threading.Thread(target=reader_thread, daemon=True).start()
done = False
while not done:                          # the consumer: this is what root.after(50, poll) does
    while True:
        try:
            msg = inbox.get_nowait()
        except queue.Empty:
            break
        print("UI thread handles:", msg)
        done = msg["type"] == "GAME_OVER"
    time.sleep(0.05)

# %% [markdown]
# ## ✍️ Try it yourself
#
# 1. Remove `time.sleep(0)` from `add_points_unsafe`. Does the bug still appear? Is the code now correct? (Careful!)
# 2. Two threads each run `counter += 1` 1,000 times with no lock. What are the smallest and largest possible
#    results? (theory 4.x, question 1)
# 3. In section 5, remove the `if self.state != "QUESTION"` check. What does `closed_count` become?
#
# Then solve exercises 4–6 in `03_exercises/`.
