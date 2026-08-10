import re
import json

file_path = "/data/workspace/projects/vindkollen/static/guider/kommunalt-veto-vindkraft.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()

schema = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "Kommunalt Veto Vindkraft: Fakta & Regler 2026",
    "author": {
        "@type": "Organization",
        "name": "Vindkollen",
        "url": "https://vindkoll.se"
    },
    "publisher": {
        "@type": "Organization",
        "name": "Vindkollen",
        "logo": {
            "@type": "ImageObject",
            "url": "https://vindkoll.se/static/favicon.svg"
        }
    },
    "mainEntityOfPage": {
        "@type": "WebPage",
        "@id": "https://vindkoll.se/guider/kommunalt-veto-vindkraft"
    }
}

new_script = f'<script type="application/ld+json">\n{json.dumps(schema, indent=4, ensure_ascii=False)}\n</script>'

html = re.sub(
    r'<script type="application/ld\+json">.*?</script>',
    new_script,
    html,
    flags=re.DOTALL
)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(html)
print("Updated schema for kommunalt-veto-vindkraft.html")
