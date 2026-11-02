#!/usr/bin/env python3
"""Builds privacy.html from the policy's source in the app repo.

  python3 tool/privacy.py [path/to/privacy-policy.md]

Default source: ../vocab-tool/docs/legal/privacy-policy.md (the repos side by
side). Only the policy text between the page's navigation line and its
footer is replaced; the head, styles, theme switch and footer stay. The
Markdown is the subset the policy uses: #/##/### headings, paragraphs,
"- " lists, **bold**, *italic*, `code`, [links](url), --- rules and the
address block (lines ending in two spaces). The "short version" paragraph
becomes the highlighted summary box, the effective date the page's meta line.
"""
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT.parent / 'vocab-tool/docs/legal/privacy-policy.md'
PAGE = ROOT / 'privacy.html'
EMAIL = re.compile(r'\b([\w.+-]+@[\w-]+\.[\w.]+)\b')


def inline(text):
    t = html.escape(text, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])', r'<em>\1</em>', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', t)
    # Bare email addresses become mailto links (not inside an existing link).
    if '<a ' not in t:
        t = EMAIL.sub(r'<a href="mailto:\1">\1</a>', t)
    return t


def convert(md):
    out = []
    lines = md.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith('# '):
            out.append(f'<h1>{inline(line[2:])}</h1>')
        elif line.startswith('### '):
            out.append(f'<h3>{inline(line[4:])}</h3>')
        elif line.startswith('## '):
            out.append(f'<h2>{inline(line[3:])}</h2>')
        elif line.strip() == '---':
            pass  # the summary box already separates the introduction
        elif line.startswith('**Effective date:**'):
            out.append(f'<p class="meta">Effective date: {inline(line.split("**", 2)[2].strip())}</p>')
        elif line.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                items.append(f'  <li>{inline(lines[i][2:])}</li>')
                i += 1
            out.append('<ul>\n' + '\n'.join(items) + '\n</ul>')
            continue
        elif line.endswith('  '):
            # Address block: consecutive lines ending in two spaces, plus the
            # last line of the block.
            rows = []
            while i < len(lines) and lines[i].strip():
                rows.append(inline(lines[i].strip()))
                last = not lines[i].endswith('  ')
                i += 1
                if last:
                    break
            out.append('<address>\n  ' + '<br>\n  '.join(rows) + '\n</address>')
            continue
        else:
            para = [line]
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r'(#|- |---)', lines[i]):
                para.append(lines[i])
                i += 1
            text = inline(' '.join(p.strip() for p in para))
            if text.startswith('<strong>The short version:</strong>'):
                out.append(f'<div class="summary">\n  <p>{text}</p>\n</div>')
            else:
                out.append(f'<p>{text}</p>')
            continue
        i += 1
    return '\n\n'.join(out)


def main():
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else SOURCE
    body = convert(source.read_text())
    page = PAGE.read_text()
    start = page.index('<h1>')
    end = page.index('<footer>')
    PAGE.write_text(page[:start] + body + '\n\n' + page[end:])
    print(f'privacy.html rebuilt from {source}')


if __name__ == '__main__':
    main()
