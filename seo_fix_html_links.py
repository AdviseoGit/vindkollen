import os
import re

files = [f for f in os.listdir('/data/workspace/projects/vindkollen/static/') if f.endswith('.html')]

for file in files:
    with open(f"/data/workspace/projects/vindkollen/static/{file}", 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Fix explicit .html and index.html issues
    content = content.replace('href="index.html"', 'href="/"')
    content = content.replace('href="/index.html"', 'href="/"')
    content = content.replace('href="index.html#calculator"', 'href="/#calculator"')
    content = content.replace('href="/index.html#calculator"', 'href="/#calculator"')
    content = content.replace('href="index.html#kalkylator"', 'href="/#kalkylator"')
    content = content.replace('href="faq.html"', 'href="/#faq"')
    content = content.replace('href="guide-ersattning-vindkraft.html"', 'href="/guider/guide-ersattning-vindkraft"')
    content = content.replace('href="kalkylator.html"', 'href="/kalkylator"')
    content = content.replace('href="intaktsdelning-vindkraft.html"', 'href="/intaktsdelning-vindkraft"')
    content = content.replace('href="ersattningsnivaer-region-for-region.html"', 'href="/ersattningsnivaer-region-for-region"')
    content = content.replace('href="om-sajten.html"', 'href="/om-sajten"')
    content = content.replace('href="kommun-dashboard.html"', 'href="/kommun-dashboard"')
    content = content.replace('href="ersattning-for-vindkraft.html"', 'href="/ersattning-for-vindkraft"')
    
    with open(f"/data/workspace/projects/vindkollen/static/{file}", 'w', encoding='utf-8') as f:
        f.write(content)
        
print("Fixed internal html-suffixed links.")
