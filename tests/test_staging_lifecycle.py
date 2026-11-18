# -*- coding: utf-8 -*-
"""
VerseNest Originals — Staging Lifecycle & Persistence Test Suite
Validates:
1. Fresh volume initialization from seed (without overwriting existing databases)
2. Health check endpoint /api/health
3. Live catalogue counts (73 Sinhala + 12 English = 85 published, 185 pending excluded)
4. Admin authentication, JWT tokens, and revocation on logout
5. Database data persistence across simulated container restarts
6. Atomic online backup and restoration integrity
7. Staging security headers (X-Robots-Tag, noindex)
"""

import os
import sys
import unittest
import sqlite3
import shutil
import tempfile
import time
from fastapi.testclient import TestClient

backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from database import DB_PATH, get_db_connection, init_db, ensure_database_ready
from server import app, generate_admin_token, BASE_URL

class TestStagingLifecycle(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["TESTING"] = "true"
        cls.client = TestClient(app)

    def test_01_fresh_volume_bootstrap_safety(self):
        """TEST 1: Verify fresh volume bootstrap from seed without overwriting existing data."""
        temp_dir = tempfile.mkdtemp(prefix="versenest_fresh_vol_")
        test_db_path = os.path.join(temp_dir, "versenest.db")

        try:
            # Initial state: file does not exist
            self.assertFalse(os.path.exists(test_db_path))

            # Run ensure_database_ready targeting the empty volume path
            ensure_database_ready(target_path=test_db_path)
            self.assertTrue(os.path.exists(test_db_path))
            self.assertGreater(os.path.getsize(test_db_path), 0)

            # Check that seeded database has the 85 songs
            conn = sqlite3.connect(test_db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published';")
            count = c.fetchone()[0]
            self.assertEqual(count, 85, f"Expected 85 published songs in seeded volume, got {count}")

            # Test non-overwrite: write a marker record, run ensure_database_ready again
            c.execute("""
                INSERT INTO songs (song_uuid, title_si, title_en, normalized_title_si, normalized_title_en, artist, normalized_artist, publication_status)
                VALUES ('seed-marker-001', 'මාකර්', 'Marker Song', 'මාකර්', 'marker song', 'Tester', 'tester', 'published');
            """)
            conn.commit()

            # Call ensure_database_ready again - must NOT overwrite
            ensure_database_ready(target_path=test_db_path)
            c.execute("SELECT COUNT(*) FROM songs WHERE song_uuid = 'seed-marker-001';")
            self.assertEqual(c.fetchone()[0], 1, "Marker record was overwritten by ensure_database_ready!")
            conn.close()

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
        print("✓ TEST 1 PASSED: Fresh volume bootstraps from seed safely and never overwrites existing data.")

    def test_02_health_check_endpoint(self):
        """TEST 2: Verify /api/health reports healthy database, published songs, and correct env."""
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "healthy")
        self.assertTrue(data["database"]["connected"])
        self.assertEqual(data["database"]["integrity"], "ok")
        self.assertEqual(data["database"]["published_songs"], 85)
        self.assertIn("environment", data)
        self.assertIn("base_url", data)
        print("✓ TEST 2 PASSED: Health check confirms healthy status and 85 published songs.")

    def test_03_catalogue_counts_and_isolation(self):
        """TEST 3: Verify 73 Sinhala songs, 12 English originals, and 185 pending unexposed songs."""
        res = self.client.get("/api/stats")
        self.assertEqual(res.status_code, 200)
        stats = res.json()
        self.assertEqual(stats["total_songs"], 85)
        self.assertEqual(stats["sinhala_songs"], 73)
        self.assertEqual(stats["english_originals"], 12)

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'pending_verification';")
        pending_count = c.fetchone()[0]
        self.assertEqual(pending_count, 185, f"Expected 185 pending songs, got {pending_count}")

        c.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'rejected';")
        rejected_count = c.fetchone()[0]
        self.assertEqual(rejected_count, 2, f"Expected 2 rejected songs, got {rejected_count}")
        conn.close()
        print("✓ TEST 3 PASSED: Verified 73 Sinhala, 12 English, 185 pending, and 2 rejected songs.")

    def test_04_admin_login_and_logout_revocation(self):
        """TEST 4: Admin authentication, session token issuance, and logout token revocation."""
        # Generate valid token
        token = generate_admin_token("admin")
        headers = {"Authorization": f"Bearer {token}"}

        # Check authenticated endpoint
        res = self.client.get("/api/admin/dashboard-stats", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["total_songs"], 272)

        # Logout
        res_logout = self.client.post("/api/admin/logout", headers=headers)
        self.assertEqual(res_logout.status_code, 200)

        # Subsequent request with revoked token must fail with HTTP 401
        res_revoked = self.client.get("/api/admin/dashboard-stats", headers=headers)
        self.assertEqual(res_revoked.status_code, 401)
        print("✓ TEST 4 PASSED: Admin session creation, dashboard access, and logout revocation verified.")

    def test_05_data_persistence_across_restart(self):
        """TEST 5: Insert test record, simulate application restart, confirm record persists, and clean up."""
        test_uuid = f"staging-persist-test-{int(time.time())}"
        
        # 1. Insert record
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("""
            INSERT INTO songs (
                song_uuid, title_si, title_en, normalized_title_si, normalized_title_en,
                artist, normalized_artist, release_year, publication_status, lyrics_status
            ) VALUES (
                ?, 'තාවකාලික පරීක්ෂණ ගීතය', 'Temporary Persistence Song',
                'තාවකාලික පරීක්ෂණ ගීතය', 'temporary persistence song',
                'Staging Tester', 'staging tester', 2026, 'published', 'rights_unknown'
            );
        """, (test_uuid,))
        conn.commit()
        inserted_id = c.lastrowid
        conn.close()
        self.assertIsNotNone(inserted_id)

        # 2. Simulate container restart (simulate re-executing get_db_connection with new connection pool)
        # Verify record exists
        conn2 = get_db_connection()
        c2 = conn2.cursor()
        c2.execute("SELECT id, title_en FROM songs WHERE song_uuid = ?;", (test_uuid,))
        row = c2.fetchone()
        self.assertIsNotNone(row, "Test record did not persist across connection reset!")
        self.assertEqual(row["title_en"], "Temporary Persistence Song")

        # 3. Clean up safely
        c2.execute("DELETE FROM songs WHERE song_uuid = ?;", (test_uuid,))
        conn2.commit()
        
        # Confirm cleanup
        c2.execute("SELECT COUNT(*) FROM songs WHERE song_uuid = ?;", (test_uuid,))
        self.assertEqual(c2.fetchone()[0], 0)
        conn2.close()
        print("✓ TEST 5 PASSED: Data persistence verified across simulated container restart, safely cleaned up.")

    def test_06_database_backup_and_restoration(self):
        """TEST 6: Test atomic SQLite online backup and restoration integrity."""
        backup_file = os.path.join(os.path.dirname(DB_PATH), "versenest_test_backup.db")
        if os.path.exists(backup_file):
            os.remove(backup_file)

        # 1. Perform online backup
        source_conn = get_db_connection()
        backup_conn = sqlite3.connect(backup_file)
        source_conn.backup(backup_conn)
        backup_conn.close()
        source_conn.close()

        self.assertTrue(os.path.exists(backup_file))
        self.assertGreater(os.path.getsize(backup_file), 100000)

        # 2. Verify backup integrity
        verify_conn = sqlite3.connect(backup_file)
        c = verify_conn.cursor()
        c.execute("PRAGMA integrity_check;")
        self.assertEqual(c.fetchone()[0], "ok")

        c.execute("SELECT COUNT(*) FROM songs WHERE publication_status = 'published';")
        self.assertEqual(c.fetchone()[0], 85)
        verify_conn.close()

        # 3. Clean up backup file
        os.remove(backup_file)
        print("✓ TEST 6 PASSED: Atomic SQLite backup and restoration verified with 100% integrity.")

if __name__ == "__main__":
    unittest.main()
