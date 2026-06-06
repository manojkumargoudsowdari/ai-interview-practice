# Ollama Local Validation Evidence

## 1. Branch Name

`feature/ollama-local-validation`

## 2. Summary of Validation Work

Validated local Ollama setup with `llama3.2:3b`, fixed backend `.env` loading so configuration is read from `backend/.env` regardless of launch folder, and added a helper script for switching between `mock` and `ollama`.

## 3. Files Created/Modified

Created:

- `scripts/set_llm_provider.ps1`

Modified:

- `backend/app/config.py`
- `backend/app/main.py`
- `backend/app/services/llm_service.py`
- `backend/.env.ollama.example`
- `docs/ollama_setup.md`
- `evidence/ollama_local_validation_evidence.md`
- `evidence/ollama_manual_test_checklist.md`
- `evidence/ollama_test_commands.md`
- `scripts/check_ollama.ps1`

## 4. Ollama Setup Status

Ollama is installed and reachable.

## 5. Whether `ollama` Command Was Available

Yes.

```text
Ollama command found: C:\Users\manoj\AppData\Local\Programs\Ollama\ollama.exe
ollama version is 0.30.6
```

## 6. Whether Ollama API Was Reachable

Yes.

```text
Ollama API is reachable at http://localhost:11434/api/tags
```

## 7. Whether Required Model Was Available

Yes. `llama3.2:3b` is available and treated as valid for local validation.

```text
Available models:
- llama3.2:3b
llama3.2:3b is available and ready for local validation.
```

## 8. Backend `/llm/health` Result

After running:

```powershell
.\scripts\set_llm_provider.ps1 -Provider ollama -Model llama3.2:3b
```

and restarting the backend, `/llm/health` returned:

```json
{
  "provider": "ollama",
  "configured": true,
  "available": true,
  "message": "Ollama is reachable.",
  "ollama_base_url": "http://localhost:11434",
  "ollama_model": "llama3.2:3b"
}
```

## 9. `/generate-cues` Result

`scripts/backend_smoke_test.ps1` ran successfully and showed:

```text
Cue provider: ollama
```

The local `llama3.2:3b` model returned cue-generation content. A small guardrail was added so final API responses can normalize question-form cue points to short fallback cues while preserving a transparent risk flag.

## 10. Fallback Behavior Result If Ollama Was Unavailable

Fallback behavior was previously validated by configuring Ollama with an unreachable local URL. The backend returned mock fallback cues with a risk flag instead of crashing.

## 11. Environment Path Fix And Provider Switch Validation

- `backend/app/config.py` now resolves `backend/.env` with an absolute path based on `backend/app/config.py`.
- The backend reads the same `backend/.env` when imported from the project root or from the backend folder.
- `scripts/set_llm_provider.ps1` writes to `backend/.env` using a path relative to the script location, not the current terminal directory.
- `scripts/check_ollama.ps1` now accepts either `llama3.2:3b` or `llama3.1:8b`, with `llama3.2:3b` as the lightweight default.
- Smoke test now shows provider `ollama` after backend restart.

## 12. Commands Run

```powershell
git status --short --branch
git branch --show-current
git diff --check
python -m compileall app
npm run build
npm run lint
.\scripts\check_ollama.ps1
.\scripts\set_llm_provider.ps1 -Provider ollama -Model llama3.2:3b
Get-Content backend\.env
.\scripts\backend_smoke_test.ps1
```

Additional validation:

```powershell
$env:PYTHONPATH='backend'; .\backend\.venv\Scripts\python -c "from app.config import settings, ENV_FILE; print(ENV_FILE); print(settings.llm_provider); print(settings.ollama_model)"
cd backend
.\.venv\Scripts\python -c "from app.config import settings, ENV_FILE; print(ENV_FILE); print(settings.llm_provider); print(settings.ollama_model)"
```

Both checks resolved `D:\Work\Code\ai-interview-practice\backend\.env` and loaded `ollama` / `llama3.2:3b`.

## 13. Test Results

- Backend compile passed.
- Frontend build passed.
- Frontend lint passed.
- Ollama command check passed.
- Ollama API check passed.
- `llama3.2:3b` model detection passed.
- Provider switch script wrote the expected `backend/.env`.
- Backend smoke test passed and showed provider `ollama`.

## 14. Known Issues

- The local `llama3.2:3b` model may occasionally return question-form cue points. Guardrails now normalize those at the API boundary.
- Existing backend processes can hold port `8000`; restart the backend after switching providers.
- Real `backend/.env` remains ignored and must not be committed.

## 15. Next Recommended Step

Use the frontend to verify the LLM status panel and cue generation display while backend is running with `LLM_PROVIDER=ollama`.
