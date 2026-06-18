"""
Vindkollen lead magnet — the personalised "marknadsrapport" the kalkylator
page promises ("vi skickar en skraddarsydd PDF-rapport till din inbox").

This is a multi-page, designed PDF that actually delivers on the four promises
made on the kalkylator page:
  1. Oversikt + so hittar du planerade/beviljade vindkraftsparker nara dig
  2. Genomsnittliga arrenden och royaltynivaer i din region
  3. Checklista for forhandlingar med vindkraftsbolag
  4. (veckobrev — handled via subscription; flagged in the report)

Honesty guardrail: we never invent specific named parks/MW for a kommun. We
give accurate regional economics + a guided path to Vindbrukskollen (the
official Lansstyrelsen/Energimyndigheten registry) for the exact local parks.

fpdf2 core fonts use latin-1, which covers a/ä/ö. _s() keeps those and only
strips characters latin-1 cannot represent (em-dash, smart quotes, ...).
"""
from datetime import datetime

# Brand palette
CLAY = (16, 94, 78)       # vindkollen green (primary)
CLAY_DK = (9, 61, 50)     # darker green
ACCENT = (217, 119, 6)    # amber accent
INK = (30, 41, 59)        # near-black text
MUTED = (100, 116, 139)   # slate
LINE = (203, 213, 225)    # light border
WASH = (236, 253, 245)    # very light green row wash
WASH2 = (248, 250, 252)   # alt row wash

# --- Region economics (kept consistent with static/kommun-dashboard.html) ---
FULL_LOAD_HOURS = 3200
ASSUMED_MW_PER_TURBINE = 6.0
ARRENDE_PCT = (0.03, 0.05)   # typical landowner royalty band
BYGDEPENG_PCT = 0.0075

ELOMRADE = {
    "SE1": {"namn": "Norra Sverige (Luleå)", "pris_ore": 30,
            "kontext": "Lägst elpriser i landet, men mycket landbaserad vindkraft byggs här "
                       "tack vare goda vindlägen och gott om mark."},
    "SE2": {"namn": "Norra Mellansverige (Sundsvall)", "pris_ore": 35,
            "kontext": "Sveriges mest expansiva landbaserade vindkraftsregion - här byggs "
                       "merparten av de stora nya parkerna."},
    "SE3": {"namn": "Södra Mellansverige (Stockholm)", "pris_ore": 45,
            "kontext": "Hög efterfrågan och stigande utbyggnad; både landbaserat och planerad "
                       "havsbaserad vindkraft längs ostkusten."},
    "SE4": {"namn": "Södra Sverige (Malmö)", "pris_ore": 60,
            "kontext": "Högst elpriser i landet, vilket gör ersättningar och arrenden mest "
                       "värdefulla här. Stora havsbaserade projekt planeras i söder."},
}

CHECKLIST = [
    ("Royalty, inte bara fast avgift", "Begär att arrendet baseras på faktisk produktion eller "
     "intäkt (en procentsats), så att din ersättning följer med när elpriset stiger - inte bara "
     "ett fast belopp som urholkas av inflationen."),
    ("Garanterat golv per verk", "Förhandla en minimigaranti per verk och år oavsett elpris och "
     "vindläge, så att du har en trygg basnivå även svaga år."),
    ("Ersättning för intrång separat", "Vägar, kabeldragning, transformatorstation och övrigt "
     "markintrång ska ersättas separat - utöver själva arrendet."),
    ("Indexuppräkning", "Kräv att fasta belopp räknas upp årligen med index (KPI), annars tappar "
     "de värde över avtalets 25-35 år."),
    ("Återställningsgaranti", "Säkra en bankgaranti för nedmontering och återställning av marken "
     "när parken avvecklas - så kostnaden inte hamnar på dig."),
    ("Betalt för optionstiden", "Projektören vill ofta ha en option i flera år innan bygget. "
     "Tidsbegränsa den och få betalt för själva optionsperioden."),
    ("Villkor vid ägarbyte", "Reglera vad som händer om projektet säljs vidare - dina villkor ska "
     "följa med till en ny ägare."),
    ("Oberoende rådgivning", "Ta in egen juridisk OCH ekonomisk rådgivning innan du skriver på. "
     "Kostnaden är liten mot vad avtalet är värt över decennier."),
    ("Jämför flera bud", "Är marken attraktiv? Låt gärna fler än en projektör lämna bud - "
     "konkurrens höjer din ersättning."),
    ("Tänk på grannarna", "Reglera ersättning/dialog med närboende tidigt - det minskar risken "
     "för överklaganden som försenar hela projektet (och din intäkt)."),
]


