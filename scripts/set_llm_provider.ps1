param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("mock", "ollama")]
    [string]$Provider,

    [string]$Model = "llama3.2:3b"
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$envPath = Join-Path $projectRoot "backend\.env"

$providerValue = $Provider.ToLowerInvariant()

$content = @(
    "APP_ENV=local"
    "LLM_PROVIDER=$providerValue"
    "OLLAMA_BASE_URL=http://localhost:11434"
    "OLLAMA_MODEL=$Model"
    "LLM_TIMEOUT_SECONDS=60"
) -join [Environment]::NewLine

Set-Content -LiteralPath $envPath -Value $content -Encoding UTF8

Write-Host "Wrote backend environment file:"
Write-Host $envPath
Write-Host ""
Write-Host "Final backend/.env content:"
Get-Content -LiteralPath $envPath
