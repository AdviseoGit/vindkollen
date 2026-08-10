import json

file_path = "/data/workspace/projects/vindkollen/static/guider/kommunalt-veto-vindkraft.html"
with open(file_path, "r", encoding="utf-8") as f:
    html = f.read()
    
# check if schema is there
if '<script type="application/ld+json">' in html:
    print("Schema found.")
else:
    print("Schema missing.")
