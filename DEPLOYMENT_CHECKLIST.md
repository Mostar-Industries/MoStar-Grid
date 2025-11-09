# ✅ MOSTAR AI - DEPLOYMENT CHECKLIST

## Pre-Flight Checks

### 1. Environment Setup
- [ ] Python 3.11+ installed
- [ ] Node.js 20+ installed
- [ ] Neo4j running (port 7687)
- [ ] Ollama installed and running (port 11434)

### 2. Backend Dependencies
```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Frontend Dependencies
```powershell
cd frontend
npm install
```

### 4. Environment Variables
Create `.env` files if needed:

**Backend `.env`:**
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
OLLAMA_URL=http://localhost:11434
```

**Frontend `.env`:**
```env
VITE_API_URL=http://localhost:7000
```

---

## Startup Sequence

### Step 1: Start Neo4j
```powershell
# If using Neo4j Desktop: Start from GUI
# If using Docker:
docker run -d `
  --name neo4j `
  -p 7474:7474 -p 7687:7687 `
  -e NEO4J_AUTH=neo4j/your_password `
  neo4j:latest
```

**Verify:** Open http://localhost:7474

### Step 2: Start Ollama
```powershell
# Pull model if not already done
ollama pull mistral

# Run model
ollama run mistral
```

**Verify:** 
```powershell
curl http://localhost:11434/api/tags
```

### Step 3: Start Backend
```powershell
cd backend
.venv\Scripts\python.exe grid_main.py
```

**Expected Output:**
```
✅ MostarAI Chat router mounted (Sovereign AI online)
✅ Neo4j router mounted (Graph API online)
🚀 Server running on http://localhost:7000
```

**Verify:**
```powershell
curl http://localhost:7000/health
```

### Step 4: Start Frontend
```powershell
cd frontend
npm run dev
```

**Expected Output:**
```
VITE v6.2.0  ready in 1234 ms
➜  Local:   http://localhost:5173/
```

**Verify:** Open http://localhost:5173 in browser

---

## Functional Tests

### Test 1: Chat Endpoint
```powershell
$body = @{ prompt = "What is Ubuntu?" } | ConvertTo-Json
$response = Invoke-RestMethod `
    -Uri "http://localhost:7000/api/chat" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

Write-Host "✅ Chat Response: $($response.response.Substring(0, 100))..."
```

### Test 2: Neo4j Query Endpoint
```powershell
$body = @{
    cypher = "MATCH (n) RETURN count(n) as total"
    parameters = @{}
} | ConvertTo-Json

$response = Invoke-RestMethod `
    -Uri "http://localhost:7000/api/neo4j/query" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body

Write-Host "✅ Total Nodes: $($response.records[0].total)"
```

### Test 3: Frontend UI
- [ ] Navigate to http://localhost:5173
- [ ] Click "MostarAI Chat" in sidebar
- [ ] Send test message: "What is the Gadaa System?"
- [ ] Verify response appears
- [ ] Click "Query Builder" in sidebar
- [ ] Select preset query
- [ ] Click "Run Cypher Query"
- [ ] Verify JSON results appear

---

## Troubleshooting

### Backend Won't Start
**Error:** `ModuleNotFoundError: No module named 'fastapi'`
**Fix:** 
```powershell
cd backend
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Ollama Connection Failed
**Error:** `Connection refused to localhost:11434`
**Fix:**
```powershell
# Check if Ollama is running
Get-Process ollama

# If not running, start it
ollama serve
```

### Neo4j Connection Failed
**Error:** `ServiceUnavailable: Unable to connect to Neo4j`
**Fix:**
```powershell
# Check Neo4j status
# If using Docker:
docker ps | grep neo4j

# If stopped, start it:
docker start neo4j
```

### Frontend Build Errors
**Error:** `Cannot find module 'react-dropzone'`
**Fix:**
```powershell
cd frontend
npm install react-dropzone @types/react-dropzone
```

### CORS Errors
**Error:** `Access-Control-Allow-Origin header is missing`
**Fix:** Check `backend/grid_main.py` has CORS middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Performance Checks

### Backend Response Time
```powershell
Measure-Command {
    Invoke-RestMethod -Uri "http://localhost:7000/api/chat" `
        -Method Post `
        -ContentType "application/json" `
        -Body '{"prompt":"test"}'
}
```

**Expected:** < 5 seconds for chat response

### Neo4j Query Speed
```powershell
Measure-Command {
    Invoke-RestMethod -Uri "http://localhost:7000/api/neo4j/query" `
        -Method Post `
        -ContentType "application/json" `
        -Body '{"cypher":"MATCH (n) RETURN n LIMIT 10","parameters":{}}'
}
```

**Expected:** < 1 second for simple queries

---

## Security Checklist

- [ ] Neo4j password is not default
- [ ] `.env` files are in `.gitignore`
- [ ] No API keys in source code
- [ ] CORS origins are restricted
- [ ] Backend runs on localhost only (not 0.0.0.0)
- [ ] Ollama is not exposed to public internet

---

## Production Readiness

### Not Ready For Production (Current State)
- ❌ No authentication/authorization
- ❌ No rate limiting
- ❌ No input validation/sanitization
- ❌ No logging/monitoring
- ❌ No error tracking
- ❌ No backup strategy

### To Make Production-Ready
1. Add authentication (JWT tokens)
2. Implement rate limiting
3. Add input validation (Pydantic models)
4. Set up logging (structured logs)
5. Add error tracking (Sentry)
6. Implement backup strategy for Neo4j
7. Use environment-specific configs
8. Add health check endpoints
9. Set up CI/CD pipeline
10. Add monitoring/alerting

---

## Quick Reference

### Ports
- **Frontend:** 5173
- **Backend:** 7000
- **Neo4j HTTP:** 7474
- **Neo4j Bolt:** 7687
- **Ollama:** 11434

### Key Files
- **Backend Entry:** `backend/grid_main.py`
- **Frontend Entry:** `frontend/src/main.tsx`
- **Chat Route:** `backend/server/routes/chat.py`
- **Neo4j Route:** `backend/server/routes/neo4j.py`
- **Query Builder:** `frontend/pages/GraphQueryBuilder.tsx`

### Logs Location
- **Backend:** Console output
- **Frontend:** Browser console (F12)
- **Neo4j:** Check Neo4j Desktop logs
- **Ollama:** Check Ollama logs

---

## Success Criteria

✅ All services start without errors  
✅ Chat endpoint returns valid responses  
✅ Neo4j queries execute successfully  
✅ Frontend loads without console errors  
✅ Navigation between pages works  
✅ Preset queries execute correctly  
✅ Custom Cypher queries work  
✅ Response times are acceptable  

---

**When all checks pass, the Grid is fully operational. 🔥**
