#!/usr/bin/env python3
"""Validate generated HTML and sitemap before deployment. No network required."""
import json
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '_site').resolve()
ORIGIN = 'https://productifyapp.org'
errors = []

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids, self.links, self.canonicals, self.schemas = set(), [], [], []
        self.title, self.description, self.robots = '', '', ''
        self.h1 = 0
        self.redirect = False
        self.in_title = self.in_json = False
        self.json_text = ''
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.in_title = True
        if tag == 'meta':
            if a.get('name') == 'description': self.description = a.get('content', '')
            if a.get('name') == 'robots': self.robots = a.get('content', '')
            if a.get('http-equiv', '').lower() == 'refresh': self.redirect = True
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href', ''))
        if tag in ('a', 'img', 'script', 'link'):
            value = a.get('href') if tag in ('a', 'link') else a.get('src')
            if value: self.links.append((tag, value))
        if tag == 'img' and 'alt' not in a:
            errors.append(f'{self.path.relative_to(ROOT)}: image missing alt: {a.get("src")}')
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.in_json, self.json_text = True, ''

    def handle_data(self, text):
        if self.in_title: self.title += text
        if self.in_json: self.json_text += text

    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
        if tag == 'script' and self.in_json:
            try: self.schemas.append(json.loads(self.json_text))
            except ValueError as e: errors.append(f'{self.path.relative_to(ROOT)}: invalid JSON-LD: {e}')
            self.in_json = False

def target(url):
    path = ROOT / unquote(urlsplit(url).path).lstrip('/')
    return path / 'index.html' if path.is_dir() else path

pages = {p: Page(p) for p in ROOT.rglob('*.html')}
titles = Counter()
descriptions = Counter()
ratings = set()

def inspect_schema(value):
    if isinstance(value, list):
        for item in value: inspect_schema(item)
    elif isinstance(value, dict):
        if value.get('@type') == 'SoftwareApplication' and value.get('name', '').startswith('Productify'):
            rating = value.get('aggregateRating')
            if rating:
                ratings.add((str(rating.get('ratingValue')), str(rating.get('ratingCount', rating.get('reviewCount')))))
        for item in value.values(): inspect_schema(item)

for path, page in pages.items():
    relative = path.relative_to(ROOT).as_posix()
    url = ORIGIN + '/' + relative.removesuffix('index.html')
    indexable = not page.redirect and 'noindex' not in page.robots
    if indexable:
        if not page.title.strip() or not page.description.strip():
            errors.append(f'{relative}: missing title or description')
        titles[page.title.strip()] += 1
        descriptions[page.description.strip()] += 1
        if page.h1 != 1: errors.append(f'{relative}: expected one H1, found {page.h1}')
        if page.canonicals != [url]: errors.append(f'{relative}: incorrect canonical {page.canonicals}')
    for schema in page.schemas: inspect_schema(schema)
    for tag, href in page.links:
        resolved = urljoin(url, href)
        parts = urlsplit(resolved)
        if parts.netloc != 'productifyapp.org': continue
        dest = target(resolved)
        if not dest.is_file(): errors.append(f'{relative}: broken {tag} target {href}')
        elif tag == 'a' and parts.fragment and dest in pages and not pages[dest].redirect:
            if unquote(parts.fragment) not in pages[dest].ids:
                errors.append(f'{relative}: missing anchor {href}')
for title, count in titles.items():
    if count > 1: errors.append(f'duplicate title ({count} pages): {title}')
for description, count in descriptions.items():
    if count > 1: errors.append(f'duplicate description ({count} pages): {description}')
if len(ratings) > 1: errors.append(f'conflicting Productify ratings: {sorted(ratings)}')
ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
urls = [n.text for n in ET.parse(ROOT / 'sitemap.xml').findall('s:url/s:loc', ns)]
if len(urls) != len(set(urls)): errors.append('duplicate sitemap URLs')
for url in urls:
    page = pages.get(target(url))
    if not page or page.redirect or 'noindex' in page.robots or page.canonicals != [url]:
        errors.append(f'sitemap URL is not canonical/indexable: {url}')
for error in sorted(set(errors)): print(error)
print(f'Checked {len(pages)} HTML pages and {len(urls)} sitemap URLs; {len(set(errors))} errors.')
sys.exit(bool(errors))