def _s(t):
    """Make text safe for fpdf2 core (latin-1) fonts. å/ä/ö survive; only chars
    outside latin-1 (em-dash, smart quotes, ...) are normalised/stripped."""
    t = str(t)
    for a, b in [("—", "-"), ("–", "-"), ("’", "'"), ("‘", "'"),
                 ("“", '"'), ("”", '"'), ("…", "..."), (" ", " ")]:
        t = t.replace(a, b)
    return t.encode("latin-1", "replace").decode("latin-1")


def _sek(v):
    try:
        return f"{int(round(float(v))):,}".replace(",", " ") + " kr"
    except Exception:
        return "-"


def _num(v, suffix=""):
    try:
        if v is None:
            return "-"
        n = float(v)
        s = f"{int(n)}" if n == int(n) else f"{n:g}"
        return s + suffix
    except Exception:
        return "-"


class VindReport:
    """Thin wrapper around FPDF with branded section/table/callout helpers."""

    MARGIN = 14
    WIDTH = 210 - 2 * 14  # 182mm content width

    def __init__(self):
        from fpdf import FPDF  # lazy: a missing fpdf2 must never crash app boot
        self.pdf = FPDF(format="A4")
        self.pdf.set_auto_page_break(auto=True, margin=20)
        self.pdf.set_margins(self.MARGIN, self.MARGIN, self.MARGIN)

    def section(self, title, subtitle=None):
        pdf = self.pdf
        if pdf.get_y() > 245:
            pdf.add_page()
        pdf.ln(3)
        y = pdf.get_y()
        pdf.set_fill_color(*CLAY)
        pdf.rect(self.MARGIN, y, self.WIDTH, 9, "F")
        pdf.set_xy(self.MARGIN + 3, y + 1)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(self.WIDTH - 6, 7, _s(title), ln=1)
        pdf.set_text_color(*INK)
        if subtitle:
            pdf.set_xy(self.MARGIN, y + 11)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*MUTED)
            pdf.multi_cell(self.WIDTH, 4.5, _s(subtitle))
            pdf.set_text_color(*INK)
        pdf.ln(2)

    def body(self, txt, size=10, color=INK):
        pdf = self.pdf
        pdf.set_font("Helvetica", "", size)
        pdf.set_text_color(*color)
        pdf.multi_cell(self.WIDTH, 5, _s(txt))
        pdf.ln(1)

    def callout(self, label, value, sub=None):
        pdf = self.pdf
        y = pdf.get_y()
        h = 24 if sub else 18
        pdf.set_fill_color(*WASH)
        pdf.set_draw_color(*CLAY)
        pdf.rect(self.MARGIN, y, self.WIDTH, h, "DF")
        pdf.set_xy(self.MARGIN + 4, y + 2.5)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*MUTED)
        pdf.cell(0, 5, _s(label), ln=1)
        pdf.set_x(self.MARGIN + 4)
        pdf.set_font("Helvetica", "B", 22)
        pdf.set_text_color(*CLAY)
        pdf.cell(0, 10, _s(value), ln=1)
        if sub:
            pdf.set_x(self.MARGIN + 4)
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*MUTED)
            pdf.cell(0, 4, _s(sub), ln=1)
        pdf.set_text_color(*INK)
        pdf.set_y(y + h + 3)

    def kv_table(self, rows, k_w=62):
        pdf = self.pdf
        pdf.set_font("Helvetica", "", 10)
        for i, (k, v) in enumerate(rows):
            fill = WASH if i % 2 == 0 else WASH2
            pdf.set_fill_color(*fill)
            pdf.set_text_color(*MUTED)
            pdf.cell(k_w, 7, "  " + _s(k), border=0, fill=True)
            pdf.set_text_color(*INK)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(self.WIDTH - k_w, 7, _s(v), border=0, fill=True, ln=1)
            pdf.set_font("Helvetica", "", 10)
        pdf.ln(2)

    def cols3(self, header, rows):
        pdf = self.pdf
        c = [self.WIDTH * 0.46, self.WIDTH * 0.27, self.WIDTH * 0.27]
        pdf.set_fill_color(*CLAY_DK)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 9)
        for i, h in enumerate(header):
            pdf.cell(c[i], 7, "  " + _s(h), border=0, fill=True, align="L" if i == 0 else "R")
        pdf.ln(7)
        pdf.set_text_color(*INK)
        for r_i, row in enumerate(rows):
            fill = WASH if r_i % 2 == 0 else WASH2
            pdf.set_fill_color(*fill)
            for i, val in enumerate(row):
                pdf.set_font("Helvetica", "B" if i == 0 else "", 9)
                pdf.cell(c[i], 6.5, ("  " if i == 0 else "") + _s(val) + ("  " if i else ""),
                         border=0, fill=True, align="L" if i == 0 else "R")
            pdf.ln(6.5)
        pdf.ln(2)

    def checklist(self, items):
        pdf = self.pdf
        for i, (head, txt) in enumerate(items, 1):
            if pdf.get_y() > 255:
                pdf.add_page()
            y = pdf.get_y()
            pdf.set_fill_color(*CLAY)
            pdf.ellipse(self.MARGIN, y + 0.5, 5, 5, "F")
            pdf.set_xy(self.MARGIN, y + 0.5)
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(255, 255, 255)
            pdf.cell(5, 5, str(i), align="C")
            pdf.set_xy(self.MARGIN + 8, y)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(*INK)
            pdf.cell(0, 5, _s(head), ln=1)
            pdf.set_x(self.MARGIN + 8)
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*MUTED)
            pdf.multi_cell(self.WIDTH - 8, 4.5, _s(txt))
            pdf.ln(1.5)
        pdf.set_text_color(*INK)


