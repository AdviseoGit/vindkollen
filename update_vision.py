import re

with open('/data/workspace/projects/vindkollen/SITE_VISION.md', 'r') as f:
    content = f.read()

# Update milestone
content = content.replace(
    '- [☐] Jämförelseverktyg: "Ersättning vs Arrendeavtal" (interaktiv, fångar data)',
    '- [x] Jämförelseverktyg: "Ersättning vs Arrendeavtal" (interaktiv, fångar data)'
)

with open('/data/workspace/projects/vindkollen/SITE_VISION.md', 'w') as f:
    f.write(content)
print("Updated SITE_VISION.md")
