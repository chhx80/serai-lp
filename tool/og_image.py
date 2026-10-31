#!/usr/bin/env python3
"""Render the share image (Open Graph / Twitter card) from tool/og_image.html.

    python3 tool/og_image.py [out.png]      # default: assets/og-image-silk.png

Needs Playwright with Chromium (pip install playwright && playwright install chromium);
Pillow, if installed, quantizes the PNG to keep it small. The repo root is served over
a throwaway local HTTP server so the page can use the real /assets/... files (fonts,
icon, landscape, paper grain). Assets are cached as immutable for 30 days, so a changed
image needs a new file name and updated og:image references in the pages.
"""
import functools, http.server, io, pathlib, sys, threading

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'assets' / 'og-image-silk.png'


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(ROOT)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={'width': 1200, 'height': 630}, device_scale_factor=1)
            page.goto(f'http://127.0.0.1:{server.server_port}/tool/og_image.html', wait_until='networkidle')
            page.evaluate('document.fonts.ready')
            png = page.screenshot(clip={'x': 0, 'y': 0, 'width': 1200, 'height': 630})
            browser.close()
    finally:
        server.shutdown()
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(png)).convert('RGB').quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
        buf = io.BytesIO()
        img.save(buf, 'PNG', optimize=True)
        png = buf.getvalue()
    except ImportError:
        print('Pillow not installed: writing the PNG unquantized')
    OUT.write_bytes(png)
    print(f'{OUT.relative_to(ROOT) if OUT.is_relative_to(ROOT) else OUT}: {len(png) // 1024} KB')


if __name__ == '__main__':
    main()
