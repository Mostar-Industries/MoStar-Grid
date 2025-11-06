# 📈 Large Dataset Generation Guide

Complete guide to generating **millions of rows** with your MostlyAI generator.

---

## 🎯 Quick Start

### Generate 10K Rows (All Tables)

```bash
python backend/scripts/generate_large_dataset.py --all --size 10000
```

### Generate 500K Rows (All Tables)

```bash
python backend/scripts/generate_large_dataset.py --all --size 500000
```

### Generate 1 Million Rows (All Tables)

```bash
python backend/scripts/generate_large_dataset.py --all --size 1000000 --batch-size 100000
```

---

## 📊 Capacity & Limits

### Updated Limits

| Limit | Previous | **New** |
|-------|----------|---------|
| **Default Size** | 100 | **1,000** |
| **Max per Request** | 10,000 | **100,000** |
| **Batch Support** | No | **Yes** |
| **Total Capacity** | ~100K | **Unlimited** (batched) |

### What You Can Generate

```
9 tables × 1,000,000 rows = 9,000,000 total records

Breakdown:
• infancy:        10,000,000 rows
• childhood:      15,000,000 rows
• adolescence:    9,000,000 rows
• adulthood:      9,000,000 rows
• culture:        10,000,000 rows
• ethics:         10,000,000 rows
• knowledge_graph: 10,000,000 rows
• real_life:      10,000,000 rows
• science:        10,000,000 rows
```

---

## 🚀 Generation Methods

### Method 1: Python Script (Recommended)

```bash
# Activate environment
backend\server\.venv\Scripts\Activate.ps1

# Generate all tables with 50K rows each
python backend/scripts/generate_large_dataset.py \
  --all \
  --size 50000

# Generate specific lifecycle stages with 100K rows
python backend/scripts/generate_large_dataset.py \
  --lifecycle childhood adolescence adulthood \
  --size 100000

# Generate specific knowledge domains with 200K rows
python backend/scripts/generate_large_dataset.py \
  --knowledge culture ethics knowledge_graph \
  --size 200000 \
  --batch-size 50000
```

### Method 2: Direct API Call

#### Standard Endpoint (up to 100K rows)

```bash
curl -X POST http://localhost:8000/api/synthetic/generate \
  -H "Content-Type: application/json" \
  -d '{
    "lifecycle_stages": ["infancy", "childhood", "adolescence", "adulthood"],
    "knowledge_domains": ["culture", "ethics", "knowledge_graph", "real_life", "science"],
    "size_per_table": 50000
  }'
```

#### Batch Endpoint (100K+ rows)

```bash
curl -X POST http://localhost:8000/api/synthetic/batch-generate \
  -H "Content-Type: application/json" \
  -d '{
    "lifecycle_stages": ["infancy", "childhood", "adolescence", "adulthood"],
    "knowledge_domains": ["culture", "ethics", "knowledge_graph", "real_life", "science"],
    "total_size": 500000,
    "batch_size": 50000
  }'
```

### Method 3: Python Code

```python
import asyncio
import httpx

async def generate_massive_dataset():
    """Generate 1 million rows per table"""
    
    async with httpx.AsyncClient(timeout=3600.0) as client:
        response = await client.post(
            "http://localhost:8000/api/synthetic/batch-generate",
            json={
                "lifecycle_stages": ["infancy", "childhood", "adolescence", "adulthood"],
                "knowledge_domains": ["culture", "ethics", "knowledge_graph", "real_life", "science"],
                "total_size": 1000000,
                "batch_size": 100000
            }
        )
        
        result = response.json()
        print(f"✅ Generated {result['total_records']:,} total records")
        print(f"📦 Completed {result['batches_completed']} batches")
        print(f"🎯 Average resonance: {result['avg_resonance']:.4f}")
        
        return result

# Run
asyncio.run(generate_massive_dataset())
```

---

## 📋 Command Reference

### Script Options

```bash
python backend/scripts/generate_large_dataset.py [OPTIONS]

Options:
  --all                        Generate all 9 tables
  --lifecycle STAGE [STAGE...] Generate specific lifecycle stages
                               Choices: infancy, childhood, adolescence, adulthood
  --knowledge DOMAIN [DOMAIN...] Generate specific knowledge domains
                               Choices: culture, ethics, knowledge_graph, real_life, science
  --size N                     Rows per table (default: 1000)
  --batch-size N               Rows per batch (default: 50000)
  --use-batch                  Force batch endpoint
  -h, --help                   Show help message
```

### Examples

```bash
# 1. Quick test (1K rows each)
python backend/scripts/generate_large_dataset.py --all --size 1000

# 2. Medium dataset (10K rows each)
python backend/scripts/generate_large_dataset.py --all --size 10000

# 3. Large dataset (100K rows each)
python backend/scripts/generate_large_dataset.py --all --size 100000

# 4. Massive dataset (1M rows each, 9M total)
python backend/scripts/generate_large_dataset.py --all --size 1000000 --batch-size 100000

# 5. Only lifecycle stages (500K each)
python backend/scripts/generate_large_dataset.py \
  --lifecycle infancy childhood adolescence adulthood \
  --size 500000

# 6. Only knowledge domains (250K each)
python backend/scripts/generate_large_dataset.py \
  --knowledge culture ethics knowledge_graph real_life science \
  --size 250000

# 7. Specific tables (custom size)
python backend/scripts/generate_large_dataset.py \
  --lifecycle childhood adolescence \
  --knowledge culture ethics \
  --size 75000
```

---

## ⚡ Performance Optimization

### Batch Size Guidelines

