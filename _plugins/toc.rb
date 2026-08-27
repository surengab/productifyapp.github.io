# Builds the "In this guide" table of contents from the <h2 id="..."> elements
# kramdown generates for the post body, so adding a section to an article no
# longer means hand-editing a second list that can silently fall out of sync.
#
# Opt out per page with `toc: false`. Exclude a single heading with
# {: .no-toc} on the kramdown heading.
#
# The title is a <p class="toc__title">, matching the explicit `toc_items`
# branch in _layouts/post.html. It was an <h4>, which both skipped a heading
# level after the article <h1> and missed the `.toc > p` styling the posts
# define, so the two rendering paths disagreed visually.
module Jekyll
  module TocFilter
    HEADING = %r{<h2[^>]*\sid="([^"]+)"[^>]*>(.*?)</h2>}m

    def toc(html)
      return "" if html.nil?

      entries = html.to_s.scan(HEADING).reject do |id, inner|
        inner =~ /class="no-toc"/ || id.empty?
      end
      return "" if entries.empty?

      items = entries.map do |id, inner|
        label = inner.gsub(%r{<a\s[^>]*class="[^"]*anchor[^"]*".*?</a>}m, "")
                     .gsub(%r{<[^>]+>}, "")
                     .strip
        %(                    <li><a href="##{id}">#{label}</a></li>)
      end

      <<~HTML.rstrip
        <nav class="toc" aria-label="Table of contents">
                        <p class="toc__title">In this guide</p>
                        <ol>
        #{items.join("\n")}
                        </ol>
                    </nav>
      HTML
    end
  end
end

Liquid::Template.register_filter(Jekyll::TocFilter)
