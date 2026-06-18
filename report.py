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

fpdf2 core fonts use latin-1, which covers a/a/o; _s() makes text safe.
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
# Markarrende (royalty) share of gross, narboende intaktsdelning, bygdepeng.
ARRENDE_PCT = (0.03, 0.05)   # typical landowner royalty band
BYGDEPENG_PCT = 0.0075

ELOMRADE = {
    "SE1": {"namn": "Norra Sverige (Lulea)", "pris_ore": 30,
            "kontext": "Lagst elpriser i landet, men mycket landbaserad vindkraft byggs har "
                       "tack vare goda vindlagen och gott om mark."},
    "SE2": {"namn": "Norra Mellansverige (Sundsvall)", "pris_ore": 35,
            "kontext": "Sveriges mest expansiva landbaserade vindkraftsregion - har byggs "
                       "merparten av de stora nya parkerna."},
    "SE3": {"namn": "Sodra Mellansverige (Stockholm)", "pris_ore": 45,
            "kontext": "Hog efterfragan och stigande utbyggnad; bade landbaserat och planerad "
                       "havsbaserad vindkraft langs ostkusten."},
    "SE4": {"namn": "Sodra Sverige (Malmo)", "pris_ore": 60,
            "kontext": "Hogst elpriser i landet, vilket gor ersattningar och arrenden mest "
                       "vardefulla har. Stora havsbaserade projekt planeras i soder."},
}

CHECKLIST = [
    ("Royalty, inte bara fast avgift", "Begar att arrendet baseras pa faktisk produktion eller "
     "intakt (en procentsats), sa att din ersattning foljer med nar elpriset stiger - inte bara "
     "ett fast belopp som urholkas av inflationen."),
    ("Garanterat golv per verk", "Forhandla en minimigaranti per verk och ar oavsett elpris och "
     "vindlage, sa att du har en trygg basniva aven svaga ar."),
    ("Ersattning for intrang separat", "Vagar, kabeldragning, transformatorstation och ovrigt "
     "markintrang ska ersattas separat - utover sjalva arrendet."),
    ("Indexuppraking", "Kraver att fasta belopp rakas upp arligen med index (KPI), annars taper "
     "de varde over avtalets 25-35 ar."),
    ("Aterstallningsgaranti", "Sakra en bankgaranti for nedmontering och aterstallning av marken "
     "nar parken avvecklas - sa kostnaden inte hamnar pa dig."),
    ("Betalt for optionstiden", "Projektoren vill ofta ha en option i flera ar innan bygget. "
     "Tidsbegransa den och fa betalt for sjalva optionsperioden."),
    ("Villkor vid agarbyte", "Reglera vad som hander om projektet saljs vidare - dina villkor ska "
     "folja med till en ny agare."),
    ("Oberoende radgivning", "Ta in egen juridisk OCH ekonomisk radgivning innan du skriver pa. "
     "Kostnaden ar liten mot vad avtalet ar vart over decennier."),
    ("Jamfor flera bud", "Ar marken attraktiv? Lat garna fler an en projektor lamna bud - "
     "konkurrens hojer din ersattning."),
    ("Tank pa grannarna", "Reglera ersattning/dialog med narboende tidigt - det minskar risken "
     "for overklaganden som forsenar hela projektet (och din intakt)."),
]


def _s(t):
    """Make text safe for fpdf2 core (latin-1) fonts."""
    t = str(t)
    for a, b in [("—", "-"), ("–", "-"), ("’", "'"), ("‘", "'"),
                 ("“", '"'), ("”", '"'), ("…", "..."), (" ", " ")]:
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

    # -- low level --
    def _x(self):
        return self.MARGIN

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
            pdf.set_font("Helvetica", "" if r_i else "B", 9)
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
    pdf.cell(0, 6, _s(f"Ersattning, arrenden & vindkraftslaget i {muni}"), ln=1)
    pdf.set_y(70)
    name = _s(d.get("name") or "markagare")
    r.body(f"Hej {name}!", size=12, color=INK)
    r.body(
        "Tack for att du anvande Vindkollens ersattningskalkylator. Den har rapporten ar "
        "skraddarsydd utifran uppgifterna du angav och gar ett steg langre an kalkylatorn: "
        "vi visar hur din ersattning rakas fram, vilka arrende- och royaltynivaer som galler "
        "i din region, hur du hittar de planerade och beviljade parkerna nara dig, och en "
        "konkret checklista infor en forhandling med ett vindkraftsbolag.",
        size=10, color=MUTED)
    r.body(f"Skapad {datetime.utcnow().strftime('%Y-%m-%d')} - vindkoll.se", size=8, color=MUTED)


