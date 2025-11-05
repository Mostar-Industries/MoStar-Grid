$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendPath = Join-Path $scriptDir "frontend"

if (-not (Test-Path $frontendPath)) {
    Write-Host "❌ Frontend folder not found at $frontendPath" -ForegroundColor Red
    exit 1
}

# Check Node
try {
    $nodeV = node --version 2>$null
    Write-Host "✅ Node detected: $nodeV" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Install Node (v16+) and npm first." -ForegroundColor Red
    exit 1
}

# Start frontend in new window, install deps if needed, then run dev
$cmd = "cd `"$frontendPath`"; if (-not (Test-Path node_modules)) { Write-Host 'Installing frontend dependencies...'; npm install } ; Write-Host 'Starting frontend dev server...'; npm run dev"
Start-Process -FilePath "powershell" -ArgumentList "-NoExit","-ExecutionPolicy Bypass","-Command",$cmd

Write-Host "🔁 Frontend start command issued (new window)." -ForegroundColor Cyan
