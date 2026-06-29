import re

with open('/data/workspace/projects/vindkollen/generate_sitemap.py', 'r') as f:
    content = f.read()

# Add to STATIC_PAGES if missing
if '"/jamforelse-ersattning-vs-arrende"' not in content:
    content = content.replace(
        '("/arrendekalkylator", "0.9", "weekly"),',
        '("/arrendekalkylator", "0.9", "weekly"),\n    ("/jamforelse-ersattning-vs-arrende", "0.9", "weekly"),'
    )

    with open('/data/workspace/projects/vindkollen/generate_sitemap.py', 'w') as f:
        f.write(content)
    print("Added to generate_sitemap.py")
else:
    print("Already in generate_sitemap.py")
