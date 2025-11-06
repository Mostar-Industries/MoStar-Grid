# test_mostly.ps1
# Test MostlyAI integration

Write-Host "`n=== MostlyAI Integration Test ===" -ForegroundColor Cyan

# Check environment variables
Write-Host "`n[1/3] Checking environment configuration..." -ForegroundColor Yellow
$apiKey = $env:MOSTLY_API_KEY
if ($apiKey) {
    Write-Host "✅ MOSTLY_API_KEY is set" -ForegroundColor Green
    Write-Host "   Key: $($apiKey.Substring(0,20))..." -ForegroundColor Gray
} else {
    Write-Host "❌ MOSTLY_API_KEY not set" -ForegroundColor Red
    Write-Host "   Run: `$env:MOSTLY_API_KEY='your-key'" -ForegroundColor Yellow
    exit 1
}

$genId = $env:MOSTLY_GENERATOR_ID
if ($genId) {
    Write-Host "✅ MOSTLY_GENERATOR_ID is set: $genId" -ForegroundColor Green
} else {
    Write-Host "⚠️  MOSTLY_GENERATOR_ID not set (will be created)" -ForegroundColor Yellow
}

# Test Python SDK installation
Write-Host "`n[2/3] Checking MostlyAI SDK..." -ForegroundColor Yellow
try {
    python -c "from mostlyai.sdk import MostlyAI; print('✅ MostlyAI SDK installed')"
} catch {
    Write-Host "❌ MostlyAI SDK not installed" -ForegroundColor Red
    Write-Host "   Run: pip install -U mostlyai" -ForegroundColor Yellow
    exit 1
}

# Test quick connection
Write-Host "`n[3/3] Testing MostlyAI connection..." -ForegroundColor Yellow
python -c @"
import os
from mostlyai.sdk import MostlyAI

mostly = MostlyAI(
    api_key=os.getenv('MOSTLY_API_KEY'),
    base_url=os.getenv('MOSTLY_BASE_URL', 'https://app.mostly.ai')
)

try:
    # Try to list generators
    generators = list(mostly.generators.list())
    print(f'✅ Connected to MostlyAI ({len(generators)} generators found)')
    
    if generators:
        for g in generators[:3]:  # Show first 3
            print(f'   - {g.name} (ID: {g.id})')
    
    gen_id = os.getenv('MOSTLY_GENERATOR_ID')
    if gen_id:
        try:
            g = mostly.generators.get(gen_id)
            print(f'✅ Generator {gen_id} is accessible')
            print(f'   Name: {g.name}')
            print(f'   Status: {g.status}')
        except Exception as e:
            print(f'⚠️  Generator {gen_id} not found: {e}')
    
except Exception as e:
    print(f'❌ Connection failed: {e}')
    exit(1)
"@

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "1. Run setup: python mostly_quick_start.py" -ForegroundColor Gray
Write-Host "2. Restart backend: python grid_main.py" -ForegroundColor Gray
Write-Host "3. Test endpoint: POST http://127.0.0.1:7000/api/synthetic/probe" -ForegroundColor Gray
