#!/usr/bin/env bash
# Ensure common node/pm2 paths are included
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/.npm-global/bin:$HOME/.local/bin:~/.npm-global/bin:~/.nvm/versions/node/$(nvm current 2>/dev/null)/bin

echo "=== Restarting PM2 ==="
pm2 restart all
sleep 5

echo "=== Chat API Test ==="
curl -s --max-time 60 http://localhost:7001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Nnọ Mo. Who are you?"}' | python3 -m json.tool
