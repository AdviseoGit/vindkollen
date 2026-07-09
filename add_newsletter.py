with open('/data/workspace/projects/vindkollen/static/index.html', 'r') as f:
    content = f.read()

newsletter_html = """
<!-- Newsletter Section -->
<section id="newsletter" class="py-20 bg-slate-900 border-y border-slate-800">
    <div class="max-w-3xl mx-auto px-6 text-center">
        <h2 class="text-3xl font-bold text-white mb-4">Missa inga viktiga lagändringar</h2>
        <p class="text-slate-400 mb-8">Få uppdateringar om nya ersättningsnivåer, lagkrav och intäktsdelning direkt till din inkorg. 100% oberoende.</p>
        
        <form id="hero-form" class="max-w-md mx-auto space-y-4" onsubmit="event.preventDefault(); submitLead('hero');">
            <div class="flex flex-col sm:flex-row gap-3">
                <input type="email" id="hero-email" placeholder="Din e-postadress" required class="flex-1 bg-slate-950 border border-slate-700 px-4 py-3 rounded-xl outline-none focus:border-blue-500 text-white placeholder-slate-500 shadow-inner">
                <button type="submit" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-bold transition whitespace-nowrap">Prenumerera</button>
            </div>
            <p class="text-xs text-slate-500 italic">Vi delar aldrig din data. Du kan avregistrera dig när som helst.</p>
        </form>
        
        <div id="success-msg" class="hidden mt-6 p-5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 font-medium flex items-center justify-center gap-3">
            <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
            Tack! Du är nu prenumerant på Vindkollens uppdateringar.
        </div>
    </div>
</section>
"""

if 'id="newsletter"' not in content:
    content = content.replace('<!-- Footer / Bottom Lead -->', newsletter_html + '\n<!-- Footer / Bottom Lead -->')
    with open('/data/workspace/projects/vindkollen/static/index.html', 'w') as f:
        f.write(content)
    print("Added newsletter section")
else:
    print("Newsletter section already exists")
