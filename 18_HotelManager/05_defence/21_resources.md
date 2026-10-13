# Chapter 21 — Reading plan and sources

Order matters; each item assumes the previous ones.

## Before stage 1 (week 1)

| # | Source | What for | Time |
|---|---|---|---|
| 1 | Python docs — `datetime` (date, timedelta) · https://docs.python.org/3/library/datetime.html | subtracting dates, `weekday()` | 30 min |
| 2 | Real Python — Data Classes · https://realpython.com/python-data-classes/ | `@dataclass`, `frozen`, `__post_init__` | 45 min |
| 3 | Chapters 1–8 of this guide | the four algorithms | one evening |
| 4 | Allen (1983), *Maintaining Knowledge about Temporal Intervals* — the first two pages | the 13 relations, for the book | 30 min |

## Before stage 2 (database)

| # | Source | What for | Time |
|---|---|---|---|
| 5 | SQLBolt lessons 1–12 · https://sqlbolt.com/ | SELECT, WHERE, JOIN, GROUP BY — interactive | 2 h |
| 6 | Python docs — `sqlite3` · https://docs.python.org/3/library/sqlite3.html | placeholders, `row_factory`, transactions | 45 min |
| 7 | SQLite — Foreign Key Support · https://www.sqlite.org/foreignkeys.html | why the PRAGMA | 15 min |
| 8 | DB Browser for SQLite · https://sqlitebrowser.org/ | look at your own database | install |

## Before stages 3–5 (the algorithms and patterns)

| # | Source | What for | Time |
|---|---|---|---|
| 9 | Refactoring Guru — Strategy · https://refactoring.guru/design-patterns/strategy | allocation + pricing rules | 30 min |
| 10 | Refactoring Guru — State · https://refactoring.guru/design-patterns/state | the booking life cycle | 30 min |
| 11 | Refactoring Guru — Facade, Factory Method | `HotelService`, `allocation.create` | 30 min |
| 12 | Python docs — `abc` · https://docs.python.org/3/library/abc.html | abstract base classes | 20 min |
| 13 | pytest — Getting Started · https://docs.pytest.org/en/stable/getting-started.html | running and reading tests | 30 min |

## Before stages 6–7 (interface and reports)

| # | Source | What for | Time |
|---|---|---|---|
| 14 | TkDocs tutorial · https://tkdocs.com/tutorial/ | Notebook, Treeview, Canvas, grid | 2 h |
| 15 | Tkinter Canvas — rectangles and tags · https://tkdocs.com/tutorial/canvas.html | the calendar | 45 min |
| 16 | matplotlib — embedding in Tk · https://matplotlib.org/stable/gallery/user_interfaces/embedding_in_tk_sgskip.html | the report charts | 20 min |

## For the project book's bibliography

| Topic | Source |
|---|---|
| Interval relations | Allen, J. F. (1983). *Maintaining Knowledge about Temporal Intervals*. CACM 26(11), 832–843. |
| Design patterns | Gamma, Helm, Johnson, Vlissides (1994). *Design Patterns*. Addison-Wesley. |
| Layered architecture | Fowler, M. (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley. |
| Databases | Silberschatz, Korth, Sudarshan (2019). *Database System Concepts*, 7th ed. |
| Allocation strategies | Silberschatz, Galvin, Gagne. *Operating System Concepts* — memory allocation (first-fit / best-fit). |
| Open/closed principle | Meyer, B. (1988). *Object-Oriented Software Construction*. |
| SQLite | https://www.sqlite.org/docs.html |

Rule: every source in the bibliography is one you actually read, and you can say in one sentence what
it contributed to your project.
