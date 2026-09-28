#!/usr/bin/env ruby
# Check the current URL architecture after a fresh Jekyll build. Pages must
# exist at their canonical paths and legacy paths must have redirect pages.
require "json"

SITE = ARGV[0] ? File.expand_path(ARGV[0]) : File.expand_path("../_site", __dir__)

REQUIRED = %w[
  /
  /blog/
  /guides/
  /blog/areas-of-life/
  /blog/bad-habits-list/
  /blog/best-habit-tracker-apps-2026/
  /blog/habit-tracker-vs-to-do-list/
  /blog/how-long-to-build-a-habit/
  /blog/accountability-partner/
  /guides/how-many-goals-should-i-set/
  /guides/how-to-break-bad-habits/
  /guides/how-to-build-habits-that-stick/
  /guides/how-to-start-a-daily-habit/
  /guides/how-to-build-a-reading-habit/
  /guides/how-to-use-a-habit-tracker/
  /guides/habit-duo/
  /blog/what-habits-to-track/
  /compare/productify-vs-habitica/
  /compare/productify-vs-habitify/
  /features/ai-analyser/
  /features/habit-duo/
  /features/streak-tracking/
  /features/habit-templates/
  /features/habit-tracker/
  /guides/habit-tracker-printable/
  /assets/printables/habit-tracker-monthly-a4.pdf
  /assets/printables/habit-tracker-monthly-letter.pdf
  /assets/printables/habit-tracker-weekly-monday-a4.pdf
  /assets/printables/habit-tracker-weekly-monday-letter.pdf
  /assets/printables/habit-tracker-weekly-sunday-a4.pdf
  /assets/printables/habit-tracker-weekly-sunday-letter.pdf
  /tools/
  /de/
  /fr/
  /ja/
  /ko/
  /assets/localized.css
  /de/tools/
  /de/tools/30-day-habit-tracker/
  /de/tools/year-in-pixels/
  /de/tools/habit-tracker-printable/
  /de/tools/habit-streak-calculator/
  /assets/printables/de/30-day-habit-tracker-multi-a4.pdf
  /assets/printables/de/30-day-habit-tracker-single-a4.pdf
  /assets/printables/de/habit-tracker-monthly-a4.pdf
  /assets/printables/de/habit-tracker-weekly-monday-a4.pdf
  /assets/printables/de/year-in-pixels-a4.pdf
  /fr/tools/
  /fr/tools/30-day-habit-tracker/
  /fr/tools/year-in-pixels/
  /fr/tools/habit-tracker-printable/
  /fr/tools/habit-streak-calculator/
  /assets/printables/fr/30-day-habit-tracker-multi-a4.pdf
  /assets/printables/fr/30-day-habit-tracker-multi-letter.pdf
  /assets/printables/fr/30-day-habit-tracker-single-a4.pdf
  /assets/printables/fr/30-day-habit-tracker-single-letter.pdf
  /assets/printables/fr/habit-tracker-monthly-a4.pdf
  /assets/printables/fr/habit-tracker-monthly-letter.pdf
  /assets/printables/fr/habit-tracker-weekly-monday-a4.pdf
  /assets/printables/fr/habit-tracker-weekly-monday-letter.pdf
  /assets/printables/fr/year-in-pixels-a4.pdf
  /assets/printables/fr/year-in-pixels-letter.pdf
  /ja/tools/
  /ja/tools/30-day-habit-tracker/
  /ja/tools/year-in-pixels/
  /ja/tools/habit-tracker-printable/
  /ja/tools/habit-streak-calculator/
  /assets/printables/ja/30-day-habit-tracker-multi-a4.pdf
  /assets/printables/ja/30-day-habit-tracker-single-a4.pdf
  /assets/printables/ja/habit-tracker-monthly-a4.pdf
  /assets/printables/ja/habit-tracker-weekly-monday-a4.pdf
  /assets/printables/ja/habit-tracker-weekly-sunday-a4.pdf
  /assets/printables/ja/year-in-pixels-a4.pdf
  /ko/tools/
  /ko/tools/30-day-habit-tracker/
  /ko/tools/year-in-pixels/
  /ko/tools/habit-tracker-printable/
  /ko/tools/habit-streak-calculator/
  /assets/printables/ko/30-day-habit-tracker-multi-a4.pdf
  /assets/printables/ko/30-day-habit-tracker-single-a4.pdf
  /assets/printables/ko/habit-tracker-monthly-a4.pdf
  /assets/printables/ko/habit-tracker-weekly-monday-a4.pdf
  /assets/printables/ko/habit-tracker-weekly-sunday-a4.pdf
  /assets/printables/ko/year-in-pixels-a4.pdf
  /assets/streak-calculator.js
  /guides/30-day-habit-tracker/
  /guides/year-in-pixels/
  /guides/habit-streak-calculator/
  /assets/printables/30-day-habit-tracker-single-a4.pdf
  /assets/printables/30-day-habit-tracker-single-letter.pdf
  /assets/printables/30-day-habit-tracker-multi-a4.pdf
  /assets/printables/30-day-habit-tracker-multi-letter.pdf
  /assets/printables/year-in-pixels-a4.pdf
  /assets/printables/year-in-pixels-letter.pdf
  /features/measurable-goals/
  /solutions/evening-routine/
  /solutions/habit-tracker-for-adhd/
  /solutions/morning-routine/
  /solutions/productivity-at-work/
  /pricing/
  /download/
  /privacy.html
  /terms.html
  /sitemap.xml
  /robots.txt
  /llms.txt
  /shared.css
  /editorial/
  /compare/productify-vs-loop/
  /compare/productify-vs-productive/
  /compare/productify-vs-streaks/
].freeze

REDIRECTS = JSON.parse(File.read(File.expand_path("../_data/redirects.json", __dir__))).freeze

def output_path(url)
  path = File.join(SITE, url)
  url.end_with?("/") ? File.join(path, "index.html") : path
end

missing = (REQUIRED + REDIRECTS.keys + REDIRECTS.values).uniq.reject { |url| File.file?(output_path(url)) }
missing.each { |url| warn "check_urls: missing URL #{url}" }
exit 1 unless missing.empty?

puts "check_urls: all #{REQUIRED.size} required URLs and #{REDIRECTS.size} legacy redirects exist"
