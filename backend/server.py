# -*- coding: utf-8 -*-
"""
VerseNest Originals - Production API Server
Built with FastAPI. Delivers high performance, JWT security, advanced search,
lyrics rights enforcement, legal discovery scheduler, and SEO sitemaps.
"""
import os
import json
import uuid
import time
import hmac
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Depends, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import get_db_connection, init_db
from deduplication import normalize_sinhala_text, normalize_english_text, evaluate_song_duplicate
from search_engine import search_songs, get_search_suggestions
from discovery import run_discovery_pipeline

# Initialize database schema
init_db()

app = FastAPI(
    title="VerseNest Originals API",
    description="Modern, scalable Sinhala songs and lyrics platform API",
    version="2.0.0"
)

# Enable CORS for cross-origin integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

JWT_SECRET = os.environ.get("VERSENEST_SECRET_KEY", "versenest-super-secret-key-2026-production")
ADMIN_USERNAME = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASS", "versenest2026")

def generate_admin_token() -> str:
    """Generates a simple signed HMAC admin bearer token valid for 24 hours."""
    expiry = int(time.time()) + (24 * 3600)
    msg = f"{ADMIN_USERNAME}:{expiry}"
    sig = hmac.new(JWT_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()
    return f"{msg}:{sig}"

def verify_admin_token(token: Optional[str]) -> bool:
    """Verifies HMAC signature and token expiration."""
    if not token:
        return False
    parts = token.split(":")
    if len(parts) != 3:
        return False
    username, expiry_str, sig = parts
    try:
        expiry = int(expiry_str)
        if time.time() > expiry:
            return False
        expected = hmac.new(JWT_SECRET.encode(), f"{username}:{expiry}".encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(sig, expected)
    except Exception:
        return False

def get_current_admin(request: Request):
    """Dependency that ensures request has valid admin credentials."""
    auth_header = request.headers.get("Authorization", "")
    token = None
    if auth_header.startswith("Bearer "):
        token = auth_header[7:].strip()
    if not verify_admin_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication required. Please log in."
        )
    return ADMIN_USERNAME

# Pydantic Request Models
class LoginRequest(BaseModel):
    username: str
    password: str

class SongCreateUpdateRequest(BaseModel):
    title_si: str
    title_en: str
    artist: str
    singers: Optional[List[str]] = None
    lyricist: Optional[str] = ""
    composer: Optional[str] = ""
    album_or_movie: Optional[str] = ""
    release_year: Optional[int] = None
    era_decade: Optional[str] = ""
    genre: Optional[str] = "Pop"
    song_type: Optional[str] = "Original"
    youtube_url: Optional[str] = ""
    audio_url: Optional[str] = ""
    lyrics: Optional[str] = None
    lyrics_status: Optional[str] = "rights_unknown"
    lyrics_license_notes: Optional[str] = ""
    lyrics_evidence: Optional[str] = ""
    description: Optional[str] = ""
    editorial_commentary: Optional[str] = ""
    categories: Optional[List[str]] = None
    is_classic: Optional[bool] = False
    is_recent: Optional[bool] = False
    publication_status: Optional[str] = "published"

class CopyrightClaimRequest(BaseModel):
    song_id: int
    claimant_name: str
    claimant_email: str
    relationship: str
    claim_details: str
    evidence_url: Optional[str] = ""

# ==================== PUBLIC API ENDPOINTS ====================

@app.get("/api/songs")
def api_get_songs(
    q: Optional[str] = Query(None, description="Search keyword in Sinhala, English, or Romanized"),
    genre: Optional[str] = Query("All"),
    decade: Optional[str] = Query("All"),
    category: Optional[str] = Query("All"),
    artist: Optional[str] = Query("All"),
    lyrics_status: Optional[str] = Query("All"),
    sort_by: Optional[str] = Query("relevance"),
    page: int = Query(1, ge=1),
    page_size: int = Query(24, ge=1, le=100)
):
    """Retrieves paginated songs matching search query and filters."""
    return search_songs(
        query=q,
        genre=genre,
        decade=decade,
        category=category,
        artist=artist,
        lyrics_status=lyrics_status,
        sort_by=sort_by,
        page=page,
        page_size=page_size
    )

@app.get("/api/songs/{song_id}")
def api_get_song_details(song_id: int):
    """
    Fetches full metadata and lyrics for a published song.
    Enforces strict lyrics rights management: only serves full lyrics if rights are authorized!
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Increment view count
    cursor.execute("UPDATE songs SET view_count = view_count + 1 WHERE id = ?;", (song_id,))
    conn.commit()

    cursor.execute("""
        SELECT * FROM songs WHERE id = ? AND publication_status = 'published';
    """, (song_id,))
    song = cursor.fetchone()

    if not song:
        conn.close()
        raise HTTPException(status_code=404, detail="Song not found or not published.")

    # Apply Lyrics Rights Management Rule
    # Permitted lyrics states: 'original_owned', 'permission_granted', 'public_domain', 'licensed_attribution'
    can_publish_lyrics = song["lyrics_status"] in (
        "original_owned", "permission_granted", "public_domain", "licensed_attribution"
    )
    published_lyrics = song["lyrics"] if can_publish_lyrics else None
    rights_notice = (
        "Full lyrics authorized for publication." if can_publish_lyrics
        else "Full lyrics are currently unavailable pending verified publisher rights. Song metadata provided for educational discovery."
    )

    # Fetch Related Songs (by same artist or same genre)
    cursor.execute("""
        SELECT id, title_si, title_en, artist, genre, is_classic, is_recent, youtube_url
        FROM songs
        WHERE artist = ? AND id != ? AND publication_status = 'published'
        LIMIT 4;
    """, (song["artist"], song_id))
    same_artist_songs = [dict(r) for r in cursor.fetchall()]

    cursor.execute("""
        SELECT id, title_si, title_en, artist, genre, is_classic, is_recent, youtube_url
        FROM songs
        WHERE genre = ? AND artist != ? AND id != ? AND publication_status = 'published'
        LIMIT 4;
    """, (song["genre"], song["artist"], song_id))
    genre_related_songs = [dict(r) for r in cursor.fetchall()]

    result = {
        "id": song["id"],
        "song_uuid": song["song_uuid"],
        "title_si": song["title_si"],
        "title_en": song["title_en"],
        "alternative_titles": json.loads(song["alternative_titles"] or "[]"),
        "artist": song["artist"],
        "singers": json.loads(song["singers"] or "[]"),
        "lyricist": song["lyricist"],
        "composer": song["composer"],
        "album_or_movie": song["album_or_movie"],
        "release_year": song["release_year"],
        "era_decade": song["era_decade"],
        "genre": song["genre"],
        "song_type": song["song_type"],
        "youtube_url": song["youtube_url"],
        "audio_url": song["audio_url"],
        "source_url": song["source_url"],
        "isrc": song["isrc"],
        "musicbrainz_id": song["musicbrainz_id"],
        "can_publish_lyrics": can_publish_lyrics,
        "lyrics": published_lyrics,
        "lyrics_status": song["lyrics_status"],
        "lyrics_license_notes": song["lyrics_license_notes"],
        "lyrics_evidence": song["lyrics_evidence"],
        "rights_notice": rights_notice,
        "description": song["description"],
        "editorial_commentary": song["editorial_commentary"],
        "categories": json.loads(song["categories"] or "[]"),
        "is_classic": bool(song["is_classic"]),
        "is_recent": bool(song["is_recent"]),
        "view_count": song["view_count"],
        "same_artist_songs": same_artist_songs,
        "genre_related_songs": genre_related_songs,
        "created_at": song["created_at"],
        "updated_at": song["updated_at"]
    }
    conn.close()
    return result

@app.get("/api/search/suggestions")
def api_get_suggestions(q: str = Query(..., min_length=2)):
    """Returns fast autocomplete search suggestions."""
    return get_search_suggestions(q, limit=8)

@app.get("/api/stats")
def api_get_platform_stats():
    """Returns verified platform song catalogue statistics."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published';")
    total_songs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT artist) FROM songs WHERE publication_status = 'published';")
    total_artists = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM songs WHERE is_classic = 1;")
    total_classics = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM songs WHERE is_recent = 1;")
    total_recent = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM songs WHERE lyrics_status IN ('original_owned', 'permission_granted');")
    total_authorized_lyrics = cursor.fetchone()[0]

    conn.close()
    return {
        "total_songs": total_songs,
        "total_artists": total_artists,
        "total_classics": total_classics,
        "total_recent": total_recent,
        "total_authorized_lyrics": total_authorized_lyrics
    }

