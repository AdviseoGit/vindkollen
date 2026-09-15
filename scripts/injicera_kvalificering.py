"""
Ger varje sida en väg till ett kvalificerat lead.

Bakgrunden: sajtens trafik och sajtens leadmaskin satt på olika sidor. De sju
silosidorna hade ett formulär som poängsätter, härleder elområde och matchar
mot partnerregistret. De övriga 36 hade antingen ett nyhetsbrevsfält som bara
sparar en mejladress, eller ingenting alls — och det var där trafiken låg.
/ersattning-for-vindkraft ensam stod för 39 % av sajtens klick och kunde inte
producera ett enda förmedlingsbart lead.

Skriptet lägger in ett gemensamt kvalificeringsblock strax före </main> på de
sidor som saknar ett. Blocket är samma komponent överallt, så designen hålls
enhetlig, och det använder vk-silo.js som redan finns: segment-radion styr
vilka fält som visas, länet härleder elområde, och GA4 får en generate_lead
per silo.

Nyhetsbrevsrutorna mitt i artiklarna lämnas orörda — de är ett annat, lättare
erbjudande och de fungerar.

    python scripts/injicera_kvalificering.py            # visa vad som skulle ändras
    python scripts/injicera_kvalificering.py --skarpt   # skriv
"""

import argparse
import glob
import os
import re
import sys

ROT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MARKOR = "data-vk-kvalificering"

# Sidor som medvetet står utanför.
# om-sajten är AI-transparenssidan — den ska förklara vem som driver sajten,
# inte sälja. kalkylator har redan sin egen tratt (/api/lead/report), som
# poängsätter och matchar; ett andra stort formulär där är CTA-överbelastning
# på den enda sida som redan konverterar.
UNDANTAG = {"om-sajten.html", "kalkylator.html"}

LAN = [
    "Blekinge", "Dalarna", "Gotland", "Gävleborg", "Halland", "Jämtland",
    "Jönköping", "Kalmar", "Kronoberg", "Norrbotten", "Skåne", "Stockholm",
    "Södermanland", "Uppsala", "Värmland", "Västerbotten", "Västernorrland",
    "Västmanland", "Västra Götaland", "Örebro", "Östergötland",
]

INPUT = ("w-full bg-slate-950 border border-slate-700 px-4 py-3 rounded-xl "
         "outline-none focus:border-blue-500 text-white placeholder-slate-500")
LABEL = "block text-sm font-semibold text-slate-300 mb-2"


def _lanval(prefix: str) -> str:
    rader = "\n".join(f'<option value="{l}">{l}</option>' for l in LAN)
    return (f'<select class="{INPUT}" id="{prefix}-county" name="county" required>'
            f'<option value="">Välj län…</option>{rader}</select>')


