#!/usr/bin/env python3
import requests
import json

base = "https://mostar-grid.vercel.app"

endpoints = [
    "/api/moments",
    "/api/moment",
    "/api/voice",
    "/api/consciousness",
    "/api/chat",
]

print("=" * 70)
print("ENDPOINT ROUTING DIAGNOSTIC")
print("=" * 70)

for endpoint in endpoints:
    url = f"{base}{endpoint}"
    print(f"\n{endpoint}:")
    try:
        r = requests.get(url, timeout=5)
        data = r.json()
        
        # Check response structure
        fields = list(data.keys())
        print(f"  Status: {r.status_code}")
        print(f"  Fields: {fields}")
        
        if "insignia" in data:
            print(f"  ⚠️  Contains 'insignia' (OLD code)")
        if "provenance" in data:
            print(f"  ✅ Contains 'provenance' (NEW code)")
            
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:60]}")

print("\n" + "=" * 70)
print("ANALYSIS")
print("=" * 70)
print("""
If /api/moments returns OLD code (insignia field):
- The serverless handler (frontend/api/moments.js) is NOT being used
- Vercel may be serving from a different project or old code path

If /api/moments returns NEW code (provenance field):
- The deployment is correct
- Check Neo4j env vars and connection

If /api/moments times out or 404s:
- The route doesn't exist in the deployed version
- Vercel may be building from wrong repo/branch
""")
