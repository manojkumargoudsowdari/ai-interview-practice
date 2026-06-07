# Question Bank Generation Evidence

## 1. Branch Name

`feature/question-bank-generation`

## 2. Summary of Feature

Added JD/resume-specific interview question bank generation for the visible AI Interview Practice App.

The backend can generate, save, load, and clear a categorized question bank using saved resume/JD context. The generator supports Ollama and deterministic fallback behavior. The frontend now has a `Question Bank` section for generating, loading, clearing, and reviewing grouped practice questions.

## 3. Files Created/Modified

Modified:

- `.gitignore`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `frontend/src/App.css`
- `frontend/src/App.tsx`

Created:

- `backend/app/services/question_bank_generator.py`
- `backend/app/services/question_bank_store.py`
- `evidence/question_bank_generation_evidence.md`
- `evidence/question_bank_api_test_commands.md`
- `evidence/question_bank_manual_test_checklist.md`

Ignored runtime file:

- `backend/data/processed/question_bank.json`

## 4. Backend Endpoints Added

- `POST /question-bank/generate`
- `GET /question-bank`
- `DELETE /question-bank`

## 5. Frontend Sections Added

Added `Question Bank` section with:

- total questions input
- difficulty selector
- saved context checkbox
- generate button
- load saved question bank button
- clear question bank button
- provider and total display
- warnings display
- grouped question cards by category

Each question card displays:

- difficulty
- question
- interviewer intent
- expected answer angle
- follow-up questions

## 6. Provider Behavior

- `mock`: deterministic fallback bank.
- `ollama`: calls local Ollama `/api/chat`, parses strict JSON, normalizes categories/difficulty, and fills missing questions with fallback questions if needed.
- `ollama-fallback`: used when Ollama is configured but unavailable or returns invalid/unusable JSON.

## 7. Commands Run

```powershell
git status --short --branch
git branch --show-current
git diff --check
python -m compileall app
npm run build
npm run lint
.\scripts\set_llm_provider.ps1 -Provider ollama -Model llama3.2:3b
Invoke-RestMethod -Uri 'http://127.0.0.1:8010/'
Invoke-RestMethod -Uri 'http://127.0.0.1:8010/llm/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:8010/question-bank/generate' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8010/question-bank'
Invoke-RestMethod -Uri 'http://127.0.0.1:8010/question-bank' -Method Delete
```

Port note: validation used `8010` because stale local listeners were still serving old code on `8000`. The implemented endpoints are normal FastAPI routes and will run on `8000` after restarting the backend cleanly.

## 8. Test Results

- Backend compile passed.
- Frontend build passed.
- Frontend lint passed.
- Backend health check passed.
- `/llm/health` passed with provider `ollama`.
- `POST /question-bank/generate` with `total_questions: 11` passed.
- `GET /question-bank` returned saved preview metadata.
- `DELETE /question-bank` returned `question_bank_cleared`.
- Clamp behavior passed: request with `total_questions: 5` returned `11`.
- `backend/data/processed/question_bank.json` is ignored by Git.

## 9. Ollama Result

Ollama was available with `llama3.2:3b`.

Generation result:

```text
provider: ollama
total_questions: 11
categories: 11
```

## 10. Fallback Result

Fallback was tested in a separate backend Python process with an unreachable Ollama URL.

Result:

```text
provider: ollama-fallback
total_questions: 11
```

Warnings included:

```text
Ollama question bank generation failed; used fallback questions.
```

## 11. Known Issues

- Ollama may return fewer questions than requested; the backend fills the remainder with deterministic fallback questions.
- Very large banks are intentionally clamped to 110 questions. Paging/batch generation can be added later.
- Port `8000` had stale local listeners during validation; restart backend processes before testing on the normal port.

## 12. Next Recommended Step

Use the frontend on a clean backend restart at port `8000` to review generated questions and tune the prompt/category balance based on actual interview practice.
