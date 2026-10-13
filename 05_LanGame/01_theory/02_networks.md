# Chapter 2 — How two computers talk

## 2.1 IP address and port

Every computer on a network has an **IP address** — like a street address: `192.168.1.20`.
But one computer runs many programs (browser, game, Spotify). To reach the *right program*, you also
need a **port** — like an apartment number: a number from 0 to 65535. Our server listens on port
`5050`. The pair `192.168.1.20:5050` is one specific program on one specific computer.

- Ports below 1024 are reserved for well-known services (80 = web, 443 = secure web, 22 = SSH).
- `127.0.0.1` is the "loopback" address: **this computer**. Use it to test the server and clients
  on one machine.
- `0.0.0.0` when *listening* means "accept connections on every network card of this machine"
  (Wi-Fi and cable).

📄 **The pieces of an address**
```text
192.168.1.20 : 5050
^^^^^^^^^^^^   ^^^^
which computer  which program on it
```

## 2.2 Client and server

A **server** is a program that *waits* for connections. A **client** is a program that *starts*
a connection. In LanGame the server waits on port 5050; every player's client connects to it. Once
connected, both sides can send bytes in both directions — the roles only describe who started.

## 2.3 TCP vs. UDP — and why we chose TCP

There are two ways to send data over the internet:

| | TCP | UDP |
|---|---|---|
| Delivery | Guaranteed — lost pieces are resent | Not guaranteed — lost is lost |
| Order | Guaranteed — bytes arrive in the order sent | Not guaranteed |
| Connection | Yes — a "handshake" first, then a stream | No — each packet is on its own |
| Speed | A little slower (acknowledgements) | Faster |
| Used for | Web, email, files, chat | Video calls, online shooters, DNS |

In a trivia game, **every message matters**: a lost question or a lost answer breaks the round. So
we use TCP. The extra few milliseconds do not matter on a local network.

❓ **Possible supervisor question: why do fast online games use UDP, then?**
In a shooter, a position update from 50 ms ago is useless — it is better to drop it and send the
new one than to wait for a resend. In trivia there is nothing "newer" than a player's answer; it
must arrive. Different needs, different protocol.

## 2.4 The TCP handshake

Before any data, the client and the server agree to talk. Three tiny packets:

📄 **Three-way handshake**
```text
client  --- SYN ------------>  server     "I want to connect"
client  <-- SYN + ACK -------  server     "OK, and I want to connect too"
client  --- ACK ------------>  server     "OK"
                                          connection established
```

In Python this happens inside `socket.connect()` on the client and `socket.accept()` on the server.
You will see these three packets in Wireshark (chapter 3) — a screenshot of them belongs in the
networks chapter of your book.

## 2.5 TCP is a stream — the most important idea in this chapter

Here is the thing that surprises everyone the first time. TCP does **not** send "messages". It
sends a **stream of bytes**, like water through a pipe. If the client sends "HELLO" and then
"WORLD", the server may receive:

📄 **What the receiver may see**
```text
sent:      "HELLO"   then   "WORLD"
received:  "HELLOWORLD"                 (glued together)
      or:  "HEL"  then  "LOWORLD"       (cut at a random place)
      or:  "HELLO"  then  "WORLD"       (as sent - only if you are lucky)
```

TCP promises that the *bytes* arrive complete and in order. It promises nothing about *where the
cuts are*. So the program itself must mark where one message ends and the next begins. This is
called **framing**, and there are two common ways:

1. **A delimiter** — a special character after every message. We use the newline `\n`. The
   receiver collects bytes until it sees `\n`, and that is one message.
2. **A length prefix** — send "the next message is 43 bytes", then the 43 bytes.

We use the delimiter because our messages are JSON, and JSON never contains a raw newline, so the
`\n` can never appear *inside* a message.

📄 **Framing with a delimiter — the receiver's logic**
```text
buffer = ""
every time bytes arrive:
    buffer += bytes
    while buffer contains "\n":
        message, buffer = split buffer at the first "\n"
        handle(message)
    # whatever is left in buffer is the START of the next message - keep it
```

This is exactly `MessageBuffer.feed()` in `protocol.py`, and `tests/test_protocol.py` has one test
for "glued" and one for "cut" — they fail until you handle both.

💡 The bug this prevents: a client sends two answers quickly, the server reads both in one
`recv()`, and `json.loads` crashes on `{"type":...}{"type":...}`. Or a long question is cut in
two and `json.loads` crashes on half a message. Both look "random" — they depend on timing — and
that is what makes them nasty.

## 2.6 Latency and the server clock

**Latency** is the time from sending a message until it arrives. On a classroom network: 1–5 ms.
On the internet: 20–200 ms. It is different for every player (Wi-Fi vs. cable, distance from the
router).

For fair scoring, the time a player took must not depend on the player's latency or the player's
clock. So the server measures **both ends on its own clock**: the moment it *sent* the question and
the moment the answer *arrived*. The player's computer clock is never used.

📄 **Measuring response time — on the server only**
```python
question_sent_at = time.monotonic()      # when the question was broadcast
...
response_time = time.monotonic() - question_sent_at   # when the ANSWER message arrived
```

💡 `time.monotonic()` and not `time.time()`. `time.time()` is the wall clock and can jump (the
user changes the time, NTP syncs). `monotonic()` only goes forward, at a constant rate — exactly
what you want for measuring a duration.

## ✅ Check yourself — Chapter 2

1. A server listens on `0.0.0.0:5050`. The server machine has IP `192.168.1.20`. What does a
   client on another machine type as host? And a client on the same machine?
2. The client sends `{"a":1}\n` and then `{"b":2}\n`. Write three different ways the bytes may
   arrive at the server in two `recv()` calls, and what `MessageBuffer` must return after each call.
3. Why can we not use a comma as the delimiter instead of `\n`?
4. Player A has 2 ms latency, player B has 40 ms. Both click at exactly 3.000 s after the question
   appeared on their screens. What response time does the server measure for each, roughly? Is this
   fair? What would be needed to make it perfectly fair?
5. Give one reason a trivia game should use TCP and one reason a racing game should use UDP.

## 📚 Further reading — Chapter 2

- **Python — Socket Programming HOWTO**: https://docs.python.org/3/howto/sockets.html — short and
  honest about the "stream, not messages" problem. Read the section "Using a Socket".
- **Beej's Guide to Network Programming**, chapters 1–3: https://beej.us/guide/bgnet/ — the classic,
  in plain language (examples in C, but the ideas are the same).
- **Kurose & Ross, Computer Networking**, chapter 3 (Transport layer): TCP vs UDP, the handshake.
- **Gaffer On Games — What every programmer needs to know about game networking**:
  https://gafferongames.com/post/what_every_programmer_needs_to_know_about_game_networking/
