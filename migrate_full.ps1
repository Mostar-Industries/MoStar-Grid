$github = "C:\Users\idona\OneDrive - World Health Organization\Documents\Github"
$dev = "C:\Users\idona\OneDrive - World Health Organization\Documents\Dev"
$base = "\\wsl.localhost\Ubuntu\home\idona\MoStar"

$github_repos = @('AFRO-SENTINEL', 'flameborn-genesis', 'FLB', 'MoVerse', 'Sigma_Signals', 'mostarverse', 'prepositioning-index-dashboard', 'report-weaver', 'Nagy-may-', 'jane_earth', 'map-explorer')
$dev_repos = @('afriguard-weather-intelligence', 'RAD-X', 'AFRO_STORM_WEB_APP', 'flameborn-mini-pay', 'phantom-poe-engine')

foreach ($repo in $github_repos) {
    $src = Join-Path $github $repo
    $dst = Join-Path $base $repo
    Write-Host "Migrating $repo from GitHub..." -ForegroundColor Cyan
    if (Test-Path $src) {
        robocopy "$src" "$dst" /E /XD node_modules .git .next dist .vite /R:0 /W:0 /NP
    } else {
        Write-Host "WARNING: Not found at $src" -ForegroundColor Magenta
    }
}

foreach ($repo in $dev_repos) {
    $src = Join-Path $dev $repo
    $dst = Join-Path $base $repo
    Write-Host "Migrating $repo from Dev..." -ForegroundColor Cyan
    if (Test-Path $src) {
        robocopy "$src" "$dst" /E /XD node_modules .git .next dist .vite /R:0 /W:0 /NP
    } else {
        Write-Host "WARNING: Not found at $src" -ForegroundColor Magenta
    }
}

Write-Host "=== ALL SOVEREIGN REPOSITORIES MIGRATED SUCCESSFULLY ===" -ForegroundColor Green
