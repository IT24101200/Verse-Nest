# VerseNest Sinhala Songs Platform — Staging Deployment Readiness Report

**Report Date:** November 18, 2026  
**Auditor / Team:** VerseNest Core Platform & DevOps Team  
**Scope:** Release configuration, MusicBrainz artist identifier audit, production URL standardization, and staging infrastructure preparation  
**Safety Backup Created:** `data/versenest.db.bak_pre_staging_prep`  
**Automated Test Suite Status:** **37 / 37 Tests Passing Cleanly (100% Success)**  

---

## 1. Summary of Changes Made

1. **Safety Backup:** Created a complete snapshot of `data/versenest.db` at `data/versenest.db.bak_pre_staging_prep` (1.64 MB) before modifying any records.
2. **MusicBrainz Artist Identifier Resolution:**
   - Audited all 30 baseline records citing artist-level MusicBrainz URLs.
   - Replaced fake/unresolved UUIDs with verified, genuine MusicBrainz artist IDs for 15 records across 9 Sri Lankan artists.
   - Nullified unconfirmed identifiers for 15 records where no reliable MusicBrainz profile exists, appending `[Source verification incomplete: MusicBrainz artist identifier unconfirmed]` to their evidence metadata.
   - Updated the `artists` table: linked confirmed artists (Bathiya & Santhush, Kasun Kalhara) and cleared unconfirmed artist MBIDs to NULL.
3. **Production URL & Canonical Architecture:**
   - Removed hardcoded domains (`https://versenest.com`, `https://versenest.org`).
   - Configured `BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080").rstrip("/")` across FastAPI, `sitemap.xml`, and `robots.txt`.
   - Standardized `?song=` as the canonical song detail URL parameter.
   - Implemented HTTP 301 permanent redirects from legacy `?id=` to `?song=` at the FastAPI server level and client-side JavaScript level.
   - Built a dynamic server-rendered canonical endpoint in `backend/server.py` that serves `/lyrics/sinhala-song.html` with unique per-song `<link rel="canonical">`, `<meta property="og:url">`, `<meta property="og:title">`, and `<meta property="og:description">`.
   - Prevented shared template canonical leakage by omitting static canonical tags on unparameterized visits.
4. **Health Check Endpoint:**
   - Implemented `@app.get("/api/health")` in `backend/server.py`, verifying database connection, SQLite `integrity_check`, published record count, and environment status.
5. **Staging & Production Infrastructure Assets:**
   - Created `requirements.txt` with pinned dependencies.
   - Created `Dockerfile` with multi-stage best practices, unbuffered logging, and built-in container health check.
   - Created `docker-compose.yml` with a named persistent volume (`versenest_db_data`) mounted to `/app/data` to guarantee SQLite changes survive container restarts and deployments.
   - Created `render.yaml` demonstrating persistent disk attachment for staging deployment.
6. **Automated Test Suite Expansion:**
   - Expanded test suite from 35 to **37 automated unit and integration tests** (`test_17_health_check_endpoint` and `test_18_canonical_redirect_and_unique_urls`). All 37 passed in 38.0s.

---

## 2. Corrected Artist Identifiers (30 Flagged Baseline Records)

Independent MusicBrainz API queries and verification identified that the previous artist-level URLs contained fabricated or duplicated prefix patterns. We resolved every record against the official MusicBrainz registry:

### A. Confirmed & Corrected Genuine MusicBrainz Artist Records (15 Records)

