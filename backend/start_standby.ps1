# Start backend in standby (allow no DB) mode.
$ErrorActionPreference = "Stop"

# Ensure script runs from backend directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Export env vars to allow running without DB
$env:MOGRID_ALLOW_NO_DB = "true"
$env:MOGRID_MODE = "standby"

Write-Host "Starting MoStar GRID in STANDBY mode (no DB required)..." -ForegroundColor Cyan
Write-Host "MOGRID_ALLOW_NO_DB=$($env:MOGRID_ALLOW_NO_DB)  MOGRID_MODE=$($env:MOGRID_MODE)" -ForegroundColor Yellow
Write-Host ""

# Call the existing start script (keeps existing dependency checks and logging)
if (Test-Path ".\start_grid.ps1") {
    & .\start_grid.ps1
} else {
    Write-Host "start_grid.ps1 not found in $scriptDir" -ForegroundColor Red
    exit 1
}
