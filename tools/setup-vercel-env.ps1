param(
  [string]$EnvFile = "backend\.env.local"
)
$ErrorActionPreference = "Stop"

Write-Host "=== Vercel Environment Variable Setup ===" -ForegroundColor Cyan

# Read the API key from local env file
$envPath = Join-Path $PSScriptRoot "..\$EnvFile"

if (-not (Test-Path $envPath)) {
  Write-Error "Environment file not found: $envPath"
  exit 1
}

Write-Host "Reading from: $envPath" -ForegroundColor Yellow

# Parse the env file for GEMINI_API_KEY or API_KEY
$apiKey = $null
Get-Content $envPath | ForEach-Object {
  if ($_ -match '^\s*(?:GEMINI_API_KEY|API_KEY|VITE_API_KEY)\s*=\s*(.+)$') {
    $apiKey = $matches[1].Trim().Trim('"').Trim("'")
  }
}

if (-not $apiKey) {
  Write-Error "No API_KEY, GEMINI_API_KEY, or VITE_API_KEY found in $envPath"
  exit 1
}

Write-Host "Found API key: $($apiKey.Substring(0, [Math]::Min(10, $apiKey.Length)))..." -ForegroundColor Green

# Set the environment variable in Vercel for all environments
Write-Host "`nSetting VITE_API_KEY in Vercel..." -ForegroundColor Cyan

# Production
Write-Host "Adding to Production..." -ForegroundColor Yellow
$apiKey | vercel env add VITE_API_KEY production

# Preview (optional)
Write-Host "`nAdding to Preview..." -ForegroundColor Yellow
$apiKey | vercel env add VITE_API_KEY preview

# Development (optional)
Write-Host "`nAdding to Development..." -ForegroundColor Yellow
$apiKey | vercel env add VITE_API_KEY development

Write-Host "`n✓ Environment variables configured!" -ForegroundColor Green
Write-Host "`nNow deploying to production..." -ForegroundColor Cyan

# Redeploy
vercel --prod --yes

Write-Host "`n✓ Deployment complete!" -ForegroundColor Green
