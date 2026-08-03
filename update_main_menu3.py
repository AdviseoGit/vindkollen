with open('/data/workspace/projects/vindkollen/static/index.html', 'r') as f:
    content = f.read()

# Try injecting into a block
if "arrendera-ut-mark-for-vindkraftverk" not in content:
    content = content.replace(
        '<a class="hover:text-white transition" href="/markagare">Markägare</a>',
        '<a class="hover:text-white transition" href="/markagare">Markägare</a>\n<a class="hover:text-white transition" href="/arrendera-ut-mark-for-vindkraftverk">Arrendera ut mark</a>'
    )
    with open('/data/workspace/projects/vindkollen/static/index.html', 'w') as f:
        f.write(content)
