# VerseNest Live Website Acceptance & Deployment Audit Report

**Report Date:** November 19, 2026  
**Auditor / Roles:** Senior Frontend Engineer, Responsive UI/UX Designer & Quality Assurance Specialist  
**Repository:** `IT24101200/Verse-Nest` (Branch: `main`)  
**Live Hosting Provider:** Render (Cloud Native Web Service / Docker ASGI)  
**Live Website Public URL:** [https://verse-nest.onrender.com](https://verse-nest.onrender.com)  
**Deployment Health Endpoint:** [https://verse-nest.onrender.com/api/health](https://verse-nest.onrender.com/api/health)  
**Latest Deployed Git Commit:** `7f818cd` (*build: untrack large evidence zip from repository and update .gitignore*) / `0982737` (*fix(ui): polish 1024px header, balance featured grid, and fix decade text consistency*)  
**Overall Acceptance Status:** **ACCEPTED & FULLY VERIFIED (100% PASS)**

---

## 1. Executive Summary

A comprehensive source-level and browser-level live acceptance audit was conducted directly against the public production staging deployment on **Render** at **`https://verse-nest.onrender.com`**.

All requested verification phases have been executed with headless Chromium/Playwright browsers across 8 distinct viewports (320px, 375px, 768px, 960px, 1000px, 1024px, 1440px, 1920px) under both Dark and Light color schemes. No horizontal scrollbars, text clipping, or broken layouts were detected.

The persistent SQLite database mounted at `/app/data/versenest.db` on Render survived hibernation spin-downs and container restarts with zero data corruption and 100% integrity (`PRAGMA integrity_check` -> `ok`).

---

## 2. Live Hosting & Deployment Diagnostics

| Parameter | Live Value | Verification Details |
|---|---|---|
| **Hosting Platform** | Render Cloud Web Service | Python ASGI container powered by Uvicorn |
| **Public Endpoint** | `https://verse-nest.onrender.com` | Verified HTTP 200 via Cloudflare edge routing |
| **Health API** | `https://verse-nest.onrender.com/api/health` | `{"status":"healthy","environment":"staging","database":{"connected":true,"integrity":"ok","published_songs":85}}` |
| **Total Published Songs** | **85 Songs** | 73 Verified Sinhala Classics + 12 VerseNest English Originals |
| **Pending / Hidden Records** | 185 records | Quarantined from public discovery & sitemaps |
| **Persistent Volume** | `/app/data` (1 GB persistent disk) | Survives service restarts and idle hibernation |
| **Security Headers** | Active | `X-Robots-Tag: noindex, nofollow`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN` |
| **Console Errors** | **0 Errors** | Headless Chrome navigation recorded 0 unhandled JS errors |
| **Failed Network Requests** | **0 Failures** | All assets (`/assets/styles.css`, `/assets/main.js`, SVG icons) returned HTTP 200 |

---

## 3. Step 1: Featured Song Grid Verification (960px & 1000px)

The intermediate tablet/small-desktop viewports (960px and 1000px) were inspected in both Dark and Light modes to verify card balance and prevent awkward wrapping:

| Viewport | Theme | Container Width | Grid Template Columns | Gap | Card Dimensions | Horizontal Overflow | Result |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **960px** | Dark | 892.8px | 3 columns (`282.9px` each) | 22px | 282.9px × 312.8px | `False` (0px) | **PASS** |
| **960px** | Light | 892.8px | 3 columns (`282.9px` each) | 22px | 282.9px × 312.8px | `False` (0px) | **PASS** |
| **1000px** | Dark | 930.0px | 3 columns (`295.3px` each) | 22px | 295.3px × 312.8px | `False` (0px) | **PASS** |
| **1000px** | Light | 930.0px | 3 columns (`295.3px` each) | 22px | 295.3px × 312.8px | `False` (0px) | **PASS** |

### Visual Layout Structure (6 Items):
* **Row 1:** Card 1, Card 2, Card 3
* **Row 2:** Card 4, Card 5, Card 6
* Result: Perfectly balanced 2 × 3 grid with zero orphan cards.

---

## 4. Step 2 & 3: Repository Cleanliness & Version Control

1. **Large Evidence Archive Removal:**
   * `VERSENEST_WIDE_LAYOUT_FINAL_EVIDENCE.zip` (23.0 MB) was removed from version control using `git rm --cached`.
   * The archive is preserved safely on the local disk as an offline artifact without bloating git clone speeds.
2. **Updated `.gitignore`:**
   * Rule `*.zip` now safely ignores all `.zip` bundles.
3. **Commit & Push History:**
   * Commit `0982737`: *fix(ui): polish 1024px header, balance featured grid, and fix decade text consistency*
   * Commit `7f818cd`: *build: untrack large evidence zip from repository and update .gitignore*
   * Both commits pushed and reconciled with `origin/main`.

---

## 5. Steps 5 & 6: Live Functional & Visual Acceptance Matrix

| Test Suite / Section | Tested URL / Target | Verified Behaviors | Status |
|---|---|---|:---:|
| **1. Homepage Hero & Metrics** | `/index.html` | Hero title, vinyl disc illustration, dynamic counters (85+ songs, 73 Sinhala, 12 Originals). Fraction grid prevents container clipping. | **PASS** |
| **2. Featured Highlights Grid** | `/#browse-classics` | 6 cards displayed. Filter tabs (All, Classics, Recent) toggle dynamically via `/api/songs`. | **PASS** |
| **3. Sinhala Song Library** | `/sinhala.html` | Displays all 73 Sinhala songs with 24 songs per page, responsive pagination, genre/decade dropdown filters. | **PASS** |
| **4. Live Autocomplete Search** | `/sinhala.html#song-search` | Searching *"Manda Pama"* returns Song 5191. Searching *"Amaradeva"* returns 4 classic records. Suggestions box renders cleanly. | **PASS** |
| **5. Song Detail Page** | `/lyrics/sinhala-song.html?song=5191` | Verified *Manda Pama* (Umaria Sinhawansa). Title, artist, lyricist, composer (`DIM`), year (`2020`), era (`2020s`), and editorial commentary match. | **PASS** |
| **6. Mobile Navigation Drawer** | Mobile `<header>` (375px) | Hamburger button (☰) toggles accessible slide-down drawer with 6 functional navigation routes. | **PASS** |
| **7. Dark & Light Themes** | Global `#theme-btn` | Full CSS variable toggle (`--bg-primary`, `--text-primary`, `--bg-surface`, `--accent-primary`). Verified high contrast. | **PASS** |
| **8. Admin Portal** | `/admin.html` | Secure password login form renders cleanly; unauthorized access properly gated. | **PASS** |
| **9. Database Connection & Health** | `/api/health` | Connected: `true`, Integrity: `ok`, Published: `85`, Environment: `staging`. | **PASS** |
| **10. Copyright Protection & Takedown** | `/copyright.html` | Educational fair use notice, zero-scraped-lyrics policy, and DMCA rights claim form intact. | **PASS** |

---

## 6. Viewport Responsiveness Verification (Live Site)

All tests performed against live `https://verse-nest.onrender.com/`:

| Viewport | Mode | Client Width | Scroll Width | Overflow? | Verification Screenshot |
|---|---|:---:|:---:|:---:|---|
| **320px** (Small Mobile) | Dark | 320px | 320px | **No** | `screenshots/live-deployment/live_homepage_320px_dark.png` |
| **320px** (Small Mobile) | Light | 320px | 320px | **No** | `screenshots/live-deployment/live_homepage_320px_light.png` |
| **375px** (iPhone SE) | Dark | 375px | 375px | **No** | `screenshots/live-deployment/live_homepage_375px_dark.png` |
| **375px** (iPhone SE) | Light | 375px | 375px | **No** | `screenshots/live-deployment/live_homepage_375px_light.png` |
| **768px** (Tablet Portrait) | Dark | 768px | 768px | **No** | `screenshots/live-deployment/live_homepage_768px_dark.png` |
| **768px** (Tablet Portrait) | Light | 768px | 768px | **No** | `screenshots/live-deployment/live_homepage_768px_light.png` |
| **1024px** (Tablet Landscape) | Dark | 1024px | 1024px | **No** | `screenshots/live-deployment/live_homepage_1024px_dark.png` |
| **1024px** (Tablet Landscape) | Light | 1024px | 1024px | **No** | `screenshots/live-deployment/live_homepage_1024px_light.png` |
| **1440px** (Desktop HD) | Dark | 1440px | 1440px | **No** | `screenshots/live-deployment/live_homepage_1440px_dark.png` |
| **1440px** (Desktop HD) | Light | 1440px | 1440px | **No** | `screenshots/live-deployment/live_homepage_1440px_light.png` |
| **1920px** (Full HD Ultrawide) | Dark | 1920px | 1920px | **No** | `screenshots/live-deployment/live_homepage_1920px_dark.png` |
| **1920px** (Full HD Ultrawide) | Light | 1920px | 1920px | **No** | `screenshots/live-deployment/live_homepage_1920px_light.png` |

---

## 7. Database Persistence Status

* **Storage Location on Cloud:** `/app/data/versenest.db`
* **Mount Type:** Attached 1 GB Persistent Disk (Render Starter Web Service)
* **Cold Spin-Down / Wakeup Test:** When the service spun down during inactivity, the first incoming HTTP request woke the container. The database mounted cleanly with all 85 records preserved.
* **Integrity Status:** `PRAGMA integrity_check` -> `ok`
* **Catalogue Breakdown:**
  * 73 Verified Sinhala Songs
  * 12 VerseNest English Originals
  * 185 Quarantined cultural tracks held in pending verification state
  * 2 Quarantined fabricated tracks rejected

---

## 8. Remaining Items & Conclusion

* **Remaining Critical Issues:** **Zero**.
* **Deployment Stability:** Verified live on Render with automated continuous deployment from the GitHub `main` branch.
* **Sign-off:** The VerseNest Sinhala Songs platform meets all visual design, responsive layout, copyright protection, database persistence, and architectural standards.
