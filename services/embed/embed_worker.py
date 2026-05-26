#!/usr/bin/env python3
"""
Embedding worker - processes corpus records and stores vectors in Qdrant.
Run as a one-time batch job to create the vector index.
"""
import os
import argparse
import psycopg2
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from FlagEmbedding import BGEM3FlagModel
import torch

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://basirah:password@basirah-postgres:5432/basirah")
QDRANT_URL = os.getenv("QDRANT_URL", "http://basirah-qdrant:6333")
MODEL_PATH = os.getenv("MODEL_PATH", "/model")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "basirah_corpus")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))

def create_collection(client, collection_name, recreate=False):
    """Create or recreate Qdrant collection"""

    if recreate and client.collection_exists(collection_name):
        print(f"Deleting existing collection: {collection_name}")
        client.delete_collection(collection_name)

    if not client.collection_exists(collection_name):
        print(f"Creating collection: {collection_name}")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=1024,  # BGE-M3 dense vector size
                distance=Distance.COSINE
            )
        )
        print(f"✓ Collection created")
    else:
        print(f"Collection already exists: {collection_name}")

def fetch_corpus_records(conn):
    """Fetch all corpus records from Postgres"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, source_type, reference, text_english, metadata
            FROM corpus
            ORDER BY source_type, reference
        """)
        records = cur.fetchall()

    return [
        {
            "id": str(row[0]),
            "source_type": row[1],
            "reference": row[2],
            "text": row[3],
            "metadata": row[4]
        }
        for row in records
    ]

def embed_and_upload(records, model, qdrant_client, collection_name, batch_size):
    """Embed corpus records and upload to Qdrant in batches"""

    print(f"\nEmbedding {len(records)} records in batches of {batch_size}...")

    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]

        # Prepare texts for embedding
        texts = [r["text"] for r in batch]

        # Generate embeddings (dense vectors only for now)
        print(f"Processing batch {i//batch_size + 1}/{(len(records) + batch_size - 1)//batch_size} ({len(batch)} records)...")
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            max_length=512
        )

        # Use dense embeddings (first output from BGE-M3)
        if isinstance(embeddings, dict):
            dense_vecs = embeddings['dense_vecs']
        else:
            dense_vecs = embeddings

        # Create Qdrant points
        points = []
        for j, record in enumerate(batch):
            vector = dense_vecs[j].tolist() if torch.is_tensor(dense_vecs[j]) else dense_vecs[j]

            point = PointStruct(
                id=record["id"],
                vector=vector,
                payload={
                    "source_type": record["source_type"],
                    "reference": record["reference"],
                    "text": record["text"],
                    "metadata": record["metadata"]
                }
            )
            points.append(point)

        # Upload batch to Qdrant
        qdrant_client.upsert(
            collection_name=collection_name,
            points=points
        )

        print(f"  ✓ Uploaded batch {i//batch_size + 1} ({i + len(batch)}/{len(records)} total)")

    print(f"\n✓ Successfully embedded and uploaded {len(records)} records")

def main():
    parser = argparse.ArgumentParser(description="Embed corpus and upload to Qdrant")
    parser.add_argument("--recreate-collection", action="store_true", help="Delete and recreate collection")
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE, help="Batch size for embedding")
    args = parser.parse_args()

    print("="*60)
    print("Basirah Embedding Worker")
    print("="*60)

    # Connect to databases
    print(f"\nConnecting to Postgres...")
    pg_conn = psycopg2.connect(DATABASE_URL)

    print(f"Connecting to Qdrant at {QDRANT_URL}...")
    qdrant_client = QdrantClient(url=QDRANT_URL)

    # Create collection
    create_collection(qdrant_client, COLLECTION_NAME, recreate=args.recreate_collection)

    # Check if collection already has vectors
    collection_info = qdrant_client.get_collection(COLLECTION_NAME)
    existing_count = collection_info.points_count

    if existing_count > 0 and not args.recreate_collection:
        print(f"\n⚠ Collection already contains {existing_count} vectors")
        print("Use --recreate-collection to rebuild from scratch")
        return

    # Fetch corpus records
    print(f"\nFetching corpus records from Postgres...")
    records = fetch_corpus_records(pg_conn)
    print(f"Found {len(records)} records")

    if len(records) == 0:
        print("ERROR: No corpus records found. Run ingestion first.")
        return

    # Load embedding model
    print(f"\nLoading BGE-M3 model from {MODEL_PATH}...")
    model = BGEM3FlagModel(MODEL_PATH, use_fp16=True)
    print(f"✓ Model loaded")

    # Embed and upload
    embed_and_upload(records, model, qdrant_client, COLLECTION_NAME, args.batch_size)

    # Verify final count
    collection_info = qdrant_client.get_collection(COLLECTION_NAME)
    final_count = collection_info.points_count
    print(f"\n✓ Final collection size: {final_count} vectors")

    pg_conn.close()
    print("\nEmbedding complete!")

if __name__ == "__main__":
    main()
