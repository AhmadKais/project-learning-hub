"""Live demo for the class: a real race condition, and the lock that fixes it.

    python race_demo.py            # 4 threads each add 1 to a shared score 10,000 times - without a lock
    python race_demo.py --lock     # the same, with `with lock:` around the read-add-write

`score += 1` is really READ, ADD, WRITE.  The occasional sleep(0) between them lets Python switch threads at
the worst moment - which a busy real server does by itself, just less often (and that is worse: the bug
appears once in a thousand games).
"""
import random
import sys
import threading
import time

USE_LOCK = "--lock" in sys.argv
THREADS, ADDS = 4, 10_000


class Game:
    def __init__(self):
        self.score = 0
        self.lock = threading.Lock()

    def add_point(self):
        if USE_LOCK:
            with self.lock:                  # only one thread at a time in here
                self._read_add_write()
        else:
            self._read_add_write()

    def _read_add_write(self):
        value = self.score                   # READ
        if random.random() < 0.02:           # now and then a thread switch happens right here
            time.sleep(0)
        self.score = value + 1               # ADD + WRITE


def run_once():
    game = Game()
    workers = [threading.Thread(target=lambda: [game.add_point() for _ in range(ADDS)]) for _ in range(THREADS)]
    for w in workers:
        w.start()
    for w in workers:
        w.join()
    return game.score


if __name__ == "__main__":
    expected = THREADS * ADDS
    for trial in range(1, 4):
        got = run_once()
        print(f"trial {trial}: score = {got:6,}   expected {expected:,}   lost updates: {expected - got:,}")
