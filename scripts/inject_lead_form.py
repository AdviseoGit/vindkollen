import os
import re

form_html = """
<div class="mt-16 mb-8 bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-3xl mx-auto shadow-xl relative overflow-hidden">
    <div class="absolute -top-24 -right-24 w-48 h-48 bg-blue-600/20 rounded-full blur-3xl pointer-events-none"></div>
    <div class="relative z-10">
        <h3 class="text-2xl font-bold text-white mb-3 flex items-center gap-2">
            <svg class="w-6 h-6 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
            Bevaka vindkraftsnyheter & ersättningar
        </h3>
        <p class="text-slate-300 mb-6">Missa inga viktiga lagändringar eller nya ersättningsnivåer. Få Vindkollens uppdateringar direkt till din inkorg.</p>
        <form class="space-y-4" id="news-form-{{id}}" onsubmit="submitLead(event, '{{id}}')">
            <div class="grid sm:grid-cols-2 gap-4">
                <input class="bg-slate-950 border border-slate-700 px-4 py-3 rounded-xl outline-none focus:border-blue-500 text-white placeholder-slate-500 w-full shadow-inner" id="news-name-{{id}}" placeholder="Förnamn (valfritt)" type="text"/>
                <input class="bg-slate-950 border border-slate-700 px-4 py-3 rounded-xl outline-none focus:border-blue-500 text-white placeholder-slate-500 w-full shadow-inner" id="news-municipality-{{id}}" placeholder="Din kommun (valfritt)" type="text"/>
            </div>
            <div class="flex flex-col sm:flex-row gap-4">
                <input class="flex-1 bg-slate-950 border border-slate-700 px-4 py-3 rounded-xl outline-none focus:border-blue-500 text-white placeholder-slate-500 w-full shadow-inner" id="news-email-{{id}}" placeholder="Din e-postadress" required="" type="email"/>
                <button class="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-xl font-bold transition-colors whitespace-nowrap shadow-lg shadow-blue-900/20" type="submit">Prenumerera</button>
            </div>
            <p class="text-xs text-slate-500 italic mt-3 text-center sm:text-left">Vi delar aldrig din data. Du kan avregistrera dig när som helst.</p>
        </form>
        <div class="hidden mt-4 p-5 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-emerald-400 font-medium flex items-center gap-3" id="news-success-{{id}}">
            <svg class="w-6 h-6 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path></svg>
            Tack! Du är nu prenumerant på Vindkollens uppdateringar.
        </div>
    </div>
</div>
"""

script_js = """
<script>
async function submitLead(event, formId) {
    event.preventDefault();
    const email = document.getElementById('news-email-' + formId).value;
    const name = document.getElementById('news-name-' + formId).value;
    const municipality = document.getElementById('news-municipality-' + formId).value;
    const form = document.getElementById('news-form-' + formId);
    const btn = form.querySelector('button[type="submit"]');
    const originalText = btn.innerText;

    btn.disabled = true;
    btn.innerText = 'Skickar...';
    btn.classList.add('opacity-70', 'cursor-not-allowed');

    try {
        const response = await fetch('/api/lead', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                email: email, 
                name: name,
                municipality: municipality,
                source: window.location.pathname + '_newsletter'
            })
        });
        
        if (response.ok) {
            form.classList.add('hidden');
            document.getElementById('news-success-' + formId).classList.remove('hidden');
        } else {
            alert('Ett fel uppstod. Vänligen försök igen senare.');
            btn.disabled = false;
            btn.innerText = originalText;
            btn.classList.remove('opacity-70', 'cursor-not-allowed');
        }
    } catch (err) {
        console.error('Submit failed', err);
        alert('Ett fel uppstod. Vänligen försök igen senare.');
        btn.disabled = false;
        btn.innerText = originalText;
        btn.classList.remove('opacity-70', 'cursor-not-allowed');
    }
}
</script>
"""

def inject(filepath):
    with open(filepath, 'r') as f:
        content = f.read()

    # Skip if already has a form or form processing script
    if '<form' in content or 'submitLead(' in content:
        print(f"Skipping {filepath} (already has form)")
        return False
        
    if '</article>' in content:
        fid = os.path.basename(filepath).replace('.html', '').replace('-', '_')
        injection = form_html.replace('{{id}}', fid) + script_js
        content = content.replace('</article>', f"{injection}\n</article>")
    elif '</main>' in content:
        fid = os.path.basename(filepath).replace('.html', '').replace('-', '_')
        injection = form_html.replace('{{id}}', fid) + script_js
        content = content.replace('</main>', f"{injection}\n</main>")
    elif '<!-- Footer -->' in content:
        fid = os.path.basename(filepath).replace('.html', '').replace('-', '_')
        injection = form_html.replace('{{id}}', fid) + script_js
        content = content.replace('<!-- Footer -->', f"{injection}\n<!-- Footer -->")
    else:
        print(f"Could not find injection point for {filepath}")
        return False
        
    with open(filepath, 'w') as f:
        f.write(content)
    
    print(f"Injected into {filepath}")
    return True

static_dir = '/data/workspace/projects/vindkollen/static'
for root, _, files in os.walk(static_dir):
    for file in files:
        if file.endswith('.html'):
            inject(os.path.join(root, file))
