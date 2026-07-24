# -*- coding: utf-8 -*-
"""Lägger in silo-navigationen (Markägare/Närboende/Kommun) på alla sidor.

Navigationen är handskriven per sida och har därför drivit isär i markup.
Skriptet matchar på länktexten i stället för på klassattributen, behåller varje
sidas befintliga styling och lägger till Närboende-länken där den saknas.

Kör: python scripts/update_nav_silos.py
"""

import glob
import re

SKIP = {"static/index.html", "static/markagare.html", "static/narboende.html",
        "static/kommun.html", "static/juridisk-hjalp-arrendeavtal.html"}

MARKAGARE = re.compile(r'<a\b([^>]*?)>Markägare</a>')
KOMMUNER = re.compile(r'<a\b([^>]*?)>Kommuner</a>')
HREF = re.compile(r'href="[^"]*"')


def set_href(attrs: str, url: str) -> str:
    if HREF.search(attrs):
        return HREF.sub(f'href="{url}"', attrs, count=1)
    return f' href="{url}"' + attrs


def process(path: str) -> bool:
    with open(path, encoding="utf-8") as f:
        src = f.read()
    original = src
    has_narboende = 'href="/narboende"' in src

    def markagare(m):
        attrs = set_href(m.group(1), "/markagare")
        link = f'<a{attrs}>Markägare</a>'
        if has_narboende:
            return link
        # Klona länken till Närboende med samma styling. Ligger den i en
        # listpunkt måste klonen få en egen <li>.
        clone = f'<a{set_href(m.group(1), "/narboende")}>Närboende</a>'
        tail = src[m.end():m.end() + 20]
        if tail.lstrip().startswith("</li>"):
            return link + "</li>\n<li>" + clone
        return link + "\n" + clone

    src = MARKAGARE.sub(markagare, src)
    src = KOMMUNER.sub(lambda m: f'<a{set_href(m.group(1), "/kommun")}>Kommuner</a>', src)

    if src != original:
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        return True
    return False


def main():
    paths = sorted(glob.glob("static/*.html") + glob.glob("static/guider/*.html")
                   + glob.glob("content/**/*.html", recursive=True))
    changed = [p for p in paths if p not in SKIP and process(p)]
    print(f"uppdaterade {len(changed)} sidor:")
    for p in changed:
        print("  ", p)


if __name__ == "__main__":
    main()
