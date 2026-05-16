# AI Career Coach + Interview Simulator

A Flask full-stack application for candidate resume analysis, AI mock interviews, interview evaluation, and recruiter review.

## Folder Structure

```text
AI_Coaching/
  app/
    admin/
    auth/
    candidate/
    services/
    static/
      css/
      js/
    templates/
      admin/
      auth/
      candidate/
      shared/
    __init__.py
    config.py
    extensions.py
    models.py
    utils.py
  uploads/
  .env.example
  requirements.txt
  run.py
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` and set:

```text
SECRET_KEY=your-long-random-secret
GROQ_API_KEY=your-groq-api-key
```

## Run

```powershell
python run.py
```

Open `http://127.0.0.1:5000`.

## Notes

- Candidate and admin users are selected during registration.
- Uploaded resumes are stored under `uploads/<user_id>/`.
- SQLite is used by default through `career_coach.db`.
- If `GROQ_API_KEY` is missing, the app uses local fallback analysis so the interface remains usable.
