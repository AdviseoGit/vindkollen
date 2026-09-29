import re

with open('/data/workspace/projects/vindkollen/static/markagare.html', 'r') as f:
    html = f.read()

new_block = """<div class="mt-8 bg-slate-800/50 p-6 rounded-xl border border-slate-700">
<h3 class="text-xl font-bold text-white mb-2">Vad är nästa steg?</h3>
<p class="text-slate-300 text-sm mb-4">Om marken ser lovande ut väntar en process med mätningar, tillstånd och avtal. Se vår guide om att bygga vindkraftverk steg för steg för att förstå vad som krävs.</p>
<a href="/guider/bygga-vindkraftverk-steg-for-steg" class="text-blue-400 hover:underline font-semibold">Läs guiden: Bygga vindkraftverk steg för steg →</a>
</div>

<div class="mt-8 bg-slate-800/50 p-6 rounded-xl border border-slate-700">"""

html = html.replace('<div class="mt-8 bg-slate-800/50 p-6 rounded-xl border border-slate-700">', new_block, 1)

with open('/data/workspace/projects/vindkollen/static/markagare.html', 'w') as f:
    f.write(html)
