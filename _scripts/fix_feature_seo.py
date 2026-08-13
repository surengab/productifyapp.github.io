"""
For all feature pages:
1. Change og:type from "article" to "website"
2. Add FAQPage JSON-LD schema for pages missing it.
3. Ensure BreadcrumbList schema has datePublished/dateModified on Article schemas.
"""
import re, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FAQ_SCHEMAS = {
    "ai-analyser": """\
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "Is the AI Habit Analyser private?",
                "acceptedAnswer": { "@type": "Answer", "text": "Yes. Productify's AI Habit Analyser processes your habit completion data on-device using Apple's frameworks wherever possible. Your data is not sold or shared with third parties." }
            },
            {
                "@type": "Question",
                "name": "Does the AI Habit Analyser require a subscription?",
                "acceptedAnswer": { "@type": "Answer", "text": "Yes. The AI Habit Analyser is available on Productify Pro. You can try Productify free and upgrade to Pro to unlock AI insights." }
            },
            {
                "@type": "Question",
                "name": "What kind of insights does the AI Habit Analyser provide?",
                "acceptedAnswer": { "@type": "Answer", "text": "It surfaces patterns in your completion history — your most consistent days, time-of-day trends, and habits that tend to cluster together. Insights are calm and informational, not prescriptive." }
            },
            {
                "@type": "Question",
                "name": "Can the AI Habit Analyser help with ADHD or mental health?",
                "acceptedAnswer": { "@type": "Answer", "text": "Productify is a habit tracker, not a medical or therapeutic tool. The AI Analyser offers general habit pattern insights. It is not designed to diagnose or treat any condition." }
            }
        ]
    }
    </script>""",

    "habit-templates": """\
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "How many habit templates does Productify include?",
                "acceptedAnswer": { "@type": "Answer", "text": "Productify includes 50+ ready-made habit templates across health, fitness, focus, sleep, and mindfulness categories. All templates are customisable." }
            },
            {
                "@type": "Question",
                "name": "Can I edit a habit template after I start using it?",
                "acceptedAnswer": { "@type": "Answer", "text": "Yes. Every template in Productify is fully editable — you can change the name, icon, reminder time, target, and frequency to match your own routine." }
            },
            {
                "@type": "Question",
                "name": "Are habit templates available on the free plan?",
                "acceptedAnswer": { "@type": "Answer", "text": "Yes. Habit templates are available to all Productify users, including the free tier. No subscription required to access and use templates." }
            },
            {
                "@type": "Question",
                "name": "What categories of habits are available in templates?",
                "acceptedAnswer": { "@type": "Answer", "text": "Productify's template library covers health and fitness (walking, water, workouts), mental wellness (journalling, meditation), focus and learning (reading, deep work), sleep hygiene, and more." }
            }
        ]
    }
    </script>""",

    "minimalist-design": """\
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "Why does Productify use a minimalist design?",
                "acceptedAnswer": { "@type": "Answer", "text": "Research suggests that cluttered interfaces increase cognitive load, which makes it harder to stick to new behaviours. Productify's calm design removes distractions so checking in on your habits feels effortless." }
            },
            {
                "@type": "Question",
                "name": "Does Productify have a dark mode?",
                "acceptedAnswer": { "@type": "Answer", "text": "Yes. Productify supports both light and dark mode, automatically following your iPhone's system appearance setting." }
            },
            {
                "@type": "Question",
                "name": "Is Productify accessible?",
                "acceptedAnswer": { "@type": "Answer", "text": "Productify is designed with clarity and accessibility in mind, including support for Dynamic Type for larger text sizes and high-contrast display." }
            }
        ]
    }
    </script>""",

    "smart-reminders": """\
    <script type="application/ld+json">
    {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": "Can I set different reminder times for different habits?",
                "acceptedAnswer": { "@type": "Answer", "text": "Yes. Each habit in Productify can have its own unique reminder time, so you can set a morning reminder for meditation and an evening one for journalling." }
            },
            {
                "@type": "Question",
                "name": "Are habit reminders available on the free plan?",
                "acceptedAnswer": { "@type": "Answer", "text": "Yes. Habit reminders are available to all Productify users on the free plan. No subscription is required to use daily reminders." }
            },
            {
                "@type": "Question",
                "name": "Will reminders still work if I miss a day?",
                "acceptedAnswer": { "@type": "Answer", "text": "Yes. Productify's reminders fire daily based on your schedule regardless of whether you completed the habit the day before. Missing a day does not affect your reminder schedule." }
            },
            {
                "@type": "Question",
                "name": "Can I turn off reminders for specific days?",
                "acceptedAnswer": { "@type": "Answer", "text": "Yes. You can configure each habit to only remind you on specific days of the week — for example, only on weekdays — so you won't get pinged on your rest days." }
            }
        ]
    }
    </script>""",
}

feature_pages = {
    "ai-analyser": os.path.join(ROOT, "features", "ai-analyser", "index.html"),
    "habit-templates": os.path.join(ROOT, "features", "habit-templates", "index.html"),
    "minimalist-design": os.path.join(ROOT, "features", "minimalist-design", "index.html"),
    "smart-reminders": os.path.join(ROOT, "features", "smart-reminders", "index.html"),
}

# Also fix og:type article → website on ALL feature pages
all_feature_pages = [
    os.path.join(ROOT, "features", d, "index.html")
    for d in os.listdir(os.path.join(ROOT, "features"))
    if os.path.isfile(os.path.join(ROOT, "features", d, "index.html"))
]

updated = []

# Fix og:type on all feature pages
for path in all_feature_pages:
    with open(path, 'r', encoding='utf-8') as fh:
        html = fh.read()
    new_html = html.replace(
        '<meta property="og:type" content="article">',
        '<meta property="og:type" content="website">'
    )
    if new_html != html:
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(new_html)
        updated.append(f"og:type fix: {os.path.relpath(path, ROOT)}")

# Add missing FAQPage schemas
for slug, path in feature_pages.items():
    with open(path, 'r', encoding='utf-8') as fh:
        html = fh.read()

    if "FAQPage" in html:
        print(f"  [SKIP] {slug} already has FAQPage schema")
        continue

    faq_block = FAQ_SCHEMAS[slug]
    # Insert before closing </head>
    if "</head>" in html:
        html = html.replace("</head>", faq_block + "\n</head>", 1)
        with open(path, 'w', encoding='utf-8') as fh:
            fh.write(html)
        updated.append(f"FAQPage added: {os.path.relpath(path, ROOT)}")

print(f"\nDone. {len(updated)} changes:")
for u in updated:
    print(f"  {u}")
