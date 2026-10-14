# Lesson 31 — TCP is a stream: sockets, the protocol and message framing

> **For:** Liraz (LanGame stages 1–2) &nbsp;·&nbsp; **Time:** 2 × 45 min
> **Before:** Python bytes/strings, JSON &nbsp;·&nbsp; **After this:** Lessons 32, 30

## The story

> Liraz's quiz game works perfectly on her laptop: the server and two players on the same computer. In the classroom, on
> the Wi-Fi, with 8 players, it crashes every few minutes with `JSONDecodeError`. She adds prints and sees the server
> received `{"type":"ANSWER","payload":{"question_id":17,"cho` — **half a message**. Another time, **two messages glued
> together**. She thought "one `send` = one `recv`". It isn't. Imagine pouring water through a pipe: the receiver gets the
> water, in order, but never "one cup at a time" as you poured it. TCP is that pipe. This lesson explains it and the simple
> fix: **framing**.

## 🎯 By the end, the student can

1. Explain client, server, IP address, port and socket with the building analogy, and the TCP handshake.
2. Explain why TCP glues and cuts messages, and show it happening on a real socket.
3. Write the newline-framing receiver.
4. Explain the protocol (`type` + `payload`, one JSON per line) and "never trust the other side".

## Words you need

| word | meaning | analogy |
|---|---|---|
| **server** | the program that waits, decides, and answers | the quiz master |
| **client** | a program that connects and asks | a player |
| **IP address** | which computer | the building's street address |
| **port** | which program on that computer (LanGame: 5050) | the apartment number |
| **socket** | one end of a connection, used in the code | your end of a phone line |
| **TCP** | a connection that delivers bytes reliably and in order | a phone call |
| **UDP** | single packets, may be lost or out of order | throwing notes over a fence |
| **bytes** | what really travels: numbers 0–255 (text is encoded as bytes) | |
| **stream** | a flow of bytes with no boundaries between messages | water in a pipe |
| **framing** | marking where one message ends | a full stop at the end of each sentence |
| **protocol** | the agreed list of messages and their meaning | the rules of the quiz |
| **JSON** | text format for data: `{"type": "JOIN", "payload": {"name": "liraz"}}` | |

---

## 1. Who talks to whom

![architecture](figs/architecture.png)

The **server** runs on one computer, listens on port 5050, holds the game (questions, scores, the clock) and **decides**.
The **clients** connect, send requests (JOIN, ANSWER…) and display what the server **broadcasts** to everyone.

## 2. Connecting — the handshake

![TCP handshake](figs/handshake.png)

