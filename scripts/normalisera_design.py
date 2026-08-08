"""
Ger alla sidor samma UI som startsidan.

Sajten har vuxit i omgångar och sidorna har drivit isär: några har ljus
bakgrund på en mörk sajt, några saknar Tailwind helt och är därför oläsbara,
och mobilmenyn dubblerade loggan på samtliga.

Skriptet rör bara *chrome och klasser* — aldrig brödtext, rubriker, länkar
eller schema.org. Det är säkert att köra om.

    python scripts/normalisera_design.py            # visa vad som skulle ändras
    python scripts/normalisera_design.py --skarpt   # skriv
"""

import argparse
import glob
import os
import re
import sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Kanoniskt utseende, hämtat från startsidan.
BODY = 'bg-[#030712] text-slate-100 antialiased overflow-x-hidden'
TAILWIND = '<script src="https://cdn.tailwindcss.com"></script>'
FONTER = (
    '<link href="https://fonts.googleapis.com" rel="preconnect"/>\n'
    '<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>\n'
    '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700'
    '&amp;family=Plus+Jakarta+Sans:wght@700;800&amp;display=swap" rel="stylesheet"/>'
)
STIL = """<style>
        body { font-family: 'Inter', sans-serif; }
        h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif; }
        .hero-gradient { background: radial-gradient(circle at 50% 50%, #111827 0%, #030712 100%); }
    </style>"""
FAVICON = '<link href="/static/favicon.svg" rel="icon" type="image/svg+xml"/>'

# Ljust tema -> mörkt. Ordningen spelar roll: längre klassnamn först, annars
# skriver "text-gray-90" över "text-gray-900".
KLASSKARTA = [
    ("bg-white", "bg-slate-900/40"),
    ("bg-gray-50", "bg-slate-900/40"),
    ("bg-gray-100", "bg-slate-900/60"),
    ("bg-gray-200", "bg-slate-800"),
    ("bg-slate-50", "bg-slate-900/40"),
    ("bg-slate-100", "bg-slate-900/60"),
    ("text-gray-900", "text-white"),
    ("text-gray-800", "text-slate-100"),
    ("text-gray-700", "text-slate-300"),
    ("text-gray-600", "text-slate-400"),
    ("text-gray-500", "text-slate-500"),
    ("text-slate-900", "text-white"),
    ("text-slate-800", "text-slate-100"),
    ("text-slate-700", "text-slate-300"),
    ("text-slate-600", "text-slate-400"),
    ("border-gray-200", "border-slate-800"),
    ("border-gray-300", "border-slate-700"),
    ("border-gray-100", "border-slate-800"),
    ("border-slate-200", "border-slate-800"),
    ("border-slate-300", "border-slate-700"),
    ("divide-gray-200", "divide-slate-800"),
    ("hover:bg-gray-50", "hover:bg-slate-800"),
    ("hover:bg-gray-100", "hover:bg-slate-800"),
]

# Bakgrunder på <body> som ska bli den kanoniska.
KROPPSBAKGRUNDER = re.compile(
    r'\b(?:bg-(?:white|gray-\d{2,3}|slate-\d{2,3}|neutral-\d{2,3}))\b')
KROPPSTEXT = re.compile(r'\btext-(?:gray|slate|neutral)-\d{2,3}\b')


def _har(html: str, nål: str) -> bool:
    return nål.lower() in html.lower()


def fixa_huvud(html: str, logg: list) -> str:
    """Se till att sidan laddar Tailwind, fonter, stil och favicon."""
    if "</head>" not in html:
        return html
    tillägg = []
    if not _har(html, "cdn.tailwindcss.com"):
        tillägg.append(TAILWIND); logg.append("tailwind saknades")
    if not _har(html, "Plus+Jakarta"):
        tillägg.append(FONTER); logg.append("fonter saknades")
    if "font-family: 'Inter'" not in html:
        tillägg.append(STIL); logg.append("stilblock saknades")
    if not _har(html, "favicon.svg"):
        tillägg.append(FAVICON); logg.append("favicon saknades")
    if tillägg:
        html = html.replace("</head>", "\n".join(tillägg) + "\n</head>", 1)
    return html


