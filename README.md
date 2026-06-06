# AI Interview Practice

A visible interview training app with a FastAPI backend and React frontend.

The backend provides:

- Question detection
- Cue generation
- Answer scoring

The frontend provides a simple practice UI for calling those APIs.

## Run Backend

From the project root:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

## Run Frontend

Open a second PowerShell terminal from the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Build Frontend

```powershell
cd frontend
npm run build
```

## Run With Docker

Docker support currently covers the backend service.

```powershell
docker compose up --build
```

Open:

```text
http://localhost:8000/docs
```
