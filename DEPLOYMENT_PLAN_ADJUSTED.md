# Basirah DGX Deployment Plan - ADJUSTED

**Status**: ⏸️ AWAITING APPROVAL  
**Date**: 2026-05-25  
**Target System**: DGX with NVIDIA GB10 GPU

---

## Critical Hardware Findings

### Your System vs. Original Plan

| Component | Original Plan | Your DGX | Impact |
|---|---|---|---|
| **GPU** | 2× A100 80GB | 1× NVIDIA GB10 (memory unknown) | **HIGH** - Requires time-sharing |
| **CPU** | 32 cores | 20 cores (Cortex-X925/A725) | **LOW** - Acceptable for MVP |
| **RAM** | 128 GB | 122 GB | **LOW** - Adequate |
| **CUDA** | ≥12.1 | 13.0 | ✅ Ready |
| **Docker** | v2.20+ | v5.0.2 | ✅ Ready |

### GPU Memory Detection Issue

The NVIDIA GB10 is part of the Grace Blackwell platform. Standard `nvidia-smi` memory queries return 0/N/A, likely due to:
- Unified memory architecture (CPU+GPU shared)
- Non-standard driver reporting
- Development platform tooling differences

**Conservative approach**: Start with **Qwen2.5-7B-Instruct** (~14-20GB VRAM requirement)
- Guaranteed to fit on any modern GPU
- Adequate quality for citation-grounded answers (model isn't the source of truth)
- Can upgrade to 14B later if headroom allows

---

## Adjusted Architecture

### Single-GPU Time-Sharing Strategy

**Phase 1: Embedding (One-time, ~2-4 hours)**
```bash
# GPU 0: BGE-M3 embedding model
# Batch-process all 21,000+ corpus records
# Output: Qdrant vector collection
# Then: Stop embedding service, free GPU
```

**Phase 2: Serving (Continuous)**
```bash
# GPU 0: vLLM with Qwen2.5-7B-Instruct
# Dedicated to API inference requests
# Embedding service remains offline
```

**Re-embedding strategy**: If corpus updates needed, temporarily stop vLLM, run embedding job, restart vLLM.

### Storage Layout

```
/home/syeddgx/Projects/Basirah/data/
├── models/
│   ├── llm/                  # Qwen2.5-7B-Instruct (~14GB)
│   ├── embed/                # BAAI/bge-m3 (~2GB)
│   └── rerank/               # BAAI/bge-reranker-v2-m3 (~1GB)
├── corpus/
│   ├── raw/                  # Downloaded sources
│   │   ├── quran/           # Tanzil XML/text
│   │   ├── bukhari/         # Hadith JSON/CSV
│   │   └── muslim/          # Hadith JSON/CSV
│   ├── normalized/          # JSONL per source
│   └── manifests/           # Provenance metadata
├── postgres/                # Corpus records (~500MB)
├── qdrant/                  # Vector index (~5GB for 21k records)
└── logs/                    # Service logs
```

**Total storage**: ~70GB (models dominate)

---

## Docker Compose Adjustments

### Key Changes from Original Plan

1. **Single GPU assignment**
   ```yaml
   basirah-vllm:
     environment:
       NVIDIA_VISIBLE_DEVICES: "0"
     command: >
       --model /model
       --gpu-memory-utilization 0.90  # Increased from 0.85
       --max-model-len 8192
       --dtype bfloat16
   
   basirah-embed:
     # No runtime: nvidia in production compose
     # Run as one-shot job with --gpus all via docker compose run
   ```

2. **Memory limits for 122GB RAM**
   ```yaml
   services:
     basirah-postgres:
       deploy:
         resources:
           limits:
             memory: 8G
     
     basirah-qdrant:
       deploy:
         resources:
           limits:
             memory: 16G
     
     basirah-api:
       deploy:
         resources:
           limits:
             memory: 8G
   ```

3. **Volume paths**
   ```yaml
   volumes:
     - /home/syeddgx/Projects/Basirah/data/postgres:/var/lib/postgresql/data
     - /home/syeddgx/Projects/Basirah/data/qdrant:/qdrant/storage
     # ... etc
   ```

---

## Deployment Sequence

### Phase 0: Pre-flight (Tasks 1-2)
- ✅ Validate GPU (completed above - using 7B model)
- Create `/home/syeddgx/Projects/Basirah/data` directory tree

### Phase 1: Asset Acquisition (Tasks 3-8)
Download models:
- `Qwen/Qwen2.5-7B-Instruct` → `data/models/llm/`
- `BAAI/bge-m3` → `data/models/embed/`
- `BAAI/bge-reranker-v2-m3` → `data/models/rerank/`

Download corpora:
- Tanzil Quran → `data/corpus/raw/quran/`
- Sahih al-Bukhari → `data/corpus/raw/bukhari/`
- Sahih Muslim → `data/corpus/raw/muslim/`

**Estimated time**: 1-2 hours (network-dependent)

### Phase 2: Repository Scaffold (Tasks 9-13)
Create directory structure:
```
basirah/
├── apps/api/          # FastAPI service
├── apps/web/          # Next.js frontend
├── services/ingest/   # Corpus normalization
├── services/embed/    # Embedding worker
├── infra/compose/     # Docker configs
└── tests/             # Eval & smoke tests
```

Write configs:
- `docker-compose.yml` (with single-GPU adjustments)
- `nginx.conf`
- `.env.example`
- Postgres schema SQL

**Estimated time**: 30 minutes

### Phase 3: Infrastructure Services (Task 14)
```bash
docker compose up -d basirah-postgres basirah-qdrant
# Wait for health checks
docker compose ps
```

**Milestone 1 checkpoint**: Both services healthy

### Phase 4: Corpus Ingestion (Tasks 15-19)
Build and run ingestion service:
```bash
docker compose build basirah-ingest
docker compose run --rm basirah-ingest python ingest_quran.py
docker compose run --rm basirah-ingest python ingest_bukhari.py
docker compose run --rm basirah-ingest python ingest_muslim.py
docker compose run --rm basirah-ingest python validate_corpus.py
```

**Milestone 1 complete**: 21,269 records in Postgres
- 6,236 Quran ayat
- 7,563 Bukhari hadiths
- 7,470 Muslim hadiths

**Estimated time**: 1 hour

### Phase 5: Embedding (Tasks 20-22)
Build embedding service and run one-time job:
```bash
docker compose build basirah-embed
docker compose run --rm --gpus all basirah-embed python embed_worker.py \
  --input /data/corpus/normalized \
  --qdrant-url http://basirah-qdrant:6333 \
  --collection basirah_corpus \
  --batch-size 64 \
  --recreate-collection
```

Verify:
```bash
curl http://localhost:6333/collections/basirah_corpus
# Should show ~21k points
```

**Estimated time**: 2-3 hours (GPU-bound)

### Phase 6: LLM Service (Tasks 23-24)
Start vLLM with Qwen2.5-7B:
```bash
docker compose up -d basirah-vllm
# Wait for model load (1-2 minutes)
docker compose logs -f basirah-vllm
```

Smoke test:
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "basirah-llm",
    "messages": [{"role":"user","content":"Test"}],
    "max_tokens": 10
  }'