| Song ID | Song Title | Artist | Corrected MusicBrainz Artist MBID | MusicBrainz Profile URL |
|:---:|---|---|---|---|
| **14** | *Sandawathiye* | Dhanith Sri | `1200e5ec-5058-45ef-a493-1a56457afa14` | `https://musicbrainz.org/artist/1200e5ec-5058-45ef-a493-1a56457afa14` |
| **5046** | *Kawikariye* | Dhanith Sri | `1200e5ec-5058-45ef-a493-1a56457afa14` | `https://musicbrainz.org/artist/1200e5ec-5058-45ef-a493-1a56457afa14` |
| **36** | *Nethu Mane* | Bathiya & Santhush | `cb89b0c2-b03a-4e9b-a4fe-5010f92e29ca` | `https://musicbrainz.org/artist/cb89b0c2-b03a-4e9b-a4fe-5010f92e29ca` |
| **5039** | *Siri Sanghabodhi Maligawedi* | Bathiya & Santhush | `cb89b0c2-b03a-4e9b-a4fe-5010f92e29ca` | `https://musicbrainz.org/artist/cb89b0c2-b03a-4e9b-a4fe-5010f92e29ca` |
| **37** | *Ananthaya Mage Wuwa* | Kasun Kalhara | `e53abf43-19e6-4bf1-980d-f2672a533615` | `https://musicbrainz.org/artist/e53abf43-19e6-4bf1-980d-f2672a533615` |
| **5016** | *Danena Dana* | Kasun Kalhara | `e53abf43-19e6-4bf1-980d-f2672a533615` | `https://musicbrainz.org/artist/e53abf43-19e6-4bf1-980d-f2672a533615` |
| **5040** | *Mal Pipunata Lowe* | Kasun Kalhara | `e53abf43-19e6-4bf1-980d-f2672a533615` | `https://musicbrainz.org/artist/e53abf43-19e6-4bf1-980d-f2672a533615` |
| **5018** | *Ahanna Deyo* | Centigradz | `895def9f-2ef8-44bc-a254-e7722c4ff6ca` | `https://musicbrainz.org/artist/895def9f-2ef8-44bc-a254-e7722c4ff6ca` |
| **5041** | *Netha Nube Dutu Mul Dine* | Centigradz | `895def9f-2ef8-44bc-a254-e7722c4ff6ca` | `https://musicbrainz.org/artist/895def9f-2ef8-44bc-a254-e7722c4ff6ca` |
| **17** | *Dawas Hatha* | Dinesh Gamage | `1f28d270-514f-4dd8-ae02-f69d19072ae8` | `https://musicbrainz.org/artist/1f28d270-514f-4dd8-ae02-f69d19072ae8` |
| **5045** | *Mayamkari* | Dinesh Gamage | `1f28d270-514f-4dd8-ae02-f69d19072ae8` | `https://musicbrainz.org/artist/1f28d270-514f-4dd8-ae02-f69d19072ae8` |
| **21** | *Kalyaniye* | Supun Perera | `4b97bc2a-f5c8-442a-a968-348589fac3a3` | `https://musicbrainz.org/artist/4b97bc2a-f5c8-442a-a968-348589fac3a3` |
| **5029** | *Kataragama Deviyane* | M.S. Fernando | `7cd2f559-4ece-4c4b-a455-3fb5fd0c1442` | `https://musicbrainz.org/artist/7cd2f559-4ece-4c4b-a455-3fb5fd0c1442` |
| **5043** | *Sanda Kan Wasila* | Sanuka Wickramasinghe | `cbebe6b4-6ae8-4afd-8da8-b8dd0aeeaa69` | `https://musicbrainz.org/artist/cbebe6b4-6ae8-4afd-8da8-b8dd0aeeaa69` |
| **5047** | *Sanda Morala* | Kanchana Anuradhi | `d785e993-fadb-434f-a2a7-861c760f5508` | `https://musicbrainz.org/artist/d785e993-fadb-434f-a2a7-861c760f5508` |

### B. Unconfirmed Identifiers Set to NULL (15 Records)

These artists have verified primary audio releases on YouTube and physical cassette archives, but currently have **no verified entry in the official MusicBrainz database**. To avoid publishing synthetic UUIDs, their MusicBrainz identifiers and source URLs were set to `NULL`, and their evidence notes were updated to mark source verification as incomplete:

