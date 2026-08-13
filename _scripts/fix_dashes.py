"""Replace em dashes in content with natural punctuation alternatives."""
import re

path = "/Users/surengabrielyan/Workspace/github_page/productifyapp.github.io/solutions/productivity-at-work/index.html"

with open(path, "r", encoding="utf-8") as f:
    html = f.read()

replacements = [
    # JSON-LD schema
    ("usually either focused work time or daily learning.", "usually focused work time or daily learning."),
    ("work — usually either", "work, usually"),
    ("Productify supports both — you set the schedule that matches the behavior.",
     "Productify supports both. You set the schedule that matches the behavior."),
    ("a to-do list does not. Productify supports measurable targets — minutes, sessions, pages — so you can track quantity, not just completion.",
     "a to-do list does not. Productify supports measurable targets (minutes, sessions, pages) so you can track quantity, not just completion."),

    # Hero lead
    ("small, consistent habits — things you do daily that most people skip.",
     "small, consistent habits: the things you do daily that most people skip."),

    # Why work habits differ
    ("That delayed return makes them easier to skip — and more valuable to maintain.",
     "That delayed return makes them easier to skip, and more valuable to maintain."),

    # Highlight box
    ("doesn't just add up linearly — it creates connections between ideas,",
     "doesn't just add up linearly; it creates connections between ideas,"),

    # Deep work section
    ("each day — no notifications, no context-switching — can often",
     "each day (no notifications, no context-switching) can often"),
    ("the pattern becomes clear — which days you protect the time, which days you don't, and what the correlations are.",
     "the pattern becomes clear: which days you protect the time, which days you don't, and what the correlations are."),

    # Reading section
    ("up to several books' worth of learning — far more than most people",
     "up to several books' worth of learning, far more than most people"),
    ("of pages or minutes — rather than just",
     "of pages or minutes rather than just"),

    # Weekly review
    ("A 30-minute weekly review — looking at what you completed, what you didn't, and what matters next week — is",
     "A 30-minute weekly review (what you completed, what you didn't, and what matters next week) is"),

    # Shutdown ritual
    ("A consistent end-of-day habit — reviewing your open tasks, writing tomorrow's single most important priority, then closing your apps — creates",
     "A consistent end-of-day habit, reviewing your open tasks, writing tomorrow's single most important priority, and then closing your apps, creates"),

    # Use-case cards
    ("Track pages or minutes — Productify lets you choose the unit that fits your style.",
     "Track pages or minutes. Productify lets you choose the unit that fits your style."),

    # How Productify supports list
    ("let you track exact minutes, sessions, or pages — not just binary completion",
     "let you track exact minutes, sessions, or pages, not just binary completion"),

    # Habit tracker vs to-do section heading paragraph
    ("Both are useful tools — but they solve different problems.",
     "Both are useful tools, but they solve different problems."),

    # To-do card
    ("Once done, that item disappears — as it should.",
     "Once done, that item disappears, as it should."),

    # Habit tracker card
    ("It makes consistency visible — which is precisely what creates momentum",
     "It makes consistency visible, which is precisely what creates momentum"),

    # Paragraph after cards
    ("Productify makes those repeated patterns visible — you can see at a glance",
     "Productify makes those repeated patterns visible. You can see at a glance"),

    # FAQ heading
    ("Productivity habits at work — common questions",
     "Productivity habits at work: common questions"),

    # FAQ answer 2 (visible)
    ("your specific work — usually either focused work time or daily learning.",
     "your specific work, usually focused work time or daily learning."),

    # FAQ answer 3 (visible)
    ("Productify supports both — you set the schedule that matches the actual behavior,",
     "Productify supports both. You set the schedule that matches the actual behavior,"),

    # FAQ answer 4 (visible)
    ("pages — so you see how much",
     "pages, so you see how much"),

    # CTA
    ("No pressure, no complexity — just a clean, honest record of the work you're putting in.",
     "No pressure, no complexity. Just a clean, honest record of the work you're putting in."),
]

for old, new in replacements:
    if old in html:
        html = html.replace(old, new, 1)
        print(f"  ✓ {old[:60]}...")
    else:
        print(f"  ✗ NOT FOUND: {old[:60]}...")

# Catch any remaining em dashes in content (not in schema strings or aria-labels)
remaining = [m.start() for m in re.finditer("—", html)]
if remaining:
    print(f"\n  ⚠ {len(remaining)} remaining em dash(es) — checking context:")
    for pos in remaining:
        print(f"    line context: ...{html[max(0,pos-40):pos+40]}...")

with open(path, "w", encoding="utf-8") as f:
    f.write(html)

print("\nDone.")
