"""LanGame - solutions to exercises.py.

Try first. Then compare: there is more than one correct way to write each one.
To run the tests against these solutions:  EXERCISES=solutions pytest test_exercises.py
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


def ex01_to_wire(type_, payload=None):
    text = json.dumps({"type": type_, "payload": payload or {}}, ensure_ascii=False)
    return (text + "\n").encode("utf-8")


def ex02_from_wire(line):
    try:
        data = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProtocolError("bad_json") from None
    if not isinstance(data, dict) or data.get("type") not in MESSAGE_TYPES:
        raise ProtocolError("unknown_type")
    if not isinstance(data.get("payload"), dict):
        raise ProtocolError("bad_payload")
    return data["type"], data["payload"]


class Ex03MessageBuffer:
    def __init__(self):
        self._buffer = b""

    def feed(self, data):
        self._buffer += data
        lines = []
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            if line.strip():
                lines.append(line)
        if len(self._buffer) > MAX_MESSAGE_BYTES:
            self._buffer = b""
            raise ProtocolError("too_large")
        return lines


class Ex04SafeScore:
    def __init__(self):
        self._lock = threading.Lock()
        self._value = 0

    def add(self, points):
        with self._lock:
            self._value += points

    @property
    def value(self):
        with self._lock:
            return self._value


class Ex05Round:
    def __init__(self):
        self._lock = threading.Lock()
        self.state = "QUESTION"
        self.times_closed = 0

    def close(self):
        with self._lock:
            if self.state != "QUESTION":
                return False
            self.state = "SCORING"
            self.times_closed += 1
            return True


def ex06_snapshot_then_send(lock, handlers, send):
    with lock:
        targets = list(handlers)
    for h in targets:
        send(h)
    return len(targets)


def ex07_points_for(is_correct, response_time, time_limit=15.0, max_points=1000, min_correct=100):
    if not is_correct:
        return 0
    t = min(max(response_time, 0.0), time_limit)
    return max(min_correct, round(max_points * (time_limit - t) / time_limit))


def ex08_leaderboard(scores):
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(i + 1, name, score) for i, (name, score) in enumerate(ranked)]


def ex09_prepare(ids, n, seed=None):
    ids = list(ids)
    if len(ids) < n:
        raise ValueError(f"only {len(ids)} questions available, {n} needed")
    random.Random(seed).shuffle(ids)
    return ids[:n]


ALLOWED = {
    "LOBBY": {"JOIN", "LEAVE", "START_GAME"},
    "QUESTION": {"ANSWER", "LEAVE"},
    "SCORING": {"LEAVE"},
    "GAME_OVER": {"LEAVE"},
}


def ex10_check_allowed(state, message_type):
    if message_type in ALLOWED.get(state, set()):
        return None
    if message_type == "ANSWER":
        return "not_accepting"
    if message_type == "JOIN":
        return "game_started"
    return "not_allowed"


def ex11_public_question(question):
    return {k: v for k, v in question.items() if k != "correct_index"}


def ex12_read_all_messages(sock):
    buffer, out = Ex03MessageBuffer(), []
    while True:
        chunk = sock.recv(4096)
        if chunk == b"":
            return out
        for line in buffer.feed(chunk):
            try:
                out.append(ex02_from_wire(line))
            except ProtocolError:
                continue
