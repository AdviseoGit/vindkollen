"""
Bygger Vindkollens fyra silo-sidor från en gemensam mall.

Sidorna delar allt utom innehållet: samma head, nav, footer, formulärmotor
(/static/js/vk-silo.js) och samma CTA-hierarki. Att hålla dem i en mall är enda
sättet att slippa den drift som redan finns mellan de handskrivna sidorna.

Kör: python scripts/build_silo_pages.py
"""

import os

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

COUNTIES = [
    "Blekinge", "Dalarna", "Gotland", "Gävleborg", "Halland", "Jämtland",
    "Jönköping", "Kalmar", "Kronoberg", "Norrbotten", "Skåne", "Stockholm",
    "Södermanland", "Uppsala", "Värmland", "Västerbotten", "Västernorrland",
    "Västmanland", "Västra Götaland", "Örebro", "Östergötland",
]

COUNTY_OPTIONS = "\n".join(
    f'<option value="{c}">{c}</option>' for c in COUNTIES
)

FIELD = ("w-full bg-slate-950 border border-slate-700 px-4 py-3 rounded-xl outline-none "
         "focus:border-blue-500 text-white placeholder-slate-500")
LABEL = "block text-sm font-semibold text-slate-300 mb-2"
CHECK = "mt-1 h-5 w-5 rounded border-slate-600 bg-slate-950 text-blue-600 focus:ring-blue-500"


def county_select(name="county", required=True):
    return f"""<select class="{FIELD}" name="{name}"{' required' if required else ''}>
<option value="">Välj län…</option>
{COUNTY_OPTIONS}
</select>"""


def nav(active):
    """Silo-medveten navigation. Aktiv silo markeras så att besökaren alltid
    vet vilket spår hen befinner sig i."""
    items = [
        ("/markagare", "Markägare", "markagare"),
        ("/narboende", "Närboende", "narboende"),
        ("/kommun", "Kommun", "kommun"),
        ("/kalkylator", "Kalkylator", "kalkylator"),
        ("/arrendekalkylator", "Arrendekalkylator", "arrendekalkylator"),
    ]
    desktop = "\n".join(
        f'<a class="{"text-white font-semibold" if key == active else "hover:text-white"} transition" href="{href}">{label}</a>'
        for href, label, key in items
    )
    mobile = "\n".join(
        f'<a class="text-lg {"text-blue-400 font-semibold" if key == active else "text-slate-300"} '
        f'hover:text-white py-3 px-4 rounded-lg hover:bg-slate-800 transition" href="{href}">{label}</a>'
        for href, label, key in items
    )
    return f"""<nav class="max-w-7xl mx-auto px-6 py-8 flex justify-between items-center relative z-50 w-full">
<a class="text-2xl font-extrabold tracking-tight text-white" href="/">
<span class="text-blue-500">Vind</span>kollen
</a>
<div class="hidden md:flex gap-7 text-sm font-medium text-slate-400 items-center">
{desktop}
</div>
<button id="mobile-menu-btn" class="md:hidden text-white p-2 hover:bg-slate-800 rounded-lg transition" aria-label="Meny">
<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
</button>
</nav>
<div id="mobile-menu" class="fixed inset-0 bg-slate-900/95 backdrop-blur-sm z-40 hidden">
<div class="flex flex-col h-full">
<div class="flex justify-between items-center p-6">
<a class="text-2xl font-extrabold tracking-tight text-white" href="/"><span class="text-blue-500">Vind</span>kollen</a>
<button id="mobile-menu-close" class="text-white p-2 hover:bg-slate-800 rounded-lg transition" aria-label="Stäng meny">
<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
</button>
</div>
<div class="flex flex-col gap-2 px-6 py-8">
<a class="text-lg text-slate-300 hover:text-white py-3 px-4 rounded-lg hover:bg-slate-800 transition" href="/">Hem</a>
{mobile}
</div>
</div>
</div>"""


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
<li><a class="hover:text-blue-400 transition" href="/juridisk-hjalp-arrendeavtal">Jag behöver juridisk hjälp</a></li>
</ul>
</div>
<div>
<h4 class="text-white font-bold mb-4">Verktyg</h4>
<ul class="space-y-2 text-sm text-slate-400">
<li><a class="hover:text-blue-400 transition" href="/kalkylator">Ersättningskalkylator</a></li>
<li><a class="hover:text-blue-400 transition" href="/arrendekalkylator">Arrendekalkylator</a></li>
<li><a class="hover:text-blue-400 transition" href="/jamforelse-ersattning-vs-arrende">Jämför ersättning vs arrende</a></li>
<li><a class="hover:text-blue-400 transition" href="/kommun-dashboard">Kommun-dashboard</a></li>
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
<div class="max-w-7xl mx-auto px-6 mt-12 pt-8 border-t border-slate-800 text-sm text-slate-500 text-center">
&copy; 2026 Vindkollen.se. All information i våra kalkyler och guider är uppskattningar baserade på tillgänglig branschdata.
</div>
<div class="border-t border-slate-800 mt-12 pt-8 text-center text-sm text-slate-500">
<p>Denna sajt skapas och drivs helt av AI &middot; <a href="/om-sajten" class="hover:text-blue-400 transition-colors underline decoration-slate-700 underline-offset-4">Om sajten</a></p>
</div>
</footer>"""


def faq_schema(url, name, faqs):
    entities = ",\n".join(
        '{"@type":"Question","name":%s,"acceptedAnswer":{"@type":"Answer","text":%s}}'
        % (_json(q), _json(a))
        for q, a in faqs
    )
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@graph": [
    {{
      "@type": "WebPage",
      "@id": "{url}#webpage",
      "url": "{url}",
      "name": {_json(name)},
      "inLanguage": "sv-SE",
      "isPartOf": {{ "@id": "https://vindkoll.se/#website" }}
    }},
    {{
      "@type": "FAQPage",
      "mainEntity": [
{entities}
      ]
    }}
  ]
}}
</script>"""


def _json(s):
    import json
    return json.dumps(s, ensure_ascii=False)


def faq_block(faqs):
    items = "\n".join(
        f"""<details class="group bg-slate-900/40 border border-slate-800 rounded-xl p-5">
<summary class="cursor-pointer font-semibold text-white list-none flex justify-between gap-4">{q}
<span class="text-blue-400 group-open:rotate-45 transition">+</span></summary>
<p class="text-slate-400 mt-3 leading-relaxed">{a}</p>
</details>"""
        for q, a in faqs
    )
    return f"""<section class="max-w-4xl mx-auto px-6 py-16">
<h2 class="text-3xl font-bold text-white mb-8">Vanliga frågor</h2>
<div class="space-y-3">
{items}
</div>
</section>"""


