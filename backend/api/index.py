"""
Vercel serverless function handler for FastAPI
"""
from fastapi import FastAPI
from mangum import Mangum
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

# Import the FastAPI app from grid_main
from grid_main import app

# Create Mangum handler for Vercel
handler = Mangum(app, lifespan="off")
