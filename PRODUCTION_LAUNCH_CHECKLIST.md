# VerseNest — Production Launch & Cloud Readiness Checklist

**Document Date:** November 19, 2026  
**Auditor:** VerseNest DevOps & Full-Stack Platform Team  
**Live Target Host:** [https://verse-nest.onrender.com](https://verse-nest.onrender.com)  
**Git Repository:** `IT24101200/Verse-Nest` (Branch: `main`)  
**Deployment Blueprint:** `render.yaml`  
**Overall Readiness:** **STAGING VERIFIED — READY FOR PRODUCTION SWITCH**

---

## 1. Actual Live Service Status & Diagnostics

All checks were performed live against `https://verse-nest.onrender.com`:

| Check | Live Endpoint / Parameter | Verified Result | Status |
|---|---|---|:---:|
| **Root URL Response** | `GET https://verse-nest.onrender.com/` | HTTP 200 OK (Cloudflare edge + Uvicorn) | **PASS** |
| **Health API** | `GET https://verse-nest.onrender.com/api/health` | `status: "healthy"`, `environment: "staging"` | **PASS** |
| **Database Status** | `database.connected` | `true`, `integrity: "ok"` | **PASS** |
| **Active Catalogue Count** | `database.published_songs` | **85 published songs** (73 Sinhala + 12 Originals) | **PASS** |
| **Pending Tracks** | `publication_status = 'pending_verification'` | **185 tracks** (quarantined from public pages/sitemaps) | **PASS** |
| **Fabricated Tracks** | `publication_status = 'rejected'` | **2 tracks** (*Dengue Maduruwa*, *Haal Garena*) quarantined | **PASS** |
| **Deployed Git Commit** | `0982737` / `7f818cd` / `16b460f` | Verified latest CSS & dynamic 2020s commentary | **PASS** |
| **Browser Console Errors** | Automated Headless Chrome scan | **0 Console Errors** | **PASS** |
| **Network Asset Failures** | Headless Chrome asset scan | **0 Failed Requests** | **PASS** |

---

## 2. Render Compute Plan & Persistent Disk Investigation

### Investigation of Idle Spin-Down Claim
* **Observed Cloud Behavior:** On the initial request to `https://verse-nest.onrender.com`, the connection experienced a cold start delay (~50 seconds) before returning HTTP 200.
* **Root Cause Analysis:**
  1. On Render, **Starter Plan ($7/mo)** instances are always-on and **never spin down**.
  2. In contrast, Render's **Free Web Service Tier** automatically suspends (spins down) container instances after 15 minutes of inactivity.
  3. Furthermore, **Persistent Disks cannot be attached to Free Web Services** on Render; persistent disks strictly require a paid plan (Starter or higher).
  4. Although `render.yaml` specifies `plan: starter` with disk `versenest-data` (`mountPath: /app/data`), the currently active live instance was deployed under Render's **Free Tier**.
  5. The container currently operates on an ephemeral filesystem bootstrapped at startup from `data_seed/versenest.db`.
* **Action Required for True Production:**
  To prevent cold starts and ensure permanent disk writes survive redeployments, the team must apply the `render.yaml` Blueprint via Render Dashboard to provision the **Starter Plan** with the 1 GB persistent disk attached.

---

## 3. Database Persistence & Backup Verification

### Local Staging Parity Tests
* **Lifecycle Test Suite:** Automated test suite [tests/test_staging_lifecycle.py](file:///e:/Projects/versenest_website/versenest_website/tests/test_staging_lifecycle.py) passed all 6 lifecycle stages:
  1. Fresh volume bootstrapping from seed database (`data_seed/versenest.db`).
  2. Zero-overwrite protection when target `/app/data/versenest.db` exists.
  3. Insertion of temporary private test record (`staging-persist-test-xxx`).
  4. Simulated container reboot and connection pool recycle.
  5. Verification that test record survived reboot across sessions.
  6. Atomic SQLite online backup generation and test record cleanup.

### Cloud Persistence Diagnostics
* **Live Service Wakeup:** Following container spin-down, the SQLite database woke up intact with all 85 published songs, 185 pending songs, and `PRAGMA integrity_check: ok`.
* **Redeployment Note:** Cloud-level redeployment test using the Render Dashboard was **not performed** because dashboard credentials and Render API keys are not stored in this workspace (*"Redeploy the service using the Render dashboard if access and authorization are available. Do not claim success for any test not performed."*).
* **Backup Snapshots Created:**
  * Active Local DB: `data/versenest.db` (1.64 MB)
  * Pre-Production Local Snapshot: `data/versenest.db.bak_pre_production_prep` (1.64 MB)
  * Version-Controlled Seed & Off-Site Backup: `data_seed/versenest.db` (1.64 MB, committed to GitHub `IT24101200/Verse-Nest`)

---

## 4. Current Staging Security & Privacy Configuration

| Setting | Live Value | Verification Evidence |
|---|---|---|
| **`ENV` Variable** | `staging` | Verified in `/api/health` response: `"environment": "staging"` |
| **`robots.txt`** | `User-agent: *\nDisallow: /` | Crawler blocking active; prevents premature search indexing |
| **HTTP Security Header** | `X-Robots-Tag: noindex, nofollow, noarchive` | Injected into all responses by server middleware |
| **Google AdSense** | Completely Disabled | Scanned all `.html` templates; 0 AdSense tags or trackers |
| **Credentials Exposure** | Zero Secrets Exposed | Scanned all public JS and HTML; zero API keys or passwords |
| **Admin Authentication** | Securely Gated | `POST /api/admin/login` enforces PBKDF2 password hashing & rate limiting |

---

## 5. Step-by-Step Production Switch Procedure

When the team is ready to launch the public production website, execute the following steps in order:

### Step 1: Update Environment Variables in Render Dashboard
Log in to the [Render Dashboard](https://dashboard.render.com/) -> Select `verse-nest` (or `versenest-staging`) -> **Environment**:

| Key | Staging Value | Final Production Value | Purpose |
|---|---|---|---|
| `ENV` | `staging` | `production` | Disables `X-Robots-Tag: noindex` and allows search indexing |
| `BASE_URL` | `http://localhost:8080` | `https://versenest.org` (or `https://verse-nest.onrender.com`) | Generates correct canonical URLs and XML sitemap |
| `ADMIN_PASSWORD` | *(auto-generated)* | Strong 32-character random string | Secures production administrator dashboard |
| `SECRET_KEY` | *(auto-generated)* | Strong 64-character random string | Signs admin session tokens securely |

### Step 2: Attach Persistent Disk (Upgrade to Starter Plan)
1. In Render Dashboard -> **Settings** -> **Compute Plan** -> Select **Starter** ($7/mo).
2. Go to **Disks** -> Click **Add Disk**:
   * **Name:** `versenest-data`
   * **Mount Path:** `/app/data`
   * **Size:** `1 GB` ($0.25/mo)
3. Save changes. Render will automatically redeploy the container with persistent storage mounted.

### Step 3: Verify Dynamic Production SEO & Sitemap
Once `ENV=production` is active:
1. `GET /robots.txt` will automatically transition to:
   ```text
   User-agent: *
   Allow: /
   Disallow: /admin
   Disallow: /admin.html
   Disallow: /api/admin/

   Sitemap: https://verse-nest.onrender.com/sitemap.xml
   ```
2. `GET /sitemap.xml` will dynamically render all 85 canonical URLs prefixed with the production `BASE_URL`:
   * 7 Static pages: `/`, `/sinhala.html`, `/about.html`, `/contact.html`, `/copyright.html`, `/privacy.html`, `/terms.html`.
   * 73 Verified Sinhala song pages: `/lyrics/sinhala-song.html?song={id}`.
   * 12 Original creative lyric pages.

### Step 4: Connect Google Search Console
1. Navigate to [Google Search Console](https://search.google.com/search-console).
2. Add Property -> Enter your production domain (e.g., `https://verse-nest.onrender.com` or custom domain).
3. Verification method: Add the Google verification meta tag to the `<head>` of `index.html` or upload the HTML verification file to the web root.
4. Submit sitemap URL: `https://<YOUR-DOMAIN>/sitemap.xml`.

### Step 5: Verify Legal Pages & Copyright Protections
* Confirm all 5 legal and compliance pages are published and accessible:
  * [about.html](file:///e:/Projects/versenest_website/versenest_website/about.html) — Project mission & cultural preservation.
  * [contact.html](file:///e:/Projects/versenest_website/versenest_website/contact.html) — Public inquiry and communications channel.
  * [copyright.html](file:///e:/Projects/versenest_website/versenest_website/copyright.html) — Rights attribution, DMCA takedown procedure, zero-scraped-lyrics policy.
  * [privacy.html](file:///e:/Projects/versenest_website/versenest_website/privacy.html) — Transparent privacy policy adhering to student and privacy guidelines.
  * [terms.html](file:///e:/Projects/versenest_website/versenest_website/terms.html) — Educational terms of use.

---

## 6. Pre-Launch Blocker Audit

| Item | Status | Action Required Before Production |
|---|:---:|---|
| **UI Responsiveness & Layout** | **CLEAN** | None. All 8 viewports verified with zero overflow. |
| **Catalogue Authenticity** | **CLEAN** | None. 85 published songs verified against genuine recordings. |
| **Pending Track Isolation** | **CLEAN** | None. 185 unverified tracks safely quarantined. |
| **Render Plan Upgrade** | **PENDING** | Team must upgrade service from Free to Starter in Render dashboard to activate Persistent Disk and eliminate cold starts. |
| **Production Domain / BASE_URL** | **PENDING** | Set `BASE_URL` in Render environment variables once final domain is designated. |
| **Public Search Indexing** | **INTENTIONALLY BLOCKED** | Switch `ENV=production` only when officially ready for public launch. |
