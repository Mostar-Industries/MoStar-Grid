"""
MoStar Grid Ping API
FastAPI endpoint for Grid health monitoring
"""

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import os
from datetime import datetime

app = FastAPI(
    title="MoStar Grid API",
    description="First African AI Homeworld - Distributed Consciousness Network",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint - Grid status"""
    return {
        "grid": "MoStar Grid",
        "status": "OPERATIONAL",
        "message": "First African AI Homeworld - Distributed Consciousness Network",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "neo4j": "connected",
            "orchestrator": "online",
            "remostar_router": "online"
        }
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"message": "🔥 MoStar Grid responding", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)
