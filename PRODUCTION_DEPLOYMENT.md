# 🚀 Production Deployment Guide

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    PRODUCTION STACK                         │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Vercel)                                          │
│  └─ https://mo-star-grid.vercel.app                         │
│                                                             │
│  Backend API (Railway/Render/Fly/VM)                        │
│  └─ https://api.mostar-grid.xyz                             │
│     ├─ REST: /api/health, /api/notes, etc.                 │
│     └─ WebSocket: /ws/live-stream                           │
│                                                             │
│  Database (Neon)                                            │
│  └─ PostgreSQL with SSL                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 Pre-Deployment Checklist

### ✅ Local Development Working

- [ ] FastAPI runs on `http://127.0.0.1:8000`
- [ ] Frontend runs on `http://localhost:5173`
- [ ] `/api/health` returns `{"ok": true}`
- [ ] `/api/notes` CRUD operations work
- [ ] WebSocket `/ws/live-stream` streams telemetry
- [ ] Vite proxy routes `/api` and `/ws` correctly

### ✅ Environment Variables Ready

- [ ] `DATABASE_URL` - Neon PostgreSQL connection string
- [ ] `VITE_API_KEY` - Gemini API key (for client features)
- [ ] `ALLOW_ORIGINS` - Vercel domains (for CORS)

---

## 🌐 Backend Deployment

### Option 1: Railway (Recommended)

1. **Install Railway CLI**

   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create New Project**

   ```bash
   railway init
   railway link
   ```

3. **Set Environment Variables**

   ```bash
   railway variables set DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
   railway variables set ALLOW_ORIGINS="https://mo-star-grid.vercel.app,https://*.vercel.app"
   railway variables set ALLOW_NO_DB="false"
   railway variables set API_HOST="0.0.0.0"
   railway variables set API_PORT="8000"
   ```

4. **Create Procfile** (in repo root)

   ```
   web: cd backend && python grid_main.py
   ```

5. **Deploy**

   ```bash
   railway up
   ```

6. **Get Public URL**

   ```bash
   railway domain
   # Note the URL, e.g., https://mostar-grid-production.up.railway.app
   ```

### Option 2: Render

1. Create new **Web Service** at <https://render.com>
2. Connect GitHub repository
3. Set **Build Command**: `cd backend && pip install -r requirements.txt`
4. Set **Start Command**: `cd backend && python grid_main.py`
5. Add Environment Variables (same as Railway)
6. Deploy

### Option 3: Fly.io

1. **Install Fly CLI**

   ```bash
   curl -L https://fly.io/install.sh | sh
   fly auth login
   ```

2. **Create fly.toml** (in repo root)

   ```toml
   app = "mostar-grid"
   
   [build]
     dockerfile = "Dockerfile"
   
   [env]
     API_HOST = "0.0.0.0"
     API_PORT = "8000"
   
   [[services]]
     internal_port = 8000
     protocol = "tcp"
   
     [[services.ports]]
       port = 80
       handlers = ["http"]
   
     [[services.ports]]
       port = 443
       handlers = ["tls", "http"]
   ```

3. **Create Dockerfile** (in repo root)

   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY backend/requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   COPY backend/ .
   CMD ["python", "grid_main.py"]
   ```

4. **Deploy**

   ```bash
   fly launch
   fly secrets set DATABASE_URL="..." ALLOW_ORIGINS="..."
   fly deploy
   ```

---

## 🎨 Frontend Deployment (Vercel)

### 1. Set Environment Variables in Vercel

Go to: <https://vercel.com/mo-101s-projects/mo-star-grid/settings/environment-variables>

Add the following for **Production**:

```bash
# Backend API URL (replace with your actual backend URL)
VITE_API_URL=https://mostar-grid-production.up.railway.app/api

# WebSocket URL (same host, ws protocol)
VITE_WS_URL=wss://mostar-grid-production.up.railway.app/ws

# Gemini API Key (for client-side features)
VITE_API_KEY=<your-gemini-api-key>
```

### 2. Redeploy Frontend

```bash
# Option A: Via Vercel CLI
vercel --prod

# Option B: Via Git Push
git push origin main  # Auto-deploys if connected
```

### 3. Verify Deployment

```bash
# Check environment variables are loaded
open https://mo-star-grid.vercel.app
# Open DevTools Console, should see:
# [env] API_BASE: https://mostar-grid-production.up.railway.app/api
# [env] WS_BASE: wss://mostar-grid-production.up.railway.app/ws
```

---

## 🧪 Production Smoke Tests

### REST API Endpoints

```bash
# Health check
curl -fsS https://mostar-grid-production.up.railway.app/api/health