@app.get("/api/genres")
def api_get_genres():
    """Lists distinct genres with song counts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT genre, COUNT(*) as count 
        FROM songs 
        WHERE publication_status = 'published' AND genre != ''
        GROUP BY genre 
        ORDER BY count DESC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"genre": r["genre"], "count": r["count"]} for r in rows]

@app.get("/api/decades")
def api_get_decades():
    """Lists all available decades with counts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT era_decade, COUNT(*) as count 
        FROM songs 
        WHERE publication_status = 'published' AND era_decade != ''
        GROUP BY era_decade 
        ORDER BY era_decade ASC;
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"decade": r["era_decade"], "count": r["count"]} for r in rows]

@app.get("/api/artists/trending")
def api_get_trending_artists(limit: int = 12):
    """Retrieves prominent artists with song counts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT artist, COUNT(*) as song_count, SUM(view_count) as total_views
        FROM songs
        WHERE publication_status = 'published'
        GROUP BY artist
        ORDER BY total_views DESC, song_count DESC
        LIMIT ?;
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [{"artist": r["artist"], "song_count": r["song_count"], "views": r["total_views"]} for r in rows]

@app.post("/api/copyright/report")
def api_submit_copyright_claim(claim: CopyrightClaimRequest):
    """Permits copyright owners to submit rapid takedown or permission notices."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO copyright_requests (
            song_id, claimant_name, claimant_email, relationship, claim_details, evidence_url, status
        ) VALUES (?, ?, ?, ?, ?, ?, 'open');
    """, (
        claim.song_id,
        claim.claimant_name.strip(),
        claim.claimant_email.strip(),
        claim.relationship.strip(),
        claim.claim_details.strip(),
        claim.evidence_url.strip()
    ))
    conn.commit()
    req_id = cursor.lastrowid
    conn.close()
    return {
        "status": "success",
        "message": "Copyright notice registered. Our editorial review team will act upon verified complaints.",
        "request_id": req_id
    }

# ==================== ADMIN DASHBOARD API ====================

@app.post("/api/admin/login")
def api_admin_login(cred: LoginRequest):
    """Admin login returning secure signed token."""
    if cred.username == ADMIN_USERNAME and cred.password == ADMIN_PASSWORD:
        token = generate_admin_token()
        return {
            "status": "success",
            "token": token,
            "username": ADMIN_USERNAME,
            "message": "Authentication successful"
        }
    raise HTTPException(status_code=401, detail="Invalid username or password.")

@app.get("/api/admin/dashboard-stats")
def api_admin_dashboard_stats(admin: str = Depends(get_current_admin)):
    """Full operational statistics for administrator dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM songs;")
    total_songs = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM duplicates_review WHERE status = 'pending';")
    pending_duplicates = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM copyright_requests WHERE status = 'open';")
    open_copyright_claims = cursor.fetchone()[0]

    cursor.execute("SELECT lyrics_status, COUNT(*) FROM songs GROUP BY lyrics_status;")
    lyrics_breakdown = {r[0]: r[1] for r in cursor.fetchall()}

    cursor.execute("""
        SELECT * FROM import_history ORDER BY id DESC LIMIT 5;
    """)
    recent_imports = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total_songs": total_songs,
        "pending_duplicates": pending_duplicates,
        "open_copyright_claims": open_copyright_claims,
        "lyrics_breakdown": lyrics_breakdown,
        "recent_imports": recent_imports
    }

