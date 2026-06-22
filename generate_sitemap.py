"""Regenerate sitemap.xml from the static page list and content/ markdown files.

The previous version hard-coded the wrong domain (vindkollen.se) and a
projects/-prefixed path that no longer exists. This rewrite reflects the
production layout: site is served at https://vindkoll.se and content lives
in ./content.
"""

import os
from datetime import datetime


BASE_URL = "https://vindkoll.se"
CONTENT_DIR = "content"
SITEMAP_PATH = "sitemap.xml"

# (path, priority, changefreq) — kept in priority order.
STATIC_PAGES = [
    ("/", "1.0", "weekly"),
    ("/kalkylator", "0.9", "weekly"),
    ("/arrendekalkylator", "0.9", "weekly"),
    ("/om-sajten", "0.5", "monthly"),
    ("/kommun-dashboard", "0.9", "monthly"),
    ("/guider/guide-ersattning-vindkraft", "0.8", "monthly"),
    ("/sa-far-du-vindkraft-pa-din-mark", "0.7", "monthly"),
    ("/fordelar-med-vindkraft", "0.7", "monthly"),
    ("/arrendeavtal-vindkraft", "0.7", "monthly"),
    ("/nackdelar-med-vindkraft", "0.8", "monthly"),
    ("/ersattning-for-vindkraft", "0.8", "monthly"),
    ("/guider/nackdelar-med-vindkraft", "0.8", "monthly"),
    ("/guider/bygga-vindkraftverk-steg-for-steg", "0.8", "monthly"),
    ("/paverkar-vindkraft-fastighetsvarde", "0.8", "monthly"),
    ("/skatt-vindkraftersattning", "0.8", "monthly"),
    ("/guider/bygdepeng-guide-2026", "0.8", "monthly"),
]


def generate_sitemap() -> None:
    today = datetime.now().strftime("%Y-%m-%d")
    urls = []

    for path, priority, freq in STATIC_PAGES:
        urls.append(
            f"""
    <url>
        <loc>{BASE_URL}{path}</loc>
        <lastmod>{today}</lastmod>
        <changefreq>{freq}</changefreq>
        <priority>{priority}</priority>
    </url>"""
        )

    # (content/*.md auto-include removed: those slugs are not served)

    sitemap_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
        f'{"".join(urls)}\n'
        "</urlset>\n"
    )

    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    print(f"Sitemap generated at {SITEMAP_PATH}")


if __name__ == "__main__":
    generate_sitemap()
