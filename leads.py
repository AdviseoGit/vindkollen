"""
Lead-silos för Vindkollen.

Sajten har tre publiker med helt olika kommersiellt värde:

  markagare  — äger mark där verk kan stå. "Guld-lead": ett arrendeavtal är värt
               miljonbelopp för projektören, och markägaren behöver ofta juridisk
               hjälp inför förhandlingen.
  narboende  — bor inom nio verkshöjder och omfattas av intäktsdelningen från
               1 juli 2026. Hög volym, lägre värde per lead, men kan bli
               juridik-lead vid inlösen/värdeminskning.
  kommun     — kommuner och organisationer som utvärderar etableringar.
               B2B-rådgivning, långa cykler.

Modulen håller silo-definitionerna på ett ställe: etiketter, giltiga värden,
län → elområde, poängsättning och de mejl som går ut. main.py gör bara
persistens och HTTP.
"""

from typing import Optional, Tuple

# ---------------------------------------------------------------------------
# Silos
# ---------------------------------------------------------------------------

SEGMENTS = {
    "markagare": {
        "label": "Markägare",
        "beskrivning": "Äger mark där vindkraftverk kan placeras",
        "base_score": 40,
        "landing": "/markagare",
    },
    "narboende": {
        "label": "Närboende",
        "beskrivning": "Bor nära en planerad eller befintlig park",
        "base_score": 12,
        "landing": "/narboende",
    },
    "kommun": {
        "label": "Kommun/organisation",
        "beskrivning": "Utvärderar etableringar eller intäkter för kommunen",
        "base_score": 28,
        "landing": "/kommun",
    },
    "ovrig": {
        "label": "Övrig",
        "beskrivning": "Annan roll (projektör, rådgivare, journalist m.m.)",
        "base_score": 5,
        "landing": "/",
    },
}

DEFAULT_SEGMENT = "ovrig"

# Var i processen leadet befinner sig. Avgör hur "het" den är för en köpare.
PROJECT_STAGES = {
    "ingen_kontakt": {"label": "Ingen kontakt än – undersöker möjligheten", "score": 6},
    "kontaktad": {"label": "Kontaktad av projektör", "score": 18},
    "forhandlar": {"label": "Avtalsförslag på bordet / förhandlar nu", "score": 28},
    "har_avtal": {"label": "Har redan avtal – vill se om det är marknadsmässigt", "score": 14},
    "byggd_park": {"label": "Park finns redan i närheten", "score": 8},
}

# Tidshorisont för beslut.
TIMEFRAMES = {
    "nu": {"label": "Inom 3 månader", "score": 15},
    "i_ar": {"label": "Inom ett år", "score": 8},
    "senare": {"label": "Längre fram / bevakar bara", "score": 2},
}

# ---------------------------------------------------------------------------
# Geografi — grunden för exklusivitet per region
# ---------------------------------------------------------------------------
#
# Vindkraftsetableringar är geografiskt bundna. Genom att alltid fånga län +
# elområde kan samma lead-flöde säljas till flera icke-konkurrerande köpare
# (t.ex. en projektör i SE2 och en i SE4) utan krock.
#
# Elområdesgränserna följer inte länsgränser exakt. Kartan nedan är en
# förifyllning som användaren kan ändra i formuläret — inte en sanning.

COUNTY_TO_ELAREA = {
    "Norrbotten": "SE1",
    "Västerbotten": "SE2",
    "Jämtland": "SE2",
    "Västernorrland": "SE2",
    "Gävleborg": "SE3",
    "Dalarna": "SE3",
    "Värmland": "SE3",
    "Örebro": "SE3",
    "Västmanland": "SE3",
    "Uppsala": "SE3",
    "Stockholm": "SE3",
    "Södermanland": "SE3",
    "Östergötland": "SE3",
    "Västra Götaland": "SE3",
    "Jönköping": "SE3",
    "Gotland": "SE3",
    "Halland": "SE3",
    "Kalmar": "SE4",
    "Kronoberg": "SE4",
    "Blekinge": "SE4",
    "Skåne": "SE4",
}

COUNTIES = list(COUNTY_TO_ELAREA.keys())

ELAREAS = ("SE1", "SE2", "SE3", "SE4")


def elarea_for_county(county: Optional[str]) -> Optional[str]:
    """Föreslå elområde utifrån län. Returnerar None för okänt län."""
    if not county:
        return None
    return COUNTY_TO_ELAREA.get(county.strip())


def normalise_segment(segment: Optional[str]) -> str:
    seg = (segment or "").strip().lower()
    return seg if seg in SEGMENTS else DEFAULT_SEGMENT


def segment_label(segment: Optional[str]) -> str:
    return SEGMENTS[normalise_segment(segment)]["label"]


# ---------------------------------------------------------------------------
# Poängsättning
# ---------------------------------------------------------------------------


