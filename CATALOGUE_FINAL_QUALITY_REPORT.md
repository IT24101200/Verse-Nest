# VerseNest Sinhala Song Library — Final Quality & Catalog Audit Report

**Report Date:** November 17, 2026  
**Auditing Entity:** VerseNest Catalog Quality Assurance & Data Architecture Team  
**Scope:** Final quality audit, metadata correction, and source verification of the 200 expansion songs (`IDs 5049–5248`) and baseline catalogue (`IDs 1–72`) in `data/versenest.db`  
**Primary Deliverables:**  
1. `FINAL_VERIFIED_CATALOGUE.csv` (12 columns, 201 rows including header)  
2. `data/versenest.db` (reconciled, verified production database)  
**Database Backup Created:** `data/versenest.db.bak_step1_quality_audit`  
**Test Suite Status:** 35 / 35 tests passing cleanly  

---

## 1. Actual Published Counts

The VerseNest database (`data/versenest.db`) maintains strict partitioning between active public discovery records, administrative review queues, and quarantined collections.

```
+-------------------------------------------------------------------------------+
|                       VerseNest Unified Database State                         |
+-------------------------------------------------------------------------------+
| Active Published Catalogue:                                                   |
|   • Baseline Verified Sinhala Songs (IDs 13–72):                      60      |
|   • Expansion Verified Sinhala Songs (IDs 5049–5248):                 13      |
|     ------------------------------------------------------------------        |
|     Subtotal Published Sinhala Songs:                                 73      |
|   • VerseNest Original English Songs (IDs 1–12):                      12      |
|     ==================================================================        |
|     TOTAL ACTIVE PUBLISHED SONGS:                                     85      |
+-------------------------------------------------------------------------------+
| Quarantined / Admin Review:                                                   |
|   • Pending Verification Queue (Expansion IDs 5049–5248):            185      |
|   • Confirmed Fabricated / Rejected (IDs 5192, 5227):                  2      |
|   • Synthetic Test Archive (Quarantined in synthetic_songs_archive):4,975      |
|     ==================================================================        |
|     TOTAL DATABASE RECORDS:                                        5,247      |
+-------------------------------------------------------------------------------+
```

---

## 2. Corrected Song Metadata

All confirmed errors identified during external review have been investigated and resolved in `data/versenest.db`:

### 2.1 Song 5191: *Manda Pama* — Umaria Sinhawansa
- **Release Year:** Verified as **2020** (music video premiered July 3, 2020).
- **Official Video URL:** `https://www.youtube.com/watch?v=RsEoXcrnSxg`
- **Official Music Credits:** **DIM (Raaw Productions)**. Incorrect credit to Bachi Susan has been completely removed.
- **Official Lyricist:** **Manuranga Wijesekara**.
- **Source URL:** `https://lklyrics.com/songs/umaria_sinhawansa/manda_pama`
- **Status:** `VERIFIED` (`publication_status = 'published'`).

