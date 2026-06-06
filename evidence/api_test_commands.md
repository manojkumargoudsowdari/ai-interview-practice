# API Test Commands

Run these from PowerShell while the backend is running at `http://127.0.0.1:8000`.

## GET /

```powershell
curl.exe "http://127.0.0.1:8000/"
```

## POST /detect-question

```powershell
curl.exe -X POST "http://127.0.0.1:8000/detect-question" `
  -H "Content-Type: application/json" `
  -d '{"transcript":"Tell me about your background in Databricks.","resume_context":"","job_description":""}'
```

## POST /generate-cues

```powershell
curl.exe -X POST "http://127.0.0.1:8000/generate-cues" `
  -H "Content-Type: application/json" `
  -d '{"question":"How did you optimize Spark jobs?","resume_context":"","job_description":""}'
```

## POST /score-answer

```powershell
curl.exe -X POST "http://127.0.0.1:8000/score-answer" `
  -H "Content-Type: application/json" `
  -d '{"question":"How did you optimize Spark jobs?","answer":"I reviewed Spark UI stages, found shuffle skew, adjusted partitioning, and optimized file sizes. The pipeline became more stable in production and reduced latency for downstream reporting.","job_description":""}'
```
