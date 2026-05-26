"""
Retrieval service - semantic search in Qdrant vector store
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Dict, Any, Optional
import requests

class RetrievalService:
    """Handles semantic search and retrieval from Qdrant"""

    def __init__(self, qdrant_url: str, collection_name: str):
        self.client = QdrantClient(url=qdrant_url)
        self.collection_name = collection_name
        print(f"✓ Retrieval service initialized: {qdrant_url}/{collection_name}")

    def search(
        self,
        query_vector: List[float],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Qdrant

        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return
            filters: Optional filters (e.g., {"source_type": "quran"})

        Returns:
            List of search results with scores
        """
        # Build Qdrant filter
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            if conditions:
                qdrant_filter = Filter(must=conditions)

        # Search
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter
        )

        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "id": result.id,
                "score": result.score,
                "reference": result.payload.get("reference"),
                "text": result.payload.get("text"),
                "source_type": result.payload.get("source_type"),
                "metadata": result.payload.get("metadata")
            })

        return formatted_results

    def get_collection_info(self) -> Dict[str, Any]:
        """Get collection statistics"""
        info = self.client.get_collection(self.collection_name)
        return {
            "name": self.collection_name,
            "vectors_count": info.points_count,
            "status": info.status.value if hasattr(info.status, 'value') else str(info.status)
        }
