import os
import re
import glob

# Målfiler att injicera länkarna i
TARGETS = [
    "static/guider/guide-ersattning-vindkraft.html",
    "static/ersattning-for-vindkraft.html",
    "static/sa-far-du-vindkraft-pa-din-mark.html",
    "static/skatt-vindkraftersattning.html",
    "static/paverkar-vindkraft-fastighetsvarde.html",
    "static/kalkylator.html",
    "static/arrendekalkylator.html"
]

LINKS = [
    {"url": "/bullerniva-minimiavstand-vindkraft", "anchor": "bullernivå och minimiavstånd"},
    {"url": "/avveckling-och-atervinning-vindkraft", "anchor": "avveckling och återvinning av vindkraft"},
    {"url": "/arrendeavtal-vindkraft", "anchor": "arrendeavtal för vindkraft"},
    {"url": "/bygdepeng-vindkraft-regler-2026", "anchor": "bygdepeng regler 2026"}
]

def add_links_to_files():
    for target in TARGETS:
        try:
            with open(target, 'r') as f:
                content = f.read()
            
            modified = False
            # Leta efter platser att lägga till relaterade guider om det inte redan finns
            if '<div class="mt-12 p-6 bg-slate-900 rounded-xl border border-slate-800">' not in content and 'Relaterade guider' not in content:
                
                # Lägg till i botten av content men innan footer
                insertion_point = content.find('</main>')
                if insertion_point != -1:
                    links_html = """
                    <div class="mt-12 p-6 bg-slate-900 rounded-xl border border-slate-800">
                        <h3 class="text-xl font-bold text-white mb-4">Relaterade guider</h3>
                        <ul class="space-y-3">
                            <li><a href="/bullerniva-minimiavstand-vindkraft" class="text-blue-400 hover:text-blue-300 transition">Läs vår kompletta guide om bullernivå och minimiavstånd för vindkraft →</a></li>
                            <li><a href="/avveckling-och-atervinning-vindkraft" class="text-blue-400 hover:text-blue-300 transition">Så fungerar avveckling och återvinning av vindkraft (2026) →</a></li>
                            <li><a href="/arrendeavtal-vindkraft" class="text-blue-400 hover:text-blue-300 transition">Detaljerad genomgång av arrendeavtal för vindkraft →</a></li>
                            <li><a href="/bygdepeng-vindkraft-regler-2026" class="text-blue-400 hover:text-blue-300 transition">Nya regler för bygdepeng vindkraft 2026 →</a></li>
                        </ul>
                    </div>
                    """
                    content = content[:insertion_point] + links_html + content[insertion_point:]
                    modified = True
            
            if modified:
                with open(target, 'w') as f:
                    f.write(content)
                print(f"Updated {target} with related links")
        except Exception as e:
            print(f"Error processing {target}: {e}")

if __name__ == "__main__":
    add_links_to_files()
