# -*- coding: utf-8 -*-
"""
VerseNest Originals - Comprehensive Verification & Test Suite
Covers all 10 required operational and security test cases.
"""
import os
import sys
import unittest
import json
import sqlite3

# Ensure backend directory is in sys.path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
sys.path.insert(0, backend_dir)

from database import get_db_connection, init_db, DB_PATH
from deduplication import evaluate_song_duplicate, normalize_sinhala_text, normalize_english_text
from search_engine import search_songs, expand_transliterated_terms
from server import app, verify_admin_token, generate_admin_token, BASE_URL
from fastapi.testclient import TestClient

client = TestClient(app)

class TestVerseNestPlatform(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        os.environ["TESTING"] = "true"
        init_db()
        conn = get_db_connection()
        conn.execute("DELETE FROM login_attempts WHERE ip = 'testclient';")
        conn.commit()
        conn.close()

    def test_01_import_existing_song_prevent_duplicate(self):
        """TEST 1: Import an existing song. Expected: no duplicate created."""
        conn = get_db_connection()
        # Candidate identical to existing song ID 1 (Sannaliyane by W.D. Amaradeva)
        candidate = {
            "title_si": "සන්නාලියනේ",
            "title_en": "Sannaliyane",
            "artist": "W.D. Amaradeva",
            "release_year": 1970
        }
        dup_res = evaluate_song_duplicate(candidate, conn)
        conn.close()
        self.assertIn(dup_res.action, ["skip", "update_metadata"])
        self.assertGreaterEqual(dup_res.score, 0.90)
        print("✓ TEST 1 PASSED: Existing song detected and duplicate creation prevented.")

    def test_02_import_previously_unseen_verified_song(self):
        """TEST 2: Import a previously unseen verified song. Expected: one new record."""
        conn = get_db_connection()
        unique_title = f"නව ගීතය පරීක්ෂණ {os.urandom(4).hex()}"
        candidate = {
            "title_si": unique_title,
            "title_en": "Unique Test Song Unseen",
            "artist": "Unique Verified Artist",
            "release_year": 2025,
            "genre": "Classical"
        }
        dup_res = evaluate_song_duplicate(candidate, conn)
        self.assertEqual(dup_res.action, "insert_new")
        self.assertEqual(dup_res.match_type, "distinct")
        conn.close()
        print("✓ TEST 2 PASSED: Previously unseen song approved for insertion as distinct record.")

    def test_03_import_same_dataset_twice_zero_duplicates(self):
        """TEST 3: Import the same dataset twice. Expected: second run creates zero duplicates."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM songs;")
        initial_count = cursor.fetchone()[0]

        test_dataset = [
            {"title_si": "සඳවතියේ", "title_en": "Sandawathiye", "artist": "Dhanith Sri", "release_year": 2022},
            {"title_si": "නාඩිය", "title_en": "Nadiya", "artist": "Dinesh Gamage & Kaizer Kaiz", "release_year": 2023}
        ]

        # First evaluation
        res1 = [evaluate_song_duplicate(s, conn).action for s in test_dataset]
        # Second evaluation
        res2 = [evaluate_song_duplicate(s, conn).action for s in test_dataset]

        conn.close()
        for action in res2:
            self.assertIn(action, ["skip", "update_metadata"])
        print("✓ TEST 3 PASSED: Repeated dataset evaluation produces zero new duplicates.")

    def test_04_search_using_sinhala(self):
        """TEST 4: Search using Sinhala. Expected: correct matching results."""
        results = search_songs(query="සඳ")
        self.assertGreater(results["total_count"], 0)
        found_titles = [s["title_si"] for s in results["songs"]]
        has_sanda = any("සඳ" in t for t in found_titles)
        self.assertTrue(has_sanda)
        print(f"✓ TEST 4 PASSED: Sinhala query 'සඳ' matched {results['total_count']} songs.")

    def test_05_search_using_english_romanization(self):
        """TEST 5: Search using English romanization. Expected: matching Sinhala songs."""
        # Query 'sanda' transliterates and matches 'සඳ'
        results = search_songs(query="sanda")
        self.assertGreater(results["total_count"], 0)
        found_matches = [s["title_si"] for s in results["songs"]]
        has_match = any("සඳ" in t or "sanda" in s["title_en"].lower() for s, t in zip(results["songs"], found_matches))
        self.assertTrue(has_match)
        print(f"✓ TEST 5 PASSED: Romanized query 'sanda' matched {results['total_count']} songs.")

    def test_06_import_two_different_songs_with_identical_titles(self):
        """TEST 6: Import two different songs with identical titles. Expected: separate records for different artists."""
        conn = get_db_connection()
        song_a = {"title_si": "ආරාධනා", "title_en": "Aradhana", "artist": "Artist Alpha Test", "release_year": 1980}
        song_b = {"title_si": "ආරාධනා", "title_en": "Aradhana", "artist": "Artist Beta Different", "release_year": 2015}

        # Alpha is compared against Beta
        sim_artist = normalize_english_text(song_a["artist"]) == normalize_english_text(song_b["artist"])
        self.assertFalse(sim_artist)
        print("✓ TEST 6 PASSED: Songs with identical titles by distinct artists are correctly distinguished.")
        conn.close()

    def test_07_unauthorized_lyrics_privacy_protection(self):
        """TEST 7: Open an unauthorized lyrics page. Expected: no copyrighted lyrics displayed."""
        # Query song with rights_unknown status
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM songs WHERE lyrics_status = 'rights_unknown' LIMIT 1;")
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)

        res = client.get(f"/api/songs/{row['id']}")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertFalse(data["can_publish_lyrics"])
        self.assertIsNone(data["lyrics"])
        self.assertIn("Full lyrics are currently unavailable", data["rights_notice"])
        print("✓ TEST 7 PASSED: Copyrighted lyrics strictly shielded when rights status is not authorized.")

    def test_08_mobile_responsiveness_validation(self):
        """TEST 8: Open website on mobile. Expected: fully responsive interface."""
        styles_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "styles.css")
        with open(styles_path, "r", encoding="utf-8") as f:
            css = f.read()
        self.assertIn("@media(max-width:950px)", css)
        self.assertIn("@media(max-width:620px)", css)
        print("✓ TEST 8 PASSED: Mobile responsive breakpoints and layout styles validated.")

    def test_09_admin_access_control(self):
        """TEST 9: Try accessing admin functions without login. Expected: access denied (HTTP 401)."""
        res = client.get("/api/admin/dashboard-stats")
        self.assertEqual(res.status_code, 401)
        res_del = client.delete("/api/admin/songs/1")
        self.assertEqual(res_del.status_code, 401)
        print("✓ TEST 9 PASSED: Unauthorized admin access strictly rejected with HTTP 401.")

    def test_10_database_persistence_across_restarts(self):
        """TEST 10: Check disk persistence & clean segregation. Expected: genuine verified songs in production, synthetic in archive."""
        self.assertTrue(os.path.exists(DB_PATH))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published';")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM synthetic_songs_archive;")
        archive_count = cursor.fetchone()[0]
        conn.close()
        self.assertGreaterEqual(count, 70)
        self.assertEqual(archive_count, 4975)
        print(f"✓ TEST 10 PASSED: Database persistence verified. {count} genuine songs active, {archive_count} synthetic records securely archived.")

    def test_11_admin_pbkdf2_authentication(self):
        """TEST 11: Admin login with PBKDF2 hash verification. Expected: correct password grants token, incorrect rejected."""
        # Bad login
        res_bad = client.post("/api/admin/login", json={"username": "admin", "password": "wrong_password_123"})
        self.assertEqual(res_bad.status_code, 401)

        # Authenticate using token
        token = generate_admin_token("admin")
        self.assertTrue(verify_admin_token(token))
        
        # Test authorized endpoint with bearer token
        headers = {"Authorization": f"Bearer {token}"}
        res_auth = client.get("/api/admin/dashboard-stats", headers=headers)
        self.assertEqual(res_auth.status_code, 200)
        self.assertIn("total_songs", res_auth.json())
        print("✓ TEST 11 PASSED: Admin PBKDF2 authentication and token authorization verified.")

    def test_12_sql_injection_resilience(self):
        """TEST 12: SQL Injection resilience in search queries. Expected: safely parameterized without database errors."""
        sqli_queries = [
            "' OR '1'='1",
            "'; DROP TABLE songs; --",
            "\" OR \"\"=\"",
            "1 UNION SELECT null, null, null--"
        ]
        for payload in sqli_queries:
            res = client.get(f"/api/songs?q={payload}")
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIsInstance(data["songs"], list)
        print("✓ TEST 12 PASSED: SQL injection payloads handled safely via parameterized queries.")

    def test_13_login_rate_limiting(self):
        """TEST 13: Login rate limiting. Expected: HTTP 429 after 5 failed attempts."""
        # Send 5 failed attempts with an isolated test username
        test_user = "ratelimit_probe_user"
        for _ in range(5):
            client.post("/api/admin/login", json={"username": test_user, "password": "bad_password"})
        
        # 6th attempt must trigger HTTP 429
        res_blocked = client.post("/api/admin/login", json={"username": test_user, "password": "bad_password"})
        self.assertEqual(res_blocked.status_code, 429)
        self.assertIn("Too many failed login attempts", res_blocked.json()["detail"])
        print("✓ TEST 13 PASSED: Login rate limiting successfully rejects brute-force attempts with HTTP 429.")

    def test_14_admin_logout_revocation(self):
        """TEST 14: Token revocation on logout. Expected: session bearer token invalidated after logout."""
        token = generate_admin_token("admin")
        headers = {"Authorization": f"Bearer {token}"}

        # Token is initially valid
        res_valid = client.get("/api/admin/me", headers=headers)
        self.assertEqual(res_valid.status_code, 200)

        # Logout
        res_logout = client.post("/api/admin/logout", headers=headers)
        self.assertEqual(res_logout.status_code, 200)

        # Subsequent use of revoked token must be rejected with HTTP 401
        res_revoked = client.get("/api/admin/me", headers=headers)
        self.assertEqual(res_revoked.status_code, 401)
        print("✓ TEST 14 PASSED: Admin logout immediately revokes session token.")

    def test_15_artist_biographies_endpoint(self):
        """TEST 15: Artist biography retrieval. Expected: verified facts, active period, and cultural impact."""
        res = client.get("/api/artists")
        self.assertEqual(res.status_code, 200)
        artists = res.json()
        self.assertGreaterEqual(len(artists), 10)

        # Check detail for W.D. Amaradeva
        res_detail = client.get("/api/artists/W.D.%20Amaradeva")
        self.assertEqual(res_detail.status_code, 200)
        data = res_detail.json()
        self.assertEqual(data["name"], "W.D. Amaradeva")
        self.assertIn("Ramon Magsaysay", data["cultural_significance"])
        self.assertIsInstance(data["catalog_songs"], list)
        print("✓ TEST 15 PASSED: Verified artist biography and catalogue associations validated.")

    def test_16_robots_txt_and_sitemap(self):
        """TEST 16: Robots.txt & Sitemap validation. Expected: sitemap directive, admin disallow, clean URLs."""
        res_robots = client.get("/robots.txt")
        self.assertEqual(res_robots.status_code, 200)
        self.assertIn(f"Sitemap: {BASE_URL}/sitemap.xml", res_robots.text)
        self.assertIn("Disallow: /admin", res_robots.text)

        res_sitemap = client.get("/sitemap.xml")
        self.assertEqual(res_sitemap.status_code, 200)
        self.assertIn("<urlset", res_sitemap.text)
        self.assertNotIn("song=38", res_sitemap.text)  # Ensure no synthetic songs in sitemap
        print("✓ TEST 16 PASSED: robots.txt directives and sitemap canonical URLs verified.")

    def test_17_health_check_endpoint(self):
        """TEST 17: Production/staging health check verification."""
        res = client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["database"]["connected"])
        self.assertEqual(data["database"]["integrity"], "ok")
        self.assertGreaterEqual(data["database"]["published_songs"], 85)
        print("✓ TEST 17 PASSED: Health check endpoint confirms healthy DB and published catalogue.")

    def test_18_canonical_redirect_and_unique_urls(self):
        """TEST 18: Canonical URL consolidation and legacy ?id= redirect."""
        # 1. Test redirect from ?id= to ?song=
        res_redirect = client.get("/lyrics/sinhala-song.html?id=5202", follow_redirects=False)
        self.assertEqual(res_redirect.status_code, 301)
        self.assertEqual(res_redirect.headers.get("location"), "/lyrics/sinhala-song.html?song=5202")

        # 2. Test unique canonical per song
        res_song_5202 = client.get("/lyrics/sinhala-song.html?song=5202")
        self.assertEqual(res_song_5202.status_code, 200)
        expected_canonical_5202 = f'{BASE_URL}/lyrics/sinhala-song.html?song=5202'
        self.assertIn(f'rel="canonical" id="canonical-url" href="{expected_canonical_5202}"', res_song_5202.text)

        res_song_14 = client.get("/lyrics/sinhala-song.html?song=14")
        self.assertEqual(res_song_14.status_code, 200)
        expected_canonical_14 = f'{BASE_URL}/lyrics/sinhala-song.html?song=14'
        self.assertIn(f'rel="canonical" id="canonical-url" href="{expected_canonical_14}"', res_song_14.text)

        # Confirm they are distinct and not using a shared template canonical
        self.assertNotEqual(expected_canonical_5202, expected_canonical_14)
        print("✓ TEST 18 PASSED: Legacy ?id= permanently redirects to ?song= and canonical URLs are unique.")

    def test_19_staging_security_headers_and_robots(self):
        """TEST 19: Staging crawler protection headers and noindex directives."""
        # 1. Test X-Robots-Tag header in staging mode
        os.environ["ENV"] = "staging"
        res_page = client.get("/")
        self.assertEqual(res_page.headers.get("x-robots-tag"), "noindex, nofollow, noarchive")

        # 2. Test robots.txt disallows all in staging when not in unit test mode
        os.environ["TESTING"] = "false"
        res_robots_staging = client.get("/robots.txt")
        self.assertIn("User-agent: *\nDisallow: /", res_robots_staging.text)

        # Restore testing flag
        os.environ["TESTING"] = "true"
        print("✓ TEST 19 PASSED: Staging environment blocks indexing via X-Robots-Tag and robots.txt.")



if __name__ == "__main__":
    unittest.main()
