"""
Script to generate large synthetic datasets for MoStar GRID
Supports generating millions of records across all 9 tables
"""
import asyncio
import argparse
import httpx
from datetime import datetime

# Configuration
API_BASE = "http://localhost:8000"
GENERATOR_ID = "22df93d3-bd0d-4857-ba69-0653249ddfd4"

# Available tables
LIFECYCLE_TABLES = ["infancy", "childhood", "adolescence", "adulthood"]
KNOWLEDGE_TABLES = ["culture", "ethics", "knowledge_graph", "real_life", "science"]
ALL_TABLES = LIFECYCLE_TABLES + KNOWLEDGE_TABLES

async def generate_dataset(
    lifecycle_stages: list[str],
    knowledge_domains: list[str],
    size_per_table: int,
    batch_size: int = 50000,
    use_batch_endpoint: bool = False
):
    """
    Generate synthetic dataset with specified parameters
    
    Args:
        lifecycle_stages: List of lifecycle stages to generate
        knowledge_domains: List of knowledge domains to generate
        size_per_table: Number of rows per table
        batch_size: Rows per batch (for large datasets)
        use_batch_endpoint: Use batch endpoint for sizes > 100K
    """
    print("=" * 80)
    print("🎯 MoStar GRID - Synthetic Data Generation")
    print("=" * 80)
    print(f"Generator ID: {GENERATOR_ID}")
    print(f"Lifecycle Stages: {lifecycle_stages}")
    print(f"Knowledge Domains: {knowledge_domains}")
    print(f"Size per table: {size_per_table:,} rows")
    print(f"Total tables: {len(lifecycle_stages) + len(knowledge_domains)}")
    print(f"Total records: {(len(lifecycle_stages) + len(knowledge_domains)) * size_per_table:,}")
    print("=" * 80)
    
    start_time = datetime.now()
    
    async with httpx.AsyncClient(timeout=3600.0) as client:
        
        if use_batch_endpoint and size_per_table > 100000:
            # Use batch endpoint for very large datasets
            print(f"\n📊 Using batch generation (batch size: {batch_size:,} rows)")
            
            response = await client.post(
                f"{API_BASE}/api/synthetic/batch-generate",
                json={
                    "lifecycle_stages": lifecycle_stages,
                    "knowledge_domains": knowledge_domains,
                    "total_size": size_per_table,
                    "batch_size": batch_size
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Batch Generation Complete!")
                print(f"Total records: {result['total_records']:,}")
                print(f"Batches completed: {result['batches_completed']}")
                print(f"Average resonance: {result['avg_resonance']:.4f}")
                print("\nTable breakdown:")
                for table, count in result['tables'].items():
                    print(f"  • {table:<20} {count:>10,} rows")
            else:
                print(f"\n❌ Generation failed: {response.status_code}")
                print(response.text)
        
        else:
            # Use standard endpoint
            print(f"\n📊 Using standard generation")
            
            response = await client.post(
                f"{API_BASE}/api/synthetic/generate",
                json={
                    "lifecycle_stages": lifecycle_stages,
                    "knowledge_domains": knowledge_domains,
                    "size_per_table": size_per_table
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print("\n✅ Generation Complete!")
                print(f"Job ID: {result['job_id']}")
                print(f"Status: {result['status']}")
                print(f"Resonance score: {result['resonance_score']:.4f}")
                print("\nTable breakdown:")
                for table, count in result['tables'].items():
                    print(f"  • {table:<20} {count:>10,} rows")
            else:
                print(f"\n❌ Generation failed: {response.status_code}")
                print(response.text)
    
    elapsed = datetime.now() - start_time
    print(f"\n⏱️  Total time: {elapsed.total_seconds():.1f} seconds")
    print("=" * 80)

async def main():
    parser = argparse.ArgumentParser(
        description="Generate large synthetic datasets for MoStar GRID"
    )
    
    parser.add_argument(
        "--lifecycle",
        nargs="+",
        choices=LIFECYCLE_TABLES,
        default=[],
        help="Lifecycle stages to generate"
    )
    
    parser.add_argument(
        "--knowledge",
        nargs="+",
        choices=KNOWLEDGE_TABLES,
        default=[],
        help="Knowledge domains to generate"
    )
    
    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate all 9 tables"
    )
    
    parser.add_argument(
        "--size",
        type=int,
        default=1000,
        help="Number of rows per table (default: 1000)"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50000,
        help="Batch size for large datasets (default: 50000)"
    )
    
    parser.add_argument(
        "--use-batch",
        action="store_true",
        help="Force use of batch endpoint"
    )
    
    args = parser.parse_args()
    
    # Determine which tables to generate
    if args.all:
        lifecycle_stages = LIFECYCLE_TABLES
        knowledge_domains = KNOWLEDGE_TABLES
    else:
        lifecycle_stages = args.lifecycle or []
        knowledge_domains = args.knowledge or []
    
    if not lifecycle_stages and not knowledge_domains:
        print("❌ Error: Must specify --all, --lifecycle, or --knowledge")
        parser.print_help()
        return
    
    # Automatically use batch endpoint for large datasets
    use_batch = args.use_batch or args.size > 100000
    
    await generate_dataset(
        lifecycle_stages=lifecycle_stages,
        knowledge_domains=knowledge_domains,
        size_per_table=args.size,
        batch_size=args.batch_size,
        use_batch_endpoint=use_batch
    )

if __name__ == "__main__":
    asyncio.run(main())
