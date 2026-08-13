#!/usr/bin/env ruby
# Fails the build if any URL that the pre-Jekyll site published stops resolving.
# Run after `jekyll build`; the deploy workflow gates on it.
require "set"

SITE = File.expand_path("../_site", __dir__)

REQUIRED = %w[
  /
  /blog/
  /blog/areas-of-life/
  /blog/bad-habits-list/
  /blog/best-habit-tracker-apps-2026/
  /blog/habit-tracker-vs-to-do-list/
  /blog/how-long-to-build-a-habit/
  /blog/how-many-goals-should-i-set/
  /blog/how-to-break-bad-habits/
  /blog/how-to-build-habits-that-stick/
  /blog/how-to-start-a-daily-habit/
  /blog/how-to-use-a-habit-tracker/
  /blog/what-habits-to-track/
  /compare/productify-vs-habitica/
  /compare/productify-vs-habitify/
  /features/ai-analyser/
  /features/habit-duo/
  /features/habit-streaks/
  /features/habit-templates/
  /features/habit-tracker/
  /features/measurable-goals/
  /features/streak-tracking/
  /solutions/morning-routine/
  /solutions/productivity-at-work/
  /privacy.html
  /terms.html
  /sitemap.xml
  /robots.txt
  /llms.txt
  /shared.css
  /index.md
  /blog/index.md
  /blog/habit-tracker-vs-to-do-list/index.md
  /blog/how-long-to-build-a-habit/index.md
  /blog/how-to-start-a-daily-habit/index.md
  /blog/how-to-use-a-habit-tracker/index.md
  /blog/what-habits-to-track/index.md
  /features/ai-analyser/index.md
  /features/habit-duo/index.md
  /features/habit-streaks/index.md
  /features/habit-templates/index.md
  /features/habit-tracker/index.md
  /features/measurable-goals/index.md
  /features/streak-tracking/index.md
  /solutions/morning-routine/index.md
  /solutions/productivity-at-work/index.md
].freeze

missing = REQUIRED.reject do |url|
  path = url.end_with?("/") ? File.join(SITE, url, "index.html") : File.join(SITE, url)
  File.file?(path)
end

if missing.empty?
  puts "check_urls: all #{REQUIRED.size} published URLs resolve"
else
  warn "check_urls: #{missing.size} URL(s) missing from the build:"
  missing.each { |u| warn "  #{u}" }
  exit 1
end
