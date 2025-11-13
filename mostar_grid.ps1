# =====================================================
# MoStar-Grid Base Directory Initialization Script
# Purpose: Creates the full foundational structure for
# Soul, Mind, Body, Graph, and Data layers
# =====================================================

# Root path (edit if needed)
$rootPath = "C:\Users\$env:USERNAME\Documents\GitHub\MoStar-Grid"

# Define directory structure
$dirs = @(
    "$rootPath\soul_layer",
    "$rootPath\mind_layer",
    "$rootPath\body_layer",
    "$rootPath\graph_backend",
    "$rootPath\data"
)

# Create directories if they don’t exist
foreach ($dir in $dirs) {
    if (!(Test-Path -Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "Directory already exists: $dir" -ForegroundColor Yellow
    }
}

# Create placeholder files
$files = @(
    "$rootPath\soul_layer\spiritual_engine.py",
    "$rootPath\mind_layer\verdict_engine.py",
    "$rootPath\mind_layer\ifa_oracle.py",
    "$rootPath\mind_layer\truth_engine.py",
    "$rootPath\body_layer\api_executor.py",
    "$rootPath\graph_backend\backend_boot.py",
    "$rootPath\data\seed_neo4j.cypher",
    "$rootPath\.env"
)

foreach ($file in $files) {
    if (!(Test-Path -Path $file)) {
        New-Item -ItemType File -Path $file | Out-Null
        Write-Host "Created file: $file" -ForegroundColor Cyan
    } else {
        Write-Host "File already exists: $file" -ForegroundColor Yellow
    }
}

Write-Host "`n✅ MoStar-Grid base structure initialized successfully." -ForegroundColor Green
function Get-MostarPythonPath {
    if ($env:VIRTUAL_ENV) {
        $venvPython = Join-Path $env:VIRTUAL_ENV "Scripts\python.exe"
        if (Test-Path $venvPython) {
            return $venvPython
        }
    }
    $localVenvPython = Join-Path $rootPath ".venv\Scripts\python.exe"
    if (Test-Path $localVenvPython) {
        return $localVenvPython
    }
    return "python"
}

function Start-MostarBackend {
    param(
        [int]$Port = 8001
    )
    $python = Get-MostarPythonPath
    $escapedPython = $python -replace "'", "''"
    $cmd = @"
Set-Location '$rootPath'
& '$escapedPython' -m uvicorn core_engine.api_gateway:app --reload --host 0.0.0.0 --port $Port
"@
    Write-Host "Starting backend on port $Port..." -ForegroundColor Cyan
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", $cmd -WorkingDirectory $rootPath
}

function Start-MostarFrontend {
    param(
        [int]$Port = 3000
    )
    $frontendPath = Join-Path $rootPath "frontend"
    if ($Port -eq 3000) {
        $cmd = @"
Set-Location '$frontendPath'
npm run dev
"@
    }
    else {
        $cmd = @"
Set-Location '$frontendPath'
npx next dev -p $Port
"@
    }
    Write-Host "Starting frontend on port $Port..." -ForegroundColor Cyan
    Start-Process pwsh -ArgumentList "-NoExit", "-Command", $cmd -WorkingDirectory $frontendPath
}

function Start-MostarGrid {
    param(
        [int]$ApiPort = 8001,
        [int]$WebPort = 3000
    )
    Start-MostarBackend -Port $ApiPort
    Start-MostarFrontend -Port $WebPort
    Write-Host "Backend and frontend launched. Close the spawned windows to stop the services." -ForegroundColor Green
}

function Start-Grid {
    param(
        [int]$ApiPort = 8001,
        [int]$WebPort = 3000
    )
    Start-MostarGrid -ApiPort $ApiPort -WebPort $WebPort
}
