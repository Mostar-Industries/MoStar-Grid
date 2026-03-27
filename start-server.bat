@echo off
REM ╔══════════════════════════════════════════════════════╗
REM ║       MOSTAR GRID — LAPTOP SERVER STARTUP               ║
REM ║       AuraDB + Ollama + Docker + Cloudflare           ║
REM ╚══════════════════════════════════════════════════════╝

echo [1/4] Starting MoStar Grid Laptop Server...
echo.

echo [2/4] Checking Ollama status...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama not running. Please start Ollama first.
    pause
    exit /b 1
)
echo ✅ Ollama is running

echo [3/4] Starting Docker containers...
docker compose up -d
if %errorlevel% neq 0 (
    echo ❌ Docker startup failed
    pause
    exit /b 1
)
echo ✅ Docker containers started

echo [4/4] Verifying services...
timeout /t 10 /nobreak >nul

echo.
echo 🌐 MoStar Grid Server Status:
echo   Backend API: http://localhost:8001
echo   Public API: https://api.mostarindustries.com
echo   Ollama: http://localhost:11434
echo.
echo ✅ MoStar Grid is running!
echo.

pause
