with open('/data/workspace/projects/vindkollen/static/index.html', 'r') as f:
    content = f.read()

# Add link to the new guide from index.html (in an appropriate section or just making sure it's accessible)
if "arrendera-ut-mark-for-vindkraftverk" not in content:
    content = content.replace(
        '<a class="hover:text-white transition" href="/kalkylator">Kalkylator</a>',
        '<a class="hover:text-white transition" href="/arrendera-ut-mark-for-vindkraftverk">Arrendera ut mark</a>\n        <a class="hover:text-white transition" href="/kalkylator">Kalkylator</a>'
    )
    with open('/data/workspace/projects/vindkollen/static/index.html', 'w') as f:
        f.write(content)
