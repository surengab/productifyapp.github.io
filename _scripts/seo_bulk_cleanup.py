#!/usr/bin/env python3
"""One-off bulk SEO cleanup for static HTML. Run from repo root."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # repo root (parent of _scripts/)

FOOTER_OLD = (
    "A calm, minimalist daily companion for iOS. Build lasting routines, your way.",
    "The best daily habit tracker for iOS. Build lasting routines your way, calm, consistent, and free to start.",
)
FOOTER_NEW = "A calm daily habit tracker for iOS. Build lasting routines your way, consistent and free to start."


def process(html: str) -> str:
    # 1) meta keywords
    html = re.sub(r"^\s*<meta name=\"keywords\"[^>]*>\s*\n", "", html, flags=re.MULTILINE)
    # 2) markdown alternate
    html = re.sub(
        r"^\s*<link rel=\"alternate\" type=\"text/markdown\"[^>]*>\s*\n", "", html, flags=re.MULTILINE
    )
    # 3) hreflang comment blocks (various)
    html = re.sub(
        r"^\s*<!--\s*hreflang[^>]*-->\s*\n", "", html, flags=re.MULTILINE | re.IGNORECASE
    )
    # 4) en-AU / en-US alternates
    html = re.sub(
        r"^\s*<link rel=\"alternate\" hreflang=\"en-AU\"[^>]*>\s*\n", "", html, flags=re.MULTILINE
    )
    html = re.sub(
        r"^\s*<link rel=\"alternate\" hreflang=\"en-US\"[^>]*>\s*\n", "", html, flags=re.MULTILINE
    )
    # 5) footer
    for old in FOOTER_OLD:
        html = html.replace(old, FOOTER_NEW)
    return html


def main():
    for path in sorted(ROOT.rglob("*.html")):
        if "_scripts" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new = process(text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            print("updated:", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
