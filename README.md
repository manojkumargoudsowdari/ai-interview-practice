# AI Interview Practice

A visible interview training app with a FastAPI backend and React frontend.

The backend provides:

- Question detection
- Cue generation
- Answer scoring

The frontend provides a simple practice UI for calling those APIs.

## Features

- Backend health check
- Question detection
- Resume upload for `.pdf`, `.txt`, and `.md`
- Job description paste or file upload for `.pdf`, `.txt`, and `.md`
- Local saved practice context
- Cue generation using saved or manual context
- Answer scoring

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

## Local Context Storage

Uploaded practice files are saved locally under `backend/data/uploads/`.
Extracted resume and job description context is saved under `backend/data/processed/context.json`.

These files are ignored by Git so private resumes and job descriptions are not committed.

## LLM Cue Generation

Cue generation defaults to the local mock/rule-based provider.

To use Ollama for local LLM-backed cue generation:

```powershell
ollama pull llama3.1:8b
```

Set `backend/.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
LLM_TIMEOUT_SECONDS=60
```

Restart the backend after changing `.env`.

## Run With Docker

Docker support currently covers the backend service.

```powershell
docker compose up --build
```

Open:

```text
http://localhost:8000/docs
```