def fixa_kropp(html: str, logg: list) -> str:
    """Normalisera <body>-klasserna till sajtens mörka tema."""
    m = re.search(r"<body([^>]*)>", html, re.I)
    if not m:
        return html
    attr = m.group(1)
    kl = re.search(r'class="([^"]*)"', attr)
    if not kl:
        ny = f'<body class="{BODY}"{attr}>'
        logg.append("body saknade klasser")
        return html[:m.start()] + ny + html[m.end():]

    klasser = kl.group(1)
    if KROPPSBAKGRUNDER.search(klasser) or KROPPSTEXT.search(klasser):
        if BODY.split()[0] not in klasser:
            logg.append(f"body-tema: {klasser[:40]}")
    # Behåll layoutklasser (flex, min-h-screen …), byt bara tema.
    behåll = [k for k in klasser.split()
              if not KROPPSBAKGRUNDER.match(k) and not KROPPSTEXT.match(k)
              and k not in ("antialiased", "overflow-x-hidden")
              and not k.startswith("bg-[")]
    nya = BODY.split() + behåll
    # Bevara ordningen men ta bort dubbletter.
    sedda, ut = set(), []
    for k in nya:
        if k not in sedda:
            sedda.add(k); ut.append(k)
    nytt_attr = re.sub(r'class="[^"]*"', f'class="{" ".join(ut)}"', attr, count=1)
    return html[:m.start()] + f"<body{nytt_attr}>" + html[m.end():]


def fixa_innehallsklasser(html: str, logg: list) -> str:
    """Mappa ljusa utility-klasser i innehållet till mörka motsvarigheter.

    Att bara vända <body> räcker inte — sidan är då full av vita kort och
    mörkgrå text som blir oläsbar mot den mörka bakgrunden.
    """
    antal = 0
    for ljus, mörk in KLASSKARTA:
        # Bara som helt klassnamn, aldrig som del av ett längre.
        mönster = re.compile(r'(?<![\w-])' + re.escape(ljus) + r'(?![\w-])')
        html, n = mönster.subn(mörk, html)
        antal += n
    if antal:
        logg.append(f"{antal} ljusa klasser mörkades")
    return html


NAV_LANKAR = [
    ("/markagare", "Markägare"),
    ("/narboende", "Närboende"),
    ("/kommun", "Kommun"),
    ("/kalkylator", "Kalkylator"),
    ("/arrendekalkylator", "Arrendekalkylator"),
]

KANONISK_NAV = """<nav class="max-w-7xl mx-auto px-6 py-8 flex justify-between items-center relative z-50 w-full">
<a class="text-2xl font-extrabold tracking-tight text-white" href="/">
<span class="text-blue-500">Vind</span>kollen
</a>
<div class="hidden md:flex gap-7 text-sm font-medium text-slate-400 items-center">
%s
</div>
<button id="mobile-menu-btn" class="md:hidden text-white p-2 hover:bg-slate-800 rounded-lg transition" aria-label="Öppna meny" aria-expanded="false" aria-controls="mobile-menu">
<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
</button>
</nav>
<div id="mobile-menu" class="fixed inset-0 bg-slate-900/95 backdrop-blur-sm z-[60] hidden" role="dialog" aria-modal="true" aria-label="Meny">
<div class="flex flex-col h-full">
<div class="flex justify-between items-center p-6">
<a class="text-2xl font-extrabold tracking-tight text-white" href="/"><span class="text-blue-500">Vind</span>kollen</a>
<button id="mobile-menu-close" class="text-white p-2 hover:bg-slate-800 rounded-lg transition" aria-label="Stäng meny">
<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
</button>
</div>
<div class="flex flex-col gap-2 px-6 py-8">
<a class="text-lg font-medium text-slate-300 hover:text-white py-3 px-4 rounded-lg hover:bg-slate-800 transition" href="/">Hem</a>
%s
</div>
</div>
</div>""" % (
    "\n".join(f'<a class="hover:text-white transition" href="{h}">{t}</a>'
              for h, t in NAV_LANKAR),
    "\n".join('<a class="text-lg font-medium text-slate-300 hover:text-white py-3 px-4 '
              f'rounded-lg hover:bg-slate-800 transition" href="{h}">{t}</a>'
              for h, t in NAV_LANKAR),
)

