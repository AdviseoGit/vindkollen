import os
from datetime import datetime

STATIC_PAGES = [
    "/",
    "/kalkylator",
    "/arrendekalkylator",
    "/jamforelse-ersattning-vs-arrende",
    "/om-sajten",
    "/kommun-dashboard",
    "/guider/guide-ersattning-vindkraft",
    "/sa-far-du-vindkraft-pa-din-mark",
    "/fordelar-med-vindkraft",
    "/arrendeavtal-vindkraft",
    "/ersattning-for-vindkraft",
    "/guider/nackdelar-med-vindkraft",
    "/guider/bygga-vindkraftverk-steg-for-steg",
    "/paverkar-vindkraft-fastighetsvarde",
    "/skatt-vindkraftersattning",
    "/guider/bygdepeng-guide-2026",
    "/kommunersattning-vindkraft-2026",
    "/ersattningsnivaer-region-for-region",
    "/original-data-rapport-arrende-2026",
    "/intaktsdelning-vindkraft",
    "/bullerniva-minimiavstand-vindkraft",
    "/avveckling-och-atervinning-vindkraft",
]

def generate_sitemap():
    today = datetime.now().strftime("%Y-%m-%d")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    
    for page in STATIC_PAGES:
        priority = "1.0" if page == "/" else "0.9" if "kalkylator" in page or "dashboard" in page else "0.8"
        xml.append('    <url>')
        xml.append(f'        <loc>https://vindkoll.se{page}</loc>')
        xml.append(f'        <lastmod>{today}</lastmod>')
        xml.append('        <changefreq>monthly</changefreq>')
        xml.append(f'        <priority>{priority}</priority>')
        xml.append('    </url>')
        
    xml.append('</urlset>')
    
    with open('/data/workspace/projects/vindkollen/sitemap.xml', 'w') as f:
        f.write('\n'.join(xml))

if __name__ == "__main__":
    generate_sitemap()