Before any data, TCP opens a connection with three short messages — like a phone call: *"can we talk?"* — *"yes, can you
hear me?"* — *"yes"*. After that, every byte sent is confirmed; lost bytes are sent again automatically. That's why
LanGame uses TCP: "who answered first" must never get lost. (UDP is fine for video, where a lost frame doesn't matter.)

## 3. The most important idea: TCP is a stream of bytes

![the stream](figs/stream.gif)

The sender sends three messages. The network cuts the bytes wherever it likes. The receiver's `recv()` returns **whatever has
arrived so far**:

```
sent:       {"type":"JOIN",…}⏎   {"type":"ANSWER",…}⏎   {"type":"LEAVE",…}⏎        (⏎ = newline)
recv() #1:  {"type":"
recv() #2:  JOIN","payload":{"nam
recv() #3:  e":"liraz"}
recv() #4:  }⏎{"type":"ANSWER",            ← the end of one message + the start of the next
…
```

TCP promises the bytes arrive **complete and in order** — it promises **nothing** about where the cuts are.

### Framing — the receiver keeps a buffer

LanGame puts a **newline** after every JSON message (JSON never contains a raw newline, so it can't appear inside one). The
receiver:

```
buffer = empty
every time bytes arrive:
    1. add them to the end of the buffer
    2. while the buffer contains a newline:
           cut off everything up to the first newline → that's ONE complete message → handle it
    3. whatever is left is the START of the next message → keep it for later
```

By hand with the chunks above:

```
after #1:  buffer = {"type":"                                → no newline → wait
after #2:  buffer = {"type":"JOIN","payload":{"nam           → wait
after #3:  buffer = {"type":"JOIN","payload":{"name":"liraz"} → wait
after #4:  buffer = {"type":"JOIN",…}}⏎{"type":"ANSWER",
           newline found → message 1 = JOIN ✓      buffer = {"type":"ANSWER",
```

![naive vs buffer](figs/naive_vs_buffer.png)

```python
class MessageBuffer:
    def feed(self, chunk: bytes) -> list:                       # a sketch — follow the TODO in protocol.py
        self._pending += chunk
        if len(self._pending) > MAX_MESSAGE_BYTES:              # never trust the other side (§5)
            raise ProtocolError("too_large", ...)
        *complete, self._pending = self._pending.split(b"\n")   # the LAST piece is incomplete: keep it
        return [decode(line) for line in complete if line]
```

### See it for real

```bash
cd lessons/31_tcp_framing
python demo_socket.py            # json.loads on every recv()  → 3 failures
python demo_socket.py --framed   # the buffer                  → JOIN, ANSWER, LEAVE
```

## 4. The protocol

```
{"type": "ANSWER", "payload": {"question_id": 17, "choice": 2}}⏎
```

* `type` — one of a fixed list (`MessageType`); the receiver decides what to do by it.
* `payload` — the details; its keys depend on the type.
* JSON because it's readable (in logs and in Wireshark), every language reads it, and adding a field later doesn't break
  old players.
* The QUESTION message **never contains the correct answer** — anyone with Wireshark could read it.

## 5. Never trust the other side

A buggy or malicious client can send 10 MB without a newline, broken JSON, an unknown type, or `"choice": 7`. Each becomes an
`ERROR` reply; the server never crashes. The 64 KB limit stops a client from filling the server's memory.

## 6. Common mistakes

| student says | the truth |
|---|---|
| "One `send()` = one `recv()`" | Only by luck on one computer. On a network, never. |
| "It works on my laptop, so it's fine" | Localhost rarely cuts messages; the classroom Wi-Fi does. Use the demo. |
| "`recv(4096)` returns 4096 bytes" | *Up to* 4096 — whatever arrived. 0 bytes = the other side closed. |

## 7. Activities

1. **Paper pipe (10 min).** Write 3 messages on a long paper strip with ⏎ marks; cut it at random places; hand the pieces one
   by one to a "receiver" who rebuilds the messages using only a buffer and the ⏎ marks.
2. **Run the demo** in both modes; then change the cut points in `sender()`.
3. **Wireshark (15 min).** Capture `tcp.port == 5050` while two clients play; find a QUESTION message; confirm there's no
   correct answer in it.

## 8. Do it yourself

<details><summary>1. Buffer holds `{"type":"JO`; the next chunk is `IN","payload":{}}⏎{"ty`. What does feed() return and keep?</summary>

Returns one message (JOIN); keeps `{"ty` for the next chunk.
</details>

<details><summary>2. Why is a newline a safe separator for JSON messages?</summary>

`json.dumps` writes a newline inside a string as the two characters `\n`, so a real newline byte never appears inside a
message.
</details>

<details><summary>3. Why the 64 KB limit?</summary>

A client that never sends a newline would make the buffer grow forever and fill the server's memory.
</details>

## 9. In your project

| Project | Where |
|---|---|
| LanGame | `langame/common/protocol.py` → `Message.to_wire`, `Message.from_wire`, `MessageBuffer.feed` · `server/client_handler.py` → `run`, `send` · `server/game_server.py` → `serve_forever`, `broadcast` · `client/network_client.py` → `_reader_loop`, `send` · config `SERVER_PORT = 5050`, `MAX_MESSAGE_BYTES` · theory `05_LanGame/01_theory/02_networks.md`, `03_sockets_protocol.md` · notebooks `01_tcp_stream_and_framing.ipynb`, `04_mini_server.ipynb` |

## 🎬 Watch & explore

* *TCP 3-way handshake explained* — [search on YouTube](https://www.youtube.com/results?search_query=TCP+3+way+handshake+explained)
* Python docs — [Socket Programming HOWTO](https://docs.python.org/3/howto/sockets.html)
* Wireshark — [user guide](https://www.wireshark.org/docs/wsug_html_chunked/)
