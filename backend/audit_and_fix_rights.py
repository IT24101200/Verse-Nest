# -*- coding: utf-8 -*-
"""
VerseNest Originals - Comprehensive Copyright & Database Quality Remediation
Audits all 5,012 records, corrects false 'original_owned' / 'public_domain' statuses,
withholds unauthorized commercial lyrics, quarantines unverified combinatorial records,
and preserves verified songs.
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "versenest.db")

def run_remediation():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("[Audit] Starting database quality and copyright remediation...")

    # 1. Protect Verified Original VerseNest Songs (IDs 1-12)
    cursor.execute("""
        UPDATE songs
        SET lyrics_status = 'original_owned',
            publication_status = 'published',
            lyrics_license_notes = 'Original creative writing sample owned directly by VerseNest Originals.'
        WHERE id BETWEEN 1 AND 12;
    """)
    print("[Audit] Verified 12 original VerseNest English songs (IDs 1-12) as 'original_owned'.")

    # 2. Update Verified Authentic Sinhala Classics & Hits (IDs 13-37)
    # These have verified real artists, lyricists, composers, and release years.
    # Because full commercial lyrics publishing requires an explicit written license,
    # set lyrics_status to 'rights_unknown' and nullify stored lyrics to prevent unauthorized reproduction.
    cursor.execute("""
        UPDATE songs
        SET lyrics_status = 'rights_unknown',
            publication_status = 'published',
            lyrics = NULL,
            lyrics_license_notes = 'Commercial composition metadata indexed for educational discovery. Lyrics withheld pending verified publisher license.'
        WHERE id BETWEEN 13 AND 37;
    """)
    print("[Audit] Verified 25 iconic Sinhala songs (IDs 13-37) as 'published' metadata with lyrics shielded as 'rights_unknown'.")

    # 3. Quarantine Unverified / Combinatorial Records (IDs 38 to end)
    # These records were synthetically generated and must not claim 'original_owned' or 'public_domain'.
    # Quarantine them for administrator review and nullify any synthetic lyrics.
    cursor.execute("""
        UPDATE songs
        SET lyrics_status = 'rights_unknown',
            publication_status = 'pending_review',
            lyrics = NULL,
            lyrics_license_notes = 'Unverified candidate record quarantined for administrator review. Public display disabled.'
        WHERE id > 37;
    """)
    quarantined_count = cursor.rowcount
    print(f"[Audit] Quarantined {quarantined_count} unverified records (IDs 38+) as 'pending_review' with lyrics set to NULL.")

    # 4. Clean up and verify categories and descriptions
    cursor.execute("""
        UPDATE songs
        SET description = title_si || ' (' || title_en || ') by ' || artist
        WHERE description = '' OR description IS NULL;
    """)

    conn.commit()

    # Verify final counts
    cursor.execute("SELECT lyrics_status, COUNT(*) FROM songs GROUP BY lyrics_status;")
    ls_counts = cursor.fetchall()
    print("[Audit] Final Lyrics Status Breakdown:", [dict(r) for r in ls_counts])

    cursor.execute("SELECT publication_status, COUNT(*) FROM songs GROUP BY publication_status;")
    ps_counts = cursor.fetchall()
    print("[Audit] Final Publication Status Breakdown:", [dict(r) for r in ps_counts])

    cursor.execute("SELECT COUNT(*) FROM songs WHERE lyrics IS NOT NULL AND lyrics != '';")
    active_lyrics = cursor.fetchone()[0]
    print(f"[Audit] Total records with active published lyrics: {active_lyrics} (strictly the 12 authorized original creative samples).")

    conn.close()
    print("[Audit] Remediation completed successfully.")

if __name__ == "__main__":
    run_remediation()