| Total Rows per Table | Recommended Batch Size | Batches Needed |
|---------------------|------------------------|----------------|
| 1,000 - 50,000 | Single request | 1 |
| 50,000 - 100,000 | 50,000 | 1-2 |
| 100,000 - 500,000 | 50,000 - 100,000 | 5-10 |
| 500,000 - 1,000,000 | 100,000 | 10 |
| 1,000,000+ | 100,000 | 10+ |

### Estimated Generation Times

Based on typical API performance:

| Rows per Table | Total Rows (9 tables) | Estimated Time |
|---------------|----------------------|----------------|
| 1,000 | 9,000 | ~10 seconds |
| 10,000 | 90,000 | ~30 seconds |
| 50,000 | 450,000 | ~2 minutes |
| 100,000 | 900,000 | ~5 minutes |
| 500,000 | 4,500,000 | ~25 minutes |
| 1,000,000 | 9,000,000 | ~50 minutes |

*Times vary based on network, API load, and data complexity*

---

## 💾 Storage Requirements

### Estimated Storage per Row

Assuming average record size of ~500 bytes:

```
1,000 rows      = ~500 KB
10,000 rows     = ~5 MB
100,000 rows    = ~50 MB
1,000,000 rows  = ~500 MB

Full dataset (9M rows) = ~4.5 GB
```

### Database Storage

PostgreSQL storage with indexes:

```
Table          Rows        Storage (approx)
─────────────────────────────────────────
infancy        1,000,000   ~650 MB
childhood      1,000,000   ~650 MB
adolescence    1,000,000   ~650 MB
adulthood      1,000,000   ~650 MB
culture        1,000,000   ~650 MB
ethics         1,000,000   ~650 MB
knowledge_graph 1,000,000  ~650 MB
real_life      1,000,000   ~650 MB
science        1,000,000   ~650 MB
─────────────────────────────────────────
Total          9,000,000   ~6 GB (with indexes)
```

---

## 🔍 Monitoring Progress

### Real-time Progress

When using the batch endpoint or script, you'll see:

```
==================================================================================
🎯 MoStar GRID - Synthetic Data Generation
==================================================================================
Generator ID: 22df93d3-bd0d-4857-ba69-0653249ddfd4
Lifecycle Stages: ['infancy', 'childhood', 'adolescence', 'adulthood']
Knowledge Domains: ['culture', 'ethics', 'knowledge_graph', 'real_life', 'science']
Size per table: 500,000 rows
Total tables: 9
Total records: 4,500,000
==================================================================================

📊 Using batch generation (batch size: 50,000 rows)
Batch 1/10 complete (10.0%)
Batch 2/10 complete (20.0%)
Batch 3/10 complete (30.0%)
...
Batch 10/10 complete (100.0%)

✅ Batch Generation Complete!
Total records: 4,500,000
Batches completed: 10
Average resonance: 0.7521

Table breakdown:
  • infancy              500,000 rows
  • childhood            500,000 rows
  • adolescence          500,000 rows
  • adulthood            500,000 rows
  • culture              500,000 rows
  • ethics               500,000 rows
  • knowledge_graph      500,000 rows
  • real_life            500,000 rows
  • science              500,000 rows

⏱️  Total time: 1523.4 seconds
==================================================================================
```

---

## 🎯 Production Recommendations

### For Development

```bash
# Quick testing (completes in seconds)
python backend/scripts/generate_large_dataset.py --all --size 1000
```

### For Staging

```bash
# Representative sample (completes in ~2 minutes)
python backend/scripts/generate_large_dataset.py --all --size 50000
```

### For Production

```bash
# Full dataset (completes in ~50 minutes)
python backend/scripts/generate_large_dataset.py \
  --all \
  --size 1000000 \
  --batch-size 100000
```

---

## 🐛 Troubleshooting

### Issue: Timeout Error

**Symptom**: Request times out for large datasets

**Solution**:
```python
# Increase timeout in your client
async with httpx.AsyncClient(timeout=3600.0) as client:
    # Your request here
```

### Issue: Memory Error

**Symptom**: Out of memory when generating large datasets

**Solution**: Use smaller batch sizes
```bash
# Instead of 100K batches, use 50K
python backend/scripts/generate_large_dataset.py \
  --all \
  --size 1000000 \
  --batch-size 50000
```

### Issue: Slow Generation

**Symptom**: Generation taking longer than expected

**Solutions**:
1. Check API key is set correctly
2. Verify network connection
3. Use batch endpoint for sizes > 100K
4. Increase batch size (up to 100K)

---

## 📊 Verification

### Check Generated Data

```bash
# Check generator status
curl http://localhost:8000/api/synthetic/status

# Verify data was generated
curl http://localhost:8000/api/health
```

### Sample Generation Test

```bash
# Test with small sample first
python backend/scripts/generate_large_dataset.py \
  --lifecycle childhood \
  --size 100

# If successful, scale up
python backend/scripts/generate_large_dataset.py \
  --all \
  --size 100000
```

---

## 🚀 Next Steps

1. **Start Small**: Test with 1K rows
2. **Verify Quality**: Check resonance scores
3. **Scale Up**: Gradually increase to 100K, 500K, 1M
4. **Production**: Generate full dataset (9M rows)
5. **Persist**: Save to database for Grid use

---

## 📞 Configuration

Update your `.env` with generator credentials:

```bash
MOSTLY_API_KEY=your_api_key_here
MOSTLY_GENERATOR_ID=22df93d3-bd0d-4857-ba69-0653249ddfd4
MOSTLY_BASE_URL=https://api.mostly.ai/v1
```

**Your generator is ready to produce unlimited data!** 🎉
