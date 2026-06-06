$ErrorActionPreference = "Stop"

$baseUrl = "http://127.0.0.1:8000"

Write-Host "Backend smoke test started at $(Get-Date -Format o)"
Write-Host "Backend base URL: $baseUrl"

try {
    $health = Invoke-RestMethod -Uri "$baseUrl/" -Method Get -TimeoutSec 10
} catch {
    Write-Error "Backend is not running at $baseUrl. Start it with: cd backend; .\.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"
    exit 1
}

Write-Host "Backend health:"
$health | ConvertTo-Json -Depth 5

$llmHealth = Invoke-RestMethod -Uri "$baseUrl/llm/health" -Method Get -TimeoutSec 10
Write-Host "LLM health:"
$llmHealth | ConvertTo-Json -Depth 5

$cueRequest = @{
    question = "How did you optimize Spark jobs?"
    resume_context = "Senior Data Engineer with Databricks, PySpark, Delta Lake, production pipelines, data quality, and performance tuning experience."
    job_description = "Looking for Senior Data Engineer with Spark, Databricks, ETL, production support, and performance optimization."
}

$cues = Invoke-RestMethod `
    -Uri "$baseUrl/generate-cues" `
    -Method Post `
    -ContentType "application/json" `
    -Body ($cueRequest | ConvertTo-Json -Depth 5) `
    -TimeoutSec 90

Write-Host "Cue provider: $($cues.provider)"
Write-Host "Cue points:"
$cues.cue_points | ForEach-Object { Write-Host "- $_" }
Write-Host "Short direction: $($cues.short_direction)"

Write-Host "Risk flags:"
if ($cues.risk_flags.Count -gt 0) {
    $cues.risk_flags | ForEach-Object { Write-Host "- $_" }
} else {
    Write-Host "- None"
}

Write-Host "Follow-up questions:"
if ($cues.follow_up_questions.Count -gt 0) {
    $cues.follow_up_questions | ForEach-Object { Write-Host "- $_" }
} else {
    Write-Host "- None"
}

Write-Host "Backend smoke test completed."
