# Practice Session Mode Evidence

## 1. Branch Name

`feature/practice-session-mode`

## 2. Summary of Feature

Added Practice Session Mode for the AI Interview Practice App.

Users can start a practice session from the saved question bank, answer questions one at a time, score answers with the existing scoring service, advance through the session, and save session history locally.

## 3. Files Created/Modified

Modified:

- `.gitignore`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/question_bank_store.py`
- `frontend/src/App.tsx`
- `frontend/src/App.css`

Created:

- `backend/app/services/practice_session_store.py`
- `evidence/practice_session_mode_evidence.md`
- `evidence/practice_session_api_test_commands.md`
- `evidence/practice_session_manual_test_checklist.md`

Ignored runtime file:

- `backend/data/processed/practice_sessions.json`

## 4. Backend Endpoints Added

- `POST /practice/start`
- `POST /practice/answer`
- `GET /practice/session/{session_id}`
- `GET /practice/sessions`
- `DELETE /practice/sessions`

## 5. Frontend Sections Added

Added `Practice Session` section with:

- category filter dropdown
- difficulty dropdown
- max questions input
- shuffle checkbox
- start practice session button
- load latest session button
- clear practice sessions button
- current question card
- answer textarea
- submit answer button
- score feedback
- session summary display

## 6. Practice Session Behavior

- Loads saved question bank.
- Applies category and difficulty filters.
- Clamps `max_questions` between 1 and 50.
- Optionally shuffles questions.
- Creates a UUID session id.
- Saves question order, current index, answers, score payloads, and completion state.
- Scores answers with existing `score_answer`.
- Advances to the next question after each answer.
- Summarizes average score, weak categories, strong categories, history, and completion state.

## 7. Commands Run

```powershell
git status --short --branch
git branch --show-current
git diff --check
python -m compileall app
npm run build
npm run lint
Invoke-RestMethod -Uri 'http://127.0.0.1:8011/'
Invoke-RestMethod -Uri 'http://127.0.0.1:8011/llm/health'
Invoke-RestMethod -Uri 'http://127.0.0.1:8011/question-bank/generate' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8011/practice/start' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8011/practice/answer' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8011/practice/session/{session_id}'
Invoke-RestMethod -Uri 'http://127.0.0.1:8011/practice/sessions'
Invoke-RestMethod -Uri 'http://127.0.0.1:8011/practice/sessions' -Method Delete
```

Port note: API validation used `8011` to avoid stale local listeners on `8000`. The app routes are normal FastAPI routes and should run on `8000` after a clean backend restart.

## 8. Test Results

- Backend compile passed.
- Frontend build passed.
- Frontend lint passed.
- Backend health check passed.
- Generated question bank for session prerequisite.
- `POST /practice/start` passed.
- `POST /practice/answer` passed and returned score `6.5`.
- `GET /practice/session/{session_id}` returned answered count `1`.
- `GET /practice/sessions` returned total sessions `1`.
- `DELETE /practice/sessions` returned `practice_sessions_cleared`.
- Category filter passed with `Spark / PySpark`.
- Difficulty filter passed with `easy`.
- Max question minimum clamp passed with `max_questions: 0` returning `1`.

## 9. Known Issues

- Loading the latest session currently displays the latest saved summary/history. Continuing an older incomplete session from the frontend can be improved in a later branch.
- Validation used port `8011` due stale local listeners on `8000`.
- Practice sessions are local JSON storage only, not a multi-user database.

## 10. Next Recommended Step

Add a session history table with “resume incomplete session” support and per-category trend tracking.
