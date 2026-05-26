# Basirah - Islamic Knowledge RAG System

**Basirah** (Arabic: بصيرة, meaning "insight" or "clarity of vision") is a Retrieval-Augmented Generation (RAG) system that provides grounded answers from authentic Islamic sources: the Quran, Sahih al-Bukhari, and Sahih Muslim.

## Overview

Basirah uses vector similarity search, cross-encoder reranking, and LLM-based generation to answer questions while maintaining strict citation requirements. Every answer is grounded in retrieved evidence with canonical references.

### Key Features

- **Grounded Generation**: Every factual claim cited to specific verses/hadiths
- **Multi-Source Corpus**: Quran, Sahih al-Bukhari, Sahih Muslim
- **Hybrid Retrieval**: Dense vector search + cross-encoder reranking
- **Citation Enforcement**: LLM instructed to cite every statement
- **Confidence Scoring**: Estimates answer quality based on retrieval and citations
- **ARM64 Optimized**: Runs natively on ARM architecture (DGX, Apple Silicon)

## Architecture

```
┌─────────────┐
│   User      │
│  Question   │
└──────┬──────┘
       │
       v
┌─────────────────────────────────────────────────┐
│              Basirah API (FastAPI)              │
│                                                 │
│  1. Embed Query (BGE-M3)                       │
│  2. Retrieve (Qdrant)                          │
│  3. Rerank (BGE-reranker-v2-m3)               │
│  4. Build Prompt                               │
│  5. Generate (llama.cpp + Qwen2.5-7B)         │
│  6. Calculate Confidence                       │
└─────────────────────────────────────────────────┘
       │
       v
┌──────────────────────────────────────────┐
│  Answer + Citations + Evidence           │
│  [Quran 2:183] [Bukhari 1891]            │
└──────────────────────────────────────────┘
```

### Technology Stack

**Infrastructure:**
- PostgreSQL 16 - Corpus storage
- Qdrant v1.9.2 - Vector database
- Docker Compose - Orchestration
- Nginx - Reverse proxy

**Models:**
- **Embedding**: BAAI/bge-m3 (1024-dim, multilingual)
- **Reranker**: BAAI/bge-reranker-v2-m3 (cross-encoder)
- **LLM**: Qwen2.5-7B-Instruct-Q5_K_M (GGUF, quantized)

**Backend:**
- FastAPI - REST API framework
- llama.cpp - ARM64-native LLM inference
- sentence-transformers - Model serving
- psycopg2 - PostgreSQL driver
- qdrant-client - Vector operations

**Frontend** (planned):
- Next.js 15
- React 19
- TailwindCSS

## Project Structure

```
Basirah/
├── apps/
│   ├── api/                    # FastAPI backend
│   │   ├── main.py            # Application entry point
│   │   ├── routers/           # API endpoints
│   │   │   ├── health.py      # Health check
│   │   │   ├── retrieve.py    # Vector retrieval
│   │   │   └── query.py       # Full RAG pipeline
│   │   ├── services/          # Business logic
│   │   │   ├── retrieval.py   # Qdrant search
│   │   │   ├── rerank.py      # Cross-encoder reranking
│   │   │   ├── embedding_client.py
│   │   │   ├── llm_client.py
│   │   │   ├── prompt_builder.py
│   │   │   └── confidence.py
│   │   ├── models/
│   │   │   └── schema.py      # Pydantic models
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── web/                   # Next.js frontend (TBD)
│
├── services/
│   ├── ingest/                # Corpus ingestion
│   │   ├── ingest_quran.py
│   │   ├── download_hadith.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── embed/                 # Embedding generation
│       ├── embed_worker.py
│       ├── Dockerfile
│       └── requirements.txt
│
├── infra/
│   ├── compose/
│   │   ├── docker-compose.yml
│   │   ├── nginx.conf
│   │   ├── init.sql           # Postgres schema
│   │   └── .env.example
│   └── start_llama.sh         # llama.cpp launcher
│
├── data/                      # External mount (not in repo)
│   ├── corpus/               # Source texts
│   ├── models/               # Model weights
│   ├── postgres/             # Database files
│   ├── qdrant/              # Vector storage
│   └── logs/                # Application logs
│
└── STATUS.md                 # Deployment progress tracker
```

