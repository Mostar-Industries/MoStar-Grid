#!/bin/bash
export OLLAMA_HOST=127.0.0.1:11434
echo "=== Station Rebuild: MoStar-AI 7B (Mistral) ==="
ollama create mostar/mostar-ai:latest -f /mnt/c/Users/idona/OneDrive\ -\ World\ Health\ Organization/Documents/Dev/MoStar-Grid/Modelfile_mostar_gpu 

echo ""
echo "=== Final Performance Benchmark (CUDA Accelerated) ==="
curl -s http://$OLLAMA_HOST/api/generate -d '{"model": "mostar/mostar-ai:latest", "prompt": "Nnọ Mo! Who are you?", "stream": false}' | python3 -m json.tool
