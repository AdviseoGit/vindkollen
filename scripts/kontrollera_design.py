"""
Kontrollerar att alla sidor delar sajtens UI.

Kompletterar normalisera_design.py: den skriver, den här läser och gnäller.
Körs efter varje designändring så att sidorna inte driver isär igen.

    python scripts/kontrollera_design.py

Avslutar med felkod 1 om någon sida avviker, så den kan användas i ett
byggsteg eller en pre-commit-hook.
"""

import glob
import os
import re
import sys
from html.parser import HTMLParser

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOMMA = ("br", "img", "input", "meta", "link", "hr", "path", "source", "circle",
         "polygon", "rect", "use", "area", "col", "embed", "track", "wbr")


class Balans(HTMLParser):
    """Enkel kontroll av att taggarna går ihop."""

    def __init__(self):
        super().__init__()
        self.stack, self.fel = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in TOMMA:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in TOMMA:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        elif tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
        else:
            self.fel.append(f"oväntad </{tag}>")

    def oslutna(self):
        return [t for t in self.stack if t not in ("html", "body", "head")]


def granska(sökväg: str):
    with open(sökväg, encoding="utf-8") as f:
        html = f.read()
    fel = []

    if "#030712" not in html:
        fel.append("fel bakgrund")
    if "cdn.tailwindcss.com" not in html:
        fel.append("saknar tailwind (sidan blir ostylad)")
    if "Plus+Jakarta" not in html:
        fel.append("saknar rubriktypsnitt")
    if "<footer" not in html:
        fel.append("saknar footer")
    if 'id="mobile-menu-btn"' not in html:
        fel.append("saknar hamburgare")
    if "js/mobile-menu.js" not in html:
        fel.append("laddar inte menyskriptet")

    antal = html.count('id="mobile-menu"')
    if antal != 1:
        fel.append(f"{antal} menyelement (ska vara 1)")

    overlay = re.search(r'id="mobile-menu" class="([^"]*)"', html)
    if not overlay or "fixed" not in overlay.group(1) or "inset-0" not in overlay.group(1):
        fel.append("menyn är inte sajtens fullskärmsoverlay")

    # Navet får aldrig ligga över menyn — då syns loggan dubbelt.
    nav_z = re.search(r"<nav[^>]*\bz-\[?(\d+)", html)
    ov_z = re.search(r'id="mobile-menu"[^>]*\bz-\[?(\d+)', html)
    if not ov_z:
        fel.append("menyn saknar z-index")
    elif nav_z and int(ov_z.group(1)) <= int(nav_z.group(1)):
        fel.append(f"nav z-{nav_z.group(1)} ligger över meny z-{ov_z.group(1)} (dubbel logga)")

    # Inline-menylogik utöver den delade filen ger dubbla lyssnare.
    inline = re.findall(r"<script>(?:(?!</script>).)*?mobile-menu-btn", html, re.S)
    if inline:
        fel.append(f"{len(inline)} inline-menyskript kvar (dubbla lyssnare)")

    b = Balans()
    b.feed(html)
    if b.oslutna() or b.fel:
        fel.append(f"struktur: oslutna {b.oslutna()[:3]} {b.fel[:2]}")

    return fel


def main():
    filer = sorted(glob.glob(os.path.join(ROT, "static/**/*.html"), recursive=True)
                   + glob.glob(os.path.join(ROT, "content/**/*.html"), recursive=True))
    brister = 0
    for f in filer:
        fel = granska(f)
        if fel:
            brister += 1
            print(f"{os.path.relpath(f, ROT)}")
            for x in fel:
                print(f"    · {x}")

    print(f"\n{len(filer) - brister} av {len(filer)} sidor delar sajtens UI")
    if brister:
        print("Kör: python scripts/normalisera_design.py --skarpt")
        sys.exit(1)


if __name__ == "__main__":
    main()
