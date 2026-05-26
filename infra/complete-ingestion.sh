#!/bin/bash
#
# Complete Corpus Ingestion Pipeline
# Run this after all downloads are complete
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$SCRIPT_DIR/compose"

echo "🌙 Basirah Complete Ingestion Pipeline"
echo "======================================="
echo ""

# Check if downloads are complete
echo "📊 Checking download status..."
BUKHARI_COUNT=$(wc -l < "$PROJECT_ROOT/data/corpus/raw/bukhari/bukhari_hadiths.jsonl" || echo "0")
MUSLIM_COUNT=$(wc -l < "$PROJECT_ROOT/data/corpus/raw/muslim/muslim_hadiths.jsonl" || echo "0")
TAFSIR_COUNT=$(wc -l < "$PROJECT_ROOT/data/corpus/raw/tafsir/tafsir_ibn_kathir.jsonl" 2>/dev/null || echo "0")

echo "  Bukhari: $BUKHARI_COUNT / 7563"
echo "  Muslim: $MUSLIM_COUNT / 7470"
echo "  Tafsir: $TAFSIR_COUNT / ~6200"
echo ""

# Confirm before proceeding
read -p "Continue with ingestion? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 1
fi

echo ""
echo "Step 1/5: Ingesting Sahih al-Bukhari..."
echo "========================================"
docker compose run --rm basirah-ingest python ingest_bukhari.py
echo "✓ Bukhari ingested"
echo ""

echo "Step 2/5: Ingesting Sahih Muslim..."
echo "===================================="
docker compose run --rm basirah-ingest python ingest_muslim.py
echo "✓ Muslim ingested"
echo ""

echo "Step 3/5: Ingesting Tafsir Ibn Kathir..."
echo "========================================="
if [ "$TAFSIR_COUNT" -gt 1000 ]; then
    docker compose run --rm basirah-ingest python ingest_tafsir.py
    echo "✓ Tafsir ingested"
else
    echo "⚠ Tafsir not downloaded yet. Run download_tafsir.py first."
    echo "Skipping tafsir ingestion..."
fi
echo ""

echo "Step 4/5: Verifying database corpus..."
echo "======================================="
docker exec basirah-postgres psql -U basirah -d basirah -c "
    SELECT
        source_type,
        COUNT(*) as count,
        ROUND(AVG(LENGTH(text_english))) as avg_length
    FROM corpus
    GROUP BY source_type
    ORDER BY source_type;
"
echo ""

echo "Step 5/5: Generating embeddings (GPU required)..."
echo "=================================================="
echo "This will take ~30-45 minutes on GPU"
echo ""
read -p "Generate embeddings now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose run --rm basirah-embed python embed_worker.py
    echo "✓ Embeddings generated"
else
    echo "⚠ Skipped embedding generation"
    echo "Run manually later: docker compose run --rm basirah-embed python embed_worker.py"
fi
echo ""

echo "🎉 Ingestion Complete!"
echo "======================"
echo ""
echo "Final corpus statistics:"
docker exec basirah-postgres psql -U basirah -d basirah -c "
    SELECT
        source_type,
        COUNT(*) as entries
    FROM corpus
    GROUP BY source_type
    ORDER BY source_type;
"
echo ""

echo "Vector store status:"
curl -s http://localhost:8081/health | jq .
echo ""

echo "✅ All done! Your Basirah system now has:"
echo "   • Quran (6,236 verses)"
echo "   • Sahih al-Bukhari (7,563 hadiths)"
echo "   • Sahih Muslim (7,470 hadiths)"
if [ "$TAFSIR_COUNT" -gt 1000 ]; then
    echo "   • Tafsir Ibn Kathir (~6,200 entries)"
fi
echo ""
echo "Access at: http://192.168.1.147"
echo ""
