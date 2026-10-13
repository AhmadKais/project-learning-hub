# Chapter 19 — Reading plan and resources

The order matters: every item assumes the previous ones.

## 19.1 Before stage 1 (first week — understand)

| # | Source | What | Time |
|---|---|---|---|
| 1 | Python — Socket Programming HOWTO · https://docs.python.org/3/howto/sockets.html | Sockets, "stream not messages" | 45 min |
| 2 | Real Python — Socket Programming in Python, parts 1–3 · https://realpython.com/python-sockets/ | Echo server/client, then a message protocol | 2 hours |
| 3 | Real Python — Intro to Threading · https://realpython.com/intro-to-python-threading/ | Threads, race conditions, locks — with runnable code | 1.5 hours |
| 4 | Chapters 1–5 of this guide | Make sure it all connects | one evening |

## 19.2 Before stage 2 (server)

| # | Source | What | Time |
|---|---|---|---|
| 5 | Python docs — socket · https://docs.python.org/3/library/socket.html | `bind/listen/accept/settimeout/sendall` | 30 min |
| 6 | Python docs — threading · https://docs.python.org/3/library/threading.html | `Thread`, `Lock`, `RLock`, `Timer` | 30 min |
| 7 | Beej's Guide, chapters 1–3, 5 · https://beej.us/guide/bgnet/ | The classic; what the socket calls really do | 1.5 hours |
| 8 | Wireshark — first steps · https://www.wireshark.org/docs/wsug_html_chunked/ChapterIntroduction.html | Install, capture, filter `tcp.port == 5050` | 45 min |

## 19.3 Before stages 3–4 (database, state machine)

| # | Source | What | Time |
|---|---|---|---|
| 9 | SQLBolt, lessons 1–12 · https://sqlbolt.com/ | SELECT, JOIN, GROUP BY, INSERT — interactive | 2 hours |
| 10 | Python docs — sqlite3 · https://docs.python.org/3/library/sqlite3.html | Placeholders, transactions, `row_factory` | 45 min |
| 11 | SQLite — Foreign Key Support · https://www.sqlite.org/foreignkeys.html | Why the PRAGMA | 15 min |
| 12 | Refactoring Guru — Command, State · https://refactoring.guru/design-patterns | The two patterns in the engine | 45 min |

## 19.4 Before stages 5–6 (client, admin)

| # | Source | What | Time |
|---|---|---|---|
| 13 | TkDocs tutorial · https://tkdocs.com/tutorial/ | Widgets, grid, Treeview, the event loop | 2 hours |
| 14 | Python docs — queue · https://docs.python.org/3/library/queue.html | The inbox between threads | 15 min |
| 15 | Real Python — MVC · https://realpython.com/lessons/mvc-summary/ | The client's layering | 20 min |
| 16 | pytest — Getting Started · https://docs.pytest.org/en/stable/getting-started.html | Running and writing tests | 30 min |

## 19.5 Going deeper (if there is time)

- **Kurose & Ross — Computer Networking: A Top-Down Approach**, chapter 3 (transport layer)
- **Tanenbaum — Computer Networks**, chapter 6
- **Gaffer On Games — Game networking series**: https://gafferongames.com/categories/game-networking/
- **Python docs — selectors / asyncio** (the alternative to thread-per-client, for the alternatives chapter):
  https://docs.python.org/3/library/selectors.html · https://docs.python.org/3/library/asyncio.html
- **Computerphile — TCP/IP videos** (YouTube): https://www.youtube.com/results?search_query=computerphile+tcp

## 19.6 Sources for the project book bibliography

| Topic | Source | Link |
|---|---|---|
| Networks textbook | Tanenbaum & Wetherall (2011), Computer Networks, 5th ed. | ISBN 978-0132126953 |
| Networks textbook | Kurose & Ross (2021), Computer Networking, 8th ed. | ISBN 978-0136681557 |
| Design patterns | Gamma et al. (1994), Design Patterns | ISBN 978-0201633610 |
| Game networking | Fiedler, What Every Programmer Needs To Know About Game Networking | https://gafferongames.com/post/what_every_programmer_needs_to_know_about_game_networking/ |
| Sockets | Python Socket Programming HOWTO | https://docs.python.org/3/howto/sockets.html |
| Sockets | Beej's Guide to Network Programming | https://beej.us/guide/bgnet/ |
| Threads | Python threading documentation | https://docs.python.org/3/library/threading.html |
| GIL | Real Python, What Is the Python GIL? | https://realpython.com/python-gil/ |
| SQLite | SQLite documentation | https://www.sqlite.org/docs.html |
| TCP | RFC 9293, Transmission Control Protocol | https://www.rfc-editor.org/rfc/rfc9293 |
| JSON | RFC 8259, The JSON Data Interchange Format | https://www.rfc-editor.org/rfc/rfc8259 |

Citation rule: every source in the bibliography — you read at least its relevant section and can
say in one sentence what it contributed to the project.
