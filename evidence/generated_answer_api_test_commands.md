# Generated Practice Answer API Test Commands

Run these from the project root after starting the backend on `http://127.0.0.1:8000`.

## Backend health

```powershell
curl.exe http://127.0.0.1:8000/
```

## Generate a practice answer

```powershell
curl.exe -X POST http://127.0.0.1:8000/practice/generate-answer `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"How did you optimize Spark jobs?\",\"category\":\"Spark / PySpark\",\"difficulty\":\"medium\",\"interviewer_intent\":\"Check practical Spark tuning experience.\",\"expected_answer_angle\":\"diagnosis, tuning actions, validation, and production impact\",\"follow_up_questions\":[\"How did you identify skew?\"],\"use_saved_context\":true}"
```

## Generate an answer with explicit context

```powershell
curl.exe -X POST http://127.0.0.1:8000/practice/generate-answer `
  -H "Content-Type: application/json" `
  -d "{\"question\":\"Tell me about your data engineering background.\",\"category\":\"Resume walkthrough\",\"difficulty\":\"easy\",\"interviewer_intent\":\"Understand the candidate profile.\",\"expected_answer_angle\":\"brief senior data engineering summary aligned to the role\",\"resume_context\":\"Senior Data Engineer with related Databricks, PySpark, Delta Lake, ETL, production support, and data quality experience.\",\"job_description\":\"Senior Data Engineer role focused on Spark, Databricks, ETL pipelines, and production support.\",\"use_saved_context\":false}"
```

## Practice session flow

```powershell
curl.exe -X POST http://127.0.0.1:8000/question-bank/generate `
  -H "Content-Type: application/json" `
  -d "{\"total_questions\":11,\"difficulty\":\"mixed\",\"use_saved_context\":true}"

curl.exe -X POST http://127.0.0.1:8000/practice/start `
  -H "Content-Type: application/json" `
  -d "{\"category_filter\":\"all\",\"difficulty_filter\":\"mixed\",\"max_questions\":1,\"shuffle\":false}"
```

Use the returned `current_question` fields from `/practice/start` as the body for `/practice/generate-answer`.
