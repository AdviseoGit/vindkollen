import re

with open("/data/workspace/projects/vindkollen/main.py", "r") as f:
    content = f.read()

# Add RedirectResponse to imports
if "RedirectResponse" not in content[:1500]:
    content = content.replace("from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse", "from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse")
    with open("/data/workspace/projects/vindkollen/main.py", "w") as f:
        f.write(content)
    print("Import added.")
else:
    print("Import already present.")
