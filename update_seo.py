import os
import re

updates = {
    "/data/workspace/projects/vindkollen/static/index.html": {
        "title": "Vindkollen | Oberoende guider & kalkylator för vindkraft",
        "description": "Räkna ut din ersättning för vindkraft. Oberoende guider för markägare och närboende om bygdepeng, arrende och dina rättigheter 2026."
    },
    "/data/workspace/projects/vindkollen/static/kalkylator.html": {
        "title": "Ersättningskalkylator för Vindkraft 2026 | Vindkollen",
        "description": "Beräkna din uppskattade vindkraftsersättning som närboende. Fyll i avstånd, antal verk och få en direkt uppskattning på din årliga ersättning."
    },
    "/data/workspace/projects/vindkollen/static/arrendekalkylator.html": {
        "title": "Arrendekalkylator för Vindkraft | Räkna ut din intäkt",
        "description": "Markägare? Räkna ut ditt potentiella vindkraftsarrende per år. Kalkylator baserad på aktuella marknadspriser och produktionsestimat för 2026."
    },
    "/data/workspace/projects/vindkollen/static/ersattning-for-vindkraft.html": {
        "title": "Ersättning Vindkraft 2026 | Markägare & Närboende",
        "description": "Allt du behöver veta om ersättning för vindkraft 2026. Guide för markägare och närboende med fokus på arrendeavtal, bygdepeng och inlösen."
    },
    "/data/workspace/projects/vindkollen/static/nackdelar-med-vindkraft.html": {
        "title": "Nackdelar med Vindkraft: Buller, Skuggor & Fastighetsvärde",
        "description": "Vad är nackdelarna med att bo nära vindkraftverk? Läs om ljudnivåer, skuggkastning, påverkan på fastighetsvärde och dina rättigheter som granne."
    },
    "/data/workspace/projects/vindkollen/static/arrendeavtal-vindkraft.html": {
        "title": "Arrendeavtal Vindkraft: Detta ska du tänka på (Guide)",
        "description": "Ska du skriva arrendeavtal för vindkraft? Lär dig om fallgropar, indexuppräkning, minimiarrende och vad som händer när vindkraftverket ska rivas."
    }
}

for filepath, meta in updates.items():
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Update title
        content = re.sub(r'<title>.*?</title>', f"<title>{meta['title']}</title>", content, flags=re.IGNORECASE | re.DOTALL)
        
        # Update or insert description
        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*>', content, re.IGNORECASE)
        desc_tag = f'<meta name="description" content="{meta["description"]}">'
        
        if desc_match:
            content = content.replace(desc_match.group(0), desc_tag)
        else:
            # Insert after title
            content = re.sub(r'(<title>.*?</title>)', r'\1\n    ' + desc_tag, content, flags=re.IGNORECASE | re.DOTALL)
            
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {filepath}")
    except FileNotFoundError:
        print(f"File not found: {filepath}")

