# Audio Question Practice Evidence

## Branch name

`feature/audio-question-practice`

## Summary

Added a visible audio question practice workflow:

- Browser microphone captures a spoken interviewer question.
- Browser speech recognition converts the audio to editable text.
- Backend detects whether the transcript is an interview question.
- Backend generates a read-aloud answer using saved resume/JD context.

Ollama is used for answer generation when configured. Audio transcription is handled by the browser SpeechRecognition API to keep the local setup lightweight.

## Files created/modified

- `backend/app/schemas.py`
- `backend/app/main.py`
- `frontend/src/App.tsx`
- `frontend/src/App.css`
- `evidence/audio_question_practice_evidence.md`
- `evidence/audio_question_api_test_commands.md`
- `evidence/audio_question_manual_test_checklist.md`

## Backend endpoint added

- `POST /voice-practice/process-transcript`

## Frontend section added

- `Live Audio Question`

Controls:

- `Start Listening`
- `Stop`
- `Generate Answer`
- `Clear`
- `Use saved resume/JD context`

## Commands run

- `git switch -c feature/audio-question-practice`
- `python -m compileall app` from `backend`
- `npm run build` from `frontend`
- `npm run lint` from `frontend`
- `git diff --check`
- `Invoke-RestMethod http://127.0.0.1:8000/`
- `Invoke-RestMethod http://127.0.0.1:8000/llm/health`
- `Invoke-RestMethod -Method Post http://127.0.0.1:8000/voice-practice/process-transcript`
- `git status --short --branch`

## Test results

- Backend compile passed.
- Frontend build passed.
- Frontend lint passed.
- `git diff --check` passed with line-ending warnings only.
- Backend health returned `status: running`.
- LLM health returned `provider: ollama`, `available: true`, `ollama_model: llama3.2:3b`.
- `POST /voice-practice/process-transcript` with saved context returned:
  - `detection.is_question: true`
  - `detection.topic: Spark / PySpark`
  - `generated_answer.provider: ollama`
  - message: `Question detected and practice answer generated.`
- `POST /voice-practice/process-transcript` without saved context returned `provider: ollama` plus warnings that no saved resume/JD context was available.
- Browser microphone capture was not tested from terminal. Manual browser test is documented in `evidence/audio_question_manual_test_checklist.md`.

## Known issues

- Browser speech recognition is not supported in every browser. Use Chrome or Edge on `localhost`.
- The backend does not store audio files.
- Ollama generates the answer; the browser handles speech-to-text for this MVP.

## Next recommended step

Add optional backend speech-to-text support with a local model only if browser transcription is not enough.
