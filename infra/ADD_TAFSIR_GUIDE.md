# Adding Tafsir Ibn Kathir to Basirah

This guide shows you how to add Tafsir Ibn Kathir commentary to your Basirah system.

## What's Been Prepared

✅ Database schema updated (tafsir source type added)  
✅ Download script created (`download_tafsir.py`)  
✅ Ingestion script created (`ingest_tafsir.py`)  
✅ System prompt updated to include Tafsir  
✅ Frontend updated to display Tafsir (📜 icon)  

## Step 1: Download Tafsir Ibn Kathir

This will download ~6,236 tafsir entries (one for each Quranic verse):

```bash
cd /home/syeddgx/Projects/Basirah/services/ingest

# Install requests if needed
pip install requests

# Download tafsir (takes ~1 hour with rate limiting)
python download_tafsir.py
```

**Output**: `data/corpus/raw/tafsir/tafsir_ibn_kathir.jsonl`

**Note**: Downloads at 2 requests/second to respect API limits (~50 minutes total).

## Step 2: Ingest into PostgreSQL

Load the tafsir into the database:

```bash
cd /home/syeddgx/Projects/Basirah/infra/compose

# Run ingestion
docker compose run --rm basirah-ingest python ingest_tafsir.py
```

**Expected**: ~6,200+ tafsir entries inserted

## Step 3: Generate Embeddings

Create vector embeddings for the tafsir:

```bash
# Run embedding job (requires GPU, ~15 min for tafsir)
docker compose run --rm basirah-embed python embed_worker.py --source-type tafsir
```

**Expected**: ~6,200+ vectors added to Qdrant collection

## Step 4: Rebuild & Restart Frontend

Rebuild the web frontend with updated types:

```bash
docker compose build basirah-web
docker compose restart basirah-web basirah-nginx
```

## Step 5: Test

Ask a question that would benefit from tafsir commentary:

```bash
curl -X POST http://192.168.1.147/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is the meaning of Ayat al-Kursi?",
    "top_k": 20,
    "max_tokens": 500
  }' | jq .
```

You should see evidence from both:
- **Quran** (📖): The actual verse text
- **Tafsir** (📜): Ibn Kathir's commentary explaining it

## What's Different

### Before (Quran + Hadith only)
```
Evidence sources:
📖 Quran 2:255
📚 Bukhari 123
📕 Muslim 456
```

### After (with Tafsir)
```
Evidence sources:
📖 Quran 2:255 (verse text)
📜 Tafsir 2:255 (Ibn Kathir's explanation)
📚 Bukhari 123
📕 Muslim 456
```

## Citation Format

The LLM will cite tafsir like this:

> According to [Tafsir 2:255], Ayat al-Kursi demonstrates Allah's sovereignty...

## Verification

Check how many tafsir entries are in the system:

```bash
# In database
docker exec basirah-postgres psql -U basirah -d basirah \
  -c "SELECT COUNT(*) FROM corpus WHERE source_type = 'tafsir';"

# In vector store
curl http://192.168.1.147:8081/health | jq .
```

## Optional: Download in Background

For long downloads, use nohup:

```bash
cd /home/syeddgx/Projects/Basirah/services/ingest
nohup python download_tafsir.py > tafsir_download.log 2>&1 &

# Check progress
tail -f tafsir_download.log
```

## Corpus Statistics (After Tafsir)

| Source | Count | Status |
|--------|-------|--------|
| Quran | 6,236 verses | ✅ |
| Tafsir Ibn Kathir | ~6,200 | 🔄 To add |
| Sahih al-Bukhari | 7,563 | 🔄 Downloading |
| Sahih Muslim | 7,470 | 🔄 Downloading |
| **Total** | **~27,500** | |

---

**Note**: Tafsir provides rich scholarly commentary that helps explain context, meanings, and interpretations of Quranic verses. It enhances answers with deeper understanding while remaining grounded in authentic Islamic scholarship.