def _cover(r, d):
    pdf = r.pdf
    pdf.add_page()
    pdf.set_fill_color(*CLAY)
    pdf.rect(0, 0, 210, 62, "F")
    pdf.set_fill_color(*CLAY_DK)
    pdf.rect(0, 58, 210, 4, "F")
    pdf.set_xy(14, 14)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 26)
    pdf.cell(0, 12, "Vindkollen", ln=1)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 14)
    pdf.cell(0, 8, _s("Din personliga marknadsrapport"), ln=1)
    pdf.set_x(14)
    pdf.set_font("Helvetica", "", 10)
    muni = _s(d.get("municipality") or "din kommun")
    pdf.cell(0, 6, _s(f"Ersättning, arrenden & vindkraftsläget i {muni}"), ln=1)
    pdf.set_y(70)
    name = _s(d.get("name") or "markägare")
    r.body(f"Hej {name}!", size=12, color=INK)
    r.body(
        "Tack för att du använde Vindkollens ersättningskalkylator. Den här rapporten är "
        "skräddarsydd utifrån uppgifterna du angav och går ett steg längre än kalkylatorn: "
        "vi visar hur din ersättning räknas fram, vilka arrende- och royaltynivåer som gäller "
        "i din region, hur du hittar de planerade och beviljade parkerna nära dig, och en "
        "konkret checklista inför en förhandling med ett vindkraftsbolag.",
        size=10, color=MUTED)
    r.body(f"Skapad {datetime.utcnow().strftime('%Y-%m-%d')} - vindkoll.se", size=8, color=MUTED)