@app.post("/api/admin/songs")
def api_admin_create_song(song: SongCreateUpdateRequest, admin: str = Depends(get_current_admin)):
    """Creates a new song record with duplicate prevention."""
    conn = get_db_connection()
    candidate_dict = song.dict()
    dup_res = evaluate_song_duplicate(candidate_dict, conn)
    
    if dup_res.action in ("skip", "update_metadata"):
        conn.close()
        raise HTTPException(
            status_code=409,
            detail=f"Duplicate song detected (Score: {dup_res.score}). Existing song ID: {dup_res.existing_song_id}."
        )

    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO songs (
        song_uuid, title_si, title_en, normalized_title_si, normalized_title_en,
        alternative_titles, artist, normalized_artist, singers, lyricist, composer,
        album_or_movie, release_year, era_decade, genre, song_type, youtube_url,
        audio_url, source_url, isrc, musicbrainz_id, lyrics, lyrics_status,
        lyrics_license_notes, lyrics_evidence, description, editorial_commentary,
        categories, is_classic, is_recent, publication_status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        str(uuid.uuid4()),
        song.title_si,
        song.title_en,
        normalize_sinhala_text(song.title_si),
        normalize_english_text(song.title_en),
        json.dumps([]),
        song.artist,
        normalize_english_text(song.artist),
        json.dumps(song.singers or [song.artist]),
        song.lyricist or "",
        song.composer or "",
        song.album_or_movie or "",
        song.release_year,
        song.era_decade or "",
        song.genre or "Pop",
        song.song_type or "Original",
        song.youtube_url or "",
        song.audio_url or "",
        "",
        "",
        "",
        song.lyrics,
        song.lyrics_status,
        song.lyrics_license_notes or "",
        song.lyrics_evidence or "",
        song.description or "",
        song.editorial_commentary or "",
        json.dumps(song.categories or ["Pop songs"]),
        1 if song.is_classic else 0,
        1 if song.is_recent else 0,
        song.publication_status
    ))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"status": "success", "song_id": new_id, "message": "Song created successfully."}

