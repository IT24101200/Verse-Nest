# VerseNest — Production Go-Live & Cloud Storage Resolution Report

**Report Date:** November 19, 2026  
**Auditor / Team:** VerseNest Core Platform & DevOps Team  
**Live Target Host:** [https://verse-nest.onrender.com](https://verse-nest.onrender.com)  
**Git Repository:** `IT24101200/Verse-Nest` (Branch: `main`)  
**Deployment Infrastructure:** Render Cloud Web Service  
**Final Production Decision:** **CONDITIONAL GO (Application 100% Ready; Blocked on Manual Render Plan Upgrade)**

---

## 1. Executive Summary & Critical Storage Finding

A rigorous deployment inspection was conducted to resolve the persistent storage blocker identified in `PRODUCTION_LAUNCH_CHECKLIST.md`.

### Critical Finding Confirmed
1. **Active Compute Plan:** The live web service at `https://verse-nest.onrender.com` is running on Render's **Free Web Service Tier**, not a paid Starter plan.
2. **Persistent Disk Status:** Render strictly prohibits attaching persistent disks to Free tier services. As a result, the live container currently operates on an ephemeral local filesystem.
3. **Data Lifecycle on Free Tier:** On startup, `ensure_database_ready()` safely seeds the ephemeral filesystem from `data_seed/versenest.db` (1.64 MB). The database survives idle container spin-downs, but **any runtime modifications made to the database would be lost during a redeployment or container rebuild**.
4. **Architectural Parity:** While `render.yaml` specifies `plan: starter` with disk `versenest-data` (`mountPath: /app/data`), Render **does not automatically convert an active Free service into a paid plan** without user authorization in the Render Dashboard.

---

## 2. Phase 1 — Storage and Data Safety Audit

| Check | Target | Findings & Verified Action | Status |
|---|---|---|:---:|
| **SQLite Path** | Container runtime | `/app/data/versenest.db` configured via `DB_PATH` in `backend/database.py`. | **PASS** |
| **Startup Protection** | `ensure_database_ready()` | Confirmed: When `/app/data/versenest.db` exists and is > 0 bytes, bootstrapping code **never overwrites** it. | **PASS** |
| **Seed Database Integrity** | `data_seed/versenest.db` | Verified 272 records total: 85 published songs, 185 pending verification, 2 rejected. `PRAGMA integrity_check` -> `ok`. | **PASS** |
| **Sensitive Data Audit** | `data_seed/versenest.db` | Purged legacy test records from `revoked_tokens` and `login_attempts`. `copyright_requests` contains 0 records. | **CLEAN** |
| **Backup Redundancy** | Multiple locations | 1. Local active: `data/versenest.db`<br>2. Local snapshot: `data/versenest.db.bak_pre_production_prep`<br>3. Off-site Git repo: `data_seed/versenest.db` | **PASS** |

---

## 3. Phase 2 — Render Hosting Configuration & Port Handling

### Dynamic Port Binding Fix
* In [Dockerfile](file:///e:/Projects/versenest_website/versenest_website/Dockerfile), the default entrypoint was updated from `--port 8080` to dynamically bind to the port assigned by Render:
  ```dockerfile
  CMD ["sh", "-c", "exec uvicorn backend.server:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]
  ```
* This guarantees compatibility whether running locally on port 8080, inside Docker Compose, or on Render's dynamic cloud port (`$PORT`).

### Expected Hosting Costs & Plan Requirements
To activate persistent disk storage and eliminate cold starts, the account owner must configure the following in the Render Dashboard:

| Resource | Required Tier | Monthly Cost | Purpose |
|---|---|:---:|---|
| **Web Service Instance** | Starter Plan | $7.00 / month | Always-on compute; eliminates 50s cold start spin-down. |
| **Persistent Disk** | 1 GB SSD (`versenest-data`) | $0.25 / month | Mounted at `/app/data` to permanently preserve `versenest.db`. |
| **Total Hosting Cost** | — | **$7.25 / month** | Full cloud data persistence. |

---

## 4. Phase 3 — Database Persistence Verification

### Local & Container Lifecycle Verification
Automated staging lifecycle tests ([tests/test_staging_lifecycle.py](file:///e:/Projects/versenest_website/versenest_website/tests/test_staging_lifecycle.py)) were executed with 100% success across 6 test stages:
1. Fresh volume initialization from seed.
2. Verified 85 published songs (73 Sinhala + 12 Originals).
3. Inserted private temporary test record (`staging-persist-test-xxx`).
4. Simulated container reboot and connection pool reset.
5. Confirmed test record survived reboot across sessions.
6. Atomic online backup generated and test record cleanly deleted.

### Cloud Persistence Diagnostics
* On the live cloud service, the database survived idle suspension and woke up with all 85 published songs intact.
* Cloud redeployment persistence was **not tested on Render** because persistent disks are not supported on the Free tier and dashboard credentials are not available in this workspace.

---

## 5. Phase 4 — Production SEO & Sitemap Verification

### Sitemap URL Recalculation (Exact Count: 92 URLs)
The dynamic sitemap generator at `/sitemap.xml` was audited to verify canonical coverage:

```
  7 Static Root Pages:
    - / (Homepage)
    - /sinhala.html (Sinhala Library)
    - /about.html
    - /contact.html
    - /copyright.html
    - /privacy.html
    - /terms.html
+ 73 Verified Sinhala Song Detail Pages (/lyrics/sinhala-song.html?song={id})
+ 12 VerseNest English Originals Detail Pages (/lyrics/{slug}.html)
--------------------------------------------------------------------------------
= 92 Total Canonical URLs
```

* **Exclusions Verified:**
  * 185 `pending_verification` tracks: Strictly excluded from sitemap.
  * 2 `rejected` tracks: Strictly excluded from sitemap.
  * Admin portal routes (`/admin`, `/admin.html`, `/api/admin/*`): Disallowed in `robots.txt`.

### Staging vs. Production SEO Switch State
* **Current State:** Staging crawler blocking is **ACTIVE** (`User-agent: *\nDisallow: /` and `X-Robots-Tag: noindex, nofollow, noarchive`).
* **Switch Mechanism:** Setting `ENV=production` in Render environment variables automatically disables `X-Robots-Tag: noindex` and allows search indexing.

---

## 6. Phase 5 — Security & Rights Compliance

1. **Administrator Authentication:** Protected via PBKDF2 password hashing (100,000 iterations), HMAC session tokens, and IP brute-force rate limiting (HTTP 429).
2. **API Endpoint Security:** All `/api/admin/*` endpoints require valid `Authorization: Bearer <token>`. Unauthorized requests return HTTP 401.
3. **Sensitive Data Protection:** `/api/health` returns operational health metrics without exposing file paths, environment secrets, or user data.
4. **Copyright & DMCA Workflow:** Public takedown form at `/copyright.html` routes to `POST /api/copyright/report`, registering complaints into `copyright_requests` for editorial review.
5. **Zero Commercial Scraped Lyrics:** Unverified commercial lyrics remain strictly shielded.

---

## 7. Remaining Manual Actions for Launch

The following 3 manual steps must be completed in the **Render Dashboard** by the project owner:

1. **Step 1: Upgrade Web Service to Starter Plan**
   * Go to [Render Dashboard](https://dashboard.render.com/) -> Select `verse-nest`.
   * **Settings** -> **Instance Type** -> Select **Starter** ($7/mo).
2. **Step 2: Attach Persistent Disk**
   * Go to **Disks** tab -> Click **Add Disk**.
   * Name: `versenest-data`
   * Mount Path: `/app/data`
   * Size: `1 GB` ($0.25/mo).
3. **Step 3: Update Environment Variables**
   * Go to **Environment** tab:
     * Set `ENV`: `production`
     * Set `BASE_URL`: `https://verse-nest.onrender.com` (or your custom domain)
     * Set `ADMIN_PASSWORD`: Generate a strong 32-character password.
     * Set `SECRET_KEY`: Generate a strong 64-character secret.
   * Click **Save Changes** (Render will trigger a production redeploy with persistent storage).

---

## 8. Final GO / NO-GO Decision

| Component | Status | Decision |
|---|:---:|:---:|
| **Frontend UI & Responsive Design** | 100% Verified (0 horizontal overflow) | **GO** |
| **Song Catalogue & Authenticity** | 85 Verified Songs (73 Sinhala + 12 Originals) | **GO** |
| **Pending Track Isolation** | 185 tracks quarantined | **GO** |
| **Application Server & Security** | FastAPI / Uvicorn / JWT / PBKDF2 | **GO** |
| **Production SEO & Sitemap** | 92 canonical URLs ready | **GO** |
| **Cloud Persistent Storage** | Requires Render Starter Upgrade | **HOLD (PENDING USER ACTION)** |
| **OVERALL LAUNCH STATUS** | **CONDITIONAL GO** | **Proceed to launch immediately upon completing the 3 Render Dashboard steps above.** |
