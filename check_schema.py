import json
import glob
from bs4 import BeautifulSoup
import re

files = glob.glob('/data/workspace/projects/vindkollen/static/**/*.html', recursive=True)
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '<script type="application/ld+json">' not in content:
        print(f"Missing schema.org: {file}")
