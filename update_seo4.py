import re

content = ""
with open("/data/workspace/projects/vindkollen/static/guider/vindkraftsersattning-2026.html", "r", encoding="utf-8") as f:
    content = f.read()

unique_section = """
<div class="bg-blue-900/20 border-l-4 border-blue-500 p-6 my-8 rounded-r-lg">
    <h3 class="text-xl font-bold text-white mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Vindkollens Insikter 2026
    </h3>
    <p class="text-slate-300 mb-4">Lagförslaget om intäktsdelning (SOU 2023:18) som var tänkt att införas 2025 har skjutits upp. Regeringen remitterar för närvarande förslaget om att projektörer ska betala en motsvarighet till fastighetsskatten direkt till kommunerna. För markägare innebär 2026 att frivilliga avtal fortfarande är den enda vägen framåt för att garantera ersättning, varför det är viktigare än någonsin att ha ett vattentätt <a href="/arrendeavtal-vindkraft" class="text-blue-400 hover:underline">arrendeavtal</a>. Vi rekommenderar också att du jämför potentiella intäkter med vår arrendekalkylator.</p>
    <a href="/arrendekalkylator" class="text-blue-400 hover:text-blue-300 font-semibold inline-flex items-center gap-1">Testa vår arrendekalkylator <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" /></svg></a>
</div>
"""

content = re.sub(r'(<h2[^>]*>Lagförslaget: Rätt till intäktsdelning.*?</h2[^>]*>)', unique_section + r'\1', content)

with open("/data/workspace/projects/vindkollen/static/guider/vindkraftsersattning-2026.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
