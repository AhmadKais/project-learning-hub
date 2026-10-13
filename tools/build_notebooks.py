"""Build the example notebooks from their plain-Python sources.

Each notebook is written as a .py file in "percent" format:

    # %% [markdown]
    # # A title
    # Some explanation.

    # %%
    x = 1 + 1
    print(x)

This script turns every tools/notebook_src/<project>/<name>.py into
<project>/02_examples/<name>.ipynb, runs it from top to bottom, and saves
the outputs, so the notebooks show their results on GitHub and every
example is known to run.

    python tools/build_notebooks.py                  # all projects
    python tools/build_notebooks.py 32_WineGrader    # one project
    python tools/build_notebooks.py --no-run         # convert only

Needs: pip install nbformat nbclient ipykernel
"""
import argparse
import re
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "tools" / "notebook_src"
CELL = re.compile(r"^# %%(.*)$", re.M)


def parse_cells(text):
    """Split a percent-format file into (kind, source) pairs."""
    parts = CELL.split(text)
    cells = []
    # parts = [before_first_marker, header1, body1, header2, body2, ...]
    for header, body in zip(parts[1::2], parts[2::2]):
        body = body.strip("\n")
        if "[markdown]" in header:
            lines = [re.sub(r"^# ?", "", line) for line in body.splitlines()]
            cells.append(nbformat.v4.new_markdown_cell("\n".join(lines)))
        elif body.strip():
            cells.append(nbformat.v4.new_code_cell(body))
    return cells


def build(src: Path, run: bool):
    project = src.parent.name
    out_dir = ROOT / project / "02_examples"
    out_dir.mkdir(parents=True, exist_ok=True)
    nb = nbformat.v4.new_notebook()
    nb.cells = parse_cells(src.read_text(encoding="utf-8"))
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    if run:
        NotebookClient(nb, timeout=3600, kernel_name="python3",
                       resources={"metadata": {"path": str(out_dir)}}).execute()
    out = out_dir / (src.stem + ".ipynb")
    nbformat.write(nb, out)
    print(f"  {'ran  ' if run else 'wrote'} {out.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("projects", nargs="*")
    ap.add_argument("--no-run", action="store_true")
    ap.add_argument("--only", help="build only notebooks whose name contains this text")
    args = ap.parse_args()
    dirs = [SRC / p for p in args.projects] if args.projects else sorted(SRC.iterdir())
    for d in dirs:
        print(d.name)
        for src in sorted(d.glob("*.py")):
            if args.only and args.only not in src.stem:
                continue
            build(src, run=not args.no_run)


if __name__ == "__main__":
    sys.exit(main())
