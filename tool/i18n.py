#!/usr/bin/env python3
"""Localized landing pages.

  python3 tool/i18n.py extract      # i18n/en.json from index.html
  python3 tool/i18n.py build        # <lang>/index.html from i18n/<lang>.json

index.html (English) is the source. `extract` collects every translatable
unit: block elements (p, h1–h3, dt, dd, figcaption, li, title) as inner
HTML (inline tags kept), loose text between tags, translatable attributes
(alt, aria-label, meta descriptions) and the JSON-LD texts. A unit's id is
a short hash of its English text, so unchanged texts keep their
translations. `build` writes one page per i18n/<lang>.json with hreflang
links, canonical URL, html lang and the per-language animation texts.
"""
import hashlib, html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ['en', 'de', 'ru', 'fr', 'kk', 'cs', 'es', 'zh', 'ko', 'it', 'mn', 'tr', 'ja']
NATIVE = {'en': 'English', 'de': 'Deutsch', 'ru': 'Русский', 'fr': 'Français', 'kk': 'Қазақша',
          'cs': 'Čeština', 'es': 'Español', 'zh': '中文', 'ko': '한국어', 'it': 'Italiano', 'mn': 'Монгол', 'tr': 'Türkçe',
          'ja': '日本語'}
HREFLANG = {'zh': 'zh-Hans'}
OG_LOCALE = {'en': 'en_US', 'de': 'de_DE', 'ru': 'ru_RU', 'fr': 'fr_FR', 'kk': 'kk_KZ', 'cs': 'cs_CZ',
             'es': 'es_ES', 'zh': 'zh_CN', 'ko': 'ko_KR', 'it': 'it_IT', 'mn': 'mn_MN', 'tr': 'tr_TR', 'ja': 'ja_JP'}
BLOCK = re.compile(r'(<(p|h1|h2|h3|dt|dd|figcaption|title)(?:\s[^>]*)?>)(.*?)(</\2>)', re.S)
ATTR = re.compile(r'\b(alt|aria-label)="([^"]*)"')
META = re.compile(r'(<meta (?:name="description"|property="og:(?:title|description|image:alt)") content=")([^"]*)(")')
LOOSE = re.compile(r'>([^<>]*[^\s<>][^<>]*)<')
KEEP = re.compile(r'^[\s\W\d]*$|^[A-ZÀ-ÿ]$')  # punctuation, numbers, single letters (board cells)
# Names that stay as they are on every page.
VERBATIM = {'Serai', 'Daily Hunt', 'The Taklamakan Crossing', 'English', 'Deutsch', 'Русский', 'Français',
            'Қазақша', 'Čeština', 'Español', '中文', '한국어', 'Italiano', 'Монгол', 'Türkçe', '日本語', 'chris@getserai.app',
            '© 2026 Christian Heuer', 'kārvān', 'sarāy', 'caravanserai',
            'A1', 'A2', 'B1', 'B2', 'C1', 'C2', ''}


# Unbounded and Geologica have no Chinese, Japanese or Korean glyphs. On
# these pages the text falls back to fonts of the page's language (so Han
# characters take that language's glyph forms); Latin letters stay in
# Unbounded/Geologica.
CJK = {'ja': '"Hiragino Sans","Hiragino Kaku Gothic ProN","Noto Sans JP","Yu Gothic",Meiryo',
       'zh': '"PingFang SC","Hiragino Sans GB","Noto Sans SC","Microsoft YaHei"',
       'ko': '"Apple SD Gothic Neo","Noto Sans KR","Malgun Gothic"'}


# The animation's texts: the clue words (the board's answers SPOON, BREAD,
# CUP and TEA stay English: the page's reader learns English) and the
# Pause/Play button.
EXTRA = ['Löffel', 'Brot', 'Tasse', 'Tee', 'Pause animation', 'Play animation', 'Language']


def uid(text):
    return hashlib.sha1(text.encode()).hexdigest()[:10]


def protect(src):
    """Replaces <script>, <style> and <svg> blocks with placeholders."""
    kept = []
    def keep(m):
        kept.append(m.group(0))
        return f'\x00{len(kept) - 1}\x00'
    return re.sub(r'<(script|style|svg)\b.*?</\1>', keep, src, flags=re.S), kept


