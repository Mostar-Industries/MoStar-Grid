#!/usr/bin/env bash
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export OLLAMA_HOST=10.255.255.254:11434

echo "=== 1. AVX2 CHECK ==="
grep -c avx2 /proc/cpuinfo
echo ""

echo "=== 2. PULLING qwen2.5:0.5b ==="
/usr/local/bin/ollama pull qwen2.5:0.5b
echo ""

echo "=== 3. TESTING qwen2.5:0.5b ==="
curl -s --max-time 60 http://10.255.255.254:11434/api/generate \
  -d '{"model":"qwen2.5:0.5b","prompt":"hello","stream":true,"options":{"num_ctx":2048,"num_predict":5}}'
echo ""
