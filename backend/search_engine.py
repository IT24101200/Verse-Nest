# -*- coding: utf-8 -*-
"""
VerseNest Originals - Advanced Sinhala & English Search Engine (Audited & Fixed)
Supports bi-directional Sinhala Unicode and Romanized English transliteration,
strict term validation (no empty wildcard matching), relevance scoring, and accurate pagination.
"""
import re
import unicodedata
from typing import Dict, Any, List, Optional
from database import get_db_connection
from deduplication import normalize_sinhala_text, normalize_english_text

# Romanized to Sinhala phonetic mappings
ROMAN_TO_SINHALA = {
    "sanda": "සඳ",
    "sandawathiye": "සඳවතියේ",
    "sandakada": "සඳකඩ",
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
    "rookantha": "රූකාන්ත",
    "neela": "නීලා",
    "dhanith": "ධනිත්",
    "dinesh": "දිනේෂ්",
    "yohani": "යොහානි",
    "supun": "සුපුන්",
    "kasun": "කසුන්",
    "bathiya": "භාතිය",
    "santhush": "සන්තුෂ්",
    "sannaliyane": "සන්නාලියනේ"
}

# Reverse mapping: Sinhala to Romanized
SINHALA_TO_ROMAN = {v: k for k, v in ROMAN_TO_SINHALA.items()}

def has_sinhala_characters(text: str) -> bool:
    """Detects if string contains Sinhala Unicode code points (\u0D80-\u0DFF)."""
    return any('\u0D80' <= c <= '\u0DFF' for c in text)

def expand_search_terms(query: str) -> List[str]:
    """
    Expands search query into clean, non-empty search terms.
    Preserves Sinhala Unicode and expands Romanized English phonetically.
    """
    if not query or not query.strip():
        return []

    terms = set()
    raw_query = query.strip()

    if has_sinhala_characters(raw_query):
        # 1. Sinhala input path
        norm_si = normalize_sinhala_text(raw_query)
        if norm_si:
            terms.add(norm_si)
            for w in norm_si.split():
                if len(w) >= 2:
                    terms.add(w)
                    # Check reverse romanization
                    if w in SINHALA_TO_ROMAN:
                        terms.add(SINHALA_TO_ROMAN[w])
    else:
        # 2. English / Romanized input path
        norm_en = normalize_english_text(raw_query)
        if norm_en:
            terms.add(norm_en)
            words = norm_en.split()
            for w in words:
                if len(w) >= 2:
                    terms.add(w)
                    # Check roman to sinhala phonetic map
                    for r_prefix, s_val in ROMAN_TO_SINHALA.items():
                        if w == r_prefix or w.startswith(r_prefix):
                            terms.add(s_val)

    # Filter out empty or whitespace-only terms to prevent '%%' wildcard runaway
    clean_terms = [t for t in terms if t and len(t.strip()) >= 2 or (len(t.strip()) >= 1 and has_sinhala_characters(t))]
    return sorted(list(clean_terms), key=lambda x: -len(x))

# Alias for backward compatibility
expand_transliterated_terms = expand_search_terms


def search_songs(
    query: Optional[str] = None,
    genre: Optional[str] = None,
    decade: Optional[str] = None,
    category: Optional[str] = None,
    artist: Optional[str] = None,
    lyrics_status: Optional[str] = None,
    include_quarantined: bool = False,
    sort_by: str = "relevance",  # "relevance", "popular", "newest", "year", "title"
    page: int = 1,
    page_size: int = 24
) -> Dict[str, Any]:
    """
    Executes search with strict term expansion, relevance ranking, and publication filtering.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    conditions = []
    params = []

    # Unless admin explicitly requests quarantined records, search published only!
    if not include_quarantined:
        conditions.append("publication_status = 'published'")

    search_terms = expand_search_terms(query) if query else []

    if search_terms:
        term_subclauses = []
        for term in search_terms:
            like_val = f"%{term}%"
            term_subclauses.append("""
                (normalized_title_si LIKE ? OR normalized_title_en LIKE ? 
                 OR normalized_artist LIKE ? OR lyricist LIKE ? 
                 OR composer LIKE ? OR album_or_movie LIKE ? OR artist LIKE ?)
            """)
            params.extend([like_val, like_val, like_val, like_val, like_val, like_val, like_val])

        conditions.append(f"({' OR '.join(term_subclauses)})")

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

    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    # Count matching records
    count_sql = f"SELECT COUNT(*) FROM songs {where_clause};"
    cursor.execute(count_sql, params)
    total_count = cursor.fetchone()[0]

    # Order by clause
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
               youtube_url, lyrics_status, publication_status, is_classic, is_recent, view_count,
               categories, description
        FROM songs
        {where_clause}
        {order_clause}
        LIMIT ? OFFSET ?;
    """
    fetch_params = list(params)
    fetch_params.extend([page_size, offset])
    cursor.execute(fetch_sql, fetch_params)
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
            "publication_status": r["publication_status"],
            "is_classic": bool(r["is_classic"]),
            "is_recent": bool(r["is_recent"]),
            "view_count": r["view_count"],
            "description": r["description"]
        })

    conn.close()
    total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1

    return {
        "query": query,
        "search_terms_used": search_terms,
        "page": page,
        "page_size": page_size,
        "total_count": total_count,
        "total_pages": total_pages,
        "songs": results
    }

def get_search_suggestions(query: str, limit: int = 8) -> List[Dict[str, str]]:
    """Returns fast autocomplete suggestions for published songs."""
    if not query or len(query.strip()) < 2:
        return []

    terms = expand_search_terms(query)
    if not terms:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    
    suggestions = []
    seen = set()

    for term in terms:
        like_term = f"%{term}%"
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
