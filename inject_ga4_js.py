import os
import glob

static_dir = "/data/workspace/projects/vindkollen/static"
html_files = glob.glob(f"{static_dir}/**/*.html", recursive=True)

script_tag = '<script src="/static/ga4_events.js"></script>'

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if script_tag not in content:
        # Insert before closing </body>
        content = content.replace("</body>", f"    {script_tag}\n</body>")
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Injected into {file_path}")
    else:
        print(f"Already injected in {file_path}")
