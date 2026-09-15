"""
Bygger Vindkollens sidor för förnybart bortom vindkraft.

Varför: markägaren som googlar "arrende solcellspark" eller "arrendera mark
batterilager" är exakt samma person som silon markagare redan är byggd för —
samma län, samma avtalsfrågor, samma motpart på andra sidan bordet. Nischen
"vad är min mark värd för energi" är bredare än vind, och den som äger hela
frågan äger också leadet oavsett vilken teknik som till slut byggs.

Sidorna genereras ur samma mall som silosidorna (build_silo_pages.page), så
nav, footer, formulärmotor och CTA-hierarki är identiska med resten av sajten.

    python scripts/bygg_fornybart_sidor.py

Skriptet SKRIVER ÖVER static/solpark-arrende-ersattning.html och
static/batterilager-arrende-ersattning.html i sin helhet.

Om siffrorna: nivåerna för sol- och batteriarrende samlas inte in offentligt
i Sverige på det sätt som vindens gör. Sidorna anger därför spann och säger
rakt ut att de är indikativa. Att uppfinna en precision som inte finns vore
att göra exakt det sajten kritiserar projektörerna för.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_silo_pages import (  # noqa: E402
    CHECK, FIELD, LABEL, cards, county_select, hero, link_list, page,
)


def formular(sid: str, rubrik: str, ingress: str) -> str:
    """Kvalificeringsformulär, låst till markägarsilon."""
    return f"""<section class="max-w-4xl mx-auto px-6 py-16" id="anmalan">