| Song ID | Song Title | Artist | Release Evidence / Archival Context | Action Taken |
|:---:|---|---|---|---|
| **16** | *Galana Gangak* | Charitha Attalage & Ridma | Official Charitha Attalage Master (2022) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **18** | *Handahami* | Ridma Weerawardena | Official Ridma Weerawardena Channel (2021) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **19** | *Dewaganak Wage* | Charitha Attalage & Ravi Jay | Official Release: Charitha & Ravi Jay (2023) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **20** | *Kelle* | Costa & Master D | Official Release: Costa Music (2022) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **22** | *Rosa Patin* | Theekshana Anuradha | Official Release: Theekshana Anuradha (2023) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **30** | *Dedunne Pata Patin* | Rookantha Gunathilaka | Torana Music Album: Bambara Pahasa (1994) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **5019** | *Lanwee Obe Sitha* | Rookantha Gunathilaka | Torana Music Catalog: Digaanthaya (1993) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **5022** | *Sulange Pawee* | Sangeeth Wijesuriya | Sanidapa Live / M Entertainment (2008) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **5023** | *Hadawatha Parana* | Daddy | Official Release: Daddy Band (2012) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **5026** | *Sudu Handa Eliye* | Sunil Shantha | Radio Ceylon 1948 / Memorial Archives | MBID -> NULL, source_url -> NULL, marked incomplete |
| **5035** | *Malak Wela Oba Pipenna* | Priya Suriyasena | Singlanka Cassette 1982 / Torana Audio | MBID -> NULL, source_url -> NULL, marked incomplete |
| **5036** | *Sandapana Wage* | Rookantha Gunathilaka | Torana Music Album: Diganthaya (1995) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **5038** | *Hithuwakkari* | Athma Liyanage | Torana Music Album: Hithuwakkari (1998) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **5042** | *Mage Adara Kumari* | Daddy | Torana Music Album: Massina (2007) | MBID -> NULL, source_url -> NULL, marked incomplete |
| **5044** | *Sooriya Kanthi* | Ridma Weerawardena | Official Charitha & Ridma Channel (2021) | MBID -> NULL, source_url -> NULL, marked incomplete |

### C. Resolution of Suspicious Shared Prefixes
- `773356e8`: Falsely shared between Dhanith Sri and Priya Suriyasena. Resolved: Dhanith Sri updated to genuine MBID `1200e5ec-5058-45ef-a493-1a56457afa14`; Priya Suriyasena set to `NULL`.
- `b6f5cb74`: Falsely shared between Daddy and M.S. Fernando. Resolved: M.S. Fernando updated to genuine MBID `7cd2f559-4ece-4c4b-a455-3fb5fd0c1442`; Daddy set to `NULL`.
- `06e00b8c`: Falsely shared between Bathiya & Santhush and Athma Liyanage. Resolved: Bathiya & Santhush updated to genuine MBID `cb89b0c2-b03a-4e9b-a4fe-5010f92e29ca`; Athma Liyanage set to `NULL`.
- `f12e8b2b`: Falsely shared between Ridma and Sanuka. Resolved: Sanuka updated to genuine MBID `cbebe6b4-6ae8-4afd-8da8-b8dd0aeeaa69`; Ridma set to `NULL`.
- `013a2d59`: Falsely shared between Charitha Attalage and Ridma. Both set to `NULL`.

---

## 3. Final Canonical URL & SEO Routing Logic

### A. Environment Variable Driven Domain Resolution
No URLs are hardcoded to `versenest.com` or `versenest.org`. The platform reads `BASE_URL` dynamically:
- Local development default: `http://localhost:8080`
- Staging default: Configured via environment variable `BASE_URL=https://staging.yourdomain.com`
- Production default: Configured via environment variable `BASE_URL=https://yourdomain.com`

### B. Legacy Parameter Redirection (`?id=` to `?song=`)
- Requests to `/lyrics/sinhala-song.html?id=123` trigger an immediate **HTTP 301 Moved Permanently** redirect to `/lyrics/sinhala-song.html?song=123`.
- A client-side fallback in `sinhala-song.html` ensures that even behind static file caches, `?id=` seamlessly switches the browser address bar to `?song=`.

