$ErrorActionPreference = "Stop"

Write-Host "Ollama validation started at $(Get-Date -Format o)"

$ollamaCommand = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollamaCommand) {
    Write-Error "Ollama command was not found. Install Ollama, then run: ollama --version"
    exit 1
}

Write-Host "Ollama command found: $($ollamaCommand.Source)"
Write-Host "Version:"
ollama --version

$tagsUrl = "http://localhost:11434/api/tags"

try {
    $tags = Invoke-RestMethod -Uri $tagsUrl -Method Get -TimeoutSec 10
} catch {
    Write-Error "Ollama API is not reachable at $tagsUrl. Start Ollama Desktop or run: ollama serve"
    exit 1
}

Write-Host "Ollama API is reachable at $tagsUrl"

$models = @()
if ($tags.models) {
    $models = @($tags.models | ForEach-Object { $_.name })
}

if ($models.Count -eq 0) {
    Write-Host "No local Ollama models were returned."
} else {
    Write-Host "Available models:"
    $models | ForEach-Object { Write-Host "- $_" }
}

$requiredModel = "llama3.1:8b"
if ($models -notcontains $requiredModel) {
    Write-Host "Recommended model is missing. Pull it with:"
    Write-Host "ollama pull $requiredModel"
}

Write-Host "Ollama validation completed."
