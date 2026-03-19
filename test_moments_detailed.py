#!/usr/bin/env python3
import requests
import json

try:
    r = requests.get('https://mostar-grid.vercel.app/api/moments', timeout=10)
    print(f'Status: {r.status_code}')
    
    data = r.json()
    print(f'\nFull Response:')
    print(json.dumps(data, indent=2))
    
    provenance = data.get('provenance', {})
    print(f'\nProvenance Details:')
    print(f'  Source: {provenance.get("source", "unknown")}')
    print(f'  Error: {provenance.get("error", "None")}')
    print(f'  Error Type: {provenance.get("error_type", "None")}')
    print(f'  URI: {provenance.get("uri", "Not set")}')
    
except Exception as e:
    print(f'❌ Error: {e}')
