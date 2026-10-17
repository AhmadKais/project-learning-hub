"""Lesson 30 - finite state machines: the hotel booking life cycle and the LanGame server, plus time-based scoring."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403
from matplotlib.patches import FancyArrowPatch

L = Lesson(__file__)


def draw_fsm(ax, states, edges, current=None, flash=None, note=None, title=""):
    """states: {name: (x, y, colour)}; edges: [(from, to, label, rad)]."""
    blank(ax, (0, 1.7), (0, 1))
    for a, b, label, rad in edges:
        (x1, y1, _), (x2, y2, _) = states[a], states[b]
        hot = flash == (a, b)
        p = FancyArrowPatch((x1, y1), (x2, y2), connectionstyle=f"arc3,rad={rad}", arrowstyle="-|>", mutation_scale=20,
                            lw=3 if hot else 1.8, color=ORANGE if hot else INK2, shrinkA=48, shrinkB=48)
        ax.add_patch(p)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        dx, dy = y2 - y1, x1 - x2
        ax.text(mx + rad * dx * 0.55, my + rad * dy * 0.55, label, ha="center", va="center", fontsize=10.5,
                color=ORANGE if hot else INK2, bbox=dict(fc=PAPER, ec="none", pad=1))
    for name, (x, y, col) in states.items():
        on = name == current
        ax.add_patch(plt.Circle((x, y), 0.1, color=col if on else PAPER, ec=col, lw=3, zorder=3))
        ax.text(x, y, name.replace("_", "\n"), ha="center", va="center", fontsize=10.5, weight="bold",
                color="white" if on else INK, zorder=4)
    if note:
        ax.text(0.85, 0.02, note[0], ha="center", fontsize=13, color=note[1], weight="bold")
    ax.set_title(title, fontsize=13)
    ax.set_aspect("equal")


# ---------------------------------------------------------------- 1. the hotel booking
BSTATES = {"CONFIRMED": (0.3, 0.72, BLUE), "CHECKED_IN": (0.85, 0.72, ORANGE), "CHECKED_OUT": (1.4, 0.72, GREEN),
           "CANCELLED": (0.3, 0.27, MUTED)}
BEDGES = [("CONFIRMED", "CHECKED_IN", "check_in\n[today ≥ check-in]", 0.0),
          ("CHECKED_IN", "CHECKED_OUT", "check_out\n→ invoice", 0.0),
          ("CONFIRMED", "CANCELLED", "cancel\n[before check-in]\nfee 0 or 1 night", 0.0)]
if L.wanted("booking_fsm"):
    story = [("CONFIRMED", None, ("create_booking: room free + price quoted  →  CONFIRMED  (blocks the room)", INK)),
             ("CONFIRMED", ("CONFIRMED", "CHECKED_IN"), ("check_in on the arrival day", ORANGE)),
             ("CHECKED_IN", None, ("CHECKED_IN  (still blocks the room)", INK)),
             ("CHECKED_IN", None, ("cancel now?  ✗  'Cannot cancel: the guest has already checked in'", RED)),
             ("CHECKED_IN", ("CHECKED_IN", "CHECKED_OUT"), ("check_out → build the invoice in ONE transaction", ORANGE)),
             ("CHECKED_OUT", None, ("CHECKED_OUT: blocks_room = False → the room is free for the next guest", GREEN)),
             ("CHECKED_OUT", None, ("check_in again?  ✗  no arrow leaves CHECKED_OUT", RED))]
    fig, ax = plt.subplots(figsize=(14, 7.4))
    frames = [i for i in range(len(story)) for _ in range(2)]
    L.animate(fig, lambda f: draw_fsm(ax, BSTATES, BEDGES, story[frames[f]][0], story[frames[f]][1], story[frames[f]][2],
                                      "HotelManager: a booking's life cycle"), len(frames), "booking_fsm", fps=1)

# ---------------------------------------------------------------- 2. the LanGame server
GSTATES = {"LOBBY": (0.25, 0.7, BLUE), "QUESTION": (0.85, 0.7, ORANGE), "SCORING": (1.45, 0.7, VIOLET),
           "GAME_OVER": (0.85, 0.25, GREEN)}
GEDGES = [("LOBBY", "QUESTION", "START_GAME\n[host, ≥ 2 players]", 0.0),
          ("QUESTION", "SCORING", "time up / all answered", 0.35),
          ("SCORING", "QUESTION", "more questions", 0.35),
          ("SCORING", "GAME_OVER", "last question", 0.0),
          ("GAME_OVER", "LOBBY", "reset", 0.0)]
if L.wanted("game_fsm"):
    story = [("LOBBY", None, ("players JOIN; an ANSWER now → ERROR not_accepting", INK)),
             ("LOBBY", ("LOBBY", "QUESTION"), ("host sends START_GAME with 3 players", ORANGE)),
             ("QUESTION", None, ("QUESTION 1 broadcast; Timer(15 s) started; ANSWERs recorded once each", INK)),
             ("QUESTION", ("QUESTION", "SCORING"), ("everyone answered at 5.874 s → close early, cancel the timer", ORANGE)),
             ("SCORING", None, ("score_round(); broadcast RESULT + LEADERBOARD; an ANSWER now is 'too late'", INK)),
             ("SCORING", ("SCORING", "QUESTION"), ("Timer(4 s) → next question", ORANGE)),
             ("QUESTION", None, ("… the last question …", INK)),
             ("QUESTION", ("QUESTION", "SCORING"), ("15 s timer fires: whoever didn't answer gets 0", ORANGE)),
             ("SCORING", ("SCORING", "GAME_OVER"), ("no more questions → GAME_OVER, save the game", ORANGE)),
             ("GAME_OVER", None, ("GAME_OVER: everything except LEAVE is rejected", GREEN))]
    fig, ax = plt.subplots(figsize=(14, 7.4))
    frames = [i for i in range(len(story)) for _ in range(2)]
    L.animate(fig, lambda f: draw_fsm(ax, GSTATES, GEDGES, story[frames[f]][0], story[frames[f]][1], story[frames[f]][2],
                                      "LanGame: the server's game state"), len(frames), "game_fsm", fps=1)

# ---------------------------------------------------------------- 3. the transition table (LanGame)
if L.wanted("transition_table"):
    states = ["LOBBY", "QUESTION", "SCORING", "GAME_OVER"]
    events = ["JOIN", "START_GAME", "ANSWER", "LEAVE"]
    table = {("LOBBY", "JOIN"): "ok", ("LOBBY", "START_GAME"): "→ QUESTION\n(host, ≥ 2)", ("LOBBY", "ANSWER"): "not_accepting",
             ("LOBBY", "LEAVE"): "ok", ("QUESTION", "JOIN"): "game_started", ("QUESTION", "START_GAME"): "rejected",
             ("QUESTION", "ANSWER"): "ok once\n(2nd: already_answered)", ("QUESTION", "LEAVE"): "ok",
             ("SCORING", "JOIN"): "game_started", ("SCORING", "START_GAME"): "rejected",
             ("SCORING", "ANSWER"): "not_accepting\n(too late)", ("SCORING", "LEAVE"): "ok",
             ("GAME_OVER", "JOIN"): "rejected", ("GAME_OVER", "START_GAME"): "rejected",
             ("GAME_OVER", "ANSWER"): "rejected", ("GAME_OVER", "LEAVE"): "ok"}
    fig, ax = plt.subplots(figsize=(13, 5.6))
    blank(ax, (0, 5), (0, 5))
    for j, e in enumerate(events):
        ax.text(j + 1.5, 4.5, e, ha="center", fontsize=13, weight="bold")
    for i, s in enumerate(states):
        y = 3.5 - i
        ax.text(0.95, y + 0.5, s, ha="right", va="center", fontsize=12.5, weight="bold")
        for j, e in enumerate(events):
            v = table[(s, e)]
            good = v.startswith("ok") or v.startswith("→")
            ax.add_patch(plt.Rectangle((j + 1.03, y + 0.05), 0.94, 0.9, color="#d5ecd5" if good else "#f8d6d6"))
            ax.text(j + 1.5, y + 0.5, v, ha="center", va="center", fontsize=10.5, color=GREEN if good else RED)
    ax.set_title("Every command starts with ONE question: 'is this allowed in the current state?'", fontsize=13)
    L.save(fig, "transition_table")

# ---------------------------------------------------------------- 4. time-based scoring (LanGame)
if L.wanted("scoring"):
    MAX, LIMIT, MIN = 1000, 15, 100

    def points(t, correct=True):
        if not correct:
            return 0
        t = min(max(t, 0), LIMIT)
        return max(MIN, round(MAX * (LIMIT - t) / LIMIT))

    ts = np.linspace(0, 15, 301)
    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.plot(ts, [points(t) for t in ts], color=ORANGE, lw=3, label="correct answer")
    ax.plot(ts, [0] * len(ts), color=BLUE, lw=3, label="wrong / no answer")
    for t in (0, 3, 7.5, 14.9):
        ax.plot(t, points(t), "o", color=INK, ms=8)
        ax.annotate(f"{t:g} s → {points(t)}", (t, points(t)), xytext=(t + 0.3, points(t) + 70), fontsize=11.5)
    ax.axhline(MIN, color=MUTED, ls="--", lw=1)
    ax.text(10.3, MIN + 20, "floor: a correct answer always gets ≥ 100", fontsize=11, color=INK2)
    ax.set_xlabel("response time (seconds, measured on the SERVER clock)")
    ax.set_ylabel("points")
    ax.set_title("points = round(1000 × (15 − t) / 15), never below 100 if correct  —  every second costs ~67 points")
    ax.legend(loc="upper right")
    L.save(fig, "scoring")

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 5. state machines in everyday life
if L.wanted("fsm_world"):
    tiles = [("Traffic light", "red → green → yellow → red", "no arrow red → yellow"),
             ("Vending machine", "waiting → paid → giving drink → waiting", "'give drink' while waiting: impossible"),
             ("Washing machine", "filling → washing → rinsing → spinning", "door locked in every state but 'done'"),
             ("Phone call", "ringing → talking → ended", "you can't 'hang up' a call that ended"),
             ("Lift (elevator)", "doors open → closed → moving → stopped", "never 'moving' with doors open"),
             ("Turnstile", "locked → (coin) unlocked → (push) locked", "push while locked: nothing happens")]
    fig, axes = plt.subplots(2, 3, figsize=(15, 6.2))
    for ax, (title, states, rule), col in zip(axes.ravel(), tiles, SERIES):
        blank(ax)
        ax.add_patch(FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0,rounding_size=0.05", lw=2.5,
                                    edgecolor=col, facecolor=PAPER))
        ax.add_patch(FancyBboxPatch((0.02, 0.74), 0.96, 0.24, boxstyle="round,pad=0,rounding_size=0.05", lw=0,
                                    facecolor=col))
        ax.text(0.5, 0.86, title, ha="center", va="center", color="white", fontsize=14, weight="bold")
        ax.text(0.06, 0.52, states, fontsize=11)
        ax.text(0.06, 0.24, rule, fontsize=11, weight="bold", color=col)
    fig.suptitle("You live among state machines: one state at a time, only some arrows", fontsize=14, weight="bold")
    L.save(fig, "fsm_world")

# ---------------------------------------------------------------- 6. three booleans vs one Enum
if L.wanted("booleans_vs_enum"):
    import itertools
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5.4), gridspec_kw={"width_ratios": [1.5, 1]})
    blank(a1)
    a1.text(0.02, 0.94, "is_checked_in   is_checked_out   is_cancelled", fontsize=12, family="monospace", weight="bold")
    legal = {(0, 0, 0): "CONFIRMED", (1, 0, 0): "CHECKED_IN", (1, 1, 0): "CHECKED_OUT", (0, 0, 1): "CANCELLED"}
    for i, combo in enumerate(itertools.product([0, 1], repeat=3)):
        y = 0.83 - i * 0.1
        ok = combo in legal
        txt = "      ".join(f"{'True ' if v else 'False'}" for v in combo)
        a1.text(0.04, y, txt, fontsize=12, family="monospace", color=INK if ok else MUTED)
        a1.text(0.72, y, legal.get(combo, "nonsense!"), fontsize=12, color=GREEN if ok else RED, weight="bold")
    a1.set_title("3 booleans = 8 combinations - only 4 make sense", fontsize=13)
    blank(a2)
    for i, (name, col) in enumerate([("CONFIRMED", BLUE), ("CHECKED_IN", AQUA), ("CHECKED_OUT", MUTED),
                                     ("CANCELLED", RED)]):
        box(a2, 0.15, 0.75 - i * 0.2, 0.7, 0.13, f"BookingStatus.{name}", color=col, fontsize=12)
    a2.set_title("1 Enum = exactly the 4 legal states", fontsize=13)
    L.save(fig, "booleans_vs_enum")
