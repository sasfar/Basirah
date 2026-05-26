# Basirah - Next Steps

## 📊 Current Status

**System**: ✅ Fully Operational (Quran-only)  
**Access**: http://192.168.1.147  
**GitHub**: https://github.com/sasfar/Basirah

### Corpus Progress

| Source | Downloaded | Ingested | Embedded | Status |
|--------|-----------|----------|----------|--------|
| Quran | 6,236 | ✅ | ✅ | Complete |
| Bukhari | ~1,000 / 7,563 | ⏳ | ⏳ | 13% |
| Muslim | ~270 / 7,470 | ⏳ | ⏳ | 4% |
| Tafsir | 0 / ~6,200 | ⏳ | ⏳ | 0% |
| **Total** | **~7,500 / 27,500** | | | **27%** |

**Downloads ETA**: ~8 hours from now

---

## 🎯 When Downloads Complete

### Option 1: Automated Pipeline (Recommended)

Run the complete ingestion in one command:

```bash
cd /home/syeddgx/Projects/Basirah/infra
./complete-ingestion.sh
```

This will:
1. ✅ Ingest Bukhari → PostgreSQL
2. ✅ Ingest Muslim → PostgreSQL
3. ✅ Ingest Tafsir → PostgreSQL (if downloaded)
4. ✅ Verify database corpus
5. ✅ Generate all embeddings (~45 min on GPU)

### Option 2: Manual Steps

If you prefer to run each step manually:

```bash
cd /home/syeddgx/Projects/Basirah/infra/compose

# 1. Ingest hadiths
docker compose run --rm basirah-ingest python ingest_bukhari.py
docker compose run --rm basirah-ingest python ingest_muslim.py

# 2. Download Tafsir (optional, ~50 min)
cd ../../services/ingest
python download_tafsir.py

# 3. Ingest Tafsir
cd ../../infra/compose
docker compose run --rm basirah-ingest python ingest_tafsir.py

# 4. Generate embeddings for everything
docker compose run --rm basirah-embed python embed_worker.py
```

---

## 📡 Monitor Download Progress

Watch live progress with visual progress bars:

```bash
cd /home/syeddgx/Projects/Basirah/infra
./monitor-downloads.sh
```

Or check manually:

```bash
# Quick check
cd /home/syeddgx/Projects/Basirah/data/corpus/raw
echo "Bukhari: $(wc -l < bukhari/bukhari_hadiths.jsonl) / 7563"
echo "Muslim: $(wc -l < muslim/muslim_hadiths.jsonl) / 7470"

# Detailed logs
tail -f bukhari/download_slow.log
tail -f muslim/download_slow.log
```

---

## 🌙 What's Working Now

While waiting, you can use the system with Quran content:

### Test the Web UI

1. Open http://192.168.1.147 in your browser
2. Ask questions like:
   - "What is fasting in Ramadan?"
   - "What are the qualities of believers?"
   - "What does the Quran say about prayer?"

### Test the API

```bash
# Health check
curl http://192.168.1.147/health | jq .

# Full RAG query
curl -X POST http://192.168.1.147/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is charity in Islam?",
    "top_k": 10,
    "max_tokens": 300
  }' | jq .
```

---

## 🔧 System Management

### Start/Stop Services

```bash
# Using systemd (auto-start on boot)
sudo systemctl start basirah
sudo systemctl stop basirah
sudo systemctl status basirah

# Using Docker Compose directly
cd /home/syeddgx/Projects/Basirah/infra/compose
docker compose up -d      # Start all
docker compose down       # Stop all
docker compose ps         # Check status
```

### View Logs

```bash
# System service logs
sudo journalctl -u basirah -f

# Container logs
docker logs basirah-api -f
docker logs basirah-web -f
docker logs basirah-nginx -f
```

### Check Health

```bash
# Overall system
curl http://192.168.1.147/health

# Individual services
docker ps --filter "name=basirah"
```

---

## 📦 Final Corpus (After All Downloads)

Once everything is complete, your system will have:

- **Quran**: 6,236 verses with Sahih International translation
- **Tafsir Ibn Kathir**: ~6,200 detailed verse explanations
- **Sahih al-Bukhari**: 7,563 authentic hadiths
- **Sahih Muslim**: 7,470 authentic hadiths
- **Total**: ~27,500 knowledge entries

All searchable with semantic vector search and citation-grounded generation.

---

## 🎓 Example Queries (After Full Corpus)

Questions that will benefit from the complete corpus:

1. **Quran + Tafsir**:
   - "What is the meaning of Ayat al-Kursi?"
   - "Explain the opening of Surah Al-Fatiha"

2. **Quran + Hadith**:
   - "What did the Prophet say about fasting?"
   - "How should Muslims perform prayer?"

3. **Cross-source synthesis**:
   - "What is the importance of charity in Islam?"
   - "What are the rights of neighbors?"

The system will cite from all relevant sources with proper attribution.

---

## 🚀 Performance Expectations

After full corpus ingestion:

| Operation | Time | Notes |
|-----------|------|-------|
| Vector search | ~20ms | 27,500 vectors in Qdrant |
| Reranking | ~500ms | Top 20 passages |
| LLM generation | 2-5s | Qwen2.5-7B on CPU |
| **End-to-end query** | **3-6s** | Full RAG pipeline |

---

## 📝 Repository

All code is on GitHub: https://github.com/sasfar/Basirah

Latest commits include:
- ✅ Next.js chat UI with dark mode
- ✅ Tafsir Ibn Kathir integration
- ✅ LAN deployment configuration
- ✅ Systemd service for auto-start

---

## ❓ Questions?

Check the guides:
- **ADD_TAFSIR_GUIDE.md** - Tafsir integration details
- **README.md** - Complete system documentation
- **CONTRIBUTING.md** - Development guidelines

---

**System is operational and waiting for downloads to complete.**  
**Estimated completion: ~8 hours from now.**

Run `./monitor-downloads.sh` to watch progress in real-time! 📊