def _section_compensation(r, d):
    r.section("1. Din ersättning i detalj",
              "Så här räknas din uppskattade ersättning fram - och vad den beror på.")
    r.callout("Uppskattad årlig skattefri ersättning (som närboende):",
              _sek(d.get("estimated_compensation_sek")),
              sub="Enligt regeringens föreslagna trappstegsmodell för intäktsdelning.")
    r.kv_table([
        ("Fastighet / adress", d.get("property_address") or "-"),
        ("Kommun", d.get("municipality") or "-"),
        ("Elområde", d.get("elarea") or "-"),
        ("Avstånd till verk", _num(d.get("distance_m"), " m")),
        ("Turbinhöjd", _num(d.get("turbine_height_m"), " m")),
        ("Antal verk i parken", _num(d.get("turbine_count"))),
        ("Din ersättningsnivå", _num(d.get("promille"), " promille")),
    ])
    r.body(
        "Trappstegsmodellen ger närboende en andel av parkens intäkter som trappas ner med "
        "avståndet - ju närmare verken, desto högre promille. Riktvärden:")
    r.cols3(["Avstånd till närmaste verk", "Nivå", "Din situation"],
            [["Inom ca 500-800 m", "~2,5 promille", ""],
             ["Ca 800-1500 m", "~1,5 promille", ""],
             ["Ca 1500-2500 m", "~1,0 promille", ""],
             ["Över ca 2500 m", "~0,5 promille", ""],
             [f"Du: {_num(d.get('distance_m'),' m')}",
              _num(d.get("promille"), " promille"),
              _sek(d.get("estimated_compensation_sek"))]])
    r.body(
        "Siffran är en preliminär uppskattning för planeringsändamål. Den faktiska ersättningen "
        "beror på slutlig lagstiftning, parkens storlek och elpriset. Vindkollen bevakar lagen om "
        "intäktsdelning dagligen och hör av sig när detaljerna fastställs av riksdagen.",
        size=9, color=MUTED)


def _region(d):
    return ELOMRADE.get((d.get("elarea") or "").upper().strip())


def _section_arrende(r, d):
    reg = _region(d)
    pris_ore = reg["pris_ore"] if reg else 45
    pris_kr = pris_ore / 100.0
    gross_per_turbine = ASSUMED_MW_PER_TURBINE * FULL_LOAD_HOURS * 1000 * pris_kr
    arr_lo = gross_per_turbine * ARRENDE_PCT[0]
    arr_hi = gross_per_turbine * ARRENDE_PCT[1]
    bygd = gross_per_turbine * BYGDEPENG_PCT
    cnt = d.get("turbine_count")
    r.section("2. Arrenden & royaltynivåer i din region",
              "Vad marken faktiskt är värd - om verk står på eller upplåts från din fastighet.")
    if reg:
        r.body(f"Ditt elområde är {d.get('elarea')} - {reg['namn']}. {reg['kontext']} "
               f"Vi räknar nedan med ett riktpris på {pris_ore} öre/kWh och ett verk på "
               f"{ASSUMED_MW_PER_TURBINE:g} MW (~{FULL_LOAD_HOURS} fullasttimmar/år).", size=9, color=MUTED)
    else:
        r.body(f"Vi räknar nedan med ett riktpris på {pris_ore} öre/kWh och ett verk på "
               f"{ASSUMED_MW_PER_TURBINE:g} MW. Ange ditt elområde i kalkylatorn för regionspecifika tal.",
               size=9, color=MUTED)
    r.cols3(["Ersättningstyp (per verk & år)", "Nivå", "Uppskattat belopp"],
            [["Markarrende till markägare (royalty)", "3-5 % av brutto",
              f"{_sek(arr_lo)} - {_sek(arr_hi)}"],
             ["Bygdepeng till närsamhället", "~0,75 % av brutto", _sek(bygd)],
             ["Parkens bruttointäkt (referens)", "100 %", _sek(gross_per_turbine)]])
    if cnt:
        r.callout(f"Om hela parken ({_num(cnt)} verk) står på din mark - uppskattat arrende:",
                  f"{_sek(arr_lo*cnt)} - {_sek(arr_hi*cnt)} / år",
                  sub="Royalty-baserat arrende, exkl. separat ersättning för vägar/kablar/intrång.")
    r.body(
        "Markarrende betalas till markägaren som upplåter mark för verken och är normalt en "
        "royalty på parkens bruttointäkt (ofta 3-5 %), ibland med ett garanterat golv per verk. "
        "Det skiljer sig från närboendeersättningen i avsnitt 1, som går till dig som bor nära "
        "men inte nödvändigtvis upplåter mark. Nivåerna är branschriktvärden - faktiska avtal "
        "varierar med vindläge, projektets storlek och din förhandling (se avsnitt 4).",
        size=9, color=MUTED)


