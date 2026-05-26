#!/usr/bin/env python3
"""
Embedding server - provides HTTP API for generating embeddings.
Used during inference for query embedding.
"""
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from FlagEmbedding import BGEM3FlagModel
import torch

MODEL_PATH = os.getenv("MODEL_PATH", "/model")

app = FastAPI(title="Basirah Embedding Service")

# Load model at startup
print(f"Loading BGE-M3 model from {MODEL_PATH}...")
model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
print("Model loaded successfully")

class EmbedRequest(BaseModel):
    text: str
    max_length: int = 512

class EmbedResponse(BaseModel):
    vector: list[float]
    dimension: int

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/embed", response_model=EmbedResponse)
async def embed(request: EmbedRequest):
    """Generate embedding for input text"""
    try:
        # Generate embedding
        embeddings = model.encode(
            [request.text],
            batch_size=1,
            max_length=request.max_length
        )

        # Extract dense vector
        if isinstance(embeddings, dict):
            dense_vec = embeddings['dense_vecs'][0]
        else:
            dense_vec = embeddings[0]

        # Convert to list
        vector = dense_vec.tolist() if torch.is_tensor(dense_vec) else dense_vec

        return EmbedResponse(
            vector=vector,
            dimension=len(vector)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
