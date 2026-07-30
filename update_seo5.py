import re

content = ""
with open("/data/workspace/projects/vindkollen/static/arrende-vindkraft-vs-solpark.html", "r", encoding="utf-8") as f:
    content = f.read()

unique_section = """
<div class="bg-blue-900/20 border-l-4 border-blue-500 p-6 my-8 rounded-r-lg">
    <h3 class="text-xl font-bold text-white mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Vindkollens Insikter 2026: Solpark vs Vindkraft
    </h3>
    <p class="text-slate-300 mb-4">Under 2026 ser vi att solparker i södra Sverige (SE3 och SE4) oftare resulterar i snabbare arrendeavtal, eftersom tillståndsprocesserna är kortare och den folkliga opinionen ofta är mer positiv. Vindkraft ger i regel en högre teoretisk uppsida per hektar mark (tack vare högre effektivitet och energitäthet), men risken för nedlagda projekt i tillståndsfasen är betydligt högre. En ny trend är hybridparker, där markägare tecknar avtal för både sol och vind på samma fastighet för att maximera nyttjandet av nätanslutningen.</p>
</div>
"""

content = re.sub(r'(<h2[^>]*>Sammanfattning: Vad ska du välja\?.*?</h2[^>]*>)', unique_section + r'\1', content)

with open("/data/workspace/projects/vindkollen/static/arrende-vindkraft-vs-solpark.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
