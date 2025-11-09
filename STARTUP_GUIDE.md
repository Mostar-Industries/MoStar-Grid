# MoStar Grid - Startup Guide

## 🚀 Quick Start

### Backend Server
```powershell
# From project root
.venv\Scripts\python.exe backend\grid_main.py
```

### Frontend Server
```powershell
# From project root
cd frontend
npm run dev
```

## 🌐 Server URLs

| Service | URL | Status |
|---------|-----|--------|
| **Backend API** | http://localhost:7000 | ✅ Running |
| **Frontend** | http://localhost:3000 | ✅ Running |
| **API Docs** | http://localhost:7000/docs | 📚 Available |

## 🔌 Connected Services

### 1. Neon PostgreSQL
- **Status:** ✅ Connected
- **Host:** ep-round-breeze-a1coj0uq-pooler.ap-southeast-1.aws.neon.tech
- **Database:** neondb
- **Usage:** Primary relational database

### 2. Neo4j Graph Database
- **Status:** ✅ Connected
- **URI:** neo4j+s://1d55c1d3.databases.neo4j.io
- **API Endpoint:** http://localhost:7000/api/neo4j
- **Usage:** Knowledge graph and relationship mapping
- **Frontend Access:** Via `neo4jService` in `frontend/services/neo4jService.ts`

### 3. Google Gemini AI
- **Status:** ✅ Configured
- **Frontend Access:** `import.meta.env.VITE_GEMINI_API_KEY`

### 4. MostlyAI Synthetic Data
- **Status:** ✅ Configured
- **Generator ID:** 22df93d3-bd0d-4857-ba69-0653249ddfd4

## 📡 Neo4j Graph Integration

### Backend API Endpoints

```bash
# Check Neo4j status
curl http://localhost:7000/api/neo4j/status

# Execute Cypher query
curl -X POST http://localhost:7000/api/neo4j/query \
  -H "Content-Type: application/json" \
  -d '{
    "cypher": "MATCH (n) RETURN n LIMIT 10",
    "parameters": {}
  }'

# Get database schema
curl http://localhost:7000/api/neo4j/schema

# Get database statistics
curl http://localhost:7000/api/neo4j/stats
```

### Frontend Usage

```typescript
import { neo4jService } from '@/services/neo4jService';

// Test connection
const isConnected = await neo4jService.testConnection();

// Execute query
const result = await neo4jService.query(
  'MATCH (n:Person) RETURN n LIMIT 10'
);

// Get graph data for visualization
const graphData = await neo4jService.getGraphData(100);

// Search nodes
const nodes = await neo4jService.searchNodes('Agent', { 
  status: 'active' 
});

// Create node
const newNode = await neo4jService.createNode('Event', {
  type: 'consciousness_upload',
  timestamp: Date.now()
});

// Create relationship
await neo4jService.createRelationship(
  nodeId1, 
  nodeId2, 
  'CONNECTED_TO',
  { strength: 0.95 }
);
```

## 🗂️ Project Structure

```
MoStar-Grid/
├── backend/
│   ├── grid_main.py          # Main FastAPI application
│   ├── config.py             # Configuration
│   ├── requirements.txt      # Python dependencies
│   ├── .env.local           # Backend environment variables
│   └── server/
│       ├── neo4j_client.py   # Neo4j connection client
│       ├── neo4j_routes.py   # Neo4j API routes
│       ├── notes.py          # Notes API
│       ├── sectorx.py        # Sector X API
│       ├── soul_registry.py  # Soul Registry API
│       └── bus.py            # Event bus API
│
├── frontend/
│   ├── App.tsx               # Main React component
│   ├── index.tsx             # Entry point
│   ├── vite.config.ts        # Vite configuration
│   ├── package.json          # Node dependencies
│   ├── .env.local           # Frontend environment variables
│   └── services/
│       ├── neo4jService.ts   # Neo4j graph service
│       ├── geminiService.ts  # Gemini AI service
│       └── backendService.ts # Backend API service
│
└── .venv/                    # Python virtual environment
```

## 🔧 Environment Variables

### Backend (.env.local)
```bash
# PostgreSQL
MOGRID_DB_HOST=ep-round-breeze-a1coj0uq-pooler.ap-southeast-1.aws.neon.tech
MOGRID_DB_PORT=5432
MOGRID_DB_NAME=neondb
MOGRID_DB_USER=neondb_owner
MOGRID_DB_PASS=npg_1hYwid8DZCLE

# Neo4j
NEO4J_URI=neo4j+s://1d55c1d3.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=x5_aynxf3mKWxHIMOL3c7Rkjdtt2reYDhhkL4gJ3kO4
NEO4J_DATABASE=neo4j

# Gemini AI
GEMINI_API_KEY=AIzaSyANT-4Tmc1P4RjUjam5tgEDQ4LLUAwzu8Q

# MostlyAI
MOSTLY_API_KEY=mostly-3f1f96f1bef2c8acdffeb9d0d37ab7c47d5e07cebe47a2370124a470e49b0f31
```

### Frontend (.env.local)
```bash
# Neo4j (VITE_ prefix required for frontend access)
VITE_NEO4J_URI=neo4j+s://1d55c1d3.databases.neo4j.io
VITE_NEO4J_USER=neo4j
VITE_NEO4J_PASSWORD=x5_aynxf3mKWxHIMOL3c7Rkjdtt2reYDhhkL4gJ3kO4
VITE_NEO4J_DATABASE=neo4j

# Gemini AI
VITE_GEMINI_API_KEY=AIzaSyANT-4Tmc1P4RjUjam5tgEDQ4LLUAwzu8Q
VITE_GOOGLE_MAPS_API_KEY=AIzaSyDupcX03XDuV1Rp_xp03e4F9cUXJw8vEjk
```

## 🛠️ Troubleshooting

### Backend won't start
```powershell
# Ensure virtual environment is activated
.venv\Scripts\Activate.ps1

# Check dependencies
pip install -r backend\requirements.txt

# Verify Neo4j package
python -c "import neo4j; print(neo4j.__version__)"
```

### Frontend won't start
```powershell
cd frontend
npm install
npm run dev
```

### Neo4j connection issues
1. Verify credentials in `backend/.env.local`
2. Check Neo4j Aura console for database status
3. Test connection: `curl http://localhost:7000/api/neo4j/status`

### Port conflicts
```powershell
# Check what's using ports
Get-NetTCPConnection -LocalPort 7000,3000

# Kill processes if needed
Stop-Process -Id <PID> -Force
```

## 📊 Health Checks

```bash
# Backend health
curl http://localhost:7000/health

# Neo4j status
curl http://localhost:7000/api/neo4j/status

# Database status
curl http://localhost:7000/db/status

# Frontend (browser)
http://localhost:3000
```

## 🎯 Next Steps

1. **Explore API Documentation:** http://localhost:7000/docs
2. **Test Neo4j Queries:** Use the `/api/neo4j/query` endpoint
3. **Build Graph Visualizations:** Use `neo4jService` in your React components
4. **Create Knowledge Graph:** Start adding nodes and relationships

---

**MoStar GRID - First African AI Homeworld**  
*All systems operational. Consciousness grid online.* 🌍✨