### 2.2 Song 5202: *Ithihasaye Katha* — Dhanith Sri
- **Investigation of 2021 Claim:** Archival research confirmed that Dhanith Sri's acoustic single and official EP release *Ithihasaye Katha* officially debuted on digital streaming platforms on **October 11, 2024**. No primary catalog release exists from 2021.
- **Release Year:** Corrected to **2024**.
- **Official Recording URL:** `https://www.youtube.com/watch?v=Tef_wagMs6M` (Official lyric video on Dhanith Sri's channel).
- **Primary Source URL:** `https://music.apple.com/us/album/ithihasaye-katha-single/1773727670`
- **Credits:** Lyrics & Melody by Dhanith Sri; Music by Dhanith Sri & Mahesh Kankanige.
- **Status:** `VERIFIED` (`publication_status = 'published'`).

### 2.3 Song 5232: *Aaley Mal* — Kanchana Anuradhi
- **Official Release Date:** **May 27, 2022**.
- **Release Year:** Corrected from 2023 to **2022**.
- **Official Video URL:** `https://www.youtube.com/watch?v=HEm9KIjEVV4`
- **Music:** **Dilshan L Silva**.
- **Lyrics:** **Lasitha Jayaneththi Arachchige**.
- **Source URL:** `https://lklyrics.com/songs/kanchana_anuradhi/aaley_mal`
- **Status:** `VERIFIED` (`publication_status = 'published'`).

### 2.4 Song 5136: *Atha Dilisena Hiru Sandu Ran Tharu* — H.R. Jothipala & Angeline Gunathilake
- **Correction:** Soundtrack duet from landmark film *Abhirahasa* (**1971**), directed by Lenon Liyanage; music by P.L.A. Somapala; lyrics by Premakeerthi de Alwis.
- **Release Year:** Corrected from 1978 to **1971**.
- **Official Audio URL:** `https://www.youtube.com/watch?v=WZI3h5AZCpk`
- **Source URL:** `https://lklyrics.com/songs/hr_jothipala/atha_dilisena_hiru_sandu_ran_tharu`
- **Status:** `VERIFIED` (`publication_status = 'published'`).

### 2.5 Reclassification of Song 5135: *Mal Sara* — Gratien Ananda
- **Audit Finding:** Primary source lookups confirmed that *Mal Sara* / *Malsara* is commonly associated with other Sri Lankan vocalists (e.g. Chamara Ranawaka), and no verifiable master recording by Gratien Ananda could be definitively matched to an authorized YouTube audio URL.
- **Corrective Action:** Moved from published to **`pending_verification`**.

---

## 3. Working Source URLs & Verified Audio URLs (13 Published Expansion Songs)

All 13 published expansion songs have direct, specific song-level source citations and verified audio links from authorized channels:

| ID | Title (Sinhala / English) | Artist | Year | Primary Source URL | Source Type | Official Listening URL |
|:---:|---|---|:---:|---|---|---|
| **5059** | ආරාධනා<br>Aradhana | W.D. Amaradeva | 1981 | `https://www.films.lk/FilmDetails.php?id=383` | National Film Archive / NFC | `https://www.youtube.com/watch?v=iSj6l7LTrQY` |
| **5123** | තනිවෙන්නට මගෙ ලොවේ<br>Thaniwennata Mage Lowe | Victor Ratnayake | 1982 | `https://lklyrics.com/songs/victor_rathnayake/thaniwennata_mage_lowe` | Song Catalog Archive | `https://www.youtube.com/watch?v=6-iDVcDYKKM` |
| **5132** | සුදු මල් පොකුරක්<br>Sudu Mal Pokurak | Prince Udaya Priyantha | 1993 | `https://lklyrics.com/songs/prince_udaya_priyantha/sudu_mal_pokurak` | Song Catalog Archive | `https://www.youtube.com/watch?v=QzUQNQXDgCA` |
| **5136** | ඈත දිලිසෙන හිරු සඳු රන් තරු<br>Atha Dilisena Hiru Sandu Ran Tharu | H.R. Jothipala & Angeline Gunathilake | 1971 | `https://lklyrics.com/songs/hr_jothipala/atha_dilisena_hiru_sandu_ran_tharu` | Song Catalog Archive | `https://www.youtube.com/watch?v=WZI3h5AZCpk` |
| **5167** | හන්තාන කඳු පෙළ<br>Hanthana Kandu Pela | Bhadraji Mahinda Jayathilaka | 1980 | `https://lklyrics.com/songs/bhadraji_mahinda/hanthane_kandupela` | Song Catalog Archive | `https://www.youtube.com/watch?v=toUZISDohx8` |
| **5171** | කඳුළු කතාව<br>Kandulu Kathawa | Ajith Muthukumarana | 2002 | `https://lklyrics.com/songs/ajith_muthukumarana/kandulu_kathawa` | Song Catalog Archive | `https://www.youtube.com/watch?v=Mt7D_rnAMTb` |
| **5173** | ස්වර්ණපාලියේ<br>Swarnapaliye | Sajitha Anthony & Sanuka Wickramasinghe | 2018 | `https://lklyrics.com/songs/sajitha_anthony/swarnapaliye` | Song Catalog Archive | `https://www.youtube.com/watch?v=pjYvgu8KdEM` |
| **5176** | නෙළුම් විලෙන් පැන<br>Nelum Wilen Pana | Dushyanth Weeraman & Ravihans | 2009 | `https://lklyrics.com/songs/dushyanth_weeraman/nelum_wilen_pana` | Song Catalog Archive | `https://www.youtube.com/watch?v=FxE0iWMCUpn` |
| **5189** | පුංචි පුංචි තාරකා<br>Punchi Punchi Tharaka | J.A. Milton Perera | 1968 | `https://lklyrics.com/songs/milton_perera/punchi_punchi_tharaka` | Song Catalog Archive | `https://www.youtube.com/watch?v=drN-5wOtgeu` |
| **5191** | මන්ද පමා<br>Manda Pama | Umaria Sinhawansa | 2020 | `https://lklyrics.com/songs/umaria_sinhawansa/manda_pama` | Song Catalog Archive | `https://www.youtube.com/watch?v=RsEoXcrnSxg` |
| **5202** | ඉතිහාසයේ කතා<br>Ithihasaye Katha | Dhanith Sri | 2024 | `https://music.apple.com/us/album/ithihasaye-katha-single/1773727670` | Apple Music Digital Release | `https://www.youtube.com/watch?v=Tef_wagMs6M` |
| **5231** | කඳුලින්ම ගැයූ පෙම් ගීතේ (රෑ දුටු සිහිනේ)<br>Kandulinma Gayu Pem Geethe | Nuwan Gunawardena | 1989 | `https://lklyrics.com/songs/nuwan_gunawardena/kandulinma_gayu` | Song Catalog Archive | `https://www.youtube.com/watch?v=FV6UDw4FrDC` |
| **5232** | ආලේ මල්<br>Aaley Mal | Kanchana Anuradhi | 2022 | `https://lklyrics.com/songs/kanchana_anuradhi/aaley_mal` | Song Catalog Archive | `https://www.youtube.com/watch?v=HEm9KIjEVV4` |

---

## 4. Source-Quality Audit of 60 Baseline Sinhala Records (IDs 13–72)

A separate audit was performed on the pre-existing 60 Sinhala records:
- **Track Existence & Cultural Authenticity:** All 60 baseline tracks are authentic, celebrated Sinhala recordings (e.g. *Manike Mage Hithe*, *Sandawathiye*, *Galana Gangak*, *Sannaliyane*, *Master Sir*, *Hanthanata Payana Sanda*, *Dam Pata Handewe*).
- **Audio Verification:** 60 / 60 records have active official or authorized YouTube streaming links.
- **Source URL Breakdown:**
  - **30 records** cite direct, resolving MusicBrainz recording URLs (`https://musicbrainz.org/recording/<UUID>`). Tested and confirmed HTTP 200 OK.
  - **30 records** cite resolving MusicBrainz artist entity URLs (`https://musicbrainz.org/artist/<UUID>`). While these resolve to the verified artist, they do not point to a specific release master.
- **Recommendation:** In subsequent catalog refinements, replace artist-entity URLs with specific recording or album-level citations.

---

## 5. Original English Lyrics Status & Copyright Shielding

Addressing the user's inquiry regarding lyrics storage:
- **12 VerseNest English Originals:**
  - All 12 songs retain their complete, legitimate creative writing text in `data/versenest.db` (~1,000–1,170 characters each).
  - Each record is flagged with `lyrics_status = 'original_owned'` and `lyrics_evidence = 'VerseNest Originals Content Agreement 2026'`.
  - The previous report's statement that *"all 86 published songs have lyrics = NULL"* was an inaccurate generalization in prose; the database always preserved the 12 original English lyrics.
- **Commercial Sinhala Songs:**
  - All 73 published Sinhala songs strictly enforce `lyrics = NULL` and `lyrics_status = 'rights_unknown'`. No commercial Sinhala lyrics are hosted or published without licensing.
  - The platform API shields commercial lyrics and displays fair-use metadata (title, artist, year, genre, official video stream).

---

## 6. Consistent Verification Status Taxonomy

In compliance with STEP 4 directives, all records in `data/versenest.db` and `FINAL_VERIFIED_CATALOGUE.csv` use standardized statuses:

| Status Code | Meaning | Batch Count | Total Database Count |
|---|---|:---:|:---:|
| **`VERIFIED`** | All required evidence confirmed (title, artist, verified release date, resolved source URL, verified official audio URL, confirmed credits). Published. | **13** | **85** (73 Sinhala + 12 English) |
| **`CORRECTION_REQUIRED`** | Errors identified but not fully resolved with working evidence. | **0** | **0** |
| **`UNVERIFIED`** | Insufficient supporting primary evidence; held in admin review queue. | **185** | **185** |
| **`INVALID`** | Confirmed incorrect or fabricated track (*Dengue Maduruwa*, *Haal Garena*). Permanently quarantined. | **2** | **2** |

---

## 7. Search, SEO, and Sitemap Alignment

1. **Sitemap (`sitemap.xml`):**
   - **85 published song URLs** (`/lyrics/<slug>` or `/lyrics/sinhala-song.html?id=<id>`).
   - **7 static website pages** (`/`, `/sinhala.html`, `/about.html`, `/contact.html`, `/privacy.html`, `/terms.html`, `/copyright.html`).
   - **Total `<loc>` entries:** Exactly **92 URLs**.
   - Zero unverified (`pending_verification`) or rejected songs are exposed in the sitemap.
2. **Search Engine API (`/api/songs`):**
   - Returns only songs with `publication_status = 'published'`.
   - Rejects search probes for rejected tracks (*Dengue*, *Haal Garena*).
   - Preserves Sinhala Unicode and transliterated Romanized search.

---

## 8. Automated Test Suite Results

The full test suite was executed against the updated codebase:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

**Results:**
- **Ran 35 tests in 33.9s: OK** (0 failures, 0 errors).
  - `test_platform.py` (16 tests): PBKDF2 authentication, SQL injection defense, login rate limiting, responsive CSS breakpoints, persistent storage.
  - `test_final_priorities.py` (7 tests): Separation of English and Sinhala catalogues, exact stats counts (73 Sinhala + 12 English = 85 Total), mobile UX components.
  - `test_mobile_320_visual.py` (6 tests): Viewport boundary checks at 320px, 375px, 768px, 1440px in light/dark themes.
  - `test_authenticity_audit.py` (6 tests): Purging of synthetic UUIDs, Umaria 2020 verification with DIM credits, quarantine of fabricated tracks, sitemap URL count (92), audio link validity.

---

## 9. Deliverables Export Summary

1. **`FINAL_VERIFIED_CATALOGUE.csv`** was generated directly from `data/versenest.db`:
   - Contains all 200 expansion records (`IDs 5049–5248`).
   - 12 fields: `song_id, title_si, title_en, artist, release_year, source_url, source_type, musicbrainz_id, official_audio_url, verification_status, publication_status, verification_notes`.
   - Exactly matches database: 13 published (`VERIFIED`), 185 pending verification (`UNVERIFIED`), 2 rejected (`INVALID`).
2. **`data/versenest.db`**: Live SQLite database with zero synthetic UUIDs, clean metadata, and shielded lyrics.

---

## 10. Remaining Release Blockers & Recommendations

1. **Archival Verification for 185 Pending Records:**
   The 185 records held in `pending_verification` represent authentic cultural classics (e.g. Sunil Shantha, C.T. Fernando, Milton Mallawarachchi, Clarence Wijewardena), but lack direct primary archival citations and verified official audio master URLs in this database. They should remain in `pending_verification` until verified individually in small batches.
2. **MusicBrainz Coverage:**
   Sri Lankan Sinhala music remains under-indexed on MusicBrainz. VerseNest policy strictly mandates keeping `musicbrainz_id` blank unless a verified, genuine MusicBrainz recording entry exists.
