# Test MostarAI Chat Endpoint
# Verifies the chat API is working

Write-Host "🧠 Testing MostarAI Chat..." -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if backend is running
Write-Host "1. Checking backend..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:7000/health" -Method Get
    Write-Host "   ✅ Backend is running" -ForegroundColor Green
    Write-Host "   Neo4j: $($health.neo4j.connected)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Backend not running!" -ForegroundColor Red
    Write-Host "   Start it with: .venv\Scripts\python.exe backend\grid_main.py" -ForegroundColor Yellow
    exit 1
}

# Test 2: Check if Ollama is running
Write-Host ""
Write-Host "2. Checking Ollama..." -ForegroundColor Yellow
try {
    $ollama = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
    Write-Host "   ✅ Ollama is running" -ForegroundColor Green
    Write-Host "   Models available: $($ollama.models.Count)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Ollama not running!" -ForegroundColor Red
    Write-Host "   Start it with: ollama serve" -ForegroundColor Yellow
    Write-Host "   Or pull a model: ollama pull mistral" -ForegroundColor Yellow
    exit 1
}

# Test 3: Send a test question
Write-Host ""
Write-Host "3. Testing chat endpoint..." -ForegroundColor Yellow

$testPrompt = "What is the Gadaa System?"

$body = @{
    prompt = $testPrompt
} | ConvertTo-Json

Write-Host "   Question: $testPrompt" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:7000/api/chat" `
        -Method Post `
        -ContentType "application/json" `
        -Body $body `
        -TimeoutSec 60
    
    Write-Host "   ✅ Chat endpoint working!" -ForegroundColor Green
    Write-Host ""
    Write-Host "   Response:" -ForegroundColor Cyan
    Write-Host "   $($response.response.Substring(0, [Math]::Min(200, $response.response.Length)))..." -ForegroundColor White
    Write-Host ""
    Write-Host "   Context Used: $($response.context_used)" -ForegroundColor Gray
    Write-Host "   Model: $($response.model)" -ForegroundColor Gray
    
} catch {
    Write-Host "   ❌ Chat endpoint failed!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ MostarAI is fully operational!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "🌐 Open http://localhost:3000 and navigate to Chat" -ForegroundColor Magenta
Write-Host ""
