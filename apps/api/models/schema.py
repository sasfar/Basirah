"""
Pydantic models for API request/response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class RetrieveRequest(BaseModel):
    """Request model for /retrieve endpoint"""
    question: str = Field(..., min_length=3, description="User question")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of results to retrieve")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional filters (e.g., source_type)")

class Evidence(BaseModel):
    """Single piece of evidence from corpus"""
    reference: str = Field(..., description="Canonical reference (e.g., 'Quran 2:255')")
    text: str = Field(..., description="Text content")
    source_type: str = Field(..., description="Source type: quran, bukhari, or muslim")
    score: float = Field(..., description="Relevance score")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")

class RetrieveResponse(BaseModel):
    """Response model for /retrieve endpoint"""
    question: str
    evidence: List[Evidence]
    retrieved_count: int

class QueryRequest(BaseModel):
    """Request model for /query endpoint (RAG)"""
    question: str = Field(..., min_length=3, description="User question")
    top_k: int = Field(default=10, ge=1, le=50, description="Number of evidence pieces to retrieve")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional filters")
    max_tokens: int = Field(default=500, ge=50, le=2000, description="Max tokens in response")
    temperature: float = Field(default=0.3, ge=0.0, le=1.0, description="LLM temperature")

class QueryResponse(BaseModel):
    """Response model for /query endpoint"""
    question: str
    answer: str
    evidence: List[Evidence]
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    retrieved_count: int

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    services: Dict[str, str]
