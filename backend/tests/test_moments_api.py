#!/usr/bin/env python3
import requests
import json

try:
    r = requests.get('https://mostar-grid.vercel.app/api/moments', timeout=10)
    print(f'Status: {r.status_code}')
    data = r.json()
    
    moments_count = data.get('count', 0)
    error = data.get('provenance', {}).get('error', None)
    
    print(f'Moments found: {moments_count}')
    if error:
        print(f'Error: {error}')
    else:
        print(f'Source: {data.get("provenance", {}).get("source", "unknown")}')
        if moments_count > 0:
            print(f'✅ /api/moments is pulling from Neo4j!')
        else:
            print(f'⚠️  No moments in database yet')
            
except Exception as e:
    print(f'❌ Error: {e}')
