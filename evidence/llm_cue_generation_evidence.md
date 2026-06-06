# LLM Cue Generation Evidence

## 1. Branch Name

`feature/llm-cue-generation`

## 2. Summary of Feature

Added provider-based cue generation for the visible AI Interview Practice App.

The backend now supports:

- `mock` provider using the existing rule-based cue generator.
- `ollama` provider using the local Ollama `/api/chat` API.
- Strict JSON response parsing from Ollama.
- Markdown/code-fence cleanup before parsing.
- Safe fallback to mock cues if Ollama is unavailable or returns invalid JSON.
- LLM provider health checks.

The frontend now shows LLM provider status and displays cue response metadata including provider, risk flags, and follow-up questions.

## 3. Files Created/Modified

Modified:

- `README.md`
- `backend/app/config.py`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/cue_generator.py`
- `frontend/README.md`
- `frontend/src/App.css`
- `frontend/src/App.tsx`

Created:

- `backend/.env.example`
- `backend/app/services/llm_service.py`
- `evidence/llm_cue_generation_evidence.md`
- `evidence/llm_api_test_commands.md`
- `evidence/llm_manual_test_checklist.md`

## 4. Backend Endpoints Added/Changed

Added:

- `GET /llm/health`

Changed:

- `POST /generate-cues`
  - Loads saved resume/JD context when request fields are omitted.
  - Uses `LLM_PROVIDER` to choose mock or Ollama.
  - Returns `provider`, `risk_flags`, and `follow_up_questions` in addition to the existing fields.

## 5. Frontend Sections Added/Changed

Added:

- `LLM Provider` section
  - Button: `Check LLM Provider`
  - Shows provider, configured state, available state, model, and message.

Changed:

- Cue generation result now shows:
  - provider used
  - cue points
  - short direction
  - risk flags if present
  - follow-up questions if present

## 6. Provider Behavior

Mock:

- Uses existing rule-based cue generation.
- Requires no local model.
- Default provider in `.env.example`.

Ollama:

- Calls `POST {OLLAMA_BASE_URL}/api/chat`.
- Uses configured `OLLAMA_MODEL`.
- Requests strict JSON with `cue_points`, `short_direction`, `risk_flags`, and `follow_up_questions`.
- Falls back to mock cues if Ollama is unavailable or parsing fails.

## 7. Commands Run

```powershell
git status --short --branch
git branch --show-current
rg --files
.\.venv\Scripts\python -m compileall app
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/llm/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/generate-cues' -Method Post
ollama --version
Invoke-RestMethod -Uri 'http://localhost:11434/api/tags' -TimeoutSec 5
LLM_PROVIDER=ollama fallback test through a backend Python process
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/context' -Method Delete
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/upload/resume' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/upload/job-description-text' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/generate-cues' -Method Post
npm run lint
npm run build
```

## 8. Test Results

- Backend compile passed.
- Backend health check passed:

```json
{"app":"AI Interview Practice App","env":"local","status":"running"}
```

- `/llm/health` in mock mode passed.
- `/generate-cues` in mock mode passed.
- `/generate-cues` using saved resume/JD context passed.
- Frontend lint passed.
- Frontend build passed.

## 9. Mock Provider Test Result

```json
{
  "provider": "mock",
  "configured": true,
  "available": true,
  "message": "Mock provider is configured and available.",
  "ollama_base_url": null,
  "ollama_model": null
}
```

Mock cue generation returned provider `mock`, cue points, short direction, and empty `risk_flags` / `follow_up_questions` arrays.

## 10. Ollama Provider Test Result

Ollama was not installed or running on this machine:

```text
ollama: The term 'ollama' is not recognized
localhost:11434 refused connection
```

## 11. Fallback Test Result

Fallback was tested by running the backend LLM service in a separate Python process with:

```text
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:9
```

Result:

- Health returned `available=false`.
- Cue generation did not crash.
- Response used provider `mock`.
- Response included risk flag: `Ollama unavailable; used fallback cues.`

## 12. Known Issues

- Ollama was not available locally, so a successful real Ollama generation was not tested.
- LLM response parsing is strict by design; malformed model output falls back to mock cues.
- Frontend API base URL remains hard-coded to `http://127.0.0.1:8000`.
- Cue generation still returns short coaching cues, not full answer scripts.

## 13. Next Recommended Step

Install Ollama, pull `llama3.1:8b`, set `LLM_PROVIDER=ollama`, and run a real local model test through both Swagger and the frontend.