def restore(src, kept):
    return re.sub(r'\x00(\d+)\x00', lambda m: kept[int(m.group(1))], src)


def units(src, translate):
    """Applies translate(text) -> text to every unit; returns the new page."""
    body, kept = protect(src)

    def block(m):
        inner = m.group(3).strip()
        if not inner or KEEP.match(html.unescape(re.sub('<[^>]+>', '', inner))) or inner in VERBATIM:
            return m.group(0)
        return m.group(1) + translate(inner) + m.group(4)
    body = BLOCK.sub(block, body)
    # Loose text outside the blocks just handled (marked with \x01 so the
    # loose pass skips them).
    body = META.sub(lambda m: m.group(1) + translate(m.group(2)) + m.group(3), body)
    body = ATTR.sub(lambda m: f'{m.group(1)}="{translate(m.group(2))}"' if m.group(2) not in VERBATIM else m.group(0), body)

    def loose(m):
        text = m.group(1)
        s = text.strip()
        if not s or KEEP.match(html.unescape(s)) or s in VERBATIM or '\x00' in s:
            return m.group(0)
        lead = text[:len(text) - len(text.lstrip())]
        trail = text[len(text.rstrip()):]
        return '>' + lead + translate(s) + trail + '<'
    # Blocks already translated contain their own loose text; skip by
    # translating loose text only where it is not inside a block element.
    parts = re.split(r'(<(?:p|h1|h2|h3|dt|dd|figcaption|title)(?:\s[^>]*)?>.*?</(?:p|h1|h2|h3|dt|dd|figcaption|title)>)', body, flags=re.S)
    body = ''.join(p if i % 2 else LOOSE.sub(loose, p) for i, p in enumerate(parts))
    out = restore(body, kept)
    # JSON-LD
    def ld(m):
        data = json.loads(m.group(2))
        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in ('description', 'text', 'alternateName') and isinstance(v, str):
                        o[k] = translate(v)
                    elif k == 'name' and isinstance(v, str) and o.get('@type') == 'Question':
                        o[k] = translate(v)
                    else:
                        walk(v)
            elif isinstance(o, list):
                for x in o:
                    walk(x)
        walk(data)
        return m.group(1) + json.dumps(data, ensure_ascii=False) + m.group(3)
    return re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', ld, out, flags=re.S)


def extract():
    src = (ROOT / 'index.html').read_text()
    found = {}
    def collect(text):
        found.setdefault(uid(text), text)
        return text
    units(src, collect)
    # Texts of the animation script (not in the page markup).
    for extra in EXTRA:
        collect(extra)
    out = ROOT / 'i18n' / 'en.json'
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(found, ensure_ascii=False, indent=1) + '\n')
    print(f'{len(found)} units -> {out}')


SITE = 'https://getserai.app'


def url(lang):
    return f'{SITE}/' if lang == 'en' else f'{SITE}/{lang}/'


def alternates():
    rows = [f'<link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{url(l)}">' for l in LANGS]
    rows.append(f'<link rel="alternate" hreflang="x-default" href="{url("en")}">')
    return '<!-- hreflang -->\n' + '\n'.join(rows) + '\n<!-- /hreflang -->'


def switcher(lang, label):
    links = ''.join(
        f'<a href="{"/" if l == "en" else f"/{l}/"}" lang="{HREFLANG.get(l, l)}" hreflang="{HREFLANG.get(l, l)}"'
        + (' aria-current="page" style="color: var(--ink); font-weight: 600"' if l == lang else '')
        + f'>{NATIVE[l]}</a>'
        for l in LANGS)
    return (f'<!-- languages --><nav aria-label="{html.escape(label)}" style="flex-basis: 100%; display: flex; '
            f'flex-wrap: wrap; gap: 8px 16px; font-size: 13px">{links}</nav><!-- /languages -->')


