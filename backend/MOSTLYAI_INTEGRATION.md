# 🎯 MostlyAI Synthetic Data Integration

Complete integration of your MostlyAI generator (65.8% accuracy, 9 tables) with MoStar GRID.

## 📊 Generator Status

✅ **Ready to Use**
- **9 Tables**: infancy, childhood, adolescence, adulthood, culture, ethics, knowledge_graph, real_life, science
- **Accuracy**: 65.8%
- **Status**: DONE (fully trained and operational)

---

## 🔧 Setup

### 1. Environment Variables

Add to your `.env` file:

```bash
# MostlyAI Configuration
MOSTLY_API_KEY=your_mostly_api_key_here
MOSTLY_BASE_URL=https://api.mostly.ai/v1
MOSTLY_GENERATOR_ID=your_generator_id_here

# Grid Configuration (existing)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ALLOW_ORIGINS=http://localhost:5173
```

### 2. Start the Backend

```bash
# Activate virtual environment
backend\server\.venv\Scripts\Activate.ps1

# Run FastAPI server
uvicorn backend.server.main:app --reload --port 8000
```

---

## 📡 API Endpoints

### 1. **Generate Full Synthetic Dataset**

**POST** `/api/synthetic/generate`

Generate data across multiple tables with full control.

**Request Body:**
```json
{
  "lifecycle_stages": ["childhood", "adolescence"],
  "knowledge_domains": ["culture", "ethics"],
  "size_per_table": 500,
  "conditions": {
    "language": "Swahili",
    "region": "East Africa"
  },
  "covenant_threshold": 0.97
}
```

**Response:**
```json
{
  "job_id": "abc123",
  "status": "completed",
  "tables": {
    "childhood": 500,
    "adolescence": 500,
    "culture": 500,
    "ethics": 500
  },
  "resonance_score": 0.7521,
  "timestamp": "2025-11-06T02:30:00Z",
  "data": { ... }
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:8000/api/synthetic/generate \
  -H "Content-Type: application/json" \
  -d '{
    "lifecycle_stages": ["adulthood"],
    "knowledge_domains": ["knowledge_graph"],
    "size_per_table": 100
  }'
```

---

### 2. **Generate Lifecycle Data**

**POST** `/api/synthetic/lifecycle`

Quick generation of lifecycle stage data.

**Query Parameters:**
- `stages` (array): One or more of: `infancy`, `childhood`, `adolescence`, `adulthood`
- `size` (int): Records per stage (default: 100)
- `conditions` (object, optional): Filters

**Example:**
```bash
curl -X POST "http://localhost:8000/api/synthetic/lifecycle?stages=childhood&stages=adolescence&size=1000"
```

---

### 3. **Generate Knowledge Domain Data**

**POST** `/api/synthetic/knowledge`

Quick generation of knowledge domain data.

**Query Parameters:**
- `domains` (array): One or more of: `culture`, `ethics`, `knowledge_graph`, `real_life`, `science`
- `size` (int): Records per domain (default: 100)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/synthetic/knowledge?domains=culture&domains=ethics&size=500"
```

---

### 4. **Check Generator Status**

**GET** `/api/synthetic/status`

Get generator metadata and available tables.

**Response:**
```json
{
  "generator_ready": true,
  "tables": {
    "lifecycle": ["infancy", "childhood", "adolescence", "adulthood"],
    "knowledge": ["culture", "ethics", "knowledge_graph", "real_life", "science"]
  },
  "accuracy": 0.658,
  "status": "operational",
  "version": "1.0.0"
}
```

---

## 💻 Python Usage Examples

### Example 1: Generate Grid Consciousness Training Data

```python
import httpx
import asyncio

async def populate_grid_consciousness():
    """Generate synthetic data for Grid training"""
    
    async with httpx.AsyncClient() as client:
        # Generate all lifecycle stages
        response = await client.post(
            "http://localhost:8000/api/synthetic/lifecycle",
            params={
                "stages": ["infancy", "childhood", "adolescence", "adulthood"],
                "size": 1000
            }
        )
        data = response.json()
        
        print(f"Generated {sum(data['tables'].values())} records")
        print(f"Resonance score: {data['resonance_score']}")
        
        return data

# Run
asyncio.run(populate_grid_consciousness())
```

### Example 2: Conditional Generation (Swahili Culture)

```python
async def generate_swahili_data():
    """Generate culturally specific data"""
    
    payload = {
        "lifecycle_stages": ["childhood", "adolescence"],
        "knowledge_domains": ["culture", "ethics"],
        "size_per_table": 500,
        "conditions": {
            "language": "Swahili",
            "region": "East Africa",
            "cultural_context": "Ubuntu"
        },
        "covenant_threshold": 0.75  # Adjusted for cultural specificity
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/synthetic/generate",
            json=payload,
            timeout=600.0  # 10 min for large datasets
        )
        return response.json()
```

### Example 3: Background Batch Processing

```python
from fastapi import BackgroundTasks

async def refresh_grid_data(background_tasks: BackgroundTasks):
    """Schedule periodic Grid data refresh"""
    
    background_tasks.add_task(generate_and_store_data)
    return {"status": "scheduled"}

async def generate_and_store_data():
    """Background job to generate and persist data"""
    
    client = get_mostly_client()
    request = SyntheticRequest(
        lifecycle_stages=["adulthood"],
        knowledge_domains=["knowledge_graph", "science"],
        size_per_table=5000
    )
    
    result = await client.generate_synthetic_data(request)
    
    # Store to database
    for table_name, records in result.data.items():
        await store_synthetic_records(table_name, records)
