import os
import glob
import re

nav_html = """<!-- Navigation -->
<nav class="bg-blue-900 text-white shadow-lg sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16 items-center">
            <a href="/" class="text-2xl font-bold tracking-tight flex items-center gap-2">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                Vindkollen
            </a>
            <!-- Desktop Menu -->
            <div class="hidden md:flex space-x-8">
                <a href="/kalkylator" class="hover:text-blue-200 transition font-medium">Kalkylator</a>
                <a href="/arrendekalkylator" class="hover:text-blue-200 transition font-medium">Arrendekalkylator</a>
                <a href="/ersattning-for-vindkraft" class="hover:text-blue-200 transition font-medium">Markägare & Närboende</a>
                <a href="/guider/guide-ersattning-vindkraft" class="hover:text-blue-200 transition font-medium">Guider</a>
                <a href="/kommun-dashboard" class="hover:text-blue-200 transition font-medium">Kommuner</a>
            </div>
            
            <!-- Mobile Menu Button -->
            <div class="md:hidden flex items-center">
                <button id="mobile-menu-btn" class="text-white hover:text-blue-200 focus:outline-none">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
                </button>
            </div>
        </div>
    </div>
</nav>

<!-- Mobile Menu Overlay -->
<div id="mobile-menu" class="fixed inset-0 bg-blue-900/95 backdrop-blur-sm z-40 hidden">
    <div class="flex flex-col h-full">
        <div class="flex justify-between items-center p-6">
            <a class="text-2xl font-bold tracking-tight text-white flex items-center gap-2" href="/">
                <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                Vindkollen
            </a>
            <button id="mobile-menu-close" class="text-white p-2 hover:bg-blue-800 rounded-lg transition" aria-label="Stäng meny">
                <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        <div class="flex flex-col gap-2 px-6 py-8">
            <a class="text-lg font-medium text-blue-100 hover:text-white py-3 px-4 rounded-lg hover:bg-blue-800 transition" href="/">Hem</a>
            <a class="text-lg font-medium text-blue-100 hover:text-white py-3 px-4 rounded-lg hover:bg-blue-800 transition" href="/kalkylator">Kalkylator</a>
            <a class="text-lg font-medium text-blue-100 hover:text-white py-3 px-4 rounded-lg hover:bg-blue-800 transition" href="/arrendekalkylator">Arrendekalkylator</a>
            <a class="text-lg font-medium text-blue-100 hover:text-white py-3 px-4 rounded-lg hover:bg-blue-800 transition" href="/ersattning-for-vindkraft">Markägare & Närboende</a>
            <a class="text-lg font-medium text-blue-100 hover:text-white py-3 px-4 rounded-lg hover:bg-blue-800 transition" href="/guider/guide-ersattning-vindkraft">Guider</a>
            <a class="text-lg font-medium text-blue-100 hover:text-white py-3 px-4 rounded-lg hover:bg-blue-800 transition" href="/kommun-dashboard">Kommuner</a>
        </div>
    </div>
</div>"""

files = glob.glob("/data/workspace/projects/vindkollen/static/**/*.html", recursive=True)

nav_pattern = re.compile(r'<nav class="bg-blue-900 text-white shadow-lg sticky top-0 z-50">.*?</nav>', re.DOTALL)

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if nav_pattern.search(content):
        new_content = nav_pattern.sub(nav_html, content)
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Updated blue nav in {fpath}")

