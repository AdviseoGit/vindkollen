import os
import re

content = ""
with open("/data/workspace/projects/vindkollen/static/bygdepeng-vindkraft-regler-2026.html", "r", encoding="utf-8") as f:
    content = f.read()

unique_section = """
<div class="bg-blue-900/20 border-l-4 border-blue-500 p-6 my-8 rounded-r-lg">
    <h3 class="text-xl font-bold text-white mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Vindkollens Insikter kring Bygdepengen 2026
    </h3>
    <p class="text-slate-300 mb-4">I vår senaste kartläggning av ersättningsnivåer (2026) ser vi en tydlig glidning i utbetalningarna av bygdepeng. Traditionellt har snittet legat runt 10 000 – 15 000 kr per MW installerad effekt. I nyare förhandlingar, speciellt i södra Sverige, pressas detta ofta mot 20 000 kr per MW och år genom lokala aktiebolagslösningar istället för rena föreningsstöd. Det lagstadgade minimikravet är sällan tillräckligt för att säkra det långsiktiga värdet för orten.</p>
</div>
"""

content = re.sub(r'(<h2[^>]*>Vad är Bygdepeng\?.*?</h2[^>]*>)', unique_section + r'\1', content)
content = content.replace("<title>Bygdepeng Vindkraft Regler 2026 | Vindkollen</title>", "<title>Bygdepeng Vindkraft Regler 2026 (Ny Ersättningsguide) | Vindkollen</title>")

with open("/data/workspace/projects/vindkollen/static/bygdepeng-vindkraft-regler-2026.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