```

---

## 🎨 Frontend Integration (React/TypeScript)

### React Hook for Synthetic Data

```typescript
// src/hooks/useSyntheticData.ts
import { useState } from 'react';

interface SyntheticDataRequest {
  lifecycle_stages?: string[];
  knowledge_domains?: string[];
  size_per_table: number;
  conditions?: Record<string, any>;
}

export function useSyntheticData() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateData = async (request: SyntheticDataRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/synthetic/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        throw new Error(`Generation failed: ${response.statusText}`);
      }

      const data = await response.json();
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { generateData, loading, error };
}
```

### Component Example

```tsx
// src/components/SyntheticDataPanel.tsx
import React, { useState } from 'react';
import { useSyntheticData } from '../hooks/useSyntheticData';

export function SyntheticDataPanel() {
  const { generateData, loading, error } = useSyntheticData();
  const [result, setResult] = useState(null);

  const handleGenerate = async () => {
    const data = await generateData({
      lifecycle_stages: ['childhood', 'adolescence'],
      knowledge_domains: ['culture', 'ethics'],
      size_per_table: 100,
    });
    setResult(data);
  };

  return (
    <div className="p-4 border rounded">
      <h2 className="text-xl font-bold mb-4">Synthetic Data Generator</h2>
      
      <button
        onClick={handleGenerate}
        disabled={loading}
        className="bg-purple-600 text-white px-4 py-2 rounded"
      >
        {loading ? 'Generating...' : 'Generate Data'}
      </button>

      {error && (
        <div className="mt-4 p-2 bg-red-100 text-red-800 rounded">
          Error: {error}
        </div>
      )}

      {result && (
        <div className="mt-4 p-4 bg-gray-100 rounded">
          <p>Status: {result.status}</p>
          <p>Records: {JSON.stringify(result.tables)}</p>
          <p>Resonance: {result.resonance_score}</p>
        </div>
      )}
    </div>
  );
}
```

---

## 🔒 Covenant Integration

The synthetic data generator is integrated with MoStar Grid's covenant system:

- **Resonance Scoring**: Each generated dataset is scored (0.0-1.0)
- **Threshold Enforcement**: Default 0.97 minimum (Grid covenant)
- **Ifá Validation**: Symbolic validation through Grid's Ifá engine
- **Trust Tiers**: Only Allied/Vassal actors can generate data

---

## 🚀 Performance Optimization

### 1. **Caching Strategy**

```python
from functools import lru_cache
from datetime import datetime, timedelta

@lru_cache(maxsize=100)
def get_cached_synthetic_data(
    stage: str,
    size: int,
    timestamp: str  # Cache key (hourly refresh)
):
    """Cache synthetic data for 1 hour"""
    # Implementation
```

### 2. **Batch Processing**

```python
async def batch_generate(
    stages: List[str],
    batch_size: int = 1000
):
    """Generate large datasets in batches"""
    
    results = []
    for i in range(0, len(stages), batch_size):
        batch = stages[i:i + batch_size]
        result = await generate_lifecycle_data(batch, size=batch_size)
        results.append(result)
        await asyncio.sleep(1)  # Rate limiting
    
    return results
```

### 3. **Async Queue**

```python
from asyncio import Queue

synthetic_queue = Queue()

async def queue_worker():
    """Background worker for synthetic generation"""
    while True:
        request = await synthetic_queue.get()
        await generate_and_process(request)
        synthetic_queue.task_done()
```

---

## 📈 Monitoring & Metrics

### Key Metrics to Track

1. **Generation Success Rate**
   - Target: >95%
   - Alert if <90%

2. **Average Resonance Score**
   - Target: >0.70
   - Alert if <0.60

3. **Generation Latency**
   - p50: <5s for 100 records
   - p95: <30s for 1000 records

4. **API Error Rate**
   - Target: <1%

---

## 🐛 Troubleshooting

### Issue: Low Resonance Scores

**Symptom**: Generated data consistently fails covenant threshold

**Solution**:
```python
# Adjust threshold for specific use cases
request = SyntheticRequest(
    lifecycle_stages=["childhood"],
    size_per_table=100,
    covenant_threshold=0.65  # Lower threshold
)
```

### Issue: API Timeout

**Symptom**: 504 Gateway Timeout for large datasets

**Solution**:
```python
# Increase timeout and use batching
async with httpx.AsyncClient(timeout=600.0) as client:
    # Generate in smaller batches
```

### Issue: Mock Data in Production

**Symptom**: Receiving mock data instead of real synthetic data

**Solution**:
```bash
# Verify environment variables are set
echo $MOSTLY_API_KEY
echo $MOSTLY_GENERATOR_ID

# Check server logs for connection errors
```

---

## 📚 Next Steps

1. **Test the Integration**
   ```bash
   curl http://localhost:8000/api/synthetic/status
   ```

2. **Generate Sample Data**
   ```bash
   curl -X POST "http://localhost:8000/api/synthetic/lifecycle?stages=childhood&size=10"
   ```

3. **Build Frontend UI**
   - Add Synthetic Data panel to Dashboard
   - Create data visualization components
   - Implement real-time generation status

4. **Scale Up**
   - Configure production MostlyAI credentials
   - Set up database persistence
   - Implement caching layer
   - Add monitoring/alerting

---

## 🤝 Support

For issues or questions:
- Check API docs: `http://localhost:8000/docs`
- Review logs: `backend/logs/`
- Grid status: `http://localhost:8000/api/health`

**Generator Info**: 65.8% accuracy, 9 tables, fully operational ✅
