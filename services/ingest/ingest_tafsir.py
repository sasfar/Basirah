#!/usr/bin/env python3
"""
Ingest Tafsir Ibn Kathir into PostgreSQL
"""
import json
import psycopg2
from pathlib import Path
import os
import sys

def get_connection():
    """Get database connection"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("Error: DATABASE_URL environment variable not set")
        sys.exit(1)

    return psycopg2.connect(db_url)

def ingest_tafsir():
    """Ingest tafsir entries from JSONL file"""
    corpus_path = Path('/data/corpus/raw/tafsir/tafsir_ibn_kathir.jsonl')

    if not corpus_path.exists():
        print(f"Error: {corpus_path} not found")
        print("Run download_tafsir.py first")
        sys.exit(1)

    conn = get_connection()
    cur = conn.cursor()

    print("📖 Ingesting Tafsir Ibn Kathir...")

    inserted = 0
    skipped = 0

    try:
        with open(corpus_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    entry = json.loads(line.strip())

                    # Clean HTML tags from text
                    text = entry['text']
                    import re
                    # Remove HTML tags
                    text = re.sub(r'<[^>]+>', '', text)
                    # Remove extra whitespace
                    text = re.sub(r'\s+', ' ', text).strip()

                    if not text:
                        skipped += 1
                        continue

                    # Create reference like "Tafsir 2:255" (Ibn Kathir on Quran 2:255)
                    reference = f"Tafsir {entry['verse_key']}"

                    # Insert into corpus table
                    cur.execute("""
                        INSERT INTO corpus (reference, text, source_type, metadata)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (reference, source_type) DO NOTHING
                    """, (
                        reference,
                        text,
                        'tafsir',
                        json.dumps({
                            'surah': entry['surah'],
                            'verse': entry['verse'],
                            'verse_key': entry['verse_key'],
                            'tafsir_name': 'Tafsir Ibn Kathir',
                            'language': entry.get('language', 'english')
                        })
                    ))

                    if cur.rowcount > 0:
                        inserted += 1
                    else:
                        skipped += 1

                    if inserted % 100 == 0:
                        print(f"  ✓ Inserted {inserted} tafsir entries...")
                        conn.commit()

                except json.JSONDecodeError as e:
                    print(f"Warning: Failed to parse line {line_num}: {e}")
                    skipped += 1
                    continue
                except Exception as e:
                    print(f"Warning: Failed to insert line {line_num}: {e}")
                    skipped += 1
                    continue

        conn.commit()

        print()
        print(f"✅ Ingestion complete!")
        print(f"   Inserted: {inserted}")
        print(f"   Skipped: {skipped}")

        # Verify count
        cur.execute("SELECT COUNT(*) FROM corpus WHERE source_type = 'tafsir'")
        total = cur.fetchone()[0]
        print(f"   Total tafsir entries in DB: {total}")

    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    ingest_tafsir()
