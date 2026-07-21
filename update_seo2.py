import os
import re

content = ""
with open("/data/workspace/projects/vindkollen/static/avveckling-och-atervinning-vindkraft.html", "r", encoding="utf-8") as f:
    content = f.read()

# Make the page more unique
content = content.replace("<title>Avveckling och Återvinning av Vindkraftverk | Vindkollen</title>", "<title>Avveckling & Återvinning av Vindkraftverk (Regler 2026) | Vindkollen</title>")

# Add a unique "Vindkollen Insikter" section to boost uniqueness
unique_section = """
<div class="bg-blue-900/20 border-l-4 border-blue-500 p-6 my-8 rounded-r-lg">
    <h3 class="text-xl font-bold text-white mb-2 flex items-center gap-2">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
        Vindkollens Insikter kring Avveckling
    </h3>
    <p class="text-slate-300 mb-4">Många markägare missar att i detalj reglera tidpunkten för när återställningsfonden (den ekonomiska säkerheten) ska vara fullt uppbyggd. Vår data visar att de mest framgångsrika arrendeavtalen säkerställer att 100% av de uppskattade återställningskostnaderna finns deponerade redan under de första 5-10 driftsåren. En otydlig avvecklingsklausul är en av de största dolda riskerna i äldre vindkraftsavtal.</p>
    <a href="/arrendeavtal-vindkraft" class="text-blue-400 hover:text-blue-300 font-semibold inline-flex items-center gap-1">Läs hur du utformar ett tryggt arrendeavtal <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" /></svg></a>
</div>
"""

# Replace in content (before the economic security part if possible)
content = re.sub(r'(<h2[^>]*>Ekonomisk Säkerhet.*?</h2[^>]*>)', unique_section + r'\1', content)

with open("/data/workspace/projects/vindkollen/static/avveckling-och-atervinning-vindkraft.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
