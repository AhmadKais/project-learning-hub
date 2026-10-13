"""Copy each student's study-guide chapters (Markdown) into the hub.

The guides live next to the student packages, outside this repo:
    ../<Student>/מדריך_לתלמיד/src_en/*.md

Chapters are sorted by their role:
    01_theory/   the concepts and the math
    04_build/    architecture, code map and the stage-by-stage build chapters
    05_defence/  exam questions, answers, resources

Run again whenever a guide changes:   python tools/sync_guides.py
"""
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACKAGES = ROOT.parent

PROJECTS = {
    "05_LanGame": "Liraz_dakseh",
    "08_SpamClassifier": "Laith_Halabi",
    "13_FaceEmotion": "Ryan_raed",
    "18_HotelManager": "Eran_Nijm",
    "25_PhishGuard": "Dani_Faris",
    "31_ResumeMatch": "Kosai_Badreih",
    "32_WineGrader": "Seif_Ferro",
}

BUILD = re.compile(r"architecture|code_?map|codemap|build|stages|debugging|troubleshooting")
DEFENCE = re.compile(r"exam|answers|resources")


def target(name: str) -> str:
    if DEFENCE.search(name):
        return "05_defence"
    if BUILD.search(name):
        return "04_build"
    return "01_theory"


def main():
    for project, student in PROJECTS.items():
        src = PACKAGES / student / "מדריך_לתלמיד" / "src_en"
        for folder in ("01_theory", "04_build", "05_defence"):
            d = ROOT / project / folder
            if d.exists():
                shutil.rmtree(d)
            d.mkdir(parents=True)
        for md in sorted(src.glob("*.md")):
            dest = ROOT / project / target(md.stem) / md.name
            shutil.copy2(md, dest)
        print(f"{project}: {len(list(src.glob('*.md')))} chapters")


if __name__ == "__main__":
    main()
