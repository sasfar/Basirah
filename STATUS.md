# Basirah Deployment Status

**Last Updated:** 2026-05-26 17:52 UTC  
**Overall Progress:** 21/40 tasks (52.5%)

## Services Running

| Service | Status | Endpoint | Notes |
|---------|--------|----------|-------|
| Postgres | ✅ Healthy | localhost:5433 | 6,236 Quran verses loaded |
| Qdrant | ✅ Healthy | localhost:6335 | Vector store (embedding in progress) |
| llama.cpp | ✅ Running | localhost:8000 | Qwen2.5-7B-Instruct Q5_K_M |

## Data Status

| Dataset | Records | Status | Details |
|---------|---------|--------|---------|
| Quran | 6,236 / 6,236 | ✅ Complete | Tanzil (Sahih International) |
| Bukhari | ~50 / 7,563 | ⏳ Downloading | Slow API rate limits (~15h remaining) |
| Muslim | ~20 / 7,470 | ⏳ Downloading | Slow API rate limits (~15h remaining) |

## Models

| Model | Size | Status | Purpose |
|-------|------|--------|---------|
| Qwen2.5-7B-Instruct (GGUF) | 5.1GB | ✅ Loaded | LLM inference (llama.cpp) |
| BGE-M3 | 4.3GB | ⏳ In use | Embedding generation |
| BGE-reranker-v2-m3 | 2.2GB | ✅ Ready | Reranking (will run on CPU) |

## Current Operations

- **Embedding Job**: Processing 6,236 Quran verses → Qdrant vectors (ETA: 10-20 min)
- **Hadith Downloads**: Background processes continue (~15 hours remaining)

## Architecture Adjustments Made

1. **LLM**: Switched from vLLM to llama.cpp (ARM64 compatibility)
2. **Qdrant Ports**: Changed to 6335/6336 (avoided conflict with levault-qdrant)
3. **Postgres Port**: Changed to 5433 (avoided conflict with system Postgres)
4. **GPU Strategy**: Time-sharing (embedding offline, then LLM online)

## Next Tasks

- [ ] Complete embedding job
- [ ] Build FastAPI service (Tasks 25-33)
- [ ] Build Next.js frontend (Tasks 34-36)
- [ ] End-to-end testing
- [ ] Wait for hadith downloads to complete
- [ ] Ingest hadiths and re-run embedding

## Known Issues

- Hadith API rate limiting very aggressive (60s waits)
- vLLM not compatible with ARM64 architecture
- Docker port conflicts with existing services

## Storage Usage

```
/home/syeddgx/Projects/Basirah/data/
├── models/        ~26GB (llm-gguf: 5.1GB, llm: 15GB, embed: 4.3GB, rerank: 2.2GB)
├── corpus/        ~1MB (Quran text)
├── postgres/      ~10MB
├── qdrant/        ~50MB (after embedding: ~150MB)
└── logs/          ~5MB
Total: ~27GB
```

## Startup Commands

```bash
# Start infrastructure
cd ~/Projects/Basirah/infra/compose
docker compose up -d basirah-postgres basirah-qdrant

# Start LLM
~/Projects/Basirah/infra/start_llama.sh &

# Check status
docker compose ps
curl http://localhost:8000/v1/models
curl http://localhost:6335/healthz

# Monitor hadith downloads
tail -f ~/Projects/Basirah/data/corpus/raw/bukhari/download_slow.log
tail -f ~/Projects/Basirah/data/corpus/raw/muslim/download_slow.log
```
