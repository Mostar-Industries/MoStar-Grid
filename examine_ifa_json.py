#!/usr/bin/env python3
import json

# Load the Ifá 256 corpus JSON
with open('/home/idona/MoStar/MoStar-Grid/backend/neo4j-mostar-industries/import/data/scripts/ifa_256_corpus.json', 'r') as f:
    data = json.load(f)

print("JSON Keys:", list(data.keys()))
print("Metadata:", data.get('metadata', {}))
print("Principal Odu count:", len(data.get('principal_odu', [])))
print("Compound Odu count:", len(data.get('compound_odu', [])))

# Show first principal odu structure
if data.get('principal_odu'):
    print("\nFirst Principal Odu:")
    first_odu = data['principal_odu'][0]
    for key, value in first_odu.items():
        print(f"  {key}: {value}")

# Show first compound odu structure  
if data.get('compound_odu'):
    print("\nFirst Compound Odu:")
    first_compound = data['compound_odu'][0]
    for key, value in first_compound.items():
        print(f"  {key}: {value}")
