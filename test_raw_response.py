#!/usr/bin/env python3
import requests

url = 'https://mo-star-grid-aan76t0cx-mo-101s-projects.vercel.app/api/moments'

try:
    r = requests.get(url, timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Content-Type: {r.headers.get('content-type')}")
    print(f"Response (first 500 chars):\n{r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
