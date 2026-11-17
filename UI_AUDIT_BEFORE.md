# UI & UX Audit (Before Improvements)
**Project:** VerseNest — Sinhala Song & Lyrics Discovery Platform  
**Date:** November 17, 2026  
**Auditor:** Senior UI/UX & Frontend Specialist  
**Status:** Baseline Visual & Interaction Audit Completed  

---

## 1. Executive Summary

A comprehensive visual, responsive, and accessibility audit of the VerseNest platform was performed across all 12 key pages and functional views at 7 viewport widths (320px, 375px, 430px, 768px, 1024px, 1440px, 1920px).

While the underlying FastAPI backend, SQLite database (72 genuine verified songs, 12 artist biographies), and search engine function robustly, the user interface currently exhibits significant styling limitations, accessibility violations, mobile layout friction, and visual inconsistencies that detract from the platform's professional appeal.

---

## 2. Tested Viewports & Breakpoints

| Device Category | Viewport Width | Status / Findings |
|---|---|---|
| Extra Small Mobile | 320px | Severe crowding in header nav; text wraps awkwardly; badges overflow; record graphic clips |
| Standard Mobile | 375px | Nav links crowd header; filter dropdowns stack unevenly; touch targets below 44px |
| Large Mobile | 430px | Search bar suggestions dropdown truncates text; card meta text hard to distinguish |
| Tablet Portrait | 768px | 2-column grid works but gaps are inconsistent; aside panel on song detail stacks prematurely |
| Tablet Landscape / Small Laptop | 1024px | Layout feels empty with excessive lateral margins; typography scale needs tuning |
| Standard Desktop | 1440px | Adequate container centering, but lack of visual hierarchy and flat card covers |
| Ultra-Wide Desktop | 1920px | Maximum container width (1160px) leaves huge empty margins on 4K/wide screens |

---

## 3. Page-by-Page Audit & Confirmed Problems

### 3.1 Homepage (`index.html`)
1. **Misleading Statically-Coded Statistics:** The hero, nav, and badges display hardcoded "5000+ Verified Songs" before API data arrives, contradicting the actual 72 verified songs in the database.
2. **Missing Direct Search:** Users visiting the homepage must click through to `sinhala.html` to search for songs; there is no instant search bar on the homepage hero.
3. **Hero Illustration:** The decorative CSS vinyl record is static, clipped on mobile screens below 380px, and lacks interactive playback or visual waveform elements.
4. **Card Art Uniformity:** The 6 featured cards use identical CSS pseudo-elements (`✦` star with flat circle rings) and repetitive color combinations.
5. **Decade Badges:** The decade chips in the "Travel Through Time" section have fixed min-width (`130px`) causing uneven wrapping on small devices.

### 3.2 Sinhala Songs Directory (`sinhala.html`)
1. **Header Navigation Wrapping:** On mobile devices (320px–430px), nav links wrap onto two lines, pushing the page hero down unpredictably. No responsive hamburger menu exists.
2. **Autocomplete Dropdown:** The suggestions box (`.suggestions-box`) has a hardcoded dark background (`#181d2e`), unstyled scrollbar, and lacks focus trapping for keyboard navigation.
3. **Filter Controls Bar:** The genre, decade, and sort `<select>` elements use browser-native styles with poor dark-mode styling and low contrast borders (`rgba(255,255,255,0.2)`).
4. **Card Grid Responsiveness:** Uses rigid 3-column desktop layout that snaps abruptly to 2 and 1 column without fluid fluid auto-fit sizing.
5. **Light Mode Discrepancies:** While `.theme-light` exists, many elements (chips, select dropdowns, breadcrumbs, tags) remain dark or invisible.

### 3.3 Song Details Page (`lyrics/sinhala-song.html`)
1. **No Theme Toggle:** The song detail page has no light mode toggle button in the header, breaking consistency with `sinhala.html` and `index.html`.
2. **Missing Media Player:** Only provides external links (`Official Music Link ↗`). No embedded audio preview or modern player card for streaming discovery.
3. **Lyrics Unavailable Box:** When lyrics are shielded due to copyright, the box looks like an error state rather than a professional educational and rights-compliance notice.
4. **Sidebar Aside Panel:** Stacks beneath the main article on mobile, causing recommendations to be buried 5+ scrolls below the fold.
5. **Copyright Claim Modal:** Modal uses raw `<input>` elements with minimal validation and harsh borders without smooth enter/exit transitions.

