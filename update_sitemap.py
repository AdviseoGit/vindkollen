import os

sitemap_path = "/data/workspace/projects/vindkollen/generate_sitemap.py"
with open(sitemap_path, "r", encoding="utf-8") as f:
    content = f.read()

new_page = "    (\"/original-data-rapport-arrende-2026\", \"0.8\", \"monthly\"),\n"
if "/original-data-rapport-arrende-2026" not in content:
    insert_point = content.find("]")
    if insert_point != -1:
        new_content = content[:insert_point] + new_page + content[insert_point:]
        with open(sitemap_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Page added to sitemap generator")

