# Chapter 6 — Algorithm 4: the booking's life cycle

💡 **In short:** a booking is not a row you may edit freely. It is a **finite state machine** with four
states and three legal transitions, each with a condition. Illegal moves are impossible, not merely unlikely.

## 6.1 The problem

Without rules, a receptionist could check out a guest who never arrived, cancel someone already
sleeping in the room, or check in a week early. Writing those as scattered `if`s means the twentieth
one contradicts the third.

## 6.2 The machine

```
                 create_booking (room free + price quoted)
                                 │
                                 ▼
                          ┌─────────────┐
      cancel              │  CONFIRMED  │   check_in  [today ≥ check-in date]
  [before check-in]  ◄────┤ blocks room ├────►  ┌────────────┐
  fee 0 or 1 night        └─────────────┘       │ CHECKED_IN │ blocks room
           │                                     └─────┬──────┘
           ▼                                           │ check_out / invoice
     ┌───────────┐                                     ▼
     │ CANCELLED │  frees the room            ┌──────────────┐
     └───────────┘                            │ CHECKED_OUT  │ frees the room
                                              └──────────────┘
```

| From | Event | Guard (condition) | Action | To |
|---|---|---|---|---|
| CONFIRMED | check in | `today ≥ check-in` | stamp the time | CHECKED_IN |
| CHECKED_IN | check out | — | build the invoice (one transaction) | CHECKED_OUT |
| CONFIRMED | cancel | before check-in | compute the fee | CANCELLED |

Anything else → a clear error message saying *why*.

## 6.3 The elegant part — the state drives availability

`BookingStatus.blocks_room` is `True` only for CONFIRMED and CHECKED_IN, and the availability
algorithm (chapter 3) asks nothing else:

```python
if not booking.status.blocks_room:
    continue          # cancelled and checked-out bookings are invisible to availability
```
So **cancelling frees the room instantly** — no deletion, no special case, no lost history. One
property links algorithm 4 to algorithm 1. Point at this line in the defense; it is a design decision,
not an accident.

## 6.4 How a guarded transition is written

```python
def check_in(self, booking_id, today=None):
    today = today or date.today()
    booking = self.bookings.get(booking_id)
    if booking is None:
        raise HotelError("Booking not found")
    if booking.status is not BookingStatus.CONFIRMED:                 # state guard
        raise HotelError(f"Cannot check in a booking that is {booking.status.value}")
    if today < booking.stay.check_in:                                 # business guard
        raise HotelError(f"Too early - check-in is on {booking.stay.check_in}")
    booking.status = BookingStatus.CHECKED_IN                         # the transition
    booking.checked_in_at = datetime.now()
    self.bookings.update(booking)
    return booking
```
**Always the same shape:** load → check the state → check the business condition → change the state →
stamp the time → save → return. Write the other two transitions in exactly this shape.

💡 `today=None` defaulting to `date.today()` lets the tests say "pretend it is 3 March" without
waiting for March. Designing for testability deserves a sentence in your book.

## 6.5 Two details worth defending

**The cancellation fee lives in the pricing engine**, not in the service — because it is a *price*, and
every price lives in one place: free up to 48 hours before arrival, otherwise one night of the room part.

**The invoice is written in one transaction**: the invoice row and all its lines inside a single
`with self.db.connection():`. If line 10 fails, the rollback removes the whole invoice. A half-invoice
would be worse than none — that is **atomicity**, the A of ACID.

## ✅ Check yourself — Chapter 6

1. Draw the machine with the guards. Which transitions are deliberately missing (e.g. CHECKED_OUT → anything)?
2. A guest is CHECKED_IN and asks to cancel. What does the program do, and where exactly?
3. How does cancelling free the room? Quote the line.
4. Why does `check_in` accept a `today` parameter?
5. Why is the cancellation fee not in `HotelService`?
6. Why must the invoice and its lines be written together?

## 📚 Further reading

- Gamma et al. (1994). *Design Patterns* — State, Strategy, Facade.
- SQLite — transactions and ACID: https://www.sqlite.org/transactional.html
