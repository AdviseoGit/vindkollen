import os
import glob
import re
import json

files = [
    "/data/workspace/projects/vindkollen/static/ersattningsmodeller-vindkraft.html",
    "/data/workspace/projects/vindkollen/static/guide-ersattning-vindkraft.html",
    "/data/workspace/projects/vindkollen/static/jamforelse-ersattning-vs-arrende.html",
    "/data/workspace/projects/vindkollen/static/ersattning-vindkraft.html",
    "/data/workspace/projects/vindkollen/static/guider/nackdelar-vindkraft-detaljerad-guide.html",
    "/data/workspace/projects/vindkollen/static/guider/bygdepeng-och-kommunersattning-2026.html"
]

schema_template = {
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "",
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
      "url": "https://vindkoll.se/favicon.ico"
    }
  },
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": ""
  }
}

for filepath in files:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if '<script type="application/ld+json">' in content:
            continue
            
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        title = title_match.group(1) if title_match else "Vindkollen Guide"
        
        filename = os.path.basename(filepath)
        url = f"https://vindkoll.se/{filename.replace('.html', '')}"
        
        schema = schema_template.copy()
        schema["headline"] = title
        schema["mainEntityOfPage"]["@id"] = url
        
        schema_json = json.dumps(schema, ensure_ascii=False, indent=2)
        schema_script = f'\n    <script type="application/ld+json">\n{schema_json}\n    </script>\n</head>'
        
        content = content.replace('</head>', schema_script)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Added schema to {filepath}")
    except FileNotFoundError:
        print(f"File not found: {filepath}")
