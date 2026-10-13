# %% [markdown]
# # 01 · TCP is a stream — framing and the message protocol
#
# **Read first:** `01_theory/02_networks.md` (§2.5 especially), `01_theory/03_sockets_protocol.md`
#
# 1. a real server and client on this computer — and messages that arrive **glued together**
# 2. framing with `\n`: a `MessageBuffer` that always cuts in the right place
# 3. the protocol: `Message.to_wire()` / `Message.from_wire()`
# 4. never trust the other side: every kind of garbage becomes a `ProtocolError`, never a crash

# %%
import json
import socket
import threading
import time

# %% [markdown]
# ## 1. See the stream with your own eyes
#
# The client sends three **separate** messages with three `sendall` calls. The server reads with `recv(4096)`.
# How many reads does it take?

# %%
def run_server(port_holder, received, ready):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(("127.0.0.1", 0))                 # 0 = let the OS choose a free port
    listener.listen(1)
    port_holder.append(listener.getsockname()[1])
    ready.set()
    conn, addr = listener.accept()                  # blocks until the client connects
    time.sleep(0.2)                                 # give the client time to send everything
    while True:
        chunk = conn.recv(4096)
        if chunk == b"":                            # b"" = the other side closed: goodbye
            break
        received.append(chunk)
    conn.close(); listener.close()

port, received, ready = [], [], threading.Event()
t = threading.Thread(target=run_server, args=(port, received, ready), daemon=True)
t.start(); ready.wait()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", port[0]))
for msg in ('{"type": "JOIN", "payload": {"name": "liraz"}}\n',
            '{"type": "ANSWER", "payload": {"question_id": 17, "choice": 2}}\n',
            '{"type": "LEAVE", "payload": {}}\n'):
    client.sendall(msg.encode("utf-8"))
client.close(); t.join()

print(f"3 messages sent, {len(received)} recv() call(s) returned data:")
for chunk in received:
    print("  ", chunk)

# %% [markdown]
# Three messages, **one** `recv`. TCP delivers bytes complete and in order, but promises nothing about where the
# cuts are. If the server assumed "one recv = one message", it would try to parse three JSON objects as one and
# fail. With a big message (say 10 KB of questions) the opposite happens — one message arrives in several recvs.
#
# ## 2. Framing with a delimiter
#
# Collect bytes in a buffer; every `\n` ends one message. JSON never contains a raw newline, so `\n` can never
# appear *inside* a message.

# %%
MAX_MESSAGE_BYTES = 64 * 1024

class ProtocolError(Exception):
    def __init__(self, code):
        super().__init__(code)
        self.code = code

class MessageBuffer:
    def __init__(self):
        self._buffer = b""

    def feed(self, data: bytes):
        """Add received bytes; return the list of COMPLETE lines (without the \\n)."""
        self._buffer += data
        lines = []
        while b"\n" in self._buffer:
            line, self._buffer = self._buffer.split(b"\n", 1)
            if line.strip():
                lines.append(line)
        if len(self._buffer) > MAX_MESSAGE_BYTES:      # a "message" with no end: an attack or a bug
            self._buffer = b""
            raise ProtocolError("too_large")
        return lines

buf = MessageBuffer()
stream = received[0]
# cut the same stream at every possible place - framing must give the same 3 messages every time
for cut in (1, 10, 47, 60, len(stream) - 1):
    b = MessageBuffer()
    got = b.feed(stream[:cut]) + b.feed(stream[cut:])
    print(f"cut at byte {cut:3d}: {len(got)} messages")

# %% [markdown]
# ## 3. The protocol — `to_wire` and `from_wire`

# %%
MESSAGE_TYPES = {"JOIN", "START_GAME", "ANSWER", "LEAVE",                                  # client -> server
                 "WELCOME", "LOBBY_UPDATE", "COUNTDOWN", "QUESTION", "RESULT", "LEADERBOARD",
                 "GAME_OVER", "ERROR"}                                                     # server -> client

class Message:
    def __init__(self, type_, payload=None):
        self.type, self.payload = type_, payload or {}

    def to_wire(self) -> bytes:
        return (json.dumps({"type": self.type, "payload": self.payload}, ensure_ascii=False) + "\n").encode("utf-8")

    @staticmethod
    def from_wire(line: bytes) -> "Message":
        try:
            data = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ProtocolError("bad_json")
        if not isinstance(data, dict) or data.get("type") not in MESSAGE_TYPES:
            raise ProtocolError("unknown_type")
        if not isinstance(data.get("payload"), dict):
            raise ProtocolError("bad_payload")
        return Message(data["type"], data["payload"])

    def __repr__(self):
        return f"Message({self.type}, {self.payload})"

wire = Message("QUESTION", {"question_id": 3, "text": "מהו פרוטוקול TCP?", "options": ["a", "b", "c", "d"]}).to_wire()
print(wire)
print(Message.from_wire(wire.rstrip(b"\n")))

# %% [markdown]
# `ensure_ascii=False` + UTF-8 keeps Hebrew readable on the wire (and in Wireshark).
#
# ## 4. Never trust the other side

# %%
attacks = [b"hello", b'{"type": "ANSWER"}', b'{"type": "HACK", "payload": {}}', b"[1, 2, 3]",
           b'{"type": "JOIN", "payload": "liraz"}', b"\xff\xfe\x00", b'{"type": "LEAVE", "payload": {}}']
for line in attacks:
    try:
        print("OK     ", Message.from_wire(line))
    except ProtocolError as e:
        print("ERROR  ", f"{e.code:13s} <- {line!r}")

big = MessageBuffer()
try:
    big.feed(b"x" * (MAX_MESSAGE_BYTES + 1))
except ProtocolError as e:
    print("ERROR  ", e.code, "<- 64 KB with no newline")

# %% [markdown]
# One exception type with a short code. The server's handler thread catches `ProtocolError`, replies
# `ERROR {"code": ...}` and **keeps serving**. Only a closed socket ends the thread. Note that this layer checks
# the *shape* only — "is an ANSWER legal right now?" is the game engine's job (notebook 03).
#
# ## ✍️ Try it yourself
#
# 1. Send one message of 20,000 characters in section 1. How many `recv` calls does it take now?
# 2. Write the exact bytes of a LEAVE message on the wire. Check with `Message("LEAVE").to_wire()`.
# 3. What happens in `MessageBuffer` if a client sends `\n\n\n`? Is that correct?
#
# Then solve exercises 1–3 in `03_exercises/`.
