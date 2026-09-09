#!/usr/bin/env ruby
# Check the current URL architecture after a fresh Jekyll build. Pages must
# exist at their canonical paths; retired flat URLs and aliases must be absent.
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

RETIRED = %w[
  /blog/how-to-use-a-habit-tracker/
  /blog/how-to-start-a-daily-habit/
  /blog/how-to-build-habits-that-stick/
  /blog/how-to-break-bad-habits/
  /blog/how-many-goals-should-i-set/
  /habit-tracker-printable/
  /habit-duo/
  /habit-templates/
  /habit-tracker/
  /streak-tracking/
  /ai-analyser/
  /measurable-goals/
  /evening-routine/
  /habit-tracker-for-adhd/
  /morning-routine/
  /productivity-at-work/
  /productify-vs-habitica/
  /productify-vs-habitify/
  /productify-vs-loop/
  /productify-vs-productive/
  /productify-vs-streaks/
  /habit-streaks/
  /features/habit-streaks/
].freeze

def output_path(url)
  path = File.join(SITE, url)
  url.end_with?("/") ? File.join(path, "index.html") : path
end

missing = REQUIRED.reject { |url| File.file?(output_path(url)) }
retained = RETIRED.select { |url| File.file?(output_path(url)) }
missing.each { |url| warn "check_urls: missing canonical URL #{url}" }
retained.each { |url| warn "check_urls: retired URL still published #{url}" }
exit 1 unless missing.empty? && retained.empty?

puts "check_urls: all #{REQUIRED.size} required URLs resolve; #{RETIRED.size} retired URLs are absent"