<div class="bg-gradient-to-br from-blue-900/40 to-emerald-900/25 border border-blue-500/30 rounded-3xl p-8 md:p-10">
<div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-semibold mb-4 uppercase tracking-wider">Kostnadsfritt · tjänsten byggs upp nu</div>
<h2 class="text-3xl font-bold text-white mb-3">{rubrik}</h2>
<p class="text-slate-300 mb-4 leading-relaxed">{ingress}</p>
<p class="text-slate-400 mb-8 text-sm leading-relaxed border-l-2 border-slate-700 pl-4">Ärligt om läget: Vindkollen är nystartat och vi har inga avtalade rådgivare eller projektörer på plats ännu. Vi sätter inget datum vi inte kan hålla — men vi läser varje inskickning.</p>
<form class="space-y-5" onsubmit="return false" data-vk-lead-form data-segment="markagare" data-source="{sid}">
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="{sid}-name">Namn</label>
<input class="{FIELD}" id="{sid}-name" name="name" placeholder="För- och efternamn" required type="text"/></div>
<div><label class="{LABEL}" for="{sid}-email">E-post</label>
<input class="{FIELD}" id="{sid}-email" name="email" placeholder="din@epost.se" required type="email"/></div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="{sid}-phone">Telefon <span class="text-slate-500 font-normal">(ger snabbare återkoppling)</span></label>
<input class="{FIELD}" id="{sid}-phone" name="phone" placeholder="07X-XXX XX XX" type="tel"/></div>
<div><label class="{LABEL}" for="{sid}-county">Län</label>
{county_select()}</div>
</div>
<div class="grid sm:grid-cols-2 gap-4">
<div><label class="{LABEL}" for="{sid}-hectares">Markareal (hektar)</label>
<input class="{FIELD}" id="{sid}-hectares" name="land_hectares" min="0" placeholder="t.ex. 25" step="1" type="number"/></div>
<div><label class="{LABEL}" for="{sid}-stage">Var i processen är du?</label>
<select class="{FIELD}" id="{sid}-stage" name="project_stage">
<option value="ingen_kontakt">Ingen kontakt än – undersöker möjligheten</option>
<option value="kontaktad">Kontaktad av exploatör</option>
<option value="forhandlar">Avtalsförslag på bordet / förhandlar nu</option>
<option value="har_avtal">Har redan avtal – vill se om det är marknadsmässigt</option>
</select></div>
</div>
<div><label class="{LABEL}" for="{sid}-address">Fastighetsbeteckning <span class="text-slate-500 font-normal">(valfritt)</span></label>
<input class="{FIELD}" id="{sid}-address" name="property_address" placeholder="t.ex. Gnarp 4:12" type="text"/></div>
<div><label class="{LABEL}" for="{sid}-message">Något mer vi bör veta? <span class="text-slate-500 font-normal">(valfritt)</span></label>
<textarea class="{FIELD}" id="{sid}-message" name="message" placeholder="t.ex. åkermark intill 130 kV-ledning, 2 km till fördelningsstation" rows="3"></textarea></div>
<div class="space-y-3 pt-2 border-t border-slate-700/60">
<label class="flex gap-3 text-sm text-slate-300"><input class="{CHECK}" name="wants_legal_help" type="checkbox"/>
<span>Jag vill ha kontakt med någon som kan granska arrendeavtalet</span></label>
<label class="flex gap-3 text-sm text-slate-300"><input class="{CHECK}" name="wants_projector_contact" type="checkbox"/>
<span>Jag är öppen för kontakt med exploatörer som söker mark</span></label>
<label class="flex gap-3 text-sm text-slate-300"><input class="{CHECK}" name="consent_partner_share" type="checkbox"/>
<span>Jag godkänner att Vindkollen får lämna mina uppgifter vidare till en rådgivare eller exploatör som passar mitt fall. Utan bock stannar uppgifterna hos oss.</span></label>
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
</section>"""


OSAKERHET = """<div class="max-w-3xl mt-10 p-5 rounded-2xl border border-amber-500/30 bg-amber-500/5">
<p class="text-sm text-amber-200/90 leading-relaxed"><b class="text-amber-300">Om siffrorna på den här sidan.</b>
Till skillnad från vindkraftens arrenden finns ingen offentlig insamling av vad
sol- och batteriarrenden faktiskt landar på i Sverige. Spannen här bygger på
vad som återkommer i publika avtalsdiskussioner och branschmaterial, och de
varierar kraftigt med nätanslutning, markkvalitet och vem motparten är. Läs dem
som storleksordning, inte som facit — och begär alltid att få se hur just ditt
bud är räknat.</p>
</div>"""


# ---------------------------------------------------------------------------
# Solpark
# ---------------------------------------------------------------------------

SOL_BODY = f"""<section class="max-w-5xl mx-auto px-6 py-14">
<h2 class="text-3xl font-bold text-white mb-4">Vad betalar en solpark för arrenderad mark?</h2>
<p class="text-slate-300 leading-relaxed mb-6 max-w-3xl">Solparksarrende betalas
nästan alltid per hektar och år, med en fast nivå i stället för vindkraftens
andel av produktionen. Det gör avtalet enklare att räkna på — men också
känsligare för inflation, eftersom uppsidan inte följer elpriset. Nivån sätts
i praktiken av tre saker: hur nära du ligger en anslutningspunkt med ledig
kapacitet, hur plan och sammanhängande marken är, och hur många andra markägare
i samma nätområde exploatören kan välja mellan i stället för dig.</p>
{cards([
    ("Vanligt spann", "8 000–20 000 kr", "per hektar och år för färdig park. Låga änden gäller sämre lägen och långa optionstider, höga änden mark nära anslutningspunkt."),
    ("Optionsperiod", "1–3 år vanligt", "Tiden innan spaden sätts i marken. Här betalas ofta bara en bråkdel av full nivå — och det är den delen som glöms bort i förhandlingen."),
    ("Avtalstid", "30–40 år", "Längre än de flesta vindavtal, eftersom solparker har lägre teknisk risk. Indexering blir därför viktigare, inte mindre viktig."),
])}
{OSAKERHET}
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-4">Varför skiljer sig buden så mycket mellan grannar?</h2>
<p class="text-slate-300 leading-relaxed mb-4 max-w-3xl">Det som avgör är sällan
marken i sig. Det är nätet. En solpark måste anslutas, och i stora delar av
Sverige är anslutningskapaciteten det som begränsar utbyggnaden — inte
tillgången på mark. Ligger din fastighet nära en station med ledig kapacitet
har du något som är svårt att ersätta, och då förändras förhandlingsläget helt.
Ligger du tre mil bort är du en av många möjliga, och budet speglar det.</p>
<ul class="space-y-3 text-slate-300 list-disc pl-6 max-w-3xl">
<li><b class="text-white">Avstånd till anslutningspunkt.</b> Varje kilometer kabel är en kostnad exploatören drar av från vad hen kan betala dig.</li>
<li><b class="text-white">Sammanhängande yta.</b> Ett fält på 30 hektar är värt mer per hektar än tre fält på tio.</li>
<li><b class="text-white">Markens alternativvärde.</b> Högavkastande åkermark har ett golv som skogsmark och betesmark saknar — och kommunen kan ha synpunkter på att den tas ur produktion.</li>
<li><b class="text-white">Vem som frågar.</b> En projektutvecklare som säljer vidare räknar annorlunda än en aktör som ska äga parken i 35 år.</li>
</ul>
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-4">Vad skiljer solarrende från vindarrende?</h2>
<div class="overflow-x-auto rounded-2xl border border-slate-800 bg-slate-900">
<table class="w-full text-left text-sm text-slate-400">
<thead class="bg-slate-800/50 text-xs uppercase text-slate-300">
<tr><th class="px-6 py-4" scope="col">Fråga</th><th class="px-6 py-4" scope="col">Vindkraft</th><th class="px-6 py-4 border-l border-slate-800" scope="col">Solpark</th></tr>
</thead>
<tbody class="divide-y divide-slate-800">
<tr><td class="px-6 py-4 font-medium text-white">Ersättningsmodell</td><td class="px-6 py-4">Andel av produktionens värde, ofta 2–5 %</td><td class="px-6 py-4 border-l border-slate-800">Fast belopp per hektar och år</td></tr>
<tr><td class="px-6 py-4 font-medium text-white">Följer elpriset</td><td class="px-6 py-4">Ja — uppsida när priset stiger</td><td class="px-6 py-4 border-l border-slate-800">Nej — därför är indexklausulen avgörande</td></tr>
<tr><td class="px-6 py-4 font-medium text-white">Yta som tas i anspråk</td><td class="px-6 py-4">Liten — fundament, vägar, kranplatser</td><td class="px-6 py-4 border-l border-slate-800">Hela arealen, under hela avtalstiden</td></tr>
<tr><td class="px-6 py-4 font-medium text-white">Fortsatt bruk</td><td class="px-6 py-4">Jord- och skogsbruk kan i stort fortsätta</td><td class="px-6 py-4 border-l border-slate-800">Begränsat — bete under panelerna förekommer</td></tr>
<tr><td class="px-6 py-4 font-medium text-white">Återställning</td><td class="px-6 py-4">Fundament och vägar</td><td class="px-6 py-4 border-l border-slate-800">Paneler, stativ, kablar, fundament — kräver samma säkerhet</td></tr>
</tbody>
</table>
</div>
<p class="text-slate-400 text-sm mt-4 max-w-3xl">Den viktigaste skillnaden är den
sista raden i praktiken: en solpark tar hela arealen. Ett vindkraftverk delar
marken med din verksamhet, en solpark ersätter den. Det ska synas i priset.</p>
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-4">Fem punkter att kräva innan du skriver på</h2>
<ol class="space-y-3 text-slate-300 list-decimal pl-6 max-w-3xl marker:text-blue-400 marker:font-bold">
<li><b class="text-white">Indexering på allt.</b> Fast belopp i 35 år utan KPI-uppräkning är i praktiken en successiv sänkning.</li>
<li><b class="text-white">Ersättning under optionstiden.</b> Marken är bunden från dag ett även om inget byggs. Det ska kosta.</li>
<li><b class="text-white">Bankgaranti för återställning.</b> Moderbolagsborgen från ett projektbolag som kan tömmas är ingen säkerhet.</li>
<li><b class="text-white">Villkor vid överlåtelse.</b> Solparker byter ägare ofta. Dina villkor ska följa med, och du bör få veta till vem.</li>
<li><b class="text-white">Vad som händer med dräneringen.</b> Skadad täckdikning på åkermark är en kostnad som överlever avtalet.</li>
</ol>
</section>"""

SOL_FAQ = [
    ("Vad är normalt arrende för en solcellspark per hektar?",
     "Publika diskussioner och branschmaterial pekar mot ungefär 8 000–20 000 kronor per hektar och år för en färdigbyggd park. Spannet är brett därför att nätanslutningen väger tyngre än marken: en fastighet nära en anslutningspunkt med ledig kapacitet betingar helt andra nivåer än en likvärdig fastighet några mil bort. Det finns ingen offentlig statistik som fastställer nivån, så behandla siffran som storleksordning."),
    ("Hur länge binds marken i ett solparksarrende?",
     "Vanligen 30–40 år, ofta med en optionsperiod på ett till tre år innan byggstart. Optionstiden är den del markägare oftast missar i förhandlingen: marken är bunden redan då, men ersättningen är ofta en bråkdel av full nivå."),
    ("Kan jag fortsätta bruka marken under panelerna?",
     "Bara i begränsad omfattning. Bete med får förekommer och kallas ibland agrivoltaik, men till skillnad från vindkraft tar en solpark i praktiken hela arealen i anspråk under hela avtalstiden. Det är därför ersättningen per hektar bör jämföras med markens alternativavkastning, inte med vindarrende."),
    ("Är solarrende bättre eller sämre än vindarrende?",
     "De är olika risker. Vindarrende är oftast en andel av produktionens värde och följer därmed elpriset uppåt, men förutsätter att verk faktiskt byggs på just din mark. Solarrende är ett fast belopp som är enklare att förutse men saknar uppsida — vilket gör indexklausulen till avtalets viktigaste rad."),
    ("Vem betalar om parken ska rivas?",
     "Det ska avtalet svara på, och svaret ska vara säkerställt med bankgaranti som räknas upp med index. Panelerna, stativen, kablarna och fundamenten ska bort, och kostnaden ligger decennier fram i tiden — långt efter att bolaget du skrev avtal med kan ha bytt ägare flera gånger."),
]


# ---------------------------------------------------------------------------
# Batterilager
# ---------------------------------------------------------------------------

BATT_BODY = f"""<section class="max-w-5xl mx-auto px-6 py-14">
<h2 class="text-3xl font-bold text-white mb-4">Vad betalar ett batterilager för mark?</h2>
<p class="text-slate-300 leading-relaxed mb-6 max-w-3xl">Ett batterilager tar
liten yta men kräver ett exceptionellt bra nätläge. Det gör prisbilden nästan
omvänd mot solparkens: arealen är närmast irrelevant, läget är allt. Ett par
hektar intill rätt station kan vara värt mer än trettio hektar en mil bort.
Därför anges ersättningen oftare som ett belopp per år och anläggning, eller
per installerad MW, än som ett hektarpris.</p>
{cards([
    ("Ytbehov", "1–3 hektar", "För ett lager i storleksordningen tiotals MW. Betydligt mindre än en solpark med motsvarande effekt."),
    ("Vad som avgör priset", "Nätläget", "Avstånd till station och tillgänglig anslutningskapacitet väger tyngre än allt annat tillsammans."),
    ("Avtalstid", "20–30 år", "Kortare än solparkens, eftersom batterier byts ut under anläggningens livstid."),
])}
{OSAKERHET}
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-4">Varför vill någon bygga batterilager just här?</h2>
<p class="text-slate-300 leading-relaxed mb-4 max-w-3xl">Batterilager tjänar
pengar på att elpriset varierar över dygnet och på att sälja stödtjänster till
Svenska kraftnät — alltså på att hålla frekvensen stabil. Båda affärerna kräver
snabb tillgång till nätet, inte stor yta. Det betyder att en markägare med rätt
läge förhandlar från en position som är ovanligt stark: exploatören har sällan
många alternativ inom samma nätområde.</p>
<ul class="space-y-3 text-slate-300 list-disc pl-6 max-w-3xl">
<li><b class="text-white">Närhet till fördelningsstation eller ställverk.</b> Det här är den enskilt viktigaste faktorn.</li>
<li><b class="text-white">Ledig anslutningskapacitet i området.</b> Utan den finns ingen affär, oavsett hur bra marken är.</li>
<li><b class="text-white">Framkomlighet.</b> Containrar ska fram, och de ska fram igen när batterierna byts.</li>
<li><b class="text-white">Elområde.</b> Prisvariationen skiljer sig mellan SE1–SE4, och därmed också affärens värde.</li>
</ul>
</section>

