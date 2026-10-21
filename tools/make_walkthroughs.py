"""Write <project>/06_solve/WALKTHROUGH.md: every function of the project, stage by stage -
the problem in plain words, the finished code, and the tests that check it.

Reads the student's skeleton (../<Student>/<Project>/) for the list of functions and their stage,
and the teacher solution (../<Student>/_TEACHER_SOLUTION_do_not_send/<Project>/) for the code.

    python tools/make_walkthroughs.py
"""
import ast
import re
import textwrap
from collections import defaultdict
from pathlib import Path

import make_checklists as mc

ROOT = mc.ROOT
PACKAGES = mc.PACKAGES

JUNK = re.compile(r"\b(one|two|three|four|five|six) (lines?|steps?|things?)\b|written out|read this|worked example|"
                  r"^see\b|TODO|stage \d|in this (exact )?order|the whole method|that is the whole", re.I)
CODE = re.compile(r"[=\[\]{}]|\w+\(.*\)|->|^\d+\.\s|^[-*]\s|^(if|for|return|while|with|try|except|self\.)\b")


def prose(doc: str, limit: int = 3) -> str:
    """The plain-English part of a TODO docstring: the first few real sentences, no code."""
    text = mc.STAGE_IN_DOC.sub("", doc or "")
    paragraphs = re.split(r"\n\s*\n", textwrap.dedent(text).strip())
    sentences = []
    for para in paragraphs:
        lines = para.splitlines()
        if not lines or any(l.startswith((" ", "\t")) for l in lines[1:]) and lines[0].rstrip().endswith(":"):
            continue
        if sum(1 for l in lines if l.startswith("    ")) > len(lines) / 2:
            continue                                    # an indented code block
        flat = " ".join(l.strip() for l in lines).strip(" :-")
        for s in re.split(r"(?<=[.!?])\s+", flat):
            s = s.strip()
            if len(s) < 25 or JUNK.search(s) or CODE.search(s) or s.endswith(":"):
                continue
            s = re.sub(r"\b([A-Z]{3,})\b", lambda m: m.group(1) if m.group(1) in mc_caps else m.group(1).lower(), s)
            sentences.append(s[0].upper() + s[1:])
            if len(sentences) == limit:
                return " ".join(sentences)
    return " ".join(sentences)


mc_caps = {"URL", "SQL", "CSV", "JSON", "TCP", "GUI", "CNN", "FER", "BM25", "IDF", "PDF", "DOCX", "TXT", "SVM", "VAT",
           "ROC", "AUC", "FPS", "DNN", "RGB", "BGR", "LAN", "UCI", "PII", "HTML", "ISO", "GPU", "CPU", "UI", "ID", "MRR",
           "TF", "NB", "KNN", "CUDA", "AMP", "SHA", "UTF"}


def load_problems(project: str) -> dict:
    """Hand-written problem texts: blocks of 'file::Class.function' then the text, separated by blank lines."""
    path = Path(__file__).parent / "walkthrough_problems" / f"{project}.txt"
    if not path.exists():
        return {}
    out = {}
    for block in re.split(r"\n\s*\n", path.read_text(encoding="utf-8").strip()):
        key, _, text = block.strip().partition("\n")
        out[key.strip()] = " ".join(text.split())
    return out


def plain(name: str) -> str:
    """A fallback sentence from the function name: load_corpus -> 'Load corpus.'"""
    words = re.sub(r"^_+", "", name).replace("_", " ").strip()
    return (words[0].upper() + words[1:] + ".") if words else ""


