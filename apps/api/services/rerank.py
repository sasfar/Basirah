"""
Reranking service - reorder retrieved results using cross-encoder
"""
from sentence_transformers import CrossEncoder
from typing import List, Dict, Any
import numpy as np

class RerankService:
    """Reranks retrieved passages using BGE-reranker cross-encoder"""

    def __init__(self, model_path: str):
        print(f"Loading reranker model from {model_path}...")
        self.model = CrossEncoder(model_path, device="cpu")
        print("✓ Reranker model loaded")

    def rerank(
        self,
        query: str,
        passages: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank passages using cross-encoder

        Args:
            query: User query
            passages: List of retrieved passages (each with 'text' key)
            top_k: Number of top results to return after reranking

        Returns:
            Reranked and truncated list of passages with updated scores
        """
        if not passages:
            return []

        # Prepare pairs for reranking
        pairs = [[query, p["text"]] for p in passages]

        # Get reranking scores
        raw_scores = self.model.predict(pairs, show_progress_bar=False)

        # Normalize scores to 0-1 range using sigmoid
        scores = 1 / (1 + np.exp(-raw_scores))

        # Attach scores to passages
        for i, passage in enumerate(passages):
            passage["rerank_score"] = float(scores[i])

        # Sort by rerank score and return top_k
        reranked = sorted(passages, key=lambda x: x["rerank_score"], reverse=True)
        return reranked[:top_k]
