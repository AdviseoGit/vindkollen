import re

with open("/data/workspace/projects/vindkollen/main.py", "r") as f:
    content = f.read()

# Append missing routes before the catch-all
routes_to_add = """
@app.get("/arrende-vindkraft-vs-solpark", response_class=HTMLResponse)
async def arrende_vindkraft_vs_solpark():
    return _serve_static_html("static/arrende-vindkraft-vs-solpark.html")

@app.get("/bygdepeng-vindkraft-regler-2026", response_class=HTMLResponse)
async def bygdepeng_vindkraft_regler_2026():
    return _serve_static_html("static/bygdepeng-vindkraft-regler-2026.html")

"""

target = "# Catch-all for HTML pages"
if routes_to_add.strip() not in content and target in content:
    content = content.replace(target, routes_to_add + "\n" + target)
    with open("/data/workspace/projects/vindkollen/main.py", "w") as f:
        f.write(content)
    print("Routes added.")
else:
    print("Routes already present or target not found.")
