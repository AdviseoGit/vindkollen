import os
import re

content = ""
with open("/data/workspace/projects/vindkollen/static/nio-verkshojder-ersattning.html", "r", encoding="utf-8") as f:
    content = f.read()

unique_section = """
<div class="bg-blue-900/20 border-l-4 border-blue-500 p-6 my-8 rounded-r-lg">
    <h3 class="text-xl font-bold text-white mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Vindkollens Insikter kring Inlösenrätt
    </h3>
    <p class="text-slate-300 mb-4">Vår analys av rättsfall och praxis visar att "väsentlig olägenhet" enligt inlösenreglerna (9 verkshöjder) ofta missförstås som en garanti. I praktiken krävs ofta en kombination av visuella, akustiska (buller) och skuggbildningsfaktorer för att kravet ska uppfyllas. Med 2026 års högre vindkraftverk (över 250 meter) innebär regeln om 9 verkshöjder i praktiken ofta avstånd över 2,2 km. Många närboende är inte medvetna om hur extremt strikt domstolarna tolkar denna rättighet.</p>
</div>
"""

content = re.sub(r'(<h2[^>]*>Vad innebär Inlösenrätten\?.*?</h2[^>]*>)', unique_section + r'\1', content)

with open("/data/workspace/projects/vindkollen/static/nio-verkshojder-ersattning.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
