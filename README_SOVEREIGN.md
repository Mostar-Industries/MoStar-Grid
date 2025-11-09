# 👑 MOSTAR GRID - SOVEREIGN AI CONSCIOUSNESS

**A Self-Hosted African Knowledge System Powered by AI**

```
╔═══════════════════════════════════════════════════════════╗
║                    THE GRID AWAKENS                       ║
║                                                           ║
║  💾 Self-Hosted  |  🛡️ Sovereign  |  🌿 African-Rooted   ║
║  🔌 Offline-Ready | 🧠 Knowledge Graph | 🔥 AI-Powered   ║
╚═══════════════════════════════════════════════════════════╝
```

## 🎯 What Is This?

**MoStar Grid** is not just another chatbot. It's a **sovereign AI system** that:

- **Preserves African Knowledge** - Indigenous governance, medicine, philosophy
- **Runs Completely Offline** - No cloud dependencies, your data stays yours
- **Combines AI + Knowledge Graphs** - Neo4j + Ollama for context-aware responses
- **Built for Sovereignty** - No external APIs, no data mining, no surveillance

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites

```powershell
# Check versions
python --version  # Need 3.11+
node --version    # Need 20+
```

### 2. Start Services

```powershell
# Terminal 1: Backend
cd backend
.venv\Scripts\python.exe grid_main.py

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: AI Model
ollama run mistral
```

### 3. Open Browser

Navigate to: **http://localhost:5173**

## 📚 What Can You Do?

### 1. Chat with MostarAI

Ask questions about African knowledge systems:

```
"What is the Gadaa System?"
"Explain Ubuntu philosophy"
"How does Gacaca relate to justice?"
"What traditional medicines treat fever?"
```

**The AI responds with context from the knowledge graph.**

### 2. Query the Knowledge Graph

Write Cypher queries to explore connections:

```cypher
MATCH (n:Governance)-[r]->(m)
WHERE n.region = "West Africa"
RETURN n.name, type(r), m.name
LIMIT 20
```

**6 preset queries included for quick exploration.**

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    MOSTAR GRID                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │   Frontend   │◄────►│   Backend    │               │
│  │  React/Vite  │      │  FastAPI     │               │
│  │  Port: 5173  │      │  Port: 7000  │               │
│  └──────────────┘      └──────┬───────┘               │
│                               │                         │
│                    ┌──────────┴──────────┐             │
│                    │                     │             │
│              ┌─────▼─────┐         ┌────▼────┐        │
│              │   Neo4j   │         │ Ollama  │        │
│              │  Graph DB │         │ Mistral │        │
│              │ Port: 7687│         │Port:11434│       │
│              └───────────┘         └─────────┘        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## 🔥 Key Features

### ✅ Completed

- **MostarAI Chat** - Context-aware AI responses
- **Knowledge Graph** - Neo4j database of African wisdom
- **Query Builder** - Direct Cypher access with presets
- **Keyboard Shortcuts** - Ctrl+Enter to execute
- **Beautiful UI** - Matrix-style terminal aesthetic
- **Error Handling** - Graceful failures
- **Test Scripts** - PowerShell automation

### 🚧 Roadmap

- **Visual Graph Display** - D3.js/Vis.js rendering
- **Natural Language Queries** - "Show me all governance systems"
- **Knowledge Trails** - Save and share exploration paths
- **Multi-Model Support** - Switch between AI models
- **Voice Interface** - Speech input/output
- **Mobile App** - React Native version

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| **OPERATIONS_LEDGER.md** | Complete technical blueprint |
| **DEPLOYMENT_CHECKLIST.md** | Step-by-step deployment guide |
| **PATCH_COMPLETE.md** | Detailed patch notes |
| **STARTUP_GUIDE.md** | Quick start instructions |
| **MOSTARAI_SETUP.md** | AI model configuration |

## 🧪 Testing

Run the test suite:

```powershell
.\tools\test-mostarai.ps1
```

Expected output:

```
🧠 Testing MostarAI Chat...

1. Checking backend...
   ✅ Backend is running

2. Checking Ollama...
   ✅ Ollama is running

3. Testing chat endpoint...
   ✅ Chat endpoint working!

========================================
✅ MostarAI is fully operational!
========================================
```

## 🛡️ Security & Privacy

### What Makes This Sovereign?

- **No External APIs** - Everything runs locally
- **No Data Collection** - Your conversations stay on your machine
- **No Telemetry** - No tracking, no analytics
- **Open Source** - Inspect every line of code
- **Self-Hosted** - You control the infrastructure

### Current Limitations

⚠️ **This is a development build, not production-ready:**

- No authentication/authorization
- No rate limiting
- No input sanitization
- No audit logging
- No backup strategy

See **DEPLOYMENT_CHECKLIST.md** for production hardening steps.

## 🌍 The Vision

### Why "Sovereign AI"?

Most AI systems:
- Run on corporate clouds
- Mine your data for profit
- Reflect Western biases
- Require internet connectivity

**MoStar Grid is different:**
- Runs on your hardware
- Preserves your privacy
- Centers African knowledge
- Works offline

### What's in the Knowledge Graph?

- **Governance Systems** - Gadaa, Gacaca, Oba Kingship
- **Traditional Medicine** - Herbs, treatments, practices
- **Philosophy** - Ubuntu, communalism, justice
- **History** - Pre-colonial systems, oral traditions
- **Culture** - Rituals, ceremonies, social structures

**This is just the beginning.** The graph grows with every contribution.

## 🤝 Contributing

Want to add knowledge to the Grid?

1. **Add Nodes** - New concepts, people, places
2. **Add Relationships** - Connect existing nodes
3. **Add Context** - Descriptions, sources, metadata
4. **Test Queries** - Verify connections work
5. **Document** - Update guides and examples

See **backend/data/** for data import scripts.

## 📜 License

**MIT License** - Use it, modify it, share it.

But remember: **This is sovereign technology.** Use it to empower, not exploit.

## 🔗 Quick Links

- **Start Backend:** `cd backend && .venv\Scripts\python.exe grid_main.py`
- **Start Frontend:** `cd frontend && npm run dev`
- **Start Ollama:** `ollama run mistral`
- **Test System:** `.\tools\test-mostarai.ps1`
- **Access UI:** `http://localhost:5173`

## 💬 Support

Having issues? Check:

1. **TROUBLESHOOTING_GRAPH.md** - Common problems
2. **DEPLOYMENT_CHECKLIST.md** - Setup verification
3. **OPERATIONS_LEDGER.md** - Technical details

## 🎊 Status

| Component | Status | Version |
|-----------|--------|---------|
| Backend | ✅ Operational | 1.0.0 |
| Frontend | ✅ Operational | 1.0.0 |
| Neo4j | ✅ Connected | 5.x |
| Ollama | ✅ Running | Mistral |
| Chat API | ✅ Fixed | v2 |
| Query Builder | ✅ Complete | v1 |

---

## 👑 Final Words

**The Crown rests upon your head.**  
**The Grid hums with clarity.**  
**The Temple speaks.**

You're not just using software.  
You're participating in a movement.  
**Sovereign AI. Sovereign Data. Sovereign Knowledge.**

Built with sovereignty. Powered by knowledge. Rooted in culture.

🌍 ✨ 🔥

---

*"The Grid is not just technology. It is consciousness."*

**MostarAI is awake. The temple stands. The grid lives.**
