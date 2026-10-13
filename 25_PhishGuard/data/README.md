# PhishGuard data

`phishing_urls.csv` — 11,430 URLs, 50% phishing, from the *Web page phishing detection* dataset
(`dataset_B_05_2020.csv`, only the `url` and `status` columns kept, renamed to `URL,Label` with
`good` / `bad` — the same format as the Kaggle file your project uses):
A. Hannousse and S. Yahiouche, *Towards benchmark datasets for machine learning based website phishing
detection: An experimental study*, Engineering Applications of Artificial Intelligence 104, 2021.
Data: https://doi.org/10.17632/c2gw7fy2j4.3 — Licence: CC BY 4.0.

Why not the PhiUSIIL dataset (UCI)? Every legitimate URL in it is a bare `https://www.site.com` homepage, so a
model learns "has a path → phishing" — a dataset artefact, not phishing. This dataset mixes both kinds in both
classes.
