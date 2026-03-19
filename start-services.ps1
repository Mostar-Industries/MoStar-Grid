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

# --- 1. Start Neo4j ---
Write-Host "`n[1/5] Starting Neo4j Database (ports 7474/7687)..." -ForegroundColor Cyan
if (Test-PortListening -Port 7687) {
    Write-Host "   ✅ Neo4j already running on port 7687" -ForegroundColor Green
}
elseif (Test-Path $Neo4jStart) {
    Write-Host "   >> Launching Neo4j in background..." -ForegroundColor Gray
    # We run Neo4j in a background job too
    Start-Job -Name "Neo4j" -ScriptBlock {
        param($path)
        Set-Location $path
        .\start-neo4j.ps1
    } -ArgumentList (Join-Path $ScriptPath "backend\neo4j-mostar-industries") | Out-Null
    
    Write-Host "   >> Waiting for Neo4j to be ready (max 30s)..." -ForegroundColor Gray
    $waited = 0
    while ($waited -lt 30) {
        Start-Sleep -Seconds 2
        $waited += 2
        if (Test-PortListening -Port 7687) {
            Write-Host "   ✅ Neo4j ready after ${waited}s" -ForegroundColor Green
            break
        }
    }
}
else {
    Write-Host "   ❌ Neo4j start script not found at $Neo4jStart" -ForegroundColor Red
}

# --- 2. Start Memory Layer API (Port 8000) ---
Write-Host "`n[2/5] Starting Memory Layer API (port 8000)..." -ForegroundColor Cyan
if (-not (Test-Path $PythonExe)) {
    Write-Host "   ❌ Python executable not found at $PythonExe" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "memory_layer.log"
    Start-Job -Name "MemoryLayer" -ScriptBlock {
        param($python, $scriptPath, $logFile)
        $env:PYTHONPATH = $scriptPath
        $env:PYTHONUTF8 = '1'
        & $python -m uvicorn backend.memory_layer.api.main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $PythonExe, $ScriptPath, $logFile | Out-Null
    Start-Sleep -Seconds 2
}

# --- 3. Start Core Engine API (Port 8001) ---
Write-Host "`n[3/5] Starting Core Engine API (port 8001)..." -ForegroundColor Cyan
if (-not (Test-Path $PythonExe)) {
    Write-Host "   ❌ Python executable not found at $PythonExe" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "core_engine.log"
    Start-Job -Name "CoreEngine" -ScriptBlock {
        param($python, $scriptPath, $logFile)
        $env:PYTHONPATH = $scriptPath
        $env:PYTHONUTF8 = '1'
        & $python -m uvicorn backend.core_engine.api_gateway:app --host 0.0.0.0 --port 8001 --reload 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $PythonExe, $ScriptPath, $logFile | Out-Null
    Start-Sleep -Seconds 2
}

# --- 4. Start Mo Executor ---
Write-Host "`n[4/5] Starting Mo Executor (graph mutation daemon)..." -ForegroundColor Cyan
if (-not (Test-Path $ExecutorScript)) {
    Write-Host "   ❌ Mo Executor script not found at $ExecutorScript" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "mo_executor.log"
    Start-Job -Name "MoExecutor" -ScriptBlock {
        param($python, $scriptPath, $executorScript, $logFile)
        $env:PYTHONPATH = $scriptPath
        $env:PYTHONUTF8 = '1'
        $env:NEO4J_URI = 'bolt://localhost:7687'
        $env:NEO4J_USER = 'neo4j'
        $env:NEO4J_PASSWORD = 'mostar123'
        & $python $executorScript 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $PythonExe, $ScriptPath, $ExecutorScript, $logFile | Out-Null
}

# --- 5. Start Next.js Frontend ---
Write-Host "`n[5/5] Starting Next.js Frontend (port 3000)..." -ForegroundColor Cyan
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

# --- Summary & Streaming Mode ---
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  Services Started in Background Jobs     " -ForegroundColor Green
Write-Host "  Streaming logs... Press Ctrl+C to stop.  " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Note: Output logs from each service will be interleaved below." -ForegroundColor DarkGray
Write-Host ""

try {
    # Provide an initial flush and then loop
    while ($true) {
        $jobs = Get-Job | Where-Object { $_.State -eq 'Running' }
        if (-not $jobs) {
            Write-Host "All jobs exited automatically." -ForegroundColor DarkGray
            break
        }
        foreach ($j in $jobs) {
            $output = Receive-Job -Job $j
            if ($output) {
                # Add color prefix to logs for readability
                switch ($j.Name) {
                    "Neo4j"       { $color = "Green" }
                    "MemoryLayer" { $color = "Cyan" }
                    "CoreEngine"  { $color = "Yellow" }
                    "MoExecutor"  { $color = "Magenta" }
                    "Frontend"    { $color = "Blue" }
                    default       { $color = "White" }
                }
                foreach ($line in $output) {
                    $prefix = "[$($j.Name)]"
                    Write-Host "$prefix $line" -ForegroundColor $color
                }
            }
        }
        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host "`nStopping all processes..." -ForegroundColor Yellow
    Get-Job | Stop-Job
    Get-Job | Remove-Job
    Write-Host "Done!" -ForegroundColor Green
}
