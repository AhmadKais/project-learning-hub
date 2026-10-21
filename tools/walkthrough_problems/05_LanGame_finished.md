Run it from the project folder:

```
pytest -q                 # 29 passed
python run_admin.py       # add questions or import data/questions_seed.csv
python run_server.py      # prints the address players type
python run_client.py      # one window per player (--host <server address>)
```

What the finished project does:

- up to 8 players join a lobby; the first one is the host and starts the game
- each question reaches every player in under 1 ms on one computer; faster correct answers score more (1000 at once, at least 100)
- a player who disconnects does not stop the game; garbage sent to the server gets an ERROR reply and the server keeps running
- after the last question everyone sees the winner, the game is saved, and the admin tool's Games tab lists it
