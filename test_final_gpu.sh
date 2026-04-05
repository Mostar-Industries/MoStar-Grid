#!/bin/bash
export OLLAMA_HOST=127.0.0.1:11434
echo "=== Testing MoStar-AI Text Generation (GPU-Station) ==="
curl -s http://$OLLAMA_HOST/api/generate -d '{"model": "mostar/mostar-ai:latest", "prompt": "Nnọ! Who are you?", "stream": false}' | python3 -m json.tool
