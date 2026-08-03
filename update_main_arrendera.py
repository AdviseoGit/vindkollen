import re

with open('/data/workspace/projects/vindkollen/main.py', 'r') as f:
    content = f.read()

route_str = '@app.get("/arrendera-ut-mark-for-vindkraftverk", response_class=HTMLResponse)\n'

if route_str not in content:
    # Insert right before the catch-all
    content = content.replace('@app.get("/{path:path}", response_class=HTMLResponse)', route_str + '@app.get("/{path:path}", response_class=HTMLResponse)')
    with open('/data/workspace/projects/vindkollen/main.py', 'w') as f:
        f.write(content)
    print("Added route")
else:
    print("Route already exists")
