# Stamps every page and document with the date of the last commit that touched
# its source file, exposed as `page.git_lastmod`.
#
# Why: sitemap <lastmod> and JSON-LD dateModified were hand-maintained through
# `sitemap_lastmod` / `last_modified` front matter, so they drifted. After the
# August 2026 site-wide rewrite the sitemap still advertised April and May
# dates, which is exactly the wrong signal to send Google when you want a
# recrawl. Git already knows when each file really changed; ask it.
#
# Requires full history. The Actions workflow sets `fetch-depth: 0` on
# checkout for this reason -- a shallow clone yields no per-file log, in which
# case this falls back silently and the old front-matter values still apply.
module Jekyll
  class GitLastModified < Generator
    safe true
    priority :high

    def generate(site)
      @source = site.source
      return unless git_repo?

      cache = {}
      (site.pages + site.documents).each do |item|
        path = item.respond_to?(:path) ? item.path : nil
        next if path.nil? || path.empty?
        stamp = cache[path] ||= committed_at(path)
        item.data["git_lastmod"] = stamp if stamp
      end
    end

    private

    def git_repo?
      out, ok = run(%w[git rev-parse --is-inside-work-tree])
      ok && out == "true"
    end

    # %cI is the committer date, ISO 8601. Empty for an untracked or
    # newly added file, which is correct: it has no commit yet.
    def committed_at(path)
      rel = path.sub(/\A#{Regexp.escape(@source)}\/?/, "")
      out, ok = run(["git", "log", "-1", "--format=%cI", "--", rel])
      return nil unless ok && !out.empty?
      Time.parse(out)
    rescue ArgumentError
      nil
    end

    def run(cmd)
      require "open3"
      out, status = Open3.capture2(*cmd, chdir: @source)
      [out.strip, status.success?]
    rescue StandardError => e
      Jekyll.logger.warn "GitLastModified:", "#{cmd.join(' ')} failed (#{e.class}); falling back to front matter"
      ["", false]
    end
  end
end
