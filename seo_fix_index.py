import re

def insert_kalkylator():
    filepath = '/data/workspace/projects/vindkollen/static/index.html'
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        card_html = """
            <a href="/kommunersattning-kalkylator.html" class="block group h-full">
                <article class="bg-gray-900 rounded-2xl border border-gray-800 p-6 h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-2xl hover:shadow-blue-500/10 hover:border-blue-500/30 flex flex-col">
                    <div class="flex items-center justify-between mb-4">
                        <span class="text-xs font-semibold tracking-wider text-blue-400 uppercase bg-blue-400/10 px-3 py-1 rounded-full">Kalkylator</span>
                    </div>
                    <h3 class="text-xl font-bold text-white mb-3 group-hover:text-blue-400 transition-colors">Kommunersättning Kalkylator 2026</h3>
                    <p class="text-gray-400 text-sm leading-relaxed mb-6 flex-grow">
                        Räkna ut potentiell kommunersättning för vindkraft enligt de senaste förslagen. Hur mycket skulle fastighetsskatten ge din kommun?
                    </p>
                    <div class="flex items-center text-blue-400 font-medium text-sm mt-auto">
                        Testa verktyget
                        <svg class="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
                    </div>
                </article>
            </a>
"""
        
        # Insert it into the Tools/Verktyg section if it exists, otherwise into Featured Articles.
        if '<!-- TOOLS SECTION -->' in content:
            content = content.replace('<!-- TOOLS SECTION -->', f'<!-- TOOLS SECTION -->\n{card_html}')
        elif '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">' in content:
            content = content.replace('<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">', f'<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">\n{card_html}', 1)


        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Updated index.html")
    except Exception as e:
        print(f"Error processing {filepath}: {e}")

insert_kalkylator()
