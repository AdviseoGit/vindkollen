import os
import re

STATIC_DIR = "/data/workspace/projects/vindkollen/static"
FILES_TO_UPDATE = [
    "kalkylator.html",
    "ersattning-for-vindkraft.html",
    "index.html",
    "sa-far-du-vindkraft-pa-din-mark.html",
    "arrendeavtal-vindkraft.html"
]

def add_link(file_path, link_html):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Try to find a place to inject the link, e.g., in a list or related links section
    if "relaterade guider" in content.lower() or "läs mer" in content.lower():
         # Just a placeholder script, we will use sed/awk or direct replace instead for precision
         pass

