"""Generate the synthetic CV collection for 31_ResumeMatch.

Real CVs are personal data, so the examples use invented ones. Everything here
is random but reproducible (fixed seed): run it again and you get the same files.

Writes into 31_ResumeMatch/data/:
    resumes.csv   id, role, text                          (200 CVs)
    jobs.csv      job_id, title, text, relevant_ids        (5 job adverts + the "right answers")

How the CVs are built, so the experiments have something to find:
  * 10 roles, each with core skills and optional skills
  * lengths vary a lot: some CVs are short, some are padded with long generic
    paragraphs (to show what BM25's b parameter does)
  * a few "keyword stuffers" repeat one skill many times (to show saturation, k1)
  * long CVs also list many technologies they only "touched" - realistic, and
    exactly what length normalisation is for
  * a few "advert copiers" paste sentences from a job advert without having its
    skills (to show the reliability check)
"""
import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "31_ResumeMatch" / "data"
rng = random.Random(2026)

ROLES = {
    "python_backend": (["Python", "Django", "PostgreSQL", "REST APIs"], ["Docker", "Redis", "Flask", "Celery", "AWS", "Git"]),
    "frontend": (["JavaScript", "React", "TypeScript", "CSS"], ["HTML", "Redux", "Webpack", "Figma", "Jest", "Git"]),
    "data_science": (["Python", "Machine Learning", "pandas", "scikit-learn"], ["SQL", "statistics", "TensorFlow", "NumPy", "Jupyter", "data visualisation"]),
    "devops": (["Kubernetes", "Docker", "CI/CD", "Linux"], ["Terraform", "AWS", "Bash", "Ansible", "monitoring", "Jenkins"]),
    "java_backend": (["Java", "Spring", "microservices", "SQL"], ["Kafka", "Hibernate", "Maven", "Docker", "MySQL", "REST APIs"]),
    "embedded": (["C++", "embedded systems", "RTOS", "microcontrollers"], ["C", "Linux", "debugging", "UART", "SPI", "Python"]),
    "dotnet": (["C#", ".NET", "ASP.NET", "SQL Server"], ["Azure", "Entity Framework", "Angular", "LINQ", "Git", "unit testing"]),
    "qa": (["test automation", "Selenium", "QA", "test plans"], ["Python", "Jira", "Cypress", "API testing", "SQL", "regression testing"]),
    "mobile": (["Kotlin", "Android", "Swift", "iOS"], ["Firebase", "REST APIs", "Jetpack Compose", "Git", "UI design", "Flutter"]),
    "sysadmin": (["Windows Server", "Active Directory", "networking", "Linux"], ["VMware", "Bash", "PowerShell", "backup", "firewalls", "monitoring"]),
}

FIRST = ["Noa", "Amir", "Yael", "Omar", "Dana", "Rami", "Maya", "Lior", "Sara", "Adam", "Hila", "Karim",
         "Tamar", "Yosef", "Rana", "Eitan", "Lina", "Nadav", "Shira", "Fadi"]
LAST = ["Cohen", "Haddad", "Levi", "Khoury", "Mizrahi", "Nasser", "Peretz", "Saleh", "Friedman", "Azar"]

SENTENCES = [
    "Built and maintained {s} for a production system used by thousands of users.",
    "Worked daily with {s} in a small team using agile methods.",
    "Led the migration of a legacy component to {s}.",
    "Wrote documentation and trained new team members in {s}.",
    "Improved performance of a critical service using {s}.",
    "Completed an online course in {s} and applied it in a personal project.",
    "Responsible for code reviews involving {s}.",
]
GENERIC = [
    "I am a motivated and hard working person who enjoys learning new things and working with people.",
    "In my free time I volunteer at a youth centre and play basketball with friends.",
    "I have excellent communication skills and I am always ready to take responsibility.",
    "During my military service I was responsible for logistics and scheduling for a large unit.",
    "I worked as a waiter and as a shift manager in a restaurant while studying.",
    "I enjoy travelling, reading history books and cooking for my family.",
    "I believe that good teamwork and respect are the basis of every successful project.",
    "I completed a matriculation certificate with an emphasis on mathematics and English.",
]

JOBS = [
    ("J1", "Backend Python developer", "python_backend",
     "We are looking for a backend developer with strong Python and Django experience. "
     "You will design REST APIs and work with PostgreSQL. Docker and Redis are an advantage."),
    ("J2", "Data scientist", "data_science",
     "Join our data team as a data scientist. Required: Python, Machine Learning, pandas and scikit-learn. "
     "Experience with statistics and SQL is an advantage."),
    ("J3", "DevOps engineer", "devops",
     "DevOps engineer to own our Kubernetes clusters and CI/CD pipelines. Docker and Linux are a must; "
     "Terraform and AWS are an advantage."),
    ("J4", "Embedded software engineer", "embedded",
     "Embedded software engineer: C++ on microcontrollers with an RTOS. Embedded systems experience required; "
     "debugging with UART and SPI is an advantage."),
    ("J5", "C# .NET developer", "dotnet",
     "Full stack C# developer for ASP.NET applications on .NET with SQL Server. Azure and Angular are an advantage."),
]


def cv_text(role, length, stuff=None, copy_from=None):
    core, optional = ROLES[role]
    skills = rng.sample(core, rng.randint(2, 3)) + rng.sample(optional, rng.randint(1, 4))
    rng.shuffle(skills)
    name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
    lines = [f"{name}. Email {name.split()[0].lower()}{rng.randint(10, 99)}@mail.com, phone 05{rng.randint(0, 9)}-{rng.randint(1000000, 9999999)}."]
    lines.append("Skills: " + ", ".join(skills) + ".")
    for s in skills:
        lines.append(rng.choice(SENTENCES).format(s=s))
    if stuff:
        lines.append(" ".join([stuff] * 15) + ".")
    if copy_from:
        lines.append(copy_from)
    if length >= 12:                     # long CVs list everything they ever touched
        others = [x for r in ROLES.values() for x in r[0] + r[1] if x not in skills]
        lines.append("Also familiar with " + ", ".join(rng.sample(others, 10)) + ".")
        lines.append("Previous roles included work with " + ", ".join(rng.sample(others, 6)) + ".")
    for _ in range(length):
        lines.append(rng.choice(GENERIC))
    return " ".join(lines)


def main():
    ROOT.mkdir(parents=True, exist_ok=True)
    resumes = []
    roles = list(ROLES)
    for i in range(200):
        role = roles[i % len(roles)]
        length = rng.choice([0, 0, 1, 2, 3, 12, 25])          # most short, some very long
        stuff = rng.choice(ROLES[role][0]) if i % 37 == 5 else None
        copy_from = None
        if i % 41 == 7:                                         # copies a job advert it does not fit
            job = rng.choice([j for j in JOBS if j[2] != role])
            copy_from = job[3]
        resumes.append((f"R{i:03d}", role, cv_text(role, length, stuff, copy_from)))

    with open(ROOT / "resumes.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["id", "role", "text"])
        w.writerows(resumes)

    with open(ROOT / "jobs.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["job_id", "title", "text", "relevant_ids"])
        for job_id, title, role, text in JOBS:
            relevant = [rid for rid, r, _ in resumes if r == role]
            w.writerow([job_id, title, text, " ".join(relevant)])
    print(f"wrote {len(resumes)} CVs and {len(JOBS)} jobs to {ROOT}")


if __name__ == "__main__":
    main()