def page(*, filename, title, description, path, nav_active, hero, body, faqs, faq_name):
    url = f"https://vindkoll.se{path}"
    html = f"""<!DOCTYPE html>
<html class="scroll-smooth" lang="sv">
<head>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-2ZDTQZXPRC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', 'G-2ZDTQZXPRC');
</script>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title}</title>
<meta name="description" content="{description}"/>
<link href="{url}" rel="canonical"/>
<meta content="index, follow, max-image-preview:large" name="robots"/>
<meta content="#030712" name="theme-color"/>
<meta content="{title}" property="og:title"/>
<meta content="{description}" property="og:description"/>
<meta content="website" property="og:type"/>
<meta content="{url}" property="og:url"/>
<meta content="sv_SE" property="og:locale"/>
<meta content="summary_large_image" name="twitter:card"/>
<link href="/static/favicon.svg" rel="icon" type="image/svg+xml"/>
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com" rel="preconnect"/>
<link crossorigin="" href="https://fonts.gstatic.com" rel="preconnect"/>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&amp;family=Plus+Jakarta+Sans:wght@700;800&amp;display=swap" rel="stylesheet"/>
<style>
    body {{ font-family: 'Inter', sans-serif; }}
    h1, h2, h3 {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
    .hero-gradient {{ background: radial-gradient(circle at 50% 0%, #111827 0%, #030712 100%); }}
    details summary::-webkit-details-marker {{ display: none; }}
</style>
{faq_schema(url, faq_name, faqs)}
</head>
<body class="bg-[#030712] text-slate-100 antialiased overflow-x-hidden">
{nav(nav_active)}
{hero}
{body}
{faq_block(faqs)}
{FOOTER}
<script>
document.getElementById('mobile-menu-btn')?.addEventListener('click', () => {{
    document.getElementById('mobile-menu')?.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}});
document.getElementById('mobile-menu-close')?.addEventListener('click', () => {{
    document.getElementById('mobile-menu')?.classList.add('hidden');
    document.body.style.overflow = '';
}});
</script>
<script src="/static/js/vk-silo.js"></script>
</body>
</html>
"""
    out = os.path.join(OUT_DIR, filename)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"skrev {out}")


def hero(*, badge, h1_pre, h1_accent, lead, primary, secondary=None, trust=None):
    secondary_html = ""
    if secondary:
        secondary_html = (
            f'<a class="inline-flex items-center justify-center bg-slate-900/60 hover:bg-slate-800 '
            f'text-slate-200 border border-slate-700 px-8 py-4 rounded-xl font-semibold transition" '
            f'href="{secondary[1]}">{secondary[0]}</a>'
        )
    trust_html = ""
    if trust:
        items = "\n".join(
            f'<span class="flex items-center gap-1"><svg class="w-4 h-4 text-emerald-500" fill="currentColor" '
            f'viewBox="0 0 20 20"><path clip-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 '
            f'00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" fill-rule="evenodd">'
            f'</path></svg> {t}</span>' for t in trust
        )
        trust_html = f'<div class="mt-6 flex flex-wrap items-center gap-4 text-xs text-slate-500">{items}</div>'
    return f"""<header class="relative pt-12 pb-20 hero-gradient">
<div class="max-w-5xl mx-auto px-6">
<div class="inline-flex items-center px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold mb-6 uppercase tracking-wider">{badge}</div>
<h1 class="text-4xl md:text-6xl font-extrabold tracking-tight mb-6 leading-[1.1]">{h1_pre} <span class="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">{h1_accent}</span></h1>
<p class="text-xl text-slate-400 mb-8 leading-relaxed max-w-3xl">{lead}</p>
<div class="flex flex-col sm:flex-row gap-4 max-w-xl">
<a class="inline-flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-xl font-bold transition shadow-lg whitespace-nowrap" href="{primary[1]}">{primary[0]}</a>
{secondary_html}
</div>
{trust_html}
</div>
</header>"""


def cards(items, columns=3):
    body = "\n".join(
        f"""<div class="bg-slate-900/40 p-6 border border-slate-800 rounded-2xl">
<div class="text-2xl font-extrabold text-white mb-1">{v}</div>
<div class="text-sm font-semibold text-blue-400 mb-2">{k}</div>
<p class="text-slate-400 text-sm leading-relaxed">{d}</p>
</div>""" for k, v, d in items
    )
    return f'<div class="grid md:grid-cols-{columns} gap-5">{body}</div>'


def link_list(title, links):
    items = "\n".join(
        f'<li><a class="text-blue-400 hover:text-blue-300 transition" href="{href}">{label} →</a></li>'
        for label, href in links
    )
    return f"""<section class="max-w-4xl mx-auto px-6 py-12">
<div class="p-6 bg-slate-900 rounded-xl border border-slate-800">
<h3 class="text-xl font-bold text-white mb-4">{title}</h3>
<ul class="space-y-3">{items}</ul>
</div>
</section>"""


# ---------------------------------------------------------------------------
# 1. Markägare — sajtens mest värdefulla silo
# ---------------------------------------------------------------------------

