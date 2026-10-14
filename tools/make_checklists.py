"""Write <project>/06_solve/CHECKLIST.md: every function the student still has to write, stage by stage.

Reads the student's skeleton next to this repo (../<Student>/<Project>/):
    - a function is a TODO when its body raises NotImplementedError
    - its stage is the "TODO stage N" in its docstring (else the stage of TASKS.md that names it)
    - its tests are the test files that mention its name
    - stage titles and exit conditions come from TASKS.md

Run again whenever a skeleton changes:   python tools/make_checklists.py
"""
import ast
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT.parent

PROJECTS = {
    "05_LanGame": "Liraz_dakseh/LanGame",
    "08_SpamClassifier": "Laith_Halabi/SpamClassifier",
    "13_FaceEmotion": "Ryan_raed/FaceEmotion",
    "18_HotelManager": "Eran_Nijm/HotelManager",
    "25_PhishGuard": "Dani_Faris/PhishGuard",
    "31_ResumeMatch": "Kosai_Badreih/ResumeMatch",
    "32_WineGrader": "Seif_Ferro/WineGrader",
}

SKIP_DIRS = {".venv", "venv", "__pycache__", ".git", "tests", "_TEACHER_SOLUTION_do_not_send"}
STAGE_IN_DOC = re.compile(r"TODO\s+stage\s+(\d+)", re.I)
STAGE = r"^##\s+(?:Stage|שלב)\s+(\d+)(?:\s*[–-]\s*(\d+))?"             # "Stage 9–10" covers two stages
STAGE_HEADING = re.compile(STAGE + r"\s*[—:-]\s*(.+)$", re.M)
STAGE_SECTION = re.compile(STAGE + r".*?$(.*?)(?=^##\s|\Z)", re.M | re.S)
EXIT = re.compile(r"\*\*(?:Exit condition|Done when|תנאי סיום):?\*\*:?\s*(.*?)(?=\n---|\n##|\Z)", re.S)

# Ryan's TASKS.md is in Hebrew; the hub is in English
ENGLISH_STAGES = {
    "13_FaceEmotion": {
        1: ("Environment and camera",
            "a small script of your own opens `CameraService`, reads a frame and shows it with `cv2.imshow` — "
            "the video flows without freezing."),
        2: ("Face detection",
            "a green box around your face in real time (in `cv2.imshow`, before Tkinter); `detect()` is timed and "
            "printed — under 30 ms per frame. `pytest tests/test_preprocessor.py -k \"area or margin or crop\"` green."),
        3: ("Data and model",
            "`pytest tests/test_network.py tests/test_preprocessor.py -v` all green. `EmotionNet().count_parameters()` "
            "prints 4,900,551. A short `python train.py --epochs 2` starts (it may crash at the end — no Trainer yet)."),
        4: ("Full training on the GPU, and evaluation",
            "`python train.py` finishes 50 epochs (or stops early) in under 20 minutes on the GPU; "
            "`models/emotion_net_best.pt` exists; `python evaluate.py` prints **accuracy ≥ 65%** on the test set; "
            "`reports/confusion_matrix.png`, `training_curves.png`, `metrics.json` exist. Keep a table of **every** "
            "training run (epochs, LR, augmentation, accuracy) — it is the results chapter of your book."),
        5: ("Real-time integration",
            "`pytest tests/test_smoothing.py -v` green. The camera shows a coloured box + emotion name + percentage, "
            "FPS ≥ 15 (target 25 with the GPU), and the label does not flicker when your expression is steady."),
        6: ("Database, UI and export",
            "`pytest -v` **all** green. `python run.py` opens a window with video, emotion panel, live chart and "
            "statistics bar; Stop shows a summary; \"Export CSV\" writes a file in `exports/` that opens in Excel; "
            "`faceemotion.db` holds the session and its samples (check with DB Browser for SQLite)."),
        7: ("Comparing alternatives, tests and documentation",
            "a complete project book where every number comes from a file in `reports/` or from `pytest` output."),
    },
}


def raises_not_implemented(fn) -> bool:
    for node in ast.walk(fn):
        if isinstance(node, ast.Raise) and node.exc is not None:
            exc = node.exc.func if isinstance(node.exc, ast.Call) else node.exc
            if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
                return True
    return False


def instructions(fn, source: str) -> str:
    """The TODO text of a function without a docstring: a string after super().__init__(), or # comments."""
    for node in fn.body:
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            return node.value.value
    lines = source.splitlines()[fn.lineno:fn.end_lineno]
    comments = [l.strip()[1:].strip() for l in lines if l.strip().startswith("#")]
    return "\n".join(comments) if any("TODO" in c for c in comments) else ""


def signature(fn) -> str:
    if any(isinstance(d, ast.Name) and d.id == "property" for d in fn.decorator_list):
        return fn.name                                    # a property is read without ()
    args = [a.arg for a in fn.args.args if a.arg not in ("self", "cls")]
    if fn.args.vararg:
        args.append("*" + fn.args.vararg.arg)
    if fn.args.kwarg:
        args.append("**" + fn.args.kwarg.arg)
    return f"{fn.name}({', '.join(args)})"


def summary(doc: str) -> str:
    text = STAGE_IN_DOC.sub("", doc or "").strip(" :-\n")
    paragraphs = re.split(r"\n\s*\n", text)
    first = paragraphs[0]
    if first.rstrip().endswith(":") and len(paragraphs) > 1:      # "two lines:" -> show the two lines too
        first += " " + paragraphs[1]
    first = " ".join(first.split())
    return first if len(first) <= 220 else first[:217].rstrip() + "..."


