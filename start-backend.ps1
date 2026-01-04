# Start Neo4j and Core Engine (backend) with logs

$ErrorActionPreference = "Continue"
$ScriptPath = $PSScriptRoot

$JavaHome = "C:\Tools\jdk-25.0.1+8"
$Neo4jBin = Join-Path $ScriptPath "backend\neo4j-mostar-industries\bin\neo4j.bat"
$PythonExe = Join-Path $ScriptPath ".venv\Scripts\python.exe"
$LogsDir = Join-Path $ScriptPath "logs"

# Ensure logs directory exists
if (-not (Test-Path $LogsDir)) { New-Item -ItemType Directory -Path $LogsDir | Out-Null }

Write-Host "[1/2] Starting Neo4j..." -ForegroundColor Cyan
if (Test-Path $Neo4jBin) {
    $Cmd = '$env:JAVA_HOME = "{0}"; Write-Host "Starting Neo4j..."; & "{1}" console' -f $JavaHome, $Neo4jBin
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $Cmd -WorkingDirectory $ScriptPath
    Write-Host "   >> Neo4j console window launched." -ForegroundColor Gray
}
else {
    Write-Warning "Neo4j binary not found at $Neo4jBin"
}

Start-Sleep -Seconds 2

Write-Host "[2/2] Starting Core Engine API (port 8001)..." -ForegroundColor Cyan
if (Test-Path $PythonExe) {
    $Cmd = '$env:PYTHONPATH="{0}"; Write-Host "Starting Core Engine..."; & "{1}" -m uvicorn core_engine.api_gateway:app --host 0.0.0.0 --port 8001 --reload 2>&1 | Tee-Object -FilePath "{2}"' -f $ScriptPath, $PythonExe, (Join-Path $LogsDir "core_engine.log")
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $Cmd -WorkingDirectory $ScriptPath
    Write-Host "   >> Core Engine window launched. Logs: $(Join-Path $LogsDir "core_engine.log")" -ForegroundColor Gray
}
else {
    Write-Warning "Python executable not found at $PythonExe"
}

Write-Host "\nStartup initiated for Neo4j + Core Engine." -ForegroundColor Green