def block(sid: str) -> str:
    """Kvalificeringsblocket. `sid` gör id:n unika om en sida får två block."""
    p = f"vk-{sid}"
    return f"""
<section class="max-w-4xl mx-auto px-6 py-16" {MARKOR}>
<div class="bg-gradient-to-br from-blue-900/40 to-emerald-900/25 border border-blue-500/30 rounded-3xl p-8 md:p-10">
<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-semibold mb-4 uppercase tracking-wider">Kostnadsfritt · tjänsten byggs upp nu</div>
<h2 class="text-3xl font-bold text-white mb-3">Vad gäller i ditt fall?</h2>
<p class="text-slate-300 mb-4 leading-relaxed">Ersättning avgörs av var du bor, hur nära verken står och om det är din mark. Berätta kort om din situation, så återkommer vi med vad som gäller just där — och vilka aktörer som är aktiva i ditt län.</p>
<p class="text-slate-400 mb-8 text-sm leading-relaxed border-l-2 border-slate-700 pl-4">Ärligt om läget: Vindkollen är nystartat och vi har inga avtalade rådgivare eller projektörer på plats ännu. Vi sätter inget datum vi inte kan hålla — men vi läser varje inskickning.</p>
<form class="space-y-5" onsubmit="return false" data-vk-lead-form data-source="{sid}_kvalificering">
<fieldset>
<legend class="{LABEL}">Vem är du?</legend>
<div class="grid sm:grid-cols-3 gap-3">
<label class="flex items-center gap-3 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 cursor-pointer hover:border-blue-500 transition-colors"><input class="h-4 w-4 text-blue-600 focus:ring-blue-500" name="segment" type="radio" value="markagare" required/><span class="text-sm text-slate-200">Markägare</span></label>
<label class="flex items-center gap-3 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 cursor-pointer hover:border-blue-500 transition-colors"><input class="h-4 w-4 text-blue-600 focus:ring-blue-500" name="segment" type="radio" value="narboende"/><span class="text-sm text-slate-200">Närboende</span></label>
<label class="flex items-center gap-3 bg-slate-950 border border-slate-700 rounded-xl px-4 py-3 cursor-pointer hover:border-blue-500 transition-colors"><input class="h-4 w-4 text-blue-600 focus:ring-blue-500" name="segment" type="radio" value="kommun"/><span class="text-sm text-slate-200">Kommun</span></label>
</div>
</fieldset>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="{p}-name">Namn</label>
<input class="{INPUT}" id="{p}-name" name="name" placeholder="För- och efternamn" required type="text"/></div>
<div><label class="{LABEL}" for="{p}-email">E-post</label>
<input class="{INPUT}" id="{p}-email" name="email" placeholder="din@epost.se" required type="email"/></div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="{p}-phone">Telefon <span class="text-slate-500 font-normal">(ger snabbare återkoppling)</span></label>
<input class="{INPUT}" id="{p}-phone" name="phone" placeholder="07X-XXX XX XX" type="tel"/></div>
<div><label class="{LABEL}" for="{p}-county">Län</label>
{_lanval(p)}</div>
</div>

<div class="grid sm:grid-cols-2 gap-4" data-vk-show-when="segment=markagare" hidden>
<div><label class="{LABEL}" for="{p}-hectares">Markareal (hektar)</label>
<input class="{INPUT}" id="{p}-hectares" name="land_hectares" min="0" placeholder="t.ex. 120" step="1" type="number"/></div>
<div><label class="{LABEL}" for="{p}-stage">Var i processen är du?</label>
<select class="{INPUT}" id="{p}-stage" name="project_stage">
<option value="ingen_kontakt">Ingen kontakt än – undersöker möjligheten</option>
<option value="kontaktad">Kontaktad av projektör</option>
<option value="forhandlar">Avtalsförslag på bordet / förhandlar nu</option>
<option value="har_avtal">Har redan avtal – vill se om det är marknadsmässigt</option>
</select></div>
</div>
<div data-vk-show-when="segment=markagare" hidden>
<label class="{LABEL}" for="{p}-address">Fastighetsbeteckning <span class="text-slate-500 font-normal">(valfritt)</span></label>
<input class="{INPUT}" id="{p}-address" name="property_address" placeholder="t.ex. Gnarp 4:12" type="text"/></div>

<div data-vk-show-when="segment=narboende" hidden>
<label class="{LABEL}" for="{p}-distance">Avstånd till närmaste verk (meter)</label>
<input class="{INPUT}" id="{p}-distance" name="distance_m" min="0" placeholder="t.ex. 900" step="10" type="number"/></div>

<div data-vk-show-when="segment=kommun" hidden>
<label class="{LABEL}" for="{p}-municipality">Kommun</label>
<input class="{INPUT}" id="{p}-municipality" name="municipality" placeholder="t.ex. Ånge" type="text"/></div>

<div><label class="{LABEL}" for="{p}-message">Något mer vi bör veta? <span class="text-slate-500 font-normal">(valfritt)</span></label>
<textarea class="{INPUT}" id="{p}-message" name="message" placeholder="t.ex. avtalsförslag på bordet, eller tre verk planerade 800 m bort" rows="3"></textarea></div>

<div class="space-y-3 pt-2 border-t border-slate-700/60">
<label class="flex gap-3 text-sm text-slate-300"><input class="mt-1 h-5 w-5 rounded border-slate-600 bg-slate-950 text-blue-600 focus:ring-blue-500" name="wants_legal_help" type="checkbox"/>
<span>Jag vill ha kontakt med någon som kan granska avtal och ersättningsnivåer</span></label>
<label class="flex gap-3 text-sm text-slate-300" data-vk-show-when="segment=markagare" hidden><input class="mt-1 h-5 w-5 rounded border-slate-600 bg-slate-950 text-blue-600 focus:ring-blue-500" name="wants_projector_contact" type="checkbox"/>
<span>Jag är öppen för kontakt med projektörer som söker mark</span></label>
<label class="flex gap-3 text-sm text-slate-300"><input class="mt-1 h-5 w-5 rounded border-slate-600 bg-slate-950 text-blue-600 focus:ring-blue-500" name="consent_partner_share" type="checkbox"/>
<span>Jag godkänner att Vindkollen får lämna mina uppgifter vidare till en rådgivare eller projektör som passar mitt fall. Utan bock stannar uppgifterna hos oss.</span></label>
</div>
<p class="text-sm text-red-400" data-vk-error hidden></p>
<button class="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl transition-colors" type="submit">Skicka in</button>
<p class="text-xs text-slate-500 text-center">Vi säljer aldrig dina uppgifter. Du kan när som helst be oss radera dem.</p>
</form>
<div class="text-center py-6" data-vk-success hidden>
<p class="text-2xl font-bold text-emerald-400 mb-2">Tack — vi har din inskickning.</p>
<p class="text-slate-300">Vi hör av oss med vad som gäller i ditt län. Har du bockat i att vi får förmedla uppgifterna berättar vi alltid vem som fått dem innan något händer.</p>
</div>
</div>
</section>
"""


