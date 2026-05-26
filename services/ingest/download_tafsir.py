#!/usr/bin/env python3
"""
Download Tafsir Ibn Kathir from Quran.com API
"""
import json
import time
import requests
from pathlib import Path
import sys

API_BASE = "https://api.quran.com/api/v4"
TAFSIR_ID = 169  # Tafsir Ibn Kathir in English

def download_tafsir_verse(surah: int, verse: int) -> dict:
    """Download tafsir for a specific verse"""
    url = f"{API_BASE}/quran/tafsirs/{TAFSIR_ID}"
    params = {
        'verse_key': f'{surah}:{verse}'
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()

        if 'tafsirs' in data and len(data['tafsirs']) > 0:
            tafsir = data['tafsirs'][0]
            return {
                'surah': surah,
                'verse': verse,
                'verse_key': f'{surah}:{verse}',
                'text': tafsir.get('text', ''),
                'resource_name': tafsir.get('resource_name', 'Tafsir Ibn Kathir'),
                'language': tafsir.get('language_name', 'english')
            }
    except Exception as e:
        print(f"Error fetching {surah}:{verse}: {e}")
        return None

def main():
    output_dir = Path(__file__).parent.parent.parent / 'data' / 'corpus' / 'raw' / 'tafsir'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'tafsir_ibn_kathir.jsonl'

    # Quran has 114 surahs
    # We'll download all available tafsir entries
    verses_info = [
        (1, 7), (2, 286), (3, 200), (4, 176), (5, 120), (6, 165), (7, 206),
        (8, 75), (9, 129), (10, 109), (11, 123), (12, 111), (13, 43), (14, 52),
        (15, 99), (16, 128), (17, 111), (18, 110), (19, 98), (20, 135), (21, 112),
        (22, 78), (23, 118), (24, 64), (25, 77), (26, 227), (27, 93), (28, 88),
        (29, 69), (30, 60), (31, 34), (32, 30), (33, 73), (34, 54), (35, 45),
        (36, 83), (37, 182), (38, 88), (39, 75), (40, 85), (41, 54), (42, 53),
        (43, 89), (44, 59), (45, 37), (46, 35), (47, 38), (48, 29), (49, 18),
        (50, 45), (51, 60), (52, 49), (53, 62), (54, 55), (55, 78), (56, 96),
        (57, 29), (58, 22), (59, 24), (60, 13), (61, 14), (62, 11), (63, 11),
        (64, 18), (65, 12), (66, 12), (67, 30), (68, 52), (69, 52), (70, 44),
        (71, 28), (72, 28), (73, 20), (74, 56), (75, 40), (76, 31), (77, 50),
        (78, 40), (79, 46), (80, 42), (81, 29), (82, 19), (83, 36), (84, 25),
        (85, 22), (86, 17), (87, 19), (88, 26), (89, 30), (90, 20), (91, 15),
        (92, 21), (93, 11), (94, 8), (95, 8), (96, 19), (97, 5), (98, 8),
        (99, 8), (100, 11), (101, 11), (102, 8), (103, 3), (104, 9), (105, 5),
        (106, 4), (107, 7), (108, 3), (109, 6), (110, 3), (111, 5), (112, 4),
        (113, 5), (114, 6)
    ]

    total_verses = sum(v[1] for v in verses_info)
    downloaded = 0
    failed = 0

    print(f"📖 Downloading Tafsir Ibn Kathir...")
    print(f"Total verses to fetch: {total_verses}")
    print(f"Output: {output_file}")
    print()

    with open(output_file, 'w', encoding='utf-8') as f:
        for surah_num, verse_count in verses_info:
            print(f"Surah {surah_num} ({verse_count} verses)...")

            for verse_num in range(1, verse_count + 1):
                tafsir = download_tafsir_verse(surah_num, verse_num)

                if tafsir and tafsir['text'].strip():
                    f.write(json.dumps(tafsir, ensure_ascii=False) + '\n')
                    downloaded += 1

                    if downloaded % 100 == 0:
                        print(f"  ✓ Downloaded {downloaded}/{total_verses} tafsir entries")
                else:
                    failed += 1

                # Rate limiting
                time.sleep(0.5)  # 2 requests per second

    print()
    print(f"✅ Download complete!")
    print(f"   Downloaded: {downloaded}")
    print(f"   Failed/Empty: {failed}")
    print(f"   Output: {output_file}")

if __name__ == "__main__":
    main()
