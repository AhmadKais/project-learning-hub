"""Prove the walkthroughs are complete: copy each student skeleton, paste in everything WALKTHROUGH.md
tells the student to paste (imports, helper code, every function, new files), and run the tests.

    python tools/check_walkthroughs.py [project ...]
"""
import ast
import shutil
import subprocess
import sys
import tempfile
import textwrap
from collections import defaultdict
from pathlib import Path

import make_checklists as mc
import make_walkthroughs as mw

IGNORE = shutil.ignore_patterns(".venv", "venv", "__pycache__", ".pytest_cache", "*.zip")


def paste(project_dir: Path, solution_dir: Path, skeleton_dir: Path, rel: str, items: list) -> None:
    path = project_dir / rel
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    lines = source.splitlines()
    edits = []                                          # (line index, lines to remove, new lines)

    imports = mw.missing_imports(solution_dir, skeleton_dir, rel)
    top = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    after_imports = top[-1].end_lineno if top else 0
    helpers = mw.added_code(solution_dir, skeleton_dir, rel)
    module_code = [code for _, code, where in helpers if where is None]
    if imports or module_code:
        new = imports + [""] + [part for code in module_code for part in (code, "")]
        edits.append((after_imports, 0, new))

    classes = {n.name: n for n in tree.body if isinstance(n, ast.ClassDef)}
    for _, code, where in helpers:
        if where is not None:
            cls = classes[where]
            edits.append((cls.end_lineno, 0, [""] + textwrap.indent(code, "    ").splitlines()))

    for it in items:
        fn = it["fn"]
        start = (fn.decorator_list[0].lineno if fn.decorator_list else fn.lineno) - 1
        code = mw.solution_source(solution_dir, it)
        if not code:
            raise SystemExit(f"no solution code for {rel}::{fn.name}")
        edits.append((start, fn.end_lineno - start, textwrap.indent(code, " " * fn.col_offset).splitlines()))

    for at, remove, new in sorted(edits, key=lambda e: e[0], reverse=True):
        lines[at:at + remove] = new
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _functions(tree) -> dict:
    out = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out[node.name] = node
        elif isinstance(node, ast.ClassDef):
            out.update({f"{node.name}.{m.name}": m for m in node.body
                        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))})
    return out


def _without_docstring(fn) -> str:
    fn = ast.parse(ast.unparse(fn)).body[0]
    if fn.body and isinstance(fn.body[0], ast.Expr) and isinstance(getattr(fn.body[0], "value", None), ast.Constant):
        fn.body = fn.body[1:] or [ast.Pass()]
    return ast.dump(fn)


def given_differs(solution_dir: Path, skeleton_dir: Path) -> list:
    """Ready-made (non-TODO) skeleton functions that are not the same as in the solution -
    the walkthrough does not show them, so the student would never fix them."""
    out = []
    for py in sorted(skeleton_dir.rglob("*.py")):
        rel = py.relative_to(skeleton_dir)
        if mc.SKIP_DIRS & set(rel.parts) or not (solution_dir / rel).exists():
            continue
        skel = _functions(ast.parse(py.read_text(encoding="utf-8")))
        sol = _functions(ast.parse((solution_dir / rel).read_text(encoding="utf-8")))
        for name, fn in skel.items():
            if name in sol and not mc.raises_not_implemented(fn) and _without_docstring(fn) != _without_docstring(sol[name]):
                out.append(f"{rel.as_posix()}::{name}")
    return out


def check(project: str, skeleton: str) -> bool:
    skeleton_dir = mc.PACKAGES / skeleton
    student, name = skeleton.split("/")
    solution_dir = mc.PACKAGES / student / "_TEACHER_SOLUTION_do_not_send" / name
    with tempfile.TemporaryDirectory() as tmp:
        project_dir = Path(tmp) / name
        shutil.copytree(skeleton_dir, project_dir, ignore=IGNORE)
        by_file = defaultdict(list)
        for it in mc.todos(skeleton_dir):
            by_file[it["file"]].append(it)
        for py in sorted(solution_dir.rglob("*.py")):    # files with only helper code or imports to add
            rel = py.relative_to(solution_dir).as_posix()
            if (skeleton_dir / rel).exists() and not ({"tests", "data", "__pycache__"} & set(Path(rel).parts)):
                by_file.setdefault(rel, [])
        for rel, items in by_file.items():
            paste(project_dir, solution_dir, skeleton_dir, rel, items)
        for rel, code in mw.new_files(solution_dir, skeleton_dir):
            target = project_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(code + "\n", encoding="utf-8")
        left = mc.todos(project_dir)
        result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"],
                                cwd=project_dir, capture_output=True, text=True)
        last = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else result.stderr[-300:]
        differs = given_differs(solution_dir, skeleton_dir)
        ok = result.returncode == 0 and not left and not differs
        print(f"{project}: {'OK  ' if ok else 'FAIL'} {last}" + (f" | {len(left)} TODOs left" if left else ""))
        for d in differs:
            print("   skeleton differs from solution:", d)
        if not ok:
            print(result.stdout[-3000:])
        return ok


def main():
    wanted = sys.argv[1:]
    results = [check(p, s) for p, s in mc.PROJECTS.items() if not wanted or p in wanted]
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
