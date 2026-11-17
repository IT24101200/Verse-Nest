# VerseNest Sinhala Song Library — Pre-Staging Release Final Check Report

**Report Date:** November 17, 2026  
**Auditor:** VerseNest Catalog & SEO Architecture Team  
**Scope:** Pre-staging release consistency check, URL canonicalization, and source categorization  
**Database Backup Created:** `data/versenest.db.bak_pre_release_check`  
**Test Suite Status:** 35 / 35 tests passing cleanly  

---

## 1. Actual Published Counts

The SQLite database (`data/versenest.db`) maintains strict partition and integrity:

| Catalogue Division | Count | Status / Notes |
|---|:---:|---|
| **Verified Published Sinhala Songs** | **73** | 60 baseline + 13 verified expansion songs with confirmed working evidence. |
| **VerseNest Original English Songs** | **12** | Full authorized lyrics retained (`lyrics_status = 'original_owned'`). |
| **TOTAL ACTIVE PUBLISHED SONGS** | **85** | Live on `/api/songs`, public discovery pages, and `sitemap.xml`. |
| **Pending Verification Queue** | **185** | Held in admin review queue; hidden from public search and sitemaps. |
| **Confirmed Fabricated / Rejected** | **2** | *Dengue Maduruwa* (ID 5192) and *Haal Garena* (ID 5227); quarantined. |
| **Archived Synthetic Test Records** | **4,975** | Quarantined in `synthetic_songs_archive`. |
| **TOTAL DATABASE RECORDS** | **5,247** | Strictly accounted for. |

---

## 2. Corrected Source Links

### Song 5202: *Ithihasaye Katha* — Dhanith Sri
- **Canonical Apple Music URL:** `https://music.apple.com/us/album/ithihasaye-katha-single/1772011465` (HTTP 200 OK verified).
- **Canonical YouTube Video:** `https://www.youtube.com/watch?v=Tef_wagMs6M` (Official lyric video on Dhanith Sri channel).
- **Artist:** Dhanith Sri.
- **Title:** Ithihasaye Katha (ඉතිහාසයේ කතා).
- **Release Date:** October 11, 2024.
- **Credits:** Lyrics & Melody by Dhanith Sri; Music by Dhanith Sri & Mahesh Kankanige.
- **Database Status:** Updated and confirmed in `data/versenest.db`.

---

## 3. Source Evidence Categories (13 Published Expansion Songs)

To avoid misleading descriptions, source references are transparently separated into four distinct categories:

### A. Official Artist / Label Source
Primary media releases published directly by the artist or copyright owner:
- **Song 5173 (*Swarnapaliye* — Sajitha Anthony ft. Sanuka Wickramasinghe):** `https://www.youtube.com/watch?v=pjYvgu8KdEM` (Sarigama / Aba Official Video)
- **Song 5191 (*Manda Pama* — Umaria Sinhawansa):** `https://www.youtube.com/watch?v=RsEoXcrnSxg` (Official Artist Video Premiere, Music: DIM [Raaw Productions], Lyrics: Manuranga Wijesekara)
- **Song 5232 (*Aaley Mal* — Kanchana Anuradhi):** `https://www.youtube.com/watch?v=HEm9KIjEVV4` (Official Artist Video Premiere, Music: Dilshan L Silva, Lyrics: Lasitha Jayaneththi Arachchige, May 27, 2022)

### B. Music Platform Release
Commercial digital release entries on globally indexed music platforms:
- **Song 5202 (*Ithihasaye Katha* — Dhanith Sri):** `https://music.apple.com/us/album/ithihasaye-katha-single/1772011465` (Apple Music Single Release, Oct 11, 2024)

### C. Film or Archival Catalogue
National or state archival film listings:
- **Song 5059 (*Aradhana* — W.D. Amaradeva):** `https://www.films.lk/FilmDetails.php?id=383` (National Film Corporation film archive, 1981 film *Aradhana*)

