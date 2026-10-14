"""Live demo for the class: a real TCP connection on this computer that GLUES and CUTS messages.

    python demo_socket.py            # naive receiver  -> watch json.loads fail
    python demo_socket.py --framed   # MessageBuffer-style receiver -> every message arrives whole

The sender writes three JSON messages in awkward pieces (some glued, one cut in half) - exactly what a
real network may do to you.  Nothing here is LanGame code: write your own MessageBuffer.feed().
"""
import json
import socket
import sys
import threading
import time

FRAMED = "--framed" in sys.argv
MESSAGES = [{"type": "JOIN", "payload": {"name": "liraz"}},
            {"type": "ANSWER", "payload": {"question_id": 17, "choice": 2}},
            {"type": "LEAVE", "payload": {}}]


def sender(port):
    wire = b"".join(json.dumps(m).encode() + b"\n" for m in MESSAGES)
    pieces = [wire[:20], wire[20:75], wire[75:]]          # cut inside msg 1, glue 1+2, glue 2+3
    with socket.create_connection(("127.0.0.1", port)) as s:
        for p in pieces:
            s.sendall(p)
            time.sleep(0.3)                                # so each piece arrives as its own recv()


def receiver(server):
    conn, _ = server.accept()
    buffer = b""
    with conn:
        while True:
            chunk = conn.recv(4096)
            if not chunk:
                break
            print(f"recv() got {len(chunk):3d} bytes: {chunk!r}")
            if not FRAMED:
                try:
                    print("    json.loads ->", json.loads(chunk)["type"])
                except json.JSONDecodeError as e:
                    print(f"    json.loads FAILED: {e.msg}")
                continue
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                print("    complete message ->", json.loads(line)["type"])
            if buffer:
                print(f"    waiting in the buffer: {buffer!r}")


if __name__ == "__main__":
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("127.0.0.1", 0))                          # port 0 = any free port
    server.listen()
    port = server.getsockname()[1]
    print(f"{'FRAMED' if FRAMED else 'NAIVE'} receiver listening on 127.0.0.1:{port}\n")
    t = threading.Thread(target=receiver, args=(server,))
    t.start()
    sender(port)
    t.join()
    server.close()
