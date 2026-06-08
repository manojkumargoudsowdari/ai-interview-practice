# Generated Practice Answer Evidence

## Branch name

`feature/generated-practice-answer`

## Summary

Added a visible Practice Session option to generate a read-aloud draft answer for the current question. The generated answer fills the existing answer textarea so the user can practice aloud, edit the wording, and submit it for scoring.

The backend keeps provider behavior consistent with the existing app:

- `mock` returns a deterministic safe practice answer.
- `ollama` calls the local Ollama chat API.
- Ollama failure or parsing failure returns `ollama-fallback`.

Generated answers are instructed not to invent candidate experience. When saved context is missing, the fallback uses "related experience" and conceptual phrasing.

## Files created/modified

- `backend/app/schemas.py`
- `backend/app/main.py`
- `backend/app/services/answer_generator.py`
- `frontend/src/App.tsx`
- `frontend/src/App.css`
- `evidence/generated_answer_evidence.md`
- `evidence/generated_answer_api_test_commands.md`
- `evidence/generated_answer_manual_test_checklist.md`

## Backend endpoint added

- `POST /practice/generate-answer`

## Frontend section changed

- Practice Session now has a `Generate Answer` button for the current question.
- The generated answer displays provider and warnings.
- The generated answer fills the `My answer` textarea.

## Commands run

- `git switch -c feature/generated-practice-answer`
- `python -m compileall app` from `backend`
- `npm run build` from `frontend`
- `npm run lint` from `frontend`
- `git diff --check`
- `Invoke-RestMethod http://127.0.0.1:8000/`
- `Invoke-RestMethod http://127.0.0.1:8000/llm/health`
- `Invoke-RestMethod -Method Post http://127.0.0.1:8000/practice/generate-answer`
- `git status --short --branch`
- `git branch --show-current`

## Test results

- Backend compile passed.
- Frontend build passed.
- Frontend lint passed.
- `git diff --check` passed with line-ending warnings only.
- Backend health returned `status: running`.
- LLM health returned `provider: ollama`, `available: true`, `ollama_model: llama3.2:3b`.
- `POST /practice/generate-answer` returned `provider: ollama` and a concise read-aloud practice answer.
- Initial Ollama response parsing failed before JSON mode was added. After adding `"format": "json"`, the endpoint returned valid structured output.

Example endpoint result:

```json
{
  "provider": "ollama",
  "answer": "To optimize Spark jobs, I would start by analyzing the job's performance using tools like Databricks' built-in monitoring and profiling capabilities...",
  "warnings": []
}
```

## Known issues

- Generated answers are practice drafts, not proof of actual candidate experience.
- With no saved resume/JD context, fallback answers intentionally stay generic.

## Next recommended step

Run a live demo with a saved question bank, start a practice session, generate an answer, read it out loud, then submit it for scoring.
