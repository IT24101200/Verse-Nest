# -*- coding: utf-8 -*-
"""
VerseNest 320px & Multi-Viewport Real Visual Bounds Test Suite
Performs actual browser DOM measurements using Playwright to confirm:
- Zero horizontal document overflow across all viewports
- Key hero elements (eyebrow, h1, copy, search input/button, stats) strictly within [0, viewportWidth]
- No clipped text (scrollWidth <= clientWidth for containers)
- Cards fit their containers cleanly
- Intentionally horizontally scrollable containers (admin tabs) function correctly
"""
import unittest
import os
import sys
import time
import subprocess
import urllib.request
from playwright.sync_api import sync_playwright

CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
BASE_URL = "http://localhost:8080"

class TestMobile320Visual(unittest.TestCase):
    server_proc = None

    @classmethod
    def setUpClass(cls):
        # Ensure server is running on port 8080
        server_ready = False
        try:
            with urllib.request.urlopen(f"{BASE_URL}/api/stats", timeout=2) as resp:
                if resp.status == 200:
                    server_ready = True
        except Exception:
            pass

        if not server_ready:
            proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            server_script = os.path.join(proj_root, "backend", "server.py")
            cls.server_proc = subprocess.Popen([sys.executable, server_script], cwd=os.path.join(proj_root, "backend"))
            # Wait up to 5 seconds for server to be responsive
            for _ in range(25):
                time.sleep(0.2)
                try:
                    with urllib.request.urlopen(f"{BASE_URL}/api/stats", timeout=1) as resp:
                        if resp.status == 200:
                            server_ready = True
                            break
                except Exception:
                    pass

        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(executable_path=CHROME_PATH, headless=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        if cls.server_proc:
            cls.server_proc.terminate()
            cls.server_proc.wait()

    def test_01_homepage_320px_hero_bounds(self):
        """TEST 1: Homepage hero elements at 320px must remain within viewport bounds with zero clipping."""
        page = self.browser.new_page(viewport={"width": 320, "height": 800})
        page.goto(f"{BASE_URL}/", wait_until="networkidle")
        page.wait_for_timeout(300)

        metrics = page.evaluate("""() => {
            const docEl = document.documentElement;
            const cw = docEl.clientWidth;
            const sw = docEl.scrollWidth;

            const check = (sel) => {
                const el = document.querySelector(sel);
                if (!el) return null;
                const r = el.getBoundingClientRect();
                return {
                    left: r.left,
                    right: r.right,
                    width: r.width,
                    scrollWidth: el.scrollWidth,
                    clientWidth: el.clientWidth,
                    isWithinBounds: r.left >= 0 && r.right <= cw,
                    isNotClipped: el.scrollWidth <= el.clientWidth + 2
                };
            };

            return {
                docClientWidth: cw,
                docScrollWidth: sw,
                eyebrow: check('.eyebrow'),
                h1: check('.hero h1'),
                heroCopy: check('.hero-copy'),
                searchBox: check('.hero-search-box'),
                searchInput: check('.hero-search-box input'),
                searchButton: check('.hero-search-box button'),
                stats: check('.stats')
            };
        }""")

        self.assertLessEqual(metrics["docScrollWidth"], metrics["docClientWidth"], "Document has horizontal scrollbar at 320px!")
        
        for name, data in metrics.items():
            if name.startswith("doc") or not data:
                continue
            self.assertTrue(data["isWithinBounds"], f"Element {name} exceeds 320px viewport bounds! right={data['right']}")
            self.assertTrue(data["isNotClipped"], f"Element {name} is clipped! scrollWidth={data['scrollWidth']} > clientWidth={data['clientWidth']}")

        print(f"✓ TEST 1 PASSED: All 320px homepage hero elements strictly fit within viewport (right <= {metrics['docClientWidth']}px).")
        page.close()

    def test_02_homepage_across_all_mobile_viewports(self):
        """TEST 2: Homepage has zero horizontal overflow across 320, 360, 375, 390, 430, 768, 1440."""
        viewports = [320, 360, 375, 390, 430, 768, 1440]
        for w in viewports:
            page = self.browser.new_page(viewport={"width": w, "height": 800})
            page.goto(f"{BASE_URL}/", wait_until="networkidle")
            overflow = page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
            self.assertFalse(overflow, f"Homepage has horizontal overflow at {w}px!")
            page.close()
        print(f"✓ TEST 2 PASSED: Homepage has zero overflow across all {len(viewports)} viewports (320px - 1440px).")

    def test_03_sinhala_library_320px_bounds(self):
        """TEST 3: Sinhala song library search, filters, and cards fit within 320px bounds."""
        page = self.browser.new_page(viewport={"width": 320, "height": 800})
        page.goto(f"{BASE_URL}/sinhala.html", wait_until="networkidle")
        page.wait_for_timeout(400)

        data = page.evaluate("""() => {
            const cw = document.documentElement.clientWidth;
            const searchInput = document.querySelector('#song-search').getBoundingClientRect();
            const filterDrawer = document.querySelector('#mobile-filters-drawer').getBoundingClientRect();
            const firstCard = document.querySelector('.lyric-card').getBoundingClientRect();
            return {
                cw,
                docScroll: document.documentElement.scrollWidth,
                searchRight: searchInput.right,
                filterRight: filterDrawer.right,
                cardRight: firstCard.right
            };
        }""")

        self.assertLessEqual(data["docScroll"], data["cw"])
        self.assertLessEqual(data["searchRight"], data["cw"] + 1)
        self.assertLessEqual(data["filterRight"], data["cw"] + 1)
        self.assertLessEqual(data["cardRight"], data["cw"] + 1)
        print("✓ TEST 3 PASSED: Sinhala library search, filters, and song cards fit within 320px bounds.")
        page.close()

    def test_04_search_results_320px_layout(self):
        """TEST 4: Search results on 320px display matching cards cleanly within bounds."""
        page = self.browser.new_page(viewport={"width": 320, "height": 800})
        page.goto(f"{BASE_URL}/sinhala.html?q=sanda", wait_until="networkidle")
        page.wait_for_timeout(400)

        card_count = page.evaluate("""() => {
            const cards = document.querySelectorAll('#song-grid .lyric-card');
            for (const c of cards) {
                const r = c.getBoundingClientRect();
                if (r.right > 320) return -1;
            }
            return cards.length;
        }""")

        self.assertGreater(card_count, 0, "No cards displayed for 'sanda' search query!")
        print(f"✓ TEST 4 PASSED: {card_count} matching song cards displayed within 320px bounds for query 'sanda'.")
        page.close()

    def test_05_admin_dashboard_320px_and_scrollable_tabs(self):
        """TEST 5: Admin dashboard at 320px fits screen; tab strip is scrollable without breaking page layout."""
        sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend"))
        from security import generate_session_token
        token = generate_session_token("admin", duration_hours=1)

        page = self.browser.new_page(viewport={"width": 320, "height": 800})
        page.add_init_script(f"localStorage.setItem('versenest_admin_token', '{token}');")
        page.goto(f"{BASE_URL}/admin.html", wait_until="networkidle")
        page.wait_for_timeout(400)

        res = page.evaluate("""() => {
            const cw = document.documentElement.clientWidth;
            const sw = document.documentElement.scrollWidth;
            const tabs = document.querySelector('.admin-tabs');
            const tabsScrollable = tabs ? tabs.scrollWidth > tabs.clientWidth : false;
            const stats = document.querySelectorAll('.stat-card');
            let statsWithinBounds = true;
            for (const s of stats) {
                const r = s.getBoundingClientRect();
                if (r.right > cw) statsWithinBounds = false;
            }
            return {
                docScroll: sw,
                cw,
                tabsScrollable,
                statsWithinBounds,
                statsCount: stats.length
            };
        }""")

        self.assertLessEqual(res["docScroll"], res["cw"], "Admin page document has unwanted horizontal scrollbar!")
        self.assertTrue(res["tabsScrollable"], "Admin tabs should be horizontally scrollable on 320px!")
        self.assertTrue(res["statsWithinBounds"], "Admin stat cards exceed 320px bounds!")
        print("✓ TEST 5 PASSED: Admin 320px layout fits viewport; swipeable tabs function properly.")
        page.close()

    def test_06_both_themes_at_320px(self):
        """TEST 6: Both Dark and Light themes render without horizontal overflow at 320px."""
        for theme in ["dark", "light"]:
            page = self.browser.new_page(viewport={"width": 320, "height": 800})
            page.add_init_script(f"""
                localStorage.setItem('versenest_theme', '{theme}');
                document.documentElement.setAttribute('data-theme', '{theme}');
            """)
            page.goto(f"{BASE_URL}/", wait_until="networkidle")
            page.wait_for_timeout(300)
            overflow = page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
            self.assertFalse(overflow, f"Horizontal overflow detected in {theme} mode at 320px!")
            page.close()
        print("✓ TEST 6 PASSED: Dark and Light themes verified without overflow at 320px.")

if __name__ == "__main__":
    unittest.main()
