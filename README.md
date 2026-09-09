# productifyapp.org

Jekyll site deployed to GitHub Pages by `.github/workflows/jekyll.yml` on every
push to `main`.

## Editing content

Two ways, both of which commit to `main` and trigger a deploy:

1. **Pages CMS**: sign in at [app.pagescms.org](https://app.pagescms.org) with
   GitHub and open this repo. The panel is defined by `.pages.yml`: blog posts,
   feature/comparison/solution pages, the homepage, plus the navigation menu and
   footer. No server or OAuth app to run.
2. **Directly in the repo**: edit the files under `_blog/`, `_features/`,
   `_compare/`, `_solutions/`.

## Layout

| Path | What it holds |
| --- | --- |
| `_blog/`, `_features/`, `_compare/`, `_solutions/` | page content + front matter |
| `_layouts/` | `post` (articles), `page` (marketing pages), `legal`, `default` |
| `_includes/` | head/SEO, JSON-LD, navbar, mobile drawer, footer, FAQ, breadcrumb, CTA |
| `_data/nav.yml`, `_data/footer.yml` | navigation and footer, shared by every page |
| `_plugins/toc.rb` | builds the "In this guide" contents from the article's headings |
| `sitemap.xml` | generated from the collections |

URLs come from the `permalink` settings in `_config.yml`: `/features/<slug>/`,
`/solutions/<slug>/`, `/compare/<slug>/`, and `/blog/<slug>/`. The printable
resource explicitly keeps `/habit-tracker-printable/`. The 15 migrated flat
URLs and the old habit-streaks aliases are intentionally removed, with no
redirects. `_scripts/check_urls.rb` checks that current paths exist and retired
paths are absent. Always build into a clean destination after changing URLs.

`_scripts/check_seo.py` also gates deployment: it checks canonical URLs,
unique titles/descriptions, H1s, image alt attributes, internal links and
anchors, JSON-LD URLs, social sharing URLs, consistent Productify ratings,
indexable sitemap entries, and the absence of redirect pages. Run both checks against a fresh build:

```sh
bundle exec jekyll build
ruby _scripts/check_urls.rb
python3 _scripts/check_seo.py
```

The homepage is `index.html`. The `index.md` companion is excluded from
publishing by `_config.yml`; keep its product details synchronized before
ever enabling it. Feature, solution and comparison HTML is generated only
from its collection; do not add physical `index.html` files at those output
paths, since they would collide with the generated pages.

## Things worth knowing

- **FAQs live in front matter**, not in the body. One list drives both the
  visible accordion and the `FAQPage` structured data. Google requires the two
  to match, and they had drifted apart on several posts before the migration.
- **The table of contents is generated** from `<h2 id="...">` headings. Three
  posts set an explicit `toc_items` list because some of their entries point at
  section wrappers rather than headings.
- **`heading`** overrides the visible `<h1>` where it deliberately differs from
  the `title` used for `og:title` and search results.
- **`sitemap: false`** keeps a page out of `sitemap.xml`. Canonical collection
  URLs are included automatically when their permalinks change.

## Local development

```sh
bundle install
bundle exec jekyll serve
```

Requires Ruby 3.x (CI pins 3.3).