```

**Estimated time**: 5 minutes

### Phase 7: API - Retrieval (Tasks 25-28)
Build FastAPI service with retrieval logic:
- `apps/api/main.py`
- `apps/api/routers/retrieve.py`
- `apps/api/services/retrieval.py` (Qdrant client)
- `apps/api/services/rerank.py` (BGE-reranker on CPU)

Start API:
```bash
docker compose up -d basirah-api
```

Test `/retrieve`:
```bash
curl -X POST http://localhost:8080/retrieve \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the ruling on intention?","top_k":5}'
```

**Milestone 2 complete**: Retrieval returns ranked passages with references

**Estimated time**: 3-4 hours

### Phase 8: API - Generation (Tasks 29-33)
Add generation logic:
- `services/prompt_builder.py` (system prompt + evidence injection)
- `services/llm_client.py` (OpenAI-compatible vLLM client)
- `services/confidence.py` (citation coverage scoring)
- `routers/query.py` (full RAG pipeline)

Test `/query`:
```bash
curl -X POST http://localhost:8080/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What do the sources say about intention in actions?",
    "filters": {"sources": ["quran","bukhari","muslim"], "language": "en"}
  }'
```

Run eval set (20 questions) and verify citations.

**Milestone 3 complete**: Grounded answers with citations

**Estimated time**: 4-5 hours

### Phase 9: WebUI (Tasks 34-36)
Build Next.js frontend:
- Search input
- Evidence cards (expandable)
- Confidence badge
- Reference links

Start web + nginx:
```bash
docker compose up -d basirah-web basirah-nginx
```

Browser test at `http://<dgx-ip>/`