## Quick Start

### Prerequisites

- **Hardware**: ARM64 or x86_64 system with 32GB+ RAM, 1 GPU (24GB+ VRAM recommended)
- **Software**: Docker, Docker Compose, curl, jq
- **Storage**: 50GB+ free space

### 1. Clone & Setup

```bash
git clone https://github.com/sasfar/Basirah.git
cd Basirah

# Create data directories
mkdir -p data/{corpus,models/{embed,rerank,llm-gguf},postgres,qdrant,logs}
```

### 2. Download Models

```bash
# Embedding model (BGE-M3, ~2.3GB)
hf download BAAI/bge-m3 --local-dir data/models/embed

# Reranker model (BGE-reranker-v2-m3, ~1.1GB)
hf download BAAI/bge-reranker-v2-m3 --local-dir data/models/rerank

# LLM model (Qwen2.5-7B-Instruct Q5_K_M, ~5.3GB)
hf download Qwen/Qwen2.5-7B-Instruct-GGUF \
  --include "Qwen2.5-7B-Instruct-Q5_K_M.gguf" \
  --local-dir data/models/llm-gguf
```

### 3. Prepare Corpus

```bash
# Download Quran (Tanzil format)
curl -o data/corpus/quran-simple-clean.txt \
  https://tanzil.net/trans/?transID=en.sahih&type=txt-2

# Download Hadiths (scripted)
cd services/ingest
python download_hadith.py --collection bukhari --output ../../data/corpus/bukhari.json
python download_hadith.py --collection muslim --output ../../data/corpus/muslim.json
cd ../..
```

### 4. Configure Environment

```bash
cd infra/compose
cp .env.example .env

# Edit .env with your settings:
# POSTGRES_PASSWORD=your_secure_password
```

### 5. Start Infrastructure

```bash
# Start core services
docker compose up -d basirah-postgres basirah-qdrant

# Wait for health checks
docker compose ps
```

### 6. Ingest Corpus

```bash
# Ingest Quran
docker compose run --rm basirah-ingest python ingest_quran.py

# Ingest Hadiths (after downloads complete)
# docker compose run --rm basirah-ingest python ingest_bukhari.py
# docker compose run --rm basirah-ingest python ingest_muslim.py
```

### 7. Generate Embeddings

```bash
# Run embedding job (requires GPU, ~10 min for Quran)
docker compose run --rm basirah-embed python embed_worker.py
```

### 8. Start LLM Server

```bash
# Start llama.cpp (runs on host for ARM64 compatibility)
cd infra
./start_llama.sh
```

### 9. Start API

```bash
cd infra/compose
docker compose up -d basirah-api

# Check health
curl http://localhost:8081/health | jq .
```

## API Documentation

### Base URL

```
http://localhost:8081
```

### Endpoints

#### GET /health

Health check for all services.

**Response:**
```json
{
  "status": "ok",
  "services": {
    "qdrant": "ok (6236 vectors)",
    "reranker": "ok"
  }
}
```

#### POST /api/retrieve

Vector similarity search with reranking.

**Request:**
```json
{
  "question": "What is fasting?",
  "top_k": 10,
  "filters": null
}
```

**Response:**
```json
{
  "question": "What is fasting?",
  "evidence": [
    {
      "reference": "Quran 2:183",
      "text": "O you who have believed, decreed upon you is fasting...",
      "source_type": "quran",
      "score": 0.87,
      "metadata": {
        "surah": 2,
        "verse": 183,
        "translation": "Sahih International"
      }
    }
  ],
  "retrieved_count": 10
}
```

#### POST /api/query

Full RAG pipeline with grounded generation.

**Request:**
```json
{
  "question": "What does Allah say about fasting in Ramadan?",
  "top_k": 20,
  "max_tokens": 400,
  "temperature": 0.3
}
```

**Response:**
```json
{
  "question": "What does Allah say about fasting in Ramadan?",
  "answer": "Allah decrees in the Quran that fasting is to be observed during the month of Ramadhan as a means of attaining righteousness. This is stated directly in [Quran 2:183], which says, \"O you who have believed, decreed upon you is fasting as it was decreed upon those before you that you may become righteous.\" Furthermore, [Quran 2:185] provides additional context...",
  "evidence": [...],
  "confidence": 0.721,
  "retrieved_count": 20
}
```

