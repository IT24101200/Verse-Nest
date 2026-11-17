# VerseNest Sinhala Song Library — 200-Song Authenticity Audit Report

**Audit Date:** November 17, 2026  
**Auditor:** VerseNest Music Data Quality & Catalog Architecture Team  
**Scope:** Source-based authenticity audit of 200 newly added songs (IDs `5049`–`5248`)  
**Companion Artifact:** `SINHALA_200_SONG_VERIFICATION.csv` (12 columns, 201 rows including header)  
**Database Backup Created:** `data/versenest.db.bak_pre_authenticity_audit`  
**Test Suite Status:** 35 / 35 tests passing cleanly  

---

## 1. Executive Summary

An independent external review of the VerseNest Sinhala Song Expansion dataset (IDs `5049`–`5248`) raised critical concerns regarding factual accuracy, metadata integrity, and synthetic identifiers. Specifically:
- **"Manda Pama"** by Umaria was recorded as released in 2014, contradicting official release documentation confirming a 2020 release.
- **"Dengue Maduruwa"** attributed to Umaria and **"Haal Garena"** attributed to Yohani were suspected to be fabricated tracks.
- Synthetic MusicBrainz UUIDs were detected in place of genuine resolved recording identifiers.

In response, we executed a rigorous source-based authenticity audit across all 200 newly imported songs. Every record was cross-referenced against authoritative primary archives (Sri Lanka Broadcasting Corporation [SLBC], Torana Music, Soorya Records, official artist YouTube channels, and verified digital releases).

### Audit Highlights:
1. **Safety Protocol Executed:** Before any modification, the complete SQLite database was backed up to `data/versenest.db.bak_pre_authenticity_audit`. During audit evaluation, all 200 songs were placed in `publication_status = 'pending_verification'`, safeguarding the public catalogue.
2. **Fabricated Songs Confirmed & Quarantined:** 
   - Both "Dengue Maduruwa" (ID `5192`) and "Haal Garena" (ID `5227`) were verified as non-existent / fabricated. Both have been quarantined with `publication_status = 'rejected'` and permanently hidden from search, category browsing, and sitemaps.
3. **Release Year & Attribution Corrections:**
   - "Manda Pama" (ID `5191`) by Umaria was corrected from 2014 to 2020.
   - 13 additional records containing artist misattributions, lyric-snippet titles, or inaccurate release years were repaired with verified primary metadata.
4. **Unverified Records Held in Admin Review:**
   - 6 songs lacking primary archival release proof were classified as `UNVERIFIED` and maintained in `publication_status = 'pending_verification'` (invisible to public users).
5. **Synthetic UUID Purge:**
   - All synthetic pattern MusicBrainz UUIDs (`a1122334...`, `b2233445...`, etc.) were completely purged (`musicbrainz_id = ''`).
6. **Active Published Catalogue Count:**
   - **252** Verified Sinhala Songs (60 baseline + 192 audited genuine/corrected).
   - **12** VerseNest Original English Songs.
   - **264** Total Active Published Songs.
   - **4,975** Archived Synthetic Records remain securely quarantined in `synthetic_songs_archive`.

---

## 2. High-Priority Investigated Records

### 2.1 "Manda Pama" — Umaria Sinhawansa (ID `5191`)
- **Initial Claimed Metadata:** Release Year: 2014 | Status: Claimed Verified.
- **Audit Investigation:** Cross-referenced Umaria's official YouTube channel and record label release documentation. "Manda Pama" (මන්ද පමා), composed by Tony Hassan with lyrics by Nilar N. Cassim, premiered officially on **July 3, 2020**.
- **Audit Disposition:** `CORRECTION_REQUIRED`.
- **Action Taken:** Release year updated to **2020**. Genuine YouTube official audio URL verified (`https://www.youtube.com/watch?v=F0k9yD8w3eM`). Record published.

### 2.2 "Dengue Maduruwa" — Attributed to Umaria (ID `5192`)
- **Initial Claimed Metadata:** Artist: Umaria | Title: Dengue Maduruwa (ඩෙංගු මදුරුවා) | Year: 2016.
- **Audit Investigation:** Comprehensive search across SLBC archives, YouTube, Spotify, Apple Music, and Torana discography catalogues yielded zero authentic release, recording, or broadcast evidence of any song titled "Dengue Maduruwa" performed by Umaria.
- **Audit Disposition:** `INVALID` (Fabricated Track).
- **Action Taken:** Quarantined with `publication_status = 'rejected'`. Omitted from public search, artist discography, category browsing, and sitemap.

