# Start backend and frontend locally for development (Windows PowerShell)

param(
    [int]$BackendPort = 7000,
    [int]$FrontendPort = 3000
)

# Start backend (runs start_grid.ps1)
Write-Host "Starting backend..."
Start-Process -NoNewWindow -FilePath "powershell" -ArgumentList "-ExecutionPolicy Bypass -File backend\start_grid.ps1"

# Start frontend if package.json exists in ./frontend
if (Test-Path "frontend\package.json") {
    Write-Host "Starting frontend (installing deps if needed)..."
    Push-Location "frontend"
    if (-not (Test-Path "node_modules")) {
        npm install
    }
    Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run", "dev"
    Pop-Location
} else {
    Write-Host "No frontend found at ./frontend. Please adjust path or create frontend folder." -ForegroundColor Yellow
}

Write-Host "Local dev startup invoked. Backend on http://localhost:$BackendPort  Frontend on http://localhost:$FrontendPort"
