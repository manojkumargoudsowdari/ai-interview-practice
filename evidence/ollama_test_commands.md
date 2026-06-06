# Ollama Test Commands

Run these from PowerShell in the project root unless noted otherwise.

## Check Ollama

```powershell
.\scripts\check_ollama.ps1
```

## Copy Env Example

```powershell
Copy-Item backend\.env.ollama.example backend\.env -Force
```

## Switch Provider With Helper Script

Set backend to Ollama:

```powershell
.\scripts\set_llm_provider.ps1 -Provider ollama -Model llama3.2:3b
```

Set backend back to mock:

```powershell
.\scripts\set_llm_provider.ps1 -Provider mock
```

## Start Backend

```powershell
cd backend
.\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Run Backend Smoke Test

From the project root:

```powershell
.\scripts\backend_smoke_test.ps1
```

## Start Frontend

```powershell
cd frontend
npm run dev
```

## Switch Back To Mock

Edit `backend/.env`:

```env
APP_ENV=local
LLM_PROVIDER=mock
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
LLM_TIMEOUT_SECONDS=60
```

Restart the backend after changing `.env`.
