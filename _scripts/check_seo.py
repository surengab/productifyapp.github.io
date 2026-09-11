#!/usr/bin/env python3
"""Validate generated HTML and sitemap before deployment. No network required."""
import json
import re
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '_site').resolve()
ORIGIN = 'https://productifyapp.org'
REDIRECTS = json.loads((Path(__file__).resolve().parents[1] / '_data/redirects.json').read_text())
errors = []

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.ids, self.links, self.canonicals, self.schemas = set(), [], [], []
        self.title, self.description, self.robots = '', '', ''
        self.social_urls = []
        self.library_links, self.section_links, self.cards = [], [], []
        self.nav_label = ''
        self.has_main_nav = False
        self.flyouts, self.flyout_label, self.flyout_depth = {}, None, 0
        self.h1 = 0
        self.redirect = False
        self.refresh = None
        self.in_title = self.in_json = False
        self.json_text = ''
        source = path.read_text()
        self.feed(source)
        if re.search(r'\b(?:window\.)?location\s*(?:\.\s*(?:replace|assign)\s*\(|(?:\.\s*href)?\s*=(?!=))', source):
            self.redirect = True

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'nav':
            self.nav_label = a.get('aria-label', '')
            if self.nav_label == 'Main navigation': self.has_main_nav = True
        if tag == 'div':
            if self.flyout_depth: self.flyout_depth += 1
            elif a.get('role') == 'group' and a.get('aria-label') in ('Guides navigation', 'Blog navigation'):
                self.flyout_label, self.flyout_depth = a['aria-label'], 1
                self.flyouts[self.flyout_label] = []
        if tag == 'a':
            if self.flyout_label: self.flyouts[self.flyout_label].append(a.get('href'))
            if self.nav_label in ('Guides library', 'Blog library'):
                self.library_links.append((self.nav_label, a.get('href'), a.get('aria-current')))
            if self.nav_label == 'Resource sections':
                self.section_links.append((a.get('href'), a.get('aria-current')))
            if 'resource-card' in a.get('class', '').split(): self.cards.append(a.get('href'))
        if a.get('id'):
            self.ids.add(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'title': self.in_title = True
        if tag == 'meta':
            if a.get('name') == 'description': self.description = a.get('content', '')
            if a.get('name') == 'robots': self.robots = a.get('content', '')
            if a.get('property', a.get('name')) in ('og:url', 'twitter:url'):
                self.social_urls.append(a.get('content', ''))
            if a.get('http-equiv', '').lower() == 'refresh':
                self.redirect, self.refresh = True, a.get('content', '')
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
        if tag == 'div' and self.flyout_depth:
            self.flyout_depth -= 1
            if not self.flyout_depth: self.flyout_label = None
        if tag == 'nav': self.nav_label = ''
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

def inspect_schema(value, relative):
    if isinstance(value, list):
        for item in value: inspect_schema(item, relative)
    elif isinstance(value, dict):
        if value.get('@type') == 'SoftwareApplication' and value.get('name', '').startswith('Productify'):
            rating = value.get('aggregateRating')
            if rating:
                ratings.add((str(rating.get('ratingValue')), str(rating.get('ratingCount', rating.get('reviewCount')))))
        for item in value.values(): inspect_schema(item, relative)
    elif isinstance(value, str) and urlsplit(value).netloc == 'productifyapp.org':
        if not target(value).is_file():
            errors.append(f'{relative}: broken JSON-LD target {value}')

for path, page in pages.items():
    relative = path.relative_to(ROOT).as_posix()
    url = ORIGIN + '/' + relative.removesuffix('index.html')
    redirect_to = REDIRECTS.get('/' + relative.removesuffix('index.html'))
    if redirect_to:
        destination = ORIGIN + redirect_to
        if page.refresh != f'0; url={destination}' or page.canonicals != [destination]:
            errors.append(f'{relative}: expected immediate redirect and canonical to {destination}')
        if ('a', destination) not in page.links:
            errors.append(f'{relative}: redirect missing fallback link')
        dest_page = pages.get(target(destination))
        if not dest_page or dest_page.redirect or 'noindex' in dest_page.robots or dest_page.canonicals != [destination]:
            errors.append(f'{relative}: redirect target must be a canonical, indexable page')
        continue
    if page.redirect: errors.append(f'{relative}: unexpected redirect page')
    indexable = not page.redirect and 'noindex' not in page.robots
    if indexable:
        if not page.title.strip() or not page.description.strip():
            errors.append(f'{relative}: missing title or description')
        titles[page.title.strip()] += 1
        descriptions[page.description.strip()] += 1
        if page.h1 != 1: errors.append(f'{relative}: expected one H1, found {page.h1}')
        if page.canonicals != [url]: errors.append(f'{relative}: incorrect canonical {page.canonicals}')
    for social_url in page.social_urls:
        if social_url != url: errors.append(f'{relative}: incorrect social URL {social_url}')
    for schema in page.schemas: inspect_schema(schema, relative)
    if page.has_main_nav:
        for resource_section in ('guides', 'blog'):
            expected = {'/' + p.relative_to(ROOT).as_posix().removesuffix('index.html')
                        for p, child in pages.items() if p.parent.parent == ROOT / resource_section and not child.redirect}
            expected.add(f'/{resource_section}/')
            actual = page.flyouts.get(f'{resource_section.capitalize()} navigation', [])
            if set(actual) != expected or len(actual) != len(expected):
                errors.append(f'{relative}: {resource_section} hover navigation must match its collection')
    section = relative.split('/')[0]
    if section in ('guides', 'blog'):
        section_url = f'/{section}/'
        page_url = '/' + relative.removesuffix('index.html')
        children = {'/' + p.relative_to(ROOT).as_posix().removesuffix('index.html')
                    for p, child in pages.items() if p.parent.parent == ROOT / section and not child.redirect}
        links = page.library_links
        if {href for _, href, _ in links} != children | {section_url} or len(links) != len(children) + 1:
            errors.append(f'{relative}: sidebar must list its own collection exactly once')
        if any(label != f'{section.capitalize()} library' for label, _, _ in links):
            errors.append(f'{relative}: wrong section sidebar')
        if [href for _, href, current in links if current == 'page'] != [page_url]:
            errors.append(f'{relative}: sidebar current page does not match URL')
        if page.section_links != [('/guides/', 'location' if section == 'guides' else None),
                                  ('/blog/', 'location' if section == 'blog' else None)]:
            errors.append(f'{relative}: inconsistent resource section navigation')
        if page_url == section_url and (set(page.cards) != children or len(page.cards) != len(children)):
            errors.append(f'{relative}: listing must contain only its own collection, without duplicates')
        breadcrumbs = [s for s in page.schemas if isinstance(s, dict) and s.get('@type') == 'BreadcrumbList']
        expected = [ORIGIN + '/', ORIGIN + section_url]
        if page_url != section_url: expected.append(ORIGIN + page_url)
        if len(breadcrumbs) != 1 or [item.get('item') for item in breadcrumbs[0]['itemListElement']] != expected:
            errors.append(f'{relative}: breadcrumbs do not match section hierarchy')
        if page_url == section_url:
            schema_type = 'Blog' if section == 'blog' else 'CollectionPage'
            lists = [s for s in page.schemas if isinstance(s, dict) and s.get('@type') == schema_type]
            key = 'blogPost' if section == 'blog' else 'hasPart'
            if len(lists) != 1 or {s['url'] for s in lists[0].get(key, [])} != {ORIGIN + p for p in children}:
                errors.append(f'{relative}: structured listing does not match collection')
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
for href in re.findall(r'\]\(([^)\s]+)\)', (ROOT / 'llms.txt').read_text()):
    if urlsplit(href).netloc == 'productifyapp.org' and not target(href).is_file():
        errors.append(f'llms.txt: broken target {href}')
for error in sorted(set(errors)): print(error)
print(f'Checked {len(pages)} HTML pages and {len(urls)} sitemap URLs; {len(set(errors))} errors.')
sys.exit(bool(errors))