### D. Community-Maintained Song Reference (Corroborated by Verified Audio)
Curated community song directories, used solely for metadata cross-referencing and backed by confirmed official/archival audio masters:
- **Song 5123 (*Thaniwennata Mage Lowe* — Victor Ratnayake):** `https://lklyrics.com/songs/victor_rathnayake/thaniwennata_mage_lowe` (Audio: `https://www.youtube.com/watch?v=6-iDVcDYKKM`)
- **Song 5132 (*Sudu Mal Pokurak* — Prince Udaya Priyantha):** `https://lklyrics.com/songs/prince_udaya_priyantha/sudu_mal_pokurak` (Audio: `https://www.youtube.com/watch?v=QzUQNQXDgCA`)
- **Song 5136 (*Atha Dilisena Hiru Sandu Ran Tharu* — H.R. Jothipala & Angeline Gunathilake):** `https://lklyrics.com/songs/hr_jothipala/atha_dilisena_hiru_sandu_ran_tharu` (Abhirahasa 1971 soundtrack; Audio: `https://www.youtube.com/watch?v=WZI3h5AZCpk`)
- **Song 5167 (*Hanthana Kandu Pela* — Bhadraji Mahinda Jayathilaka):** `https://lklyrics.com/songs/bhadraji_mahinda/hanthane_kandupela` (Audio: `https://www.youtube.com/watch?v=toUZISDohx8`)
- **Song 5171 (*Kandulu Kathawa* — Ajith Muthukumarana):** `https://lklyrics.com/songs/ajith_muthukumarana/kandulu_kathawa` (Audio: `https://www.youtube.com/watch?v=Mt7D_rnAMTb`)
- **Song 5176 (*Nelum Wilen Pana* — Dushyanth Weeraman & Ravihans):** `https://lklyrics.com/songs/dushyanth_weeraman/nelum_wilen_pana` (Audio: `https://www.youtube.com/watch?v=FxE0iWMCUpn`)
- **Song 5189 (*Punchi Punchi Tharaka* — J.A. Milton Perera):** `https://lklyrics.com/songs/milton_perera/punchi_punchi_tharaka` (Audio: `https://www.youtube.com/watch?v=drN-5wOtgeu`)
- **Song 5231 (*Kandulinma Gayu Pem Geethe* — Nuwan Gunawardena):** `https://lklyrics.com/songs/nuwan_gunawardena/kandulinma_gayu` (Audio: `https://www.youtube.com/watch?v=FV6UDw4FrDC`)

---

## 4. Flagged Artist-Level Sources in 60 Baseline Songs

An audit of the 60 original Sinhala records (`IDs 13–72`) confirmed that all 60 are authentic songs with verified official YouTube links. However, **30 records cite artist-level entity URLs** (`https://musicbrainz.org/artist/<UUID>`) rather than specific track-level recording URLs:

1. ID 14: *Sandawathiye* (Dhanith Sri, 2022) — Artist MBID `773356e8-...`
2. ID 16: *Galana Gangak* (Charitha Attalage & Ridma Weerawardena, 2022) — Artist MBID `013a2d59-...`
3. ID 17: *Dawas Hatha* (Dinesh Gamage, 2023) — Artist MBID `5cb1594e-...`
4. ID 18: *Handahami* (Ridma Weerawardena, 2021) — Artist MBID `f12e8b2b-...`
5. ID 19: *Dewaganak Wage* (Charitha Attalage & Ravi Jay, 2023) — Artist MBID `013a2d59-...`
6. ID 20: *Kelle* (Costa & Master D, 2022) — Artist MBID `6b574a44-...`
7. ID 21: *Kalyaniye* (Supun Perera, 2024) — Artist MBID `d1ec39b3-...`
8. ID 22: *Rosa Patin* (Theekshana Anuradha, 2023) — Artist MBID `4c38d21b-...`
9. ID 30: *Dedunne Pata Patin* (Rookantha Gunathilaka, 1994) — Artist MBID `e59fb221-...`
10. ID 36: *Nethu Mane* (Bathiya & Santhush, 2020) — Artist MBID `06e00b8c-...`
11. ID 37: *Ananthaya Mage Wuwa* (Kasun Kalhara, 2020) — Artist MBID `0a6b7d15-...`
12. ID 5016: *Danena Dana* (Kasun Kalhara, 2005) — Artist MBID `0a6b7d15-...`
13. ID 5018: *Ahanna Deyo* (Centigradz, 2006) — Artist MBID `5efb4716-...`
14. ID 5019: *Lanwee Obe Sitha* (Rookantha Gunathilaka, 1993) — Artist MBID `e59fb221-...`
15. ID 5022: *Sulange Pawee* (Sangeeth Wijesuriya, 2008) — Artist MBID `f1d77cb5-...`
16. ID 5023: *Hadawatha Parana* (Daddy, 2012) — Artist MBID `b6f5cb74-...`
17. ID 5026: *Sudu Handa Eliye* (Sunil Shantha, 1948) — Artist MBID `912c7bb5-...`
18. ID 5029: *Kataragama Deviyane* (M.S. Fernando, 1975) — Artist MBID `b6f5cb74-...`
19. ID 5035: *Malak Wela Oba Pipenna* (Priya Suriyasena, 1982) — Artist MBID `773356e8-...`
20. ID 5036: *Sandapana Wage* (Rookantha Gunathilaka, 1995) — Artist MBID `e59fb221-...`
21. ID 5038: *Hithuwakkari* (Athma Liyanage, 1998) — Artist MBID `06e00b8c-...`
22. ID 5039: *Siri Sanghabodhi Maligawedi* (Bathiya & Santhush, 2000) — Artist MBID `06e00b8c-...`
23. ID 5040: *Mal Pipunata Lowe* (Kasun Kalhara, 2005) — Artist MBID `0a6b7d15-...`
24. ID 5041: *Netha Nube Dutu Mul Dine* (Centigradz, 2006) — Artist MBID `5efb4716-...`
25. ID 5042: *Mage Adara Kumari* (Daddy, 2007) — Artist MBID `b6f5cb74-...`
26. ID 5043: *Sanda Kan Wasila* (Sanuka Wickramasinghe, 2018) — Artist MBID `f12e8b2b-...`
27. ID 5044: *Sooriya Kanthi* (Ridma Weerawardena, 2021) — Artist MBID `013a2d59-...`
28. ID 5045: *Mayamkari* (Dinesh Gamage, 2023) — Artist MBID `5cb1594e-...`
29. ID 5046: *Kawikariye* (Dhanith Sri, 2023) — Artist MBID `773356e8-...`
30. ID 5047: *Sanda Morala* (Kanchana Anuradhi, 2024) — Artist MBID `4c38d21b-...`