MARKAGARE_FORM = f"""<section class="max-w-4xl mx-auto px-6 py-16" id="anmalan">
<div class="bg-gradient-to-br from-blue-900/40 to-emerald-900/25 border border-blue-500/30 rounded-3xl p-8 md:p-10">
<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-semibold mb-4 uppercase tracking-wider">Kostnadsfritt · tjänsten byggs upp nu</div>
<h2 class="text-3xl font-bold text-white mb-3">Anmäl din mark för bedömning</h2>
<p class="text-slate-300 mb-4 leading-relaxed">Beskriv din fastighet så hör vi av oss när vi kan säga något vettigt om vad marken är värd i ditt län, vilka aktörer som är aktiva där och vad du bör ha koll på innan du skriver på något. Du binder dig inte till någonting.</p>
<p class="text-slate-400 mb-8 text-sm leading-relaxed border-l-2 border-slate-700 pl-4">Ärligt om läget: Vindkollen är nystartat och vi har inga avtalade rådgivare eller projektörer på plats ännu. Vi sätter inget datum vi inte kan hålla — men vi läser varje inskickning, och du får våra marknadsuppdateringar under tiden.</p>
<form class="space-y-5" onsubmit="return false" data-vk-lead-form data-segment="markagare" data-source="markagare_silo">
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="mk-name">Namn</label>
<input class="{FIELD}" id="mk-name" name="name" placeholder="För- och efternamn" required type="text"/></div>
<div><label class="{LABEL}" for="mk-email">E-post</label>
<input class="{FIELD}" id="mk-email" name="email" placeholder="din@epost.se" required type="email"/></div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="mk-phone">Telefon <span class="text-slate-500 font-normal">(ger snabbare återkoppling)</span></label>
<input class="{FIELD}" id="mk-phone" name="phone" placeholder="07X-XXX XX XX" type="tel"/></div>
<div><label class="{LABEL}" for="mk-county">Län</label>
{county_select()}</div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="mk-municipality">Kommun</label>
<input class="{FIELD}" id="mk-municipality" name="municipality" placeholder="t.ex. Ånge" type="text"/></div>
<div><label class="{LABEL}" for="mk-hectares">Markareal (hektar)</label>
<input class="{FIELD}" id="mk-hectares" name="land_hectares" min="0" placeholder="t.ex. 120" step="1" type="number"/></div>
</div>
<div><label class="{LABEL}" for="mk-address">Fastighetsbeteckning eller adress <span class="text-slate-500 font-normal">(valfritt)</span></label>
<input class="{FIELD}" id="mk-address" name="property_address" placeholder="t.ex. Gnarp 4:12" type="text"/></div>
<div><label class="{LABEL}" for="mk-stage">Var i processen är du?</label>
<select class="{FIELD}" id="mk-stage" name="project_stage">
<option value="ingen_kontakt">Ingen kontakt än – undersöker möjligheten</option>
<option value="kontaktad">Kontaktad av projektör</option>
<option value="forhandlar">Avtalsförslag på bordet / förhandlar nu</option>
<option value="har_avtal">Har redan avtal – vill se om det är marknadsmässigt</option>
</select></div>
<div><label class="{LABEL}" for="mk-timeframe">När vill du ha svar?</label>
<select class="{FIELD}" id="mk-timeframe" name="timeframe">
<option value="nu">Inom 3 månader</option>
<option value="i_ar">Inom ett år</option>
<option value="senare">Längre fram – jag bevakar bara</option>
</select></div>
<div><label class="{LABEL}" for="mk-message">Något mer vi bör veta? <span class="text-slate-500 font-normal">(valfritt)</span></label>
<textarea class="{FIELD}" id="mk-message" name="message" placeholder="t.ex. skogsmark på höjdläge, 3 km till befintlig kraftledning" rows="3"></textarea></div>
<div class="space-y-3 pt-2 border-t border-slate-700/60">
<label class="flex gap-3 text-sm text-slate-300"><input class="{CHECK}" name="wants_projector_contact" type="checkbox"/>
<span>Jag är öppen för kontakt med projektörer i mitt län, om och när vi kan förmedla en sådan.</span></label>
<label class="flex gap-3 text-sm text-slate-300"><input class="{CHECK}" name="wants_legal_help" type="checkbox"/>
<span>Hör av er när ni kan förmedla kontakt med en jurist som kan markavtal.</span></label>
<label class="flex gap-3 text-sm text-slate-300"><input class="{CHECK}" name="consent_partner_share" type="checkbox"/>
<span>Jag samtycker till att Vindkollen får dela mina uppgifter med utvalda samarbetspartner i mitt län. Utan bock hör bara vi av oss.</span></label>
</div>
<div class="hidden text-red-400 text-sm" data-vk-error hidden></div>
<button class="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-bold text-lg transition shadow-lg" type="submit">Skicka in min fastighet →</button>
<p class="text-xs text-slate-400 italic">Vi säljer aldrig dina uppgifter vidare utan din bock ovan. Du kan när som helst be oss radera dem.</p>
</form>
<div class="hidden p-6 bg-emerald-500/15 border border-emerald-500/30 rounded-xl text-emerald-200" data-vk-success hidden>
<div class="font-bold text-lg mb-1">Tack – vi har fått dina uppgifter.</div>
Du får en bekräftelse på mejlen direkt. Sedan hör vi av oss när vi har något konkret för ditt län. Under tiden: testa <a class="underline" href="/arrendekalkylator">arrendekalkylatorn</a> för att se vad royaltynivån betyder i kronor.
</div>
</div>
</section>"""

MARKAGARE_BODY = f"""<section class="max-w-5xl mx-auto px-6 py-14">
<h2 class="text-3xl font-bold text-white mb-3">Vad marken faktiskt ger</h2>
<p class="text-slate-400 mb-8 max-w-3xl">Ett arrendeavtal för vindkraft löper i 30–40 år. Skillnaden mellan ett förhandlat och ett oförhandlat avtal räknas i miljoner över avtalstiden – här är storleksordningarna.</p>
{cards([
    ("Årligt arrende per verk", "150–300 tkr", "Vanligt spann för ett modernt verk på 4–6 MW, ofta som en kombination av fast minimiarrende och rörlig royalty."),
    ("Royalty på bruttointäkt", "3–5 %", "Branschstandard idag. Vad royaltyn räknas på – före eller efter nätförluster – kan skilja tiotusentals kronor per år."),
    ("Engångsersättning vid bygg", "50–100 tkr", "Betalas per verk vid byggstart som ersättning för markintrång, vägar och uppställningsytor."),
])}
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-3">Är din mark intressant?</h2>
<p class="text-slate-400 mb-8 max-w-3xl">Fem saker avgör om en projektör över huvud taget hör av sig. Du behöver inte kryssa i alla – men ju fler, desto starkare läge har du i förhandlingen.</p>
<ul class="grid md:grid-cols-2 gap-4 text-slate-300">
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Areal.</b> Från ca 30–50 hektar sammanhängande mark börjar det bli aktuellt. Flera grannfastigheter kan gå ihop.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Vindläge.</b> Höjdlägen och öppen terräng. Energimyndighetens vindkartering visar medelvinden på 100–150 meters höjd.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Nätanslutning.</b> Avstånd till regionnät med ledig kapacitet är ofta det som avgör projektets kalkyl.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Avstånd till bostäder.</b> Ju färre bostadshus inom nio verkshöjder, desto enklare tillstånd – och desto mindre intäktsdelning belastar parken.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Kommunens inställning.</b> Det kommunala vetot gäller fortfarande. En kommun med positiv vindbruksplan är värd mycket.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Inga hinder.</b> Natura 2000, riksintresse försvar, kungsörnsrevir och renskötselområden begränsar var verk får stå.</li>
</ul>
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-3">Innan du skriver på</h2>
<p class="text-slate-400 mb-6 max-w-3xl">Det första avtalsförslaget är sällan det bästa. De här punkterna kostar mest att missa:</p>
<ol class="space-y-3 text-slate-300 list-decimal pl-6 marker:text-blue-400 marker:font-bold">
<li><b class="text-white">Royaltybasen.</b> Räknas procenten på bruttointäkt eller efter avdrag för nätförluster, balanskostnader och certifikat?</li>
<li><b class="text-white">Indexering.</b> Ett minimiarrende utan KPI-uppräkning halveras i värde över avtalstiden.</li>
<li><b class="text-white">Optionstiden.</b> Hur länge kan bolaget binda upp din mark utan att bygga – och vad får du under tiden?</li>
<li><b class="text-white">Återställningsgaranti.</b> Vem betalar rivningen om bolaget går i konkurs? Kräv bankgaranti, inte moderbolagsborgen.</li>
<li><b class="text-white">Överlåtelse.</b> Projektet säljs nästan alltid vidare. Se till att villkoren följer med och att du får veta vem motparten blir.</li>
</ol>
<div class="mt-8 p-6 bg-amber-500/10 border border-amber-500/25 rounded-2xl">
<p class="text-amber-100"><b>Har du redan ett avtalsförslag på bordet?</b> Då är juridisk granskning nästan alltid lönsam i förhållande till vad den kostar.</p>
<a class="inline-block mt-4 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/40 text-amber-100 px-6 py-3 rounded-xl font-semibold transition" href="/juridisk-hjalp-arrendeavtal">Läs om juridisk hjälp inför arrendeavtal →</a>
</div>
</section>

{MARKAGARE_FORM}

{link_list("Fördjupning för markägare", [
    ("Arrendekalkylator – räkna på royalty, minimiarrende och engångsersättning", "/arrendekalkylator"),
    ("Arrendeavtal för vindkraft – villkor, avtalstid och fallgropar", "/arrendeavtal-vindkraft"),
    ("Så får du vindkraft på din mark – processen steg för steg", "/sa-far-du-vindkraft-pa-din-mark"),
    ("Skatt på arrende- och royaltyintäkter", "/skatt-vindkraftersattning"),
    ("Vindkraft eller solpark på marken? Jämförelse av avkastning och risk", "/arrende-vindkraft-vs-solpark"),
    ("Ersättningsnivåer region för region (SE1–SE4)", "/ersattningsnivaer-region-for-region"),
])}"""

