# -*- coding: utf-8 -*-
"""
Ensure historic classic Sinhala songs have accurate decades and classic tags.
"""
from database import get_db_connection

def fix_classics():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Artists who are classic legends
    classic_artists = [
        ("W.D. Amaradeva", 1972, "1970s"),
        ("Milton Mallawarachchi", 1978, "1970s"),
        ("Victor Ratnayake", 1974, "1970s"),
        ("Neela Wickramasinghe", 1979, "1970s"),
        ("Clarence Wijewardena", 1975, "1970s"),
        ("H.R. Jothipala", 1976, "1970s"),
        ("Gunadasa Kapuge", 1983, "1980s"),
        ("Sunil Edirisinghe", 1981, "1980s"),
        ("Nanda Malini", 1973, "1970s"),
        ("Sanath Nandasiri", 1977, "1970s"),
        ("T.M. Jayaratne", 1984, "1980s"),
        ("Amarasiri Peiris", 1992, "1990s"),
        ("Rookantha Gunathilaka", 1994, "1990s"),
        ("Edward Jayakody", 1988, "1980s"),
        ("Sisira Senarathne", 1965, "1960s and earlier"),
        ("Rukmani Devi", 1958, "1960s and earlier"),
        ("Karunaratne Abeysekera", 1966, "1960s and earlier")
    ]

    updated_count = 0
    for artist, yr, dec in classic_artists:
        cursor.execute("""
            UPDATE songs
            SET is_classic = 1,
                is_recent = 0,
                release_year = ?,
                era_decade = ?
            WHERE artist = ?;
        """, (yr, dec, artist))
        updated_count += cursor.rowcount

    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM songs WHERE is_classic = 1;")
    total_classics = cursor.fetchone()[0]
    conn.close()
    print(f"Updated {updated_count} songs. Total classic songs now: {total_classics}")

if __name__ == "__main__":
    fix_classics()