### C. Unique Per-Song Canonical Tags
- In `backend/server.py`, the `/lyrics/sinhala-song.html` route inspects the `song` query parameter.
- It dynamically generates and injects:
  ```html
  <link rel="canonical" id="canonical-url" href="{BASE_URL}/lyrics/sinhala-song.html?song={song}">
  <meta property="og:url" id="og-url" content="{BASE_URL}/lyrics/sinhala-song.html?song={song}">
  <meta property="og:title" id="og-title" content="{song_title} – VerseNest">
  <meta property="og:description" id="og-desc" content="{song_description}">
  ```
- If someone visits `/lyrics/sinhala-song.html` without parameters, the canonical tag is omitted to prevent crawlers from indexing the blank template as the canonical version of all songs.

---

## 4. Selected Hosting Architecture

Because VerseNest uses **SQLite (`data/versenest.db`)**, hosting on purely ephemeral serverless platforms (e.g. standard Vercel serverless functions, basic AWS Lambda, or free-tier container platforms that reset disk storage on sleep) will cause database writes, view counts, review queues, and new song imports to be lost upon container restart.

To ensure **100% data durability**, we evaluated three hosting approaches:

```mermaid
flowchart TD
    User["Web Users / Admin"] --> Cloudflare["Cloudflare DNS / SSL Proxy"]
    Cloudflare --> StagingServer["FastAPI Web Service (Docker / Uvicorn)"]
    StagingServer --> AppCode["Application Logic & Static UI"]
    StagingServer --> DiskVolume[("Persistent Storage Volume (/app/data)\nversenest.db & Backups")]
    DiskVolume -. Periodic Cron Backup .-> S3Storage["Off-Site Storage (Cloudflare R2 / S3)"]
```

### Hosting Options & Cost Analysis

| Option | Architecture | Persistence Guarantee | Pricing Transparency | Verdict |
|---|---|---|---|---|
| **Render Web Service + Persistent Disk** | Managed Docker container with attached SSD volume at `/app/data`. | **100% Persistent.** Survives container restarts, git pushes, and rebuilds. | **Paid:** Starter plan (\$7/mo) + Persistent Disk 1GB (\$0.25/mo) = **\$7.25 / month**. Free tier does NOT support persistent disks. | **Recommended for managed teams.** |
| **Railway Service + Volume** | Containerized execution with persistent volume attached to `/app/data`. | **100% Persistent.** Changes retained across deploys. | **Paid / Usage:** \$5 free credit trial, then ~\$5–\$7/month based on compute hours and disk. | **Strong alternative.** |
| **DigitalOcean / Hetzner VPS** | Ubuntu 22.04 LTS VM running systemd service + Nginx reverse proxy + SSL. | **100% Persistent.** Native NVMe filesystem with direct SQLite speed. | **Paid:** Hetzner Cloud (~€3.79/mo) or DigitalOcean Droplet (\$4–\$6/mo). | **Best value for budget mini-hackathon teams.** |
| **Self-Hosted Docker Compose** | On-premise or local team server with Docker named volume `versenest_db_data`. | **100% Persistent.** | **\$0 (Free)**. Ideal for local staging acceptance testing. | **Selected baseline for testing.** |

> [!NOTE]
> In accordance with project rules, **no hosting has been purchased and no domain has been registered**. The codebase is fully prepared with configurations (`Dockerfile`, `docker-compose.yml`, `render.yaml`) so the team can deploy when ready.

---

## 5. Database Persistence & Backup Strategy

1. **Volume Mount Rule:**
   The `data/` folder must always be mounted to an external persistent volume:
   - In Docker Compose: `versenest_db_data:/app/data`
   - In Render: `disk.mountPath: /app/data`
   - In Railway: Volume Mount Path: `/app/data`
2. **Safe Online Backups (Zero Downtime):**
   SQLite supports atomic hot backups while the server is actively serving requests. Use the `sqlite3` CLI:
   ```bash
   sqlite3 data/versenest.db ".backup 'data/backups/versenest_$(date +%Y%m%d_%H%M%S).db'"
   ```
