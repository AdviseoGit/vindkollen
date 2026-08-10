import re

main_path = "/data/workspace/projects/vindkollen/main.py"
with open(main_path, "r", encoding="utf-8") as f:
    content = f.read()

route_to_add = """
@app.get("/guider/kommunalt-veto-vindkraft", response_class=HTMLResponse)
async def kommunalt_veto_vindkraft():
    return _serve_static_html("static/guider/kommunalt-veto-vindkraft.html")

"""

target = "@app.get(\"/guider/nackdelar-med-vindkraft"
if "/guider/kommunalt-veto-vindkraft" not in content and target in content:
    # Insert just before the nackdelar route
    content = content.replace(target, route_to_add + target)
    with open(main_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Route /guider/kommunalt-veto-vindkraft added.")
else:
    print("Route already present or target not found.")
