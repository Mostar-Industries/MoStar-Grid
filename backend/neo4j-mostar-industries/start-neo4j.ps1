# ═══════════════════════════════════════════════════════════════
# MoStar Grid — Neo4j Launcher (JDK 21 enforced)
# Run this script to start Neo4j with the correct Java runtime.
# ═══════════════════════════════════════════════════════════════

$env:JAVA_HOME = "C:\Tools\jdk-21\jdk-21.0.5+11"
$env:PATH = "$env:JAVA_HOME\bin;$env:PATH"

# Confirm version
Write-Host "=== NEO4J — MoStar Grid ===" -ForegroundColor Green
Write-Host "Java: $(java -version 2>&1 | Select-Object -First 1)" -ForegroundColor Green

# Launch Neo4j
Set-Location "$PSScriptRoot"
.\bin\neo4j.bat console
