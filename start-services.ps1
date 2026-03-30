# ==============================================================================
# MOSTAR GRID - UNIFIED SERVICE LAUNCHER (CLI Inline)
# Starts ALL services: Neo4j, Memory Layer, Core Engine, Mo Executor, Frontend
# ==============================================================================

$ErrorActionPreference = "Continue"
$ScriptPath = $PSScriptRoot

Write-Host ""
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "   MoStar-Grid: Inline System Boot" -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta

# --- Configuration ---
$Neo4jStart = Join-Path $ScriptPath "backend\neo4j-mostar-industries\start-neo4j.ps1"
$PythonExe = Join-Path $ScriptPath ".venv\Scripts\python.exe"
$FrontendPath = Join-Path $ScriptPath "frontend"
$LogsDir = Join-Path $ScriptPath "logs"
$ExecutorScript = Join-Path $ScriptPath "backend\mo_executor.py"

# --- Load Neo4j env from backend/.env ---
$envFile = Join-Path $ScriptPath "backend\.env"
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^(NEO4J_URI|NEO4J_USER|NEO4J_PASSWORD)=(.*)$') {
            Set-Variable -Name $matches[1] -Value $matches[2] -Scope Script
        }
    }
    Write-Host "   Loaded Neo4j config from backend/.env" -ForegroundColor Gray
}
else {
    Write-Host "   WARNING: backend/.env not found, using defaults" -ForegroundColor Yellow
}

# --- Always use AuraDB (override local bolt URI if set) ---
$NEO4J_URI = 'neo4j+s://371530ba.databases.neo4j.io'
$NEO4J_USER = 'neo4j'
$NEO4J_PASSWORD = 'mostar123'
Write-Host "   Using AuraDB: $NEO4J_URI" -ForegroundColor Gray

if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir | Out-Null }

# --- Helper: Kill process on port ---
function Stop-PortProcess {
    param([int]$Port)
    $conn = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" }
    if ($conn) {
        $procIds = $conn.OwningProcess | Sort-Object -Unique
        foreach ($p in $procIds) {
            $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
            if ($proc) {
                Write-Host "   >> Killing $($proc.ProcessName) (PID $p) on port $Port" -ForegroundColor Yellow
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            }
        }
        Start-Sleep -Milliseconds 500
    }
}

# --- Helper: Test if port is listening ---
function Test-PortListening {
    param([int]$Port)
    try {
        $result = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue -InformationLevel Quiet
        return $result
    }
    catch {
        return $false
    }
}

# --- 0. Clear stale processes ---
Write-Host "`n[0/5] Clearing stale processes on ports 3000, 8000, 8001..." -ForegroundColor DarkYellow
Stop-PortProcess -Port 8000
Stop-PortProcess -Port 8001
Stop-PortProcess -Port 3000

# Cleanup any lingering jobs from previous runs
Get-Job | Stop-Job -ErrorAction SilentlyContinue
Get-Job | Remove-Job -ErrorAction SilentlyContinue

Write-Host "   >> Ports cleared." -ForegroundColor Gray

# --- 1. Start Neo4j (Disabled: Using Aura) ---
Write-Host "`n[1/6] (Skipped) Starting Neo4j Database - Using Aura" -ForegroundColor Gray

