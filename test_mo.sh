#!/usr/bin/env bash
echo "=== Chat API Test ==="
curl -s --max-time 150 http://localhost:7001/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Nnọ Mo. Who are you?"}' | python3 -m json.tool