MARKAGARE_FAQ = [
    ("Hur mycket får jag i arrende för ett vindkraftverk?",
     "För ett modernt verk på 4–6 MW ligger det årliga arrendet vanligen mellan 150 000 och 300 000 kronor per verk. "
     "Ersättningen består oftast av ett garanterat minimiarrende på 100 000–150 000 kronor och en royalty på 3–5 procent "
     "av parkens bruttointäkt, där den högre av de två betalas ut."),
    ("Hur mycket mark behöver jag?",
     "Ett enskilt verk tar bara någon hektar i anspråk inklusive vägar och uppställningsyta, men projektörer söker "
     "normalt sammanhängande områden från cirka 30–50 hektar. Flera grannfastigheter kan gå samman i ett gemensamt "
     "projekt och dela ersättningen."),
    ("Påverkar den nya lagen om intäktsdelning mitt arrende?",
     "Nej. Intäktsdelningen från 1 juli 2026 är en lagstadgad ersättning till närboende bostadsägare och betalas av "
     "verksamhetsutövaren. Ditt markarrende är ett civilrättsligt avtal som förhandlas separat med projektören."),
    ("Kan jag förhandla om det första avtalsförslaget?",
     "Ja. Det första förslaget är en utgångspunkt, inte ett facit. Royaltybas, indexering, optionstid och "
     "återställningsgaranti är alla förhandlingsbara, och skillnaden mellan ett granskat och ett ogranskat avtal räknas "
     "ofta i miljoner över avtalets 30–40 år."),
    ("Vad kostar det att använda Vindkollen?",
     "Ingenting för dig som markägare. Vi är oberoende från kraftbolagen och tar aldrig betalt av markägare eller "
     "närboende för information, kalkyler eller kontaktförmedling."),
]

# ---------------------------------------------------------------------------
# 2. Närboende
# ---------------------------------------------------------------------------

NARBOENDE_FORM = f"""<section class="max-w-4xl mx-auto px-6 py-16" id="anmalan">
<div class="bg-gradient-to-br from-blue-900/40 to-emerald-900/25 border border-blue-500/30 rounded-3xl p-8 md:p-10">
<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-semibold mb-4 uppercase tracking-wider">Kostnadsfritt · uppdateringar om lagen</div>
<h2 class="text-3xl font-bold text-white mb-3">Håll koll på vad som gäller</h2>
<p class="text-slate-300 mb-4 leading-relaxed">Vi följer lagen om intäktsdelning och hör av oss när reglerna ändras eller anmälningsfönstret öppnar. Den som missar sin årliga anmälan går miste om hela årets ersättning – det är den påminnelsen som är värd mest.</p>
<p class="text-slate-400 mb-8 text-sm leading-relaxed border-l-2 border-slate-700 pl-4">Lämnar du län och avstånd vet vi vilken situation utskicken ska passa. Vi övervakar inte enskilda parker automatiskt – vi bevakar lagstiftningen och skriver till dig när något faktiskt ändras.</p>
<form class="space-y-5" onsubmit="return false" data-vk-lead-form data-segment="narboende" data-source="narboende_silo">
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="nb-name">Namn</label>
<input class="{FIELD}" id="nb-name" name="name" placeholder="För- och efternamn" required type="text"/></div>
<div><label class="{LABEL}" for="nb-email">E-post</label>
<input class="{FIELD}" id="nb-email" name="email" placeholder="din@epost.se" required type="email"/></div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="nb-county">Län</label>
{county_select()}</div>
<div><label class="{LABEL}" for="nb-municipality">Kommun</label>
<input class="{FIELD}" id="nb-municipality" name="municipality" placeholder="t.ex. Falkenberg" type="text"/></div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="nb-address">Adress till bostaden <span class="text-slate-500 font-normal">(valfritt)</span></label>
<input class="{FIELD}" id="nb-address" name="property_address" placeholder="Gatuadress" type="text"/></div>
<div><label class="{LABEL}" for="nb-distance">Avstånd till närmaste verk (meter)</label>
<input class="{FIELD}" id="nb-distance" name="distance_m" min="0" placeholder="t.ex. 1200" step="50" type="number"/></div>
</div>
<div><label class="{LABEL}" for="nb-stage">Hur ser läget ut där du bor?</label>
<select class="{FIELD}" id="nb-stage" name="project_stage">
<option value="ingen_kontakt">Rykten om att något planeras</option>
<option value="kontaktad">Samråd pågår eller har hållits</option>
<option value="forhandlar">Tillstånd sökt eller beviljat</option>
<option value="byggd_park">Parken är redan byggd</option>
</select></div>
<div class="space-y-3 pt-2 border-t border-slate-700/60">
<label class="flex gap-3 text-sm text-slate-300"><input class="{CHECK}" name="wants_legal_help" type="checkbox"/>
<span>Jag vill veta mer om mina rättigheter vid värdeminskning eller inlösen av fastigheten.</span></label>
<label class="flex gap-3 text-sm text-slate-300" data-vk-owns-land><input class="{CHECK}" name="wants_projector_contact" type="checkbox"/>
<span>Jag äger också mark där verk skulle kunna placeras och är öppen för kontakt om och när det blir aktuellt.</span></label>
<label class="flex gap-3 text-sm text-slate-300"><input class="{CHECK}" name="consent_partner_share" type="checkbox"/>
<span>Jag samtycker till att mina uppgifter får delas med utvalda samarbetspartner i mitt län.</span></label>
</div>
<div class="hidden text-red-400 text-sm" data-vk-error hidden></div>
<button class="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-bold text-lg transition shadow-lg" type="submit">Bevaka min adress →</button>
<p class="text-xs text-slate-400 italic">Vi delar aldrig dina uppgifter med kraftbolag utan ditt godkännande. Avregistrera när du vill.</p>
</form>
<div class="hidden p-6 bg-emerald-500/15 border border-emerald-500/30 rounded-xl text-emerald-200" data-vk-success hidden>
<div class="font-bold text-lg mb-1">Tack – du står på listan.</div>
Vi hör av oss när reglerna ändras på ett sätt som påverkar din ersättning. Räkna gärna på beloppet redan nu i <a class="underline" href="/kalkylator">ersättningskalkylatorn</a>.
</div>
</div>
</section>"""

