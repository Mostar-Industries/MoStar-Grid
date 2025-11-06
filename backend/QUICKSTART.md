# MoStar GRID - Quick Start Guide

## 🚀 Start the Complete Application

### Option 1: One Command (Recommended)
```powershell
.\start_all.ps1
```
This starts both backend and frontend in separate windows.

### Option 2: Manual Start (Two Terminals)

**Terminal 1 - Backend API**
```powershell
cd backend
python grid_main.py
```

**Terminal 2 - Frontend**
```powershell
cd web
npm install  # First time only
npm run dev
```

## 📍 Access Points

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:7000
- **API Docs**: http://localhost:7000/docs
- **Health Check**: http://localhost:7000/health

## 📂 Project Structure

```
MoStar-Grid/
├── backend/          # Python FastAPI server
│   ├── grid_main.py  # Main entry point
│   ├── server/       # API endpoints
│   └── pantheon/     # Core logic
├── web/              # React frontend
│   ├── src/          # Frontend source
│   └── vite.config.ts
├── docs/             # Doctrine markdown
└── tools/            # Scripts & utilities
```

## 🔧 First Time Setup

1. **Install Python dependencies**
```powershell
cd backend
pip install fastapi uvicorn asyncpg httpx pydantic
```

2. **Install Node dependencies**
```powershell
cd web
npm install
```

3. **Start the app**
```powershell
cd ..
.\start_all.ps1
```

## 📝 Notes

- Backend requires Python 3.8+
- Frontend requires Node.js 16+
- No Docker required
- CORS handled by Vite proxy in development