def solution_source(solution_dir: Path, item) -> str:
    path = solution_dir / item["file"]
    if not path.exists():
        return ""
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    scope = tree.body
    if item["cls"]:
        cls = next((n for n in scope if isinstance(n, ast.ClassDef) and n.name == item["cls"]), None)
        if cls is None:
            return ""
        scope = cls.body
    fn = next((n for n in scope if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
               and n.name == item["fn"].name), None)
    if fn is None:
        return ""
    lines = source.splitlines()
    start = (fn.decorator_list[0].lineno if fn.decorator_list else fn.lineno) - 1
    body = lines[start:fn.end_lineno]
    first = fn.body[0]
    if isinstance(first, ast.Expr) and isinstance(getattr(first, "value", None), ast.Constant) \
            and isinstance(first.value.value, str) and len(fn.body) > 1:
        cut = range(first.lineno - 1 - start, first.end_lineno - start)
        body = [l for i, l in enumerate(body) if i not in cut]
    return textwrap.dedent("\n".join(body)).rstrip()


def _defs(tree):
    """{(class or None, name): node} for functions, plus top-level classes and assignments."""
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[(None, node.name)] = node
        elif isinstance(node, ast.ClassDef):
            out[("class", node.name)] = node
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    out[(node.name, sub.name)] = sub
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    out[("const", t.id)] = node
    return out


def added_code(solution_dir: Path, skeleton_dir: Path, rel: str) -> list:
    """Code in the solution file that the skeleton does not have: helpers, new classes, constants."""
    sol = solution_dir / rel
    if not sol.exists():
        return []
    sol_src = sol.read_text(encoding="utf-8")
    sol_defs = _defs(ast.parse(sol_src))
    skel = skeleton_dir / rel
    skel_defs = _defs(ast.parse(skel.read_text(encoding="utf-8"))) if skel.exists() else {}
    new_classes = {name for (kind, name) in sol_defs if kind == "class" and (kind, name) not in skel_defs}
    blocks = []
    for key, node in sol_defs.items():
        if key in skel_defs:
            continue
        kind, name = key
        if kind not in ("class", "const", None) and kind in new_classes:
            continue                                   # shown with its whole class
        start = (node.decorator_list[0].lineno if getattr(node, "decorator_list", None) else node.lineno) - 1
        segment = "\n".join(sol_src.splitlines()[start:node.end_lineno])     # whole lines, so dedent works
        if kind not in ("class", "const", None):
            segment = textwrap.dedent(segment)
            label, where = f"`{kind}.{name}`", kind
        else:
            label, where = f"`{name}`", None
        blocks.append((node.lineno, label, segment, where))
    return [(label, code, where) for _, label, code, where in sorted(blocks)]


def _bound(node) -> set:
    return {(a.asname or a.name).split(".")[0] for a in node.names}


def missing_imports(solution_dir: Path, skeleton_dir: Path, rel: str) -> list:
    """Import lines of the solution file whose names the skeleton file does not import yet."""
    sol = solution_dir / rel
    if not sol.exists():
        return []
    sol_src = sol.read_text(encoding="utf-8")
    skel = skeleton_dir / rel
    have = set()
    if skel.exists():
        for node in ast.parse(skel.read_text(encoding="utf-8")).body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                have |= _bound(node)
    out = []
    for node in ast.parse(sol_src).body:
        if isinstance(node, (ast.Import, ast.ImportFrom)) and not _bound(node) <= have:
            out.append(ast.get_source_segment(sol_src, node))
    return out


def new_files(solution_dir: Path, skeleton_dir: Path) -> list:
    out = []
    for py in sorted(solution_dir.rglob("*.py")):
        rel = py.relative_to(solution_dir)
        if {"tests", "data", "__pycache__"} & set(rel.parts):
            continue
        if not (skeleton_dir / rel).exists():
            out.append((rel.as_posix(), py.read_text(encoding="utf-8").rstrip()))
    return out


def test_names(item, tests_dir: Path) -> list:
    name = item["fn"].name
    if name.startswith("__"):
        name = item["cls"] or name
    word = re.compile(rf"\b{re.escape(name)}\b")
    hits = []
    for path in sorted(tests_dir.glob("test_*.py")):
        source = path.read_text(encoding="utf-8")
        for node in ast.parse(source).body:
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test"):
                if word.search(ast.get_source_segment(source, node) or ""):
                    hits.append(f"{path.name}::{node.name}")
    return hits


