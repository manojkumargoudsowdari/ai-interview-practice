# Question Bank API Test Commands

Run these from PowerShell while the backend is running at `http://127.0.0.1:8000`.

## POST /question-bank/generate

```powershell
curl.exe -X POST "http://127.0.0.1:8000/question-bank/generate" `
  -H "Content-Type: application/json" `
  -d "{\"total_questions\":55,\"difficulty\":\"mixed\",\"use_saved_context\":true}"
```

## GET /question-bank

```powershell
curl.exe "http://127.0.0.1:8000/question-bank"
```

## DELETE /question-bank

```powershell
curl.exe -X DELETE "http://127.0.0.1:8000/question-bank"
```

## POST /question-bank/generate with total_questions: 11

```powershell
curl.exe -X POST "http://127.0.0.1:8000/question-bank/generate" `
  -H "Content-Type: application/json" `
  -d "{\"total_questions\":11,\"difficulty\":\"mixed\",\"use_saved_context\":true}"
```

## POST /question-bank/generate with saved context

```powershell
curl.exe -X POST "http://127.0.0.1:8000/question-bank/generate" `
  -H "Content-Type: application/json" `
  -d "{\"total_questions\":55,\"difficulty\":\"mixed\",\"use_saved_context\":true}"
```
