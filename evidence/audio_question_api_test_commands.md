# Audio Question Practice API Test Commands

Run these from PowerShell after starting the backend on `http://127.0.0.1:8000`.

## Backend health

```powershell
curl.exe http://127.0.0.1:8000/
```

## LLM health

```powershell
curl.exe http://127.0.0.1:8000/llm/health
```

## Process a spoken-question transcript

```powershell
curl.exe -X POST http://127.0.0.1:8000/voice-practice/process-transcript `
  -H "Content-Type: application/json" `
  -d "{\"transcript\":\"How did you optimize Spark jobs in production?\",\"use_saved_context\":true}"
```

## Process transcript without saved context

```powershell
curl.exe -X POST http://127.0.0.1:8000/voice-practice/process-transcript `
  -H "Content-Type: application/json" `
  -d "{\"transcript\":\"Tell me about your data engineering background.\",\"use_saved_context\":false,\"resume_context\":\"Senior Data Engineer with related Spark, Databricks, ETL, and production support experience.\",\"job_description\":\"Senior Data Engineer role focused on Databricks, Spark, and data pipelines.\"}"
```

## Expected response shape

```json
{
  "transcript": "...",
  "detection": {
    "is_question": true,
    "question": "...",
    "category": "...",
    "topic": "..."
  },
  "generated_answer": {
    "provider": "ollama",
    "answer": "...",
    "warnings": []
  },
  "message": "Question detected and practice answer generated."
}
```