def run_section(project: str, solution_dir: Path) -> list:
    lines = ["## The finished project", ""]
    finished = Path(__file__).parent / "walkthrough_problems" / f"{project}_finished.md"
    if finished.exists():
        lines += [finished.read_text(encoding="utf-8").strip(), ""]
    shots = sorted((ROOT / project / "06_solve" / "screens").glob("*.png"))
    if shots:
        lines += ["### Screenshots", ""]
        for shot in shots:
            title = shot.stem.split("_", 1)[-1].replace("_", " ")
            lines += [f"**{title}**", "", f"![{title}](screens/{shot.name})", ""]
    return lines


def build(project: str, skeleton: str) -> None:
    skeleton_dir = PACKAGES / skeleton
    student, name = skeleton.split("/")
    solution_dir = PACKAGES / student / "_TEACHER_SOLUTION_do_not_send" / name
    tasks = (skeleton_dir / "TASKS.md").read_text(encoding="utf-8")
    titles = {}
    for first, last, title in mc.STAGE_HEADING.findall(tasks):
        for n in range(int(first), int(last or first) + 1):
            titles[n] = title.strip()
    for n, (title, _) in mc.ENGLISH_STAGES.get(project, {}).items():
        titles[n] = title

    items = mc.todos(skeleton_dir)
    for it in items:
        if it["stage"] is None:
            it["stage"] = mc.stage_from_tasks(it, tasks, loose=False)
    for it in items:
        if it["stage"] is None:
            same = [o["stage"] for o in items if o["file"] == it["file"] and o["stage"] is not None]
            it["stage"] = min(same) if same else mc.stage_from_tasks(it, tasks, loose=True)
    by_stage = defaultdict(list)
    for it in items:
        by_stage[it["stage"]].append(it)

    problems = load_problems(project)
    shown_files = set()
    missing, unwritten = 0, []
    lines = [
        f"# {name} — walkthrough",
        "",
        f"Every function you write in this project ({len(items)} of them), in the order of `TASKS.md`. For each one:",
        "",
        "- **Problem** — what the function has to do,",
        "- **Solution** — the finished code,",
        "- **Check** — the test that proves it works.",
        "",
        "Try each function yourself first, then compare. Run the check after every function, not at the end.",
        "",
        "## Where the code goes",
        "",
        f"Every path below starts in your project folder `{name}/` (the folder with `TASKS.md`). For each file:",
        "",
        "1. **Imports** — if the file section lists imports, add the lines that are missing to the top of the file, "
        "next to the other `import` lines.",
        "2. **Helper code** — paste it once, where the section says: *in the file* means below the imports and above "
        "the first class; *inside class X* means inside that class, next to its other methods (indented like them).",
        "3. **Each function** — in your skeleton, find the `def` with the same name. Delete the whole function — "
        "the `def` line, the TODO text and `raise NotImplementedError` — and paste the solution in its place. "
        "Inside a class, every line moves 4 spaces to the right, so the `def` lines up with the other methods.",
        "4. **New files** — at the end, under *Files the solution adds*: create the file at that path and paste "
        "the whole code.",
        "",
        "Before and after, for a method inside a class:",
        "",
        "```python",
        "class Example:",
        "",
        "    def total(self, items):          # BEFORE - the skeleton",
        "        \"\"\"",
        "        TODO stage 3: add up the prices.",
        "        \"\"\"",
        "        raise NotImplementedError",
        "```",
        "",
        "```python",
        "class Example:",
        "",
        "    def total(self, items):          # AFTER - the solution pasted in its place",
        "        return sum(item.price for item in items)",
        "```",
        "",
        "Then run the **Check** command from the project folder.",
        "",
        "## Contents",
        "",
    ]
    order = sorted(by_stage, key=lambda s: (s is None, s or 0))
    for stage in order:
        title = titles.get(stage, "") if stage is not None else "Other"
        anchor = re.sub(r"[^\w\- ]", "", f"stage {stage} — {title}".lower()).replace(" ", "-")   # GitHub's rule
        lines.append(f"- [Stage {stage} — {title}](#{anchor}) ({len(by_stage[stage])} functions)")
    if new_files(solution_dir, skeleton_dir):
        lines.append("- [Files the solution adds](#files-the-solution-adds)")
    lines += ["- [The finished project](#the-finished-project)", ""]

    for stage in order:
        title = titles.get(stage, "") if stage is not None else "Other"
        lines += [f"## Stage {stage} — {title}", ""]
        current = None
        for it in by_stage[stage]:
            if it["file"] != current:
                current = it["file"]
                lines += [f"### `{current}`", "", f"Open `{name}/{current}`.", ""]
                if current not in shown_files:
                    shown_files.add(current)
                    imports = missing_imports(solution_dir, skeleton_dir, current)
                    if imports:
                        lines += ["**Imports** — add these at the top of the file:", "",
                                  "```python", *imports, "```", ""]
                    extra = added_code(solution_dir, skeleton_dir, current)
                    if extra:
                        lines += ["**Helper code in this file** (used by the functions below, not a TODO in your skeleton):", ""]
                        for label, code, where in extra:
                            place = f"inside class `{where}`" if where else "in the file, below the imports"
                            lines += [f"{label} — paste {place}:", "", "```python", code, "```", ""]
            owner = f"{it['cls']}." if it["cls"] else ""
            lines += [f"#### `{owner}{mc.signature(it['fn'])}`", ""]
            key = f"{it['file']}::{owner}{it['fn'].name}"
            problem = problems.get(key)
            if problem is None:
                unwritten.append(key)
                problem = prose(it["doc"]) or plain(it["fn"].name)
            lines += [f"**Problem.** {problem}", ""]
            code = solution_source(solution_dir, it)
            if code:
                where = (f"inside class `{it['cls']}` (indented 4 spaces)" if it["cls"] else "at the top level of the file")
                lines += [f"**Solution.** Paste in `{it['file']}`, {where}, in place of the skeleton's "
                          f"`def {it['fn'].name}`:", "", "```python", code, "```", ""]
            else:
                missing += 1
            hits = test_names(it, skeleton_dir / "tests")
            if hits:
                by_file = defaultdict(list)
                for h in hits:
                    f, t = h.split("::")
                    by_file[f].append(t)
                cmds = []
                for f, names in by_file.items():
                    names = names[:4]
                    cmds.append(f"`pytest tests/{f}::{names[0]}`" if len(names) == 1
                                else f'`pytest tests/{f} -k "{" or ".join(names)}"`')
                lines += ["**Check.** " + " and ".join(cmds), ""]
            else:
                lines += ["**Check.** No unit test - run the program and look (see the stage's exit condition in `TASKS.md`).", ""]
        lines.append("")
    extra_files = new_files(solution_dir, skeleton_dir)
    if extra_files:
        lines += ["## Files the solution adds", "",
                  "These files are not in your skeleton; the finished project needs them. "
                  "Create each one at the path shown and paste the whole code.", ""]
        for rel, code in extra_files:
            lines += [f"### `{rel}`", "", f"Create `{name}/{rel}`:", "", "```python", code, "```", ""]
    lines += run_section(project, solution_dir)
    out = ROOT / project / "06_solve" / "WALKTHROUGH.md"
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(f"{project}: {len(items)} functions" + (f", {missing} without solution code" if missing else "")
          + (f", {len(unwritten)} without a written problem" if unwritten else ""))
    for key in unwritten if problems else []:
        print("   no problem text:", key)


def main():
    for project, skeleton in mc.PROJECTS.items():
        build(project, skeleton)


if __name__ == "__main__":
    main()
