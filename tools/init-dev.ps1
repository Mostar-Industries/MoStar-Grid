param(
  [string]$BackendPath = "backend"
)
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$BackendFull = Join-Path $RepoRoot $BackendPath

Write-Host "=== Init Dev (Vite) ===" -ForegroundColor Cyan
if (-not (Test-Path $BackendFull)) { Write-Error "Backend path not found: $BackendFull"; exit 2 }

Push-Location $BackendFull
try {
  node -v
  npm -v
} catch {
  Write-Error "Node.js and npm are required. Install LTS (>=18) and retry."; Pop-Location; exit 3
}

try {
  if (Test-Path ".\package-lock.json") {
    Write-Host "npm ci..." -ForegroundColor Cyan
    npm ci
  } else {
    Write-Host "npm install..." -ForegroundColor Cyan
    npm install
  }
  Write-Host "Starting Vite dev server..." -ForegroundColor Cyan
  npm run dev
} finally {
  Pop-Location
}