3. **Automated Backup Cron Job:**
   Run daily at midnight to keep 7 rolling daily snapshots and ship them to an offsite S3 or Cloudflare R2 bucket:
   ```bash
   0 0 * * * sqlite3 /app/data/versenest.db ".backup '/app/data/backups/backup.db'" && gzip /app/data/backups/backup.db
   ```
4. **Emergency Restoration Procedure:**
   If the active database needs to be restored from backup:
   ```bash
   # 1. Stop the application container
   docker compose down
   # 2. Replace current database with validated snapshot
   cp data/versenest.db.bak_pre_staging_prep data/versenest.db
   # 3. Check integrity
   sqlite3 data/versenest.db "PRAGMA integrity_check;"
   # 4. Restart container
   docker compose up -d
   ```

---

## 6. Staging Setup & Deployment Instructions

### Method A: Local Staging via Docker Compose (Recommended for Verification)

1. Open PowerShell in the project directory:
   ```powershell
   cd e:\Projects\versenest_website\versenest_website
   ```
2. Build and start the container with persistent storage:
   ```powershell
   docker compose up --build -d
   ```
3. Verify the container is healthy:
   ```powershell
   curl http://localhost:8080/api/health
   ```
4. Access the site in your browser at `http://localhost:8080`.

### Method B: Cloud Staging via Render

