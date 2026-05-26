#!/usr/bin/env python3
"""Validate corpus integrity after ingestion"""
import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://basirah:password@basirah-postgres:5432/basirah")

def validate_corpus(conn):
    """Run validation checks on corpus"""
    print("="*60)
    print("Corpus Validation")
    print("="*60)

    with conn.cursor() as cur:
        # Count by source type
        cur.execute("""
            SELECT source_type, COUNT(*) as count
            FROM corpus
            GROUP BY source_type
            ORDER BY source_type
        """)
        counts = cur.fetchall()

        print("\nRecord counts by source:")
        total = 0
        for source_type, count in counts:
            print(f"  {source_type:10s}: {count:,}")
            total += count
        print(f"  {'TOTAL':10s}: {total:,}")

        # Expected counts
        expected = {
            "quran": 6236,
            "bukhari": 7563,
            "muslim": 7470
        }

        print("\nExpected vs Actual:")
        all_good = True
        for source_type in ["quran", "bukhari", "muslim"]:
            actual = dict(counts).get(source_type, 0)
            expect = expected[source_type]
            status = "✓" if actual == expect else "⚠"
            pct = (actual / expect * 100) if expect > 0 else 0
            print(f"  {status} {source_type:10s}: {actual:,} / {expect:,} ({pct:.1f}%)")
            if actual != expect:
                all_good = False

        # Check for missing references
        cur.execute("""
            SELECT COUNT(*) FROM corpus
            WHERE reference IS NULL OR reference = ''
        """)
        missing_refs = cur.fetchone()[0]

        if missing_refs > 0:
            print(f"\n⚠ WARNING: {missing_refs} records have missing references")
            all_good = False

        # Check for missing text
        cur.execute("""
            SELECT COUNT(*) FROM corpus
            WHERE text_english IS NULL OR text_english = ''
        """)
        missing_text = cur.fetchone()[0]

        if missing_text > 0:
            print(f"⚠ WARNING: {missing_text} records have missing text")
            all_good = False

        # Sample records
        print("\nSample records:")
        cur.execute("""
            SELECT source_type, reference, LEFT(text_english, 80) as preview
            FROM corpus
            ORDER BY RANDOM()
            LIMIT 3
        """)
        for source_type, ref, preview in cur.fetchall():
            print(f"  [{source_type}] {ref}: {preview}...")

        print("\n" + "="*60)
        if all_good:
            print("✓ Validation PASSED - Corpus is complete")
        else:
            print("⚠ Validation WARNINGS - See above")
        print("="*60)

def main():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        validate_corpus(conn)
        conn.close()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

if __name__ == "__main__":
    main()
