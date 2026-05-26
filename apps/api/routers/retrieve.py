"""
Retrieval endpoint - semantic search without generation
"""
from fastapi import APIRouter, Request, HTTPException
from models.schema import RetrieveRequest, RetrieveResponse, Evidence
from services.embedding_client import EmbeddingClient

router = APIRouter()
embedding_client = EmbeddingClient()

@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve(request: Request, req: RetrieveRequest):
    """
    Retrieve relevant passages from corpus using semantic search

    This endpoint performs retrieval without generation:
    1. Embed the query
    2. Search Qdrant for similar vectors
    3. Rerank results
    4. Return top passages with references
    """
    try:
        # Generate query embedding
        query_vector = embedding_client.embed_query(req.question)

        # Retrieve from Qdrant
        results = request.app.state.retrieval_service.search(
            query_vector=query_vector,
            top_k=req.top_k,
            filters=req.filters
        )

        if not results:
            return RetrieveResponse(
                question=req.question,
                evidence=[],
                retrieved_count=0
            )

        # Rerank results
        reranked = request.app.state.rerank_service.rerank(
            query=req.question,
            passages=results,
            top_k=min(req.top_k, len(results))
        )

        # Format evidence
        evidence = [
            Evidence(
                reference=r["reference"],
                text=r["text"],
                source_type=r["source_type"],
                score=r.get("rerank_score", r.get("score", 0.0)),
                metadata=r.get("metadata")
            )
            for r in reranked
        ]

        return RetrieveResponse(
            question=req.question,
            evidence=evidence,
            retrieved_count=len(evidence)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Retrieval error: {str(e)}")
