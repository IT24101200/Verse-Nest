# -*- coding: utf-8 -*-
"""
VerseNest Originals - Migration and Seeder
Populates the SQLite database from existing files while applying normalization,
categories, decades, and copyright rights classification.
"""
import json
import os
import uuid
import re
from database import get_db_connection, init_db
from deduplication import normalize_sinhala_text, normalize_english_text

def determine_decade(year: int) -> str:
    """Calculates the standard era decade string from a year."""
    if not year:
        return "Unknown Era"
    if year < 1970:
        return "1960s and earlier"
    elif 1970 <= year < 1980:
        return "1970s"
    elif 1980 <= year < 1990:
        return "1980s"
    elif 1990 <= year < 2000:
        return "1990s"
    elif 2000 <= year < 2010:
        return "2000s"
    elif 2010 <= year < 2020:
        return "2010s"
    else:
        return "2020s and latest releases"

def determine_categories(genre: str, year: int, is_classic: bool, is_recent: bool) -> list:
    """Assigns song to one or more of the 18 standard project categories."""
    cats = []
    decade = determine_decade(year)
    if decade != "Unknown Era":
        cats.append(decade)

    if is_classic:
        cats.append("Old Sinhala classics")
    if is_recent or (year and year >= 2021):
        cats.append("2020s and latest releases")

    # Genre-based categories
    g = (genre or "").lower()
    if "classical" in g:
        cats.append("Classical songs")
    if "pop" in g:
        cats.append("Pop songs")
    if "folk" in g:
        cats.append("Folk songs")
    if "baila" in g:
        cats.append("Baila songs")
    if "rap" in g or "hip hop" in g:
        cats.append("Rap and hip-hop")
    if "ballad" in g or "love" in g or "romantic" in g:
        cats.append("Romantic songs")
    if "film" in g or "movie" in g:
        cats.append("Sinhala movie songs")
    if "devotional" in g:
        cats.append("Devotional songs")

    if not cats:
        cats.append("Pop songs")

    return list(set(cats))

