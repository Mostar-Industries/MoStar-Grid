# ==============================================================================
# MOSTAR GRID - UNIFIED SERVICE LAUNCHER (WSL handoff)
# ==============================================================================

$ErrorActionPreference = "Stop"
$ScriptPath = (Resolve-Path $PSScriptRoot).Path
$WslRoot = ($ScriptPath -replace '^\\\\wsl\.localhost\\[^\\]+', '') -replace '\\', '/'

if (-not $WslRoot.StartsWith('/')) {
    throw "This launcher must be run from a WSL-backed project path. Current path: $ScriptPath"
}

$BootScript = "$WslRoot/scripts/grid-inline-boot.sh"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "   MoStar-Grid: Inline System Boot       " -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "   WSL root: $WslRoot" -ForegroundColor DarkGray
Write-Host ""

& wsl.exe bash -lc "bash '$BootScript'"
exit $LASTEXITCODE