_NAV = re.compile(r"<nav\b.*?</nav>", re.S | re.I)
_MOBIL = re.compile(r'<div id="mobile-menu".*?</div>\s*</div>\s*</div>', re.S | re.I)


def fixa_nav(html: str, logg: list) -> str:
    """Ge sidan sajtens navigering om den har en egen variant.

    Flera sidor har en helt egen nav utan mobilmeny — på telefon finns då ingen
    väg vidare alls. Den ersätts med den kanoniska, som har både silo-länkarna
    och en fungerande hamburgermeny.
    """
    har_knapp = 'id="mobile-menu-btn"' in html
    overlay = re.search(r'id="mobile-menu" class="([^"]*)"', html)
    # Sajtens meny är en fullskärmsoverlay. Några sidor har i stället en panel
    # som fälls ut under navet — samma funktion, men en annan upplevelse.
    kanonisk_overlay = bool(overlay and "fixed" in overlay.group(1)
                            and "inset-0" in overlay.group(1))
    if har_knapp and kanonisk_overlay:
        return html  # har redan sajtens meny
    if har_knapp and overlay and not kanonisk_overlay:
        logg.append("utfällbar panel byts mot sajtens fullskärmsmeny")

    # Ta första nav:en som inte är en brödsmula. Breadcrumbs är också <nav> och
    # ska bevaras — de bär sidans plats i strukturen.
    träff = next((m for m in _NAV.finditer(html)
                  if "breadcrumb" not in m.group(0).lower()), None)
    if not träff:
        return html

    # Ersätt navet först. På flera sidor ligger menyn *inuti* <nav>, och då
    # försvinner den på köpet. Att städa overlayen först åt upp </nav> och
    # lämnade sidan utan navigering — därför den här ordningen.
    html = html[:träff.start()] + KANONISK_NAV + html[träff.end():]
    logg.append("egen nav ersatt med sajtens")

    # Låg menyn utanför navet finns den kvar som dubblett — ta bort den.
    if html.count('id="mobile-menu"') > 1:
        kanonisk = html.find('id="mobile-menu"')
        rest = html[kanonisk + 10:]
        träffar = list(_MOBIL.finditer(rest))
        if träffar:
            html = html[:kanonisk + 10] + rest[:träffar[0].start()] + rest[träffar[0].end():]
            logg.append("gammal överbliven meny borttagen")
    return html


def fixa_menyfarg(html: str, logg: list) -> str:
    """Mobilmenyn ska ha samma bakgrund överallt."""
    ny = re.sub(r'(id="mobile-menu"[^>]*?)bg-(?:blue|gray|neutral)-\d{2,3}/(\d{2})',
                r'\1bg-slate-900/\2', html)
    if ny != html:
        logg.append("menyfärg till sajtens")
    return ny


_INLINE_MENY = re.compile(
    r"<script>(?:(?!</script>).)*?mobile-menu-btn(?:(?!</script>).)*?</script>",
    re.S | re.I)

# Skript som gör mer än att öppna menyn får inte röras.
_ANNAT = ("fetch(", "function calculate", "submitLead", "submitReport", "gtag(",
          "calcArrende", "calculateArrende", "VKSilo")


def fixa_menyskript(html: str, logg: list) -> str:
    """En implementation av mobilmenyn per sida, inte tre.

    Sidorna hade inline-kopior av menylogiken — ibland två på samma sida plus
    den delade filen — vilket gav dubbla lyssnare så att menyn kunde öppnas och
    stängas i samma klick. Inline-blocken tas bort och den delade filen laddas.
    """
    borttagna = 0

    def kanske_ta_bort(m):
        nonlocal borttagna
        block = m.group(0)
        if any(n in block for n in _ANNAT):
            return block  # blandat innehåll — låt stå
        borttagna += 1
        return ""

    html = _INLINE_MENY.sub(kanske_ta_bort, html)
    if borttagna:
        logg.append(f"{borttagna} inline-menyskript borttagna (dubbla lyssnare)")

    if 'id="mobile-menu-btn"' in html and "js/mobile-menu.js" not in html:
        if "</body>" in html:
            html = html.replace(
                "</body>", '<script src="/static/js/mobile-menu.js"></script>\n</body>', 1)
            logg.append("delad menyfil laddas nu")
    return html


