# Alignment Toolkit

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
