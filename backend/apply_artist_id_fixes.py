# -*- coding: utf-8 -*-
"""
VerseNest Originals — Artist Identifier Check & Correction Engine
Purpose:
1. Validates the 30 baseline records with artist-level MusicBrainz URLs.
2. Updates confirmed artists with their verified genuine MusicBrainz artist UUIDs.
3. Sets unconfirmed identifiers to NULL and marks source verification as incomplete.
4. Preserves genuine song records, lyrics shielding, and counts.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "versenest.db")

# Confirmed real MusicBrainz artist profiles (LK artists)
CONFIRMED_ARTISTS = {
    "Dhanith Sri": "1200e5ec-5058-45ef-a493-1a56457afa14",
    "Bathiya & Santhush": "cb89b0c2-b03a-4e9b-a4fe-5010f92e29ca",
    "Kasun Kalhara": "e53abf43-19e6-4bf1-980d-f2672a533615",
    "Centigradz": "895def9f-2ef8-44bc-a254-e7722c4ff6ca",
    "Dinesh Gamage": "1f28d270-514f-4dd8-ae02-f69d19072ae8",
    "Supun Perera": "4b97bc2a-f5c8-442a-a968-348589fac3a3",
    "M.S. Fernando": "7cd2f559-4ece-4c4b-a455-3fb5fd0c1442",
    "Sanuka Wickramasinghe": "cbebe6b4-6ae8-4afd-8da8-b8dd0aeeaa69",
    "Kanchana Anuradhi": "d785e993-fadb-434f-a2a7-861c760f5508"
}

# The 30 baseline song IDs flagged in the audit
CONFIRMED_SONG_IDS = {
    14: ("Dhanith Sri", "Sandawathiye"),
    5046: ("Dhanith Sri", "Kawikariye"),
    36: ("Bathiya & Santhush", "Nethu Mane"),
    5039: ("Bathiya & Santhush", "Siri Sanghabodhi Maligawedi"),
    37: ("Kasun Kalhara", "Ananthaya Mage Wuwa"),
    5016: ("Kasun Kalhara", "Danena Dana"),
    5040: ("Kasun Kalhara", "Mal Pipunata Lowe"),
    5018: ("Centigradz", "Ahanna Deyo"),
    5041: ("Centigradz", "Netha Nube Dutu Mul Dine"),
    17: ("Dinesh Gamage", "Dawas Hatha"),
    5045: ("Dinesh Gamage", "Mayamkari"),
    21: ("Supun Perera", "Kalyaniye"),
    5029: ("M.S. Fernando", "Kataragama Deviyane"),
    5043: ("Sanuka Wickramasinghe", "Sanda Kan Wasila"),
    5047: ("Kanchana Anuradhi", "Sanda Morala")
}

UNCONFIRMED_SONG_IDS = [
    16, 18, 19, 20, 22, 30, 5019, 5022, 5023, 5026, 5035, 5036, 5038, 5042, 5044
]

def apply_fixes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== STEP 1: Updating Confirmed Artists in songs table ===")
    for song_id, (artist_name, title) in CONFIRMED_SONG_IDS.items():
        mbid = CONFIRMED_ARTISTS[artist_name]
        source_url = f"https://musicbrainz.org/artist/{mbid}"
        cursor.execute("""
            UPDATE songs
            SET musicbrainz_id = ?, source_url = ?
            WHERE id = ?;
        """, (mbid, source_url, song_id))
        print(f"Updated Song ID {song_id} ({title} by {artist_name}) -> MBID: {mbid}")

    print("\n=== STEP 2: Setting Unconfirmed Identifiers to NULL in songs table ===")
    for song_id in UNCONFIRMED_SONG_IDS:
        cursor.execute("SELECT title_en, artist, lyrics_evidence FROM songs WHERE id = ?;", (song_id,))
        row = cursor.fetchone()
        if row:
            title_en, artist, evidence = row
            evidence_str = (evidence or "")
            if "[Source verification incomplete" not in evidence_str:
                evidence_str = f"{evidence_str} [Source verification incomplete: MusicBrainz artist identifier unconfirmed]".strip()
            cursor.execute("""
                UPDATE songs
                SET musicbrainz_id = NULL, source_url = NULL, lyrics_evidence = ?
                WHERE id = ?;
            """, (evidence_str, song_id))
            print(f"Set ID {song_id} ({title_en} by {artist}) -> MBID: NULL, source_url: NULL, evidence updated")

    print("\n=== STEP 3: Updating artists table ===")
    # Update confirmed artists
    cursor.execute("UPDATE artists SET musicbrainz_artist_id = ? WHERE name = 'Bathiya & Santhush';", 
                   (CONFIRMED_ARTISTS['Bathiya & Santhush'],))
    cursor.execute("UPDATE artists SET musicbrainz_artist_id = ? WHERE name = 'Kasun Kalhara';", 
                   (CONFIRMED_ARTISTS['Kasun Kalhara'],))
    
    # Nullify unconfirmed artist identifiers in artists table
    unconfirmed_artist_names = [
        'W.D. Amaradeva', 'Clarence Wijewardena', 'Milton Mallawarachchi',
        'Victor Ratnayake', 'H.R. Jothipala', 'Sunil Edirisinghe',
        'Gunadasa Kapuge', 'Rookantha Gunathilaka', 'Charitha Attalage', 'Yohani'
    ]
    for aname in unconfirmed_artist_names:
        cursor.execute("UPDATE artists SET musicbrainz_artist_id = NULL WHERE name = ?;", (aname,))
        print(f"Artist '{aname}' in artists table -> musicbrainz_artist_id: NULL")

    conn.commit()
    conn.close()
    print("\nAll database updates applied successfully.")

if __name__ == "__main__":
    apply_fixes()
