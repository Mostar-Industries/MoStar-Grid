# Comprehensive Vercel Deployment Verification & Fix Script
# This script checks all critical deployment settings

Write-Host "=" * 70 -ForegroundColor Cyan
Write-Host "MOSTAR GRID DEPLOYMENT VERIFICATION" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

# 1. Check local git status
Write-Host "`n[1/5] LOCAL GIT STATUS" -ForegroundColor Yellow
$latestCommit = git log -1 --oneline
Write-Host "Latest commit: $latestCommit" -ForegroundColor Green
if ($latestCommit -match "dc1b753") {
    Write-Host "✅ Commit dc1b753 (frontend/api/moments) is in local repo" -ForegroundColor Green
} else {
    Write-Host "⚠️  Expected commit dc1b753 not found" -ForegroundColor Red
}

# 2. Verify frontend/api/moments.js exists
Write-Host "`n[2/5] FRONTEND API MOMENTS HANDLER" -ForegroundColor Yellow
$momentsPath = "frontend\api\moments.js"
if (Test-Path $momentsPath) {
    Write-Host "✅ $momentsPath exists" -ForegroundColor Green
    $content = Get-Content $momentsPath -Raw
    if ($content -match "neo4j.driver") {
        Write-Host "✅ Contains Neo4j driver initialization" -ForegroundColor Green
    }
} else {
    Write-Host "❌ $momentsPath NOT FOUND" -ForegroundColor Red
}

# 3. Verify frontend/src/app/api/moments/route.ts exists
Write-Host "`n[3/5] FRONTEND APP MOMENTS ROUTE" -ForegroundColor Yellow
$routePath = "frontend\src\app\api\moments\route.ts"
if (Test-Path $routePath) {
    Write-Host "✅ $routePath exists" -ForegroundColor Green
    $content = Get-Content $routePath -Raw
    if ($content -match "provenance") {
        Write-Host "✅ Contains provenance field (new code)" -ForegroundColor Green
    }
} else {
    Write-Host "❌ $routePath NOT FOUND" -ForegroundColor Red
}

# 4. Check .env has Neo4j Aura credentials
Write-Host "`n[4/5] LOCAL ENVIRONMENT VARIABLES" -ForegroundColor Yellow
$envPath = ".env"
if (Test-Path $envPath) {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    $envContent = Get-Content $envPath -Raw
    
    if ($envContent -match "NEO4J_URI.*371530ba") {
        Write-Host "✅ NEO4J_URI set to Aura instance" -ForegroundColor Green
    }
    if ($envContent -match "NEO4J_USER.*neo4j") {
        Write-Host "✅ NEO4J_USER set to neo4j" -ForegroundColor Green
    }
    if ($envContent -match "NEO4J_PASSWORD.*mostar123") {
        Write-Host "✅ NEO4J_PASSWORD set" -ForegroundColor Green
    }
} else {
    Write-Host "❌ .env NOT FOUND" -ForegroundColor Red
}

# 5. Test current deployment
Write-Host "`n[5/5] PRODUCTION DEPLOYMENT TEST" -ForegroundColor Yellow
Write-Host "Testing https://mostar-grid.vercel.app/api/moments..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri "https://mostar-grid.vercel.app/api/moments" -TimeoutSec 15 -ErrorAction Stop
    $data = $response.Content | ConvertFrom-Json
    
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    
    if ($data.PSObject.Properties.Name -contains "insignia") {
        Write-Host "⚠️  Response contains OLD code fields (insignia, generatedAt)" -ForegroundColor Red
        Write-Host "    This means Vercel is NOT serving commit dc1b753 yet" -ForegroundColor Red
    }
    
    if ($data.PSObject.Properties.Name -contains "provenance") {
        Write-Host "✅ Response contains NEW code fields (provenance)" -ForegroundColor Green
        if ($data.provenance.source -eq "neo4j") {
            Write-Host "✅ Connected to Neo4j Aura!" -ForegroundColor Green
            Write-Host "   Moments found: $($data.count)" -ForegroundColor Green
        } else {
            Write-Host "⚠️  Neo4j not connected. Source: $($data.provenance.source)" -ForegroundColor Yellow
            if ($data.provenance.error) {
                Write-Host "   Error: $($data.provenance.error)" -ForegroundColor Yellow
            }
        }
    }
} catch {
    Write-Host "❌ Connection failed: $_" -ForegroundColor Red
    Write-Host "   Possible causes:" -ForegroundColor Yellow
    Write-Host "   - Deployment still building" -ForegroundColor Yellow
    Write-Host "   - Domain misconfigured" -ForegroundColor Yellow
    Write-Host "   - Vercel service issue" -ForegroundColor Yellow
}

# Summary and next steps
Write-Host "`n" + "=" * 70 -ForegroundColor Cyan
Write-Host "NEXT STEPS" -ForegroundColor Cyan
Write-Host "=" * 70 -ForegroundColor Cyan

Write-Host @"
If deployment test FAILED or shows OLD code:

1. Open Vercel Dashboard:
   https://vercel.com/mo-101s-projects/mo-star-grid/deployments

2. Find the deployment with commit: dc1b753
   (Message: "fix: add frontend/api/moments Neo4j-backed serverless route")

3. Check its status:
   - If "Ready" → Click "Promote to Production"
   - If "Building" → Wait 2-3 minutes and refresh
   - If "Failed" → Click to view build logs

4. Verify domain alias:
   https://vercel.com/mo-101s-projects/mo-star-grid/settings/domains
   - Confirm mostar-grid.vercel.app is listed
   - If missing, add it and select the Ready deployment

5. Verify Neo4j env vars:
   https://vercel.com/mo-101s-projects/mo-star-grid/settings/environment-variables
   - NEO4J_URI = neo4j+s://371530ba.databases.neo4j.io
   - NEO4J_USER = neo4j
   - NEO4J_PASSWORD = mostar123
   (All must be set to "Production" environment)

6. After fixes, wait 60 seconds and re-run this script:
   .\verify_and_fix.ps1

If deployment test SUCCEEDED with NEW code:
- Grid is live and connected to Neo4j Aura
- Next: Attach mostarindustries.com custom domain
"@

Write-Host "`n" + "=" * 70 -ForegroundColor Cyan
