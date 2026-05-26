"""
Basirah API - Islamic Knowledge RAG System
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from routers import query, retrieve, health
from services.retrieval import RetrievalService
from services.rerank import RerankService

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup"""
    print("Initializing Basirah API services...")

    # Initialize retrieval service
    qdrant_url = os.getenv("QDRANT_URL", "http://basirah-qdrant:6333")
    collection_name = os.getenv("COLLECTION_NAME", "basirah_corpus")
    app.state.retrieval_service = RetrievalService(qdrant_url, collection_name)

    # Initialize reranker service
    rerank_model_path = os.getenv("RERANK_MODEL_PATH", "/models/rerank")
    app.state.rerank_service = RerankService(rerank_model_path)

    print("✓ Services initialized")

    yield

    print("Shutting down services...")

# Create FastAPI app
app = FastAPI(
    title="Basirah API",
    description="Islamic Knowledge Retrieval-Augmented Generation System",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(retrieve.router, prefix="/api", tags=["retrieval"])
app.include_router(query.router, prefix="/api", tags=["query"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Basirah API",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "retrieve": "/api/retrieve",
            "query": "/api/query"
        }
    }