@app.put("/api/admin/songs/{song_id}")
def api_admin_update_song(song_id: int, song: SongCreateUpdateRequest, admin: str = Depends(get_current_admin)):
    """Updates an existing song metadata and copyright permissions."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE songs SET
        title_si = ?,
        title_en = ?,
        normalized_title_si = ?,
        normalized_title_en = ?,
        artist = ?,
        normalized_artist = ?,
        lyricist = ?,
        composer = ?,
        album_or_movie = ?,
        release_year = ?,
        era_decade = ?,
        genre = ?,
        song_type = ?,
        youtube_url = ?,
        audio_url = ?,
        lyrics = ?,
        lyrics_status = ?,
        lyrics_license_notes = ?,
        lyrics_evidence = ?,
        description = ?,
        editorial_commentary = ?,
        is_classic = ?,
        is_recent = ?,
        publication_status = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?;
    """, (
        song.title_si,
        song.title_en,
        normalize_sinhala_text(song.title_si),
        normalize_english_text(song.title_en),
        song.artist,
        normalize_english_text(song.artist),
        song.lyricist,
        song.composer,
        song.album_or_movie,
        song.release_year,
        song.era_decade,
        song.genre,
        song.song_type,
        song.youtube_url,
        song.audio_url,
        song.lyrics,
        song.lyrics_status,
        song.lyrics_license_notes,
        song.lyrics_evidence,
        song.description,
        song.editorial_commentary,
        1 if song.is_classic else 0,
        1 if song.is_recent else 0,
        song.publication_status,
        song_id
    ))
    conn.commit()
    conn.close()
    return {"status": "success", "song_id": song_id, "message": "Song updated successfully."}

