import os
import re

files = [f for f in os.listdir('/data/workspace/projects/vindkollen/static/') if f.endswith('.html')]

print("Checking internal links in HTML files...")
broken_links = 0
for file in files:
    with open(f"/data/workspace/projects/vindkollen/static/{file}", 'r', encoding='utf-8') as f:
        content = f.read()
        
    links = re.findall(r'href="([^"]+)"', content)
    for link in links:
        if link.startswith('http') or link.startswith('#') or link.startswith('mailto:'):
            continue
            
        link_path = link.split('#')[0].split('?')[0]
        if link_path == '/' or link_path.endswith('.svg') or link_path.endswith('.png') or link_path.endswith('.css') or link_path.endswith('.js'):
            continue
            
        # Strip trailing slash if it exists
        if link_path.endswith('/'):
            link_path = link_path[:-1]
            
        # Check if corresponding HTML file exists
        if not os.path.exists(f"/data/workspace/projects/vindkollen/static/{link_path}.html") and not os.path.exists(f"/data/workspace/projects/vindkollen/static{link_path}.html"):
            # Exclude known dynamic routes or routes without specific HTML files but handled in main.py
            if not link_path in ['/kalkylator', '/arrendekalkylator', '/ersattning-for-vindkraft', '/kommun-dashboard', '/om-sajten', '/api', '/healthz']:
                 # Check main.py to see if it's explicitly handled
                 with open('/data/workspace/projects/vindkollen/main.py', 'r') as m:
                     main_content = m.read()
                     if f'@app.get("{link_path}"' not in main_content:
                         print(f"File {file}: Broken link found -> {link}")
                         broken_links += 1
print(f"Total broken links: {broken_links}")
