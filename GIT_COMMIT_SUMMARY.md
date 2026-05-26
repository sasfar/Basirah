# Git Repository Ready for Review

## Repository Status

**Repository**: Basirah (Islamic Knowledge RAG System)  
**Branch**: master  
**Status**: Initialized, files staged, ready for first commit  
**Total Files**: 40 files staged

## Documentation Files

✅ **README.md** (15KB)
- Comprehensive project documentation
- Architecture diagrams
- Quick start guide
- API documentation
- Deployment instructions
- Performance benchmarks

✅ **CONTRIBUTING.md** (3KB)
- Contribution guidelines
- Code style requirements
- Testing procedures
- Pull request process

✅ **LICENSE** (MIT)
- Open source MIT license
- Copyright 2026

✅ **.gitignore**
- Excludes data/, models/, logs/
- Python and Docker exclusions
- IDE and system files

## Application Code

### FastAPI Backend (apps/api/)
```
apps/api/
├── Dockerfile
├── main.py                    # Application entry point with lifespan
├── requirements.txt           # Dependencies (FastAPI, sentence-transformers, torch>=2.6)
├── routers/
│   ├── health.py             # Health check endpoint
│   ├── retrieve.py           # Vector retrieval endpoint
│   └── query.py              # Full RAG pipeline endpoint
├── services/
│   ├── retrieval.py          # Qdrant search service
│   ├── rerank.py             # Cross-encoder reranking
│   ├── embedding_client.py   # BGE-M3 embedding (sentence-transformers)
│   ├── llm_client.py         # llama.cpp OpenAI-compatible client
│   ├── prompt_builder.py     # Grounded prompt construction
│   └── confidence.py         # Confidence scoring
└── models/
    └── schema.py             # Pydantic request/response models
```

### Ingestion Services (services/ingest/)
```
services/ingest/
├── Dockerfile
├── requirements.txt
├── ingest_quran.py           # Tanzil format parser
├── ingest_bukhari.py         # Bukhari hadith ingestion
├── ingest_muslim.py          # Muslim hadith ingestion
└── validate_corpus.py        # Corpus integrity checks
```

### Embedding Services (services/embed/)
```
services/embed/
├── Dockerfile
├── requirements.txt
├── embed_worker.py           # Batch embedding generation
└── server.py                 # Embedding HTTP service (unused)
```

## Infrastructure

### Docker Compose (infra/compose/)
```
infra/compose/
├── docker-compose.yml        # Main orchestration (6 services)
├── nginx.conf                # Reverse proxy configuration
├── init.sql                  # Postgres schema
└── .env.example              # Environment template
```

**Services Defined:**
1. `basirah-postgres` - PostgreSQL 16
2. `basirah-qdrant` - Qdrant v1.9.2
3. `basirah-api` - FastAPI application
4. `basirah-nginx` - Nginx reverse proxy
5. `basirah-ingest` - Corpus ingestion (profile: tools)
6. `basirah-embed` - Embedding generation (profile: tools)

### Scripts (infra/)
```
infra/
├── start_llama.sh            # llama.cpp launcher for ARM64
└── start_vllm.sh             # vLLM launcher (deprecated, x86 only)
```

## Key Technical Details

### Fixed Issues (Recent Session)
- ✅ Replaced FlagEmbedding with sentence-transformers (stability)
- ✅ Upgraded torch to 2.6+ (CVE-2025-32434 fix)
- ✅ Fixed app.state initialization in lifespan
- ✅ Resolved port conflicts (8080 → 8081)
- ✅ Fixed Qdrant health check dependency

### API Endpoints
```
GET  /health          - Service health check
POST /api/retrieve    - Vector similarity search
POST /api/query       - Full RAG pipeline
```

### Ports
```
5433 → Postgres
6335 → Qdrant HTTP
6336 → Qdrant gRPC
8000 → llama.cpp LLM
8081 → FastAPI
80   → Nginx
```

## Current System Status

**Working (Tested):**
- ✅ Postgres (6,236 Quran verses)
- ✅ Qdrant (6,236 embeddings)
- ✅ llama.cpp (Qwen2.5-7B-Instruct)
- ✅ FastAPI with all endpoints
- ✅ Full RAG pipeline with citations

**In Progress:**
- 🔄 Hadith downloads (Bukhari: 734/7563, Muslim: 114/7470)
- ⏳ Frontend (Next.js) - not started

## Files NOT Included (Excluded by .gitignore)

```
data/                         # Too large (models, corpus, DBs)
├── corpus/                   # Quran + Hadith texts
├── models/                   # 27GB of model weights
│   ├── embed/               # BGE-M3 (2.3GB)
│   ├── rerank/              # BGE-reranker (1.1GB)
│   └── llm-gguf/            # Qwen2.5 (5.3GB)
├── postgres/                # Database files
├── qdrant/                  # Vector storage
└── logs/                    # Application logs
```

## Next Steps (After Review)

1. **Review README.md** - Ensure documentation is accurate
2. **Commit**: `git commit -m "Initial commit: Basirah RAG system"`
3. **Create GitHub repo**: `gh repo create Basirah --public`
4. **Push**: `git push -u origin master`
5. **Add topics**: `islamic-ai`, `rag`, `llm`, `quran`, `hadith`

## Suggested First Commit Message

```
Initial commit: Basirah RAG system

Basirah (بصيرة - insight) is a Retrieval-Augmented Generation system
for Islamic knowledge, providing grounded answers from the Quran,
Sahih al-Bukhari, and Sahih Muslim.

Features:
- FastAPI backend with full RAG pipeline
- Vector search (Qdrant) + cross-encoder reranking
- LLM generation (llama.cpp + Qwen2.5-7B)
- Citation enforcement and confidence scoring
- ARM64 optimized for DGX and Apple Silicon

Current status: MVP operational with Quran corpus (6,236 verses).
Hadith ingestion in progress.

Tech stack: FastAPI, PostgreSQL, Qdrant, sentence-transformers,
llama.cpp, Docker Compose.
```

## Statistics

| Metric | Value |
|--------|-------|
| Total lines of code | ~3,500 |
| Python files | 20 |
| Docker services | 6 |
| API endpoints | 3 |
| Models integrated | 3 |
| Current corpus size | 6,236 verses |
| Target corpus size | 21,269 texts |
| Deployment progress | 25/40 tasks (62.5%) |

---

**Ready for review. No git push has been executed yet.**
