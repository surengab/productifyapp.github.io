"""
Replaces the old full-screen mobile nav overlay with the new slide-in drawer
in all blog, feature, and solutions pages (not index.html — already done).
"""
import re, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── NEW NAV HTML ──────────────────────────────────────────────────────────────
NEW_NAV = '''\
<div class="mobile-nav-backdrop" id="mobileNavBackdrop" onclick="closeMobileNav()"></div>
<nav class="mobile-nav" id="mobileNav" role="dialog" aria-modal="true" aria-label="Mobile navigation">
    <div class="mobile-nav__header">
        <a href="/" class="mobile-nav__brand">Productify</a>
        <button class="mobile-nav__close" id="closeNav" aria-label="Close menu">✕</button>
    </div>

    <div class="mobile-nav__body">
        <div class="mobile-nav__section">
            <span class="mobile-nav__group-label">Features</span>
            <a href="/features/habit-tracker/" class="mobile-nav__link">Habit Tracker</a>
            <a href="/features/habit-duo/" class="mobile-nav__link">Habit Duo</a>
            <a href="/features/ai-analyser/" class="mobile-nav__link">AI Habit Analyser</a>
            <a href="/features/habit-templates/" class="mobile-nav__link">Templates</a>
            <a href="/features/streak-tracking/" class="mobile-nav__link">Streak Tracking</a>
        </div>

        <div class="mobile-nav__section">
            <a href="/#how-it-works" class="mobile-nav__link mobile-nav__link--primary">How It Works</a>
            <a href="/#pricing" class="mobile-nav__link mobile-nav__link--primary">Pricing</a>
            <a href="/#about" class="mobile-nav__link">About</a>
            <a href="/#contact" class="mobile-nav__link">Contact</a>
        </div>

        <div class="mobile-nav__section">
            <span class="mobile-nav__group-label">Blog</span>
            <a href="/blog/" class="mobile-nav__link">All Articles</a>
            <a href="/blog/best-habit-tracker-apps-2026/" class="mobile-nav__link">Best Habit Tracker Apps 2026</a>
            <a href="/blog/how-to-start-a-daily-habit/" class="mobile-nav__link">How to Start a Daily Habit</a>
        </div>
    </div>

    <div class="mobile-nav__footer">
        <a href="https://apps.apple.com/us/app/habit-tracker-productify/id1389900237"
           class="appstore-badge-link"
           aria-label="Download Productify on the App Store">
            <img src="/appstore_badge.svg" alt="Download on the App Store" class="appstore-badge" width="150" height="44">
        </a>
    </div>
</nav>'''

# ── NEW NAV JS ────────────────────────────────────────────────────────────────
NEW_JS = '''\
    const openBtn     = document.getElementById('openNav');
    const closeBtn    = document.getElementById('closeNav');
    const mobileNav   = document.getElementById('mobileNav');
    const navBackdrop = document.getElementById('mobileNavBackdrop');
    function openMobileNav() {
        mobileNav.classList.add('open');
        navBackdrop.classList.add('open');
        document.body.style.overflow = 'hidden';
        openBtn.setAttribute('aria-expanded', 'true');
    }
    function closeMobileNav() {
        mobileNav.classList.remove('open');
        navBackdrop.classList.remove('open');
        document.body.style.overflow = '';
        openBtn.setAttribute('aria-expanded', 'false');
    }
    openBtn.addEventListener('click', openMobileNav);
    closeBtn.addEventListener('click', closeMobileNav);
    document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeMobileNav(); });'''

# Regex for the old nav block (from <nav class="mobile-nav" ... to </nav>)
OLD_NAV_RE = re.compile(
    r'<nav class="mobile-nav"[^>]*>.*?</nav>',
    re.DOTALL
)

# Regex for the old JS block (open/close mobile nav lines)
OLD_JS_RE = re.compile(
    r'(const openBtn\s*=\s*document\.getElementById\(\'openNav\'\);.*?'
    r'mobileNav\.addEventListener\(\'click\'.*?\}\);)',
    re.DOTALL
)

files = (
    glob.glob(os.path.join(ROOT, 'blog', '*', 'index.html')) +
    glob.glob(os.path.join(ROOT, 'features', '*', 'index.html')) +
    glob.glob(os.path.join(ROOT, 'solutions', '*', 'index.html'))
)

updated = []
for path in files:
    with open(path, 'r', encoding='utf-8') as fh:
        html = fh.read()

    changed = False

    # Replace old nav HTML (if not already the new style)
    if 'mobile-nav__sub' in html or 'mobile-nav__group' in html:
        html_new = OLD_NAV_RE.sub(NEW_NAV, html, count=1)
        if html_new != html:
            html = html_new
            changed = True

    # Replace old JS
    if "mobileNav.style.display = 'flex'" in html:
        html_new = OLD_JS_RE.sub(NEW_JS.strip(), html, count=1)
        if html_new != html:
            html = html_new
            changed = True

    if changed:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(html)
        updated.append(os.path.relpath(path, ROOT))

print(f"Updated {len(updated)} files:")
for p in sorted(updated):
    print(f"  {p}")
