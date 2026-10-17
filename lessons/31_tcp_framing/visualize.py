"""Lesson 31 - TCP is a byte stream: the handshake, why messages get glued and cut, and newline framing."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "_viz"))
import numpy as np
from common import *  # noqa: F401,F403

L = Lesson(__file__)

MSGS = [{"type": "JOIN", "payload": {"name": "liraz"}},
        {"type": "ANSWER", "payload": {"question_id": 17, "choice": 2}},
        {"type": "LEAVE", "payload": {}}]
WIRE = "".join(json.dumps(m, separators=(",", ":")) + "\n" for m in MSGS)
CUTS = [9, 30, 41, 60, 64, len(WIRE)]           # where the network happens to cut the stream
CHUNKS = [WIRE[a:b] for a, b in zip([0] + CUTS[:-1], CUTS)]
COLS = [BLUE, ORANGE, GREEN]


def colour_of(pos):
    """Which message a character of the wire string belongs to."""
    end = 0
    for i, m in enumerate(MSGS):
        end += len(json.dumps(m, separators=(",", ":"))) + 1
        if pos < end:
            return COLS[i]
    return INK


# ---------------------------------------------------------------- 1. the stream, chopped and re-assembled
if L.wanted("stream"):
    fig, ax = plt.subplots(figsize=(15, 7.4))

    def upd(f):
        k = min(f, len(CHUNKS))
        blank(ax)
        ax.text(0.01, 0.95, "SENDER: three messages, each JSON + \\n", fontsize=13, weight="bold")
        x = 0.01
        for i, m in enumerate(MSGS):
            s = json.dumps(m, separators=(",", ":")) + "\\n"
            ax.text(x, 0.88, s, fontsize=9.5, family="monospace", color=COLS[i])
            x += 0.0072 * len(s) + 0.008
        ax.text(0.01, 0.76, "THE NETWORK: TCP delivers the bytes in order, but cuts them where it likes", fontsize=13,
                weight="bold")
        pos = 0
        for j, ch in enumerate(CHUNKS[:k]):
            y = 0.68 - j * 0.065
            ax.text(0.01, y, f"recv() #{j + 1}:", fontsize=11, color=INK2)
            for c_i, c in enumerate(ch):
                ax.text(0.1 + c_i * 0.0105, y, "⏎" if c == "\n" else c, fontsize=10.5, family="monospace",
                        color=colour_of(pos + c_i))
            pos += len(ch)
        # the receiver's buffer after k chunks
        received = "".join(CHUNKS[:k])
        done, pending = [], received
        while "\n" in pending:
            line, pending = pending.split("\n", 1)
            done.append(line)
        ax.text(0.01, 0.24, "RECEIVER:  buffer += chunk;  while '\\n' in buffer: cut off one message", fontsize=13,
                weight="bold")
        ax.text(0.01, 0.17, "buffer (waiting):", fontsize=11, color=INK2)
        ax.text(0.13, 0.17, pending if pending else "(empty)", fontsize=10.5, family="monospace", color=MUTED)
        ax.text(0.01, 0.09, "complete messages:", fontsize=11, color=INK2)
        for i, d in enumerate(done):
            ax.text(0.15 + i * 0.28, 0.09, f"✓ {json.loads(d)['type']}", fontsize=13, weight="bold", color=COLS[i])
    L.animate(fig, upd, len(CHUNKS) + 4, "stream", fps=1)

# ---------------------------------------------------------------- 2. naive json.loads per recv() vs a buffer
if L.wanted("naive_vs_buffer"):
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(15, 4.8))
    for ax, title, smart in [(a1, "WRONG: json.loads(each recv())", False), (a2, "RIGHT: MessageBuffer.feed()", True)]:
        blank(ax)
        ax.set_title(title, fontsize=13, color=RED if not smart else GREEN)
        buf = ""
        for j, ch in enumerate(CHUNKS):
            y = 0.88 - j * 0.15
            shown = ch.replace("\n", "⏎")
            ax.text(0.01, y, shown if len(shown) < 26 else shown[:24] + "…", fontsize=10.5, family="monospace")
            if not smart:
                try:
                    json.loads(ch)
                    ax.text(0.62, y, "✓ ok (lucky)", fontsize=11, color=GREEN)
                except json.JSONDecodeError as e:
                    ax.text(0.62, y, f"✗ JSONDecodeError", fontsize=11, color=RED)
            else:
                buf += ch
                out = []
                while "\n" in buf:
                    line, buf = buf.split("\n", 1)
                    out.append(json.loads(line)["type"])
                ax.text(0.62, y, ("→ " + ", ".join(out)) if out else "(keep waiting)", fontsize=11,
                        color=GREEN if out else MUTED)
    caption(fig, "The same five recv() results.  Glued and cut messages look 'random' because they depend on timing - "
                 "test_protocol.py has one test for each.")
    L.save(fig, "naive_vs_buffer")

# ---------------------------------------------------------------- 3. the TCP handshake and a message
if L.wanted("handshake"):
    fig, ax = plt.subplots(figsize=(11, 7))
    blank(ax)
    ax.plot([0.2, 0.2], [0.05, 0.9], color=BLUE, lw=3)
    ax.plot([0.8, 0.8], [0.05, 0.9], color=ORANGE, lw=3)
    ax.text(0.2, 0.94, "client (player)", ha="center", fontsize=13, weight="bold", color=BLUE)
    ax.text(0.8, 0.94, "server :5050", ha="center", fontsize=13, weight="bold", color=ORANGE)
    msgs = [(0.82, True, "SYN  'can we talk?'"), (0.72, False, "SYN-ACK  'yes, can you hear me?'"),
            (0.62, True, "ACK  'yes'  →  connection open"), (0.45, True, '{"type":"JOIN",…}\\n'),
            (0.35, False, "ACK  (TCP confirms, re-sends if lost)"), (0.25, False, '{"type":"WELCOME",…}\\n')]
    for y, right, label in msgs:
        a, b = (0.2, 0.8) if right else (0.8, 0.2)
        arrow(ax, (a, y), (b, y - 0.06), color=INK2)
        ax.text(0.5, y - 0.02, label, ha="center", fontsize=11.5, rotation=-5 if right else 5,
                bbox=dict(fc=PAPER, ec="none"), family="monospace" if label.startswith("{") else None)
    ax.text(0.5, 0.68 + 0.17, "the 3-way handshake", ha="center", fontsize=11, color=INK2, style="italic")
    ax.set_title("TCP: connect first, then a reliable, ordered stream of bytes", fontsize=13)
    L.save(fig, "handshake")

# ---------------------------------------------------------------- 4. client / server architecture
if L.wanted("architecture"):
    fig, ax = plt.subplots(figsize=(14, 6))
    blank(ax)
    box(ax, 0.38, 0.3, 0.26, 0.4, "", color=ORANGE, fill=LIGHT_ORANGE)
    ax.text(0.51, 0.66, "GameServer  (0.0.0.0 : 5050)", ha="center", fontsize=12, weight="bold")
    box(ax, 0.41, 0.5, 0.2, 0.1, "accept loop", color=INK2, fontsize=11)
    box(ax, 0.41, 0.34, 0.2, 0.12, "GameEngine (FSM)\nONE lock", color=VIOLET, fontsize=11)
    for i in range(3):
        y = 0.75 - i * 0.28
        box(ax, 0.02, y, 0.18, 0.16, f"client {i + 1}\nTkinter + reader thread", color=BLUE, fontsize=10.5)
        box(ax, 0.23, y + 0.02, 0.13, 0.12, f"ClientHandler\nthread {i + 1}", color=AQUA, fontsize=10)
        arrow(ax, (0.2, y + 0.08), (0.23, y + 0.08), style="<|-|>")
        arrow(ax, (0.36, y + 0.08), (0.41, 0.4), color=MUTED)
    box(ax, 0.72, 0.38, 0.2, 0.24, "Timer threads\n(close question,\nnext question)", color=GREEN, fontsize=11)
    arrow(ax, (0.72, 0.5), (0.61, 0.42), color=MUTED)
    ax.text(0.51, 0.04, "broadcast(): the server sends every state change to all clients - "
                        "the server decides, clients only display", ha="center", fontsize=12)
    ax.set_title("LanGame: one server, one thread per client, one lock around the game state", fontsize=13)
    L.save(fig, "architecture")

# ================================================================ expanded lesson: more pictures
# ---------------------------------------------------------------- 5. the buffer at work, chunk by chunk
if L.wanted("buffer_feed"):
    msgs = [b'{"type":"JOIN","payload":{"name":"liraz"}}\n', b'{"type":"ANSWER","payload":{"question_id":17,"choice":2}}\n',
            b'{"type":"LEAVE","payload":{}}\n']
    stream = b"".join(msgs)
    cuts = [0, 9, 30, 41, 62, 88, 103, len(stream)]
    chunks = [stream[a:b] for a, b in zip(cuts, cuts[1:])]
    fig, ax = plt.subplots(figsize=(14, 6))

    def show(b):
        return b.decode().replace("\n", "⏎")

    def upd(k):
        blank(ax)
        pending, done = b"", []
        for ch in chunks[: k + 1]:
            pending += ch
            *complete, pending = pending.split(b"\n")
            done += [c.decode() for c in complete if c]
        ax.text(0.02, 0.92, f"recv() #{k + 1} returned {len(chunks[k])} bytes:", fontsize=12, color=INK2)
        ax.text(0.02, 0.84, show(chunks[k]), fontsize=12, family="monospace", color=VIOLET, weight="bold")
        ax.text(0.02, 0.68, "the buffer now keeps (an unfinished message):", fontsize=12, color=INK2)
        ax.text(0.02, 0.6, show(pending) or "(empty)", fontsize=12, family="monospace", color=ORANGE,
                bbox=dict(fc=LIGHT_ORANGE, ec=ORANGE))
        ax.text(0.02, 0.44, "complete messages handed to the program so far:", fontsize=12, color=INK2)
        for i, m in enumerate(done):
            ax.text(0.04, 0.35 - i * 0.09, "✓ " + m, fontsize=12, family="monospace", color=GREEN)
        ax.set_title("MessageBuffer.feed(): add the chunk, cut at every ⏎, keep the last piece", fontsize=14)
    frames = [k for k in range(len(chunks)) for _ in range(2)] + [len(chunks) - 1] * 3
    L.animate(fig, lambda i: upd(frames[i]), len(frames), "buffer_feed", fps=1)