def score_lead(d: dict) -> Tuple[int, str]:
    """Poängsätt ett lead 0–100 och sätt en tier (A/B/C).

    Poängen speglar hur mycket en köpare (projektör, jurist, rådgivare) rimligen
    betalar: silo först, sedan hur nära ett faktiskt avtal personen står, hur
    mycket mark de har och om de faktiskt vill bli kontaktade.
    """
    segment = normalise_segment(d.get("segment"))
    score = SEGMENTS[segment]["base_score"]

    stage = (d.get("project_stage") or "").strip().lower()
    if stage in PROJECT_STAGES:
        score += PROJECT_STAGES[stage]["score"]

    timeframe = (d.get("timeframe") or "").strip().lower()
    if timeframe in TIMEFRAMES:
        score += TIMEFRAMES[timeframe]["score"]

    # Markareal säger direkt hur många verk som får plats. Under ~10 ha är det
    # sällan aktuellt med egen etablering.
    hectares = d.get("land_hectares")
    if isinstance(hectares, (int, float)):
        if hectares >= 200:
            score += 20
        elif hectares >= 50:
            score += 14
        elif hectares >= 10:
            score += 7

    # Ett lead som aktivt ber om juridisk hjälp eller projektörskontakt är värt
    # långt mer än ett som bara laddar ner en guide.
    if d.get("wants_legal_help"):
        score += 12
    if d.get("wants_projector_contact"):
        score += 15

    # Kontaktbarhet.
    if (d.get("phone") or "").strip():
        score += 6
    if (d.get("property_address") or "").strip():
        score += 4
    if (d.get("county") or "").strip():
        score += 3

    score = max(0, min(100, int(round(score))))
    return score, tier_for_score(score)


def tier_for_score(score: int) -> str:
    if score >= 70:
        return "A"
    if score >= 45:
        return "B"
    return "C"


TIER_LABELS = {
    "A": "A – het, kontakta idag",
    "B": "B – kvalificerad, följ upp inom veckan",
    "C": "C – nurture via nyhetsbrev",
}


# ---------------------------------------------------------------------------
# Mejl
# ---------------------------------------------------------------------------

_BRAND = "#105e4e"


def _row(label: str, value) -> str:
    shown = value if value not in (None, "", False) else "—"
    if value is True:
        shown = "Ja"
    return (
        f'<tr><td style="padding:5px 12px;color:#64748b;white-space:nowrap">{label}</td>'
        f'<td style="padding:5px 12px;font-weight:600">{shown}</td></tr>'
    )


def build_owner_email_html(d: dict, score: int, tier: str) -> str:
    """Notis till oss. Silon och poängen står överst — det är det som avgör
    om leadet ska ringas idag eller gå till nurture."""
    segment = normalise_segment(d.get("segment"))
    stage = PROJECT_STAGES.get((d.get("project_stage") or "").lower(), {}).get("label")
    timeframe = TIMEFRAMES.get((d.get("timeframe") or "").lower(), {}).get("label")
    tier_colour = {"A": "#b91c1c", "B": "#b45309", "C": "#475569"}[tier]

    rows = "".join([
        _row("Silo", SEGMENTS[segment]["label"]),
        _row("Namn", d.get("name")),
        _row("E-post", d.get("email")),
        _row("Telefon", d.get("phone")),
        _row("Län", d.get("county")),
        _row("Elområde", d.get("elarea")),
        _row("Kommun", d.get("municipality")),
        _row("Organisation", d.get("organisation")),
        _row("Roll", d.get("role")),
        _row("Fastighet", d.get("property_address")),
        _row("Markareal (ha)", d.get("land_hectares")),
        _row("Status i processen", stage),
        _row("Tidshorisont", timeframe),
        _row("Vill ha juridisk hjälp", d.get("wants_legal_help")),
        _row("Vill matchas med projektör", d.get("wants_projector_contact")),
        _row("Samtycker till partnerdelning", d.get("consent_partner_share")),
        _row("Avstånd (m)", d.get("distance_m")),
        _row("Uppskattad ersättning (kr/år)", d.get("estimated_compensation_sek")),
        _row("Källa", d.get("source")),
    ])

    return f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:600px;color:#1e293b">
  <div style="background:{tier_colour};color:#fff;padding:16px 20px;border-radius:12px 12px 0 0">
    <div style="font-size:13px;letter-spacing:.08em;text-transform:uppercase;opacity:.85">
      Nytt lead · {SEGMENTS[segment]['label']}
    </div>
    <div style="font-size:22px;font-weight:800;margin-top:4px">
      {TIER_LABELS[tier]} · {score}/100
    </div>
  </div>
  <div style="border:1px solid #e2e8f0;border-top:0;border-radius:0 0 12px 12px;padding:16px 8px">
    <table style="border-collapse:collapse;font-size:14px;width:100%">{rows}</table>
  </div>
