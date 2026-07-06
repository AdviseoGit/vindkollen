import re

def fix_desc(filepath, manual_desc=None):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Some might be missing a <meta name="description"... tag entirely
        if 'name="description"' not in content.lower():
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
            title = title_match.group(1) if title_match else "Läs mer om vindkraft och ersättningar på Vindkollen."
            desc = manual_desc if manual_desc else title[:157]
            meta_tag = f'\n    <meta name="description" content="{desc}">\n'
            content = content.replace('</title>', f'</title>{meta_tag}')
        else:
            # Let's ensure the meta desc format is correct.
            content = re.sub(r'<meta[^>]*content="([^"]*)"[^>]*name="description"[^>]*>', r'<meta name="description" content="\1">', content, flags=re.IGNORECASE)
            content = re.sub(r'<meta[^>]*name="description"[^>]*content="([^"]*)"[^>]*>', r'<meta name="description" content="\1">', content, flags=re.IGNORECASE)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

files = [
    '/data/workspace/projects/vindkollen/static/kommun-dashboard.html',
    '/data/workspace/projects/vindkollen/static/skatt-vindkraftersattning.html',
    '/data/workspace/projects/vindkollen/static/original-data-rapport-arrende-2026.html',
    '/data/workspace/projects/vindkollen/static/paverkar-vindkraft-fastighetsvarde.html',
    '/data/workspace/projects/vindkollen/static/sa-far-du-vindkraft-pa-din-mark.html',
    '/data/workspace/projects/vindkollen/static/fordelar-med-vindkraft.html',
    '/data/workspace/projects/vindkollen/static/guider/vindkraftsersattning-2026.html',
    '/data/workspace/projects/vindkollen/static/guider/bygdepeng-guide-2026.html'
]

for f in files:
    fix_desc(f)
