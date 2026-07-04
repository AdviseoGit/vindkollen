import os
import glob
import re

files = glob.glob("/data/workspace/projects/vindkollen/static/**/*.html", recursive=True)

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if "Denna sajt skapas och drivs helt av AI" not in content and "skapas och drivs helt av AI" not in content:
        # Find footer and add AI transparency text
        footer_end_idx = content.rfind("</footer>")
        if footer_end_idx != -1:
            div_end_idx = content.rfind("</div>", 0, footer_end_idx)
            
            ai_text = """
            <div class="mt-12 pt-8 border-t border-slate-800/60 text-center flex flex-col md:flex-row items-center justify-between text-slate-500 text-sm">
                <p>&copy; 2026 Vindkollen.se. Alla rättigheter förbehållna.</p>
                <p class="mt-4 md:mt-0">Denna sajt skapas och drivs helt av AI &middot; <a href="/om-sajten" class="text-blue-500 hover:text-blue-400">Om sajten</a></p>
            </div>"""
            
            if "Alla rättigheter förbehållna" in content:
                # Replace existing copyright text
                copy_pattern = r'<div class="mt-12 pt-8 border-t border-slate-800/60 text-center flex flex-col md:flex-row items-center justify-between text-slate-500 text-sm">.*?</div>'
                content = re.sub(copy_pattern, ai_text, content, flags=re.DOTALL)
            else:
                content = content[:div_end_idx] + ai_text + "\n" + content[div_end_idx:]
                
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated AI transparency in {filepath}")
