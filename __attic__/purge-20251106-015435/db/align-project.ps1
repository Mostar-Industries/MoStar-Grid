param(
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

