@echo off
REM ╔══════════════════════════════════════════════════════╗
REM ║       MOSTAR GRID — ONE-TIME PM2 SETUP               ║
REM ║       Run this ONCE as Administrator                  ║
REM ╚══════════════════════════════════════════════════════╝

echo [1/5] Installing PM2 globally...
npm install -g pm2

echo [2/5] Installing PM2 Windows service installer...
npm install -g pm2-installer

echo [3/5] Creating logs directory...
mkdir "C:\Users\idona\OneDrive - World Health Organization\Documents\Dev\MoStar-Grid\logs"

echo [4/5] Starting Grid processes from ecosystem config...
pm2 start "C:\Users\idona\OneDrive - World Health Organization\Documents\Dev\MoStar-Grid\ecosystem.config.js"

echo [5/5] Saving process list so it survives reboot...
pm2 save

echo.
echo ══════════════════════════════════════════
echo  Grid is running. Check status with:
echo  pm2 status
echo.
echo  To install as Windows startup service:
echo  pm2-installer install
echo ══════════════════════════════════════════
pause
