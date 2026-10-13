# %% [markdown]
# # 04 · Putting it together — a mini lobby server with real sockets
#
# **Read first:** `04_build/07_architecture.md`, and notebooks 01–03
#
# A small but complete server: a listening socket, **one thread per client**, framing, the protocol, a shared
# lobby protected by a lock, broadcast with copy-under-lock, and a bad client that sends garbage. Three clients
# connect from this same notebook.

# %%
import json
import socket
import threading
import time

class ProtocolError(Exception):
    def __init__(self, code):
        super().__init__(code); self.code = code

def to_wire(type_, payload=None):
    return (json.dumps({"type": type_, "payload": payload or {}}, ensure_ascii=False) + "\n").encode("utf-8")

def from_wire(line):
    try:
        data = json.loads(line.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProtocolError("bad_json")
    if not isinstance(data, dict) or data.get("type") not in {"JOIN", "LEAVE"} or not isinstance(data.get("payload"), dict):
        raise ProtocolError("bad_message")
    return data["type"], data["payload"]

# %% [markdown]
# ## The server

# %%
class LobbyServer:
    def __init__(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listener.bind(("127.0.0.1", 0))
        self.listener.listen(8)
        self.listener.settimeout(0.5)              # so the accept loop can notice shutdown
        self.port = self.listener.getsockname()[1]
        self.lock = threading.Lock()
        self.clients = {}                          # socket -> name (None until JOIN)
        self.running = True
        self.log = []

    def serve_forever(self):
        while self.running:
            try:
                conn, addr = self.listener.accept()
            except socket.timeout:
                continue
            with self.lock:
                self.clients[conn] = None
            threading.Thread(target=self.handle, args=(conn,), daemon=True).start()

    def handle(self, conn):                        # one of these threads per client
        buffer = b""
        conn.settimeout(0.5)
        try:
            while self.running:
                try:
                    chunk = conn.recv(4096)
                except socket.timeout:
                    continue
                if chunk == b"":                   # the client closed the connection
                    break
                buffer += chunk
                while b"\n" in buffer:
                    line, buffer = buffer.split(b"\n", 1)
                    try:
                        self.dispatch(conn, *from_wire(line))
                    except ProtocolError as e:     # garbage: reply, keep serving
                        conn.sendall(to_wire("ERROR", {"code": e.code}))
        finally:
            self.remove(conn)

    def dispatch(self, conn, type_, payload):
        if type_ == "JOIN":
            name = str(payload.get("name", ""))[:16]
            with self.lock:
                if not name or name in self.clients.values():
                    conn.sendall(to_wire("ERROR", {"code": "name_taken"}))
                    return
                self.clients[conn] = name
            conn.sendall(to_wire("WELCOME", {"name": name}))
            self.broadcast_lobby()
        elif type_ == "LEAVE":
            conn.shutdown(socket.SHUT_RDWR)

    def remove(self, conn):
        with self.lock:
            name = self.clients.pop(conn, None)
        conn.close()
        if name:
            self.log.append(f"{name} left")
            self.broadcast_lobby()

    def broadcast_lobby(self):
        with self.lock:                            # copy under the lock ...
            targets = [c for c, n in self.clients.items() if n]
            players = sorted(n for n in self.clients.values() if n)
        for c in targets:                          # ... send outside it
            try:
                c.sendall(to_wire("LOBBY_UPDATE", {"players": players}))
            except OSError:
                pass

    def shutdown(self):
        self.running = False
        self.listener.close()

server = LobbyServer()
threading.Thread(target=server.serve_forever, daemon=True).start()
print("server listening on 127.0.0.1 port", server.port)

# %% [markdown]
# ## Three clients — and one troublemaker
#
# Each client has a reader thread that collects what the server sends (exactly what `NetworkClient` does in your
# project, with a queue instead of a list).

# %%
class Client:
    def __init__(self, port):
        self.sock = socket.create_connection(("127.0.0.1", port))
        self.inbox = []
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        buffer = b""
        while True:
            try:
                chunk = self.sock.recv(4096)
            except OSError:
                return
            if not chunk:
                return
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                self.inbox.append(json.loads(line))

    def send_raw(self, data):
        self.sock.sendall(data)

    def disconnect(self):
        # shutdown() first: it sends the FIN even while our reader thread is blocked in recv().
        # A bare close() from another thread may not - the server would never hear goodbye.
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

liraz, dana, omar = Client(server.port), Client(server.port), Client(server.port)
liraz.send_raw(to_wire("JOIN", {"name": "liraz"})); time.sleep(0.1)
dana.send_raw(to_wire("JOIN", {"name": "dana"}));   time.sleep(0.1)
omar.send_raw(b'{"type": "JOIN", "payload": {"name": "omar"}}\n{"type": "JO')   # 1.5 messages at once ...
time.sleep(0.1)
omar.send_raw(b'IN", "payload": {"name": "liraz"}}\nthis is not json\n')        # ... the rest + garbage
time.sleep(0.3)

for name, c in (("liraz", liraz), ("dana", dana), ("omar", omar)):
    print(f"--- {name} received:")
    for m in c.inbox:
        print("    ", m)

# %% [markdown]
# Look at omar: his messages arrived split and glued, yet the server understood all of them; his second JOIN as
# "liraz" got `name_taken`; the garbage line got `bad_json` — and the server kept running for everyone.
#
# ## A client disconnects

# %%
dana.disconnect()
time.sleep(0.8)
print("liraz's last message:", liraz.inbox[-1])
print("server log:", server.log)
server.shutdown()

# %% [markdown]
# `recv` returned `b""` in dana's handler thread, the thread removed her and broadcast the new lobby, and nobody
# crashed. That is stage 2 of your `TASKS.md`.
#
# ## ✍️ Try it yourself
#
# 1. Send a JOIN with a 500-character name. What does the lobby show?
# 2. Make one client "slow" (`time.sleep(2)` before each `recv` in its reader). Does the lobby update still reach
#    the others immediately? Why?
# 3. Open Wireshark on the loopback interface, filter `tcp.port == <the port>`, re-run, and find the three
#    handshake packets and one LOBBY_UPDATE.
#
# Then solve exercises 11–12 in `03_exercises/`.
