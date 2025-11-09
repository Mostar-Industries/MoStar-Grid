# 🧠 MostarAI - Sovereign AI Chat Setup

## 🔥 What You Just Built

**MostarAI** - A locally-hosted AI chatbot that:
- ✅ Runs **100% on your machine** (no Google, no OpenAI, no cloud)
- ✅ Pulls context from your **Neo4j knowledge graph**
- ✅ Answers questions about **African wisdom systems**
- ✅ Uses **Ollama** (local LLM) for inference

## 🛠️ Setup Instructions

### 1. Install Ollama

**Windows:**
```powershell
# Download from: https://ollama.com/download
# Or use winget:
winget install Ollama.Ollama
```

**Mac/Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Pull a Model

```powershell
# Recommended: Mistral (fast, smart, 7B params)
ollama pull mistral

# Or try these:
ollama pull llama3        # Meta's LLaMA 3
ollama pull dolphin-mixtral  # Uncensored Mixtral
ollama pull phi3          # Microsoft's Phi-3 (small, fast)
```

### 3. Start Ollama Server

```powershell
# Ollama runs as a service, but you can manually start it:
ollama serve
```

It will run on `http://localhost:11434`

### 4. Test Ollama

```powershell
# Quick test
ollama run mistral "What is Ubuntu philosophy?"
```

### 5. Start MoStar Grid Backend

```powershell
cd C:\Users\AI\Documents\GitHub\MoStar-Grid
.venv\Scripts\python.exe backend\grid_main.py
```

You should see:
```
✅ MostarAI Chat router mounted (Sovereign AI online)
```

### 6. Start Frontend

```powershell
cd frontend
npm run dev
```

### 7. Open Chat Page

Navigate to: **http://localhost:3000**

Click on **Chat** in the sidebar (or navigate to `/chat`)

## 🎯 Try These Prompts

```
What is the Gadaa System?

Tell me about Ifá divination

What does Oba Kingship connect to?

How is Gacaca related to community justice?

What traditional medicines are used for fever?

Explain the relationship between Orisha and Yoruba culture
```

## 🔍 How It Works

```
User Question
    ↓
Frontend (ChatPage.tsx)
    ↓
Backend (/api/chat)
    ↓
Neo4j Context Fetch (Cypher query)
    ↓
Enriched Prompt = System Context + Neo4j Data + User Question
    ↓
Ollama (Local LLM)
    ↓
Response with African Knowledge
    ↓
Frontend Display
```

## 📡 API Endpoints

### POST `/api/chat`

**Request:**
```json
{
  "prompt": "What is Ubuntu?"
}
```

**Response:**
```json
{
  "response": "Ubuntu is a Nguni Bantu term meaning 'humanity'...",
  "context_used": true,
  "model": "mistral"
}
```

## 🎨 Frontend Features

- **Neo4j Context Indicator** - Shows when graph data is used
- **Loading States** - Spinner while thinking
- **Error Handling** - Clear messages if Ollama is down
- **Keyboard Shortcuts** - Ctrl+Enter to send
- **Beautiful UI** - Gradient buttons, smooth animations

## ⚙️ Configuration

### Change LLM Model

Edit `backend/server/routes/chat.py`:

```python
payload = {
    "model": "llama3",  # Change this
    "prompt": enriched_prompt,
    "stream": False
}
```

### Adjust Temperature

```python
"options": {
    "temperature": 0.7,  # Lower = more focused, Higher = more creative
    "top_p": 0.9
}
```

### Increase Context Limit

Edit the Cypher query in `chat.py`:

```python
LIMIT 10  # Change to 20, 50, etc.
```

## 🔒 Security Notes

- **Local only** - No data leaves your machine
- **No API keys** - No cloud services
- **Private** - Your conversations stay on your hardware
- **Sovereign** - You control the model, data, and infrastructure

## 🐛 Troubleshooting

### "Cannot connect to Ollama"

```powershell
# Check if Ollama is running
curl http://localhost:11434

# If not, start it
ollama serve
```

### "Model not found"

```powershell
# Pull the model
ollama pull mistral
```

### "Neo4j context empty"

- Check Neo4j is connected: `http://localhost:7000/api/neo4j/status`
- Verify data exists: `http://localhost:7000/api/neo4j/stats`

### Frontend shows error

- Check backend is running on port 7000
- Check browser console (F12) for errors
- Verify CORS is not blocking requests

## 📊 Performance

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| **mistral** | 7B | Fast | Excellent |
| **llama3** | 8B | Fast | Excellent |
| **dolphin-mixtral** | 47B | Slow | Best |
| **phi3** | 3.8B | Very Fast | Good |

## 🚀 Next Steps

1. **Add Streaming** - Real-time token-by-token responses
2. **Conversation History** - Remember previous messages
3. **Voice Input** - Speak your questions
4. **Export Conversations** - Save chat history
5. **Multi-Model** - Switch between models in UI
6. **RAG Enhancement** - Better context retrieval from Neo4j

## 🌍 What Makes This Special

**Traditional AI Chatbots:**
- ❌ Cloud-dependent (Google, OpenAI)
- ❌ Generic knowledge
- ❌ No cultural context
- ❌ Data leaves your control

**MostarAI:**
- ✅ 100% local
- ✅ African knowledge systems
- ✅ Neo4j-powered context
- ✅ Your data, your hardware, your sovereignty

## 📚 Resources

- **Ollama:** https://ollama.com
- **Neo4j:** https://neo4j.com
- **FastAPI:** https://fastapi.tiangolo.com
- **React:** https://react.dev

---

**Welcome to Sovereign AI. Mostar speaks. 🌿👑**
