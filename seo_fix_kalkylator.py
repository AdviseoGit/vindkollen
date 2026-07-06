import re
import json

def fix_desc(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        schema_template = {
          "@context": "https://schema.org",
          "@type": "SoftwareApplication",
          "name": "Kommunersättning Vindkraft Kalkylator",
          "applicationCategory": "BusinessApplication",
          "operatingSystem": "Web",
          "description": "Räkna ut potentiell kommunersättning för vindkraft enligt de senaste förslagen 2026 (motsvarande intäkt från fastighetsskatt).",
          "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "SEK"
          }
        }
        
        schema_json = json.dumps(schema_template, ensure_ascii=False, indent=2)
        schema_script = f'\n    <script type="application/ld+json">\n{schema_json}\n    </script>\n</head>'
        
        if '<script type="application/ld+json">' not in content:
             content = content.replace('</head>', schema_script)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

fix_desc('/data/workspace/projects/vindkollen/static/kommunersattning-kalkylator.html')