</div>"""


_SEGMENT_INTRO = {
    "markagare": (
        "Som markägare sitter du på den del av affären som projektören behöver mest — marken. "
        "Arrendenivåer, royaltysatser och avtalsvillkor skiljer sig kraftigt mellan bolag, och "
        "de flesta avtal löper i 30–40 år.",
        [
            ("Arrendekalkylator – räkna på royalty och minimiarrende",
             "https://vindkoll.se/arrendekalkylator"),
            ("Arrendeavtal för vindkraft – villkor och fallgropar",
             "https://vindkoll.se/arrendeavtal-vindkraft"),
            ("Skatt på arrende- och royaltyintäkter",
             "https://vindkoll.se/skatt-vindkraftersattning"),
        ],
    ),
    "narboende": (
        "Från 1 juli 2026 får ägare av bostadshus inom nio verkshöjder en skattefri del av parkens "
        "intäkter. Hur mycket beror på avståndet – trappstegsmodellen går från 2,5 ‰ till 0,5 ‰.",
        [
            ("Ersättningskalkylator – räkna på din bostad",
             "https://vindkoll.se/kalkylator"),
            ("Nio verkshöjder – så dras gränsen",
             "https://vindkoll.se/nio-verkshojder-ersattning"),
            ("Påverkar vindkraft fastighetsvärdet?",
             "https://vindkoll.se/paverkar-vindkraft-fastighetsvarde"),
        ],
    ),
    "kommun": (
        "Den nya lagstiftningen förändrar både kommunens intäkter och förutsättningarna för det "
        "kommunala vetot. Vi sammanställer underlaget så att ni kan räkna på en etablering innan "
        "ni tar ställning.",
        [
            ("Kommun-dashboard – intäkter per etablering",
             "https://vindkoll.se/kommun-dashboard"),
            ("Kommunersättning och fastighetsskatt 2026",
             "https://vindkoll.se/kommunersattning-vindkraft-2026"),
            ("Bygdepeng – regler och fördelning",
             "https://vindkoll.se/bygdepeng-vindkraft-regler-2026"),
        ],
    ),
    "ovrig": (
        "Vi bevakar lagen om intäktsdelning, arrendenivåer och kommunernas ersättningar löpande.",
        [
            ("Ersättningskalkylator", "https://vindkoll.se/kalkylator"),
            ("Arrendekalkylator", "https://vindkoll.se/arrendekalkylator"),
        ],
    ),
}


def build_welcome_email_html(d: dict) -> str:
    """Bekräftelse till leadet — innehållet följer silon, inte en generisk mall."""
    segment = normalise_segment(d.get("segment"))
    name = (d.get("name") or "").strip()
    hej = f"Hej {name}," if name else "Hej,"
    intro, links = _SEGMENT_INTRO[segment]
    link_html = "".join(
        f'<li style="margin-bottom:6px"><a href="{url}" style="color:{_BRAND}">{title}</a></li>'
        for title, url in links
    )

    # Vi har inga avtalade partner ännu. Bekräftelsen ska säga det rakt ut —
    # ett löfte vi inte kan hålla kostar mer än det lead det fångar.
    legal_block = ""
    if d.get("wants_legal_help"):
        legal_block = (
            '<p style="background:#fffbeb;border:1px solid #fde68a;border-radius:10px;'
            'padding:12px 14px">Du har markerat att du vill ha kontakt med en jurist som kan '
            'markavtal. Vi bygger upp det nätverket just nu och har ingen avtalad rådgivare i '
            'varje län ännu, så vi kan inte lova när vi hör av oss – bara att vi gör det när vi '
            'har någon att förmedla till. Har du bråttom: vänta inte på oss, kontakta en '
            'advokatbyrå med fastighetsrätt eller en lantbruksekonom direkt.</p>'
        )

    projector_block = ""
    if d.get("wants_projector_contact"):
        projector_block = (
            '<p style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:10px;'
            'padding:12px 14px">Du har sagt ja till kontakt med projektörer i ditt område. Vi '
            'delar aldrig dina uppgifter innan du bekräftat vilken aktör du vill prata med, och '
            'vi hör av oss först när vi har någon att förmedla till.</p>'
        )

    return f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:560px;margin:auto;color:#1e293b">
  <div style="background:{_BRAND};color:#fff;padding:22px 24px;border-radius:12px 12px 0 0">
    <h2 style="margin:0;font-size:20px">Tack – vi har tagit emot dina uppgifter</h2>
    <div style="opacity:.85;font-size:13px;margin-top:4px">
      Ditt underlag: {SEGMENTS[segment]['label']}
    </div>
  </div>
  <div style="border:1px solid #e2e8f0;border-top:0;border-radius:0 0 12px 12px;padding:24px">
    <p>{hej}</p>
    <p>{intro}</p>
    {legal_block}
    {projector_block}
    <p style="margin:18px 0 6px"><b>Börja här:</b></p>
    <ul style="margin:0 0 8px;padding-left:20px;line-height:1.7">{link_html}</ul>
    <p>Vi läser varje inskickning och hör av oss när vi har något konkret för din situation.
       Svara gärna på det här mejlet om du vill beskriva läget närmare – det är oftast den
       snabbaste vägen till ett svar.</p>
    <p style="margin-top:22px">Vänliga hälsningar,<br><b>Vindkollen</b><br>
       <a href="https://vindkoll.se" style="color:{_BRAND}">vindkoll.se</a></p>
    <p style="font-size:11px;color:#94a3b8;margin-top:22px">Du får det här mejlet för att du fyllde
       i ett formulär på vindkoll.se. Vill du bli borttagen, svara på mejlet.</p>
  </div>
</div>"""