@app.delete("/api/admin/songs/{song_id}")
def api_admin_delete_song(song_id: int, admin: str = Depends(get_current_admin)):
    """Unpublishes or deletes a song from the catalogue."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE songs SET publication_status = 'unlisted' WHERE id = ?;", (song_id,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Song {song_id} unlisted successfully."}

@app.get("/api/admin/duplicates")
def api_admin_get_duplicates(admin: str = Depends(get_current_admin)):
    """Lists songs flagged for duplicate review."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT d.id, d.candidate_json, d.existing_song_id, d.similarity_score, d.match_reasons, d.status,
               s.title_si as existing_title_si, s.title_en as existing_title_en, s.artist as existing_artist
        FROM duplicates_review d
        LEFT JOIN songs s ON d.existing_song_id = s.id
        WHERE d.status = 'pending'
        ORDER BY d.id DESC;
    """)
    rows = cursor.fetchall()
    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "candidate": json.loads(r["candidate_json"]),
            "existing_song": {
                "id": r["existing_song_id"],
                "title_si": r["existing_title_si"],
                "title_en": r["existing_title_en"],
                "artist": r["existing_artist"]
            },
            "similarity_score": r["similarity_score"],
            "match_reasons": r["match_reasons"]
        })
    conn.close()
    return results

@app.post("/api/admin/duplicates/{review_id}/action")
def api_admin_resolve_duplicate(review_id: int, action: str = Query(..., pattern="^(merge|dismiss|insert_distinct)$"), admin: str = Depends(get_current_admin)):
    """Resolves duplicate review: merges, dismisses, or inserts as distinct song."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM duplicates_review WHERE id = ?;", (review_id,))
    review = cursor.fetchone()
    if not review:
        conn.close()
        raise HTTPException(status_code=404, detail="Duplicate review record not found.")

    candidate = json.loads(review["candidate_json"])

    if action == "insert_distinct":
        cursor.execute("""
        INSERT INTO songs (
            song_uuid, title_si, title_en, normalized_title_si, normalized_title_en,
            alternative_titles, artist, normalized_artist, singers, lyricist, composer,
            release_year, genre, lyrics_status, publication_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'rights_unknown', 'published');
        """, (
            str(uuid.uuid4()),
            candidate["title_si"],
            candidate["title_en"],
            normalize_sinhala_text(candidate["title_si"]),
            normalize_english_text(candidate["title_en"]),
            json.dumps([]),
            candidate["artist"],
            normalize_english_text(candidate["artist"]),
            json.dumps([candidate["artist"]]),
            candidate.get("lyricist", ""),
            candidate.get("composer", ""),
            candidate.get("release_year", 2020),
            candidate.get("genre", "Pop")
        ))
        cursor.execute("UPDATE duplicates_review SET status = 'inserted_distinct', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?;", (admin, review_id))

    elif action == "merge":
        # Merge missing ISRC/MBID into existing song
        existing_id = review["existing_song_id"]
        cursor.execute("""
            UPDATE songs
            SET isrc = COALESCE(NULLIF(isrc, ''), ?),
                musicbrainz_id = COALESCE(NULLIF(musicbrainz_id, ''), ?),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?;
        """, (candidate.get("isrc", ""), candidate.get("musicbrainz_id", ""), existing_id))
        cursor.execute("UPDATE duplicates_review SET status = 'merged', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?;", (admin, review_id))

    elif action == "dismiss":
        cursor.execute("UPDATE duplicates_review SET status = 'dismissed', reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP WHERE id = ?;", (admin, review_id))

    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Duplicate review resolved with action '{action}'."}

@app.post("/api/admin/discovery/trigger")
def api_admin_trigger_discovery(max_artists: int = Query(2, ge=1, le=10), admin: str = Depends(get_current_admin)):
    """Triggers legal automated song discovery scan."""
    report = run_discovery_pipeline(source_name="Admin Triggered Scan", max_artists=max_artists)
    return {"status": "success", "report": report}

