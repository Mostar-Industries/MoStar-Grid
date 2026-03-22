#!/usr/bin/env python3
import requests
import json

urls = [
    'https://mo-star-grid-aan76t0cx-mo-101s-projects.vercel.app/api/moments',
    'https://mo-star-grid-ihe2wlqxp-mo-101s-projects.vercel.app/api/moments',
    'https://mostar-grid.vercel.app/api/moments'
]

for url in urls:
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        fields = list(data.keys())
        domain = url.split('//')[1].split('/')[0]
        print(f"\n{domain}:")
        print(f"  Status: {r.status_code}")
        print(f"  Fields: {fields}")
        
        if 'provenance' in data:
            print("  ✅ NEW CODE (provenance field found)")
        elif 'insignia' in data:
            print("  ❌ OLD CODE (insignia field found)")
            
    except Exception as e:
        domain = url.split('//')[1].split('/')[0]
        print(f"\n{domain}: ERROR - {str(e)[:60]}")
