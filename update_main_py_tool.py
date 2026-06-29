import re

with open('/data/workspace/projects/vindkollen/main.py', 'r') as f:
    content = f.read()

# Add route if missing
if '"/jamforelse-ersattning-vs-arrende"' not in content:
    route_code = """
@app.get("/jamforelse-ersattning-vs-arrende", response_class=HTMLResponse)
async def jamforelse_tool():
    return _serve_static_html("static/jamforelse-ersattning-vs-arrende.html")
"""
    
    # Insert after arrendekalkylator
    content = content.replace(
        'async def arrendekalkylator():\n    return _serve_static_html("static/arrendekalkylator.html")',
        'async def arrendekalkylator():\n    return _serve_static_html("static/arrendekalkylator.html")\n' + route_code
    )

    with open('/data/workspace/projects/vindkollen/main.py', 'w') as f:
        f.write(content)
    print("Added route to main.py")
else:
    print("Route already exists in main.py")
