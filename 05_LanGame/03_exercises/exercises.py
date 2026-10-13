"""LanGame - exercises.

Fill in every function marked TODO. Use only the standard library.
Check yourself after each exercise:

    pytest test_exercises.py -k ex01 -v        # one exercise
    pytest test_exercises.py -v                # all of them

Stuck for more than 20 minutes? Re-read the theory section named in the
docstring, look at the notebook, and only then open solutions.py.
"""
import json
import random
import threading

MESSAGE_TYPES = {"JOIN", "START_GAME", "ANSWER", "LEAVE", "WELCOME", "LOBBY_UPDATE", "COUNTDOWN",
                 "QUESTION", "RESULT", "LEADERBOARD", "GAME_OVER", "ERROR"}
MAX_MESSAGE_BYTES = 64 * 1024


class ProtocolError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code


# ---------------------------------------------------------------- protocol (notebook 01)

def ex01_to_wire(type_, payload=None):
    """bytes on the wire: JSON {"type": ..., "payload": {...}} + "\\n", UTF-8, Hebrew NOT escaped
    (json.dumps(..., ensure_ascii=False)). payload None -> {}.
    Theory 3.3
    """
    raise NotImplementedError("TODO ex01")


def ex02_from_wire(line):
    """One line (bytes, without the "\\n") -> (type, payload).

    Raise ProtocolError with code:
      "bad_json"      not UTF-8 or not valid JSON
      "unknown_type"  not a dict, or "type" missing / not in MESSAGE_TYPES
      "bad_payload"   "payload" missing or not a dict
    Theory 3.4
    """
    raise NotImplementedError("TODO ex02")


class Ex03MessageBuffer:
    """Framing: collect bytes, return complete lines.

    feed(data) -> list of complete lines (bytes, without "\\n"; empty lines skipped).
    If the unfinished part grows beyond MAX_MESSAGE_BYTES: clear it and raise ProtocolError("too_large").
    Theory 2.5
    """

    def __init__(self):
        raise NotImplementedError("TODO ex03")

    def feed(self, data):
        raise NotImplementedError("TODO ex03")


# ---------------------------------------------------------------- threads (notebook 02)

class Ex04SafeScore:
    """A score that many threads may add to at the same time without losing points.
    add(points) and value (a property). Use a threading.Lock. Theory 4.4
    """

    def __init__(self):
        raise NotImplementedError("TODO ex04")

    def add(self, points):
        raise NotImplementedError("TODO ex04")

    @property
    def value(self):
        raise NotImplementedError("TODO ex04")


class Ex05Round:
    """One question round. close() may be called by the timer AND by the last answer, possibly at the same
    time: it must score only ONCE. Return True from the call that actually closed the round, False otherwise.
    Attribute `state` starts as "QUESTION" and becomes "SCORING"; `times_closed` counts real closes.
    Theory 4.7
    """

    def __init__(self):
        raise NotImplementedError("TODO ex05")

    def close(self):
        raise NotImplementedError("TODO ex05")


def ex06_snapshot_then_send(lock, handlers, send):
    """Broadcast pattern: copy `handlers` (a list) while holding `lock`, RELEASE the lock, then call send(h)
    for every handler in the copy. Returns the number of handlers sent to. Theory 4.6
    """
    raise NotImplementedError("TODO ex06")


# ---------------------------------------------------------------- the game (notebook 03)

def ex07_points_for(is_correct, response_time, time_limit=15.0, max_points=1000, min_correct=100):
    """round(max_points * (time_limit - t) / time_limit), with t clamped to [0, time_limit];
    never below min_correct for a correct answer; 0 for a wrong answer. Theory 5.4
    """
    raise NotImplementedError("TODO ex07")


def ex08_leaderboard(scores):
    """scores: {name: score}. -> list of (rank, name, score): highest score first, ties by name (A..Z),
    ranks 1, 2, 3, ... (positions, even for ties). Theory 5.5
    """
    raise NotImplementedError("TODO ex08")


def ex09_prepare(ids, n, seed=None):
    """Pick n DIFFERENT question ids in random order (random.Random(seed).shuffle on a copy).
    Fewer than n ids -> ValueError mentioning how many there are. Theory 5.6
    """
    raise NotImplementedError("TODO ex09")


ALLOWED = {
    "LOBBY": {"JOIN", "LEAVE", "START_GAME"},
    "QUESTION": {"ANSWER", "LEAVE"},
    "SCORING": {"LEAVE"},
    "GAME_OVER": {"LEAVE"},
}


def ex10_check_allowed(state, message_type):
    """None if `message_type` is allowed in `state` (table ALLOWED), otherwise the error code:
    ANSWER outside QUESTION -> "not_accepting";  JOIN outside LOBBY -> "game_started";
    anything else not allowed -> "not_allowed". Theory 5.1
    """
    raise NotImplementedError("TODO ex10")


# ---------------------------------------------------------------- the server (notebook 04)

def ex11_public_question(question):
    """The QUESTION payload sent to players: a copy of `question` (a dict) WITHOUT "correct_index".
    The original dict must not change. Theory 3.3 - why must the answer never travel to the client?
    """
    raise NotImplementedError("TODO ex11")


def ex12_read_all_messages(sock):
    """Read from a connected socket until the other side closes (recv returns b"").
    Use Ex03MessageBuffer for framing and ex02_from_wire for parsing. Return the list of (type, payload)
    of the VALID messages; lines that raise ProtocolError are skipped. Theory 3.1
    """
    raise NotImplementedError("TODO ex12")
