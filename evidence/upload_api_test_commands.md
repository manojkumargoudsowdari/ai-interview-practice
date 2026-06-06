# Upload API Test Commands

Run these from the project root while the backend is running at `http://127.0.0.1:8000`.

## POST /upload/resume with sample TXT file

```powershell
curl.exe -X POST "http://127.0.0.1:8000/upload/resume" `
  -F "file=@evidence/sample_inputs/sample_resume.txt"
```

## POST /upload/job-description-text

```powershell
curl.exe -X POST "http://127.0.0.1:8000/upload/job-description-text" `
  -H "Content-Type: application/json" `
  -d "{\"text\":\"Senior data engineer role focused on Spark, Databricks, Delta Lake, production pipelines, and Azure.\",\"source\":\"curl_pasted_job_description\"}"
```

## GET /context

```powershell
curl.exe "http://127.0.0.1:8000/context"
```

## DELETE /context

```powershell
curl.exe -X DELETE "http://127.0.0.1:8000/context"
```

## POST /generate-cues using saved context

This call omits `resume_context` and `job_description`, so the backend uses saved context from `backend/data/processed/context.json`.

```powershell
curl.exe -X POST "http://127.0.0.1:8000/generate-cues" `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"How should I answer a Spark optimization question?\"}"
```
