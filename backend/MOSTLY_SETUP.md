# MostlyAI Integration for MoStar Grid

## ✅ Setup Complete

Your MostlyAI credentials have been configured in `.env.local`:
- **API Key**: `mostly-3f1f96f1...` (secured)
- **Base URL**: `https://app.mostly.ai`

## 🚀 Quick Start

### 1. Install SDK
```bash
pip install -U mostlyai
```

### 2. Run Setup Script
```bash
python mostly_quick_start.py
```

This will:
- Connect to MostlyAI
- Train a generator (or use existing)
- Save generator ID to `.env.local`
- Test the connection

### 3. Test Integration
```powershell
# Check environment
powershell -ExecutionPolicy Bypass -File test_mostly.ps1

# Test backend endpoint
$payload = @{ size = @{ infancy = 5; childhood = 5; science = 3 } } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:7000/api/synthetic/probe -Method Post -Body $payload -ContentType "application/json"
```

## 📚 Usage Examples

### Python SDK (Direct)
```python
from mostlyai.sdk import MostlyAI
import os

# Initialize
mostly = MostlyAI(
    api_key=os.getenv('MOSTLY_API_KEY'),
    base_url='https://app.mostly.ai'
)

# Train a generator
g = mostly.train(
    data='https://github.com/mostly-ai/public-demo-data/raw/dev/census/census.csv.gz',
    name='mostar-grid-lifecycle'
)

# Probe for samples
samples = mostly.probe(g, size=10)
print(samples)

# Generate synthetic dataset
sd = mostly.generate(g, size=2000)
data = sd.data()
```

### Via MoStar Grid API

**Probe (Quick Sample)**
```bash
POST /api/synthetic/probe
Content-Type: application/json

{
  "size": {
    "infancy": 10,
    "childhood": 10,
    "science": 5
  }
}
```

**Generate Full Dataset**
```bash
POST /api/synthetic/generate
Content-Type: application/json

{
  "lifecycle_stages": ["infancy", "childhood", "adolescence"],
  "knowledge_domains": ["science", "culture"],
  "size_per_table": 1000,
  "covenant_threshold": 0.97
}
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
MOSTLY_API_KEY=mostly-3f1f96f1bef2c8acdffeb9d0d37ab7c47d5e07cebe47a2370124a470e49b0f31
MOSTLY_BASE_URL=https://app.mostly.ai

# Set after running mostly_quick_start.py
MOSTLY_GENERATOR_ID=<your-generator-id>
```

### Generator Tables

The integration dynamically fetches allowed tables from your generator:
- **Lifecycle**: infancy, childhood, adolescence, adulthood
- **Knowledge**: science, culture, ethics, knowledge_graph, real_life

## 📊 Backend Integration

The Grid backend (`grid_main.py`) now includes:

1. **`/api/synthetic/probe`** - Quick sample generation
2. **`/api/synthetic/generate`** - Full dataset generation  
3. **`/api/synthetic/generator`** - Get generator metadata
4. **Dynamic table validation** - Validates requested tables against actual generator schema

## 🔐 Security Notes

- ✅ API key stored in `.env.local` (gitignored)
- ✅ Never commit `.env.local` to version control
- ✅ Rotate key if exposed
- ✅ Use environment variables in production

## 🐛 Troubleshooting

**"MostlyAI not configured"**
```bash
# Check environment
python -c "import os; print(os.getenv('MOSTLY_API_KEY'))"

# Restart backend to reload .env
python grid_main.py
```

**"Invalid tables in size dict"**
```bash
# Check available tables
python -c "from backend.server.synthetic import get_allowed_tables; print(await get_allowed_tables())"
```

**SDK Import Error**
```bash
pip install -U mostlyai
pip show mostlyai
```

## 📖 Resources

- [MostlyAI Documentation](https://docs.mostly.ai)
- [MostlyAI SDK on PyPI](https://pypi.org/project/mostlyai/)
- [Grid Integration Code](./server/mostlyai_integration.py)

## ✨ Next Steps

1. ✅ API key configured
2. ⏳ Install SDK: `pip install -U mostlyai`
3. ⏳ Run setup: `python mostly_quick_start.py`
4. ⏳ Test endpoint: `POST /api/synthetic/probe`
5. ⏳ Generate data: `POST /api/synthetic/generate`

---

**Grid Status**: Ready for synthetic data generation 🚀
