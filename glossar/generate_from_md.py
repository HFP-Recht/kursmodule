#!/usr/bin/env python3
import json
import re
import unicodedata
from pathlib import Path

root = Path(__file__).resolve().parent
src = root / 'glossar.md'
out_keywords = root / 'keywords.json'


def read_text(path: Path) -> str:
    for enc in ('utf-8-sig', 'cp1252', 'latin-1'):
        try:
            return path.read_text(encoding=enc)
        except Exception:
            continue
    raise RuntimeError(f'Cannot read {path}')


def slugify(text: str) -> str:
    t = unicodedata.normalize('NFKD', text)
    t = t.encode('ascii', 'ignore').decode('ascii').lower()
    t = re.sub(r'[^a-z0-9]+', '-', t)
    t = re.sub(r'-+', '-', t).strip('-')
    return t or 'term'


def sentence(text: str) -> str:
    text = re.sub(r'\s+', ' ', text).strip()
    if not text:
        return ''
    placeholders = {}
    abbr_pat = re.compile(r'\b(?:bzw|z\.B|d\.h|u\.a|z\.T|etc|ca|Art|Nr)\.', flags=re.IGNORECASE)

    def protect(match):
        key = f'__ABBR_{len(placeholders)}__'
        placeholders[key] = match.group(0)
        return key

    protected = abbr_pat.sub(protect, text)
    parts = re.split(r'(?<=[!?])\s+|(?<!\d\.)(?<=[.])\s+', protected)
    first = parts[0].strip() if parts else protected
    for key, original in placeholders.items():
        first = first.replace(key, original)
    return first


def html_page(term: str, definition: str) -> str:
    return f'''<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{term}</title>
<style>
body{{font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:24px auto;padding:0 16px;line-height:1.6;color:#17223b}}
h1{{color:#1a3a5c}}
</style>
</head>
<body>
<h1>{term}</h1>
<p>{definition or 'Definition folgt.'}</p>
</body>
</html>
'''

text = read_text(src)
lines = [ln.rstrip() for ln in text.splitlines()]

entries = []
i = 0
while i < len(lines):
    if not lines[i].strip():
        i += 1
        continue
    term = lines[i].strip()
    i += 1
    def_lines = []
    while i < len(lines) and lines[i].strip():
        def_lines.append(lines[i].strip())
        i += 1
    definition = ' '.join(def_lines).strip()

    # Fallback: block with single line that likely combines term + definition.
    if not definition and ' ' in term:
        m = re.match(r'^([A-ZÄÖÜ][A-Za-zÄÖÜäöüß()\-\., ]{2,}?)\s{2,}(.+)$', term)
        if m:
            term = m.group(1).strip()
            definition = m.group(2).strip()

    term = re.sub(r'\s+', ' ', term).strip(' -')
    definition = re.sub(r'\s+', ' ', definition).strip()
    if term:
        entries.append((term, definition))

# Deduplicate by term, keep first non-empty definition.
by_term = {}
for term, definition in entries:
    if term not in by_term:
        by_term[term] = definition
    elif not by_term[term] and definition:
        by_term[term] = definition

terms = []
created = 0
for term in sorted(by_term.keys(), key=lambda t: t.lower()):
    definition = by_term[term]
    page = f"{slugify(term)}.html"
    page_path = root / page
    if not page_path.exists():
        page_path.write_text(html_page(term, definition), encoding='utf-8')
        created += 1
    terms.append({
        'term': term,
        'page': page,
        'short': sentence(definition)
    })

out_keywords.write_text(json.dumps({'terms': terms}, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Parsed terms: {len(terms)}')
print(f'Created new pages: {created}')
print(f'keywords.json written: {out_keywords}')
