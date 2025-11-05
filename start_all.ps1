# Start both backend and frontend in separate PowerShell windows (Windows)
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not $root) { $root = "C:\Users\AI\Documents\GitHub\MoStar-Grid" }

$backendPath = Join-Path $root "backend"
$frontendPath = Join-Path $root "frontend"
$backendScript = Join-Path $backendPath "start_grid.ps1"

if (-not (Test-Path $backendScript)) {
    Write-Host "❌ backend\start_grid.ps1 not found at $backendScript" -ForegroundColor Red
    exit 1
}

Write-Host "🔁 Starting backend in a new window..." -ForegroundColor Cyan
$backendCmd = "cd `"$backendPath`"; .\start_grid.ps1"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-ExecutionPolicy Bypass","-Command",$backendCmd

# Wait for backend readiness
$healthUrl = "http://localhost:7000/health"
$maxWaitSec = 60
$elapsed = 0
$ready = $false

Write-Host "⏳ Waiting for backend to respond at $healthUrl (timeout ${maxWaitSec}s)..." -ForegroundColor Yellow
while ($elapsed -lt $maxWaitSec) {
    Start-Sleep -Seconds 1
    $elapsed += 1
    try {
        $resp = Invoke-WebRequest -Uri $healthUrl -UseBasicParsing -Method GET -TimeoutSec 2 -ErrorAction Stop
        if ($resp.StatusCode -eq 200) { $ready = $true; break }
    } catch {
        # still waiting
    }
}

if ($ready) {
    Write-Host "✅ Backend is up (after $elapsed seconds)." -ForegroundColor Green
} else {
    Write-Host "⚠️ Backend did not respond within timeout ($maxWaitSec s). Proceeding to start frontend anyway." -ForegroundColor Yellow
}

if (-not (Test-Path $frontendPath)) {
    Write-Host "⚠️ Frontend folder not found at $frontendPath; skipping frontend startup." -ForegroundColor Yellow
    exit 0
}

# Start frontend in new window; ensure dependencies installed
Write-Host "🔁 Starting frontend in a new window..." -ForegroundColor Cyan
$frontendCmd = "cd `"$frontendPath`"; if (-not (Test-Path node_modules)) { npm install } ; npm run dev"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-ExecutionPolicy Bypass","-Command",$frontendCmd

Write-Host "🚀 Started backend and frontend (if available). Open http://localhost:3000 for frontend and http://localhost:7000 for backend." -ForegroundColor Green
