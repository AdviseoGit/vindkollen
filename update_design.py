import os
import glob
import re

def update_forms(directory):
    files = glob.glob(f"{directory}/**/*.html", recursive=True)
    
    # Hero form style regex patterns to standardise against
    # Base styling: bg-slate-950 border border-slate-700 px-4 py-3 rounded-xl outline-none focus:border-blue-500 text-white placeholder-slate-500 shadow-inner
    
    replacements = 0
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        original_content = content
        
        # Replace various input styles with the standardized one
        # Specifically targeting bg-slate-900 inputs that don't match our new standard
        content = re.sub(
            r'class="[^"]*bg-slate-900[^"]*px-4 py-3 rounded-lg[^"]*text-white[^"]*"',
            r'class="w-full bg-slate-950 border border-slate-700 px-4 py-3 rounded-xl outline-none focus:border-blue-500 text-white placeholder-slate-500 shadow-inner"',
            content
        )
        
        # Update buttons from rounded-lg to rounded-xl and standardize colors
        content = re.sub(
            r'class="[^"]*bg-slate-700 hover:bg-slate-600 text-white py-3 rounded-lg[^"]*"',
            r'class="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 rounded-xl font-bold transition shadow-lg"',
            content
        )
        
        if content != original_content:
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            replacements += 1
            print(f"Updated forms in: {file}")
            
    print(f"Total files updated: {replacements}")

if __name__ == "__main__":
    update_forms("/data/workspace/projects/vindkollen/static")
