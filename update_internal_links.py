import os
import re

STATIC_DIR = "/data/workspace/projects/vindkollen/static"
TARGET_URL = "https://vindkoll.se/arrendeavtal-vindkraft"

links_to_add = [
    ('<a href="/arrendeavtal-vindkraft"', 'arrendeavtal-vindkraft')
]

for filename in os.listdir(STATIC_DIR):
    if filename.endswith(".html"):
        filepath = os.path.join(STATIC_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        changed = False
        # Add logic to inject internal links to arrendeavtal-vindkraft.html and nackdelar-med-vindkraft.html in relevant articles
        # This will strengthen internal linking for the Discovered - currently not indexed pages.