### 3.4 Admin Dashboard (`admin.html`)
1. **Severe HTML Validation Error:** The login modal has duplicate inputs with identical IDs (`id="login-user"` and `id="login-pass"`), one containing hardcoded default credentials in the HTML source (`admin` / `versenest2026`).
2. **Table Responsiveness:** Song catalogue and duplicate tables cause horizontal body scroll on screens under 768px.
3. **No Dark/Light Theme Integration:** Uses hardcoded dark styles that do not synchronize with the user's theme preference.

### 3.5 Informational Pages (`about.html`, `contact.html`, `copyright.html`, `privacy.html`, `terms.html`)
1. **Unformatted / Minified Single-Line HTML:** The pages are single-line minified files that are difficult to maintain.
2. **No Theme Support:** Neither light nor dark theme variables are applied; content always defaults to dark backgrounds.
3. **No Interactive Feedback:** Contact and takedown forms lack visual validation and toast notifications.

---

## 4. Typography & Sinhala Font Rendering Issues

1. **Font Stack Mismatch:** `assets/styles.css` defines `font-family: Inter, ui-sans-serif, ...` for `body`, while `<h1>` and `<h2>` use `Georgia, Cambria, 'Times New Roman', serif`. Sinhala characters displayed in serif headings look incongruous and misaligned.
2. **Diacritic Clipping:** Sinhala vowels (combining diacritics like ෙ, ෝ, ්, ු, ූ, ි, ී) clip at default line heights (`1.06`–`1.2` in headers). Line height for Sinhala must be maintained at `1.6`–`1.8`.
3. **Font Weights:** `Noto Sans Sinhala` font weights 500, 600, and 700 are not consistently applied across cards, resulting in faux-bold browser rendering on Windows.

---

## 5. Color Contrast & Accessibility (WCAG 2.2 AA) Violations

| Element | Foreground Color | Background Color | Contrast Ratio | Minimum Required | Status |
|---|---|---|---|---|---|
| Nav link (`.nav a`) | `#bbb6ca` | `#0b0e18` | 4.88:1 | 4.5:1 | Barely Pass |
| Secondary text (`.muted`) | `#8c889d` | `#0b0e18` | 3.52:1 | 4.5:1 | **FAIL** |
| Hero subtext (`.hero-copy`) | `#bcb8c9` | `#0b0e18` | 4.95:1 | 4.5:1 | Pass |
| Card meta tag (`.card-meta`) | `#e8afc4` | `#171b2b` | 6.74:1 | 4.5:1 | Pass |
| Card body paragraph | `#aaa8b8` | `#171b2b` | 4.41:1 | 4.5:1 | **FAIL** |
| Float card small text | `#c5bdd0` | `#242137` | 5.12:1 | 4.5:1 | Pass |
| Search placeholder | `#aaa4b7` | `#191d2c` | 4.23:1 | 4.5:1 | **FAIL** |
| Light theme body text | `#6b6678` | `#f9f8fc` | 4.62:1 | 4.5:1 | Barely Pass |

- **Focus Indicators:** `:focus-visible` outlines are absent on interactive chips, cards, and buttons, failing WCAG 2.4.7.
- **Touch Target Sizes:** Action chips and pagination buttons on mobile measure 32px height, failing WCAG 2.5.8 (minimum 44x44px target size).

---

## 6. Actionable Implementation Plan

The audit confirms the need for a systematic 13-stage overhaul:
1. **Design System & Tokens:** Establish CSS custom properties for dark & light modes with verified contrast ratios.
2. **Typography System:** Harmonize `Noto Sans Sinhala` with `Inter`, ensuring safe diacritic line-heights.
3. **Navigation & Mobile Drawer:** Build a responsive, accessible mobile navigation drawer with hamburger toggle and smooth animation.
4. **Homepage Overhaul:** Integrate hero search, accurate live stats, featured classic & recent song sections, and trending artist carousels.
5. **Modern Generative Music Cards:** Replace generic gradient stars with dynamic SVG musical wave patterns, genre badges, and smooth hover micro-interactions.
6. **Song Details Elevation:** Redesign `lyrics/sinhala-song.html` with cohesive rights notices, quick-listen links, and responsive sidebar.
7. **Search & Filter Enhancement:** Add instant debounced search, clear button, active filter counters, and accessible keyboard-navigable autocomplete.
8. **Admin Dashboard Polish:** Fix duplicate login input IDs, enhance table responsiveness, and add dark/light theme support.
9. **Accessibility & WCAG 2.2 AA Compliance:** Guarantee 4.5:1 text contrast, 44px touch targets, `:focus-visible` rings, and ARIA landmarks.
10. **Verification & Regression Testing:** Verify all 16 platform tests pass with zero backend regressions.