def _section_parks(r, d):
    muni = d.get("municipality") or "din kommun"
    reg = _region(d)
    r.section("3. Planerade & beviljade vindkraftsparker nära dig",
              "Så hittar du exakt vilka projekt som är på gång runt din fastighet - från källan.")
    if reg:
        r.body(f"Regionalt läge: {reg['namn']} (elområde {d.get('elarea')}). {reg['kontext']}")
    r.body(
        "De exakta, alltid aktuella projekten nära dig finns i Vindbrukskollen - den officiella "
        "karttjänsten från Länsstyrelserna och Energimyndigheten över alla vindkraftsprojekt: i "
        "drift, beviljade och under tillståndsprövning. Vi länkar dit hellre än att trycka en "
        "frusen lista, så att du alltid ser det senaste läget för just din fastighet.")
    r.callout("Vindbrukskollen - officiella kartan över alla parker:",
              "vbk.lansstyrelsen.se", sub="Sök upp din fastighet och se projekten runt omkring.")
    r.body("Så här gör du (tar ett par minuter):")
    r.checklist([
        ("Öppna kartan", "Gå till vbk.lansstyrelsen.se och välj kartvyn över vindkraftsverk och projektområden."),
        (f"Zooma in på {_s(muni)}", "Sök på din kommun eller fastighetsadress och zooma in på ditt område."),
        ("Läs av status", "Varje projekt visar status: i drift, beviljat eller under prövning - och antal verk samt projektör."),
        ("Bevaka förändringar", "Du är nu prenumerant på Vindkollen - vi hör av oss när lagen om intäktsdelning och lokala projekt utvecklas.")
    ])


def _section_checklist(r, d):
    r.section("4. Checklista inför förhandling med vindkraftsbolag",
              "Tio punkter som kan vara mycket pengar värda över avtalets 25-35 år.")
    r.checklist(CHECKLIST)


def _section_next(r, d):
    r.section("5. Nästa steg")
    r.body(
        "Du är nu prenumerant på Vindkollens veckobrev med marknadsuppdateringar - vi bevakar "
        "lagen om intäktsdelning, arrendenivåer och lokala projekt och hör av oss när något viktigt "
        "händer för dig. På vindkoll.se hittar du fördjupande guider om arrendeavtal, skatt på "
        "ersättning och hur vindkraft påverkar fastighetsvärdet.")
    r.callout("Frågor om din situation?", "Svara på mejlet med rapporten",
              sub="Vi läser varje svar och hjälper dig vidare.")


def build_report_pdf(d: dict) -> bytes:
    r = VindReport()
    pdf = r.pdf

    def footer():
        pdf.set_y(-15)
        pdf.set_draw_color(*LINE)
        pdf.line(r.MARGIN, pdf.get_y(), 210 - r.MARGIN, pdf.get_y())
        pdf.set_y(-13)
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(0, 4, _s("Vindkollen | vindkoll.se | Preliminär uppskattning - ej juridisk "
                          "eller ekonomisk rådgivning."), align="C")

    pdf.footer = footer  # fpdf2 calls self.footer() on each page

    _cover(r, d)
    _section_compensation(r, d)
    _section_arrende(r, d)
    _section_parks(r, d)
    _section_checklist(r, d)
    _section_next(r, d)

    out = pdf.output()
    return bytes(out)


