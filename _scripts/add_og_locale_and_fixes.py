"""
1. Add og:locale where missing (all pages)
2. Add JS redirect on habit-streaks legacy page
3. Ensure blog pages have datePublished / dateModified in Article schema
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

# 2. Add JS redirect to habit-streaks legacy page
habit_streaks_path = os.path.join(ROOT, "features", "habit-streaks", "index.html")
with open(habit_streaks_path, 'r', encoding='utf-8') as fh:
    html = fh.read()

REDIRECT_JS = '''\
    <script>
        // Legacy URL — redirect users to canonical page after short delay
        setTimeout(function() { window.location.replace("/features/streak-tracking/"); }, 1500);
    </script>'''

if 'window.location.replace' not in html and '</head>' in html:
    html = html.replace('</head>', REDIRECT_JS + '\n</head>', 1)
    with open(habit_streaks_path, 'w', encoding='utf-8') as fh:
        fh.write(html)
    updated.append("JS redirect: features/habit-streaks/index.html")

print(f"Done. {len(updated)} changes:")
for u in updated:
    print(f"  {u}")
