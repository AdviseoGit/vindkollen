import re

with open("/data/workspace/projects/vindkollen/static/index.html", "r") as f:
    html = f.read()

new_card = """                    <div class="bg-slate-900/40 p-8 border border-slate-800 rounded-2xl transform hover:-translate-y-1 transition-transform duration-300">
                        <span class="text-xs font-bold text-red-400 uppercase tracking-widest">Guide 2026</span>
                        <h3 class="text-xl font-semibold text-white mt-3 mb-2">Rätt till inlösen</h3>
                        <p class="text-slate-400 mb-4">Vad innebär förslaget om rätt till inlösen av fastigheter nära vindkraftverk? Vi förklarar vem som omfattas och hur värderingen görs.</p>
                        <a href="/ratt-till-inlosen-fastighet-vindkraft" class="text-blue-400 hover:text-blue-300 font-semibold">Läs guiden &rarr;</a>
                    </div>"""

# Replace the "Vindkraftsersättning 2026" card with our new one since it looks like a good spot to replace/insert
target = """<div class="bg-slate-900/40 p-8 border border-slate-800 rounded-2xl transform hover:-translate-y-1 transition-transform duration-300">
                        <span class="text-xs font-bold text-blue-400 uppercase tracking-widest">Guide 2026</span>
                        <h3 class="text-xl font-semibold text-white mt-3 mb-2">Vindkraftsersättning 2026</h3>
                        <p class="text-slate-400 mb-4">Din kompletta guide till ersättning, rättigheter och trender. Så beräknas ersättningen för närboende och markägare.</p>
                        <a href="/guider/vindkraftsersattning-2026" class="text-blue-400 hover:text-blue-300 font-semibold">Läs guiden &rarr;</a>
                    </div>"""

if target in html:
    html = html.replace(target, new_card + "\n\n                    " + target)
    with open("/data/workspace/projects/vindkollen/static/index.html", "w") as f:
        f.write(html)
    print("Updated index.html successfully.")
else:
    print("Target not found in index.html")
