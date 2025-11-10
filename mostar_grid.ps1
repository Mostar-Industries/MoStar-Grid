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
