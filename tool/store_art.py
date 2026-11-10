#!/usr/bin/env python3
"""Renders the App Store product page header (21:9, 3840×1646) and search
results image (3:2, 3840×2560) from tool/store_header.html and
tool/store_search.html, at 2×, without alpha (header PNG, as Apple requires; search JPEG).

    python3 tool/store_art.py <out-dir>

Needs Playwright with Chromium and Pillow.
"""
import functools
import http.server
import io
import sys
import threading
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
PAGES = [('store_header', 1920, 823, 'app-store-header-3840x1646.png'),
         ('store_search', 1920, 1280, 'app-store-search-3840x2560.jpg')]


def main():
    out = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
    out.mkdir(parents=True, exist_ok=True)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            for name, w, h, file in PAGES:
                page = browser.new_page(viewport={'width': w, 'height': h}, device_scale_factor=2)
                page.goto(f'http://127.0.0.1:{server.server_port}/tool/{name}.html', wait_until='networkidle')
                page.wait_for_timeout(300)
                png = page.screenshot(clip={'x': 0, 'y': 0, 'width': w, 'height': h})
                img = Image.open(io.BytesIO(png)).convert('RGB')
                # Apple takes the 21:9 header as PNG only; no alpha either way.
                img.save(out / file, **({'optimize': True} if file.endswith('.png') else {'quality': 92, 'optimize': True}))
                print(out / file, img.size)
                page.close()
            browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
