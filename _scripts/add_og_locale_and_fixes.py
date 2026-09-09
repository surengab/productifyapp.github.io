"""
1. Add og:locale where missing (all pages)
"""
import re, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

all_html = (
    glob.glob(os.path.join(ROOT, "*.html")) +
    glob.glob(os.path.join(ROOT, "blog", "*", "index.html")) +
    glob.glob(os.path.join(ROOT, "features", "*", "index.html")) +
    glob.glob(os.path.join(ROOT, "solutions", "*", "index.html")) +
    [os.path.join(ROOT, "index.html")]
)
all_html = list(set(all_html))

updated = []

for path in all_html:
    with open(path, 'r', encoding='utf-8') as fh:
        html = fh.read()
    orig = html

    # 1. Add og:locale after og:site_name if missing
    if 'og:locale' not in html and 'og:site_name' in html:
        html = html.replace(
            '<meta property="og:site_name" content="Productify">',
            '<meta property="og:site_name" content="Productify">\n    <meta property="og:locale" content="en_US">'
        )

    if html != orig:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(html)
        updated.append(f"og:locale: {os.path.relpath(path, ROOT)}")

print(f"Done. {len(updated)} changes:")
for u in updated:
    print(f"  {u}")