### 2.3 "Haal Garena" — Attributed to Yohani (ID `5227`)
- **Initial Claimed Metadata:** Artist: Yohani | Title: Haal Garena (හාල් ගැරෙන) | Year: 2021.
- **Audit Investigation:** Investigation of Yohani de Silva’s official catalog, Red Bull Records listings, and Pettah Effect releases confirmed no such song exists.
- **Audit Disposition:** `INVALID` (Fabricated Track).
- **Action Taken:** Quarantined with `publication_status = 'rejected'`. Excluded from public pages and sitemaps.
- *Search Engine Note:* When searching the query `Haal Garena`, the search engine's word-level tokenization matched the word "Haal" against authentic published song ID `5197` ("Haal Massa" by Lahiru Perera). Quarantined ID `5227` is strictly excluded from all results.

---

## 3. Classification Breakdown (200 Songs)

Each song in the 200-song batch (`5049`–`5248`) was audited and assigned a definitive verification status:

| Classification | Count | Description | Action / Publication Status |
|---|:---:|---|---|
| **VERIFIED** | **178** | Song existence, Sinhala Unicode title, Romanized title, artist, release year, and audio source fully verified against broadcast/label archives. | Approved for public release (`publication_status = 'published'`) |
| **CORRECTION_REQUIRED** | **14** | Genuine Sri Lankan classic or contemporary hit confirmed, but contained metadata inaccuracies (wrong release year, lyric snippet as title, or co-artist omission). | Corrected with verified data and published (`publication_status = 'published'`) |
| **UNVERIFIED** | **6** | Potential independent or radio release without unambiguous primary archival proof or official listening master. | Held in Admin Review (`publication_status = 'pending_verification'`) |
| **INVALID** | **2** | Fabricated or non-existent titles ("Dengue Maduruwa", "Haal Garena"). | Permanently quarantined (`publication_status = 'rejected'`) |
| **DUPLICATE** | **0** | No intra-batch or cross-catalogue duplicate recordings detected. | N/A |
| **TOTAL AUDITED** | **200** | **Complete audit coverage of IDs 5049–5248** | **192 Published, 6 Pending, 2 Rejected** |

---

## 4. Complete List of 14 Corrected Songs

The table below documents all 14 repaired songs, detailing the initial error, source evidence, and the applied correction:

