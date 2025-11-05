param(
  [string]$BackendPath = "backend"
)
$ErrorActionPreference = "Stop"

# Resolve repo root as the directory containing this script's parent by default
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir

Write-Host "=== Project Analysis ===" -ForegroundColor Cyan
Write-Host "Repo Root: $RepoRoot"
Write-Host "Backend:   $BackendPath"
$BackendFull = Join-Path $RepoRoot $BackendPath

if (-not (Test-Path $BackendFull)) {
  Write-Warning "Backend path not found: $BackendFull"
}

function Get-DirStats([string]$Path) {
  if (-not (Test-Path $Path)) {
    return [pscustomobject]@{ Path=$Path; Files=0; Bytes=0 }
  }
  $files = Get-ChildItem -Path $Path -Recurse -File -Force -ErrorAction SilentlyContinue
  $bytes = ($files | Measure-Object -Property Length -Sum).Sum
  [pscustomobject]@{
    Path=$Path
    Files=($files | Measure-Object).Count
    Bytes=$bytes
  }
}

function Humanize($bytes) {
  $sizes = "B","KB","MB","GB","TB"
  $i = 0
  while ($bytes -gt 1024 -and $i -lt $sizes.Length-1) {
    $bytes = [math]::Round($bytes/1024,2)
    $i++
  }
  return "$bytes $($sizes[$i])"
}

# Basic stats
$rootStats = Get-DirStats $RepoRoot
$backendStats = Get-DirStats $BackendFull
Write-Host "`n-- Size Stats --" -ForegroundColor Yellow
"{0,-40} {1,10} {2,12}" -f "Path","Files","Size" | Write-Host
"{0,-40} {1,10} {2,12}" -f $rootStats.Path,$rootStats.Files,(Humanize $rootStats.Bytes) | Write-Host
"{0,-40} {1,10} {2,12}" -f $backendStats.Path,$backendStats.Files,(Humanize $backendStats.Bytes) | Write-Host

# Extension breakdown (backend)
Write-Host "`n-- Backend File Types --" -ForegroundColor Yellow
Get-ChildItem -Path $BackendFull -Recurse -File -Force -ErrorAction SilentlyContinue |
  Group-Object Extension |
  Sort-Object Count -Descending |
  Select-Object @{n='Ext';e={$_.Name}}, @{n='Count';e={$_.Count}} |
  Format-Table -AutoSize

# Detect likely duplicates between repo root and backend
$dupCandidates = @(
  "index.html",
  "package.json","package-lock.json","pnpm-lock.yaml","yarn.lock",
  "vite.config.ts","vite.config.js",
  "tsconfig.json","tsconfig.app.json","tsconfig.node.json",
  "tailwind.config.ts","tailwind.config.js","postcss.config.cjs","postcss.config.js",
  ".eslintrc.cjs",".eslintrc.js",".prettierrc",".prettierrc.json",
  ".env",".env.local",".env.development",".env.production",
  "src","public",".vite","node_modules"
)

Write-Host "`n-- Duplicate Candidates (root vs backend) --" -ForegroundColor Yellow
$dupReport = @()
foreach ($name in $dupCandidates) {
  $rootItem = Join-Path $RepoRoot $name
  $backItem = Join-Path $BackendFull $name
  $existsRoot = Test-Path $rootItem
  $existsBack = Test-Path $backItem
  if ($existsRoot -and $existsBack) {
    $dupReport += [pscustomobject]@{ Name=$name; Root=$rootItem; Backend=$backItem }
  }
}
if ($dupReport.Count -gt 0) {
  $dupReport | Format-Table -AutoSize
} else {
  Write-Host "No obvious duplicates found."
}

# Git status/diff (if git available)
Write-Host "`n-- Git Status --" -ForegroundColor Yellow
try {
  & git rev-parse --is-inside-work-tree | Out-Null
  & git status --porcelain=v1
  Write-Host "`n-- Diff Stat (HEAD vs working tree) --" -ForegroundColor Yellow
  & git diff --stat
} catch {
  Write-Warning "git not available or not a repository."
}

Write-Host "`nAnalysis complete." -ForegroundColor Cyan
