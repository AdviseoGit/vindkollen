import os
import re

files_to_update = {
    '/data/workspace/projects/vindkollen/static/guider/bygdepeng-guide-2026.html': {
        'replace_target': '<h2>Vad är Bygdepeng?</h2>',
        'content': '''<h2>Vad är Bygdepeng?</h2>
<div class="bg-blue-900/20 border border-blue-800/50 rounded-xl p-6 mb-8 mt-4">
    <p class="text-slate-300 font-medium m-0"><strong>Nyhet 2026:</strong> Traditionell bygdepeng har alltid varit frivillig och baserats på överenskommelser mellan vindkraftsbolag och lokal bygd. Men med de nya lagarna 2026 (Intäktsdelning) får vi nu ett lagstadgat golv som garanterar lokal ersättning, vilket innebär att bygdepeng ofta integreras med, eller bygger ovanpå, den statligt tvingande intäktsdelningen.</p>
</div>'''
    }
}

for filepath, update in files_to_update.items():
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    new_content = content.replace(update['replace_target'], update['content'])
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {filepath}")
    else:
        print(f"Target not found or already updated in: {filepath}")
