import os
import glob
import re

js_code = """
<script>
    // Mobile Menu Logic
    document.addEventListener('DOMContentLoaded', function() {
        const mobileMenuBtn = document.getElementById('mobile-menu-btn');
        const mobileMenuClose = document.getElementById('mobile-menu-close');
        const mobileMenu = document.getElementById('mobile-menu');

        if (mobileMenuBtn && mobileMenu && mobileMenuClose) {
            mobileMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.remove('hidden');
                document.body.style.overflow = 'hidden';
            });

            mobileMenuClose.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                document.body.style.overflow = 'auto';
            });
        }
    });
</script>
"""

files = glob.glob("/data/workspace/projects/vindkollen/static/**/*.html", recursive=True)

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()
    
    if "Mobile Menu Logic" not in content and "mobile-menu-btn" in content:
        if "</body>" in content:
            new_content = content.replace("</body>", f"{js_code}\n</body>")
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Added JS to {fpath}")

