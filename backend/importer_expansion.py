# -*- coding: utf-8 -*-
"""
VerseNest Originals — Automated Idempotent 200 Sinhala Songs Importer
Adheres strictly to student mini-hackathon rules:
- Clear, simple, beginner-friendly Python logic
- Short comments explaining each key step
- Multi-tiered duplicate prevention
- Transaction rollback on error
- Detailed logging per batch
"""

import os
import sys
import json
import uuid
import sqlite3
import csv
from datetime import datetime

# Add current directory to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "data", "versenest.db")

from expansion_dataset import EXPANSION_BATCHES, ALL_200_SONGS
from deduplication import (
    evaluate_song_duplicate,
    normalize_sinhala_text,
    normalize_english_text
)

def run_import(dry_run: bool = False, db_path: str = DB_PATH):
    """
    Executes the 200 Sinhala song batch expansion across all 8 batches.
    """
    print("=" * 70)
    print("VerseNest — Starting 200 Genuine Sinhala Songs Expansion Import")
    print(f"Target Database: {db_path}")
    print(f"Dry Run Mode: {dry_run}")
    print("=" * 70)

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Step 1: Record baseline counts
    cursor.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published' AND language = 'si'")
    baseline_sinhala = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published' AND language = 'en'")
    baseline_english = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published'")
    baseline_total = cursor.fetchone()[0]

    print(f"\n[Baseline] Published Sinhala: {baseline_sinhala} | English Originals: {baseline_english} | Total: {baseline_total}")

    started_at = datetime.utcnow().isoformat()
    total_imported = 0
    total_skipped = 0
    total_queued = 0
    total_errors = 0
    imported_song_records = []

    # Process all 8 batches (25 songs per batch)
    for batch_idx, batch_songs in enumerate(EXPANSION_BATCHES):
        batch_num = batch_idx + 1
        print(f"\n--- Processing Batch {batch_num} of {len(EXPANSION_BATCHES)} ({len(batch_songs)} songs) ---")
        
        batch_imported = 0
        batch_skipped = 0
        batch_queued = 0

        # Start transaction
        try:
            for s in batch_songs:
                # Pre-import validation
                required_fields = ["title_si", "title_en", "artist", "release_year", "era_decade", "genre", "youtube_url", "musicbrainz_id"]
                missing = [f for f in required_fields if not s.get(f)]
                if missing:
                    raise ValueError(f"Song {s.get('title_en', 'Unknown')} missing required fields: {missing}")

                # Prepare candidate dict for deduplication
                candidate = {
                    "title_si": s["title_si"],
                    "title_en": s["title_en"],
                    "artist": s["artist"],
                    "singers": s.get("singers", [s["artist"]]),
                    "lyricist": s.get("lyricist", ""),
                    "composer": s.get("composer", ""),
                    "release_year": s["release_year"],
                    "song_type": "Original",
                    "youtube_url": s["youtube_url"],
                    "musicbrainz_id": s["musicbrainz_id"]
                }

                # Evaluate for duplicates against database
                check_result = evaluate_song_duplicate(candidate, conn)

                if check_result.action in ("skip", "update_metadata"):
                    batch_skipped += 1
                    total_skipped += 1
                    print(f"  [SKIP/UPDATE] Duplicate or existing record detected for '{s['title_en']}' - {check_result.reasons}")
                    continue

                elif check_result.action == "queue_review":
                    batch_queued += 1
                    total_queued += 1
                    print(f"  [QUEUE] Review needed for '{s['title_en']}' (score {check_result.score:.2f})")
                    if not dry_run:
                        cursor.execute("""
                            INSERT INTO duplicates_review 
                            (candidate_json, existing_song_id, similarity_score, match_reasons, status, created_at)
                            VALUES (?, ?, ?, ?, 'pending', ?)
                        """, (
                            json.dumps(s, ensure_ascii=False),
                            check_result.existing_song_id,
                            check_result.score,
                            json.dumps(check_result.reasons),
                            datetime.utcnow().isoformat()
                        ))
                    continue

                elif check_result.action == "insert_new":
                    # Insert genuine Sinhala song
                    song_uuid = str(uuid.uuid4())
                    now_str = datetime.utcnow().isoformat()
                    norm_title_si = normalize_sinhala_text(s["title_si"])
                    norm_title_en = normalize_english_text(s["title_en"])
                    norm_artist = normalize_english_text(s["artist"])

                    is_classic = 1 if s["release_year"] <= 1989 else 0
                    is_recent = 1 if s["release_year"] >= 2020 else 0

                    if not dry_run:
                        cursor.execute("""
                            INSERT INTO songs (
                                song_uuid, title_si, title_en, 
                                normalized_title_si, normalized_title_en, alternative_titles,
                                artist, normalized_artist, singers, lyricist, composer,
                                album_or_movie, release_year, era_decade, genre, song_type,
                                youtube_url, audio_url, source_url, isrc, musicbrainz_id,
                                lyrics, lyrics_status, lyrics_license_notes, lyrics_evidence,
                                description, editorial_commentary, categories,
                                is_classic, is_recent, publication_status, view_count,
                                created_at, updated_at, language
                            ) VALUES (
                                ?, ?, ?,
                                ?, ?, ?,
                                ?, ?, ?, ?, ?,
                                ?, ?, ?, ?, ?,
                                ?, ?, ?, ?, ?,
                                ?, ?, ?, ?,
                                ?, ?, ?,
                                ?, ?, ?, ?,
                                ?, ?, ?
                            )
                        """, (
                            song_uuid,
                            s["title_si"],
                            s["title_en"],
                            norm_title_si,
                            norm_title_en,
                            json.dumps([s["title_en"]]),
                            s["artist"],
                            norm_artist,
                            json.dumps(s.get("singers", [s["artist"]]), ensure_ascii=False),
                            s.get("lyricist", ""),
                            s.get("composer", ""),
                            s.get("album_or_movie", ""),
                            s["release_year"],
                            s["era_decade"],
                            s["genre"],
                            "Original",
                            s["youtube_url"],
                            "",
                            s.get("source_url", f"https://musicbrainz.org/recording/{s['musicbrainz_id']}"),
                            s.get("isrc", ""),
                            s["musicbrainz_id"],
                            None,  # Copyright protection: lyrics shielded
                            "rights_unknown",
                            "Restricted: Commercial Sinhala recording. Lyrics shielded under IP policy until verified.",
                            "Commercial copyrighted musical work broadcast in Sri Lanka; rights held by artist/estate/label.",
                            f"Authentic Sri Lankan classic recorded by {s['artist']}.",
                            f"Archived in VerseNest Sinhala Music Discovery catalogue ({s['era_decade']}).",
                            json.dumps(s.get("categories", [s["genre"], s["era_decade"]])),
                            is_classic,
                            is_recent,
                            "published",
                            0,
                            now_str,
                            now_str,
                            "si"
                        ))

                        new_id = cursor.lastrowid
                        imported_song_records.append({
                            "id": new_id,
                            "song_uuid": song_uuid,
                            "title_si": s["title_si"],
                            "title_en": s["title_en"],
                            "artist": s["artist"],
                            "era_decade": s["era_decade"],
                            "release_year": s["release_year"],
                            "genre": s["genre"],
                            "youtube_url": s["youtube_url"],
                            "source_url": s.get("source_url", f"https://musicbrainz.org/recording/{s['musicbrainz_id']}"),
                            "musicbrainz_id": s["musicbrainz_id"],
                            "lyrics_status": "rights_unknown"
                        })
                    
                    batch_imported += 1
                    total_imported += 1

            # Commit batch transaction
            if not dry_run:
                conn.commit()
            print(f"  -> Batch {batch_num} Committed: {batch_imported} inserted, {batch_skipped} skipped, {batch_queued} queued.")

        except Exception as e:
            conn.rollback()
            total_errors += 1
            print(f"  [ERROR] Batch {batch_num} failed with error: {e}. Transaction rolled back.")
            raise

    completed_at = datetime.utcnow().isoformat()

    # Step 3: Record import session in import_history
    if not dry_run:
        summary_text = (
            f"Expanded catalogue with {total_imported} genuine Sinhala songs across 8 batches. "
            f"Preserved all {baseline_english} English originals. 0 synthetic records restored."
        )
        cursor.execute("""
            INSERT INTO import_history (
                source_name, started_at, completed_at, total_candidates,
                imported_count, updated_count, duplicates_skipped, review_queued,
                errors_count, status, summary_details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "expansion_200_curated",
            started_at,
            completed_at,
            len(ALL_200_SONGS),
            total_imported,
            0,
            total_skipped,
            total_queued,
            total_errors,
            "completed" if total_errors == 0 else "failed",
            summary_text
        ))
        conn.commit()

    # Post-import verification
    cursor.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published' AND language = 'si'")
    final_sinhala = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published' AND language = 'en'")
    final_english = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published'")
    final_total = cursor.fetchone()[0]

    print("\n" + "=" * 70)
    print("IMPORT COMPLETE SUMMARY")
    print(f"Total Candidates: {len(ALL_200_SONGS)}")
    print(f"Successfully Imported: {total_imported}")
    print(f"Duplicates Skipped: {total_skipped}")
    print(f"Queued for Review: {total_queued}")
    print(f"Errors: {total_errors}")
    print("-" * 70)
    print(f"Final Published Sinhala Songs: {final_sinhala} (Expected: {baseline_sinhala + total_imported})")
    print(f"Final English Originals: {final_english} (Must remain {baseline_english})")
    print(f"Final Total Published Songs: {final_total}")
    print("=" * 70)

    # Export CSV deliverable if any songs were imported
    if imported_song_records and not dry_run:
        csv_path = os.path.join(PROJECT_DIR, "NEW_SINHALA_SONGS_IMPORTED.csv")
        fieldnames = [
            "id", "song_uuid", "title_si", "title_en", "artist",
            "era_decade", "release_year", "genre", "youtube_url",
            "source_url", "musicbrainz_id", "lyrics_status"
        ]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in imported_song_records:
                writer.writerow(row)
        print(f"\n[Deliverable] Exported {len(imported_song_records)} records to {csv_path}")

    conn.close()
    return total_imported, total_skipped, total_queued, total_errors

if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    run_import(dry_run=dry)
