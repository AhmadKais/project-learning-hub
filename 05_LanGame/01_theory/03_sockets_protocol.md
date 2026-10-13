# Chapter 3 — Sockets in Python and the message protocol

## 3.1 What a socket is

A **socket** is the object Python gives you to talk over the network. Think of it as one end of
a phone line. The server has one special socket that only *answers calls* (the listening socket),
and gets a *new* socket for every player that connects. Each player has one socket.

📄 **The server side — the five calls, in order**
```python
listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # AF_INET = IPv4, SOCK_STREAM = TCP
listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # restart without "address in use"
listener.bind(("0.0.0.0", 5050))                                # claim the port
listener.listen(8)                                              # start answering calls
conn, addr = listener.accept()   # BLOCKS until a client connects; conn = the new socket for that client
```

📄 **The client side — two calls**
```python
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(("192.168.1.20", 5050))   # the handshake happens here
```

📄 **Both sides — sending and receiving**
```python
sock.sendall(b'{"type": "JOIN", "payload": {"name": "liraz"}}\n')   # bytes, not str!
chunk = sock.recv(4096)     # BLOCKS until some bytes arrive; returns b"" when the other side closed
```

Three facts you must know:

- **Sockets carry bytes, not strings.** `"text".encode("utf-8")` before sending,
  `.decode("utf-8")` after receiving. Hebrew questions need UTF-8.
- **`recv(4096)` returns *up to* 4096 bytes** — maybe 5, maybe 4096. Never assume you got one
  whole message (chapter 2.5).
- **`recv()` returning `b""` (empty) means the other side closed the connection.** It is not
  an error and not "no data yet" — it is goodbye. Your loop must `break` on it, or it will spin forever.

## 3.2 Blocking, and why it forces us to use threads

`accept()` and `recv()` **block**: the program stops at that line and waits. If the server called
`recv()` on player A's socket, it would freeze until A sends something — and players B, C, D could
send answers that nobody reads. That is why the server gives **each player its own thread**
(chapter 4): thread A blocks on A's socket, thread B on B's, and nobody waits for anyone else.

`settimeout(1.0)` makes a blocking call give up after 1 second with `socket.timeout`. We use it so
a thread can check "should I still be running?" once a second and exit cleanly on shutdown,
instead of being stuck in `recv()` forever.

## 3.3 Designing the message protocol

A **protocol** is the agreement between client and server: what messages exist, what each one
contains, and who may send it when. Ours is small and written in `protocol.py`:

📄 **One message on the wire**
```text
{"type": "ANSWER", "payload": {"question_id": 17, "choice": 2}}\n
```

- `type` — one of a fixed list (`MessageType`). The receiver switches on it.
- `payload` — a dictionary; its keys depend on the type.
- `\n` — the frame delimiter (chapter 2.5).

📄 **The full message table**
```text
client -> server
  JOIN         {"name": "liraz"}                       ask to enter the lobby
  START_GAME   {}                                      host only
  ANSWER       {"question_id": 17, "choice": 2}        0..3
  LEAVE        {}

server -> client
  WELCOME       {"name", "is_host"}                    you are in
  LOBBY_UPDATE  {"players": [...], "min_players": 2}
  COUNTDOWN     {"seconds": 5}
  QUESTION      {"question_id", "text", "options", "time_limit", "number", "total"}   NO correct answer
  RESULT        {"question_id", "correct_index", "answers": [{name, choice, is_correct, points}]}
  LEADERBOARD   {"entries": [{"rank", "name", "score"}]}
  GAME_OVER     {"winner", "entries"}
  ERROR         {"code": "name_taken", "message": "..."}
```

Why JSON: it is text (you can read it in Wireshark and in the log), every language has a parser,
and adding a field later does not break old code. The price — a few more bytes than a binary format —
is irrelevant for 20 messages per minute.

## 3.4 Never trust the other side

The server will receive, at some point: invalid JSON, a message with no `type`, a `choice` of 7,
an ANSWER during the lobby, a JOIN with a 500-character name, and 1 MB of garbage from a bored
student with a script. **None of these may crash the server or change the game.** Two layers protect it:

1. **`Message.from_wire()`** checks the *shape*: valid JSON, known type, payload is a dict. Anything
   else raises `ProtocolError` — one exception type, with a short code, that the handler turns into
   an `ERROR` reply.
2. **`GameEngine`** checks the *rules*: is an ANSWER legal now? Is this the current question? Did
   this player already answer? Illegal → `ERROR` reply, state unchanged.

The handler thread's job is to catch `ProtocolError`, reply, and keep serving. Only a closed socket
ends the thread.

❓ **Possible supervisor question: what happens if a client sends `{"type": "ANSWER"}` with no payload?**
`from_wire` raises `ProtocolError("bad_payload")`; the handler sends
`ERROR {"code": "bad_payload"}` back and continues reading. The engine never sees it, so the game
state is untouched. `tests/test_protocol.py::test_malformed_raises_protocol_error` covers five such cases.

## 3.5 Seeing it with Wireshark

Wireshark records every packet on your network card. Run the server and one client, filter with
`tcp.port == 5050`, and you will see: the three handshake packets, then every JSON message as a
packet with its bytes visible in the bottom pane, and the ACK packets the other side sends back.
Right-click a packet → *Follow → TCP Stream* shows the whole conversation as text.

Take three screenshots for the project book: the handshake, one QUESTION packet with its JSON, and
the *Follow TCP Stream* view of a full round. This is your "networks chapter" evidence.

## ✅ Check yourself — Chapter 3

1. Put these in the order the server calls them: `accept`, `bind`, `socket`, `listen`, `recv`.
   Which one gives you the socket you actually talk to a player with?
2. `recv(4096)` returns `b""`. What happened, and what must your code do?
3. Why does the QUESTION message not contain `correct_index`? What could a player do if it did?
4. A client sends `ANSWER` while the game is in LOBBY. Which layer rejects it — `from_wire` or
   `GameEngine` — and why is that the right place?
5. Write the exact bytes (as a Python bytes literal) of a LEAVE message on the wire.
6. In Wireshark you see a QUESTION packet followed by a tiny packet from the client with no data.
   What is the tiny packet?

## 📚 Further reading — Chapter 3

- **Python docs — socket**: https://docs.python.org/3/library/socket.html — `bind`, `listen`, `accept`, `settimeout`, `sendall`.
- **Real Python — Socket Programming in Python**: https://realpython.com/python-sockets/ — a complete
  echo server + client, then a message protocol with a header. Read parts 1–3.
- **Wireshark — User's Guide, "Following streams"**: https://www.wireshark.org/docs/wsug_html_chunked/ChAdvFollowStreamSection.html
- **JSON — the official grammar in one page**: https://www.json.org/
