# Serai website

Landing page, support and privacy policy for the Serai iPhone app,
served at https://getserai.app.

| Page | File |
| --- | --- |
| Landing page | `index.html` |
| Support (FAQ, contact) | `support.html` |
| Privacy policy | `privacy.html`, built from `docs/legal/privacy-policy.md` in the app repo with `python3 tool/privacy.py` |

Plain static HTML and CSS, no build step. The look is the app's Silk Road
theme (Night by default, Day as the light theme): its colours, a paper grain
(`assets/paper-grain.png`, the app's texture) and the landscape header
(`assets/landscape-*.webp`). The font, Nunito (SIL Open Font License), is
self-hosted in `assets/fonts/` (variable, one file per script), so no
request goes to Google. Deployed with Dokploy from this repo: the `Dockerfile` serves the
files with nginx on port 80 (`nginx.conf`: clean URLs such as `/privacy`,
cache headers, 404 page).

App Store: the app is live (id 6820029405). Both download buttons are
Apple's official "Download on the App Store" badge, linked to
https://apps.apple.com/app/id6820029405 (the visitor's own storefront):
`assets/app-store-badge-<lang>.svg` from Apple's marketing tools, never
edited; `tool/i18n.py` puts each page's badge in (`APP_STORE_BADGES`);
Kazakh, Mongolian, Uzbek and Arabic have none from Apple and keep the
English one. The Smart App Banner (`apple-itunes-app`) is on the landing
and support pages.

## Search and answer engines

- Structured data (JSON-LD): `WebSite`, `Person` (publisher), `MobileApplication`
  with offers, and `FAQPage` on the landing and support pages. The FAQ
  answers in the JSON-LD must match the visible text.
- `assets/og-image-silk-20.png` (1200×630) is the share image (Open Graph and
  Twitter card), in the Silk Road Day design. It is generated from
  `tool/og_image.html` by `tool/og_image.py` (Playwright + Chromium; Pillow
  quantizes it). Assets are cached as immutable, so a new version needs a new
  file name and updated `og:image` / JSON-LD references. `llms.txt` describes
  the app for AI answer engines; `sitemap.xml` and `robots.txt` allow all
  crawlers.
- `MobileApplication` carries the App Store link as `downloadUrl` and
  `installUrl`. Still to do: register the site in Google Search Console and
  Bing Webmaster Tools.

## Languages

`index.html` is the English source. The other nineteen pages (`/de/`, `/ru/`, …)
are generated from it:

```
python3 tool/i18n.py extract   # after editing index.html: i18n/en.json
python3 tool/i18n.py build     # writes <lang>/index.html, hreflang, sitemap
```

Translations are in `i18n/<lang>.json` (same keys as `en.json`); notes for
translators in `i18n/NOTES.md`. A language whose file misses a key is not
built, so a new English text is visible in every language only once it is
translated.
