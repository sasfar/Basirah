"""
Health check endpoints
"""
from fastapi import APIRouter, Request
from models.schema import HealthResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check(request: Request):
    """Check health of all services"""

    services = {}

    # Check Qdrant
    try:
        info = request.app.state.retrieval_service.get_collection_info()
        services["qdrant"] = f"ok ({info['vectors_count']} vectors)"
    except Exception as e:
        services["qdrant"] = f"error: {str(e)}"

    # Check reranker
    try:
        if request.app.state.rerank_service:
            services["reranker"] = "ok"
        else:
            services["reranker"] = "not initialized"
    except Exception as e:
        services["reranker"] = f"error: {str(e)}"

    # Overall status
    status = "ok" if all("ok" in v for v in services.values()) else "degraded"

    return HealthResponse(status=status, services=services)
