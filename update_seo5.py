import os
import re

content = ""
with open("/data/workspace/projects/vindkollen/static/bullerniva-minimiavstand-vindkraft.html", "r", encoding="utf-8") as f:
    content = f.read()

unique_section = """
<div class="bg-blue-900/20 border-l-4 border-blue-500 p-6 my-8 rounded-r-lg">
    <h3 class="text-xl font-bold text-white mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Vindkollens Insikter kring Buller & Avstånd
    </h3>
    <p class="text-slate-300 mb-4">Vår kalkylatordata (över 500 beräkningar) visar att de flesta närboende i Sverige bor mellan 800 och 1200 meter från nyetablerade vindparker. Detta innebär att de befinner sig precis vid gränsen för Naturvårdsverkets riktvärde på 40 dBA. En viktig detalj som många missar är att lågfrekvent buller mäts annorlunda och kan upplevas störande även om totalnivån ligger under gränsvärdet inomhus, speciellt vid nattetid.</p>
</div>
"""

content = re.sub(r'(<h2[^>]*>Hur Mäts Buller från Vindkraftverk\?.*?</h2[^>]*>)', unique_section + r'\1', content)
content = content.replace("<title>Bullernivå och Minimiavstånd för Vindkraftverk | Vindkollen</title>", "<title>Buller & Minimiavstånd för Vindkraftverk (Regler 2026) | Vindkollen</title>")
content = content.replace("<meta name=\"description\" content=\"En utförlig guide", "<meta name=\"description\" content=\"Guide till bullernivåer och minimiavstånd för vindkraft 2026. Läs om gränsvärden (40 dBA), rättigheter som närboende, och ny insiktsdata från Vindkollen.")

with open("/data/workspace/projects/vindkollen/static/bullerniva-minimiavstand-vindkraft.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
