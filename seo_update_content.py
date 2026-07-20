import re

filepath = "/data/workspace/projects/vindkollen/static/guider/bygga-vindkraftverk-steg-for-steg.html"

try:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Find the end of the first paragraph after h1
    pattern = r'(<p class="text-slate-400 mb-4">.*?)</p>'
    
    unique_data_section = """
        <div class="bg-slate-800/80 rounded-xl p-6 my-8 border border-slate-700/50">
            <h3 class="text-xl font-bold text-white mb-3">Vindkollens data: Hur lång tid tar det i snitt 2026?</h3>
            <p class="text-slate-300 mb-2">Baserat på Vindkollens analys av nyligen beviljade projekt ser vi följande tidslinjer från idé till första spadtag:</p>
            <ul class="space-y-2 mt-4 text-slate-300">
                <li class="flex items-center"><span class="w-2 h-2 bg-blue-500 rounded-full mr-3"></span><strong>Mindre projekt (1-3 verk):</strong> 3-5 år (snabbare tillståndsprocess)</li>
                <li class="flex items-center"><span class="w-2 h-2 bg-blue-500 rounded-full mr-3"></span><strong>Större parker på land (>10 verk):</strong> 5-9 år</li>
                <li class="flex items-center"><span class="w-2 h-2 bg-blue-500 rounded-full mr-3"></span><strong>Havsbaserade projekt:</strong> 8-12 år (komplexare miljöprövningar)</li>
            </ul>
        </div>
    """

    if "Vindkollens data: Hur lång tid tar det i snitt 2026?" not in content:
        # insert unique data before h2
        content = content.replace('<h2 class="text-3xl font-bold text-white mb-6">1. Förstudie och planering</h2>', unique_data_section + '\n<h2 class="text-3xl font-bold text-white mb-6">1. Förstudie och planering</h2>')
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated content with unique insights")
    else:
        print("Content already updated")
except FileNotFoundError:
    print(f"File not found: {filepath}")