def build_user_email_html(d: dict) -> str:
    name = (d.get("name") or "").strip()
    hej = f"Hej {name}," if name else "Hej,"
    est = _sek(d.get("estimated_compensation_sek"))
    muni = (d.get("municipality") or "din kommun").strip()
    return f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:560px;margin:auto;color:#1e293b">
  <div style="background:#105e4e;color:#fff;padding:22px 24px;border-radius:12px 12px 0 0">
    <h2 style="margin:0;font-size:20px">Din marknadsrapport är här 🌬️</h2>
  </div>
  <div style="border:1px solid #e2e8f0;border-top:0;border-radius:0 0 12px 12px;padding:24px">
    <p>{hej}</p>
    <p>Tack för att du använde Vindkollens ersättningskalkylator. Din skräddarsydda
       rapport för <b>{muni}</b> finns som <b>PDF i bilagan</b> – den går längre än kalkylatorn.</p>
    <p style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:10px;padding:14px 16px">
       Uppskattad årlig skattefri ersättning (som närboende):<br>
       <span style="font-size:24px;font-weight:800;color:#105e4e">{est}</span>
    </p>
    <p style="margin:18px 0 6px">I rapporten får du:</p>
    <ul style="margin:0 0 8px;padding-left:20px;line-height:1.7">
      <li>Hur din ersättning räknas fram – hela trappstegsmodellen</li>
      <li>Arrende- och royaltynivåer i din region (med ditt elområdes elpris)</li>
      <li>Så hittar du planerade &amp; beviljade parker nära dig (officiella kartan)</li>
      <li>Checklista inför förhandling med vindkraftsbolag (10 punkter)</li>
    </ul>
    <p>Du är nu prenumerant och får vårt veckobrev med marknadsuppdateringar – vi bevakar
       lagen om intäktsdelning dagligen och hör av oss så fort detaljerna fastställs.</p>
    <p style="margin-top:22px">Vänliga hälsningar,<br><b>Vindkollen</b><br>
       <a href="https://vindkoll.se" style="color:#105e4e">vindkoll.se</a></p>
    <p style="font-size:11px;color:#94a3b8;margin-top:22px">Du får detta för att du begärde en
       rapport på vindkoll.se. Vill du avsluta prenumerationen, svara på detta mejl.</p>
  </div>
</div>"""


def build_owner_email_html(d: dict) -> str:
    fields = [
        ("E-post", d.get("email")),
        ("Namn", d.get("name")),
        ("Kommun", d.get("municipality")),
        ("Fastighet", d.get("property_address")),
        ("Elområde", d.get("elarea")),
        ("Avstånd (m)", d.get("distance_m")),
        ("Turbinhöjd (m)", d.get("turbine_height_m")),
        ("Antal verk", d.get("turbine_count")),
        ("Uppskattad ersättning", _sek(d.get("estimated_compensation_sek"))),
        ("Promille", d.get("promille")),
        ("Källa", d.get("source")),
    ]
    rows = "".join(
        f'<tr><td style="padding:4px 10px;color:#64748b">{k}</td>'
        f'<td style="padding:4px 10px;font-weight:600">{v if v not in (None,"") else "—"}</td></tr>'
        for k, v in fields
    )
    return f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:560px;color:#1e293b">
  <h3>🌬️ Ny lead — Vindkollen (rapport-funnel)</h3>
  <table style="border-collapse:collapse;font-size:14px">{rows}</table>
  <p style="font-size:12px;color:#94a3b8">Rapporten skickades automatiskt till leadet.</p>
</div>"""
