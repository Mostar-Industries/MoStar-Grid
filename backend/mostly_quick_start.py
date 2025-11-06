#!/usr/bin/env python3
"""
MostlyAI Quick Start - Train Generator for MoStar Grid
Run this script to create your lifecycle/knowledge generator.
"""
import os
from mostlyai.sdk import MostlyAI

# Load environment
from dotenv import load_dotenv
load_dotenv('.env.local')

# Initialize MostlyAI client
mostly = MostlyAI(
    api_key=os.getenv('MOSTLY_API_KEY'),
    base_url=os.getenv('MOSTLY_BASE_URL', 'https://app.mostly.ai')
)

print("🚀 MostlyAI Grid Generator Setup\n")
print("=" * 60)

# Option 1: Use census data (quickstart)
print("\n[Option 1] Train with Census Data (Quick Demo)")
print("This will create a generator using public census data.")

response = input("\nTrain census generator? (y/n): ").strip().lower()
if response == 'y':
    print("\n⏳ Training generator (this may take a few minutes)...")
    g = mostly.train(
        data='https://github.com/mostly-ai/public-demo-data/raw/dev/census/census.csv.gz',
        name='mostar-grid-census'
    )
    print(f"✅ Generator created: {g.id}")
    print(f"   Name: {g.name}")
    
    # Test with probe
    print("\n⏳ Probing for 10 samples...")
    probe_result = mostly.probe(g, size=10)
    print(f"✅ Probe successful: {len(probe_result)} samples")
    
    # Save generator ID
    print(f"\n📝 Add this to your .env.local:")
    print(f"MOSTLY_GENERATOR_ID={g.id}")
    
    # Update .env.local automatically
    env_path = '.env.local'
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    with open(env_path, 'w') as f:
        for line in lines:
            if line.startswith('MOSTLY_GENERATOR_ID='):
                f.write(f'MOSTLY_GENERATOR_ID={g.id}\n')
            else:
                f.write(line)
    
    print(f"✅ Updated {env_path} with generator ID")

# Option 2: Upload your own data
print("\n" + "=" * 60)
print("[Option 2] Train with Your Own Data")
print("You can upload CSV/Parquet files for custom lifecycle data.")
print("Example: infancy.csv, childhood.csv, science.csv, etc.")

response = input("\nUpload custom data? (y/n): ").strip().lower()
if response == 'y':
    data_path = input("Enter path to your data file: ").strip()
    if os.path.exists(data_path):
        print(f"\n⏳ Training generator with {data_path}...")
        g = mostly.train(
            data=data_path,
            name='mostar-grid-lifecycle'
        )
        print(f"✅ Generator created: {g.id}")
        print(f"\n📝 Add this to your .env.local:")
        print(f"MOSTLY_GENERATOR_ID={g.id}")
    else:
        print(f"❌ File not found: {data_path}")

print("\n" + "=" * 60)
print("✅ Setup complete! Restart your backend to use MostlyAI integration.")
print("\nNext steps:")
print("1. Restart backend: python grid_main.py")
print("2. Test probe: POST /api/synthetic/probe")
print("3. Generate data: POST /api/synthetic/generate")
