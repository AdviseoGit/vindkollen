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
        Vindkollens Insikter 2026: Lågfrekvent buller
    </h3>
    <p class="text-slate-300 mb-4">Med de allt större vindkraftverken som byggs 2026 (ofta över 250 meter i totalhöjd) har diskussionen flyttats från enbart dBA-värden till lågfrekvent ljud och skuggkastning. Många kommuner kräver nu längre skyddsavstånd än de generella 1000 meterna, särskilt i områden med spridd bebyggelse. För närboende innebär detta att <a href="/kalkylator" class="text-blue-400 hover:underline">ersättningsnivåerna (ofta baserat på fastighetsvärdets minskning)</a> förhandlas mer aggressivt, då den upplevda störningen kan vara märkbar även under gällande riktvärden för buller.</p>
</div>
"""

content = re.sub(r'(<h2[^>]*>Har du rätt till ersättning vid bullerstörningar\?.*?</h2[^>]*>)', unique_section + r'\1', content)

with open("/data/workspace/projects/vindkollen/static/bullerniva-minimiavstand-vindkraft.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
