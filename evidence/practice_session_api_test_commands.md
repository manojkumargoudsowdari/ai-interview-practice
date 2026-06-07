# Practice Session API Test Commands

Run these from PowerShell while the backend is running at `http://127.0.0.1:8000`.

## POST /question-bank/generate with total_questions 11

```powershell
curl.exe -X POST "http://127.0.0.1:8000/question-bank/generate" `
  -H "Content-Type: application/json" `
  -d "{\"total_questions\":11,\"difficulty\":\"mixed\",\"use_saved_context\":true}"
```

## POST /practice/start

```powershell
curl.exe -X POST "http://127.0.0.1:8000/practice/start" `
  -H "Content-Type: application/json" `
  -d "{\"category_filter\":\"all\",\"difficulty_filter\":\"mixed\",\"max_questions\":2,\"shuffle\":false}"
```

## POST /practice/answer

Replace `SESSION_ID` and `QUESTION_ID` with values returned by `/practice/start`.

```powershell
curl.exe -X POST "http://127.0.0.1:8000/practice/answer" `
  -H "Content-Type: application/json" `
  -d "{\"session_id\":\"SESSION_ID\",\"question_id\":\"QUESTION_ID\",\"answer\":\"I would start by checking Spark UI stages and task skew, then review shuffle volume, partitioning, file sizes, and job configuration. I would validate improvements with runtime and cost metrics before moving the change to production.\"}"
```

## GET /practice/session/{session_id}

```powershell
curl.exe "http://127.0.0.1:8000/practice/session/SESSION_ID"
```

## GET /practice/sessions

```powershell
curl.exe "http://127.0.0.1:8000/practice/sessions"
```

## DELETE /practice/sessions

```powershell
curl.exe -X DELETE "http://127.0.0.1:8000/practice/sessions"
```
