# AI Interview Practice Frontend

React + TypeScript frontend for the AI Interview Practice App.

The UI supports backend health checks, question detection, resume/JD context upload, cue generation, and answer scoring.

## Run

Start the FastAPI backend first at `http://127.0.0.1:8000`.

Then run:

```powershell
npm install
npm run dev
```

Open:

```text
http://localhost:5173
```

## Build

```powershell
npm run build
```

## Lint

```powershell
npm run lint
```

## LLM Provider

The default backend provider is `mock`, so the app works without a local model.

To use Ollama:

```powershell
ollama pull llama3.1:8b
```

Set these values in `backend/.env`, then restart the backend:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
LLM_TIMEOUT_SECONDS=60
```
