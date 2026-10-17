# Serai website

Landing page, support and privacy policy for the Serai iPhone app,
served at https://getserai.app.

| Page | File |
| --- | --- |
| Landing page | `index.html` |
| Support (FAQ, contact) | `support.html` |
| Privacy policy | `privacy.html` (source: `docs/legal/` in the app repo) |

Plain static HTML and CSS, no build step. Fonts (Unbounded, Geologica, SIL
Open Font License) are self-hosted in `assets/fonts/`, so no request goes to
Google. Deployed with Dokploy from this repo: the `Dockerfile` serves the
files with nginx on port 80 (`nginx.conf`: clean URLs such as `/privacy`,
cache headers, 404 page).

To do before launch: replace the "Coming soon" App Store button in
`index.html` with Apple's official "Download on the App Store" badge and
the app's App Store link.

## Search and answer engines

- Structured data (JSON-LD): `WebSite`, `Person` (publisher), `MobileApplication`
  with offers, and `FAQPage` on the landing and support pages. The FAQ
  answers in the JSON-LD must match the visible text.
- `assets/og-image.png` (1200×630) is the share image; `llms.txt` describes
  the app for AI answer engines; `sitemap.xml` and `robots.txt` allow all
  crawlers.
- At launch: add `<meta name="apple-itunes-app" content="app-id=…">` and the
  App Store link, replace the Coming soon button with Apple's official badge,
  and register the site in Google Search Console and Bing Webmaster Tools.

## Languages

`index.html` is the English source. The other eleven pages (`/de/`, `/ru/`, …)
are generated from it:

```
python3 tool/i18n.py extract   # after editing index.html: i18n/en.json
python3 tool/i18n.py build     # writes <lang>/index.html, hreflang, sitemap
```

Translations are in `i18n/<lang>.json` (same keys as `en.json`); notes for
translators in `i18n/NOTES.md`. A language whose file misses a key is not
built, so a new English text is visible in every language only once it is
translated.
