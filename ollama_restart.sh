#!/usr/bin/env bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

echo "=== Single-token test (num_predict:1, max-time 180s) ==="
curl -s --max-time 180 http://10.255.255.254:11434/api/generate \
  -d '{"model":"mostar/mostar-ai","prompt":"hi","stream":false,"options":{"num_ctx":2048,"num_predict":1}}' \
  -o /tmp/ollama_resp.json

echo "curl exit=$?"
echo "--- Response ---"
cat /tmp/ollama_resp.json
echo ""

# Also check Ollama log tail
echo "--- Last 10 log lines ---"
tail -10 /tmp/ollama.log