## RAG Pipeline Details

### 1. Query Embedding

User question is embedded using BGE-M3 model (1024-dimensional vector).

```python
query_vector = embedding_client.embed_query("What is fasting?")
# Returns: [0.023, -0.145, 0.891, ...]  # 1024 dimensions
```

### 2. Vector Retrieval

Dense vector search in Qdrant using cosine similarity.

```python
results = qdrant_client.search(
    collection_name="basirah_corpus",
    query_vector=query_vector,
    limit=top_k
)
```

### 3. Cross-Encoder Reranking

Rerank retrieved passages using BGE-reranker-v2-m3 for better relevance.

```python
pairs = [[query, passage["text"]] for passage in results]
scores = reranker.predict(pairs)
reranked = sorted(zip(results, scores), key=lambda x: x[1], reverse=True)
```

### 4. Prompt Construction

Build grounded prompt with system instructions and evidence.

```
You are Basirah, a knowledge assistant grounded exclusively in the Quran, 
Sahih al-Bukhari, and Sahih Muslim.

Rules you must always follow:
1. Answer ONLY from the retrieved evidence passages provided below
2. Do NOT use any knowledge from your training data
3. Cite EVERY factual claim using [Reference] format
...

Retrieved Evidence:
[1] Reference: Quran 2:183
O you who have believed, decreed upon you is fasting...

Question: What does Allah say about fasting in Ramadan?

Answer:
```

### 5. LLM Generation

Generate answer using Qwen2.5-7B via llama.cpp OpenAI-compatible API.

```python
response = llm_client.chat.completions.create(
    model="basirah-llm",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=400,
    temperature=0.3
)
```

### 6. Confidence Scoring

Calculate confidence based on:
- **Retrieval Quality (30%)**: Average score of top-5 passages
- **Citation Coverage (50%)**: % of evidence cited in answer
- **Answer Quality (20%)**: Length heuristics + citation presence

```python
confidence = (
    avg_retrieval_score * 0.3 +
    citation_coverage * 0.5 +
    answer_quality * 0.2
)
```

## Corpus Statistics

| Source | Count | Format | Status |
|--------|-------|--------|--------|
| Quran (Sahih International) | 6,236 verses | Tanzil TXT | ✅ Ingested |
| Sahih al-Bukhari | 7,563 hadiths | Sunnah.com JSON | 🔄 Downloading |
| Sahih Muslim | 7,470 hadiths | Sunnah.com JSON | 🔄 Downloading |
| **Total** | **21,269** | | **6,236 embedded** |

## Model Details

### BGE-M3 (Embedding)
- **Size**: 567M parameters
- **Dimensions**: 1024
- **Languages**: 100+ (including Arabic, English)
- **Max Length**: 8192 tokens
- **Purpose**: Query and passage embedding

### BGE-reranker-v2-m3 (Reranking)
- **Size**: 568M parameters
- **Type**: Cross-encoder
- **Languages**: Multilingual
- **Max Length**: 1024 tokens
- **Purpose**: Rerank retrieved passages

### Qwen2.5-7B-Instruct (Generation)
- **Size**: 7B parameters (Q5_K_M quantized to ~5.3GB)
- **Context**: 8192 tokens
- **Format**: GGUF (llama.cpp compatible)
- **Inference**: CPU/GPU via llama.cpp
- **Purpose**: Grounded answer generation

## Configuration

### Environment Variables

```bash
# Postgres
POSTGRES_DB=basirah
POSTGRES_USER=basirah
POSTGRES_PASSWORD=your_secure_password

# Qdrant
QDRANT_URL=http://basirah-qdrant:6333
COLLECTION_NAME=basirah_corpus

# LLM
VLLM_URL=http://host.docker.internal:8000

# Models
EMBED_MODEL_PATH=/models/embed
RERANK_MODEL_PATH=/models/rerank

# Logging
LOG_LEVEL=info
```

### Port Mappings

