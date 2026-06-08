"""
Vindkollen lead magnet — the personalised "marknadsrapport" the kalkylator
page promises ("vi skickar en skräddarsydd PDF-rapport till din inbox").

Generates a branded PDF from the calculator snapshot + the HTML email bodies
for the user (magnet) and the owner (lead notification).
fpdf2 core fonts use latin-1, which covers å/ä/ö.
"""
from datetime import datetime

CLAY = (16, 94, 78)        # vindkollen green
INK = (30, 41, 59)
MUTED = (100, 116, 139)


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
        return "—"


def _num(v, suffix=""):
    try:
        if v is None:
            return "—"
        n = float(v)
        s = f"{int(n)}" if n == int(n) else f"{n:g}"
        return s + suffix
    except Exception:
        return "—"


def build_report_pdf(d: dict) -> bytes:
    from fpdf import FPDF  # lazy: a missing fpdf2 must never crash app boot
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    # Header band
    pdf.set_fill_color(*CLAY)
    pdf.rect(0, 0, 210, 30, "F")
    pdf.set_xy(14, 9)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, "Vindkollen - Marknadsrapport", ln=1)
    pdf.set_xy(14, 19)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, "Preliminar ersattning for narboende & markagare", ln=1)

    pdf.set_text_color(*INK)
    pdf.set_xy(14, 40)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MUTED)
    name = _s(d.get("name") or "markagare")
    pdf.multi_cell(182, 5, f"Hej {name}! Har ar din personliga uppskattning, baserad pa "
                           f"uppgifterna du angav i kalkylatorn och regeringens trappstegsmodell. "
                           f"Skapad {datetime.utcnow().strftime('%Y-%m-%d')}.")
    pdf.ln(3)

    # Headline number
    pdf.set_text_color(*INK)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, "Uppskattad arlig skattefri ersattning:", ln=1)
    pdf.set_text_color(*CLAY)
    pdf.set_font("Helvetica", "B", 28)
    pdf.cell(0, 14, _sek(d.get("estimated_compensation_sek")), ln=1)
    pdf.ln(2)

    # Input table
    pdf.set_text_color(*INK)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Dina uppgifter", ln=1)
    rows = [
        ("Fastighet / adress", d.get("property_address") or "—"),
        ("Kommun", d.get("municipality") or "—"),
        ("Elomrade", d.get("elarea") or "—"),
        ("Avstand till verk", _num(d.get("distance_m"), " m")),
        ("Turbinhojd", _num(d.get("turbine_height_m"), " m")),
        ("Antal verk", _num(d.get("turbine_count"))),
        ("Ersattningsniva", _num(d.get("promille"), " promille")),
    ]
    pdf.set_font("Helvetica", "", 11)
    for k, v in rows:
        pdf.set_text_color(*MUTED)
        pdf.cell(60, 7, k, border=0)
        pdf.set_text_color(*INK)
        pdf.cell(0, 7, _s(v), ln=1)
    pdf.ln(4)

    # Explanation
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Sa har raknar vi", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(182, 5,
        "Berakningen foljer regeringens foreslagna trappstegsmodell for ersattning till "
        "narboende (2,5-0,5 promille av vindkraftsparkens intakter beroende pa avstand). "
        "Siffran ar en preliminar uppskattning for planeringsandamal - den faktiska "
        "ersattningen beror pa slutlig lagstiftning, parkens storlek och elpris. "
        "Vindkollen bevakar lagen om intaktsdelning dagligen och hor av sig nar detaljerna "
        "faststalls av riksdagen.")
    pdf.ln(3)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*INK)
    pdf.cell(0, 8, "Nasta steg", ln=1)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(182, 5,
        "1. Kontrollera planerade vindkraftsparker i din kommun.\n"
        "2. Las pa om arrende- och ersattningsavtal pa vindkoll.se.\n"
        "3. Du ar nu prenumerant och far en notis sa fort lagen fastställs.")

    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(*MUTED)
    pdf.multi_cell(182, 4, "Vindkollen | vindkoll.se | Preliminar uppskattning, ej juridisk eller "
                           "ekonomisk radgivning.")

    out = pdf.output()
    return bytes(out)


def build_user_email_html(d: dict) -> str:
    name = (d.get("name") or "").strip()
    hej = f"Hej {name}," if name else "Hej,"
    est = _sek(d.get("estimated_compensation_sek"))
    return f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:560px;margin:auto;color:#1e293b">
  <div style="background:#105e4e;color:#fff;padding:22px 24px;border-radius:12px 12px 0 0">
    <h2 style="margin:0;font-size:20px">Din marknadsrapport är här 🌬️</h2>
  </div>
  <div style="border:1px solid #e2e8f0;border-top:0;border-radius:0 0 12px 12px;padding:24px">
    <p>{hej}</p>
    <p>Tack för att du använde Vindkollens ersättningskalkylator. Din skräddarsydda
       rapport finns som <b>PDF i bilagan</b> till det här mejlet.</p>
    <p style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:10px;padding:14px 16px">
       Uppskattad årlig skattefri ersättning:<br>
       <span style="font-size:24px;font-weight:800;color:#105e4e">{est}</span>
    </p>
    <p>Siffran följer regeringens föreslagna trappstegsmodell och är en preliminär
       uppskattning. Vi bevakar lagen om intäktsdelning dagligen och hör av oss så
       fort detaljerna fastställs av riksdagen — du är nu prenumerant.</p>
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
