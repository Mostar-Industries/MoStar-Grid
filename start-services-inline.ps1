# ==============================================================================
# MOSTAR GRID - INLINE SERVICE LAUNCHER (IDE terminal visible output)
# Starts services in foreground with direct output to IDE terminal
# ==============================================================================

$ErrorActionPreference = "Continue"
$ScriptPath = $PSScriptRoot

Write-Host ""
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "   MoStar-Grid: Inline System Boot       " -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta

# --- Configuration ---
$Neo4jStart = Join-Path $ScriptPath "backend\neo4j-mostar-industries\start-neo4j.ps1"
$PythonExe = Join-Path $ScriptPath ".venv\Scripts\python.exe"
$FrontendPath = Join-Path $ScriptPath "frontend"
$LogsDir = Join-Path $ScriptPath "logs"
$ExecutorScript = Join-Path $ScriptPath "backend\mo_executor.py"

# Resolve to absolute paths (required for Start-Job which runs in a separate process)
$PythonExe = (Resolve-Path $PythonExe -ErrorAction SilentlyContinue).Path
$ScriptPath = (Resolve-Path $ScriptPath -ErrorAction SilentlyContinue).Path

# --- Load Neo4j config from backend/.env ---
$envFile = Join-Path $ScriptPath "backend\.env"
$Neo4jUri = 'bolt://localhost:7687'
$Neo4jUser = 'neo4j'
$Neo4jPass = ''
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^NEO4J_URI=(.+)$') { $script:Neo4jUri = $matches[1].Trim() }
        if ($_ -match '^NEO4J_PASSWORD=(.+)$') { $script:Neo4jPass = $matches[1].Trim() }
        if ($_ -match '^NEO4J_USER=(.+)$') { $script:Neo4jUser = $matches[1].Trim() }
    }
    Write-Host "   Neo4j config: $Neo4jUri (from backend/.env)" -ForegroundColor Gray
}
else {
    Write-Host "   backend/.env not found, using defaults" -ForegroundColor Yellow
}

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
Write-Host "   >> Ports cleared." -ForegroundColor Gray