def _section_compensation(r, d):
    r.section("1. Din ersattning i detalj",
              "Sa har rakas din uppskattade ersattning fram - och vad den beror pa.")
    r.callout("Uppskattad arlig skattefri ersattning (som narboende):",
              _sek(d.get("estimated_compensation_sek")),
              sub="Enligt regeringens foreslagna trappstegsmodell for intaktsdelning.")
    r.kv_table([
        ("Fastighet / adress", d.get("property_address") or "-"),
        ("Kommun", d.get("municipality") or "-"),
        ("Elomrade", d.get("elarea") or "-"),
        ("Avstand till verk", _num(d.get("distance_m"), " m")),
        ("Turbinhojd", _num(d.get("turbine_height_m"), " m")),
        ("Antal verk i parken", _num(d.get("turbine_count"))),
        ("Din ersattningsniva", _num(d.get("promille"), " promille")),
    ])
    r.body(
        "Trappstegsmodellen ger narboende en andel av parkens intakter som trappas ner med "
        "avstandet - ju narmare verken, desto hogre promille. Riktvarden:")
    r.cols3(["Avstand till narmaste verk", "Niva", "Din situation"],
            [["Inom ca 500-800 m", "~2,5 promille", ""],
             ["Ca 800-1500 m", "~1,5 promille", ""],
             ["Ca 1500-2500 m", "~1,0 promille", ""],
             ["Over ca 2500 m", "~0,5 promille", ""],
             [f"Du: {_num(d.get('distance_m'),' m')}",
              _num(d.get("promille"), " promille"),
              _sek(d.get("estimated_compensation_sek"))]])
    r.body(
        "Siffran ar en preliminar uppskattning for planeringsandamal. Den faktiska ersattningen "
        "beror pa slutlig lagstiftning, parkens storlek och elpriset. Vindkollen bevakar lagen om "
        "intaktsdelning dagligen och hor av sig nar detaljerna faststalls av riksdagen.",
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
    r.section("2. Arrenden & royaltynivaer i din region",
              "Vad marken faktiskt ar vard - om verk star pa eller upplats fran din fastighet.")
    if reg:
        r.body(f"Ditt elomrade ar {d.get('elarea')} - {reg['namn']}. {reg['kontext']} "
               f"Vi rakar nedan med ett riktpris pa {pris_ore} ore/kWh och ett verk pa "
               f"{ASSUMED_MW_PER_TURBINE:g} MW (~{FULL_LOAD_HOURS} fullasttimmar/ar).", size=9, color=MUTED)
    else:
        r.body(f"Vi rakar nedan med ett riktpris pa {pris_ore} ore/kWh och ett verk pa "
               f"{ASSUMED_MW_PER_TURBINE:g} MW. Ange ditt elomrade i kalkylatorn for regionspecifika tal.",
               size=9, color=MUTED)
    r.cols3(["Ersattningstyp (per verk & ar)", "Niva", "Uppskattat belopp"],
            [["Markarrende till markagare (royalty)", "3-5 % av brutto",
              f"{_sek(arr_lo)} - {_sek(arr_hi)}"],
             ["Bygdepeng till narsamhallet", "~0,75 % av brutto", _sek(bygd)],
             ["Parkens bruttointakt (referens)", "100 %", _sek(gross_per_turbine)]])
    if cnt:
        r.callout(f"Om hela parken ({_num(cnt)} verk) star pa din mark - uppskattat arrende:",
                  f"{_sek(arr_lo*cnt)} - {_sek(arr_hi*cnt)} / ar",
                  sub="Royalty-baserat arrende, exkl. separat ersattning for vagar/kablar/intrang.")
    r.body(
        "Markarrende betalas till markagaren som upplater mark for verken och ar normalt en "
        "royalty pa parkens bruttointakt (ofta 3-5 %), ibland med ett garanterat golv per verk. "
        "Det skiljer sig fran narboendeersattningen i avsnitt 1, som gar till dig som bor nara "
        "men inte nodvandigtvis upplater mark. Niverna ar branschriktvarden - faktiska avtal "
        "varierar med vindlage, projektets storlek och din forhandling (se avsnitt 4).",
        size=9, color=MUTED)


def _section_parks(r, d):
    muni = d.get("municipality") or "din kommun"
    reg = _region(d)
    r.section("3. Planerade & beviljade vindkraftsparker nara dig",
              "Sa hittar du exakt vilka projekt som ar pa gang runt din fastighet - fran kallan.")
    if reg:
        r.body(f"Regionalt lage: {reg['namn']} (elomrade {d.get('elarea')}). {reg['kontext']}")
    r.body(
        "De exakta, alltid aktuella projekten nara dig finns i Vindbrukskollen - den officiella "
        "karttjansten fran Lansstyrelserna och Energimyndigheten over alla vindkraftsprojekt: i "
        "drift, beviljade och under tillstandsproving. Vi lankar dit hellre an att trycka en "
        "fryst lista, sa att du alltid ser det senaste lagent for just din fastighet.")
    r.callout("Vindbrukskollen - officiella kartan over alla parker:",
              "vbk.lansstyrelsen.se", sub="Sok upp din fastighet och se projekten runt omkring.")
    r.body("Sa har gor du (tar ett par minuter):")
    r.checklist([
        ("Oppna kartan", "Ga till vbk.lansstyrelsen.se och valj kartvyn over vindkraftsverk och projektomraden."),
        (f"Zooma in pa {_s(muni)}", "Sok pa din kommun eller fastighetsadress och zooma in pa ditt omrade."),
        ("Las av status", "Varje projekt visar status: i drift, beviljat eller under provning - och antal verk samt projektor."),
        ("Bevaka forandringar", "Du ar nu prenumerant pa Vindkollen - vi hor av oss nar lagen om intaktsdelning och lokala projekt utvecklas.")
    ])


def _section_checklist(r, d):
    r.section("4. Checklista infor forhandling med vindkraftsbolag",
              "Tio punkter som kan vara mycket pengar varda over avtalets 25-35 ar.")
    r.checklist(CHECKLIST)


def _section_next(r, d):
    r.section("5. Nasta steg")
    r.body(
        "Du ar nu prenumerant pa Vindkollens veckobrev med marknadsuppdateringar - vi bevakar "
        "lagen om intaktsdelning, arrendenivaer och lokala projekt och hor av oss nar nagot viktigt "
        "hander for dig. Pa vindkoll.se hittar du fordjupande guider om arrendeavtal, skatt pa "
        "ersattning och hur vindkraft paverkar fastighetsvardet.")
    r.callout("Fragor om din situation?", "Svara pa mejlet med rapporten",
              sub="Vi laser varje svar och hjalper dig vidare.")


def build_report_pdf(d: dict) -> bytes:
    r = VindReport()
    # Footer/page number on every page.
    pdf = r.pdf

    def footer():
        pdf.set_y(-15)
        pdf.set_draw_color(*LINE)
        pdf.line(r.MARGIN, pdf.get_y(), 210 - r.MARGIN, pdf.get_y())
        pdf.set_y(-13)
        pdf.set_font("Helvetica", "I", 7.5)
        pdf.set_text_color(*MUTED)
        pdf.cell(0, 4, _s("Vindkollen | vindkoll.se | Preliminar uppskattning - ej juridisk "
                          "eller ekonomisk radgivning."), align="C")

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
