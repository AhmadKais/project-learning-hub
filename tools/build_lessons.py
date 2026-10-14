"""Build the lessons: draw every picture / animation, and join all lessons into one teaching file.

    python tools/build_lessons.py                 # figures (PNG + GIF + MP4) for every lesson, then LESSONS.html
    python tools/build_lessons.py 15_knn          # only the lessons whose folder name contains "15_knn"
    python tools/build_lessons.py --no-video      # skip the MP4 files (no ffmpeg needed)
    python tools/build_lessons.py --html-only     # only rebuild lessons/LESSONS.html from the LESSON.md files

LESSONS.html is the "teaching book": every lesson in order, one table of contents, the GIFs play in the
browser.  Open it from inside the lessons/ folder (it links to the figs/ folders next to it) and press F11
for the projector.  Needs: pandoc (for the HTML), ffmpeg (for MP4), and the packages in requirements.txt.
"""
import argparse
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

HUB = Path(__file__).resolve().parent.parent
LESSONS = HUB / "lessons"

CSS = """
:root { --paper:#fcfcfb; --ink:#0b0b0b; --ink2:#52514e; --line:#e4e3df; --accent:#2a78d6; --soft:#f3f2ee; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) {
  --paper:#1a1a19; --ink:#f0efec; --ink2:#c3c2b7; --line:#3a3936; --accent:#3987e5; --soft:#262624; } }
body { background:var(--paper); color:var(--ink); font:18px/1.6 system-ui, sans-serif; max-width:1100px;
       margin:0 auto; padding:24px 16px 80px; }
img { max-width:100%; height:auto; background:#fcfcfb; border-radius:6px; }
h1 { border-top:3px solid var(--accent); padding-top:28px; margin-top:64px; }
h1:first-of-type { border:none; margin-top:0; }
table { border-collapse:collapse; display:block; overflow-x:auto; }
th, td { border:1px solid var(--line); padding:6px 10px; vertical-align:top; }
th { background:var(--soft); }
code { background:var(--soft); padding:1px 4px; border-radius:4px; }
pre { background:var(--soft); padding:12px; overflow-x:auto; border-radius:6px; }
pre code { padding:0; }
blockquote { border-left:4px solid var(--accent); margin:0; padding:4px 16px; color:var(--ink2); }
details { background:var(--soft); border-radius:6px; padding:8px 12px; margin:8px 0; }
summary { cursor:pointer; font-weight:600; }
a { color:var(--accent); }
nav#TOC { background:var(--soft); padding:12px 20px; border-radius:8px; }
nav#TOC > ul > li { margin:4px 0; }
nav#TOC ul ul { display:none; }
"""


def run_figures(folders, no_video):
    py = sys.executable
    for folder in folders:
        script = folder / "visualize.py"
        if not script.exists():
            continue
        t0 = time.time()
        print(f"== {folder.name}")
        cmd = [py, str(script)] + (["--no-video"] if no_video else [])
        res = subprocess.run(cmd, cwd=folder, capture_output=True, text=True)
        out = [l for l in (res.stdout + res.stderr).splitlines() if "Warning" not in l and "warn(" not in l]
        print("\n".join("   " + l.strip() for l in out if l.strip()))
        if res.returncode != 0:
            raise SystemExit(f"{folder.name}/visualize.py failed")
        print(f"   ({time.time() - t0:.0f} s)")


def build_html():
    if not shutil.which("pandoc"):
        raise SystemExit("pandoc is not installed - https://pandoc.org/installing.html")
    parts = [(LESSONS / "README.md").read_text(encoding="utf-8")]
    for folder in sorted(p for p in LESSONS.iterdir() if p.is_dir() and re.match(r"\d\d_", p.name)):
        md = (folder / "LESSON.md").read_text(encoding="utf-8")
        # make the relative links work from lessons/: figs/x -> NN_name/figs/x, file.py -> NN_name/file.py
        md = re.sub(r"\]\((?!https?:|#|\.\./)([^)]+)\)", lambda m: f"]({folder.name}/{m.group(1)})", md)
        parts.append(md)
    parts.append((LESSONS / "GLOSSARY.md").read_text(encoding="utf-8"))
    # the README's own links to NN_name/LESSON.md become in-page anchors
    joined = "\n\n".join(parts)
    joined = re.sub(r"\((\d\d_[a-z0-9_]+)/LESSON\.md\)", lambda m: f"(#{m.group(1)})", joined)
    src = LESSONS / "_LESSONS.md"
    css = LESSONS / "_lessons.css"
    src.write_text(joined, encoding="utf-8")
    css.write_text(CSS, encoding="utf-8")
    out = LESSONS / "LESSONS.html"
    subprocess.run(["pandoc", src.name, "-f", "gfm+tex_math_dollars", "-t", "html5", "--standalone", "--toc",
                    "--toc-depth=1", "--mathml", "--wrap=none", "--css", css.name, "--metadata",
                    "title=Algorithms — the teaching book", "-o", out.name], check=True, cwd=LESSONS)
    # anchors for each lesson folder, so the README table links jump inside the page
    html = out.read_text(encoding="utf-8")
    for folder in sorted(p for p in LESSONS.iterdir() if p.is_dir() and re.match(r"\d\d_", p.name)):
        num = folder.name[:2]
        html = re.sub(rf'(<h1 id="lesson-{num}-[^"]*")', rf'<a id="{folder.name}"></a>\1', html, count=1)
    out.write_text(html, encoding="utf-8")
    src.unlink()
    print(f"wrote {out.relative_to(HUB)}  ({out.stat().st_size / 1e3:.0f} KB)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("only", nargs="?", help="build only the lessons whose folder name contains this")
    ap.add_argument("--no-video", action="store_true")
    ap.add_argument("--html-only", action="store_true")
    a = ap.parse_args()
    folders = sorted(p for p in LESSONS.iterdir() if p.is_dir() and re.match(r"\d\d_", p.name))
    if a.only:
        folders = [f for f in folders if a.only in f.name]
    if not a.html_only:
        run_figures(folders, a.no_video)
    build_html()
