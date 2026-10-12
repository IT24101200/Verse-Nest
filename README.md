# VerseNest Originals — Website Starter

This is a ready-to-preview, responsive *static* lyrics website. It is not yet published online and Google AdSense is **not** connected or approved.

## Included

- Home page with 12 complete, original sample song lyrics and working search/mood filters.
- 12 separate lyrics pages with full words, song meanings, and writing notes.
- 3 original beginner songwriting guides.
- About, Contact, Privacy, Terms, and Copyright pages.
- Mobile-friendly design, page descriptions, clean navigation, and SEO sitemap script.
- No external dependencies, tracking code, account logins, or live ad placements.

## Preview on your computer (Windows)

1. Unzip `versenest_website.zip`.
2. Double-click `index.html` to view most pages.
3. To preview through a local server, install Python from python.org if needed. In PowerShell, run:

   ```powershell
   cd path\to\versenest_website
   py -m http.server 8000
   ```

4. Open `http://localhost:8000`. Search, mood filters, and pages should work.

## Before publishing (important)

1. Edit **contact.html**: replace `CONTACT_EMAIL_HERE` with a real reachable email.
2. Edit **about.html** to add truthful publisher/editor information.
3. Review and update **privacy.html**, **terms.html**, and **copyright.html** to match your real ownership, hosting, and local requirements.
4. Replace or improve sample content with your own meaningful original work, or properly licensed content. Do not copy existing commercial song lyrics without permission.
5. **For standalone hosting such as Netlify or Vercel, plan to use a custom root domain for AdSense registration.** Google’s general site sign-up requires a standard domain, and non-partner subdomains such as a temporary `netlify.app` preview URL may not qualify. A custom domain does not guarantee approval. Free `blogspot.com` addresses use Blogger’s special host-partner signup flow.
6. Ensure the site is public, fully working, and has useful content before applying. AdSense approval is Google's decision.

## Deploy without needing a backend (one simple route)

1. Sign into a static hosting provider such as Netlify or Cloudflare Pages (an account is required).
2. Choose its manual drag-and-drop static site deployment option where available.
3. Upload the **contents of the website folder** (or the folder itself if the interface accepts a folder).
4. Confirm a live public URL, then generate the sitemap.
5. Make sure every page is reachable and links work.

**Alternative:** Deploy to Vercel with a Git repository containing these files. Set Framework Preset to `Other`, leave Build Command blank, and use the root folder as the project directory. This site does not need a build. Check the platform's current steps.

## Generate an accurate sitemap after publication

From the website folder, use:

```bash
python generate_sitemap.py --base-url https://your-real-domain.example
```

Replace the example with the **exact public origin** including https. Upload the regenerated `sitemap.xml` and `robots.txt` to your live website. You may then submit `https://your-real-domain.example/sitemap.xml` in Google Search Console.

## Google AdSense connection — after the website is live

1. Go to `https://adsense.google.com/` and sign in with your own Google account.
2. If you already have an AdSense publisher account, use that one; do not create a duplicate individual publisher account.
3. In AdSense **Sites**, add this new public website using its eligible public domain (for standalone hosting, normally your own root domain). Do **not** submit a temporary preview URL as if it were your own root domain.
4. AdSense will provide a verification method, such as a code snippet or meta tag. Add the exact code inside the `<head>` section in the HTML pages (each page has a comment showing where). Redeploy.
5. Complete your publisher/payment details and request site review. Wait for Google's actual decision; no one can guarantee approval.
6. After approval, enable **Auto ads** (or set up manual ad units) according to the instructions in your AdSense account. Add the actual publisher code Google provides, and ensure ad and consent policies are followed.
7. If Google requires `ads.txt`, create a root-level `ads.txt` using **your real publisher ID** and Google's exact instructions. Never reuse an example publisher number.
8. Update your Privacy Policy and implement a suitable consent management solution where required, before you serve advertising.

For guidance, see Google Help articles:
- https://support.google.com/adsense/answer/7584263
- https://support.google.com/adsense/answer/9729
- https://support.google.com/adsense/answer/7299563
- https://support.google.com/adsense/answer/1269077

## If you prefer Blogger instead of a static website

This ZIP is a standalone HTML site. It is **not a Blogger theme XML**. To use Blogger, create a separate new blog, publish original songs as Blogger posts, create About/Privacy/Contact pages, and apply through Blogger → Earnings. Do not paste the entire ZIP as a Blogger theme.

## Editorial / legal notes

- The content here is newly generated starter copy and should be reviewed and improved by the site owner.
- Original lyrics are not a promise of exclusivity or non-infringement; check before commercial release.
- Many popular commercial lyrics have copyright owners. Artist credit alone is not a license.
- Site needs genuine publisher information before launch.
- This starter site does not automatically collect traffic or earn revenue.
