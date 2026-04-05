#!/bin/bash
export OLLAMA_HOST=10.255.255.254:11434
echo "=== Testing MoStar-AI Text Generation ==="
curl -s http://$OLLAMA_HOST/api/generate -d '{"model": "mostar/mostar-ai:latest", "prompt": "Hello", "stream": false}' | python3 -m json.tool