| Service | Internal | External | Description |
|---------|----------|----------|-------------|
| Postgres | 5432 | 5433 | Database |
| Qdrant HTTP | 6333 | 6335 | Vector search API |
| Qdrant gRPC | 6334 | 6336 | Vector search gRPC |
| llama.cpp | 8000 | 8000 | LLM inference |
| API | 8080 | 8081 | FastAPI backend |
| Nginx | 80 | 80 | Reverse proxy |

### Resource Limits

```yaml
basirah-postgres:
  memory: 8G

basirah-qdrant:
  memory: 16G

basirah-api:
  memory: 8G
```

## Development

### Running Tests

```bash
# API tests
cd apps/api
pytest

# Integration tests
cd tests
pytest test_rag_pipeline.py
```

### Local Development

```bash
# Run API locally (without Docker)
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8080
```

### Adding New Endpoints

1. Create router in `apps/api/routers/`
2. Add business logic to `apps/api/services/`
3. Update `main.py` to include router
4. Document in README

## Deployment

### Production Considerations

1. **Security**:
   - Change default passwords
   - Enable SSL/TLS on Nginx
   - Restrict CORS origins
   - Use secrets management

2. **Scaling**:
   - Use external Postgres (managed)
   - Deploy Qdrant cluster
   - Load balance API containers
   - Cache embeddings

3. **Monitoring**:
   - Add Prometheus metrics
   - Set up log aggregation
   - Monitor GPU/CPU usage
   - Track query latency

4. **Backup**:
   - Postgres dumps (daily)
   - Qdrant snapshots
   - Model checkpoints

## Performance

### Benchmarks (Quran-only, 6,236 vectors)

| Operation | Latency | Notes |
|-----------|---------|-------|
| Embedding (query) | ~50ms | CPU, batch_size=1 |
| Vector search | ~20ms | Qdrant, top_k=20 |
| Reranking | ~300ms | CPU, 20 passages |
| LLM generation | ~2-5s | llama.cpp, 200-400 tokens |
| **Total (end-to-end)** | **~3-6s** | Full RAG pipeline |

### Optimization Opportunities

- [ ] GPU inference for reranker (5x faster)
- [ ] Batch query processing
- [ ] Response caching (Redis)
- [ ] Async embedding generation
- [ ] Quantize reranker to INT8

## Known Issues

1. **Qdrant Health Check**: Container marked "unhealthy" but functional (missing curl in image)
2. **Hadith Downloads**: Sunnah.com API rate-limited (2s delay between requests)
3. **Memory Usage**: Full corpus + models requires 48GB+ RAM

## Roadmap

### Phase 1: Core RAG (Current)
- [x] Quran ingestion
- [x] Vector embedding
- [x] Retrieval API
- [x] Query API with citations
- [ ] Complete Hadith ingestion
- [ ] Re-embed full corpus

### Phase 2: Frontend
- [ ] Next.js web interface
- [ ] Chat-style Q&A
- [ ] Citation highlighting
- [ ] Source browsing

### Phase 3: Advanced Features
- [ ] Multilingual support (Arabic)
- [ ] Query history
- [ ] Bookmark answers
- [ ] Export citations
- [ ] Advanced filters (by source, topic)

### Phase 4: Production
- [ ] Authentication
- [ ] Rate limiting
- [ ] Analytics dashboard
- [ ] Mobile app (React Native)

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Citation

If you use Basirah in your research, please cite:

```bibtex
@software{basirah2026,
  title={Basirah: Islamic Knowledge Retrieval-Augmented Generation System},
  author={Your Name},
  year={2026},
  url={https://github.com/sasfar/Basirah}
}
```

## Acknowledgments

- **Models**: BAAI (Beijing Academy of Artificial Intelligence) for BGE models
- **LLM**: Alibaba Cloud for Qwen2.5
- **Corpus**: Tanzil.net for Quran translation, Sunnah.com for Hadith
- **Inference**: llama.cpp community for ARM64-native LLM serving

## Contact

For questions, issues, or collaboration:

- Email: syed@saasglobal.ca
- GitHub Issues: [github.com/sasfar/Basirah/issues](https://github.com/sasfar/Basirah/issues)

---

**Built with insight (بصيرة) for the Muslim community**
