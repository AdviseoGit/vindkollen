import os
import re

main_py_path = "/data/workspace/projects/vindkollen/main.py"
with open(main_py_path, "r", encoding="utf-8") as f:
    content = f.read()

new_route = """@app.get("/original-data-rapport-arrende-2026", response_class=HTMLResponse)
async def original_data_rapport():
    return _serve_static_html("static/original-data-rapport-arrende-2026.html")

"""
if "/original-data-rapport-arrende-2026" not in content:
    insert_point = content.find("@app.get(\"/arrendekalkylator\", response_class=HTMLResponse)")
    if insert_point != -1:
        new_content = content[:insert_point] + new_route + content[insert_point:]
        with open(main_py_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Route added to main.py")
    else:
        print("Could not find insert point in main.py")
else:
    print("Route already exists in main.py")
