import re
import os

filepath = "/data/workspace/projects/vindkollen/static/arrende-vindkraft-vs-solpark.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Add unique data value section
unique_data_section = """
        <div class="bg-slate-800 rounded-xl p-8 mb-10 border border-slate-700">
            <h3 class="text-2xl font-bold text-white mb-4">Vindkollens Insikter (Juli 2026)</h3>
            <p class="text-slate-300 mb-4">
                Baserat på analyser från Vindkollens kalkylatorer och aktuella arrendeavtal under 2026, ser vi en tydlig trend i valet mellan sol och vind:
            </p>
            <ul class="space-y-3 mb-6">
                <li class="flex items-start">
                    <svg class="h-6 w-6 text-blue-400 mr-2 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span class="text-slate-300"><strong>Högsta möjliga totalintäkt:</strong> Storskalig vindkraft ger generellt högst intäkt per hektar (när man räknar in den yta som faktiskt påverkas), upp till <span class="text-white font-semibold">250 000 - 350 000 kr per verk och år</span>.</span>
                </li>
                <li class="flex items-start">
                    <svg class="h-6 w-6 text-blue-400 mr-2 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span class="text-slate-300"><strong>Stabilast och lägst risk:</strong> Solparker ger en mer förutsägbar, om än något lägre, fast intäkt per hektar ianspråktagen mark (ofta mellan <span class="text-white font-semibold">10 000 - 15 000 kr per hektar/år</span>), och påverkar inte landskapsbilden på samma sätt som vindkraft.</span>
                </li>
                 <li class="flex items-start">
                    <svg class="h-6 w-6 text-blue-400 mr-2 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    <span class="text-slate-300"><strong>Kombinerad markanvändning:</strong> Vindkraft tillåter i stor utsträckning fortsatt jordbruk eller skogsbruk runt verken, vilket ger en <em>dubbel avkastning</em> från marken, medan en solpark ofta ockuperar ytan helt.</span>
                </li>
            </ul>
        </div>
"""

content = content.replace('<h2>Intäkter: Vad ger mest pengar?</h2>', unique_data_section + '\n<h2>Intäkter: Vad ger mest pengar?</h2>')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated content with unique insights")