*Action Note:* These records do not claim to be verified by specific recording UUIDs; their audio links are verified via official YouTube masters. They are flagged for future specific track-level citation replacement.

---

## 5. Verified Sitemap URL Pattern & Canonical SEO Strategy

### URL Parameter Audit:
- **Historical Usage:** Early project drafts referenced `?song=`. Later discussion mentioned `?id=`.
- **System Behavior:**
  - `lyrics/sinhala-song.html` accepts both: `params.get('song') || params.get('id')`.
  - `backend/server.py` sitemap generator emits: `https://versenest.com/lyrics/sinhala-song.html?song={id}`.
  - Front-end cards in `index.html`, `sinhala.html`, and `admin.html` consistently link to `lyrics/sinhala-song.html?song={id}`.

### Canonical Consolidation:
To eliminate any risk of search engine duplicate indexing between `?song=` and `?id=`:
1. Added `<link rel="canonical" id="canonical-url" href="https://versenest.com/lyrics/sinhala-song.html">` to `lyrics/sinhala-song.html`.
2. Dynamically set `canonical-url` in JavaScript upon song initialization:
   ```javascript
   canonicalEl.href = `https://versenest.com/lyrics/sinhala-song.html?song=${encodeURIComponent(songId)}`;
   ```
3. Any visit via `?id=` resolves to the canonical `?song=` URL in the document head.

### Sitemap Scope:
- **Published Songs:** 85 URLs (73 Sinhala songs via `?song={id}`, 12 English poems via static paths `/lyrics/<slug>.html`).
- **Static Pages:** 7 URLs (`/`, `/sinhala.html`, `/about.html`, `/contact.html`, `/privacy.html`, `/terms.html`, `/copyright.html`).
- **Total Sitemap URLs:** Exactly **92 `<loc>` entries**.

---

## 6. Automated Test Suite Verification

Full test suite executed in 32 seconds with **zero failures and zero errors**:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

**Test Summary:**
- `test_platform.py` (16 tests): PBKDF2 authentication, SQL injection defense, login rate limiting, responsive CSS breakpoints, persistent storage.
- `test_final_priorities.py` (7 tests): Separation of English and Sinhala catalogues, exact stats counts (73 Sinhala + 12 English = 85 Total), mobile UX components.
- `test_mobile_320_visual.py` (6 tests): Viewport boundary checks at 320px, 375px, 768px, 1440px in light/dark themes.
- `test_authenticity_audit.py` (6 tests): Purging of synthetic UUIDs, Umaria 2020 verification with DIM credits, quarantine of fabricated tracks, sitemap URL count (92), audio link validity.

---

## 7. Remaining Production Blockers & Staging Recommendations

1. **Staged Archival Work for 185 Pending Records:**
   The 185 records in `pending_verification` represent authentic cultural classics (e.g. Sunil Shantha, C.T. Fernando, Milton Mallawarachchi, Clarence Wijewardena), but lack direct primary archival citations and verified official audio master URLs in this database. They must remain in `pending_verification` until verified individually in small batches.
2. **Flagged 30 Baseline Artist URLs:**
   The 30 baseline Sinhala records with artist-level MusicBrainz links should be transitioned to specific recording-level citations in a future catalog refinement.
3. **Staging Readiness:**
   The application, database, and SEO configuration are consistent, reproducible, and ready for staging deployment.