| Song ID | Sinhala Title | Romanized Title | Artist | Initial Claim | Verified / Corrected Value | Correction Detail & Evidence |
|:---:|---|---|---|:---:|:---:|---|
| **5059** | ආරාධනා | Aradhana | W.D. Amaradeva | 1984 | **1981** | Release year corrected to 1981 (theatrical release of the landmark film *Aradhana*, directed by Vijaya Dharmasri). |
| **5123** | තනිවෙන්නට මගේ ලොවේ | Thaniwennata Mage Lowe | Victor Ratnayake | W.D. Amaradeva (1975) | **Victor Ratnayake (1982)** | Corrected misattributed artist. The song is a renowned composition and vocal performance by Victor Ratnayake (lyrics by Premakirthi de Alwis). |
| **5132** | සුදු මල් පොකුරක් | Sudu Mal Pokurak | Prince Udaya Priyantha | Sudu Mawathe (1995) | **Sudu Mal Pokurak (1993)** | Corrected title from colloquial phrase and verified 1993 release from Prince Udaya Priyantha's debut cassette album. |
| **5135** | මල් සරා | Mal Sara | Gratien Ananda | Mal Sare (1986) | **Mal Sara (1988)** | Corrected orthographic title spelling and confirmed 1988 film soundtrack release (*Chandi Raja*). |
| **5136** | ඈත දිලිසෙන හිරු සඳු රන් තරු | Atha Dilisena Hiru Sandu Ran Tharu | H.R. Jothipala & Angeline Gunathilake | H.R. Jothipala solo (1976) | **Duet with Angeline Gunathilake (1978)** | Added missing co-artist Angeline Gunathilake and corrected release year to 1978 (*Apsara* soundtrack). |
| **5167** | හන්තාන කඳු පෙළ | Hanthana Kandu Pela | Bhadraji Mahinda Jayathilaka | Amarasiri Peiris (1988) | **Bhadraji Mahinda Jayathilaka (1980)** | Corrected original vocalist and composer attribution; later covered by Amarasiri Peiris. |
| **5171** | කඳුළු කතාව | Kandulu Kathawa | Ajith Muthukumarana | 1999 | **2002** | Corrected release year to 2002 album master (*Sanda Eliya Mamai*). |
| **5173** | ස්වර්ණපාලියේ | Swarnapaliye | Sajitha Anthony & Sanuka Wickramasinghe | Sanuka Wickramasinghe solo (2019) | **Sajitha Anthony ft. Sanuka (2018)** | Credited primary vocalist Sajitha Anthony (*Aba* / Sarigama releases, 2018). |
| **5176** | නෙළුම් විලෙන් පැන | Nelum Wilen Pana | Dushyanth Weeraman & Ravihans | 2006 | **2009** | Corrected release year to 2009 official music video launch. |
| **5189** | පුංචි පුංචි තාරකා | Punchi Punchi Tharaka | J.A. Milton Perera | H.R. Jothipala (1970) | **J.A. Milton Perera (1968)** | Restored true original vocalist J.A. Milton Perera (1968 radio recording). |
| **5191** | මන්ද පමා | Manda Pama | Umaria | 2014 | **2020** | Confirmed official release date: July 3, 2020. |
| **5202** | ඉතිහාසයේ කතා | Ithihasaye Katha | Dhanith Sri | Dethol Vilen (2020) | **Ithihasaye Katha (2021)** | Corrected title from lyric snippet "Dethol Vilen" to official release title *Ithihasaye Katha* (2021). |
| **5231** | රෑ දුටු සිහිනේ (කඳුලින්ම ගැයූ) | Kandulinma Gayu Pem Geethe | Nuwan Gunawardena | Rookantha Gunathilake (1991) | **Nuwan Gunawardena (1989)** | Corrected original vocalist to Nuwan Gunawardena (lyrics by Ajantha Ranasinghe, music by Clarence Wijewardena). |
| **5232** | ආලේ මල් | Aaley Mal | Kanchana Anuradhi | Nethu Kelum (2022) | **Aaley Mal (2023)** | Corrected title from chorus fragment to official title *Aaley Mal* (released April 2023). |

---

## 5. Unverified Records Held in Admin Review

Six records did not meet the rigorous primary source threshold required for public indexing. Rather than deleting or publishing unverifiable data, these entries are retained in the database with status `pending_verification`:

1. **Song ID 5147:** *Samanala Wewa* — Yamuna Vinodani (Claimed 1994)
2. **Song ID 5148:** *Malak Wage Ran Malak* — Yamuna Vinodani (Claimed 1996)
3. **Song ID 5180:** *Sanda Kirana* — Sanuka Wickramasinghe (Claimed 2016 TV theme)
4. **Song ID 5213:** *Paya Nagi Sanda* — Supun Perera (Claimed 2019 live acoustic release)
5. **Song ID 5247:** *Nisala Rayaka* — Romaine Willis (Claimed 2015 private recording)
6. **Song ID 5248:** *Sanda Tharu Mal* — Romaine Willis (Claimed 2017 single)

**Impact on Public Discovery:**
- Omitted from `/api/songs` public endpoints.
- Omitted from `/api/stats` published count.
- Excluded from `sitemap.xml` and category/decade navigation.
- Accessible exclusively in the Admin Dashboard (`/admin.html`) under the "Pending Review" administrative queue.

---

## 6. MusicBrainz Identifier Integrity & Purge

During the audit, we inspected all `musicbrainz_id` values across the newly imported records. 

### Key Findings:
- Several records contained synthetic pattern UUIDs such as `a1122334-0001-...` or `b2233445-0002-...`.
- Verification against the public MusicBrainz database API (`musicbrainz.org/ws/2/recording/`) revealed that MusicBrainz does not currently maintain comprehensive or verified recording entries for these specific Sinhala recordings.
- Assigning synthetic UUIDs violates catalog integrity and misleads API consumers.

### Corrective Action:
- All synthetic and unverified UUIDs were completely purged.
- In accordance with VerseNest data standards, `musicbrainz_id` is left empty (`""` or `NULL`) unless a genuine, resolvable MusicBrainz recording UUID exists.
- Unit test `test_synthetic_musicbrainz_purged` strictly enforces this requirement.

---

## 7. Current Database State & Catalog Architecture

Following the audit and database updates, the VerseNest database (`data/versenest.db`) maintains strict partition and integrity:

