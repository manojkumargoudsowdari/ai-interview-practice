# AI Interview Practice

FastAPI backend for question detection, cue generation, and answer scoring.

## Run Locally

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`.

## Run With Docker

```powershell
docker compose up --build
```

Open `http://localhost:8000/docs`.
