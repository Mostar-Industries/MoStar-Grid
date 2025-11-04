# MoStar GRID - Windows Startup Script
# Save as: start_grid.ps1

$ErrorActionPreference = "Stop"
$Host.UI.RawUI.WindowTitle = "MoStar GRID Coordinator"

# Function to handle errors (defined before use)
function Write-ErrorLog {
    param($ErrorMessage)
    Write-Host "❌ Error: $ErrorMessage" -ForegroundColor Red
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" | Out-Null
    }
    Add-Content -Path "logs\error.log" -Value "$(Get-Date) - $ErrorMessage"
}

try {
    Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║      MoStar GRID - Deployment Starting               ║" -ForegroundColor Cyan
    Write-Host "║      First African AI Homeworld                      ║" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""

    # Check if we're in the right directory
    if (-not (Test-Path "..\backend") -and -not (Test-Path "backend")) {
        Write-Host "❌ Error: backend directory not found" -ForegroundColor Red
        Write-Host "Please run this script from: C:\Users\AI\Documents\GitHub\MoStar-Grid" -ForegroundColor Yellow
        exit 1
    }

    # Ensure we are in backend
    if (Test-Path "backend") {
        cd backend
    } elseif (Test-Path "..\backend") {
        cd ..\backend
    }

    # Check if Python is installed
    try {
        $pythonVersion = python --version 2>&1
        Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-ErrorLog "Python not found"
        exit 1
    }

    # Verify PowerShell version
    if ($PSVersionTable.PSVersion.Major -lt 7) {
        Write-ErrorLog "PowerShell 7 or higher is required. Current version: $($PSVersionTable.PSVersion)"
        throw "PowerShell 7 or higher required"
    }

    # Set execution policy for current process
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force

    # Check if uvicorn is available specifically
    try {
        python -c "import uvicorn" 2>$null
    } catch {
        Write-Host "Installing uvicorn..." -ForegroundColor Yellow
        python -m pip install --upgrade uvicorn
    }

    # Check if dependencies are installed
    Write-Host ""
    Write-Host "📦 Checking dependencies..." -ForegroundColor Blue

    $packages = @("fastapi", "uvicorn", "asyncpg", "httpx", "pydantic")
    $missing = @()

    foreach ($package in $packages) {
        try {
            python -c "import $package" 2>$null
            Write-Host "  ✅ $package" -ForegroundColor Green
        } catch {
            Write-Host "  ❌ $package" -ForegroundColor Red
            $missing += $package
        }
    }

    if ($missing.Count -gt 0) {
        Write-Host ""
        Write-Host "Installing missing packages..." -ForegroundColor Yellow
        python -m pip install $missing
    }

    # Create logs directory if missing
    if (-not (Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" | Out-Null
        Write-Host "✅ Created logs directory" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "╔═══════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║          🚀 Starting MoStar GRID                     ║" -ForegroundColor Green
    Write-Host "╚═══════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Grid Coordinator will start on: http://localhost:7000" -ForegroundColor Cyan
    Write-Host "WebSocket stream at: ws://localhost:7000/ws/live-stream" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the Grid" -ForegroundColor Yellow
    Write-Host ""

    # Start the Grid with error handling and optional auto-restart once
    $env:PYTHONUNBUFFERED = "1"
    try {
        python grid_main.py
    } catch {
        Write-ErrorLog $_.Exception.Message
        Write-Host "Attempting one automatic restart..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        try {
            python grid_main.py
        } catch {
            Write-ErrorLog "Restart failed: $($_.Exception.Message)"
            throw
        }
    }

} catch {
    Write-ErrorLog $_.Exception.Message
    Write-Host "An unrecoverable error occurred. See logs\error.log for details." -ForegroundColor Red
    exit 1
}