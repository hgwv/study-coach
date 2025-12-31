# Study Coach

**Live demo:** https://studycoach-fbfd.onrender.com

Study Coach is a data-informed study tracking web app that helps students understand *how* they study and build better habits using simple, explainable insights.

This project was built to practice full-stack development, data analysis, and turning user data into actionable feedback.

---

## Features

### Core functionality
- User authentication (register, log in, log out)
- Log study sessions with:
  - subject
  - duration (minutes)
  - self-reported focus rating (1–5)
- Create, complete, and delete tasks
- Personalized dashboard per user

### Weekly insights
Based on the last 7 days of study data, Study Coach calculates:
- Total minutes studied
- Number of days studied
- Average focus rating
- Time spent per subject
- Best-focus subject

Using these metrics, the app generates **rule-based coach notes**, such as:
- suggestions to improve consistency
- reminders to study more or rest
- feedback on focus quality

All insights are explainable and derived directly from user data.

---

## How the insights work (high level)

1. Study sessions from the last 7 days are queried from the database
2. Simple statistics are computed:
   - sums
   - averages
   - unique study days
3. If/else rules generate feedback messages based on thresholds  
   (e.g. low focus, high consistency, short study time)

This approach avoids “black-box AI” and keeps the logic transparent and interpretable.

---

## Tech stack

- **Backend:** Python, Flask
- **Auth:** Flask-Login
- **Database:** SQLite
- **ORM:** Flask-SQLAlchemy
- **Frontend:** Jinja templates, HTML/CSS
- **Deployment:** Render + Gunicorn

---

## Screenshots



---

## Local setup

```bash
git clone https://github.com/YOUR_USERNAME/study-coach.git
cd study-coach
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
Then open: http://127.0.0.1:5000

---
