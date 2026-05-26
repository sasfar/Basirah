#!/usr/bin/env python3
"""Ingest Bukhari hadith corpus from JSONL into Postgres"""
import os
import psycopg2
from psycopg2.extras import execute_values
import json

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://basirah:password@basirah-postgres:5432/basirah")
BUKHARI_FILE = "/data/corpus/raw/bukhari/bukhari_hadiths.jsonl"

def parse_bukhari_file(filepath):
    """Parse Bukhari JSONL file from sunnah.com API"""
    records = []

    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        return records

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                hadith = json.loads(line)

                # Extract hadith number and text
                hadith_num = hadith.get("hadithNumber", "")
                body = hadith.get("body", "")

                if not hadith_num or not body:
                    continue

                # Create canonical reference (e.g., "Bukhari 1")
                reference = f"Bukhari {hadith_num}"

                # Metadata
                metadata = {
                    "hadith_number": hadith_num,
                    "book_number": hadith.get("bookNumber"),
                    "chapter": hadith.get("chapterNumber"),
                    "collection": "Sahih al-Bukhari"
                }

                records.append({
                    "source_type": "bukhari",
                    "reference": reference,
                    "text_english": body,
                    "metadata": json.dumps(metadata)
                })

            except json.JSONDecodeError as e:
                print(f"Warning: Skipping malformed JSON at line {line_num}: {e}")
                continue

    return records

def ingest_bukhari(conn):
    """Ingest Bukhari records into database"""
    print(f"Parsing {BUKHARI_FILE}...")
    records = parse_bukhari_file(BUKHARI_FILE)
    print(f"Parsed {len(records)} hadiths")

    if not records:
        print("WARNING: No records parsed!")
        return

    print("Inserting into database...")
    with conn.cursor() as cur:
        cur.execute("DELETE FROM corpus WHERE source_type = 'bukhari'")
        deleted = cur.rowcount
        if deleted > 0:
            print(f"Deleted {deleted} existing Bukhari records")

        insert_query = """
            INSERT INTO corpus (source_type, reference, text_english, metadata)
            VALUES %s
        """
        execute_values(
            cur,
            insert_query,
            [(r["source_type"], r["reference"], r["text_english"], r["metadata"]) for r in records]
        )

    conn.commit()
    print(f"✓ Successfully ingested {len(records)} Bukhari hadiths")

def main():
    print("="*60)
    print("Bukhari Hadith Corpus Ingestion")
    print("="*60)

    try:
        conn = psycopg2.connect(DATABASE_URL)
        ingest_bukhari(conn)
        conn.close()
        print("\nIngestion complete!")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
