# ResumeMatch data

`resumes.csv` (200 CVs) and `jobs.csv` (5 adverts + the ids of the relevant CVs) are **synthetic** — invented by
`tools/make_resume_data.py` with a fixed seed. No real person's CV is used: CVs are personal data.

The generator plants traps on purpose: very long CVs that list many technologies, "keyword stuffers" that repeat
one skill 15 times, and a few CVs that copied a job advert without having its skills.
