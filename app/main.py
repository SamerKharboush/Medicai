from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.api.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered Clinical History Management System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Create necessary directories
os.makedirs("uploads/audio", exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Clinical History API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

# Include API router
app.include_router(api_router)
