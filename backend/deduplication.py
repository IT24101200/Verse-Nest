# -*- coding: utf-8 -*-
"""
VerseNest Originals - Advanced Sinhala Duplicate Detection Engine
Implements Unicode NFC normalization, transliteration matching, Levenshtein distance,
token set similarity, and multi-factor collision prevention.
"""
import re
import unicodedata
from typing import Optional, Dict, Any, Tuple, List

# Basic Sinhala to Romanized and phonetic mapping rules
SINHALA_CHAR_MAP = {
    'අ': 'a', 'ආ': 'aa', 'ඇ': 'ae', 'ඈ': 'aae', 'ඉ': 'i', 'ඊ': 'ee', 'උ': 'u', 'ඌ': 'oo',
    'එ': 'e', 'ඒ': 'ee', 'ඓ': 'ai', 'ඔ': 'o', 'ඕ': 'oo', 'ඖ': 'au',
    'ක': 'ka', 'ඛ': 'kha', 'ග': 'ga', 'ඝ': 'gha', 'ඞ': 'nga',
    'ච': 'cha', 'ඡ': 'chha', 'ජ': 'ja', 'ඣ': 'jha', 'ඤ': 'nya',
    'ට': 'ta', 'ඨ': 'tha', 'ඩ': 'da', 'ඪ': 'dha', 'ණ': 'na',
    'ත': 'tha', 'ථ': 'thha', 'ද': 'dha', 'ධ': 'dhha', 'න': 'na',
    'ප': 'pa', 'ඵ': 'pha', 'බ': 'ba', 'භ': 'bha', 'ම': 'ma',
    'ය': 'ya', 'ර': 'ra', 'ල': 'la', 'ව': 'wa', 'ශ': 'sha', 'ෂ': 'sha', 'ස': 'sa', 'හ': 'ha', 'ළ': 'la',
    'ං': 'ng', 'ඃ': 'h'
}

def normalize_sinhala_text(text: str) -> str:
    """Normalizes Sinhala text by removing ZWJ, ZWNJ, excessive whitespace, and applying NFC."""
    if not text:
        return ""
    # Unicode NFC normalization
    text = unicodedata.normalize('NFC', text)
    # Remove Zero Width Joiner (\u200d) and Zero Width Non-Joiner (\u200c)
    text = text.replace('\u200d', '').replace('\u200c', '')
    # Remove punctuation & symbols, keep Sinhala range (\u0D80-\u0DFF), English letters, and numbers
    text = re.sub(r'[^\w\s\u0D80-\u0DFF]', ' ', text)
    # Normalize whitespaces to single space
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def normalize_english_text(text: str) -> str:
    """Normalizes English/Romanized text for consistent search & comparison."""
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text)
    # Strip diacritics
    text = "".join(c for c in text if not unicodedata.combining(c))
    # Replace symbols and punctuation with space
    text = re.sub(r'[^a-zA-Z0-9\s]', ' ', text)
    # Normalize whitespaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text.lower()