NARBOENDE_BODY = f"""<section class="max-w-5xl mx-auto px-6 py-14">
<h2 class="text-3xl font-bold text-white mb-3">Trappstegsmodellen: avståndet avgör</h2>
<p class="text-slate-400 mb-8 max-w-3xl">Ersättningen räknas som en promillesats av parkens årsintäkter, och satsen trappas ned med avståndet mätt i verkshöjder. För ett verk på 250 meter går yttre gränsen vid 2 250 meter.</p>
<div class="grid grid-cols-2 md:grid-cols-5 gap-3 text-center mb-8">
<div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700"><div class="text-xs text-slate-400">≤ 5× höjden</div><div class="text-xl font-bold text-emerald-400">2,5‰</div></div>
<div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700"><div class="text-xs text-slate-400">5–6×</div><div class="text-xl font-bold text-emerald-300">2,0‰</div></div>
<div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700"><div class="text-xs text-slate-400">6–7×</div><div class="text-xl font-bold text-blue-300">1,5‰</div></div>
<div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700"><div class="text-xs text-slate-400">7–8×</div><div class="text-xl font-bold text-blue-400">1,0‰</div></div>
<div class="bg-slate-800/50 p-4 rounded-xl border border-slate-700"><div class="text-xs text-slate-400">8–9×</div><div class="text-xl font-bold text-purple-400">0,5‰</div></div>
</div>
{cards([
    ("Maxnivå SE4 (södra Sverige)", "38 400 kr/år", "Elpriset är högst i söder, vilket ger den högsta ersättningen per bostad enligt regeringens beräkningar."),
    ("Maxnivå SE1 (norra Sverige)", "19 400 kr/år", "Samma modell men lägre elpris ger ungefär halva beloppet jämfört med SE4."),
    ("Skatt på ersättningen", "0 kr", "Ersättningen är skattefri till den del den avser en privatbostad – du behöver inte deklarera den."),
], columns=3)}
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-3">Fyra saker du behöver veta</h2>
<ul class="space-y-4 text-slate-300">
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Lagen gäller nya parker.</b> Intäktsdelningen omfattar parker som får lagakraftvunnet miljötillstånd efter den 1 juli 2026. Bor du nära en befintlig park är du i stället hänvisad till frivillig bygdepeng.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Du måste anmäla dig varje år.</b> Ersättningen betalas inte ut automatiskt – bostadsägaren anmäler sin bostad till verksamhetsutövaren årligen. Missad anmälan innebär utebliven ersättning för det året.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">De två närmaste verken räknas.</b> Beräkningen utgår från de två verk som ger högst ersättning för just din bostad, inte från parkens mittpunkt.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Det finns ett tak.</b> Verksamhetsutövaren betalar aldrig mer än 2 procent av parkens totala årsintäkter i sammanlagd intäktsdelning. I tätbebyggda områden kan det sänka beloppet per hushåll.</li>
</ul>
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<div class="p-6 bg-slate-900/60 border border-slate-800 rounded-2xl">
<h2 class="text-2xl font-bold text-white mb-3">Äger du också marken?</h2>
<p class="text-slate-400 mb-5">Är du både närboende och markägare är intäktsdelningen den mindre delen av kalkylen. Ett arrendeavtal ger normalt 150 000–300 000 kronor per verk och år – tio gånger mer än ersättningen som närboende.</p>
<a class="inline-block bg-emerald-600 hover:bg-emerald-500 text-white px-6 py-3 rounded-xl font-semibold transition" data-vk-segment="markagare" href="/markagare">Gå till markägarspåret →</a>
</div>
</section>

{NARBOENDE_FORM}

{link_list("Fördjupning för närboende", [
    ("Ersättningskalkylator – räkna på din bostad", "/kalkylator"),
    ("Nio verkshöjder – så dras gränsen för ersättning", "/nio-verkshojder-ersattning"),
    ("Intäktsdelning från vindkraft – hela lagen förklarad", "/intaktsdelning-vindkraft"),
    ("Bullernivå och minimiavstånd – vad gäller egentligen?", "/bullerniva-minimiavstand-vindkraft"),
    ("Påverkar vindkraft fastighetsvärdet?", "/paverkar-vindkraft-fastighetsvarde"),
    ("Rätt till inlösen av fastighet nära vindkraftverk", "/ratt-till-inlosen-fastighet-vindkraft"),
])}"""

NARBOENDE_FAQ = [
    ("Hur mycket får jag som närboende i vindkraftsersättning?",
     "Upp till cirka 38 400 kronor per år i elområde SE4 och cirka 19 400 kronor per år i SE1, enligt regeringens "
     "beräkningar. Beloppet beror på avståndet till de två närmaste verken och trappas ned från 2,5 promille av "
     "parkens årsintäkter till 0,5 promille vid nio verkshöjder."),
    ("När börjar intäktsdelningen gälla?",
     "Lagen om intäktsdelning från vindkraftsanläggningar föreslås träda i kraft den 1 juli 2026 och omfattar parker "
     "som därefter får lagakraftvunnet miljötillstånd."),
    ("Måste jag ansöka om ersättningen?",
     "Ja. Den som är ersättningsberättigad anmäler sin bostad till verksamhetsutövaren varje år. Ersättningen betalas "
     "inte ut automatiskt, och en missad anmälan innebär att du går miste om det årets ersättning."),
    ("Är ersättningen skattepliktig?",
     "Nej, ersättningen är skattefri till den del den avser en privatbostad. Avser den en näringsfastighet gäller "
     "vanliga regler för näringsverksamhet."),
    ("Får jag ersättning om parken redan är byggd?",
     "Inte enligt den nya lagen, som bara omfattar parker med tillstånd efter ikraftträdandet. För befintliga parker "
     "förekommer i stället frivillig bygdepeng, som normalt går till bygdeföreningar snarare än till enskilda hushåll."),
]

# ---------------------------------------------------------------------------
# 3. Kommun
# ---------------------------------------------------------------------------

