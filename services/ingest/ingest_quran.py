#!/usr/bin/env python3
"""Ingest Quran corpus from Tanzil text file into Postgres"""
import os
import psycopg2
from psycopg2.extras import execute_values
import json

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://basirah:password@basirah-postgres:5432/basirah")

# Input file
QURAN_FILE = "/data/corpus/raw/quran/quran-simple.txt"

def parse_quran_file(filepath):
    """Parse Tanzil Quran text file (format: SURAH|VERSE|TEXT)"""
    records = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue

            parts = line.split("|", 2)
            if len(parts) != 3:
                print(f"Warning: Skipping malformed line {line_num}: {line[:50]}")
                continue

            surah, verse, text = parts

            # Create canonical reference (e.g., "Quran 2:255")
            reference = f"Quran {surah}:{verse}"

            # Metadata
            metadata = {
                "surah": int(surah),
                "verse": int(verse),
                "translation": "Sahih International"
            }

            records.append({
                "source_type": "quran",
                "reference": reference,
                "text_english": text,
                "metadata": json.dumps(metadata)
            })

    return records

def ingest_quran(conn):
    """Ingest Quran records into database"""
    print(f"Parsing {QURAN_FILE}...")
    records = parse_quran_file(QURAN_FILE)
    print(f"Parsed {len(records)} verses")

    if not records:
        print("ERROR: No records parsed!")
        return

    # Insert into database
    print("Inserting into database...")
    with conn.cursor() as cur:
        # Delete existing Quran records
        cur.execute("DELETE FROM corpus WHERE source_type = 'quran'")
        deleted = cur.rowcount
        if deleted > 0:
            print(f"Deleted {deleted} existing Quran records")

        # Insert new records
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
    print(f"✓ Successfully ingested {len(records)} Quran verses")

def main():
    print("="*60)
    print("Quran Corpus Ingestion")
    print("="*60)

    try:
        conn = psycopg2.connect(DATABASE_URL)
        ingest_quran(conn)
        conn.close()
        print("\nIngestion complete!")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
