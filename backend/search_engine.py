# -*- coding: utf-8 -*-
"""
VerseNest Originals - Advanced Sinhala & English Search Engine
Provides phonetic transliteration search, spelling-tolerant matching,
multi-criteria filtering, instant suggestions, and ranked relevance scoring.
"""
import re
from typing import Dict, Any, List, Optional
from database import get_db_connection
from deduplication import normalize_sinhala_text, normalize_english_text

# Common Romanized to Sinhala phonetic prefixes and roots
ROMAN_TO_SINHALA_PREFIXES = {
    "sanda": "සඳ",
    "adare": "ආදරේ",
    "adara": "ආදර",
    "oba": "ඔබ",
    "mal": "මල්",
    "wassa": "වැස්ස",
    "sulanga": "සුළඟ",
    "tharu": "තරු",
    "raa": "රෑ",
    "ra": "රෑ",
    "sihine": "සිහිනේ",
    "heene": "හීනේ",
    "mathaka": "මතක",
    "hadawatha": "හදවත",
    "manike": "මැණිකේ",
    "surangani": "සුරංගනී",
    "dawas": "දවස්",
    "kelle": "කෙල්ලේ",
    "nadiya": "නාඩිය",
    "galana": "ගලන",
    "ganga": "ගඟ",
    "seetha": "සීත",
    "lanwee": "ළංවී",
    "amaradeva": "අමරදේව",
    "jothipala": "ජෝතිපාල",
    "clarence": "ක්ලැරන්ස්",
    "kapuge": "කපුගේ",
    "edward": "එඩ්වඩ්",
    "sunil": "සුනිල්",
    "victor": "වික්ටර්",
    "rookantha": "රූකාන්ත"
}

def expand_transliterated_terms(query: str) -> List[str]:
    """Expands Romanized English input to include corresponding Sinhala phonetic forms."""
    normalized_q = normalize_english_text(query)
    expanded = [normalized_q]
    
    # Check words against transliteration table
    words = normalized_q.split()
    matched_si = []
    for w in words:
        for rom_prefix, si_equiv in ROMAN_TO_SINHALA_PREFIXES.items():
            if w.startswith(rom_prefix):
                matched_si.append(si_equiv)
                break
    
    if matched_si:
        expanded.append(" ".join(matched_si))
        for m in matched_si:
            expanded.append(m)

    return list(set(expanded))

def search_songs(
    query: Optional[str] = None,
    genre: Optional[str] = None,
    decade: Optional[str] = None,
    category: Optional[str] = None,
    artist: Optional[str] = None,
    lyrics_status: Optional[str] = None,
    sort_by: str = "relevance",  # "relevance", "popular", "newest", "year", "title"
    page: int = 1,
    page_size: int = 24
) -> Dict[str, Any]:
    """
    Executes advanced search query with ranking, filtering, and pagination.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = ["publication_status = 'published'"]
    params = []

    if query and query.strip():
        search_terms = expand_transliterated_terms(query)
        term_conditions = []
        for term in search_terms:
            like_val = f"%{term}%"
            term_conditions.append("""
                (normalized_title_si LIKE ? OR normalized_title_en LIKE ? 
                 OR normalized_artist LIKE ? OR lyricist LIKE ? 
                 OR composer LIKE ? OR album_or_movie LIKE ?)
            """)
            params.extend([like_val, like_val, like_val, like_val, like_val, like_val])
        
        conditions.append(f"({' OR '.join(term_conditions)})")

    if genre and genre != "All":
        conditions.append("genre = ?")
        params.append(genre)

    if decade and decade != "All":
        conditions.append("era_decade = ?")
        params.append(decade)

    if category and category != "All":
        conditions.append("categories LIKE ?")
        params.append(f"%{category}%")

    if artist and artist != "All":
        conditions.append("(artist = ? OR normalized_artist LIKE ?)")
        params.extend([artist, f"%{normalize_english_text(artist)}%"])

    if lyrics_status and lyrics_status != "All":
        conditions.append("lyrics_status = ?")
        params.append(lyrics_status)

    where_clause = " WHERE " + " AND ".join(conditions)

    # Count total matching rows
    count_sql = f"SELECT COUNT(*) FROM songs {where_clause};"
    cursor.execute(count_sql, params)
    total_count = cursor.fetchone()[0]

    # Order By Clause
    if sort_by == "popular":
        order_clause = "ORDER BY view_count DESC, id ASC"
    elif sort_by == "newest":
        order_clause = "ORDER BY id DESC"
    elif sort_by == "year":
        order_clause = "ORDER BY release_year DESC, title_si ASC"
    elif sort_by == "title":
        order_clause = "ORDER BY title_si ASC"
    else:  # relevance
        order_clause = "ORDER BY is_recent DESC, is_classic DESC, view_count DESC, id ASC"

    offset = (page - 1) * page_size
    fetch_sql = f"""
        SELECT id, song_uuid, title_si, title_en, artist, lyricist, composer,
               album_or_movie, release_year, era_decade, genre, song_type,
               youtube_url, lyrics_status, is_classic, is_recent, view_count,
               categories, description
        FROM songs
        {where_clause}
        {order_clause}
        LIMIT ? OFFSET ?;
    """
    params.extend([page_size, offset])
    cursor.execute(fetch_sql, params)
    rows = cursor.fetchall()

    results = []
    for r in rows:
        results.append({
            "id": r["id"],
            "song_uuid": r["song_uuid"],
            "title_si": r["title_si"],
            "title_en": r["title_en"],
            "artist": r["artist"],
            "lyricist": r["lyricist"],
            "composer": r["composer"],
            "album_or_movie": r["album_or_movie"],
            "release_year": r["release_year"],
            "era_decade": r["era_decade"],
            "genre": r["genre"],
            "song_type": r["song_type"],
            "youtube_url": r["youtube_url"],
            "lyrics_status": r["lyrics_status"],
            "is_classic": bool(r["is_classic"]),
            "is_recent": bool(r["is_recent"]),
            "view_count": r["view_count"],
            "description": r["description"]
        })

    conn.close()
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1

    return {
        "query": query,
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "songs": results
    }

def get_search_suggestions(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """Generates instant autocomplete search suggestions for input box."""
    if not query or len(query.strip()) < 2:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    terms = expand_transliterated_terms(query)
    
    suggestions = []
    seen = set()

    for term in terms:
        like_term = f"{term}%"
        cursor.execute("""
            SELECT id, title_si, title_en, artist, genre
            FROM songs
            WHERE (normalized_title_si LIKE ? OR normalized_title_en LIKE ? OR normalized_artist LIKE ?)
              AND publication_status = 'published'
            LIMIT ?;
        """, (like_term, like_term, like_term, limit))

        for row in cursor.fetchall():
            key = (row["title_si"], row["artist"])
            if key not in seen:
                seen.add(key)
                suggestions.append({
                    "id": str(row["id"]),
                    "title": f"{row['title_si']} ({row['title_en']})",
                    "artist": row["artist"],
                    "genre": row["genre"]
                })
            if len(suggestions) >= limit:
                break
        if len(suggestions) >= limit:
            break

    conn.close()
    return suggestions
