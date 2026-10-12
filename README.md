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
