"""
Query endpoint - full RAG pipeline with grounded generation
"""
from fastapi import APIRouter, Request, HTTPException
from models.schema import QueryRequest, QueryResponse, Evidence
from services.embedding_client import EmbeddingClient
from services.llm_client import LLMClient
from services.prompt_builder import build_prompt
from services.confidence import calculate_confidence

router = APIRouter()
embedding_client = EmbeddingClient()
llm_client = LLMClient()

@router.post("/query", response_model=QueryResponse)
async def query(request: Request, req: QueryRequest):
    """
    Full RAG pipeline: Retrieve → Rerank → Generate → Score

    This endpoint performs the complete Basirah workflow:
    1. Embed the query
    2. Retrieve relevant passages from Qdrant
    3. Rerank using cross-encoder
    4. Build grounded prompt with evidence
    5. Generate answer from LLM
    6. Calculate confidence score
    7. Return answer with citations and evidence
    """
    try:
        # Step 1: Generate query embedding
        query_vector = embedding_client.embed_query(req.question)

        # Step 2: Retrieve from Qdrant
        results = request.app.state.retrieval_service.search(
            query_vector=query_vector,
            top_k=req.top_k,
            filters=req.filters
        )

        if not results:
            return QueryResponse(
                question=req.question,
                answer="I could not find any relevant information in the available sources to answer your question.",
                evidence=[],
                confidence=0.0,
                retrieved_count=0
            )

        # Step 3: Rerank results
        reranked = request.app.state.rerank_service.rerank(
            query=req.question,
            passages=results,
            top_k=min(10, len(results))  # Use top 10 for generation
        )

        # Step 4: Build prompt
        prompt = build_prompt(req.question, reranked)

        # Step 5: Generate answer
        answer = llm_client.generate(
            prompt=prompt,
            max_tokens=req.max_tokens,
            temperature=req.temperature
        )

        # Step 6: Calculate confidence
        retrieval_scores = [r.get("rerank_score", r.get("score", 0.0)) for r in reranked]
        confidence = calculate_confidence(answer, reranked, retrieval_scores)

        # Step 7: Format evidence
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

        return QueryResponse(
            question=req.question,
            answer=answer,
            evidence=evidence,
            confidence=confidence,
            retrieved_count=len(results)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")