def common(page, lang, label):
    """hreflang links, the footer's language list (both idempotent)."""
    page = re.sub(r'<!-- hreflang -->.*?<!-- /hreflang -->\n?', '', page, flags=re.S)
    page = page.replace(f'<link rel="canonical" href="{SITE}/">', f'<link rel="canonical" href="{url(lang)}">')
    page = re.sub(r'(<link rel="canonical" href="[^"]*">)', lambda m: m.group(1) + '\n' + alternates(), page, count=1)
    page = re.sub(r'<!-- languages -->.*?<!-- /languages -->', '', page, flags=re.S)
    return page.replace('</footer>', switcher(lang, label) + '\n</footer>', 1)


def build():
    src = (ROOT / 'index.html').read_text()
    en = json.loads((ROOT / 'i18n' / 'en.json').read_text())
    src = common(src, 'en', 'Language')
    (ROOT / 'index.html').write_text(src)
    built = ['en']
    for lang in LANGS[1:]:
        f = ROOT / 'i18n' / f'{lang}.json'
        if not f.exists():
            print(f'{lang}: no translation yet, skipped')
            continue
        tr = json.loads(f.read_text())
        missing = [k for k in en if not tr.get(k)]
        if missing:
            print(f'{lang}: {len(missing)} units untranslated, skipped')
            continue
        t = lambda text: tr.get(uid(text), text)
        page = units(src, t)
        page = page.replace('<html lang="en">', f'<html lang="{HREFLANG.get(lang, lang)}">', 1)
        page = page.replace(f'<meta property="og:url" content="{SITE}/">', f'<meta property="og:url" content="{url(lang)}">')
        page = page.replace('<meta property="og:locale" content="en_US">', f'<meta property="og:locale" content="{OG_LOCALE[lang]}">')
        page = page.replace('<a href="/" style="display: flex;', f'<a href="/{lang}/" style="display: flex;', 1)
        page = page.replace('"inLanguage": "en"', f'"inLanguage": "{HREFLANG.get(lang, lang)}"', 1)
        page = page.replace('"url": "https://getserai.app/#faq"', f'"url": "{url(lang)}#faq"')
        found = t('2/4 found').replace('2/4', '{n}/4', 1)
        text = {'clues': {k: t(v) for k, v in (('spoon', 'Löffel'), ('bread', 'Brot'), ('cup', 'Tasse'), ('tea', 'Tee'))},
                'found': found, 'desc': t('You eat soup with it'),
                'pause': t('Pause animation'), 'play': t('Play animation')}
        page = page.replace('<script>\n// Game graphics in motion',
                            '<script>window.SERAI_TEXT = ' + json.dumps(text, ensure_ascii=False) + ';</script>\n<script>\n// Game graphics in motion', 1)
        if lang in ('kk', 'mn'):
            # Unbounded has no Kazakh or Mongolian letters (Ә Ө Ү …): headings
            # use Geologica, like the app.
            page = page.replace('</style>', '[style*="Unbounded"]{font-family:Geologica,system-ui,sans-serif!important}\n</style>', 1)
        if lang in CJK:
            page = page.replace('</style>', f'[style*="Unbounded"],.hero-cleared p{{font-family:Unbounded,{CJK[lang]},sans-serif!important}}\n'
                                f'[style*="Geologica"]{{font-family:Geologica,{CJK[lang]},system-ui,sans-serif!important}}\n</style>', 1)
        page = re.sub(r'<!-- languages -->.*?<!-- /languages -->', switcher(lang, t('Language')), page, flags=re.S)
        out = ROOT / lang / 'index.html'
        out.parent.mkdir(exist_ok=True)
        out.write_text(page)
        built.append(lang)
    sitemap(built)
    print('built:', ' '.join(built))


def sitemap(built):
    alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{url(l)}"/>' for l in built)
    alt += f'<xhtml:link rel="alternate" hreflang="x-default" href="{url("en")}"/>'
    import datetime
    today = datetime.date.today().isoformat()
    rows = [f'<url><loc>{url(l)}</loc><lastmod>{today}</lastmod>{alt}</url>' for l in built]
    rows += [f'<url><loc>{SITE}/{p}</loc><lastmod>{today}</lastmod></url>' for p in ('support.html', 'privacy.html')]
    (ROOT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + '\n'.join(rows) + '\n</urlset>\n')


if __name__ == '__main__':
    {'extract': extract, 'build': build}[sys.argv[1]]()
