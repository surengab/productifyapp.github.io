#!/usr/bin/env ruby
# Fails the build if any URL the site has ever published stops resolving. That
# includes the pre-Jekyll paths and the /features/ /compare/ /solutions/ URLs
# retired in the flattening, which must keep serving their redirect stubs.
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
  /productify-vs-habitica/
  /productify-vs-habitify/
  /ai-analyser/
  /habit-duo/
  /habit-streaks/
  /habit-templates/
  /habit-tracker/
  /measurable-goals/
  /streak-tracking/
  /morning-routine/
  /productivity-at-work/
  /privacy.html
  /terms.html
  /sitemap.xml
  /robots.txt
  /llms.txt
  /shared.css
  /features/ai-analyser/
  /features/habit-duo/
  /features/habit-streaks/
  /features/habit-templates/
  /features/habit-tracker/
  /features/measurable-goals/
  /features/streak-tracking/
  /compare/productify-vs-habitica/
  /compare/productify-vs-habitify/
  /solutions/morning-routine/
  /solutions/productivity-at-work/
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
