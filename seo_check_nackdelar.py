import re

with open("/data/workspace/projects/vindkollen/static/nackdelar-med-vindkraft.html", "r", encoding="utf-8") as f:
    html = f.read()

title_match = re.search(r'<title>(.*?)</title>', html)
desc_match = re.search(r'<meta name="description" content="(.*?)">', html)

if title_match:
    print(f"Title: {title_match.group(1)}")
else:
    print("Title not found")

if desc_match:
    print(f"Description: {desc_match.group(1)}")
else:
    print("Description not found")