def har_kvalificering(html: str) -> bool:
    return MARKOR in html or "data-vk-lead-form" in html


def sid_for(sokvag: str) -> str:
    stam = os.path.splitext(os.path.basename(sokvag))[0]
    return re.sub(r"[^a-z0-9]+", "_", stam.lower()).strip("_")[:40] or "sida"


def behandla(sokvag: str, skarpt: bool):
    if os.path.basename(sokvag) in UNDANTAG:
        return []

    html = open(sokvag, encoding="utf-8").read()
    andringar = []

    if har_kvalificering(html):
        return andringar

    if "</main>" not in html:
        return ["saknar </main> — hoppas över"]

    ny = html.replace("</main>", block(sid_for(sokvag)) + "</main>", 1)
    andringar.append("kvalificeringsblock infogat")

    if "/static/js/vk-silo.js" not in ny:
        ny = ny.replace("</body>", '<script src="/static/js/vk-silo.js"></script>\n</body>', 1)
        andringar.append("vk-silo.js laddas nu")

    if skarpt and andringar:
        open(sokvag, "w", encoding="utf-8").write(ny)
    return andringar


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skarpt", action="store_true", help="skriv ändringarna")
    args = ap.parse_args()

    sidor = sorted(glob.glob(os.path.join(ROT, "static", "**", "*.html"), recursive=True))
    rorda = 0
    for s in sidor:
        andringar = behandla(s, args.skarpt)
        if andringar:
            rorda += 1
            print(os.path.relpath(s, ROT))
            for a in andringar:
                print("    ·", a)

    verb = "ändrade" if args.skarpt else "skulle ändra"
    print(f"\n{verb} {rorda} av {len(sidor)} sidor")
    if not args.skarpt and rorda:
        print("Kör med --skarpt för att skriva.")


if __name__ == "__main__":
    sys.exit(main())