# --- 1. Start Neo4j ---
Write-Host "`n[1/5] Starting Neo4j Database (ports 7474/7687)..." -ForegroundColor Cyan
if (Test-PortListening -Port 7687) {
    Write-Host "   ✅ Neo4j already running on port 7687" -ForegroundColor Green
}
elseif (Test-Path $Neo4jStart) {
    Write-Host "   >> Launching Neo4j..." -ForegroundColor Gray
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", $Neo4jStart `
        -WorkingDirectory (Join-Path $ScriptPath "backend\neo4j-mostar-industries")
    
    Write-Host "   >> Waiting for Neo4j to be ready (max 30s)..." -ForegroundColor Gray
    $waited = 0
    while ($waited -lt 30) {
        Start-Sleep -Seconds 2
        $waited += 2
        if (Test-PortListening -Port 7687) {
            Write-Host "   ✅ Neo4j ready after ${waited}s" -ForegroundColor Green
            break
        }
        Write-Host "   ... still waiting (${waited}s)" -ForegroundColor DarkGray
    }
    if ($waited -ge 30) { 
        Write-Host "   ⚠️  Neo4j may not be ready yet. Continuing anyway." -ForegroundColor Yellow
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
    $job = Start-Job -ScriptBlock {
        param($python, $scriptPath, $logFile, $nUri, $nUser, $nPass)
        $env:PYTHONPATH = $scriptPath
        $env:PYTHONUTF8 = '1'
        $env:NEO4J_URI = $nUri
        $env:NEO4J_USER = $nUser
        $env:NEO4J_PASSWORD = $nPass
        Set-Location $scriptPath
        & $python -m uvicorn backend.memory_layer.api.main:app --host 0.0.0.0 --port 8000 --reload 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $PythonExe, $ScriptPath, $logFile, $Neo4jUri, $Neo4jUser, $Neo4jPass
    
    Write-Host "   >> Job started (ID: $($job.Id)). Waiting for port..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
    
    if (Test-PortListening -Port 8000) {
        Write-Host "   ✅ Memory Layer API responding on port 8000" -ForegroundColor Green
        Write-Host "      Docs: http://localhost:8000/docs" -ForegroundColor DarkGray
    }
    else {
        Write-Host "   ⚠️  Port 8000 not responding yet. Check logs: $logFile" -ForegroundColor Yellow
    }
}

# --- 3. Start Core Engine API (Port 8001) ---
Write-Host "`n[3/5] Starting Core Engine API (port 8001)..." -ForegroundColor Cyan
if (-not (Test-Path $PythonExe)) {
    Write-Host "   ❌ Python executable not found at $PythonExe" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "core_engine.log"
    $job = Start-Job -ScriptBlock {
        param($python, $scriptPath, $logFile, $nUri, $nUser, $nPass)
        $env:PYTHONPATH = $scriptPath
        $env:PYTHONUTF8 = '1'
        $env:NEO4J_URI = $nUri
        $env:NEO4J_USER = $nUser
        $env:NEO4J_PASSWORD = $nPass
        Set-Location $scriptPath
        & $python -m uvicorn backend.core_engine.api_gateway:app --host 0.0.0.0 --port 8001 --reload 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $PythonExe, $ScriptPath, $logFile, $Neo4jUri, $Neo4jUser, $Neo4jPass
    
    Write-Host "   >> Job started (ID: $($job.Id)). Waiting for port..." -ForegroundColor Gray
    Start-Sleep -Seconds 3
    
    if (Test-PortListening -Port 8001) {
        Write-Host "   ✅ Core Engine API responding on port 8001" -ForegroundColor Green
        Write-Host "      Docs: http://localhost:8001/docs" -ForegroundColor DarkGray
    }
    else {
        Write-Host "   ⚠️  Port 8001 not responding yet. Check logs: $logFile" -ForegroundColor Yellow
    }
}

# --- 4. Start Mo Executor ---
Write-Host "`n[4/5] Starting Mo Executor (graph mutation daemon)..." -ForegroundColor Cyan
if (-not (Test-Path $ExecutorScript)) {
    Write-Host "   ❌ Mo Executor script not found at $ExecutorScript" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "mo_executor.log"
    $job = Start-Job -ScriptBlock {
        param($python, $scriptPath, $executorScript, $logFile, $nUri, $nUser, $nPass)
        $env:PYTHONPATH = $scriptPath
        $env:PYTHONUTF8 = '1'
        $env:NEO4J_URI = $nUri
        $env:NEO4J_USER = $nUser
        $env:NEO4J_PASSWORD = $nPass
        Set-Location $scriptPath
        & $python $executorScript 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $PythonExe, $ScriptPath, $ExecutorScript, $logFile, $Neo4jUri, $Neo4jUser, $Neo4jPass
    
    Write-Host "   ✅ Mo Executor job started (ID: $($job.Id))" -ForegroundColor Green
    Write-Host "      Log: $logFile" -ForegroundColor DarkGray
}

# --- 5. Start Next.js Frontend ---
Write-Host "`n[5/5] Starting Next.js Frontend (port 3000)..." -ForegroundColor Cyan
if (-not (Test-Path $FrontendPath)) {
    Write-Host "   ❌ Frontend directory not found at $FrontendPath" -ForegroundColor Red
}
else {
    $logFile = Join-Path $LogsDir "frontend.log"
    $job = Start-Job -ScriptBlock {
        param($frontendPath, $logFile)
        Set-Location $frontendPath
        npm run dev 2>&1 | Tee-Object -FilePath $logFile
    } -ArgumentList $FrontendPath, $logFile
    
    Write-Host "   >> Job started (ID: $($job.Id)). Waiting for port..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    if (Test-PortListening -Port 3000) {
        Write-Host "   ✅ Frontend responding on port 3000" -ForegroundColor Green
        Write-Host "      URL: http://localhost:3000" -ForegroundColor DarkGray
    }
    else {
        Write-Host "   ⚠️  Port 3000 not responding yet. Check logs: $logFile" -ForegroundColor Yellow
    }
}

# --- Summary ---
Write-Host ""
Write-Host "==========================================" -ForegroundColor Green
Write-Host "  MoStar Grid - Services Status          " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# Check all ports
$neo4jOk = Test-PortListening -Port 7687
$memoryOk = Test-PortListening -Port 8000
$coreOk = Test-PortListening -Port 8001
$frontendOk = Test-PortListening -Port 3000

$neo4jStatus = if ($neo4jOk) { "✅ RUNNING" } else { "❌ DOWN" }
$memoryStatus = if ($memoryOk) { "✅ RUNNING" } else { "❌ DOWN" }
$coreStatus = if ($coreOk) { "✅ RUNNING" } else { "❌ DOWN" }
$frontendStatus = if ($frontendOk) { "✅ RUNNING" } else { "❌ DOWN" }

Write-Host "  Neo4j (7687)        : $neo4jStatus" -ForegroundColor $(if ($neo4jOk) { "Green" } else { "Red" })
Write-Host "  Memory Layer (8000) : $memoryStatus" -ForegroundColor $(if ($memoryOk) { "Green" } else { "Red" })
Write-Host "  Core Engine (8001)  : $coreStatus" -ForegroundColor $(if ($coreOk) { "Green" } else { "Red" })
Write-Host "  Frontend (3000)     : $frontendStatus" -ForegroundColor $(if ($frontendOk) { "Green" } else { "Red" })
Write-Host ""
Write-Host "  Active Jobs: $(Get-Job | Where-Object { $_.State -eq 'Running' } | Measure-Object | Select-Object -ExpandProperty Count)" -ForegroundColor Cyan
Write-Host "  Logs: $LogsDir" -ForegroundColor DarkGray
Write-Host ""
Write-Host "  To view job output: Get-Job | Receive-Job -Keep" -ForegroundColor DarkGray
Write-Host "  To stop all jobs:   Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor DarkGray
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""