def todos(project_dir: Path):
    found = []
    for py in sorted(project_dir.rglob("*.py")):
        rel = py.relative_to(project_dir)
        if SKIP_DIRS & set(rel.parts):
            continue
        source = py.read_text(encoding="utf-8")
        tree = ast.parse(source)
        # a method a subclass in the same file redefines is an interface, not a task
        overridden = {(base.id, m.name)
                      for c in tree.body if isinstance(c, ast.ClassDef)
                      for base in c.bases if isinstance(base, ast.Name)
                      for m in c.body if isinstance(m, ast.FunctionDef)}
        for node in tree.body:
            items = [(None, node)]
            if isinstance(node, ast.ClassDef):
                items = [(node.name, n) for n in node.body]
            for cls, fn in items:
                if (cls, getattr(fn, "name", None)) in overridden:
                    continue
                if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) and raises_not_implemented(fn):
                    doc = ast.get_docstring(fn) or instructions(fn, source)
                    m = STAGE_IN_DOC.search(doc)
                    found.append({
                        "file": rel.as_posix(), "cls": cls, "fn": fn, "doc": doc,
                        "stage": int(m.group(1)) if m else None,
                    })
    return found


def stage_from_tasks(item, tasks: str, loose: bool):
    """The stage whose TASKS.md line names this file and function (loose: just the file or its folder)."""
    folder = Path(item["file"]).parent.as_posix()
    for num, _, body in STAGE_SECTION.findall(tasks):
        for line in body.splitlines():
            if not loose and item["file"] in line and re.search(rf"\b{item['fn'].name}\b|everything|all ", line):
                return int(num)
            if loose and (Path(item["file"]).name in line or any(f"{folder}/{x}" in line for x in ("*", "`", " "))):
                return int(num)
    return None


def tests_for(item, tests: dict) -> list:
    name = item["fn"].name
    if name.startswith("__"):
        name = item["cls"] or name
    word = re.compile(rf"\b{re.escape(name)}\b")
    module = Path(item["file"]).with_suffix("").as_posix().replace("/", ".")
    hits = []
    for tname, text in tests.items():
        if word.search(text) and (module in text or (item["cls"] and item["cls"] in text) or Path(item["file"]).stem in text):
            hits.append(tname)
    return hits


def exit_conditions(tasks: str) -> dict:
    out = {}
    for num, _, body in STAGE_SECTION.findall(tasks):
        m = EXIT.search(body)
        if m:
            out[int(num)] = " ".join(m.group(1).split())
    return out


def build(project: str, skeleton: str):
    project_dir = PACKAGES / skeleton
    tasks = (project_dir / "TASKS.md").read_text(encoding="utf-8")
    titles = {}
    for first, last, title in STAGE_HEADING.findall(tasks):
        for n in range(int(first), int(last or first) + 1):
            titles[n] = title.strip()
    exits = exit_conditions(tasks)
    for n, (title, exit_text) in ENGLISH_STAGES.get(project, {}).items():
        titles[n], exits[n] = title, exit_text
    tests = {p.name: p.read_text(encoding="utf-8") for p in sorted((project_dir / "tests").glob("test_*.py"))}

    by_stage = defaultdict(list)
    items = todos(project_dir)
    for it in items:      # __init__ & co. without their own stage: TASKS.md, else their class, else their file
        if it["stage"] is None:
            it["stage"] = stage_from_tasks(it, tasks, loose=False)
    for it in items:
        if it["stage"] is None:
            for same in (lambda o: o["file"] == it["file"] and o["cls"] == it["cls"] and it["cls"],
                         lambda o: o["file"] == it["file"]):
                stages = [o["stage"] for o in items if same(o) and o["stage"] is not None]
                if stages:
                    it["inherited"] = min(stages)
                    break
    for it in items:
        stage = it["stage"] or it.get("inherited") or stage_from_tasks(it, tasks, loose=True)
        by_stage[stage].append(it)

    name = skeleton.split("/")[-1]
    lines = [
        f"# {name} — the full checklist",
        "",
        f"Every function you still have to write in your skeleton: **{len(items)}**, in the order of `TASKS.md`.",
        "Tick each box when its tests are green. The text after each name is the first line of its TODO —",
        "the full instructions are in the docstring in your code. `HINTS.md` (next to this file) helps with the hard ones.",
        "",
        "Generated from your skeleton by `tools/make_checklists.py` — do not edit by hand.",
        "",
    ]
    for stage in sorted(by_stage, key=lambda s: (s is None, s or 0)):
        title = titles.get(stage, "") if stage is not None else ""
        lines.append(f"## Stage {stage} — {title}" if stage is not None else "## Not tied to a stage")
        lines.append("")
        current = None
        for it in by_stage[stage]:
            if it["file"] != current:
                if current is not None:
                    lines.append("")
                current = it["file"]
                lines.append(f"**`{current}`**")
                lines.append("")
            owner = f"{it['cls']}." if it["cls"] else ""
            line = f"- [ ] `{owner}{signature(it['fn'])}`"
            text = summary(it["doc"])
            if text:
                line += f" — {text}"
            hits = tests_for(it, tests)
            if hits:
                line += "  \n  ✅ checked by " + ", ".join(f"`tests/{h}`" for h in hits)
            lines.append(line)
        lines.append("")
        if stage in exits:
            lines += [f"> **Exit condition:** {exits[stage]}", ""]
    out = ROOT / project / "06_solve" / "CHECKLIST.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    unstaged = len(by_stage.get(None, []))
    print(f"{project}: {len(items)} functions, {len(by_stage) - (1 if unstaged else 0)} stages"
          + (f", {unstaged} without a stage" if unstaged else ""))


def main():
    for project, skeleton in PROJECTS.items():
        build(project, skeleton)


if __name__ == "__main__":
    main()
