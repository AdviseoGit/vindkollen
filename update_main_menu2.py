with open('/data/workspace/projects/vindkollen/static/markagare.html', 'r') as f:
    content = f.read()

if "arrendera-ut-mark-for-vindkraftverk" not in content:
    content = content.replace(
        '<a class="hover:text-white transition" href="/arrendekalkylator">Arrendekalkylator</a>',
        '<a class="hover:text-white transition" href="/arrendera-ut-mark-for-vindkraftverk">Arrendera ut mark</a>\n        <a class="hover:text-white transition" href="/arrendekalkylator">Arrendekalkylator</a>'
    )
    with open('/data/workspace/projects/vindkollen/static/markagare.html', 'w') as f:
        f.write(content)
