# AthleteOS — Unified Physical + Mental Performance Platform (Mock-up)

A Streamlit mock-up of **AthleteOS**, a single platform that brings together an
athlete's **physical performance** data (training load, recovery, sleep, HRV, resting HR)
and **mental performance** indicators (stress, focus, confidence, motivation, mood) to
produce a holistic **readiness score** and actionable insights.

Built for two target user types:

- **Athletes** — see a personal dashboard with readiness, physical & mental trends, and a daily check-in form.
- **Coaches** — see a whole-team dashboard with readiness ranking, at-risk flags, and per-athlete drilldown.

> This is a demo. Data is sample-generated and resets on reload. New check-ins
> persist for the current browser session only (no database).

---

## Features

- Simple **role-selector login** (Athlete / Coach) with demo credentials.
- **Athlete dashboard:** readiness gauge, today's snapshot, manual daily check-in, 4-week physical & mental trend charts, and automatic insights/alerts.
- **Coach dashboard:** team KPIs, readiness bar chart (lowest first), roster table with progress bars, per-athlete drilldown, and recommended actions.
- **Readiness score:** blends physical (60%) and mental (40%) signals into one 0–100 number.
- **Insights engine:** rule-based alerts for overtraining, elevated stress, low motivation, sleep debt, and peak-readiness windows.
- 5 sample athletes across different sports.

---

## Demo logins

| Role    | Username | Password      |
|---------|----------|---------------|
| Coach   | `coach`  | `coach123`    |
| Athlete | `maya`   | `athlete123`  |
| Athlete | `diego`  | `athlete123`  |
| Athlete | `aiko`   | `athlete123`  |
| Athlete | `liam`   | `athlete123`  |
| Athlete | `sara`   | `athlete123`  |

---

## Project structure

```
.
├── app.py             # Entry point: login + routing between views
├── athlete_view.py    # Athlete dashboard
├── coach_view.py      # Coach dashboard
├── mock_data.py       # Sample data, readiness scoring, insights engine
├── requirements.txt   # Python dependencies
├── .streamlit/
│   └── config.toml    # Theme + server config
└── README.md
```

---

## Run in GitHub Codespaces

1. Push this repo to GitHub (see below).
2. On the repo page, click **Code → Codespaces → Create codespace on main**.
3. In the Codespace terminal:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
4. Codespaces will detect the running port (8501) and offer to open it in the browser.

---

## Deploy on Streamlit Community Cloud

1. Push this repository to **GitHub** (public or private).
2. Go to <https://share.streamlit.io> and sign in with GitHub.
3. Click **New app**, select your repository, branch (`main`), and set the
   **Main file path** to `app.py`.
4. Click **Deploy**. Streamlit installs `requirements.txt` automatically and
   gives you a public URL.

No secrets or environment variables are required for this mock-up.

---

## Push to GitHub (first time)

```bash
git init
git add .
git commit -m "Initial commit: AthleteOS mock-up"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```