KOMMUN_FORM = f"""<section class="max-w-4xl mx-auto px-6 py-16" id="anmalan">
<div class="bg-gradient-to-br from-teal-900/40 to-blue-900/25 border border-teal-500/30 rounded-3xl p-8 md:p-10">
<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-teal-500/15 border border-teal-500/30 text-teal-300 text-xs font-semibold mb-4 uppercase tracking-wider">Kostnadsfritt · oberoende från kraftbolagen</div>
<h2 class="text-3xl font-bold text-white mb-3">Ställ er fråga till oss</h2>
<p class="text-slate-300 mb-4 leading-relaxed">Berätta vad ni behöver svar på om en planerad etablering – fastighetsskatt, intäktsdelning till närboende, bygdepeng eller sysselsättning – så återkommer vi med det underlag vi har, med källhänvisningar.</p>
<p class="text-slate-400 mb-8 text-sm leading-relaxed border-l-2 border-slate-700 pl-4">Vi är nystartade och bygger upp kommununderlagen efter hand. Kan vi inte hjälpa er säger vi det rakt ut i stället för att dra ut på det. Under tiden kan ni räkna själva i kommun-dashboarden.</p>
<form class="space-y-5" onsubmit="return false" data-vk-lead-form data-segment="kommun" data-source="kommun_silo">
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="km-org">Kommun eller organisation</label>
<input class="{FIELD}" id="km-org" name="organisation" placeholder="t.ex. Ånge kommun" required type="text"/></div>
<div><label class="{LABEL}" for="km-role">Din roll</label>
<input class="{FIELD}" id="km-role" name="role" placeholder="t.ex. planarkitekt, kommunalråd" type="text"/></div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="km-name">Namn</label>
<input class="{FIELD}" id="km-name" name="name" placeholder="För- och efternamn" required type="text"/></div>
<div><label class="{LABEL}" for="km-email">E-post</label>
<input class="{FIELD}" id="km-email" name="email" placeholder="fornamn.efternamn@kommun.se" required type="email"/></div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="km-phone">Telefon <span class="text-slate-500 font-normal">(valfritt)</span></label>
<input class="{FIELD}" id="km-phone" name="phone" placeholder="07X-XXX XX XX" type="tel"/></div>
<div><label class="{LABEL}" for="km-county">Län</label>
{county_select()}</div>
</div>
<div><label class="{LABEL}" for="km-stage">Var står ärendet?</label>
<select class="{FIELD}" id="km-stage" name="project_stage">
<option value="ingen_kontakt">Vi ser över vindbruksplanen</option>
<option value="kontaktad">Projektör har hört av sig</option>
<option value="forhandlar">Tillståndsprövning pågår – veto ska tas ställning till</option>
<option value="byggd_park">Vi har redan parker i kommunen</option>
</select></div>
<div><label class="{LABEL}" for="km-timeframe">När behöver ni underlaget?</label>
<select class="{FIELD}" id="km-timeframe" name="timeframe">
<option value="nu">Inom 3 månader</option>
<option value="i_ar">Inom ett år</option>
<option value="senare">Ingen brådska</option>
</select></div>
<div><label class="{LABEL}" for="km-message">Vad vill ni ha svar på?</label>
<textarea class="{FIELD}" id="km-message" name="message" placeholder="t.ex. vad 24 verk på 6 MW ger kommunen i årliga intäkter" rows="3"></textarea></div>
<div class="hidden text-red-400 text-sm" data-vk-error hidden></div>
<button class="w-full bg-teal-600 hover:bg-teal-500 text-white py-4 rounded-xl font-bold text-lg transition shadow-lg" type="submit">Skicka er fråga →</button>
<p class="text-xs text-slate-400 italic">Vi är oberoende från kraftbolagen och tar inte betalt av kommuner. Allt vi skickar har källhänvisningar till propositioner och myndighetsdata.</p>
</form>
<div class="hidden p-6 bg-emerald-500/15 border border-emerald-500/30 rounded-xl text-emerald-200" data-vk-success hidden>
<div class="font-bold text-lg mb-1">Tack – frågan är mottagen.</div>
Vi återkommer så snart vi kan. Under tiden kan ni räkna själva i <a class="underline" href="/kommun-dashboard">kommun-dashboarden</a>.
</div>
</div>
</section>"""

KOMMUN_BODY = f"""<section class="max-w-5xl mx-auto px-6 py-14">
<h2 class="text-3xl font-bold text-white mb-3">Tre intäktsströmmar – och vad som ändras 2026</h2>
<p class="text-slate-400 mb-8 max-w-3xl">Fram till nu har kommunernas ekonomiska nytta av vindkraft varit svag i förhållande till den lokala påverkan. Från 2026 förändras balansen i tre steg.</p>
{cards([
    ("Fastighetsskatt", "~20 tkr/MW", "Fastighetsskatten på vindkraftverk föreslås i högre grad tillfalla den kommun där verken står, i stället för att i sin helhet gå till staten."),
    ("Intäktsdelning", "0,5–2,5 ‰", "Går till närboende bostadsägare inom nio verkshöjder – inte till kommunkassan, men det påverkar den lokala acceptansen påtagligt."),
    ("Bygdepeng", "0,2–0,5 %", "Frivillig ersättning till bygden, normalt av parkens bruttointäkt. Fördelas via bygdemedelsföreningar och kommunala fonder."),
])}
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-3">Frågorna som brukar avgöra ärendet</h2>
<ul class="space-y-4 text-slate-300">
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Vad blir nettot för kommunen?</b> Fastighetsskatt och sysselsättning ställt mot vägslitage, handläggningskostnader och påverkan på besöksnäringen.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Hur påverkas det kommunala vetot?</b> Tillstyrkan enligt 16 kap. 4 § miljöbalken gäller fortfarande, men förutsättningarna att säga ja förändras när lokala intäkter tillkommer.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Hur många hushåll berörs av intäktsdelningen?</b> Antalet bostadshus inom nio verkshöjder styr både kostnaden för projektören och den lokala opinionen.</li>
<li class="bg-slate-900/40 border border-slate-800 rounded-xl p-5"><b class="text-white">Vad säger vindbruksplanen?</b> En aktuell plan minskar handläggningstiden och ger kommunen ett mycket starkare förhandlingsläge mot projektören.</li>
</ul>
</section>

{KOMMUN_FORM}

{link_list("Fördjupning för kommuner", [
    ("Kommun-dashboard – räkna på intäkterna av en etablering", "/kommun-dashboard"),
    ("Kommunersättning och fastighetsskatt 2026", "/kommunersattning-vindkraft-2026"),
    ("Bygdepeng: regler och fördelning", "/bygdepeng-vindkraft-regler-2026"),
    ("Intäktsdelning till närboende – lagen förklarad", "/intaktsdelning-vindkraft"),
    ("Nackdelar med vindkraft – faktagranskad genomgång", "/nackdelar-med-vindkraft"),
])}"""

KOMMUN_FAQ = [
    ("Hur mycket får kommunen in på ett vindkraftverk?",
     "Med den föreslagna omfördelningen av fastighetsskatten motsvarar det i storleksordningen 20 000 kronor per "
     "installerad MW och år till den kommun där verken står. En park på 24 verk om 6 MW motsvarar då cirka 2,9 "
     "miljoner kronor per år."),
    ("Går intäktsdelningen till kommunen?",
     "Nej. Intäktsdelningen från 1 juli 2026 betalas direkt till ägare av bostadshus inom nio verkshöjder. Kommunens "
     "intäkter kommer i stället via fastighetsskatt, eventuell bygdepeng och ökad sysselsättning."),
    ("Finns det kommunala vetot kvar?",
     "Ja. Kommunens tillstyrkan enligt 16 kap. 4 § miljöbalken krävs fortfarande för tillstånd till en "
     "vindkraftsanläggning. Reformerna 2026 ändrar de ekonomiska förutsättningarna, inte vetorätten i sig."),
    ("Vad är bygdepeng och är den obligatorisk?",
     "Bygdepeng är en frivillig ersättning från projektören till bygden, ofta 0,2–0,5 procent av parkens bruttointäkt. "
     "Den regleras i avtal med kommunen eller en bygdemedelsförening och följer inte av lag."),
]

# ---------------------------------------------------------------------------
# 4. Juridisk hjälp — högsta värdet per lead
# ---------------------------------------------------------------------------

