Run it from the project folder:

```
pytest -q          # 49 passed
python run.py      # Rooms tab -> "Import sample data" loads 24 rooms and 10 guests
```

What the finished project does:

- search free rooms for dates and guests, each with its price; preview the quote line by line; book a chosen room or let the allocation strategy pick one
- check in (not before the date), check out with an invoice that can be saved as CSV, cancel (free up to 48 hours before, then one night)
- the calendar shows every room and day in colour; clicking a booking opens it
- the reports tab shows occupancy and revenue per month; the top line shows today's arrivals, departures and free rooms
- the guide's worked example costs exactly 4,445.06 (see the quote in the screenshot)
