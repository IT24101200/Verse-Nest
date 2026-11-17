# -*- coding: utf-8 -*-
"""
VerseNest Originals — Source-Based Authenticity Audit Automated Test Suite
Validates:
1. Purging of synthetic/pattern MusicBrainz UUIDs
2. Release year accuracy (e.g., Umaria's 'Manda Pama' verified as 2020)
3. Strict rejection and quarantine of fabricated records ('Dengue Maduruwa', 'Haal Garena')
4. Exclusion of unverified/rejected records from public search, stats, and sitemaps
5. Source evidence and listening URL validity
6. Artist-title consistency across corrected classic recordings
"""

import os
import sys
import unittest
import sqlite3
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from server import app
from database import DB_PATH

class TestAuthenticityAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_synthetic_musicbrainz_purged(self):
        """TEST 1: Zero published songs have synthetic/pattern UUIDs."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("""
            SELECT id, title_en, musicbrainz_id 
            FROM songs 
            WHERE publication_status = 'published' AND musicbrainz_id IS NOT NULL AND musicbrainz_id != ''
        """)
        songs_with_mbid = c.fetchall()
        
        synthetic_patterns = ['a1122334', 'b2233445', 'c3344556', 'd4455667', 'e5566778', 'f6677889', 'f7788990']
        violating = [s for s in songs_with_mbid if any(p in s[2] for p in synthetic_patterns)]
        self.assertEqual(len(violating), 0, f"Found {len(violating)} songs with synthetic MusicBrainz UUIDs: {violating}")
        conn.close()
        print("✓ TEST 1 PASSED: Synthetic MusicBrainz pattern UUIDs completely purged.")

    def test_02_umaria_manda_pama_verified_2020(self):
        """TEST 2: 'Manda Pama' release year is 2020 with verified official video and credits."""
        res = self.client.get("/api/songs?q=Manda%20Pama")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        songs = [s for s in data["songs"] if s["title_en"] == "Manda Pama"]
        self.assertTrue(len(songs) > 0, "Manda Pama not found in public search")
        manda_pama = songs[0]
        self.assertEqual(manda_pama["release_year"], 2020, f"Expected 2020, got {manda_pama['release_year']}")
        self.assertEqual(manda_pama["artist"], "Umaria Sinhawansa")
        self.assertEqual(manda_pama["composer"], "DIM (Raaw Productions)")
        self.assertEqual(manda_pama["lyricist"], "Manuranga Wijesekara")
        self.assertEqual(manda_pama["youtube_url"], "https://www.youtube.com/watch?v=RsEoXcrnSxg")
        print("✓ TEST 2 PASSED: Umaria's 'Manda Pama' accurately verified as 2020 release with official credits and video.")

    def test_03_fabricated_songs_rejected(self):
        """TEST 3: Fabricated songs are marked 'rejected' and excluded from public search."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check Dengue Maduruwa
        c.execute("SELECT id, publication_status FROM songs WHERE title_en LIKE '%Dengue%'")
        dengue_rows = c.fetchall()
        self.assertTrue(len(dengue_rows) > 0, "Dengue Maduruwa record missing in DB")
        for row in dengue_rows:
            self.assertEqual(row[1], "rejected", f"Song ID {row[0]} should be 'rejected', got '{row[1]}'")

        # Check Haal Garena
        c.execute("SELECT id, publication_status FROM songs WHERE title_en LIKE '%Haal Garena%'")
        haal_rows = c.fetchall()
        self.assertTrue(len(haal_rows) > 0, "Haal Garena record missing in DB")
        for row in haal_rows:
            self.assertEqual(row[1], "rejected", f"Song ID {row[0]} should be 'rejected', got '{row[1]}'")
            
        conn.close()

        # Public search probe
        res1 = self.client.get("/api/songs?q=Dengue")
        self.assertEqual(len([s for s in res1.json()["songs"] if s["id"] == 5192 or "Dengue" in s["title_en"]]), 0,
                         "Rejected song 'Dengue Maduruwa' found in public search!")
        res2 = self.client.get("/api/songs?q=Haal%20Garena")
        self.assertEqual(len([s for s in res2.json()["songs"] if s["id"] == 5227 or s["title_en"] == "Haal Garena"]), 0,
                         "Rejected song 'Haal Garena' found in public search!")
        print("✓ TEST 3 PASSED: Fabricated songs strictly quarantined with status 'rejected'.")

    def test_04_unverified_songs_excluded_from_public_and_sitemap(self):
        """TEST 4: 'pending_verification' songs are excluded from public search, stats, and sitemap."""
        res_stats = self.client.get("/api/stats")
        self.assertEqual(res_stats.status_code, 200)
        stats = res_stats.json()

        # Verified counts: 73 Sinhala + 12 English = 85 Total published
        self.assertEqual(stats["total_songs"], 85, f"Expected 85 total published, got {stats['total_songs']}")
        self.assertEqual(stats["sinhala_songs"], 73, f"Expected 73 Sinhala, got {stats['sinhala_songs']}")
        self.assertEqual(stats["english_originals"], 12, f"Expected 12 English, got {stats['english_originals']}")

        # Verify sitemap contains exactly 85 songs + 7 static pages = 92 <loc>
        res_sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(res_sitemap.status_code, 200)
        loc_count = res_sitemap.text.count("<loc>")
        self.assertEqual(loc_count, 92, f"Expected 92 sitemap URLs, got {loc_count}")
        print("✓ TEST 4 PASSED: Unverified songs strictly excluded from public stats and sitemaps.")

    def test_05_source_url_validity(self):
        """TEST 5: All published songs have valid source URLs or documented incomplete status, and zero suspicious MBID prefixes."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, title_en, source_url, youtube_url, language, lyrics_evidence, musicbrainz_id FROM songs WHERE publication_status = 'published'")
        songs = c.fetchall()
        
        suspicious_prefixes = ['773356e8', 'b6f5cb74', '06e00b8c', 'f12e8b2b', '013a2d59']

        for s in songs:
            song_id, title_en, source_url, yt_url, lang, evidence, mbid = s
            # Verify no suspicious shared prefixes remain
            if mbid:
                for prefix in suspicious_prefixes:
                    self.assertFalse(mbid.startswith(prefix), f"Song ID {song_id} ({title_en}) still has suspicious MBID prefix {prefix}: {mbid}")
            
            # If source_url is present, it must be valid; if NULL, it must be documented as incomplete
            if source_url is not None:
                self.assertTrue(source_url.startswith("http://") or source_url.startswith("https://") or source_url.startswith("lyrics/"),
                                f"Song ID {song_id} ({title_en}) has invalid source URL: {source_url}")
            else:
                self.assertIn("Source verification incomplete", evidence or "",
                              f"Song ID {song_id} ({title_en}) has NULL source_url but lacks incomplete verification note")
            
            # All Sinhala songs must have verified YouTube listening links
            if lang == "si":
                self.assertTrue(yt_url and yt_url.startswith("https://www.youtube.com/"),
                                f"Sinhala Song ID {song_id} ({title_en}) has invalid YouTube URL: {yt_url}")
        conn.close()
        print(f"✓ TEST 5 PASSED: All {len(songs)} published songs have valid external sources or documented incomplete status.")

    def test_06_artist_title_consistency_on_corrected_records(self):
        """TEST 6: Corrected classic records have accurate titles and original artists."""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Mal Sara by Gratien Ananda (held in pending_verification)
        c.execute("SELECT title_en, artist, publication_status FROM songs WHERE id = 5135")
        r1 = c.fetchone()
        self.assertEqual(r1[0], "Mal Sara")
        self.assertEqual(r1[1], "Gratien Ananda")
        self.assertEqual(r1[2], "pending_verification")

        # Ithihasaye Katha by Dhanith Sri (2024 verified)
        c.execute("SELECT title_en, artist, release_year, youtube_url FROM songs WHERE id = 5202")
        r2 = c.fetchone()
        self.assertEqual(r2[0], "Ithihasaye Katha")
        self.assertEqual(r2[1], "Dhanith Sri")
        self.assertEqual(r2[2], 2024)
        self.assertEqual(r2[3], "https://www.youtube.com/watch?v=Tef_wagMs6M")

        # Aaley Mal by Kanchana Anuradhi (2022 verified)
        c.execute("SELECT title_en, artist, release_year, youtube_url FROM songs WHERE id = 5232")
        r_aaley = c.fetchone()
        self.assertEqual(r_aaley[0], "Aaley Mal")
        self.assertEqual(r_aaley[1], "Kanchana Anuradhi")
        self.assertEqual(r_aaley[2], 2022)
        self.assertEqual(r_aaley[3], "https://www.youtube.com/watch?v=HEm9KIjEVV4")

        # Thaniwennata Mage Lowe by Victor Ratnayake
        c.execute("SELECT title_en, artist FROM songs WHERE id = 5123")
        r3 = c.fetchone()
        self.assertEqual(r3[0], "Thaniwennata Mage Lowe")
        self.assertEqual(r3[1], "Victor Ratnayake")

        # Sudu Mal Pokurak by Prince Udaya Priyantha
        c.execute("SELECT title_en, artist FROM songs WHERE id = 5132")
        r4 = c.fetchone()
        self.assertEqual(r4[0], "Sudu Mal Pokurak")
        self.assertEqual(r4[1], "Prince Udaya Priyantha")

        conn.close()
        print("✓ TEST 6 PASSED: Corrected classic records verified for title and artist consistency.")

if __name__ == "__main__":
    unittest.main()