# Expected:
# {"status": "OK", "db": {...}, "consciousness": {...}}

# Notes CRUD
curl -fsS https://mostar-grid-production.up.railway.app/api/notes

# Create note
curl -X POST https://mostar-grid-production.up.railway.app/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","body":"Production test"}'
```

### WebSocket Telemetry

```bash
# Using websocat (install: cargo install websocat)
websocat wss://mostar-grid-production.up.railway.app/ws/live-stream

# Expected output (streaming):
# {"ts":1699223456.789,"gridLatencyMs":123,"cpu":45.2,"mem":62.1,"service":"gateway","event":"telemetry.tick"}
```

### Frontend Integration

1. Open <https://mo-star-grid.vercel.app>
2. Open DevTools → Network → WS tab
3. Should see active WebSocket connection to `wss://mostar-grid-production.up.railway.app/ws/live-stream`
4. Should see frames streaming every 1 second
5. Navigate to Notes page - should fetch from production API
6. Create a note - should persist to Neon database

---

## 🔒 Security Checklist

### Backend

- [ ] `ALLOW_ORIGINS` set to Vercel domains only (no `*`)
- [ ] `DATABASE_URL` uses `sslmode=require`
- [ ] No sensitive keys in git history
- [ ] HTTPS enforced (Railway/Render/Fly do this automatically)

### Frontend

- [ ] `VITE_API_KEY` only used for client-side features (not DB access)
- [ ] Database credentials NEVER in frontend env vars
- [ ] All API calls go through backend (no direct DB access)

---

## 🐛 Troubleshooting

### Frontend can't connect to backend

**Symptom**: CORS errors in browser console

**Fix**: Check backend `ALLOW_ORIGINS` includes Vercel domain:

```bash
railway variables set ALLOW_ORIGINS="https://mo-star-grid.vercel.app,https://mo-star-grid-git-main-mo-101s-projects.vercel.app"
```

### WebSocket connection fails

**Symptom**: `useGridStream` status stays 'offline'

**Fix**:

1. Verify `VITE_WS_URL` uses `wss://` (not `ws://`)
2. Check backend WebSocket endpoint:

   ```bash
   websocat wss://your-backend.railway.app/ws/live-stream
   ```

3. Ensure backend supports WebSocket upgrades (FastAPI does by default)

### Database connection fails

**Symptom**: Backend logs show "Database connection failed"

**Fix**:

1. Verify `DATABASE_URL` format:

   ```
   postgresql://user:password@host:5432/dbname?sslmode=require
   ```

2. Check Neon connection string is correct
3. Ensure backend can reach Neon (most cloud providers allow this)

### Notes page shows empty/errors

**Symptom**: `/api/notes` returns 500 or empty array

**Fix**:

1. Check backend logs for SQL errors
2. Verify `notes` table exists in Neon:

   ```sql
   CREATE TABLE IF NOT EXISTS notes (
       id SERIAL PRIMARY KEY,
       title TEXT NOT NULL,
       body TEXT,
       created_at TIMESTAMPTZ DEFAULT NOW()
   );
   ```

3. Run `backend/scripts/init_db.py` if needed

---

## 📊 Monitoring

### Health Checks

Set up monitoring pings to:

- `https://your-backend.railway.app/api/health` (every 5 minutes)
- Expected: `{"status": "OK"}`

### Logs

**Railway**: `railway logs`  
**Render**: Dashboard → Logs tab  
**Fly**: `fly logs`

### Metrics

Watch for:

- Response times (should be < 500ms for most endpoints)
- WebSocket connection count
- Database connection pool usage
- Error rates

---

## 🚀 Deployment Checklist

Before going live:

- [ ] Backend deployed and accessible via HTTPS
- [ ] `/api/health` returns 200 OK
- [ ] WebSocket `/ws/live-stream` streams data
- [ ] Database connected (check `/db/status`)
- [ ] CORS configured for Vercel domains
- [ ] Frontend env vars set in Vercel
- [ ] Frontend deployed and loading
- [ ] Notes CRUD works end-to-end
- [ ] WebSocket telemetry visible in frontend
- [ ] No CORS errors in browser console
- [ ] No mock data warnings in production

---

## 🎉 Post-Deployment

Once deployed:

1. **Test thoroughly** - Create notes, watch telemetry, check logs
2. **Monitor for 24h** - Watch for errors or connection issues
3. **Set up alerts** - UptimeRobot or similar for health checks
4. **Document the URLs** - Update README with production links
5. **Celebrate!** 🎊 The Grid is live!

---

**Last Updated**: 2025-11-05  
**Next Review**: After first production deployment