def fixa_mobilmeny(html: str, logg: list) -> str:
    """Lyft mobilmenyn över navigeringen.

    Navet ligger på z-50 och menyn på z-40, så navets logga ritades ovanpå
    overlayen — och eftersom overlayen har en egen logga såg man två.
    """
    if 'id="mobile-menu"' not in html:
        return html
    ny = re.sub(
        r'(id="mobile-menu"[^>]*?)\bz-40\b',
        r'\1z-[60]',
        html,
    )
    if ny != html:
        logg.append("mobilmeny lyft över nav (dubbel logga)")
    return ny


FOOTER = """<footer class="border-t border-slate-800 bg-[#030712] py-12 mt-20">
<div class="max-w-7xl mx-auto px-6 grid md:grid-cols-4 gap-8">
<div>
<a class="text-2xl font-extrabold tracking-tight text-white mb-4 block" href="/"><span class="text-blue-500">Vind</span>kollen</a>
<p class="text-slate-400 text-sm">Oberoende information om vindkraftsersättning, arrende och påverkan för markägare, närboende och kommuner.</p>
</div>
<div>
<h4 class="text-white font-bold mb-4">Din situation</h4>
<ul class="space-y-2 text-sm text-slate-400">
<li><a class="hover:text-blue-400 transition" href="/markagare">Jag äger mark</a></li>
<li><a class="hover:text-blue-400 transition" href="/narboende">Jag bor nära en park</a></li>
<li><a class="hover:text-blue-400 transition" href="/kommun">Jag företräder en kommun</a></li>
</ul>
</div>
<div>
<h4 class="text-white font-bold mb-4">Verktyg</h4>
<ul class="space-y-2 text-sm text-slate-400">
<li><a class="hover:text-blue-400 transition" href="/kalkylator">Ersättningskalkylator</a></li>
<li><a class="hover:text-blue-400 transition" href="/arrendekalkylator">Arrendekalkylator</a></li>
</ul>
</div>
<div>
<h4 class="text-white font-bold mb-4">Om oss</h4>
<ul class="space-y-2 text-sm text-slate-400">
<li><a class="hover:text-blue-400 transition" href="/om-sajten">Om sajten</a></li>
<li><a class="hover:text-blue-400 transition" href="mailto:simon@adviseo.se">Kontakt</a></li>
</ul>
</div>
</div>
<div class="border-t border-slate-800 mt-12 pt-8 text-center text-sm text-slate-500">
<p>Denna sajt skapas och drivs helt av AI &middot; <a href="/om-sajten" class="hover:text-blue-400 transition-colors underline decoration-slate-700 underline-offset-4">Om sajten</a></p>
</div>
</footer>"""

# Typografi för sidor vars innehåll är rena taggar utan klasser. Att skriva om
# varje <p> vore onödigt — elementselektorer räcker och håller texten läsbar.
ARTIKELSTIL = """<style>
        .vk-artikel h1 { font-size: 2.25rem; line-height: 1.15; font-weight: 800; color: #fff; margin-bottom: 1.5rem; }
        .vk-artikel h2 { font-size: 1.6rem; font-weight: 700; color: #fff; margin: 2.5rem 0 1rem; }
        .vk-artikel h3 { font-size: 1.2rem; font-weight: 700; color: #e2e8f0; margin: 1.75rem 0 .5rem; }
        .vk-artikel p  { color: #94a3b8; line-height: 1.75; margin-bottom: 1.15rem; }
        .vk-artikel ul, .vk-artikel ol { color: #94a3b8; line-height: 1.75; margin: 0 0 1.15rem 1.25rem; }
        .vk-artikel li { margin-bottom: .4rem; list-style: disc; }
        .vk-artikel a  { color: #60a5fa; text-decoration: underline; text-underline-offset: 3px; }
        .vk-artikel strong { color: #e2e8f0; }
    </style>"""


def är_fragment(html: str) -> bool:
    """Sidan saknar dokumentstruktur och renderas alltså helt ostylad."""
    huvud = html[:400].lower()
    return "<html" not in huvud and "<!doctype" not in huvud


