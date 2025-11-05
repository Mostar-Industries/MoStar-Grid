"""
Create PowerShell helper scripts for analysis, alignment, and initiation.
"""
from pathlib import Path

# Use current directory as base (repo root)
base = Path(__file__).parent
tools = base / "tools"
tools.mkdir(parents=True, exist_ok=True)

analyze = tools / "analyze-project.ps1"
align = tools / "align-project.ps1"
initdev = tools / "init-dev.ps1"
readme = base / "ALIGNMENT_README.md"

analyze.write_text(r'''param(
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
''', encoding="utf-8")

align.write_text(r'''param(
  [string]$BackendPath = "backend",
  [switch]$Execute,
  [switch]$ForceCleanWorkingTree
)
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$BackendFull = Join-Path $RepoRoot $BackendPath

Write-Host "=== Align Project (canonicalize to $BackendPath) ===" -ForegroundColor Cyan
Write-Host "Repo Root: $RepoRoot"
Write-Host "Backend:   $BackendFull"

if (-not (Test-Path $BackendFull)) {
  Write-Error "Backend path not found: $BackendFull"; exit 2
}
if (-not (Test-Path (Join-Path $BackendFull "package.json"))) {
  Write-Error "Missing package.json in backend; aborting."; exit 3
}

# Ensure working tree is clean unless forced
try {
  & git rev-parse --is-inside-work-tree | Out-Null
  $status = & git status --porcelain
  if ($status -and -not $ForceCleanWorkingTree) {
    Write-Error "Working tree not clean. Commit/stash or pass -ForceCleanWorkingTree."; exit 4
  }
} catch {
  Write-Warning "git not available; proceeding without VCS safety."
}

# Targets to remove from repo root if duplicated (and not inside backend)
$targets = @(
  "index.html",
  "package.json","package-lock.json","pnpm-lock.yaml","yarn.lock",
  "vite.config.ts","vite.config.js",
  "tsconfig.json","tsconfig.app.json","tsconfig.node.json",
  "tailwind.config.ts","tailwind.config.js","postcss.config.cjs","postcss.config.js",
  ".eslintrc.cjs",".eslintrc.js",".prettierrc",".prettierrc.json",
  ".env",".env.local",".env.development",".env.production",
  "src","public",".vite","node_modules"
)

$toDelete = @()
foreach ($name in $targets) {
  $rootItem = Join-Path $RepoRoot $name
  $backItem = Join-Path $BackendFull $name
  if ((Test-Path $rootItem) -and (Test-Path $backItem)) {
    # Ensure we don't delete anything inside backend
    if (-not ($rootItem -like "$BackendFull*")) {
      $toDelete += $rootItem
    }
  }
}

if ($toDelete.Count -eq 0) {
  Write-Host "No duplicated frontend targets to remove at repo root."
} else {
  Write-Host "`nPlanned removals (root-level duplicates):" -ForegroundColor Yellow
  $toDelete | ForEach-Object { Write-Host " - $_" }
}

if ($Execute) {
  foreach ($p in $toDelete) {
    if (Test-Path $p) {
      Write-Host "Removing $p" -ForegroundColor Red
      Remove-Item -LiteralPath $p -Recurse -Force -ErrorAction Continue
      try { & git rm -r --cached --force -- "$p" | Out-Null } catch {}
    }
  }

  # Optional install/build
  Push-Location $BackendFull
  try {
    if (Test-Path ".\package-lock.json") {
      Write-Host "npm ci (backend)..." -ForegroundColor Cyan
      npm ci
    } else {
      Write-Host "npm install (backend)..." -ForegroundColor Cyan
      npm install
    }
    Write-Host "npm run build (backend)..." -ForegroundColor Cyan
    npm run build
  } catch {
    Write-Warning "npm step failed: $($_.Exception.Message)"
  } finally {
    Pop-Location
  }

  Write-Host "`nAlignment complete. Review changes and commit:" -ForegroundColor Cyan
  Write-Host "  git add -A && git commit -m \"chore: align project to backend/ and remove duplicated frontend from root\""
} else {
  Write-Host "`nDry run only. Re-run with -Execute to apply removals." -ForegroundColor Yellow
}

''', encoding="utf-8")

initdev.write_text(r'''param(
  [string]$BackendPath = "backend"
)
$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
$BackendFull = Join-Path $RepoRoot $BackendPath

Write-Host "=== Init Dev (Vite) ===" -ForegroundColor Cyan
if (-not (Test-Path $BackendFull)) { Write-Error "Backend path not found: $BackendFull"; exit 2 }

Push-Location $BackendFull
try {
  node -v
  npm -v
} catch {
  Write-Error "Node.js and npm are required. Install LTS (>=18) and retry."; Pop-Location; exit 3
}

try {
  if (Test-Path ".\package-lock.json") {
    Write-Host "npm ci..." -ForegroundColor Cyan
    npm ci
  } else {
    Write-Host "npm install..." -ForegroundColor Cyan
    npm install
  }
  Write-Host "Starting Vite dev server..." -ForegroundColor Cyan
  npm run dev
} finally {
  Pop-Location
}
''', encoding="utf-8")

readme.write_text(r'''# Alignment Toolkit

## Scripts
- `tools/analyze-project.ps1` — show size stats, file-type breakdown, duplicate candidates, git status/diff.
- `tools/align-project.ps1` — dry-run removal of duplicated frontend files at repo root; use `-Execute` to apply.
- `tools/init-dev.ps1` — install deps and start Vite dev server in `backend/`.

## Typical flow (PowerShell)
```powershell
# From repo root
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\tools\analyze-project.ps1

# Dry run first
.\tools\align-project.ps1

# If the plan looks good
.\tools\align-project.ps1 -Execute -ForceCleanWorkingTree

# Kick the dev server
.\tools\init-dev.ps1
```
''', encoding="utf-8")

print("Created tools/analyze-project.ps1")
print("Created tools/align-project.ps1")
print("Created tools/init-dev.ps1")
print("Created ALIGNMENT_README.md")
print("\nRun the scripts from repo root:")
print("  .\\tools\\analyze-project.ps1")
