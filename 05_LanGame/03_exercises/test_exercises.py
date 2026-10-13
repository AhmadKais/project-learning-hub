"""Automatic checks for exercises.py.   Run:  pytest test_exercises.py -v

Every test is named after its exercise, so  pytest -k ex05  runs just that one.
"""
import importlib
import json
import os
import socket
import threading
import time

import pytest

ex = importlib.import_module(os.environ.get("EXERCISES", "exercises"))


def test_ex01_to_wire():
    assert ex.ex01_to_wire("LEAVE") == b'{"type": "LEAVE", "payload": {}}\n'
    wire = ex.ex01_to_wire("JOIN", {"name": "לירז"})
    assert wire.endswith(b"\n") and wire.count(b"\n") == 1
    assert "לירז".encode("utf-8") in wire                     # not escaped as \\u05dc...
    assert json.loads(wire) == {"type": "JOIN", "payload": {"name": "לירז"}}


@pytest.mark.parametrize("line,code", [
    (b"hello", "bad_json"), (b"\xff\xfe", "bad_json"), (b"[1, 2]", "unknown_type"),
    (b'{"type": "HACK", "payload": {}}', "unknown_type"), (b'{"payload": {}}', "unknown_type"),
    (b'{"type": "ANSWER"}', "bad_payload"), (b'{"type": "JOIN", "payload": "x"}', "bad_payload")])
def test_ex02_from_wire_rejects(line, code):
    with pytest.raises(ex.ProtocolError) as err:
        ex.ex02_from_wire(line)
    assert err.value.code == code


def test_ex02_from_wire_accepts():
    assert ex.ex02_from_wire(b'{"type": "ANSWER", "payload": {"question_id": 3, "choice": 1}}') == \
        ("ANSWER", {"question_id": 3, "choice": 1})


def test_ex03_framing_any_cut():
    stream = ex.ex01_to_wire("JOIN", {"name": "a"}) + ex.ex01_to_wire("ANSWER", {"choice": 2}) + ex.ex01_to_wire("LEAVE")
    for cut in range(1, len(stream)):
        b = ex.Ex03MessageBuffer()
        lines = b.feed(stream[:cut]) + b.feed(stream[cut:])
        assert len(lines) == 3, f"cut at {cut}"
        assert json.loads(lines[1])["type"] == "ANSWER"


def test_ex03_one_byte_at_a_time_and_empty_lines():
    b = ex.Ex03MessageBuffer()
    out = []
    for byte in b'\n\n{"type": "LEAVE", "payload": {}}\n':
        out += b.feed(bytes([byte]))
    assert out == [b'{"type": "LEAVE", "payload": {}}']


def test_ex03_too_large():
    b = ex.Ex03MessageBuffer()
    with pytest.raises(ex.ProtocolError) as err:
        b.feed(b"x" * (ex.MAX_MESSAGE_BYTES + 1))
    assert err.value.code == "too_large"
    assert b.feed(b'{"a": 1}\n') == [b'{"a": 1}']              # usable again afterwards


def test_ex04_no_points_lost():
    s = ex.Ex04SafeScore()
    def work():
        for _ in range(2000):
            s.add(5)
    threads = [threading.Thread(target=work) for _ in range(8)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert s.value == 8 * 2000 * 5
    assert any(hasattr(v, "acquire") for v in vars(s).values()), "keep a lock as an attribute (threading.Lock)"


def test_ex05_round_closes_once():
    for _ in range(20):
        r = ex.Ex05Round()
        barrier = threading.Barrier(6)
        results = []
        def closer():
            barrier.wait()
            results.append(r.close())
        threads = [threading.Thread(target=closer) for _ in range(6)]
        for t in threads: t.start()
        for t in threads: t.join()
        assert r.state == "SCORING"
        assert r.times_closed == 1
        assert results.count(True) == 1


def test_ex06_does_not_hold_the_lock_while_sending():
    lock = threading.Lock()
    seen = []
    def send(h):
        assert not lock.locked(), "the lock is still held while sending"
        seen.append(h)
    handlers = ["a", "b", "c"]
    assert ex.ex06_snapshot_then_send(lock, handlers, send) == 3
    assert seen == ["a", "b", "c"]


@pytest.mark.parametrize("correct,t,expected", [
    (True, 0.0, 1000), (True, 3.0, 800), (True, 7.5, 500), (True, 14.9, 100), (True, 6.0, 600),
    (True, 20.0, 100), (True, -1.0, 1000), (False, 1.0, 0)])
def test_ex07_points(correct, t, expected):
    assert ex.ex07_points_for(correct, t) == expected


def test_ex08_leaderboard():
    assert ex.ex08_leaderboard({"dana": 800, "omar": 1300, "adam": 800}) == \
        [(1, "omar", 1300), (2, "adam", 800), (3, "dana", 800)]
    assert ex.ex08_leaderboard({}) == []


def test_ex09_prepare():
    ids = list(range(1, 21))
    got = ex.ex09_prepare(ids, 10, seed=3)
    assert len(got) == 10 and len(set(got)) == 10 and set(got) <= set(ids)
    assert ex.ex09_prepare(ids, 10, seed=3) == got                     # same seed, same game
    assert ids == list(range(1, 21))                                   # the input list is untouched
    with pytest.raises(ValueError) as err:
        ex.ex09_prepare([1, 2, 3, 4, 5, 6], 10)
    assert "6" in str(err.value)


@pytest.mark.parametrize("state,msg,expected", [
    ("LOBBY", "JOIN", None), ("LOBBY", "ANSWER", "not_accepting"), ("QUESTION", "ANSWER", None),
    ("QUESTION", "JOIN", "game_started"), ("SCORING", "ANSWER", "not_accepting"),
    ("QUESTION", "START_GAME", "not_allowed"), ("GAME_OVER", "LEAVE", None)])
def test_ex10_check_allowed(state, msg, expected):
    assert ex.ex10_check_allowed(state, msg) == expected


def test_ex11_public_question():
    q = {"question_id": 4, "text": "?", "options": ["a", "b", "c", "d"], "correct_index": 2}
    pub = ex.ex11_public_question(q)
    assert "correct_index" not in pub and pub["options"] == ["a", "b", "c", "d"]
    assert q["correct_index"] == 2                                     # original untouched


def test_ex12_read_all_messages():
    a, b = socket.socketpair()
    def sender():
        a.sendall(b'{"type": "JOIN", "payload": {"name": "x"}}\n{"type": "ANS')
        time.sleep(0.05)
        a.sendall(b'WER", "payload": {"choice": 1}}\ngarbage\n{"type": "LEAVE", "payload": {}}\n')
        a.close()
    threading.Thread(target=sender).start()
    got = ex.ex12_read_all_messages(b)
    b.close()
    assert got == [("JOIN", {"name": "x"}), ("ANSWER", {"choice": 1}), ("LEAVE", {})]
