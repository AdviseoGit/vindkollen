import re

with open("/data/workspace/projects/vindkollen/main.py", "r") as f:
    content = f.read()

# Make sure we don't duplicate
redirect_code = """
@app.get("/guider", response_class=RedirectResponse)
async def redirect_guider():
    return RedirectResponse(url="/", status_code=301)
"""

target = "@app.get(\"/{path:path}\", response_class=HTMLResponse)"
if redirect_code.strip() not in content and target in content:
    content = content.replace(target, redirect_code + "\n" + target)
    with open("/data/workspace/projects/vindkollen/main.py", "w") as f:
        f.write(content)
    print("Redirect added.")
else:
    print("Redirect already present or target not found.")
