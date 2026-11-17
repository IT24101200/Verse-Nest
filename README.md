# VerseNest Originals — Sinhala Song & Lyrics Discovery Platform

A modern, scalable Sri Lankan music discovery platform and educational songwriting resource. Built with a high-performance **FastAPI** backend, persistent **SQLite (WAL Mode)** database of over 5,000 verified songs, transliteration-enabled search engine, legal **MusicBrainz** metadata discovery pipeline, and secure administrator portal.

---

## 🚀 Key Features

* **Persistent SQLite Song Database:** 5,012 verified songs across 18 genres, decades (from 1960s & earlier to 2020s & latest releases), and artists with ACID compliance.
* **Intelligent Transliteration Search:** Search in Sinhala script (e.g. `සඳවතියේ`) or phonetic English romanization (e.g. typing `sanda`, `oba nisa`, `amaradeva`) with instant autocomplete suggestions.
* **Advanced Multi-Factor Deduplication:** Unicode NFC normalization, phonetic distance matching, and duplicate prevention with automated review queue.
* **Strict Lyrics Rights Management:** In accordance with copyright law and Google AdSense guidelines, commercial master recordings are strictly shielded with educational notices, while verified original compositions provide full authorized lyrics.
* **MusicBrainz Legal Discovery Pipeline:** Non-destructive metadata discovery respecting API rate limits (1 req/sec) with automatic update reports.
* **Modern Mobile-First UI:** Dark/Light mode theme switch, Noto Sans Sinhala typography, responsive song cards, and detailed song analysis pages.
* **Secure Administrator Portal (`/admin.html`):** JWT-secured dashboard to manage songs, review duplicate matches, process copyright notices, and export data.
* **SEO & Google AdSense Ready:** Dynamic XML sitemap (`/sitemap.xml`), Schema.org `MusicRecording` JSON-LD structured data, and OpenGraph metadata.

---

## 📦 How to Run the Platform

### 1. Start the Production Server

In PowerShell or terminal:

```powershell
cd "e:\Projects\versenest_website\versenest_website\backend"
py server.py
```

Open your browser at: **http://localhost:8080** (or your configured `PORT`)

* **Homepage:** [http://localhost:8080/](http://localhost:8080/)
* **Sinhala Song Discovery:** [http://localhost:8080/sinhala.html](http://localhost:8080/sinhala.html)
* **Admin Portal:** [http://localhost:8080/admin.html](http://localhost:8080/admin.html) *(Managed via `backend/manage_admin.py` and `.env`)*
* **Dynamic SEO Sitemap:** [http://localhost:8080/sitemap.xml](http://localhost:8080/sitemap.xml)
* **Robots.txt Directive:** [http://localhost:8080/robots.txt](http://localhost:8080/robots.txt)
* **Interactive API Documentation:** [http://localhost:8080/docs](http://localhost:8080/docs)

---

### 2. Run the Automated Discovery Scheduler

To run background periodic discovery from MusicBrainz:

```powershell
cd "e:\Projects\versenest_website\versenest_website\backend"
py scheduler.py --interval 24
```

To run a one-off discovery test:

```powershell
py scheduler.py --once --artists 3
```

---

### 3. Run the Automated Test Suite

All 10 required operational, security, and deduplication test cases can be verified via:

```powershell
cd "e:\Projects\versenest_website\versenest_website"
py tests/test_platform.py
```

---

## 📑 Detailed Implementation Report

For full architectural blueprints, data source permissions, lyrics rights breakdown, and test results, please refer to:
👉 [SINHALA_SONG_LIBRARY_IMPLEMENTATION_REPORT.md](file:///e:/Projects/versenest_website/versenest_website/SINHALA_SONG_LIBRARY_IMPLEMENTATION_REPORT.md)

---

## © License & Attribution

All original creative writing samples and platform software are licensed under VerseNest Originals. Sri Lankan music bibliographic metadata is indexed for non-commercial educational discovery. All composition rights belong to original artists, lyricists, composers, and authorized publishers.
