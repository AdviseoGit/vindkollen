import re, glob
form_html = """
    <!-- Lead Magnet Form -->
    <div class="my-12 bg-slate-900 border border-slate-800 rounded-xl p-8 shadow-xl">
        <h3 class="text-2xl font-bold text-white mb-4">Ladda ner vår Original-data-rapport 2026</h3>
        <p class="text-slate-300 mb-6">Få den kompletta bilden av ersättningsnivåer, arrendeavtal och intäktsdelning i Sverige. Baserad på unik data från över 500 beräkningar.</p>
        <form action="/api/newsletter/subscribe" method="POST" class="flex flex-col sm:flex-row gap-3">
            <input type="email" name="email" placeholder="Din e-postadress" required class="flex-1 bg-slate-950 border border-slate-800 text-white rounded-lg px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 placeholder-slate-500">
            <input type="hidden" name="source" value="article_inline">
            <button type="submit" class="bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3 px-6 rounded-lg transition-colors whitespace-nowrap">
                Få rapporten (PDF)
            </button>
        </form>
    </div>
"""

files = [
    "/data/workspace/projects/vindkollen/static/arrende-vindkraft-vs-solpark.html",
    "/data/workspace/projects/vindkollen/static/bygdepeng-vindkraft-regler-2026.html",
    "/data/workspace/projects/vindkollen/static/nio-verkshojder-ersattning.html"
]

for path in files:
    with open(path, "r") as f:
        content = f.read()
    
    if "api/newsletter/subscribe" in content:
        continue
        
    # Inject before the last </div> before <article> ends or something similar.
    # We can inject it right before the </article> tag
    if "</article>" in content:
        content = content.replace("</article>", form_html + "\n</article>")
        with open(path, "w") as f:
            f.write(content)
        print("Injected into", path)
    elif "</main>" in content:
        content = content.replace("</main>", form_html + "\n</main>")
        with open(path, "w") as f:
            f.write(content)
        print("Injected into", path)