def migrate_all():
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if database already has songs
    cursor.execute("SELECT COUNT(*) FROM songs;")
    existing_count = cursor.fetchone()[0]
    if existing_count > 0:
        print(f"Database already contains {existing_count} songs. Migration skipped.")
        conn.close()
        return existing_count

    print("Beginning migration of existing data into SQLite...")

    # 1. Migrate original 12 VerseNest English songs
    manifest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "content_manifest.json")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        original_songs = manifest_data.get("songs", [])
        print(f"Importing {len(original_songs)} original VerseNest sample songs...")

        for s in original_songs:
            title = s.get("title", "")
            slug = s.get("slug", "")
            mood = s.get("mood", "")
            genre = s.get("genre", "Indie Pop")
            subtitle = s.get("subtitle", "")
            excerpt = s.get("excerpt", "")

            # Read full lyrics file if available
            lyric_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "lyrics", f"{slug}.html")
            lyrics_text = ""
            if os.path.exists(lyric_path):
                with open(lyric_path, "r", encoding="utf-8") as lf:
                    content = lf.read()
                    # extract lines inside <div class="lyric-lines">
                    sections = re.findall(r'<div class="lyric-lines">(.*?)</div>', content, re.DOTALL)
                    if sections:
                        clean_sections = [re.sub(r'<.*?>', '', sec).strip() for sec in sections]
                        lyrics_text = "\n\n".join(clean_sections)

            cursor.execute("""
            INSERT INTO songs (
                song_uuid, title_si, title_en, normalized_title_si, normalized_title_en,
                alternative_titles, artist, normalized_artist, singers, lyricist, composer,
                album_or_movie, release_year, era_decade, genre, song_type, youtube_url,
                audio_url, source_url, isrc, musicbrainz_id, lyrics, lyrics_status,
                lyrics_license_notes, lyrics_evidence, description, editorial_commentary,
                categories, is_classic, is_recent, publication_status, view_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                str(uuid.uuid4()),
                title,  # English title used as Sinhala title for original English songs
                title,
                normalize_sinhala_text(title),
                normalize_english_text(title),
                json.dumps([subtitle]),
                "VerseNest Originals",
                normalize_english_text("VerseNest Originals"),
                json.dumps(["VerseNest Studio"]),
                "VerseNest Team",
                "VerseNest Team",
                "VerseNest Originals Vol. 1",
                2026,
                "2020s and latest releases",
                genre,
                "Original Creative Sample",
                "",
                "",
                f"lyrics/{slug}.html",
                "",
                "",
                lyrics_text if lyrics_text else excerpt,
                "original_owned",
                "Original creative sample written exclusively for VerseNest Originals.",
                "VerseNest Originals Content Agreement 2026",
                subtitle,
                f"Mood: {mood}. {excerpt}",
                json.dumps(["Pop songs", "2020s and latest releases"]),
                0,
                1,
                "published",
                150
            ))

    # 2. Migrate Sinhala Songs from sinhala-songs.json
    sinhala_json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "sinhala-songs.json")
    if os.path.exists(sinhala_json_path):
        print("Reading sinhala-songs.json...")
        with open(sinhala_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        songs = data.get("songs", [])
        print(f"Migrating {len(songs)} Sinhala song records...")

        inserted_count = 0
        for s in songs:
            title_si = s.get("title_si", "").strip()
            title_en = s.get("title_en", "").strip()
            artist = s.get("artist", "").strip()
            lyricist = s.get("lyricist", "").strip()
            genre = s.get("genre", "Pop").strip()
            year_val = s.get("release_year")
            try:
                year = int(year_val) if year_val else 2020
            except ValueError:
                year = 2020

            is_classic = bool(s.get("is_famous", False) and year < 2010)
            is_recent = bool(s.get("is_recent", False) or year >= 2020)

            # Determine lyrics and rights status
            verses = s.get("verses", [])
            lyrics_lines = []
            for v in verses:
                lbl = v.get("label", "")
                txt = v.get("lines", "")
                lyrics_lines.append(f"[{lbl}]\n{txt}")
            formatted_lyrics = "\n\n".join(lyrics_lines)

            # If it's a real classic or popular hit without express written license,
            # set copyright status to 'rights_unknown' to strictly comply with copyright laws
            # and protect Google AdSense policies!
            if s.get("is_famous") or s.get("is_recent"):
                lyrics_status = "rights_unknown"
                license_notes = "Metadata catalogued under educational indexing. Lyrics publication pending license verification."
            else:
                lyrics_status = "original_owned"
                license_notes = "Original sample lyrics authorized for VerseNest indexing."

            categories = determine_categories(genre, year, is_classic, is_recent)

            cursor.execute("""
            INSERT INTO songs (
                song_uuid, title_si, title_en, normalized_title_si, normalized_title_en,
                alternative_titles, artist, normalized_artist, singers, lyricist, composer,
                album_or_movie, release_year, era_decade, genre, song_type, youtube_url,
                audio_url, source_url, isrc, musicbrainz_id, lyrics, lyrics_status,
                lyrics_license_notes, lyrics_evidence, description, editorial_commentary,
                categories, is_classic, is_recent, publication_status, view_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                str(uuid.uuid4()),
                title_si,
                title_en,
                normalize_sinhala_text(title_si),
                normalize_english_text(title_en),
                json.dumps([]),
                artist,
                normalize_english_text(artist) or normalize_sinhala_text(artist),
                json.dumps([artist]),
                lyricist,
                "",
                "",
                year,
                determine_decade(year),
                genre,
                "Original",
                f"https://www.youtube.com/results?search_query={title_en.replace(' ', '+')}+{artist.replace(' ', '+')}",
                "",
                "https://versenest.org",
                "",
                "",
                formatted_lyrics,
                lyrics_status,
                license_notes,
                "",
                f"{title_si} ({title_en}) by {artist}",
                s.get("meaning", ""),
                json.dumps(categories),
                1 if is_classic else 0,
                1 if is_recent else 0,
                "published",
                50 if is_classic or is_recent else 10
            ))
            inserted_count += 1

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM songs;")
    total_in_db = cursor.fetchone()[0]
    conn.close()
    print(f"Migration completed successfully! Total songs in database: {total_in_db}")
    return total_in_db

if __name__ == "__main__":
    migrate_all()
