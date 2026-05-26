"""
Embedding client - generates query embeddings
Uses sentence-transformers for stable, efficient inference
"""
from sentence_transformers import SentenceTransformer
from typing import List
import os
import torch

class EmbeddingClient:
    """Client for generating embeddings using BGE-M3"""

    _instance = None
    _model = None

    def __new__(cls):
        """Singleton pattern to avoid loading model multiple times"""
        if cls._instance is None:
            cls._instance = super(EmbeddingClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            model_path = os.getenv("EMBED_MODEL_PATH", "/models/embed")
            print(f"Loading embedding model from {model_path}...")
            device = "cpu"  # API runs on CPU, GPU reserved for LLM
            self._model = SentenceTransformer(model_path, device=device)
            print(f"✓ Embedding model loaded on {device}")

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a query text"""
        embedding = self._model.encode(
            text,
            normalize_embeddings=True,
            show_progress_bar=False
        )
        return embedding.tolist()
