require "cgi"
require "json"

module Jekyll
  class LegacyRedirects < Generator
    safe true

    def generate(site)
      site.data.fetch("redirects", {}).each do |old_path, new_path|
        destination = "#{site.config['url']}#{site.config['baseurl']}#{new_path}"
        escaped = CGI.escapeHTML(destination)
        page = PageWithoutAFile.new(site, site.source, old_path.delete_prefix("/"), "index.html")
        page.data.merge!("layout" => nil, "sitemap" => false, "redirect_to" => destination)
        # GitHub Pages serves static files: use an immediate refresh and canonical.
        # JavaScript also preserves query parameters and section links in old URLs.
        page.content = <<~HTML
          <!doctype html>
          <html lang="en">
          <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Page moved | Productify</title>
            <link rel="canonical" href="#{escaped}">
            <script>window.location.replace(#{JSON.generate(destination)} + window.location.search + window.location.hash);</script>
            <meta http-equiv="refresh" content="0; url=#{escaped}">
          </head>
          <body><p>This page has moved to <a href="#{escaped}">its new location</a>.</p></body>
          </html>
        HTML
        site.pages << page
      end
    end
  end
end
