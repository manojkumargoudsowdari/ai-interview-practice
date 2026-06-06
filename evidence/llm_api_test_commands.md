# LLM API Test Commands

Run these from PowerShell while the backend is running at `http://127.0.0.1:8000`.

## GET /llm/health

```powershell
curl.exe "http://127.0.0.1:8000/llm/health"
```

## POST /generate-cues with mock provider

Use `LLM_PROVIDER=mock` in `backend/.env`, restart the backend, then run:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/generate-cues" `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"How did you optimize Spark jobs?\",\"resume_context\":\"Related experience with Spark and Databricks pipelines.\",\"job_description\":\"Senior data engineer role using Azure and production SLAs.\"}"
```

## POST /generate-cues using saved resume/JD context

This call omits `resume_context` and `job_description`, so the backend uses saved context from `backend/data/processed/context.json`.

```powershell
curl.exe -X POST "http://127.0.0.1:8000/generate-cues" `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"How should I answer a Spark optimization question?\"}"
```

## Expected Ollama Setup Commands

```powershell
ollama --version
ollama pull llama3.1:8b
ollama list
```

## Example backend/.env for Mock

```env
APP_ENV=local
LLM_PROVIDER=mock

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
LLM_TIMEOUT_SECONDS=60
```

## Example backend/.env for Ollama

```env
APP_ENV=local
LLM_PROVIDER=ollama

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
LLM_TIMEOUT_SECONDS=60
```