def sla_in_fragment(html: str, sökväg: str, logg: list) -> str:
    """Ge ett innehållsfragment sajtens sidram."""
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S | re.I)
    rubrik = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else "Vindkollen"
    p = re.search(r"<p[^>]*>(.*?)</p>", html, re.S | re.I)
    ingress = re.sub(r"<[^>]+>", "", p.group(1)).strip()[:155] if p else ""
    slug = os.path.splitext(os.path.basename(sökväg))[0]
    url = f"https://vindkoll.se/blog/{slug}"

    logg.append("fragment utan sidram — hela sidan byggd")
    return f"""<!DOCTYPE html>
<html class="scroll-smooth" lang="sv">
<head>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2ZDTQZXPRC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-2ZDTQZXPRC');
</script>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{rubrik} | Vindkollen</title>
<meta name="description" content="{ingress}"/>
<link href="{url}" rel="canonical"/>
<meta content="index, follow, max-image-preview:large" name="robots"/>
<meta content="#030712" name="theme-color"/>
<meta content="{rubrik}" property="og:title"/>
<meta content="{ingress}" property="og:description"/>
<meta content="article" property="og:type"/>
<meta content="{url}" property="og:url"/>
<meta content="sv_SE" property="og:locale"/>
{FAVICON}
{TAILWIND}
{FONTER}
{STIL}
{ARTIKELSTIL}
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":{rubrik!r},
 "inLanguage":"sv-SE","url":"{url}",
 "publisher":{{"@type":"Organization","name":"Vindkollen","url":"https://vindkoll.se/"}}}}
</script>
</head>
<body class="{BODY}">
{KANONISK_NAV}
<main class="max-w-3xl mx-auto px-6 py-12">
<article class="vk-artikel">
{html.strip()}
</article>
<div class="mt-14 p-6 bg-slate-900 rounded-xl border border-slate-800">
<h3 class="text-xl font-bold text-white mb-4">Läs vidare</h3>
<ul class="space-y-3">
<li><a href="/markagare" class="text-blue-400 hover:text-blue-300 transition">Markägarspåret – arrende, avtal och bedömning av din mark →</a></li>
<li><a href="/narboende" class="text-blue-400 hover:text-blue-300 transition">Närboende – intäktsdelningen från 1 juli 2026 →</a></li>
<li><a href="/kalkylator" class="text-blue-400 hover:text-blue-300 transition">Räkna ut din ersättning →</a></li>
</ul>
</div>
</main>
{FOOTER}
<script src="/static/js/mobile-menu.js"></script>
</body>
</html>
"""


def normalisera(sökväg: str):
    with open(sökväg, encoding="utf-8") as f:
        original = f.read()
    logg = []
    html = original
    if är_fragment(html):
        # Saknar dokumentstruktur helt — bygg hela sidan i stället för att lappa.
        return sla_in_fragment(html, sökväg, logg), logg, True
    html = fixa_huvud(html, logg)
    html = fixa_kropp(html, logg)
    html = fixa_innehallsklasser(html, logg)
    html = fixa_nav(html, logg)
    html = fixa_menyfarg(html, logg)
    html = fixa_mobilmeny(html, logg)
    html = fixa_menyskript(html, logg)
    return html, logg, html != original


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skarpt", action="store_true", help="skriv ändringarna")
    ap.add_argument("--bara", help="kör bara på filer vars namn innehåller detta")
    args = ap.parse_args()

    filer = sorted(glob.glob(os.path.join(ROT, "static/**/*.html"), recursive=True)
                   + glob.glob(os.path.join(ROT, "content/**/*.html"), recursive=True))
    if args.bara:
        filer = [f for f in filer if args.bara in f]

    ändrade = 0
    for f in filer:
        html, logg, skiljer = normalisera(f)
        if not skiljer:
            continue
        ändrade += 1
        print(f"{os.path.relpath(f, ROT)}")
        for rad in logg:
            print(f"    · {rad}")
        if args.skarpt:
            with open(f, "w", encoding="utf-8") as fh:
                fh.write(html)

    läge = "skrev" if args.skarpt else "skulle ändra"
    print(f"\n{läge} {ändrade} av {len(filer)} sidor")
    if not args.skarpt and ändrade:
        print("Kör med --skarpt för att skriva.")


if __name__ == "__main__":
    main()
