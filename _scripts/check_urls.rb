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
  /guides/how-many-goals-should-i-set/
  /guides/how-to-break-bad-habits/
  /guides/how-to-build-habits-that-stick/
  /guides/how-to-start-a-daily-habit/
  /guides/how-to-use-a-habit-tracker/
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
  /blog/habit-duo/
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
