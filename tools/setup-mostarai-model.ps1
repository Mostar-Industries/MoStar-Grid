# 🧠 MostarAI Custom Model Setup Script
# Creates a custom Ollama model with MostarAI consciousness

Write-Host "👑 MostarAI Model Setup" -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host ""

$ollamaPath = "$env:LOCALAPPDATA\Programs\Ollama\ollama.exe"

# Check if Ollama is installed
if (-not (Test-Path $ollamaPath)) {
    Write-Host "❌ Ollama not found at: $ollamaPath" -ForegroundColor Red
    Write-Host "Installing Ollama..." -ForegroundColor Yellow
    winget install Ollama.Ollama
    Write-Host "✅ Ollama installed. Please restart your terminal and run this script again." -ForegroundColor Green
    exit 0
}

Write-Host "✅ Ollama found: $ollamaPath" -ForegroundColor Green
Write-Host ""

# Check Ollama version
Write-Host "📦 Ollama Version:" -ForegroundColor Yellow
& $ollamaPath --version
Write-Host ""

# Check if base model exists
Write-Host "🔍 Checking for base model (llama3:latest)..." -ForegroundColor Yellow
$models = & $ollamaPath list
if ($models -match "llama3:latest") {
    Write-Host "✅ Base model already exists" -ForegroundColor Green
} else {
    Write-Host "📥 Pulling base model (llama3:latest)..." -ForegroundColor Yellow
    Write-Host "⏳ This will take several minutes (4.7 GB download)..." -ForegroundColor Gray
    & $ollamaPath pull llama3:latest
    Write-Host "✅ Base model downloaded" -ForegroundColor Green
}
Write-Host ""

# Check if Modelfile exists
$modelfilePath = Join-Path (Get-Location) "Modelfile"
if (-not (Test-Path $modelfilePath)) {
    Write-Host "❌ Modelfile not found at: $modelfilePath" -ForegroundColor Red
    Write-Host "Please create a Modelfile in the project root." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Modelfile found: $modelfilePath" -ForegroundColor Green
Write-Host ""

# Create custom model
Write-Host "🔨 Creating custom MostarAI model..." -ForegroundColor Yellow
Write-Host "Model name: mostar" -ForegroundColor Gray
Write-Host ""

try {
    & $ollamaPath create mostar -f $modelfilePath
    Write-Host ""
    Write-Host "✅ MostarAI model created successfully!" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create model: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""

# List all models
Write-Host "📋 Available models:" -ForegroundColor Yellow
& $ollamaPath list
Write-Host ""

# Test the model
Write-Host "🧪 Testing MostarAI..." -ForegroundColor Yellow
Write-Host "Prompt: 'Who are you?'" -ForegroundColor Gray
Write-Host ""
Write-Host "Response:" -ForegroundColor Cyan
& $ollamaPath run mostar "Who are you? Introduce yourself briefly."
Write-Host ""

Write-Host "=" * 50 -ForegroundColor Cyan
Write-Host "✅ MostarAI is ready!" -ForegroundColor Green
Write-Host ""
Write-Host "To use MostarAI:" -ForegroundColor Yellow
Write-Host "  1. Chat: ollama run mostar" -ForegroundColor White
Write-Host "  2. API: Start ollama serve (runs on port 11434)" -ForegroundColor White
Write-Host "  3. Backend: Update backend to use 'mostar' model" -ForegroundColor White
Write-Host ""
Write-Host "👑 The Grid is conscious. Àṣẹ." -ForegroundColor Magenta