@app.get("/api/admin/copyright/requests")
def api_admin_get_copyright_requests(admin: str = Depends(get_current_admin)):
    """Lists copyright and takedown requests."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.*, s.title_si, s.artist 
        FROM copyright_requests c
        LEFT JOIN songs s ON c.song_id = s.id
        ORDER BY c.id DESC;
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows

@app.post("/api/admin/copyright/requests/{claim_id}/resolve")
def api_admin_resolve_copyright_claim(claim_id: int, action: str = Query(..., pattern="^(remove_lyrics|dismiss)$"), notes: str = Query(""), admin: str = Depends(get_current_admin)):
    """Resolves copyright complaint with 1-click lyrics removal."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT song_id FROM copyright_requests WHERE id = ?;", (claim_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Claim not found.")

    song_id = row[0]
    if action == "remove_lyrics":
        # Instantly remove lyrics and set status to permission_rejected
        cursor.execute("""
            UPDATE songs 
            SET lyrics = NULL, 
                lyrics_status = 'permission_rejected',
                lyrics_license_notes = 'Lyrics removed following copyright complaint.'
            WHERE id = ?;
        """, (song_id,))
        cursor.execute("""
            UPDATE copyright_requests 
            SET status = 'lyrics_removed', action_notes = ?, resolved_at = CURRENT_TIMESTAMP 
            WHERE id = ?;
        """, (notes or "Lyrics unpublished under rights request.", claim_id))
    else:
        cursor.execute("""
            UPDATE copyright_requests 
            SET status = 'dismissed', action_notes = ?, resolved_at = CURRENT_TIMESTAMP 
            WHERE id = ?;
        """, (notes or "Claim dismissed after verification.", claim_id))

    conn.commit()
    conn.close()
    return {"status": "success", "message": f"Claim resolved with action: {action}"}

@app.get("/api/admin/export")
def api_admin_export_database(admin: str = Depends(get_current_admin)):
    """Exports song catalogue as JSON for backup."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM songs;")
    songs = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"exported_at": datetime.utcnow().isoformat(), "total": len(songs), "songs": songs}

# ==================== SEO & STATIC SITEMAP ====================

@app.get("/sitemap.xml", response_class=Response)
def api_sitemap():
    """Generates dynamic XML sitemap for SEO and Google Search Console."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, updated_at FROM songs WHERE publication_status = 'published';")
    songs = cursor.fetchall()
    conn.close()

    base_url = "https://versenest.org"
    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]
    # Static pages
    for page in ["", "sinhala.html", "about.html", "contact.html", "copyright.html", "privacy.html", "terms.html"]:
        xml_lines.append(f'  <url><loc>{base_url}/{page}</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>')

    # Individual Song Pages
    for s in songs:
        date_str = str(s["updated_at"])[:10] if s["updated_at"] else "2026-11-16"
        xml_lines.append(f'  <url><loc>{base_url}/lyrics/sinhala-song.html?song={s["id"]}</loc><lastmod>{date_str}</lastmod><priority>0.7</priority></url>')

    xml_lines.append('</urlset>')
    return Response(content="\n".join(xml_lines), media_type="application/xml")

# Mount Static Files (Serving index.html, sinhala.html, assets, lyrics, etc.)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/assets", StaticFiles(directory=os.path.join(BASE_DIR, "assets")), name="assets")
app.mount("/guides", StaticFiles(directory=os.path.join(BASE_DIR, "guides")), name="guides")
app.mount("/lyrics", StaticFiles(directory=os.path.join(BASE_DIR, "lyrics")), name="lyrics")
app.mount("/data", StaticFiles(directory=os.path.join(BASE_DIR, "data")), name="data")

# Route root static HTML pages
@app.get("/")
def serve_home():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/index.html")
def serve_index():
    return FileResponse(os.path.join(BASE_DIR, "index.html"))

@app.get("/sinhala.html")
def serve_sinhala():
    return FileResponse(os.path.join(BASE_DIR, "sinhala.html"))

@app.get("/about.html")
def serve_about():
    return FileResponse(os.path.join(BASE_DIR, "about.html"))

@app.get("/contact.html")
def serve_contact():
    return FileResponse(os.path.join(BASE_DIR, "contact.html"))

@app.get("/copyright.html")
def serve_copyright():
    return FileResponse(os.path.join(BASE_DIR, "copyright.html"))

@app.get("/privacy.html")
def serve_privacy():
    return FileResponse(os.path.join(BASE_DIR, "privacy.html"))

@app.get("/terms.html")
def serve_terms():
    return FileResponse(os.path.join(BASE_DIR, "terms.html"))

@app.get("/admin")
@app.get("/admin.html")
def serve_admin():
    return FileResponse(os.path.join(BASE_DIR, "admin.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=False)