**Milestone 4 complete**: End-to-end user flow

**Estimated time**: 6-8 hours

### Phase 10: Hardening (Tasks 37-39)
- Configure volume persistence
- Add API health checks
- Run load test (5 concurrent queries, measure p95 latency)

**Milestone 5 complete**: Production-ready MVP

**Estimated time**: 2-3 hours

### Phase 11: Documentation (Task 40)
Write operational runbook.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| GPU memory insufficient for 7B | Low | High | Fall back to 4-bit quantization |
| 20 cores bottleneck API throughput | Medium | Medium | Limit concurrent requests to 5 |
| 122GB RAM insufficient under load | Low | High | Memory limits in compose prevent OOM |
| Corpus download sources offline | Low | Medium | Use HuggingFace mirrors |
| vLLM startup fails on GB10 | Medium | Critical | Test in Phase 6; document workarounds |

---

## Success Criteria

### Milestone 1: Corpus Foundation
- [ ] 21,269 records in Postgres (6,236 + 7,563 + 7,470)
- [ ] All records have canonical references
- [ ] Manifests include source attribution

### Milestone 2: Search-Only API
- [ ] `/retrieve` endpoint responds < 1s
- [ ] Returns top-5 passages with Quran/hadith references
- [ ] 10 test queries return relevant results

### Milestone 3: Grounded Generation
- [ ] `/query` endpoint responds < 10s
- [ ] All 20 eval questions return answers with citations
- [ ] No hallucinated references

### Milestone 4: WebUI
- [ ] Browser loads at `http://<dgx-ip>/`
- [ ] Search → retrieve → generate → display works end-to-end
- [ ] Evidence cards show correct references

### Milestone 5: Production-Ready
- [ ] All services restart cleanly
- [ ] Data persists across restarts
- [ ] Load test: 5 concurrent queries, p95 < 10s
- [ ] No crashes or OOM errors

---

## Total Estimated Time

| Phase | Time |
|---|---|
| Asset download | 1-2 hours |
| Repository setup | 30 min |
| Corpus ingestion | 1 hour |
| Embedding | 2-3 hours |
| API development | 7-9 hours |
| WebUI development | 6-8 hours |
| Hardening | 2-3 hours |
| Documentation | 1 hour |
| **Total** | **21-28 hours** |

Spread over 3-4 days at a comfortable pace.

---

## Next Steps

**⏸️ AWAITING YOUR APPROVAL**

Once you approve this plan, I will:
1. Create the storage directory structure (Task 2)
2. Begin model downloads (Tasks 3-5)
3. Acquire corpus sources (Tasks 6-8)
4. Proceed through the 11 phases sequentially

**Before I start:**
- Review the single-GPU time-sharing approach
- Confirm storage path: `~/Projects/Basirah/data`
- Confirm model choice: Qwen2.5-7B-Instruct
- Confirm corpus sources: Tanzil + sunnah.com/HuggingFace

**Questions?**
- Need any adjustments to the architecture?
- Prefer a different model (e.g., Llama-3-8B)?
- Want to pause at any specific milestone?

---

**Ready to begin deployment when you give the green light.**
