#!/usr/bin/env python3
import requests

try:
    r = requests.get('https://ollama.mostarindustries.com/api/tags', timeout=5)
    print(f'Status: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        models = data.get('models', [])
        print(f'✅ Cloud Ollama WORKING - {len(models)} models found')
        for m in models:
            print(f'   - {m["name"]}')
    else:
        print(f'❌ Cloud Ollama returned {r.status_code}')
        print(f'Response: {r.text[:100]}')
except Exception as e:
    print(f'❌ Cloud Ollama ERROR: {e}')
