# Chapter 2 — The Python you need for this project

You know `if`, `for`, functions and lists. These seven things appear all over the skeleton. Try each
example in a terminal (`python`, then type) before you start stage 1 — twenty minutes now saves days later.

## 2.1 `dataclass` — a class that is mostly data

📄
```python
from dataclasses import dataclass

@dataclass
class Room:
    number: str
    capacity: int
    floor: int = 1          # a default value

r = Room("102", 2)
r.capacity          # 2
r                   # Room(number='102', capacity=2, floor=1)   <- printing works for free
```
Without `@dataclass` you would write `__init__`, `__repr__` and `__eq__` by hand. `Room`, `Guest`,
`Booking`, `InvoiceLine` in `models/entities.py` are all dataclasses. You do not write them — you use them.

## 2.2 `frozen=True` — a value that cannot change

📄
```python
@dataclass(frozen=True)
class DateRange:
    check_in: date
    check_out: date

stay = DateRange(date(2026,3,3), date(2026,3,7))
stay.check_in = date(2026,3,4)      # FrozenInstanceError - refused
```
Why: a `DateRange` is a *value*, like the number 5. If a booking could quietly change its dates, an
availability check made a second earlier would silently become wrong. Frozen = the bug is impossible.

## 2.3 `__post_init__` — validating at birth

📄
```python
@dataclass(frozen=True)
class DateRange:
    check_in: date
    check_out: date
    def __post_init__(self):                  # runs immediately after the object is created
        if self.check_out <= self.check_in:
            raise ValueError("check-out must be after check-in")
```
Now **an invalid range cannot exist anywhere in the program**, so no other function ever has to check.
That idea has a name — *make illegal states unrepresentable* — and it is worth saying in the defense.

## 2.4 `Enum` — a fixed list of values

📄
```python
from enum import Enum

class BookingStatus(str, Enum):
    CONFIRMED  = "confirmed"
    CHECKED_IN = "checked_in"

BookingStatus.CONFIRMED.value      # 'confirmed'      <- what goes in the database
BookingStatus("confirmed")         # BookingStatus.CONFIRMED   <- reading it back
status is BookingStatus.CONFIRMED  # compare with `is`, not ==
```
Why not plain strings: a typo like `"confimed"` would silently break a comparison; with an enum it is
an immediate error. The database `CHECK (status IN (...))` guards the same thing from the other side.

## 2.5 `ABC` and `@abstractmethod` — an interface

📄
```python
from abc import ABC, abstractmethod

class AllocationStrategy(ABC):
    @abstractmethod
    def choose(self, candidates, guests, preferences): ...

class BestFitStrategy(AllocationStrategy):
    def choose(self, candidates, guests, preferences):
        return min(candidates, key=lambda r: r.capacity)

AllocationStrategy()      # TypeError - you cannot create the abstract class
```
This is how the Strategy pattern is written in Python: the base class *promises* a method, every
subclass *provides* it, and the rest of the program only knows the promise.

## 2.6 Generators — `yield` one item at a time

📄
```python
def nights_list(self):
    day = self.check_in
    while day < self.check_out:
        yield day
        day += timedelta(days=1)

for night in stay.nights_list():        # works like a list
    print(night)
list(stay.nights_list())                # turn it into a real list when you need one
```
The pricing engine walks the nights one by one; the calendar needs them too. Writing the loop once,
inside `DateRange`, means "which nights?" is answered in exactly one place in the project.

## 2.7 `@contextmanager` — code that always cleans up

📄
```python
from contextlib import contextmanager

@contextmanager
def connection(self):
    conn = self.get_connection()
    try:
        yield conn            # <- the body of the `with` block runs here
        conn.commit()         # reached only if the body finished without an exception
    except Exception:
        conn.rollback()       # any error -> undo everything
        raise
    finally:
        conn.close()          # always, error or not

with db.connection() as conn:
    conn.execute("INSERT ...")
    conn.execute("INSERT ...")      # if this fails, the first INSERT is undone too
```
This is how the whole project gets **transactions** for free. Understand these eight lines — they are
chapter 13 of your book (atomicity).

## 2.8 Reading a traceback

📄
```
Traceback (most recent call last):
  File "run.py", line 20, in main
    AppController(root).start()
  File ".../app_controller.py", line 60, in start
    self.refresh_rooms()
  File ".../repositories.py", line 44, in list_all
    return [self._row(r) for r in rows]
  File ".../repositories.py", line 30, in _row
    return Room(number=r["number"], capacity=r["capacity"])
KeyError: 'capacity'
```
Read it **bottom up**: the last line says *what* (`KeyError: 'capacity'` — that column is missing from
the row), and the first line *inside your own file* says *where* (`_row`, line 30). The lines above are
just the path that got there. Here: the SELECT did not include the `capacity` column.

## ✅ Check yourself — Chapter 2

1. What does `@dataclass` write for you? Name three methods.
2. Why is `DateRange` frozen but `Booking` is not?
3. Where does `__post_init__` run, and what is the benefit of validating there?
4. Why `status is BookingStatus.CONFIRMED` and not `status == "confirmed"`?
5. What happens if a subclass of `AllocationStrategy` forgets `choose`?
6. Convert `nights_list()` into a list of dates. Why is it a generator in the first place?
7. In the `connection()` context manager, which line runs if the second INSERT raises?
8. In the traceback above, which file and function do you open first?
