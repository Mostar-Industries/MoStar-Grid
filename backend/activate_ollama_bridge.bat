@echo off
echo 🔥 MoStar Grid - Activating Ollama Cloud Bridge...
echo 🚇 Tunnel: mostar-ollama
echo 🌐 URL: https://ollama.mostarindustries.com
echo 🎯 Target: http://192.168.0.103:11434
echo.
echo [CTRL+C] to deactivate the bridge.
echo.
C:\Tools\cloudflared.exe tunnel --url http://192.168.0.103:11434 run mostar-ollama
pause