# --- 2. Start Memory Layer API (Port 8000) ---
Write-Host "`n[2/6] Starting Memory Layer API (port 8000)..." -ForegroundColor Cyan
if (-not (Test-Path $PythonExe)) {
    Write-Host "   ❌ Python executable not found at $PythonExe" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "memory_layer.log"
    Start-Job -Name "MemoryLayer" -ScriptBlock {
        param($python, $scriptPath, $logFile, $neo4jUri, $neo4jUser, $neo4jPass)
        $env:PYTHONPATH = $scriptPath
        $env:PYTHONUTF8 = '1'
        $env:NEO4J_URI = $neo4jUri
        $env:NEO4J_USER = $neo4jUser
        $env:NEO4J_PASSWORD = $neo4jPass
        & $python -m uvicorn backend.memory_layer.api.main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $PythonExe, $ScriptPath, $logFile, $NEO4J_URI, $NEO4J_USER, $NEO4J_PASSWORD | Out-Null
    Start-Sleep -Seconds 2
}

# --- 3. Start Core Engine API (Port 8001) ---
Write-Host "`n[3/6] Starting Core Engine API (port 8001)..." -ForegroundColor Cyan
if (-not (Test-Path $PythonExe)) {
    Write-Host "   ❌ Python executable not found at $PythonExe" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "core_engine.log"
    Start-Job -Name "CoreEngine" -ScriptBlock {
        param($python, $scriptPath, $logFile, $neo4jUri, $neo4jUser, $neo4jPass)
        $env:PYTHONPATH = $scriptPath
        $env:PYTHONUTF8 = '1'
        $env:NEO4J_URI = $neo4jUri
        $env:NEO4J_USER = $neo4jUser
        $env:NEO4J_PASSWORD = $neo4jPass
        & $python -m uvicorn backend.core_engine.api_gateway:app --host 0.0.0.0 --port 8001 --reload 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $PythonExe, $ScriptPath, $logFile, $NEO4J_URI, $NEO4J_USER, $NEO4J_PASSWORD | Out-Null
    Start-Sleep -Seconds 2
}

# --- 4. Start Mo Executor ---
Write-Host "`n[4/6] Starting Mo Executor (graph mutation daemon)..." -ForegroundColor Cyan
if (-not (Test-Path $ExecutorScript)) {
    Write-Host "   ❌ Mo Executor script not found at $ExecutorScript" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "mo_executor.log"
    Start-Job -Name "MoExecutor" -ScriptBlock {
        param($python, $scriptPath, $executorScript, $logFile, $neo4jUri, $neo4jUser, $neo4jPass)
        $env:PYTHONPATH = $scriptPath
        $env:PYTHONUTF8 = '1'
        $env:NEO4J_URI = $neo4jUri
        $env:NEO4J_USER = $neo4jUser
        $env:NEO4J_PASSWORD = $neo4jPass
        & $python $executorScript 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $PythonExe, $ScriptPath, $ExecutorScript, $logFile, $NEO4J_URI, $NEO4J_USER, $NEO4J_PASSWORD | Out-Null
}

# --- 5. Start Next.js Frontend ---
Write-Host "`n[5/6] Starting Next.js Frontend (port 3000)..." -ForegroundColor Cyan
if (-not (Test-Path $FrontendPath)) {
    Write-Host "   ❌ Frontend directory not found at $FrontendPath" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "frontend.log"
    Start-Job -Name "Frontend" -ScriptBlock {
        param($frontendPath, $logFile)
        Set-Location $frontendPath
        npm run dev 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $FrontendPath, $logFile | Out-Null
    Start-Sleep -Seconds 2
}

# --- 6. Start Cloudflare Tunnel (mostar-grid - unified) ---
Write-Host "`n[6/6] Starting Cloudflare Tunnel (mostar-grid)..." -ForegroundColor Cyan
$CloudflaredExe = "C:\Users\idona\Downloads\cloudflared-windows-amd64.exe"
if (-not (Test-Path $CloudflaredExe)) {
    Write-Host "   ❌ cloudflared not found at $CloudflaredExe" -ForegroundColor Red
}
else {
    $logFileGrid = Join-Path $LogsDir "cloudflared_grid.log"
    
    # mostar-grid tunnel token (87d16259-105b-4604-850b-b14a1881fdb8)
    $GridToken = "eyJhIjoiYTI5NmFlN2I1ZjZkNmE2ZDZjMDAzY2Q4YmMzYzIyYTIiLCJzIjoiTWpVNFlUZzBPR1l0T0RVM1ppMDBPVEl6TFRrNE5Ua3RNVFZqTVdNellUUTVNVFEzIiwidCI6Ijg3ZDE2MjU5LTEwNWItNDYwNC04NTBiLWIxNGExODgxZmRiOCJ9"
    
    Start-Job -Name "CloudflaredGrid" -ScriptBlock {
        param($exe, $token, $logFile)
        & $exe tunnel run --token $token 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $CloudflaredExe, $GridToken, $logFileGrid | Out-Null

    Write-Host "   ✅ Cloudflare Tunnel (mostar-grid) starting in background..." -ForegroundColor Green
    Start-Sleep -Seconds 2
}

# --- Summary & Streaming Mode ---
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Services Started in Background Jobs     " -ForegroundColor Green
Write-Host "  Streaming logs... Press Ctrl+C to stop.  " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

try {
    Write-Host "Waiting for jobs to initialize..." -ForegroundColor DarkGray
    Start-Sleep -Seconds 5
    while ($true) {
        $jobs = Get-Job | Where-Object { $_.State -eq 'Running' }
        if (-not $jobs) {
            Write-Host "All jobs exited automatically." -ForegroundColor DarkGray
            break
        }
        foreach ($j in $jobs) {
            $output = Receive-Job -Job $j
            if ($output) {
                switch ($j.Name) {
                    "Neo4j" { $color = "Green" }
                    "MemoryLayer" { $color = "Cyan" }
                    "CoreEngine" { $color = "Yellow" }
                    "MoExecutor" { $color = "Magenta" }
                    "Frontend" { $color = "Blue" }
                    "CloudflaredGrid" { $color = "DarkCyan" }
                    default { $color = "White" }
                }
                foreach ($line in $output) {
                    Write-Host "[$($j.Name)] $line" -ForegroundColor $color
                }
            }
        }
        Start-Sleep -Milliseconds 500
    }
}
finally {
    Write-Host "`nStopping all processes..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Host "Done!" -ForegroundColor Green
}
