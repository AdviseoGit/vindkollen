import os
import glob
import re

files = glob.glob("/data/workspace/projects/vindkollen/static/**/*.html", recursive=True)

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Link from arrendekalkylator to the report
    if "arrendekalkylator.html" in fpath:
        link_html = """
        <div class="mt-8 p-6 bg-blue-900/20 border border-blue-500/30 rounded-2xl">
            <h3 class="text-xl font-bold text-white mb-2">Nyfiken på snittnivåer?</h3>
            <p class="text-slate-300 mb-4">Läs vår nya datarapport om arrendenivåer och branschsnitt i Sverige 2026 baserad på egna data.</p>
            <a href="/original-data-rapport-arrende-2026" class="text-blue-400 hover:text-blue-300 font-medium inline-flex items-center gap-1 transition-colors">
                Läs rapporten <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </a>
        </div>
        """
        if "/original-data-rapport-arrende-2026" not in content:
            insert_point = content.find("</form>")
            if insert_point != -1:
                insert_point += 7
                new_content = content[:insert_point] + link_html + content[insert_point:]
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"Added internal link to {fpath}")