<section class="max-w-5xl mx-auto px-6 py-14 border-t border-slate-900">
<h2 class="text-3xl font-bold text-white mb-4">Det som är särskilt för batteriavtal</h2>
<ol class="space-y-3 text-slate-300 list-decimal pl-6 max-w-3xl marker:text-blue-400 marker:font-bold">
<li><b class="text-white">Brandskydd och försäkring.</b> Litiumbatterier ställer krav som ingen annan energianläggning på din mark gör. Vem bär ansvaret, och håller din egen försäkring?</li>
<li><b class="text-white">Utbyte av utrustning.</b> Batterier byts under avtalstiden. Räknas det som underhåll eller som ny anläggning — och påverkar det ersättningen?</li>
<li><b class="text-white">Buller från kylning.</b> Anläggningen låter, särskilt sommartid. Ligger den nära bostad är det en fråga att reglera i avtalet, inte efteråt.</li>
<li><b class="text-white">Återställning inklusive batterier.</b> Avfallshanteringen är dyrare än för paneler och fundament. Säkerheten ska täcka den.</li>
<li><b class="text-white">Kombination med annan produktion.</b> Ligger lagret bredvid en sol- eller vindpark ska avtalen läsas ihop, inte var för sig.</li>
</ol>
</section>"""

BATT_FAQ = [
    ("Vad får man i arrende för mark till ett batterilager?",
     "Ersättningen anges oftare per år och anläggning eller per installerad MW än per hektar, eftersom ytan är liten och läget avgörande. Det finns ingen offentlig svensk statistik över nivåerna. Det du kan göra i stället för att jämföra med ett riktvärde är att begära att få se hur budet är räknat, och att förhandla utifrån att en exploatör sällan har många alternativ inom samma nätområde."),
    ("Hur mycket mark krävs för ett batterilager?",
     "Ofta runt ett till tre hektar för ett lager i storleksordningen tiotals megawatt — betydligt mindre än en solpark med motsvarande effekt. Det är därför nätläget, inte arealen, sätter priset."),
    ("Vad är skillnaden mot att arrendera ut till solpark eller vindkraft?",
     "Vindkraft betalar oftast en andel av produktionens värde och delar marken med din verksamhet. Solpark betalar ett fast hektarpris och tar hela arealen. Batterilager tar mycket liten yta men kräver ett nätläge som få fastigheter har, vilket gör förhandlingsläget starkare för den som har det."),
    ("Vilka risker är särskilda för batterilager?",
     "Brandrisken i litiumbatterier ställer krav på skydd, avstånd och försäkring som inga andra energianläggningar på jordbruksmark gör. Kylsystemen låter. Och återställningen omfattar batteriavfall, som är dyrare att ta hand om än paneler och fundament. Alla tre bör vara reglerade i avtalet och säkerställda ekonomiskt."),
    ("Behöver ett batterilager bygglov eller tillstånd?",
     "Det beror på storlek och placering och prövas kommunalt, ofta som bygglov och i vissa fall med anmälan enligt miljöbalken. Kontrollera alltid med byggnadsnämnden i din kommun — och lägg in i avtalet vem som bär kostnaden och risken om tillståndet uteblir."),
]


def build():
    page(
        filename="solpark-arrende-ersattning.html",
        title="Solpark på min mark: arrende och ersättning 2026 | Vindkollen",
        description=("Vad betalar en solcellspark i arrende per hektar? Spann, "
                     "avtalstider och de fem punkter som avgör vad ditt avtal "
                     "faktiskt är värt. Oberoende genomgång."),
        path="/solpark-arrende-ersattning",
        nav_active="markagare",
        hero=hero(
            badge="Förnybart · markägare",
            h1_pre="Solpark på din mark:",
            h1_accent="vad är arrendet värt?",
            lead=("Solparker betalar per hektar och år, inte per producerad "
                  "kilowattimme. Det gör avtalet enklare att räkna på — och "
                  "gör indexklausulen till den rad som avgör vad du faktiskt "
                  "får ut över 35 år."),
            primary=("Få en bedömning av din mark", "#anmalan"),
            secondary=("Jämför med vindarrende", "/arrende-vindkraft-vs-solpark"),
            trust=["Oberoende", "Ingen kostnad", "Vi säljer inte dina uppgifter"],
        ),
        body=SOL_BODY + formular(
            "solpark_arrende",
            "Vad är din mark värd för solel?",
            ("Berätta var marken ligger och hur stor den är, så återkommer vi "
             "med vad som gäller i ditt län och vilka aktörer som söker mark "
             "där. Du binder dig inte till någonting."),
        ) + link_list("Läs vidare", [
            ("Vindkraft eller solpark — vad ger mest?", "/arrende-vindkraft-vs-solpark"),
            ("Batterilager på arrenderad mark", "/batterilager-arrende-ersattning"),
            ("Så granskar du ett arrendeavtal", "/juridisk-hjalp-arrendeavtal"),
            ("Räkna på vindarrende", "/arrendekalkylator"),
        ]),
        faqs=SOL_FAQ,
        faq_name="Solpark på min mark: arrende och ersättning",
    )

    page(
        filename="batterilager-arrende-ersattning.html",
        title="Batterilager på min mark: arrende och ersättning 2026 | Vindkollen",
        description=("Vad betalar ett batterilager för arrenderad mark? Ytbehov, "
                     "vad nätläget betyder för priset och de risker som är "
                     "särskilda för batteriavtal."),
        path="/batterilager-arrende-ersattning",
        nav_active="markagare",
        hero=hero(
            badge="Förnybart · markägare",
            h1_pre="Batterilager på din mark:",
            h1_accent="läget avgör priset",
            lead=("Ett batterilager tar ett par hektar men kräver ett nätläge "
                  "som få fastigheter har. Har du det förhandlar du från en "
                  "ovanligt stark position — exploatören har sällan många "
                  "alternativ i samma nätområde."),
            primary=("Få en bedömning av din mark", "#anmalan"),
            secondary=("Jämför med solpark", "/solpark-arrende-ersattning"),
            trust=["Oberoende", "Ingen kostnad", "Vi säljer inte dina uppgifter"],
        ),
        body=BATT_BODY + formular(
            "batterilager_arrende",
            "Har du ett nätläge som är värt något?",
            ("Berätta var marken ligger och vad som finns i närheten — station, "
             "ledning, befintlig park. Vi återkommer med vad som gäller i ditt "
             "elområde. Du binder dig inte till någonting."),
        ) + link_list("Läs vidare", [
            ("Solpark på din mark", "/solpark-arrende-ersattning"),
            ("Vindkraft eller solpark — vad ger mest?", "/arrende-vindkraft-vs-solpark"),
            ("Så granskar du ett arrendeavtal", "/juridisk-hjalp-arrendeavtal"),
            ("Ersättning för vindkraft", "/ersattning-for-vindkraft"),
        ]),
        faqs=BATT_FAQ,
        faq_name="Batterilager på min mark: arrende och ersättning",
    )


if __name__ == "__main__":
    build()
