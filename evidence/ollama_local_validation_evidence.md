# Ollama Local Validation Evidence

## 1. Branch Name

`feature/ollama-local-validation`

## 2. Summary of Validation Work

Added local Ollama setup documentation, environment examples, and PowerShell validation scripts for the AI Interview Practice backend.

This branch does not add large product changes. It improves developer setup reliability and validates the current provider-based cue generation path.

## 3. Files Created/Modified

Created:

- `backend/.env.ollama.example`
- `docs/ollama_setup.md`
- `scripts/check_ollama.ps1`
- `scripts/backend_smoke_test.ps1`
- `evidence/ollama_local_validation_evidence.md`
- `evidence/ollama_test_commands.md`
- `evidence/ollama_manual_test_checklist.md`

Modified:

- `.gitignore`
- `backend/app/services/llm_service.py`
- `frontend/src/App.tsx`
- `frontend/src/App.css`

## 4. Ollama Setup Status

Ollama setup documentation was added in `docs/ollama_setup.md`.

The docs cover:

- Windows install options
- `ollama --version`
- `ollama serve`
- `ollama pull llama3.1:8b`
- lighter model option: `llama3.2:3b`
- backend `.env` configuration
- backend health and cue-generation tests

## 5. Whether `ollama` Command Was Available

No. `scripts/check_ollama.ps1` failed because the `ollama` command was not found.

```text
Ollama command was not found. Install Ollama, then run: ollama --version
```

## 6. Whether Ollama API Was Reachable

No. Since the `ollama` command was unavailable, the script exited before API validation.

Earlier local API checks also indicated `localhost:11434` was not reachable.

## 7. Whether Required Model Was Available

Not verified. Ollama is not installed/running, so local model listing was not available.

Required/recommended model:

```text
llama3.1:8b
```

## 8. Backend `/llm/health` Result

Backend smoke test in current mock mode returned:

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

## 9. `/generate-cues` Result

Backend smoke test returned provider `mock` and cue points:

```text
Spark UI
shuffle
partitioning
skew
AQE
file size
result
Databricks
senior ownership
```

Short direction:

```text
Start with diagnosis, explain tuning actions, then finish with measurable impact.
```

Risk flags and follow-up questions were empty in mock mode.

## 10. Fallback Behavior Result If Ollama Was Unavailable

Fallback was tested by running the backend LLM service with:

```text
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://127.0.0.1:9
OLLAMA_MODEL=llama3.1:8b
LLM_TIMEOUT_SECONDS=5
```

Result:

- health provider: `ollama`
- health available: `false`
- generated cue provider: `mock`
- risk flag: `Ollama unavailable; used fallback cues.`
- backend did not crash

## 11. Commands Run

```powershell
git status --short --branch
git branch --show-current
Get-Content -Raw backend\app\config.py
Get-Content -Raw backend\app\services\llm_service.py
Get-Content -Raw backend\.env.example
python -m compileall app
npm run build
npm run lint
.\scripts\check_ollama.ps1
.\scripts\backend_smoke_test.ps1
LLM_PROVIDER=ollama fallback test with backend Python process
```

## 12. Test Results

- Backend compile passed.
- Frontend build passed.
- Frontend lint passed.
- `scripts/check_ollama.ps1` ran and correctly failed because Ollama is not installed.
- `scripts/backend_smoke_test.ps1` passed against `http://127.0.0.1:8000`.
- Ollama-unavailable fallback test passed.

## 13. Known Issues

- Real Ollama generation was not validated because Ollama is not installed on this machine.
- Required model availability could not be checked.
- The backend is currently validated in mock mode.
- To validate real Ollama generation, install Ollama, pull a model, switch `backend/.env`, and restart the backend.

## 14. Next Recommended Step

Install Ollama, run `ollama pull llama3.1:8b`, copy `backend/.env.ollama.example` to `backend/.env`, restart the backend, then run `scripts/backend_smoke_test.ps1`.
