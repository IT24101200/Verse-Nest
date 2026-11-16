# -*- coding: utf-8 -*-
"""
VerseNest Originals - Database Engine & Schema
Production-ready SQLite implementation with WAL mode, indices, and schema migrations.
"""
import sqlite3
import os
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "versenest.db")

def get_db_connection() -> sqlite3.Connection:
    """Creates a thread-safe connection to the SQLite database with WAL mode."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for high concurrency
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA busy_timeout = 30000;")
    return conn

def init_db():
    """Initializes database tables, indices, and default configurations."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Songs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_uuid TEXT UNIQUE NOT NULL,
        title_si TEXT NOT NULL,
        title_en TEXT NOT NULL,
        normalized_title_si TEXT NOT NULL,
        normalized_title_en TEXT NOT NULL,
        alternative_titles TEXT DEFAULT '[]',
        artist TEXT NOT NULL,
        normalized_artist TEXT NOT NULL,
        singers TEXT DEFAULT '[]',
        lyricist TEXT DEFAULT '',
        composer TEXT DEFAULT '',
        album_or_movie TEXT DEFAULT '',
        release_year INTEGER,
        era_decade TEXT DEFAULT '',
        genre TEXT DEFAULT 'Pop',
        song_type TEXT DEFAULT 'Original',
        youtube_url TEXT DEFAULT '',
        audio_url TEXT DEFAULT '',
        source_url TEXT DEFAULT '',
        isrc TEXT DEFAULT '',
        musicbrainz_id TEXT DEFAULT '',
        lyrics TEXT,
        lyrics_status TEXT NOT NULL DEFAULT 'rights_unknown',
        lyrics_license_notes TEXT DEFAULT '',
        lyrics_evidence TEXT DEFAULT '',
        description TEXT DEFAULT '',
        editorial_commentary TEXT DEFAULT '',
        categories TEXT DEFAULT '[]',
        is_classic BOOLEAN DEFAULT 0,
        is_recent BOOLEAN DEFAULT 0,
        publication_status TEXT DEFAULT 'published',
        view_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Indices for blazing fast search & filtering
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_title_si ON songs(normalized_title_si);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_title_en ON songs(normalized_title_en);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(normalized_artist);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_decade ON songs(era_decade);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_isrc ON songs(isrc);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_mbid ON songs(musicbrainz_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_pub_status ON songs(publication_status);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_songs_lyrics_status ON songs(lyrics_status);")

    # 2. Duplicates Review Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS duplicates_review (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_json TEXT NOT NULL,
        existing_song_id INTEGER,
        similarity_score REAL NOT NULL,
        match_reasons TEXT NOT NULL,
        status TEXT DEFAULT 'pending', -- 'pending', 'merged', 'dismissed', 'inserted_as_distinct'
        reviewed_by TEXT DEFAULT '',
        reviewed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(existing_song_id) REFERENCES songs(id) ON DELETE SET NULL
    );
    """)

    # 3. Import History Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS import_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_name TEXT NOT NULL,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        total_candidates INTEGER DEFAULT 0,
        imported_count INTEGER DEFAULT 0,
        updated_count INTEGER DEFAULT 0,
        duplicates_skipped INTEGER DEFAULT 0,
        review_queued INTEGER DEFAULT 0,
        errors_count INTEGER DEFAULT 0,
        status TEXT DEFAULT 'running', -- 'running', 'completed', 'failed'
        summary_details TEXT DEFAULT '{}'
    );
    """)

    # 4. Copyright Requests / Takedowns Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS copyright_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        song_id INTEGER,
        claimant_name TEXT NOT NULL,
        claimant_email TEXT NOT NULL,
        relationship TEXT NOT NULL,
        claim_details TEXT NOT NULL,
        evidence_url TEXT DEFAULT '',
        status TEXT DEFAULT 'open', -- 'open', 'lyrics_removed', 'dismissed'
        action_notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        FOREIGN KEY(song_id) REFERENCES songs(id) ON DELETE SET NULL
    );
    """)

    # 5. Admin Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully at:", DB_PATH)
