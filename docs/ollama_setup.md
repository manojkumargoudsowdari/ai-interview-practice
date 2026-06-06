# Ollama Setup

Ollama is used in this project for local LLM-backed cue generation. The app still works without Ollama by using the default `mock` provider.

## Install On Windows

Download and install Ollama from the official Ollama site manually.

If `winget` is available, you can also try:

```powershell
winget install Ollama.Ollama
```

## Verify Installation

```powershell
ollama --version
```

## Start Or Confirm The Service

Ollama Desktop may start the local service automatically.

If needed, start it manually:

```powershell
ollama serve
```

## Pull A Model

Recommended model:

```powershell
ollama pull llama3.1:8b
```

Alternative lighter model for weaker machines:

```powershell
ollama pull llama3.2:3b
```

List local models:

```powershell
ollama list
```

## Test Basic Generation

```powershell
ollama run llama3.1:8b 'Return only JSON: {"status":"ok"}'
```

## Configure Backend

Copy the Ollama example env file:

```powershell
Copy-Item backend\.env.ollama.example backend\.env -Force
```

Or set these values in `backend/.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
LLM_TIMEOUT_SECONDS=60
```

Restart the backend after changing `.env`.

## Test Backend Integration

Health check:

```text
GET http://127.0.0.1:8000/llm/health
```

Cue generation:

```text
POST http://127.0.0.1:8000/generate-cues
```

You can also run:

```powershell
.\scripts\check_ollama.ps1
.\scripts\backend_smoke_test.ps1
```
