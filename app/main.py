from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Car Price Analysis API",
    description="API for analyzing car prices and providing buy recommendations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Car Price Analysis API",
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "analyze_cars": "/analyze-cars/",
            "compare_cars": "/compare-cars/",
            "ai_suggest": "/ai-suggest/",
            "test": "/test-analysis/"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "openai_key_set": bool(os.getenv("OPENAI_API_KEY")),
        "thordata_key_set": bool(os.getenv("THORDATA_API_KEY"))
    }

# Import and include routes
from app.routes import router
app.include_router(router)