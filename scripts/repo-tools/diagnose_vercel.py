#!/usr/bin/env python3
import requests
import json

print("=" * 70)
print("VERCEL DEPLOYMENT DIAGNOSTIC")
print("=" * 70)

# Test 1: Check if the response matches current code
print("\n1. Testing /api/moments response structure:")
try:
    r = requests.get('https://mostar-grid.vercel.app/api/moments', timeout=10)
    data = r.json()
    
    has_insignia = 'insignia' in data
    has_provenance = 'provenance' in data
    has_generatedAt = 'generatedAt' in data
    
    print(f"   Status: {r.status_code}")
    print(f"   Has 'insignia' field: {has_insignia} (OLD code)")
    print(f"   Has 'provenance' field: {has_provenance} (NEW code)")
    print(f"   Has 'generatedAt' field: {has_generatedAt} (OLD code)")
    
    if has_insignia and not has_provenance:
        print("\n   ⚠️  DIAGNOSIS: Serving OLD code (not from commit dc1b753)")
    elif has_provenance:
        print("\n   ✅ DIAGNOSIS: Serving NEW code (from commit dc1b753)")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Check deployment headers
print("\n2. Checking response headers for deployment info:")
try:
    r = requests.head('https://mostar-grid.vercel.app/api/moments', timeout=10)
    headers = r.headers
    
    print(f"   Server: {headers.get('Server', 'unknown')}")
    print(f"   X-Vercel-Id: {headers.get('X-Vercel-Id', 'unknown')}")
    print(f"   X-Vercel-Cache: {headers.get('X-Vercel-Cache', 'unknown')}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Check git status locally
print("\n3. Local git status:")
import subprocess
try:
    result = subprocess.run(
        ['git', 'log', '-1', '--oneline'],
        cwd='c:\\Users\\idona\\OneDrive - World Health Organization\\Documents\\Dev\\MoStar-Grid',
        capture_output=True,
        text=True
    )
    print(f"   Latest commit: {result.stdout.strip()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("""
If diagnosis shows OLD code being served:
1. Go to: https://vercel.com/mo-101s-projects/mo-star-grid/deployments
2. Find deployment from commit dc1b753 (fix: add frontend/api/moments...)
3. Click it and ensure status is "Ready"
4. Click "Promote to Production" if not already
5. Wait 30 seconds and re-run this diagnostic

If diagnosis shows NEW code:
- The deployment is working correctly
- Check Neo4j env vars are set in Vercel settings
- Test should return real moments data from Neo4j Aura
""")
