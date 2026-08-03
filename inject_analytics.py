#!/usr/bin/env python3
"""
Add vk-analytics.js to all HTML pages that have vk-silo.js but not vk-analytics.js yet.
"""
import os
import re

STATIC_DIR = "static"
ANALYTICS_SCRIPT = '<script src="/static/js/vk-analytics.js"></script>'

def inject_analytics(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has vk-analytics.js
    if 'vk-analytics.js' in content:
        print(f"✓ {filepath} - already has vk-analytics.js")
        return False
    
    # Skip if doesn't have vk-silo.js
    if 'vk-silo.js' not in content:
        print(f"⊘ {filepath} - no vk-silo.js, skipping")
        return False
    
    # Inject vk-analytics.js right after vk-silo.js
    pattern = r'(<script src="/static/js/vk-silo\.js"></script>)'
    replacement = r'\1\n<script src="/static/js/vk-analytics.js"></script>'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✓ {filepath} - injected vk-analytics.js")
        return True
    else:
        print(f"✗ {filepath} - pattern not found")
        return False

def main():
    count = 0
    for filename in os.listdir(STATIC_DIR):
        if filename.endswith('.html'):
            filepath = os.path.join(STATIC_DIR, filename)
            if inject_analytics(filepath):
                count += 1
    
    print(f"\nTotal pages updated: {count}")

if __name__ == '__main__':
    main()
