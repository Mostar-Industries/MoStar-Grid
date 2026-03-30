#!/usr/bin/env bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/.npm-global/bin:$HOME/.local/bin:~/.npm-global/bin:~/.nvm/versions/node/$(nvm current 2>/dev/null)/bin

echo "=== Stopping PM2 to clear cache ==="
pm2 stop all 2>/dev/null

echo "=== Starting PM2 with updated .env ==="
cd "/mnt/c/Users/idona/OneDrive - World Health Organization/Documents/Dev/MoStar-Grid"
pm2 restart ecosystem.config.js --update-env || pm2 start ecosystem.config.js --update-env
sleep 5

echo "=== PM2 Backend Logs (20 lines) ==="
pm2 logs mostar-backend --lines 20 --nostream

echo "=== Chat API Test ==="
curl -s --max-time 60 http://localhost:7001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Nnọ Mo. Who are you?"}' | python3 -m json.tool
