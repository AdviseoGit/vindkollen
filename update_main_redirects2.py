import re

with open("/data/workspace/projects/vindkollen/main.py", "r") as f:
    content = f.read()

redirect_code_new = """@app.get("/guider", response_class=RedirectResponse)
async def redirect_guider():
    return RedirectResponse(url="/", status_code=301)

@app.get("/guider/", response_class=RedirectResponse)
async def redirect_guider_slash():
    return RedirectResponse(url="/", status_code=301)"""

# we already have the first one. Let's just find and replace it to include both.
if "redirect_guider_slash" not in content:
    content = content.replace("""@app.get("/guider", response_class=RedirectResponse)
async def redirect_guider():
    return RedirectResponse(url="/", status_code=301)""", redirect_code_new)
    
    with open("/data/workspace/projects/vindkollen/main.py", "w") as f:
        f.write(content)
    print("Redirect trailing slash added.")
else:
    print("Already present")
