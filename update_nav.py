import os
import glob
import re

nav_html = """<!-- Navigation -->
<nav class="max-w-7xl mx-auto px-6 py-8 flex justify-between items-center relative z-50 w-full">
    <a class="text-2xl font-extrabold tracking-tight text-white" href="/">
        <span class="text-blue-500">Vind</span>kollen
    </a>
    <!-- Desktop Menu -->
    <div class="hidden md:flex gap-8 text-sm font-medium text-slate-400 items-center">
        <a class="hover:text-white transition" href="/kalkylator">Kalkylator</a>
        <a class="hover:text-white transition" href="/arrendekalkylator">Arrendekalkylator</a>
        <a class="hover:text-white transition" href="/ersattning-for-vindkraft">Markägare</a>
        <a class="hover:text-white transition" href="/guider/guide-ersattning-vindkraft">Guider</a>
        <a class="hover:text-white transition" href="/kommun-dashboard">Kommuner</a>
    </div>
    <!-- Mobile Menu Button -->
    <button id="mobile-menu-btn" class="md:hidden text-white p-2 hover:bg-slate-800 rounded-lg transition" aria-label="Meny">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path>
        </svg>
    </button>
</nav>
<!-- Mobile Menu Overlay -->
<div id="mobile-menu" class="fixed inset-0 bg-slate-900/95 backdrop-blur-sm z-40 hidden">
    <div class="flex flex-col h-full">
        <div class="flex justify-between items-center p-6">
            <a class="text-2xl font-extrabold tracking-tight text-white" href="/">
                <span class="text-blue-500">Vind</span>kollen
            </a>
            <button id="mobile-menu-close" class="text-white p-2 hover:bg-slate-800 rounded-lg transition" aria-label="Stäng meny">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        <div class="flex flex-col gap-2 px-6 py-8">
            <a class="text-lg font-medium text-slate-300 hover:text-white py-3 px-4 rounded-lg hover:bg-slate-800 transition" href="/">Hem</a>
            <a class="text-lg font-semibold text-blue-400 hover:text-blue-300 py-3 px-4 rounded-lg hover:bg-slate-800 transition" href="/kalkylator">Kalkylator</a>
            <a class="text-lg font-semibold text-blue-400 hover:text-blue-300 py-3 px-4 rounded-lg hover:bg-slate-800 transition" href="/arrendekalkylator">Arrendekalkylator</a>
            <a class="text-lg font-medium text-slate-300 hover:text-white py-3 px-4 rounded-lg hover:bg-slate-800 transition" href="/ersattning-for-vindkraft">Markägare</a>
            <a class="text-lg font-medium text-slate-300 hover:text-white py-3 px-4 rounded-lg hover:bg-slate-800 transition" href="/guider/guide-ersattning-vindkraft">Guider</a>
            <a class="text-lg font-medium text-slate-300 hover:text-white py-3 px-4 rounded-lg hover:bg-slate-800 transition" href="/kommun-dashboard">Kommuner</a>
        </div>
    </div>
</div>"""

files = glob.glob("/data/workspace/projects/vindkollen/static/**/*.html", recursive=True)

nav_pattern = re.compile(r'<!-- Navigation -->.*?</div>\n</div>', re.DOTALL)
nav_pattern_2 = re.compile(r'<nav.*?class="[^"]*max-w-7xl mx-auto px-6 py-8 flex justify-between items-center relative z-50[^"]*".*?</div>\n</div>', re.DOTALL)
nav_pattern_3 = re.compile(r'<!-- Navigation \(Unified\) -->.*?</div>\n    </div>\n</div>', re.DOTALL)

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = content
    if nav_pattern.search(content):
        new_content = nav_pattern.sub(nav_html, content)
    elif nav_pattern_3.search(content):
        new_content = nav_pattern_3.sub(nav_html, content)
    elif nav_pattern_2.search(content):
        new_content = nav_pattern_2.sub(nav_html, content)
        
    if new_content != content:
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated nav in {fpath}")