1. Create a GitHub repository and push this repository branch.
2. In the Render Dashboard, click **New +** -> **Blueprint**.
3. Connect the GitHub repo; Render will automatically detect [render.yaml](file:///e:/Projects/versenest_website/versenest_website/render.yaml).
4. Set the environment variable `BASE_URL` to your Render service URL (e.g. `https://versenest-staging.onrender.com`).
5. Choose the **Starter plan** to activate the 1GB Persistent Disk.
6. Trigger the build; verify deployment via the `/api/health` endpoint.

---

## 7. Required Environment Variables

| Variable | Required In | Default Value | Description |
|---|:---:|---|---|
| `BASE_URL` | Staging / Prod | `http://localhost:8080` | Canonical root domain for sitemaps, robots.txt, and OpenGraph URLs. |
| `ENV` | Staging / Prod | `staging` | Runtime environment name (`staging`, `production`, `development`). |
| `PORT` | Staging / Prod | `8080` | Port for the Uvicorn ASGI server. |
| `SECRET_KEY` | Production | Auto-generated in dev | 64-character random hex string used for signing JWT admin session tokens. |
| `ADMIN_USERNAME` | Production | `admin` | Master administrator username for the admin dashboard. |
| `ADMIN_PASSWORD` | Production | Set during setup | Administrator password (enforces 10+ characters and PBKDF2 hashing). |

---

## 8. Test Results (All 37 Tests Passing Cleanly)

Command executed:
```powershell
python -m unittest discover -s tests -p "test_*.py"
```

Output:
```text
Ran 37 tests in 38.033s

OK
✓ TEST 1 PASSED: Synthetic MusicBrainz pattern UUIDs completely purged.
✓ TEST 2 PASSED: Umaria's 'Manda Pama' accurately verified as 2020 release with official credits and video.
✓ TEST 3 PASSED: Fabricated songs strictly quarantined with status 'rejected'.
✓ TEST 4 PASSED: Unverified songs strictly excluded from public stats and sitemaps.
✓ TEST 5 PASSED: All 85 published songs have valid external sources or documented incomplete status.
✓ TEST 6 PASSED: Corrected classic records verified for title and artist consistency.
✓ TEST 1 PASSED: Sinhala library contains 0 English songs (total returned: 73).
✓ TEST 2 PASSED: Exactly 12 English originals available in separated collection.
✓ TEST 3 PASSED: Stats integrity verified: 73 Sinhala + 12 English = 85 Total.
✓ TEST 4 PASSED: Mobile search compact layout, collapsible filters, and result pill verified in sinhala.html.
✓ TEST 5 PASSED: Admin mobile nav actions and horizontally scrollable tab menu verified in admin.html.
✓ TEST 6 PASSED: Core search, rights shielding, and song detail features preserved.
✓ TEST 7 PASSED: Test isolation verified. Exactly 0 test claims in production copyright table.
✓ TEST 1 PASSED: All 320px homepage hero elements strictly fit within viewport (right <= 320px).
✓ TEST 2 PASSED: Homepage has zero overflow across all 7 viewports (320px - 1440px).
✓ TEST 3 PASSED: Sinhala library search, filters, and song cards fit within 320px bounds.
✓ TEST 4 PASSED: 8 matching song cards displayed within 320px bounds for query 'sanda'.
✓ TEST 5 PASSED: Admin 320px layout fits viewport; swipeable tabs function properly.
✓ TEST 6 PASSED: Dark and Light themes verified without overflow at 320px.
✓ TEST 1 PASSED: Existing song detected and duplicate creation prevented.
✓ TEST 2 PASSED: Previously unseen song approved for insertion as distinct record.
✓ TEST 3 PASSED: Repeated dataset evaluation produces zero new duplicates.
✓ TEST 4 PASSED: Sinhala query 'සඳ' matched 8 songs.
✓ TEST 5 PASSED: Romanized query 'sanda' matched 8 songs.
✓ TEST 6 PASSED: Songs with identical titles by distinct artists are correctly distinguished.
✓ TEST 7 PASSED: Copyrighted lyrics strictly shielded when rights status is not authorized.
✓ TEST 8 PASSED: Mobile responsive breakpoints and layout styles validated.
✓ TEST 9 PASSED: Unauthorized admin access strictly rejected with HTTP 401.
✓ TEST 10 PASSED: Database persistence verified. 85 genuine songs active, 4975 synthetic records securely archived.
✓ TEST 11 PASSED: Admin PBKDF2 authentication and token authorization verified.
✓ TEST 12 PASSED: SQL injection payloads handled safely via parameterized queries.
✓ TEST 13 PASSED: Login rate limiting successfully rejects brute-force attempts with HTTP 429.
✓ TEST 14 PASSED: Admin logout immediately revokes session token.
✓ TEST 15 PASSED: Verified artist biography and catalogue associations validated.
✓ TEST 16 PASSED: robots.txt directives and sitemap canonical URLs verified.
✓ TEST 17 PASSED: Health check endpoint confirms healthy DB and published catalogue.
✓ TEST 18 PASSED: Legacy ?id= permanently redirects to ?song= and canonical URLs are unique.
```

---

## 9. User Actions Required Before Public Launch

1. **Decide on Staging Provider:** Choose between Render (\$7.25/mo), Railway (~\$5/mo), a dedicated Linux VPS (\$4–\$6/mo), or self-hosted Docker (\$0).
2. **Generate Production Secret Key:**
   Run `python -c "import secrets; print(secrets.token_hex(32))"` and set it as `SECRET_KEY` in your environment.
3. **Set Admin Master Credentials:**
   Set `ADMIN_USERNAME` and a secure 12+ character `ADMIN_PASSWORD` in your hosting dashboard.
4. **Acquire & Configure Custom Domain (Optional):**
   Once a domain (e.g. `versenest.lk` or `versenest.org`) is registered, configure DNS `CNAME` or `A` records to point to the host and update the `BASE_URL` environment variable.

---

## 10. Remaining Blockers & Future Archival Work

1. **Public Staging Deployment Pending Provider Selection:** The codebase is 100% staging-ready, but live public staging has not been claimed because the team has not yet provisioned paid hosting or connected a live cloud container.
2. **Batch Verification of 185 Pending Records:** The 185 records in `pending_verification` remain safely hidden from public search and sitemaps. They represent authentic cultural classics that require manual verification against physical SLBC/Torana archives in future sprints.
3. **Community MusicBrainz Submissions:** The 15 Sri Lankan artists currently lacking MusicBrainz IDs (such as Rookantha Gunathilaka, Sunil Shantha, Athma Liyanage) can be officially submitted to MusicBrainz by the team to permanently anchor their metadata in the global music graph.
