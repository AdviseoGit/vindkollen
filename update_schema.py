import glob
import re

schema_template = """<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{title}",
  "description": "{desc}",
  "author": {{
    "@type": "Organization",
    "name": "Vindkollen"
  }}
}}
</script>"""

for f in glob.glob('/data/workspace/projects/vindkollen/static/**/*.html', recursive=True):
    with open(f, 'r') as file:
        content = file.read()
    
    if '<script type="application/ld+json">' not in content:
        title_match = re.search(r'<title>(.*?)</title>', content)
        desc_match = re.search(r'<meta[^>]*name=[\"\']description[\"\'][^>]*content=[\"\'](.*?)[\"\']', content)
        
        if title_match and desc_match:
            title = title_match.group(1).replace('"', '\\"')
            desc = desc_match.group(1).replace('"', '\\"')
            schema = schema_template.format(title=title, desc=desc)
            
            content = content.replace('</head>', f'    {schema}\n</head>')
            
            with open(f, 'w') as file:
                file.write(content)
            print(f'Added schema to {f}')
