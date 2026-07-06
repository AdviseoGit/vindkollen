import re
import json

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Fix multiple H1s by changing subsequent H1s to H2s
        h1_matches = list(re.finditer(r'<h1(.*?)>(.*?)</h1>', content, re.IGNORECASE))
        if len(h1_matches) > 1:
            print(f"Fixing multiple H1s in {filepath}")
            for match in h1_matches[1:]: # Skip the first one
                original = match.group(0)
                replacement = f"<h2{match.group(1)}>{match.group(2)}</h2>"
                content = content.replace(original, replacement, 1) # replace just this one

        # Truncate overly long meta descriptions
        meta_desc_match = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', content, re.IGNORECASE)
        if meta_desc_match:
             desc = meta_desc_match.group(1)
             if len(desc) > 160:
                 print(f"Truncating long meta description in {filepath}")
                 short_desc = desc[:157] + "..."
                 content = content.replace(f'content="{desc}"', f'content="{short_desc}"')
        elif re.search(r'<meta[^>]*content="([^"]*)"[^>]*name="description"', content, re.IGNORECASE):
             meta_desc_match = re.search(r'<meta[^>]*content="([^"]*)"[^>]*name="description"', content, re.IGNORECASE)
             desc = meta_desc_match.group(1)
             if len(desc) > 160:
                 print(f"Truncating long meta description in {filepath}")
                 short_desc = desc[:157] + "..."
                 content = content.replace(f'content="{desc}"', f'content="{short_desc}"')

        # Provide a basic meta description if missing
        if 'name="description"' not in content.lower():
             print(f"Adding missing meta description to {filepath}")
             title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
             title = title_match.group(1) if title_match else "Läs mer om vindkraft och ersättningar på Vindkollen."
             # A simple generic meta desc
             meta_tag = f'\n    <meta name="description" content="{title[:160]}">\n'
             content = content.replace('</title>', f'</title>{meta_tag}')

        # Truncate excessively long titles
        title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
        if title_match:
            title = title_match.group(1)
            if len(title) > 60:
                print(f"Truncating long title in {filepath}")
                # We want to keep " | Vindkollen" if it's there
                if " | Vindkollen" in title:
                     base = title.replace(" | Vindkollen", "")
                     short_title = base[:45] + " | Vindkollen"
                elif " - Vindkollen" in title:
                     base = title.replace(" - Vindkollen", "")
                     short_title = base[:45] + " | Vindkollen"
                else:
                     short_title = title[:60]
                content = content.replace(f'<title>{title}</title>', f'<title>{short_title}</title>')


        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

files_to_fix = [
    '/data/workspace/projects/vindkollen/static/ersattningsmodeller-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/avveckling-och-atervinning-vindkraftverk.html',
    '/data/workspace/projects/vindkollen/static/intaktsdelning-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/kommun-dashboard.html',
    '/data/workspace/projects/vindkollen/static/skatt-vindkraftersattning.html',
    '/data/workspace/projects/vindkollen/static/guide-ersattning-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/original-data-rapport-arrende-2026.html',
    '/data/workspace/projects/vindkollen/static/paverkar-vindkraft-fastighetsvarde.html',
    '/data/workspace/projects/vindkollen/static/jamforelse-ersattning-vs-arrende.html',
    '/data/workspace/projects/vindkollen/static/ersattning-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/bullerniva-minimiavstand-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/sa-far-du-vindkraft-pa-din-mark.html',
    '/data/workspace/projects/vindkollen/static/kommunersattning-vindkraft-2026.html',
    '/data/workspace/projects/vindkollen/static/fordelar-med-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/ersattningsnivaer-region-for-region.html',
    '/data/workspace/projects/vindkollen/static/guider/guide-ersattning-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/guider/bygga-vindkraftverk-steg-for-steg.html',
    '/data/workspace/projects/vindkollen/static/guider/vindkraftsersattning-2026.html',
    '/data/workspace/projects/vindkollen/static/guider/bygdepeng-guide-2026.html'
]

for f in files_to_fix:
    fix_file(f)
