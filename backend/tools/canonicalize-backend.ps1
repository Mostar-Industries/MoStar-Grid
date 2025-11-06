param(
  [string]$BackendPath = "backend",
  [switch]$Execute,
  [switch]$PurgeDocker   # remove docker-compose, netlify, etc. (moves to attic)
)

$ErrorActionPreference = "Stop"

function Write-Section($t){ Write-Host "`n=== $t ===" -ForegroundColor Cyan }
function Info($m){ Write-Host "[i] $m" -ForegroundColor Gray }
function Act($m){ Write-Host "[act] $m" -ForegroundColor Green }
function Warn($m){ Write-Warning $m }

# Resolve paths
$RepoRoot = (Get-Location).Path
$Backend  = Join-Path $RepoRoot $BackendPath
$Src      = Join-Path $Backend "src"
$Attic    = Join-Path $Backend "__attic__\$(Get-Date -Format 'yyyyMMdd-HHmmss')"
$Manifest = [ordered]@{
  timestamp = [DateTime]::UtcNow.ToString("o")
  backend   = $Backend
  src       = $Src
  attic     = $Attic
  actions   = @()
}

if (-not (Test-Path $Backend)) { throw "Backend not found: $Backend" }
if (-not (Test-Path $Src))     { New-Item -ItemType Directory -Force -Path $Src | Out-Null }

# Feature folders that belong under src/
$FeatureDirs = @(
  "components","pages","hooks","lib","services","types","utils",
  "data","db","scripts","training","public","frontend"
)

function Ensure-Dir($p){ if (-not (Test-Path $p)) { New-Item -ItemType Directory -Force -Path $p | Out-Null } }

function Hash-File($p){
  if (-not (Test-Path $p)) { return $null }
  return (Get-FileHash -Algorithm SHA256 -Path $p).Hash
}

function Move-File-Safe($from, $to){
  Ensure-Dir (Split-Path -Parent $to)
  if ($Execute) { Move-Item -LiteralPath $from -Destination $to -Force }
  $Manifest.actions += @{ op="move"; from=$from; to=$to }
  Act "move  $from  ->  $to"
}

function Delete-File-Safe($p){
  if ($Execute) { Remove-Item -LiteralPath $p -Force }
  $Manifest.actions += @{ op="delete-dupe"; path=$p }
  Act "delete dupe  $p"
}

function Archive-File($from, $rel){
  $dst = Join-Path $Attic ("conflicts\" + $rel)
  Ensure-Dir (Split-Path -Parent $dst)
  if ($Execute) { Move-Item -LiteralPath $from -Destination $dst -Force }
  $Manifest.actions += @{ op="archive-conflict"; from=$from; to=$dst }
  Warn "conflict -> archived  $from"
}

Write-Section "Fold top-level feature folders into src/"
foreach ($dir in $FeatureDirs) {
  $rootDir = Join-Path $Backend $dir
  $srcDir  = Join-Path $Src $dir

  if (-not (Test-Path $rootDir)) { continue }

  # If this is a whole duplicate 'frontend' folder, try to merge its children to src/
  if ($dir -eq "frontend") {
    Get-ChildItem -LiteralPath $rootDir -Force | ForEach-Object {
      $child = $_.Name
      $from  = Join-Path $rootDir $child
      $to    = Join-Path $Src $child
      if (Test-Path $to) {
        # if dir exists in src already, we'll handle below in general flow
      } else {
        Move-File-Safe $from $to
      }
    }
    # remove empty frontend dir later
  }

  if (-not (Test-Path $srcDir)) { Ensure-Dir $srcDir }

  # Walk all files under rootDir
  $files = Get-ChildItem -Path $rootDir -Recurse -File -Force -ErrorAction SilentlyContinue
  foreach ($f in $files) {
    $rel = Resolve-Path -LiteralPath $f.FullName | ForEach-Object {
      $_.Path.Substring($rootDir.Length).TrimStart('\','/')
    }
    $dest = Join-Path $srcDir $rel

    if (Test-Path $dest) {
      $h1 = Hash-File $f.FullName
      $h2 = Hash-File $dest
      if ($h1 -eq $h2) {
        Delete-File-Safe $f.FullName
      } else {
        Archive-File $f.FullName ("$dir\" + $rel)
      }
    } else {
      Move-File-Safe $f.FullName $dest
    }
  }

  # Clean empty dirs
  $remaining = Get-ChildItem -Path $rootDir -Recurse -Force -ErrorAction SilentlyContinue
  if ($remaining.Count -eq 0) {
    if ($Execute) { Remove-Item -LiteralPath $rootDir -Recurse -Force -ErrorAction SilentlyContinue }
    $Manifest.actions += @{ op="remove-empty-dir"; path=$rootDir }
    Act "rmdir  $rootDir"
  }
}

Write-Section "Top-level TS/TSX that belong in src/"
$RootFiles = @("App.tsx","index.tsx","main.tsx","types.ts","vite-env.d.ts","media.ts")
foreach ($name in $RootFiles) {
  $rootFile = Join-Path $Backend $name
  if (-not (Test-Path $rootFile)) { continue }
  $dest = Join-Path $Src $name
  if (Test-Path $dest) {
    $h1 = Hash-File $rootFile
    $h2 = Hash-File $dest
    if ($h1 -eq $h2) { Delete-File-Safe $rootFile }
    else { Archive-File $rootFile $name }
  } else {
    Move-File-Safe $rootFile $dest
  }
}

if ($PurgeDocker) {
  Write-Section "Archiving Docker/hosting files (dockerless)"
  $dock = @("docker-compose.yml","netlify.toml",".trunk","Dockerfile")
  foreach ($d in $dock) {
    $p = Join-Path $Backend $d
    if (-not (Test-Path $p)) { continue }
    $dst = Join-Path $Attic ("dockerless\" + $d)
    Ensure-Dir (Split-Path -Parent $dst)
    if ($Execute) { Move-Item -LiteralPath $p -Destination $dst -Force }
    $Manifest.actions += @{ op="archive-docker"; from=$p; to=$dst }
    Act "archive  $p"
  }
}

Write-Section "Save manifest"
Ensure-Dir $Attic
$manifestPath = Join-Path $Attic "canonicalize.manifest.json"
$Manifest | ConvertTo-Json -Depth 8 | Out-File -FilePath $manifestPath -Encoding UTF8
Write-Host "Manifest: $manifestPath" -ForegroundColor Yellow

if (-not $Execute) {
  Write-Host "`n[DRY RUN] No changes applied. Re-run with -Execute to apply." -ForegroundColor Yellow
  exit 0
} else {
  Write-Host "`nDone. Review attic for conflicts, then run build." -ForegroundColor Green
  exit 0
}
