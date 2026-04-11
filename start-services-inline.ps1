# ==============================================================================
# MOSTAR GRID - INLINE SERVICE LAUNCHER (WSL handoff)
# ==============================================================================

$ErrorActionPreference = "Stop"

# Resolve WSL path — works from both UNC (\\wsl.localhost\...) and native Windows paths
$ScriptPath = $PSScriptRoot

if ($ScriptPath -match '^\\\\wsl\.localhost\\([^\\]+)(.*)') {
    $WslDistro = $Matches[1]
    $WslRoot   = $Matches[2] -replace '\\', '/'
} elseif ($ScriptPath -match '^([A-Za-z]):\\(.*)') {
    # Fallback: convert Windows path to WSL path
    $Drive   = $Matches[1].ToLower()
    $Rest    = $Matches[2] -replace '\\', '/'
    $WslRoot = "/mnt/$Drive/$Rest"
    $WslDistro = "Ubuntu"
} else {
    throw "Cannot resolve WSL path from: $ScriptPath"
}

$BootScript = "$WslRoot/scripts/grid-inline-boot.sh"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "   MoStar-Grid: Inline System Boot       " -ForegroundColor Magenta
Write-Host "==========================================" -ForegroundColor Magenta
Write-Host "   WSL root : $WslRoot" -ForegroundColor DarkGray
Write-Host "   Distro   : $WslDistro" -ForegroundColor DarkGray
Write-Host ""

& wsl.exe -d $WslDistro bash -lc "bash '$BootScript'"
exit $LASTEXITCODE
