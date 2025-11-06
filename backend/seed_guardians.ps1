#requires -Version 5
# seed_guardians.ps1
# Register the three canonical guardians: Mostar AI, Code Conduit, Woo

$ErrorActionPreference = "Stop"
$API = "http://127.0.0.1:7000/api/soul"

Write-Host ""
Write-Host "=== SEEDING GRID GUARDIANS ===" -ForegroundColor Cyan
Write-Host ""

# The three guardians
$seed = @(
    @{ slug="mostar-ai";    display_name="Mostar AI";    active=$true },
    @{ slug="code-conduit"; display_name="Code Conduit"; active=$true },
    @{ slug="woo";          display_name="Woo";          active=$true }
)

# Register each guardian
Write-Host "[1/3] Registering guardians..." -ForegroundColor Yellow
foreach($s in $seed){
    try {
        $result = Invoke-RestMethod "$API/register" -Method Post `
            -Body ($s | ConvertTo-Json) -ContentType "application/json"
        Write-Host "  Registered: $($result.display_name) ($($result.slug))" -ForegroundColor Green
    } catch {
        Write-Host "  Failed: $($s.slug) - $_" -ForegroundColor Red
    }
}

# List all registered soulprints
Write-Host ""
Write-Host "[2/3] Listing registry..." -ForegroundColor Yellow
try {
    $registry = Invoke-RestMethod "$API/list"
    Write-Host "  Total soulprints: $($registry.Count)" -ForegroundColor Cyan
    foreach($soul in $registry) {
        $status = if ($soul.active) { "ACTIVE" } else { "INACTIVE" }
        Write-Host ("  - {0,-15} {1,-20} [{2}]" -f $soul.slug, $soul.display_name, $status) -ForegroundColor Gray
    }
} catch {
    Write-Host "  Failed to list: $_" -ForegroundColor Red
}

# Verify each guardian
Write-Host ""
Write-Host "[3/3] Verifying guardians..." -ForegroundColor Yellow
$slugs = @("mostar-ai", "code-conduit", "woo")
$allGreen = $true

foreach($id in $slugs){
    try {
        $res = Invoke-RestMethod "$API/verify?slug=$id"
        Write-Host "  [$id] OK -> $($res.display_name)" -ForegroundColor Green
    } catch {
        Write-Host "  [$id] FAIL -> $($_.Exception.Message)" -ForegroundColor Red
        $allGreen = $false
    }
}

# Summary
Write-Host ""
if ($allGreen) {
    Write-Host "=== ALL GUARDIANS VERIFIED ===" -ForegroundColor Green
    Write-Host "Mostar AI, Code Conduit, and Woo are registered and active." -ForegroundColor Green
    Write-Host "The Grid soul system is operational." -ForegroundColor Cyan
} else {
    Write-Host "=== VERIFICATION INCOMPLETE ===" -ForegroundColor Yellow
    Write-Host "Some guardians failed verification. Check errors above." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