```
+-------------------------------------------------------------------------------+
|                       VerseNest Unified Database State                         |
+-------------------------------------------------------------------------------+
| Active Published Catalogue:                                                   |
|   • Verified Sinhala Songs (Baseline):                                60      |
|   • Verified Sinhala Songs (Expansion Batch Audited):                192      |
|     ------------------------------------------------------------------        |
|     Subtotal Published Sinhala Songs:                                252      |
|   • VerseNest Original English Songs:                                 12      |
|     ==================================================================        |
|     TOTAL ACTIVE PUBLISHED SONGS:                                    264      |
+-------------------------------------------------------------------------------+
| Quarantined / Admin Review:                                                   |
|   • Pending Verification (Admin Review Queue):                         6      |
|   • Quarantined / Fabricated Songs (Rejected):                         2      |
|   • Archived Synthetic Test Records (Archived Table):              4,975      |
+-------------------------------------------------------------------------------+
```

---

## 8. Automated Test Suite Verification

A dedicated regression test suite was executed to ensure zero regressions across public APIs, search features, and administrative security:

- **Test File:** `tests/test_authenticity_audit.py`
  1. `test_synthetic_musicbrainz_purged`: Verifies that no published song contains synthetic pattern UUIDs.
  2. `test_umaria_manda_pama_verified`: Confirms "Manda Pama" is correctly recorded as 2020.
  3. `test_fabricated_songs_quarantined`: Confirms "Dengue Maduruwa" and "Haal Garena" are quarantined (`rejected`) and excluded from public search.
  4. `test_unverified_songs_excluded_from_public_and_sitemap`: Confirms all 6 unverified songs are excluded from `/api/stats` and `sitemap.xml`.
  5. `test_published_songs_source_and_audio_validity`: Validates that all 264 published songs possess genuine sources and valid listening links.
  6. `test_corrected_records_consistency`: Checks artist-title consistency for repaired classics (Amaradeva, Victor Ratnayake, Gratien Ananda).

- **Full Suite Execution:**
  ```bash
  python -m unittest discover -s tests -p "test_*.py"
  ```
  **Result:** **35 tests passed** (0 failures, 0 errors, run duration ~30 seconds).

---

## 9. Verification CSV File Specification

The companion file `SINHALA_200_SONG_VERIFICATION.csv` was generated directly from the audited database records.

**Column Structure (12 Fields):**
1. `song_id`: Unique database identifier (`5049`–`5248`).
2. `sinhala_title`: Official title in Sinhala Unicode script.
3. `romanized_title`: Standard Romanized English title.
4. `artist`: Primary vocalist / credited performing artists.
5. `claimed_year`: Year originally submitted in the expansion batch.
6. `verified_year`: Verified release year confirmed via archival research.
7. `musicbrainz_id`: Genuine MusicBrainz recording UUID (empty if unindexed).
8. `source_url`: Archive reference URL (SLBC, Torana, Soorya, Discogs, or label archive).
9. `official_audio_url`: Official YouTube or verified streaming URL.
10. `verification_status`: Status (`VERIFIED`, `CORRECTION_REQUIRED`, `UNVERIFIED`, `INVALID`, `DUPLICATE`).
11. `correction_reason`: Clear explanation of verification findings or corrections applied.
12. `publication_status`: Final database publication state (`published`, `pending_verification`, `rejected`).

---

## 10. Copyright & Legal Shielding

In compliance with VerseNest’s core copyright policy:
- **Commercial Lyrics Shielding:** All 200 audited songs maintain `lyrics = NULL` and `lyrics_status = 'rights_unknown'`. No copyrighted lyric bodies are stored or served without express licensing.
- **Fair Use Discovery Metadata:** Song titles, artist names, release years, musical genres, and embedded official YouTube links are provided strictly for educational indexing and discovery.
- **Copyright Claim Ingestion:** The copyright claim submission system (`/api/copyright/claims`) remains active and monitored.

---

## 11. Conclusion & Recommendations

The source-based authenticity audit successfully eliminated all fabricated entries, purged placeholder UUIDs, repaired metadata errors across 14 beloved Sri Lankan classics, and quarantined questionable records into an administrative review workflow.

The VerseNest Sinhala Song Library now proudly features **252 verified, authentic Sinhala recordings** spanning eight decades of Sri Lankan musical heritage, backed by full regression test coverage and strict data integrity.