JURIDIK_FORM = f"""<section class="max-w-4xl mx-auto px-6 py-16" id="anmalan">
<div class="bg-gradient-to-br from-amber-900/30 to-blue-900/25 border border-amber-500/30 rounded-3xl p-8 md:p-10">
<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/15 border border-amber-500/30 text-amber-200 text-xs font-semibold mb-4 uppercase tracking-wider">Under uppbyggnad · kostnadsfritt för dig</div>
<h2 class="text-3xl font-bold text-white mb-3">Anmäl intresse för juridisk hjälp</h2>
<p class="text-slate-300 mb-4 leading-relaxed">Vi håller på att bygga upp ett nätverk av oberoende jurister och lantbruksekonomer som arbetar med arrende- och markupplåtelseavtal. Beskriv ditt ärende så hör vi av oss när vi kan förmedla en kontakt i ditt län. Vi tar inte betalt av dig, och du väljer själv om du går vidare.</p>
<div class="p-4 mb-8 bg-amber-500/10 border border-amber-500/25 rounded-xl text-amber-100 text-sm leading-relaxed">
<b>Har du bråttom?</b> Vi har ännu inga avtalade rådgivare och kan inte lova när vi har det. Ligger ett avtalsförslag på bordet med kort svarstid — vänta inte på oss. Kontakta en advokatbyrå som arbetar med fastighetsrätt eller en lantbruksekonom direkt. Checklistan ovan fungerar lika bra som underlag till ett möte du bokar själv.
</div>
<form class="space-y-5" onsubmit="return false" data-vk-lead-form data-segment="markagare" data-source="juridik_silo">
<input checked hidden name="wants_legal_help" type="checkbox"/>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="ju-name">Namn</label>
<input class="{FIELD}" id="ju-name" name="name" placeholder="För- och efternamn" required type="text"/></div>
<div><label class="{LABEL}" for="ju-email">E-post</label>
<input class="{FIELD}" id="ju-email" name="email" placeholder="din@epost.se" required type="email"/></div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="ju-phone">Telefon</label>
<input class="{FIELD}" id="ju-phone" name="phone" placeholder="07X-XXX XX XX" type="tel"/></div>
<div><label class="{LABEL}" for="ju-county">Län</label>
{county_select()}</div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="ju-hectares">Markareal (hektar)</label>
<input class="{FIELD}" id="ju-hectares" name="land_hectares" min="0" placeholder="t.ex. 90" step="1" type="number"/></div>
<div><label class="{LABEL}" for="ju-stage">Var i processen är du?</label>
<select class="{FIELD}" id="ju-stage" name="project_stage">
<option value="forhandlar">Avtalsförslag på bordet</option>
<option value="kontaktad">Kontaktad av projektör</option>
<option value="har_avtal">Har redan avtal – vill få det granskat</option>
<option value="ingen_kontakt">Förbereder mig inför en kommande kontakt</option>
</select></div>
</div>
<div><label class="{LABEL}" for="ju-message">Kort om ditt ärende</label>
<textarea class="{FIELD}" id="ju-message" name="message" placeholder="t.ex. optionsavtal på 5 år, royalty 3 % efter nätförluster, ingen indexering av minimiarrendet" rows="4"></textarea></div>
<div class="space-y-3 pt-2 border-t border-slate-700/60">
<label class="flex gap-3 text-sm text-slate-300"><input class="{CHECK}" name="consent_partner_share" type="checkbox"/>
<span>Jag samtycker till att Vindkollen delar mina uppgifter med den rådgivare som kan ta ärendet, när vi har en på plats i mitt län.</span></label>
</div>
<div class="hidden text-red-400 text-sm" data-vk-error hidden></div>
<button class="w-full bg-amber-600 hover:bg-amber-500 text-white py-4 rounded-xl font-bold text-lg transition shadow-lg" type="submit">Anmäl mitt ärende →</button>
<p class="text-xs text-slate-400 italic">Vindkollen ger inte juridisk rådgivning och är inte part i avtalet. Vi förmedlar kontakt med oberoende rådgivare i den mån vi kan.</p>
</form>
<div class="hidden p-6 bg-emerald-500/15 border border-emerald-500/30 rounded-xl text-emerald-200" data-vk-success hidden>
<div class="font-bold text-lg mb-1">Tack – vi har fått ditt ärende.</div>
Vi hör av oss så snart vi kan förmedla en kontakt i ditt län. Har du bråttom: vänta inte på oss, ta kontakt med en fastighetsjurist direkt. Läs gärna <a class="underline" href="/arrendeavtal-vindkraft">genomgången av arrendeavtalets villkor</a> under tiden.
</div>
</div>
</section>"""

JURIDIK_BODY = f"""<section class="max-w-5xl mx-auto px-6 py-14">
<h2 class="text-3xl font-bold text-white mb-3">Varför avtalet är värt en granskning</h2>
<p class="text-slate-400 mb-8 max-w-3xl">Ett arrendeavtal för vindkraft binder marken i 30–40 år och skrivs av en motpart som gör tiotals sådana avtal om året. Du gör ett. Kostnaden för en granskning är en bråkdel av vad en enda felskriven paragraf kostar över avtalstiden.</p>
{cards([
    ("Avtalstid", "30–40 år", "Inklusive optionstid innan bygget. Villkoren du skriver under idag gäller nästan säkert längre än du äger fastigheten."),
    ("Vad en procentenhet royalty gör", "≈ 1,5 mkr", "Skillnaden mellan 3 och 4 procent royalty för ett 6 MW-verk över 30 år, vid normala antaganden om produktion och elpris."),
    ("Vanligaste missen", "Indexering", "Ett minimiarrende utan KPI-koppling tappar en betydande del av sitt realvärde under avtalstiden."),
])}
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900" id="punkterna">
<h2 class="text-3xl font-bold text-white mb-3">Tio punkter en rådgivare går igenom</h2>
<p class="text-slate-400 mb-6 max-w-3xl">Ta med listan till mötet – den fungerar lika bra oavsett om du bokar rådgivaren själv eller via oss.</p>
<ol class="space-y-3 text-slate-300 list-decimal pl-6 marker:text-amber-400 marker:font-bold">
<li><b class="text-white">Royaltybasen.</b> Bruttointäkt eller nettot efter nätförluster, balanskostnader och certifikat?</li>
<li><b class="text-white">Minimiarrendet.</b> Nivå, och om det är ett golv eller avräknas mot royaltyn.</li>
<li><b class="text-white">Indexering.</b> KPI-uppräkning av samtliga fasta belopp, inte bara ett av dem.</li>
<li><b class="text-white">Optionstiden.</b> Hur länge marken är bunden utan byggstart, och vad du får under tiden.</li>
<li><b class="text-white">Återställningsgaranti.</b> Bankgaranti med indexerat belopp – inte moderbolagsborgen från ett bolag som kan tömmas.</li>
<li><b class="text-white">Överlåtelse.</b> Projekt byter ägare. Villkoren ska följa med, och du bör få veta vem som tar över.</li>
<li><b class="text-white">Vägar och servitut.</b> Vem underhåller, vem får använda vägarna, och vad händer med dem efter rivning?</li>
<li><b class="text-white">Intrångsersättning.</b> Skog som avverkas, mark som tas i anspråk, skador under byggtiden.</li>
<li><b class="text-white">Sekretessklausuler.</b> Alltför breda sekretessvillkor hindrar dig från att jämföra med grannarnas avtal.</li>
<li><b class="text-white">Tvistlösning.</b> Skiljeförfarande kan bli mycket dyrt för en enskild markägare – allmän domstol är ofta bättre för dig.</li>
</ol>
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-3">Även för dig som är närboende</h2>
<p class="text-slate-400 max-w-3xl mb-5">Juridisk hjälp är inte bara en markägarfråga. Frågor om värdeminskning, rätt till inlösen och överklagande av tillstånd hanteras av samma typ av rådgivare.</p>
<div class="flex flex-wrap gap-4">
<a class="bg-slate-900/60 hover:bg-slate-800 border border-slate-700 px-6 py-3 rounded-xl font-semibold transition" href="/ratt-till-inlosen-fastighet-vindkraft">Rätt till inlösen →</a>
<a class="bg-slate-900/60 hover:bg-slate-800 border border-slate-700 px-6 py-3 rounded-xl font-semibold transition" href="/paverkar-vindkraft-fastighetsvarde">Påverkan på fastighetsvärde →</a>
</div>
</section>

{JURIDIK_FORM}

{link_list("Läs på innan mötet", [
    ("Arrendeavtal för vindkraft – villkor och fallgropar", "/arrendeavtal-vindkraft"),
    ("Skillnaden mellan markarrende och intäktsdelning", "/skillnad-arrende-intaktsdelning"),
    ("Arrendekalkylator – räkna på vad villkoren är värda", "/arrendekalkylator"),
    ("Skatt på vindkraftsersättning", "/skatt-vindkraftersattning"),
    ("Markägarspåret – hela guiden", "/markagare"),
])}"""

