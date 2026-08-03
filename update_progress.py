with open('/data/workspace/projects/vindkollen/PROGRESS_LOG.md', 'r') as f:
    content = f.read()

new_entry = "2026-07-29 | SEO | publicerade artikel om arrendera ut mark utifrån GSC trends | organisk trafik | nästa: mät ranking för arrendera ut mark\n"
with open('/data/workspace/projects/vindkollen/PROGRESS_LOG.md', 'w') as f:
    f.write(new_entry + content)
