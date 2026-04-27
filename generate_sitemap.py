import os
from datetime import datetime

def generate_sitemap():
    base_url = "https://vindkollen.se"
    content_dir = "projects/vindkollen/content"
    static_pages = ["/", "/kalkylator"]
    sitemap_path = "projects/vindkollen/sitemap.xml"

    urls = []

    # Add static pages
    for page in static_pages:
        urls.append(f"""
    <url>
        <loc>{base_url}{page}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <priority>0.8</priority>
    </url>""")

    # Add content pages
    for filename in os.listdir(content_dir):
        if filename.endswith(".md"):
            # Create a URL-friendly slug from the filename
            slug = os.path.splitext(filename)[0].replace('_', '-')
            urls.append(f"""
    <url>
        <loc>{base_url}/{slug}</loc>
        <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
        <priority>0.6</priority>
    </url>""")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls)}
</urlset>
"""

    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write(sitemap_content)

    print(f"Sitemap generated at {sitemap_path}")

if __name__ == "__main__":
    generate_sitemap()