JURIDIK_FAQ = [
    ("Behöver jag jurist för ett arrendeavtal för vindkraft?",
     "Det är starkt att rekommendera. Avtalet löper i 30–40 år, motparten skriver liknande avtal rutinmässigt och "
     "villkor som royaltybas, indexering och återställningsgaranti kan skilja miljonbelopp över avtalstiden."),
    ("Vad kostar juridisk hjälp med ett markavtal?",
     "En granskning av ett avtalsförslag ligger normalt på några timmars arbete, medan en fullständig förhandling "
     "kostar mer. Kostnaden ska alltid ställas mot avtalets totala värde – ofta flera miljoner kronor."),
    ("Kostar Vindkollens förmedling något?",
     "Nej, den är kostnadsfri för dig. Vindkollen är nystartat och nätverket av rådgivare byggs upp just nu, så vi "
     "kan inte lova hur snabbt vi kan förmedla en kontakt i ditt län. Har du bråttom bör du kontakta en "
     "fastighetsjurist eller lantbruksekonom direkt – vi ger inte juridisk rådgivning själva."),
    ("Kan flera markägare anlita samma rådgivare?",
     "Ja, och det är ofta klokt. Grannar som förhandlar samlat får både bättre villkor och lägre kostnad per fastighet, "
     "eftersom rådgivaren kan granska ett gemensamt avtalsupplägg."),
]


def build():
    page(
        filename="markagare.html",
        path="/markagare",
        nav_active="markagare",
        title="Vindkraft på min mark – arrende, ersättning och avtal 2026 | Vindkollen",
        description="Äger du mark där vindkraft kan byggas? Se arrendenivåer 2026, vad avtalet bör innehålla och få en kostnadsfri bedömning av din fastighet.",
        faq_name="Vindkraft på din mark – guide för markägare",
        hero=hero(
            badge="För dig som äger mark",
            h1_pre="Vad är din mark värd för",
            h1_accent="vindkraft?",
            lead="Ett arrendeavtal ger normalt 150 000–300 000 kronor per verk och år i 30–40 år. Räkna på nivåerna, förstå villkoren – och anmäl din fastighet för en oberoende bedömning.",
            primary=("Anmäl din mark", "#anmalan"),
            secondary=("Räkna på arrendet", "/arrendekalkylator"),
            trust=["100 % oberoende från kraftbolagen", "Kostnadsfritt för markägare", "Uppdaterad enligt prop. 2025/26:239"],
        ),
        body=MARKAGARE_BODY,
        faqs=MARKAGARE_FAQ,
    )

    page(
        filename="narboende.html",
        path="/narboende",
        nav_active="narboende",
        title="Närboende till vindkraft – din ersättning från 1 juli 2026 | Vindkollen",
        description="Bor du nära ett vindkraftverk? Så fungerar den skattefria intäktsdelningen från 1 juli 2026, hur mycket du kan få och hur du anmäler dig.",
        faq_name="Ersättning till närboende vid vindkraft",
        hero=hero(
            badge="Ny lag 1 juli 2026",
            h1_pre="Bor du nära vindkraft? Då kan du få",
            h1_accent="upp till 38 400 kr/år",
            lead="Från 1 juli 2026 får ägare av bostadshus inom nio verkshöjder en skattefri del av parkens intäkter. Så mycket blir det, så anmäler du dig – och så bevakar vi din adress åt dig.",
            primary=("Räkna ut min ersättning", "/kalkylator"),
            secondary=("Bevaka min adress", "#anmalan"),
            trust=["Skattefri ersättning", "Gäller nya parker från 1 juli 2026", "Oberoende av kraftbolagen"],
        ),
        body=NARBOENDE_BODY,
        faqs=NARBOENDE_FAQ,
    )

    page(
        filename="kommun.html",
        path="/kommun",
        nav_active="kommun",
        title="Vindkraft för kommuner – intäkter, veto och underlag 2026 | Vindkollen",
        description="Vad ger en vindkraftsetablering kommunen 2026? Fastighetsskatt, intäktsdelning och bygdepeng – med kostnadsfritt underlag för nämnd och fullmäktige.",
        faq_name="Vindkraft och kommunens ekonomi 2026",
        hero=hero(
            badge="För kommuner och organisationer",
            h1_pre="Vad ger vindkraften",
            h1_accent="er kommun?",
            lead="Fastighetsskatt, intäktsdelning och bygdepeng förändras 2026. Räkna på vad en etablering betyder för er ekonomi – med källor, oberoende från projektörerna.",
            primary=("Öppna kommun-dashboarden", "/kommun-dashboard"),
            secondary=("Ställ en fråga till oss", "#anmalan"),
            trust=["Oberoende från kraftbolagen", "Källhänvisat", "Kostnadsfritt"],
        ),
        body=KOMMUN_BODY,
        faqs=KOMMUN_FAQ,
    )

    page(
        filename="juridisk-hjalp-arrendeavtal.html",
        path="/juridisk-hjalp-arrendeavtal",
        nav_active="markagare",
        title="Juridisk hjälp inför arrendeavtal för vindkraft | Vindkollen",
        description="Har du fått ett avtalsförslag från en vindkraftsprojektör? Se de tio punkter en rådgivare granskar och bli kostnadsfritt matchad med en jurist i ditt län.",
        faq_name="Juridisk hjälp med arrendeavtal för vindkraft",
        hero=hero(
            badge="Avtal på bordet?",
            h1_pre="Skriv inte på förrän någon har",
            h1_accent="granskat avtalet",
            lead="Ett arrendeavtal för vindkraft binder marken i 30–40 år. Här är de tio punkter en rådgivare går igenom – och du kan anmäla intresse för kontakt med en oberoende jurist eller lantbruksekonom när vi har en på plats i ditt län.",
            primary=("Se de tio punkterna", "#punkterna"),
            secondary=("Anmäl intresse för rådgivare", "#anmalan"),
            trust=["Kostnadsfritt för dig", "Nätverket byggs upp nu", "Du väljer själv om du går vidare"],
        ),
        body=JURIDIK_BODY,
        faqs=JURIDIK_FAQ,
    )


if __name__ == "__main__":
    build()
