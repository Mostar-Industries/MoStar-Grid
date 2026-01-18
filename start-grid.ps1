# Start MoStar Grid using Docker Compose
Write-Host "🚀 Launching MoStar Grid via Docker..." -ForegroundColor Magenta

# Check if Docker is running
docker info >$null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Build and start the containers
docker-compose up -d --build

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ MoStar Grid is up and running!" -ForegroundColor Green
    Write-Host "🌐 Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "🔌 Backend API: http://localhost:8001" -ForegroundColor Cyan
    Write-Host "🧠 Neo4j Browser: http://localhost:7474 (user: neo4j, pass: mostar123)" -ForegroundColor Cyan
    Write-Host "`nUse 'docker-compose logs -f' to see live traces." -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Failed to launch MoStar Grid containers." -ForegroundColor Red
}
