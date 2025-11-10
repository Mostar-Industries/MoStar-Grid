# Health check script for Grid system
Write-Host " Grid System Health Check" -ForegroundColor Cyan
Write-Host "===========================" -ForegroundColor Cyan

# Check Redis
try {
     = Invoke-Expression "redis-cli ping"
    if ( -eq "PONG") {
        Write-Host " Redis is running" -ForegroundColor Green
    } else {
        Write-Host " Redis not responding correctly" -ForegroundColor Red
    }
} catch {
    Write-Host "? Redis CLI not found or service not running" -ForegroundColor Red
}

# Check Neon DB
 = Get-Content -Path "frontend\.env.local" | Where-Object {  -match "NEON_DB_URL" }
if () {
    Write-Host " Neon DB URL configured" -ForegroundColor Green
    
    # Optional: Test connection if psql is available
    try {
         = Invoke-Expression "psql -c 'SELECT 1' $env:NEON_DB_URL"
        Write-Host " Neon DB connection successful" -ForegroundColor Green
    } catch {
        Write-Host " Could not verify Neon DB connection (psql not available)" -ForegroundColor Yellow
    }
} else {
    Write-Host " Neon DB URL not configured" -ForegroundColor Red
}

# Check Next.js
if (Test-Path "frontend\node_modules\next") {
    Write-Host " Next.js installed" -ForegroundColor Green
} else {
    Write-Host "? Next.js not installed. Run 'cd frontend && npm install'" -ForegroundColor Red
}

Write-Host "
?? Run 'npm run dev' to start the application" -ForegroundColor Cyan