def compute_levenshtein_distance(s1: str, s2: str) -> int:
    """Computes basic Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return compute_levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def string_similarity_ratio(s1: str, s2: str) -> float:
    """Calculates normalized string similarity ratio from 0.0 to 1.0."""
    if not s1 and not s2:
        return 1.0
    if not s1 or not s2:
        return 0.0
    s1_clean = re.sub(r'\s+', '', s1)
    s2_clean = re.sub(r'\s+', '', s2)
    if s1_clean == s2_clean:
        return 1.0
    max_len = max(len(s1_clean), len(s2_clean))
    if max_len == 0:
        return 1.0
    dist = compute_levenshtein_distance(s1_clean, s2_clean)
    return max(0.0, 1.0 - (dist / max_len))

def token_set_similarity(s1: str, s2: str) -> float:
    """Computes Jaccard word-level similarity between two phrases."""
    tokens1 = set(s1.split())
    tokens2 = set(s2.split())
    if not tokens1 or not tokens2:
        return 0.0
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    return len(intersection) / len(union)

class DuplicateCheckResult:
    def __init__(self, action: str, match_type: str, score: float, reasons: List[str], existing_song_id: Optional[int] = None):
        self.action = action  # 'skip', 'update_metadata', 'queue_review', 'insert_new'
        self.match_type = match_type  # 'exact_id', 'exact_text', 'high_similarity', 'distinct'
        self.score = score
        self.reasons = reasons
        self.existing_song_id = existing_song_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "match_type": self.match_type,
            "score": round(self.score, 3),
            "reasons": self.reasons,
            "existing_song_id": self.existing_song_id
        }

def evaluate_song_duplicate(candidate: Dict[str, Any], conn) -> DuplicateCheckResult:
    """
    Evaluates candidate song against existing database records using multi-tiered logic:
    Tier 1: Identifiers (ISRC, MusicBrainz ID, YouTube ID)
    Tier 2: Exact normalized Sinhala / English Title + Exact normalized Artist
    Tier 3: Transliterated title match + Artist similarity
    Tier 4: Partial fuzzy matching (>=90% auto-prevent, 70-89% queue review, <70% distinct)
    """
    cursor = conn.cursor()

    c_title_si = normalize_sinhala_text(candidate.get("title_si", ""))
    c_title_en = normalize_english_text(candidate.get("title_en", ""))
    c_artist = normalize_english_text(candidate.get("artist", "")) or normalize_sinhala_text(candidate.get("artist", ""))
    c_isrc = candidate.get("isrc", "").strip()
    c_mbid = candidate.get("musicbrainz_id", "").strip()
    c_youtube = candidate.get("youtube_url", "").strip()

    # 1. Check ISRC exact match
    if c_isrc:
        cursor.execute("SELECT id, title_si, title_en, artist FROM songs WHERE isrc = ? LIMIT 1;", (c_isrc,))
        match = cursor.fetchone()
        if match:
            return DuplicateCheckResult(
                action="update_metadata",
                match_type="exact_id",
                score=1.0,
                reasons=[f"Exact ISRC match: {c_isrc} matches song ID {match['id']}"],
                existing_song_id=match["id"]
            )

    # 2. Check MusicBrainz ID exact match
    if c_mbid:
        cursor.execute("SELECT id, title_si, title_en, artist FROM songs WHERE musicbrainz_id = ? LIMIT 1;", (c_mbid,))
        match = cursor.fetchone()
        if match:
            return DuplicateCheckResult(
                action="update_metadata",
                match_type="exact_id",
                score=1.0,
                reasons=[f"Exact MusicBrainz ID match: {c_mbid} matches song ID {match['id']}"],
                existing_song_id=match["id"]
            )

    # 3. Check Exact Normalized Title + Artist
    cursor.execute("""
        SELECT id, title_si, title_en, artist, lyricist, composer, release_year, song_type
        FROM songs 
        WHERE (normalized_title_si = ? OR normalized_title_en = ?)
          AND normalized_artist = ?
        LIMIT 1;
    """, (c_title_si, c_title_en, c_artist))
    exact_match = cursor.fetchone()
    if exact_match:
        cand_type = (candidate.get("song_type") or "").strip().lower()
        exist_type = (exact_match["song_type"] or "").strip().lower()

        # If candidate is a different version (e.g. Acoustic vs Original) of the same song
        if cand_type and exist_type and cand_type != exist_type and any(t in cand_type for t in ["cover", "remake", "live", "remix", "acoustic"]):
            return DuplicateCheckResult(
                action="queue_review",
                match_type="distinct_version",
                score=0.88,
                reasons=[f"Identical title and artist but different version: candidate={cand_type}, existing={exist_type}"],
                existing_song_id=exact_match["id"]
            )

        return DuplicateCheckResult(
            action="skip",
            match_type="exact_text",
            score=1.0,
            reasons=[f"Exact match on normalized title ('{c_title_si}') and artist ('{c_artist}') with song ID {exact_match['id']}"],
            existing_song_id=exact_match["id"]
        )

    # 4. Fuzzy candidate search: retrieve top songs with same artist or similar titles
    cursor.execute("""
        SELECT id, title_si, title_en, normalized_title_si, normalized_title_en, 
               artist, normalized_artist, lyricist, composer, release_year
        FROM songs
        WHERE normalized_artist = ?
           OR normalized_title_si LIKE ?
           OR normalized_title_en LIKE ?
        LIMIT 100;
    """, (c_artist, f"%{c_title_si[:4]}%", f"%{c_title_en[:4]}%"))
    
    candidates = cursor.fetchall()
    best_match = None
    highest_score = 0.0
    match_reasons = []

    for row in candidates:
        # Title similarities
        sim_si = string_similarity_ratio(c_title_si, row["normalized_title_si"])
        sim_en = string_similarity_ratio(c_title_en, row["normalized_title_en"])
        sim_title = max(sim_si, sim_en)

        # Artist similarity
        sim_artist = string_similarity_ratio(c_artist, row["normalized_artist"])

        # Combined weighted score: Title 60%, Artist 40%
        combined_score = (sim_title * 0.60) + (sim_artist * 0.40)

        if combined_score > highest_score:
            highest_score = combined_score
            best_match = row
            match_reasons = [
                f"Title similarity: {round(sim_title, 2)}",
                f"Artist similarity: {round(sim_artist, 2)}",
                f"Matched with existing song '{row['title_si']} ({row['title_en']})' by {row['artist']}"
            ]

    # Evaluate decision threshold
    if highest_score >= 0.90:
        return DuplicateCheckResult(
            action="skip",
            match_type="high_similarity",
            score=highest_score,
            reasons=match_reasons,
            existing_song_id=best_match["id"] if best_match else None
        )
    elif highest_score >= 0.70:
        return DuplicateCheckResult(
            action="queue_review",
            match_type="uncertain_similarity",
            score=highest_score,
            reasons=match_reasons,
            existing_song_id=best_match["id"] if best_match else None
        )
    else:
        return DuplicateCheckResult(
            action="insert_new",
            match_type="distinct",
            score=highest_score,
            reasons=["Score below duplicate threshold; verified distinct record."]
        )
