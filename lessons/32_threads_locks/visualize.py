"""Lesson 32 - threads: the race condition step by step, the lock, deadlock, and threads + Tkinter."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)

# ---------------------------------------------------------------- 1. the race, step by step (Liraz's guide)
RACE = [("t1", "A", "read score → 0", 0), ("t2", "B", "read score → 0", 0), ("t3", "A", "add 800 → 800", 0),
        ("t4", "B", "add 500 → 500", 0), ("t5", "A", "write score = 800", 800), ("t6", "B", "write score = 500", 500)]
LOCKED = [("t1", "A", "take the lock", 0), ("t2", "B", "try the lock → WAIT", 0),
          ("t3", "A", "read 0, add 800, write 800", 800), ("t4", "A", "release the lock", 800),
          ("t5", "B", "take the lock", 800), ("t6", "B", "read 800, add 500, write 1300", 1300)]


def draw_race(ax, steps, k, title, final_note):
    blank(ax)
    ax.text(0.24, 0.92, "thread A (player A)", ha="center", fontsize=12.5, weight="bold", color=BLUE)
    ax.text(0.62, 0.92, "thread B (player B)", ha="center", fontsize=12.5, weight="bold", color=ORANGE)
    for i, (t, who, what, score) in enumerate(steps[:k]):
        y = 0.8 - i * 0.11
        ax.text(0.03, y, t, fontsize=11, color=INK2)
        x = 0.24 if who == "A" else 0.62
        bad = "WAIT" in what
        box(ax, x - 0.18, y - 0.04, 0.36, 0.08, what, color=BLUE if who == "A" else ORANGE,
            fill=LIGHT_BLUE if who == "A" else LIGHT_ORANGE, fontsize=11, weight="bold" if bad else "normal")
        ax.text(1.0, y, f"score={score}", ha="right", fontsize=10.5, family="monospace")
    if k == len(steps):
        ax.text(0.5, 0.06, final_note[0], ha="center", fontsize=13.5, weight="bold", color=final_note[1])
    ax.set_title(title, fontsize=13)


if L.wanted("race"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(16, 6.4))
    frames = list(range(1, 7)) + [6] * 4

    def upd(f):
        k = frames[f]
        draw_race(a1, RACE, k, "NO lock: score += …  is read, add, write", ("final 500 - A's 800 is LOST", RED))
        draw_race(a2, LOCKED, k, "WITH a lock: the three steps can't be interleaved", ("final 1300 - correct", GREEN))
    L.animate(fig, upd, len(frames), "race", fps=1)

# ---------------------------------------------------------------- 2. a real measurement: how often does it bite?
if L.wanted("race_measured"):
    import random
    import threading
    import time

    def run(p_switch, lock):
        state = {"score": 0}
        lk = threading.Lock()

        def work():
            for _ in range(3000):
                if lock:
                    lk.acquire()
                v = state["score"]
                if random.random() < p_switch:
                    time.sleep(0)
                state["score"] = v + 1
                if lock:
                    lk.release()
        ts = [threading.Thread(target=work) for _ in range(4)]
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        return 12000 - state["score"]

    ps = [0.0, 0.0001, 0.001, 0.01, 0.1]
    lost = [np.mean([run(p, False) for _ in range(3)]) for p in ps]
    locked = [np.mean([run(p, True) for _ in range(3)]) for p in ps]
    fig, ax = plt.subplots(figsize=(12, 4.8))
    x = np.arange(len(ps))
    ax.bar(x - 0.2, lost, 0.4, color=RED, label="no lock")
    ax.bar(x + 0.2, locked, 0.4, color=GREEN, label="with lock")
    for i, v in enumerate(lost):
        ax.text(i - 0.2, v + 150, f"{v:,.0f}", ha="center", fontsize=11)
    ax.set_xticks(x, [f"{p:g}" for p in ps])
    ax.set_xlabel("how often a thread switch lands between READ and WRITE")
    ax.set_ylabel("lost points (of 12,000)")
    ax.set_title("4 threads × 3,000 points, measured on this computer (race_demo.py)")
    ax.legend()
    print("  lost:", [round(v) for v in lost], " locked:", locked)
    caption(fig, "With rare switches the bug is rare - your tests pass and it fails in the classroom.  "
                 "With the lock: 0, always.")
    L.save(fig, "race_measured")

# ---------------------------------------------------------------- 3. deadlock and why one lock avoids it
if L.wanted("deadlock"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 5.4))
    blank(a1)
    box(a1, 0.05, 0.6, 0.3, 0.2, "thread A\nholds lock 1\nwaits for lock 2", color=BLUE, fill=LIGHT_BLUE)
    box(a1, 0.65, 0.6, 0.3, 0.2, "thread B\nholds lock 2\nwaits for lock 1", color=ORANGE, fill=LIGHT_ORANGE)
    box(a1, 0.38, 0.85, 0.24, 0.1, "lock 1", color=INK2)
    box(a1, 0.38, 0.4, 0.24, 0.1, "lock 2", color=INK2)
    arrow(a1, (0.2, 0.8), (0.38, 0.9), text="holds", fontsize=10)
    arrow(a1, (0.35, 0.65), (0.42, 0.5), color=RED, text="waits", fontsize=10)
    arrow(a1, (0.8, 0.6), (0.62, 0.45), text="holds", fontsize=10)
    arrow(a1, (0.65, 0.75), (0.58, 0.85), color=RED, text="waits", fontsize=10)
    a1.text(0.5, 0.15, "DEADLOCK: both wait forever.  The game freezes, no error.", ha="center", fontsize=13,
            color=RED, weight="bold")
    a1.set_title("two locks, taken in opposite order", fontsize=13)
    blank(a2)
    box(a2, 0.3, 0.55, 0.4, 0.25, "ONE lock\naround the whole game state\n(players, scores, state)",
        color=GREEN, fill="#d5ecd5", weight="bold")
    a2.text(0.5, 0.35, "every handler: with self._lock: …  - short, then release", ha="center", fontsize=12)
    a2.text(0.5, 0.22, "and ALWAYS `with`: released even if an exception happens", ha="center", fontsize=12)
    a2.set_title("LanGame: ONE lock → no deadlock", fontsize=13)
    L.save(fig, "deadlock")

# ---------------------------------------------------------------- 4. don't hold the lock while doing slow things
if L.wanted("hold_short"):
    fig, axes = plt.subplots(2, 1, figsize=(13, 5.6), sharex=True)
    for ax, title, spans in [
            (axes[0], "WRONG: send to 10 clients while holding the lock - every other thread waits",
             [("A", 0, 2, "update", ORANGE), ("A", 2, 32, "send to 10 sockets (slow)", RED),
              ("B", 0, 32, "waiting for the lock …", GRID), ("B", 32, 34, "update", ORANGE)]),
            (axes[1], "RIGHT: update under the lock, copy what to send, release, THEN send",
             [("A", 0, 2, "update + copy", ORANGE), ("A", 2, 32, "send (no lock)", BLUE),
              ("B", 2, 4, "update", ORANGE), ("B", 4, 34, "send (no lock)", BLUE)])]:
        for who, a, b, what, col in spans:
            y = 1 if who == "A" else 0
            ax.barh(y, b - a, left=a, color=col, height=0.6)
            ax.text(a + (b - a) / 2, y, what, ha="center", va="center", fontsize=10.5,
                    color="white" if col in (RED, BLUE, ORANGE) else INK2)
        ax.set_yticks([1, 0], ["thread A", "thread B"])
        ax.set_title(title, fontsize=12.5)
    axes[1].set_xlabel("milliseconds")
    L.save(fig, "hold_short")

# ---------------------------------------------------------------- 5. threads and Tkinter: the queue
if L.wanted("tk_queue"):
    fig, ax = plt.subplots(figsize=(14, 4.8))
    blank(ax)
    box(ax, 0.02, 0.35, 0.22, 0.3, "reader thread\nrecv() → feed() → Message", color=AQUA)
    box(ax, 0.38, 0.4, 0.22, 0.2, "queue.Queue\n(thread-safe)", color=VIOLET, weight="bold")
    box(ax, 0.74, 0.35, 0.24, 0.3, "Tkinter main thread\nroot.after(50, poll)\n→ update the widgets", color=BLUE)
    arrow(ax, (0.24, 0.5), (0.38, 0.5), text="put()", fontsize=11)
    arrow(ax, (0.6, 0.5), (0.74, 0.5), text="get_nowait()", fontsize=11)
    ax.text(0.5, 0.12, "Only the main thread may touch Tkinter widgets.  The reader thread never calls them - "
                       "it drops messages into the queue.", ha="center", fontsize=12)
    ax.set_title("The client: network in one thread, GUI in another, a queue between them")
    L.save(fig, "tk_queue")

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 6. LanGame's threads as lanes in time
if L.wanted("thread_lanes"):
    lanes = [("main: accept()", [(0, 1.2, "accept liraz"), (3.0, 0.8, "accept noa"), (6.5, 0.6, "accept dan")], MUTED),
             ("player liraz", [(1.2, 10.8, "waiting in recv() …"), (8.1, 0.4, "ANSWER")], BLUE),
             ("player noa", [(3.8, 8.2, "waiting in recv() …"), (9.6, 0.4, "ANSWER")], AQUA),
             ("player dan", [(7.1, 4.9, "waiting in recv() …"), (11.2, 0.4, "ANSWER")], VIOLET),
             ("timer (15 s)", [(5.0, 7.0, "sleeping until the question closes …")], YELLOW)]
    fig, ax = plt.subplots(figsize=(14, 4.8))
    for i, (name, bars, col) in enumerate(lanes):
        y = len(lanes) - 1 - i
        for start, dur, label in bars:
            busy = label.isupper() or label.startswith("accept")
            ax.add_patch(plt.Rectangle((start, y - 0.32), dur, 0.64, fc=col if busy else PAPER, ec=col, lw=2,
                                       hatch=None if busy else "///", zorder=2 if busy else 1))
            ax.text(start + dur / 2 if busy else start + 0.15, y, label, ha="center" if busy else "left", va="center",
                    fontsize=10, weight="bold" if busy else "normal", zorder=3,
                    bbox=None if busy else dict(fc=PAPER, ec="none", pad=1))
        ax.text(-0.2, y, name, ha="right", va="center", fontsize=11)
    for t, lab in [(8.1, "lock"), (9.6, "lock"), (11.2, "lock")]:
        ax.annotate("", (t + 0.2, 4.55), (t + 0.2, 4.95), arrowprops=dict(arrowstyle="->", color=RED))
    ax.text(9.6, 4.98, "each ANSWER updates the shared scores → inside `with self._lock:`", ha="center", fontsize=11,
            color=RED)
    ax.set_xlim(-3.2, 12.5)
    ax.set_ylim(-0.6, 5.3)
    ax.set_yticks([])
    ax.set_xlabel("seconds")
    ax.set_title("LanGame's server: five threads at the same time - most of them just WAITING (striped)", fontsize=13)
    L.save(fig, "thread_lanes")

# ---------------------------------------------------------------- 7. locks and deadlocks in the real world
if L.wanted("locks_world"):
    tiles = [("Single-track railway", "only the train holding the TOKEN\nmay enter the track", "a lock", BLUE),
             ("One-person toilet", "the door lock: occupied / free", "a lock", AQUA),
             ("Shared online document", "two people typing in the same sentence", "a race condition", ORANGE),
             ("Gridlocked crossing", "four cars, each waiting\nfor the one on its right", "a deadlock", RED),
             ("Corridor dance", "two people step aside to the\nsame side, again and again", "a livelock", VIOLET),
             ("Ticket sale", "two people buy the last seat\nat the same moment", "a race (needs a lock)", GREEN)]
    fig, axes = plt.subplots(2, 3, figsize=(15, 6.2))
    for ax, (title, what, name, col) in zip(axes.ravel(), tiles):
        blank(ax)
        ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0,rounding_size=0.05", lw=2.5,
                                    edgecolor=col, facecolor=PAPER))
        ax.add_patch(FancyBboxPatch((0.02, 0.74), 0.96, 0.24, boxstyle="round,pad=0,rounding_size=0.05", lw=0,
                                    facecolor=col))
        ax.text(0.5, 0.86, title, ha="center", va="center", color="white", fontsize=13.5, weight="bold")
        ax.text(0.5, 0.48, what, ha="center", fontsize=11, wrap=True)
        ax.text(0.5, 0.18, name, ha="center", fontsize=13, weight="bold", color=col)
    fig.suptitle("Races, locks and deadlocks outside computers", fontsize=14, weight="bold")
    L.save(fig, "locks_world")
