"""
Matchning av leads mot köpare.

Regelmotor, inte modell. Vilken partner som ska ha ett lead avgörs av silo,
geografi, poäng, samtycke och kapacitet — allt deterministiskt, så att samma
lead alltid ger samma svar och beslutet går att förklara för både köparen och
den vars uppgifter det gäller.

Det som INTE finns här är utskicket. Motorn föreslår mottagare och skriver
mejlet; någon måste godkänna innan det går iväg (se auto_send per partner).
"""

import os
from datetime import datetime
from typing import List, Optional, Tuple

import leads as vk_leads

# ---------------------------------------------------------------------------
# Partnertyper
# ---------------------------------------------------------------------------
#
# Typen styr vilket *intresse* hos leadet som krävs. En jurist ska inte få ett
# lead som aldrig bett om juridisk hjälp, hur högt det än är poängsatt.

PARTNER_KINDS = {
    "projektor": {
        "label": "Projektör",
        "requires_flag": "wants_projector_contact",
        "segments": ("markagare",),
    },
    "jurist": {
        "label": "Jurist / juridisk rådgivare",
        "requires_flag": "wants_legal_help",
        "segments": ("markagare", "narboende"),
    },
    "radgivare": {
        "label": "Rådgivare / lantbruksekonom",
        "requires_flag": "wants_legal_help",
        "segments": ("markagare",),
    },
    "kommunradgivning": {
        "label": "Kommunrådgivning",
        "requires_flag": None,
        "segments": ("kommun",),
    },
}


# Rådgivarsidan. Ett lead som bett om juridisk hjälp ska ha fått den kontakten
# innan projektören ringer — annars förhandlar markägaren ensam mot en motpart
# som gör tiotals sådana avtal om året, och vårt löfte om oberoende är tomt.
LEGAL_KINDS = ("jurist", "radgivare")

# Hur länge projektörens överlämning hålls tillbaka när en rådgivare fått leadet.
HOLD_DAYS = int(os.environ.get("LEAD_HOLD_DAYS", "3"))


def is_legal(kind: Optional[str]) -> bool:
    return (kind or "") in LEGAL_KINDS


def split_by_order(partners: list) -> Tuple[list, list]:
    """Dela upp mottagare i (skickas nu, hålls tillbaka).

    Rådgivare går alltid först. Projektörer hålls bara tillbaka om en rådgivare
    faktiskt fick leadet — finns ingen rådgivare att vänta på fyller fördröjningen
    ingen funktion, den skulle bara försena den enda nytta leadet ger.
    """
    legal = [p for p in partners if is_legal(p.kind)]
    others = [p for p in partners if not is_legal(p.kind)]
    if legal:
        return legal, others
    return others, []


def _csv_set(value: Optional[str]) -> set:
    """Kommaseparerad kolumn -> mängd. Tom kolumn betyder 'ingen begränsning'."""
    if not value:
        return set()
    return {v.strip() for v in value.split(",") if v.strip()}


# ---------------------------------------------------------------------------
# Matchning
# ---------------------------------------------------------------------------


def disqualifications(lead, partner, assigned_this_month: int,
                      already_assigned: bool) -> List[str]:
    """Skälen att INTE skicka det här leadet till den här partnern.

    Tom lista = matchning. Att returnera skälen i stället för bara True/False
    gör att en utebliven matchning går att felsöka utan att läsa koden.
    """
    reasons = []
    kind = PARTNER_KINDS.get(partner.kind)

    if not partner.active:
        reasons.append("partnern är pausad")
    if not kind:
        reasons.append(f"okänd partnertyp: {partner.kind}")
        return reasons

    segment = vk_leads.normalise_segment(lead.segment)
    allowed_segments = _csv_set(partner.segments) or set(kind["segments"])
    if segment not in allowed_segments:
        reasons.append(f"fel silo ({segment})")

    # Geografi: tom täckning = hela landet.
    counties = _csv_set(partner.counties)
    elareas = _csv_set(partner.elareas)
    if counties or elareas:
        in_county = bool(lead.county and lead.county in counties)
        in_elarea = bool(lead.elarea and lead.elarea in elareas)
        if not (in_county or in_elarea):
            reasons.append(f"utanför täckningen ({lead.county or lead.elarea or 'okänd region'})")

    if (lead.lead_score or 0) < (partner.min_score or 0):
        reasons.append(f"under poänggränsen ({lead.lead_score or 0} < {partner.min_score})")

    # Samtycket är hårdare än allt annat: utan bock lämnar leadet aldrig huset.
    if partner.requires_consent and not lead.consent_partner_share:
        reasons.append("leadet har inte samtyckt till partnerdelning")

    flag = kind["requires_flag"]
    if flag and not getattr(lead, flag, False):
        reasons.append(f"leadet har inte begärt {kind['label'].lower()}")

    if partner.monthly_cap and assigned_this_month >= partner.monthly_cap:
        reasons.append(f"månadstaket nått ({assigned_this_month}/{partner.monthly_cap})")

    if already_assigned:
        reasons.append("redan tilldelat den här partnern")

    return reasons


# Vem konkurrerar med vem. En jurist och en projektör konkurrerar inte — ett
# lead som bett om båda ska kunna lämnas till båda. Men en jurist och en
# lantbruksekonom gör det: ur markägarens perspektiv är de alternativ för samma
# behov, och två kalla samtal om samma sak gör leadet sämre för alla.
COMPETITION_GROUPS = {
    "jurist": "radgivning",
    "radgivare": "radgivning",
    "projektor": "projektering",
    "kommunradgivning": "kommun",
}


def competition_group(kind: Optional[str]) -> str:
    return COMPETITION_GROUPS.get(kind or "", kind or "okand")


def best_per_group(matches: list) -> list:
    """Högst rankad partner per konkurrensgrupp.

    Matchningarna är redan rankade, så den som ligger först i sin grupp är den
    med snävast täckning — den lokala rådgivaren går före den rikstäckande.
    """
    seen, out = set(), []
    for p in matches:
        grupp = competition_group(p.kind)
        if grupp not in seen:
            seen.add(grupp)
            out.append(p)
    return out


def _coverage_specificity(partner) -> int:
    """Snävare täckning vinner. Den som köpt ett enskilt län ska gå före den
    som köpt hela Sverige — annars är regionsexklusiviteten meningslös."""
    if _csv_set(partner.counties):
        return 2
    if _csv_set(partner.elareas):
        return 1
    return 0


def rank_partners(lead, partners, assignment_counts: dict,
                  already_assigned_ids: set) -> Tuple[list, list]:
    """Returnera (matchande partners rankade, avvisade med skäl).

    Ranking: exklusivitet först, sedan snävast täckning, sedan högst prioritet,
    och sist minst antal tilldelningar den här månaden — så att två likvärdiga
    köpare i samma län delar flödet jämnt i stället för att den ena svälter.
    """
    matches, rejected = [], []

    for p in partners:
        reasons = disqualifications(
            lead, p,
            assignment_counts.get(p.id, 0),
            p.id in already_assigned_ids,
        )
        if reasons:
            rejected.append((p, reasons))
        else:
            matches.append(p)

    # Har någon exklusivitet i regionen försvinner alla andra.
    exclusive = [p for p in matches if p.exclusive]
    if exclusive:
        matches = exclusive

    matches.sort(key=lambda p: (
        -_coverage_specificity(p),
        -(p.priority or 0),
        assignment_counts.get(p.id, 0),
        p.id,
    ))
    return matches, rejected


# ---------------------------------------------------------------------------
# Mejl
# ---------------------------------------------------------------------------

_BRAND = "#105e4e"


def _row(label, value):
    shown = value if value not in (None, "", False) else "—"
    if value is True:
        shown = "Ja"
    return (f'<tr><td style="padding:5px 12px;color:#64748b;white-space:nowrap">{label}</td>'
            f'<td style="padding:5px 12px;font-weight:600">{shown}</td></tr>')


def handover_subject(lead, partner) -> str:
    """Ämnesrad. En kall mottagare öppnar inte 'Nytt lead' från en avsändare de
    aldrig hört talas om — då måste raden säga vad de får och att det är gratis."""
    region = lead.county or lead.elarea or "Sverige"
    if is_cold(partner):
        areal = f", {lead.land_hectares} ha" if lead.land_hectares else ""
        # Sammansättningen skrivs ut, inte byggd av etiketten: "markägarelead"
        # av "Markägare" + "lead" är inte svenska.
        ord_ = {"markagare": "markägarlead", "narboende": "närboendelead",
                "kommun": "kommunärende"}.get(
            vk_leads.normalise_segment(lead.segment), "lead")
        return f"Kostnadsfritt {ord_} – {region}{areal} | Vindkollen"
    return (f"Nytt lead från Vindkollen – {vk_leads.segment_label(lead.segment)}, "
            f"{region}")


def is_cold(partner) -> bool:
    """Har vi inget avtal med mottagaren? Då är utskicket en presentation."""
    return getattr(partner, "relationship", "kall") != "avtalad"


def _cold_intro(partner) -> str:
    """Ingress till en mottagare som aldrig hört talas om oss.

    Leadet är pitchen: de får något värdefullt utan motprestation, och frågan
    om fortsättning ställs efter att de sett vad det är.
    """
    return f"""
    <p>Hej{(' ' + partner.contact_name) if partner.contact_name else ''},</p>
    <p>Ni känner inte oss ännu. <b>Vindkollen</b> är en oberoende sajt om
       vindkraftsersättning, arrende och intäktsdelning. Markägare och närboende
       kommer till oss för att räkna på vad marken är värd och för att förstå
       reglerna — vi är inte knutna till något kraftbolag och tar inte betalt av
       dem som hör av sig.</p>
    <p>Personen nedan har fyllt i vårt formulär, bett om kontakt med projektörer i
       sitt län och samtyckt till att uppgifterna delas. <b>Leadet är kostnadsfritt
       och utan villkor</b> — vi skickar det för att ni ska kunna bedöma om det är
       värt något för er.</p>"""


def _warm_intro(partner) -> str:
    return f"""
    <p>Hej {partner.contact_name or partner.name},</p>
    <p>Nedan följer ett lead som matchar er täckning. Personen har själv fyllt i
       formulär på vindkoll.se och <b>samtyckt till att uppgifterna delas</b> med
       utvald samarbetspartner i sitt län.</p>"""


def _cold_ask() -> str:
    """Frågan som gör utskicket till en affärsöppning i stället för ett brev."""
    return """
    <div style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:10px;
                padding:14px 16px;margin-top:18px">
      <b>Vill ni ha fler?</b><br>
      Svara på det här mejlet med två saker: vem hos er de ska gå till, och vilka
      län eller elområden ni är intresserade av. Då riktar vi flödet dit.
      Vill ni <b>inte</b> ha fler, svara "nej tack" så tar vi bort er direkt.
    </div>"""


def build_handover_email_html(lead, partner) -> str:
    """Överlämningen till köparen.

    Innehåller det köparen behöver för att ringa — och en rad om att personen
    själv bett om kontakten, eftersom det är den raden som avgör om samtalet
    tas emot väl. Ser olika ut beroende på om vi har avtal eller inte.
    """
    stage = vk_leads.PROJECT_STAGES.get((lead.project_stage or "").lower(), {}).get("label")
    timeframe = vk_leads.TIMEFRAMES.get((lead.timeframe or "").lower(), {}).get("label")
    rows = "".join([
        _row("Namn", lead.name),
        _row("E-post", lead.email),
        _row("Telefon", lead.phone),
        _row("Län", lead.county),
        _row("Kommun", lead.municipality),
        _row("Elområde", lead.elarea),
        _row("Fastighet", lead.property_address),
        _row("Markareal (ha)", lead.land_hectares),
        _row("Status i processen", stage),
        _row("Tidshorisont", timeframe),
        _row("Vill ha juridisk hjälp", lead.wants_legal_help),
        _row("Öppen för projektörskontakt", lead.wants_projector_contact),
        _row("Registrerad", lead.created_at.strftime("%Y-%m-%d") if lead.created_at else None),
    ])
    fritext = ""
    if lead.message:
        fritext = (f'<p style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;'
                   f'padding:12px 14px"><b>Egen beskrivning:</b><br>{lead.message}</p>')

    kall = is_cold(partner)
    rubrik = ("Ett kostnadsfritt lead från Vindkollen" if kall
              else "Nytt lead från Vindkollen")
    return f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:600px;color:#1e293b">
  <div style="background:{_BRAND};color:#fff;padding:20px 22px;border-radius:12px 12px 0 0">
    <h2 style="margin:0;font-size:19px">{rubrik}</h2>
    <div style="opacity:.85;font-size:13px;margin-top:4px">
      {vk_leads.segment_label(lead.segment)} · {lead.county or lead.elarea or 'okänd region'}
    </div>
  </div>
  <div style="border:1px solid #e2e8f0;border-top:0;border-radius:0 0 12px 12px;padding:20px">
    {_cold_intro(partner) if kall else _warm_intro(partner)}
    <table style="border-collapse:collapse;font-size:14px;width:100%">{rows}</table>
    {fritext}
    {_cold_ask() if kall else ''}
    <p style="font-size:13px;color:#475569;margin-top:18px">Vi är oberoende från
       kraftbolagen och tar inte betalt av markägare eller närboende. Hör av er om något
       saknas — svara bara på det här mejlet.</p>
    <p style="margin-top:18px">Vänliga hälsningar,<br><b>Vindkollen</b><br>
       <a href="https://vindkoll.se" style="color:{_BRAND}">vindkoll.se</a></p>
  </div>
</div>"""


def build_lead_notice_html(lead, partner) -> str:
    """Besked till leadet om vem som fått uppgifterna.

    Samtycket på sajten talar om "utvalda samarbetspartner" utan att namnge
    någon. Det här mejlet namnger mottagaren i efterhand, vilket både är det
    ärliga och det praktiska: den som inte vill bli uppringd säger till direkt
    i stället för att bli irriterad när telefonen ringer.
    """
    name = (lead.name or "").strip()
    hej = f"Hej {name}," if name else "Hej,"
    kind_label = PARTNER_KINDS.get(partner.kind, {}).get("label", partner.kind)
    return f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:560px;margin:auto;color:#1e293b">
  <div style="background:{_BRAND};color:#fff;padding:20px 22px;border-radius:12px 12px 0 0">
    <h2 style="margin:0;font-size:19px">Vi har förmedlat din förfrågan</h2>
  </div>
  <div style="border:1px solid #e2e8f0;border-top:0;border-radius:0 0 12px 12px;padding:22px">
    <p>{hej}</p>
    <p>Du bad oss förmedla kontakt, och nu har vi gjort det. Dina uppgifter har lämnats
       till:</p>
    <p style="background:#ecfdf5;border:1px solid #a7f3d0;border-radius:10px;padding:14px 16px">
      <b style="font-size:16px">{partner.name}</b><br>
      <span style="color:#047857">{kind_label}</span>
    </p>
    <p>De hör av sig direkt till dig. Vi är inte part i det som händer sedan — du bestämmer
       själv om du går vidare, och du är inte bunden till någonting.</p>
    <p style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:12px 14px;
              font-size:14px">Vill du <b>inte</b> bli kontaktad, eller vill du att vi tar bort
       dina uppgifter? Svara på det här mejlet så ordnar vi det — och hör av dig till oss
       även om kontakten inte sköts som den ska.</p>
    <p style="margin-top:20px">Vänliga hälsningar,<br><b>Vindkollen</b><br>
       <a href="https://vindkoll.se" style="color:{_BRAND}">vindkoll.se</a></p>
  </div>
</div>"""


def build_proposal_html(lead, matches, rejected, base_url, token_for) -> str:
    """Blocket som läggs in i ägarnotisen: föreslagen mottagare + godkännandelänk.

    Det här är hela poängen med motorn — du ska kunna se förslaget i mobilen och
    trycka en gång, i stället för att leta upp rätt partner och skriva mejlet.
    """
    if not matches:
        if not rejected:
            return ('<div style="font-family:Segoe UI,Arial,sans-serif;max-width:600px;'
                    'background:#f1f5f9;border:1px solid #cbd5e1;border-radius:10px;'
                    'padding:14px 16px;margin-top:14px;color:#475569">'
                    '<b>Ingen partner att matcha mot ännu.</b><br>'
                    'Lägg upp en partner via /api/partners så föreslås mottagare automatiskt '
                    'nästa gång.</div>')
        rows = "".join(
            f'<li style="margin-bottom:4px">{p.name}: {", ".join(r)}</li>'
            for p, r in rejected[:6]
        )
        return (f'<div style="font-family:Segoe UI,Arial,sans-serif;max-width:600px;'
                f'background:#fffbeb;border:1px solid #fde68a;border-radius:10px;'
                f'padding:14px 16px;margin-top:14px;color:#78350f">'
                f'<b>Ingen matchande partner för det här leadet.</b>'
                f'<ul style="margin:8px 0 0;padding-left:18px;font-size:13px">{rows}</ul></div>')

    per_kind = best_per_group(matches)
    forst, koade = split_by_order([p for p in per_kind if p.auto_send])
    koade_ids = {p.id for p in koade}

    blocks = []
    for p in per_kind[:3]:
        token = token_for(p)
        kind_label = PARTNER_KINDS.get(p.kind, {}).get("label", p.kind)
        ordning = ""
        if p.id in koade_ids:
            ordning = (f'<div style="font-size:12px;color:#b45309;margin-top:6px">'
                       f'Köad — skickas automatiskt om {HOLD_DAYS} dagar, så att '
                       f'rådgivaren hinner först. Knappen skickar direkt om du vill '
                       f'gå före.</div>')
        elif p in forst and is_legal(p.kind):
            ordning = ('<div style="font-size:12px;color:#047857;margin-top:6px">'
                       'Skickas först — markägaren ska vara rådgiven innan '
                       'projektören hör av sig.</div>')
        button = (
            f'<a href="{base_url}/handover/{token}" style="display:inline-block;margin-top:12px;'
            f'background:{_BRAND};color:#fff;text-decoration:none;padding:11px 18px;'
            f'border-radius:8px;font-weight:700">Granska och skicka →</a>'
            if token else
            '<div style="margin-top:12px;font-size:13px;color:#b45309">Ingen '
            'godkännandelänk: INTERNAL_API_KEY saknas i miljön.</div>'
        )
        # Alternativen är de som konkurrerar om samma uppdrag, inte bara de med
        # exakt samma partnertyp — en lantbruksekonom är ett alternativ till en
        # jurist för markägaren som vill ha hjälp med avtalet.
        alternatives = [x.name for x in matches
                        if competition_group(x.kind) == competition_group(p.kind)
                        and x.id != p.id][:3]
        alt_html = (f'<div style="font-size:12px;color:#64748b;margin-top:8px">Alternativ: '
                    f'{", ".join(alternatives)}</div>' if alternatives else "")
        blocks.append(f"""
  <div style="border-top:1px solid #a7f3d0;padding-top:14px;margin-top:14px">
    <div style="font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:#047857">
      {kind_label}
    </div>
    <div style="font-size:18px;font-weight:800;color:#065f46;margin:4px 0 2px">{p.name}</div>
    <div style="font-size:13px;color:#047857">{p.email}</div>
    {ordning}
    {button}
    {alt_html}
  </div>""")

    return f"""\
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:600px;background:#ecfdf5;
            border:1px solid #a7f3d0;border-radius:10px;padding:16px 18px;margin-top:14px">
  <div style="font-size:15px;font-weight:800;color:#065f46">
    Föreslagna mottagare ({len(per_kind)})
  </div>
  <div style="font-size:12px;color:#64748b;margin-top:4px">
    Inget skickas förrän du bekräftat på sidan som öppnas.
  </div>
  {"".join(blocks)}
</div>"""


def build_confirmation_page(lead, partner, token: str, sent_at: Optional[datetime]) -> str:
    """Bekräftelsesidan bakom godkännandelänken.

    GET får aldrig skicka något: mejlklienter och säkerhetsskannrar förhandshämtar
    länkar, och en sådan hämtning skulle annars lämna ut personuppgifter av sig
    själv. Därför visar GET bara vad som kommer att hända — utskicket sker på POST.
    """
    if sent_at:
        body = (f'<p class="done">Redan överlämnat till {partner.name} '
                f'{sent_at.strftime("%Y-%m-%d %H:%M")}.</p>')
    else:
        body = f"""
      <form method="post" action="/api/handover/{token}/send">
        <button type="submit">Skicka leadet till {partner.name}</button>
      </form>
      <p class="fine">Mejlet går till {partner.email}. Uppgifterna nedan lämnas ut.</p>"""

    stage = vk_leads.PROJECT_STAGES.get((lead.project_stage or "").lower(), {}).get("label", "—")
    return f"""<!DOCTYPE html>
<html lang="sv"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="robots" content="noindex, nofollow"/>
<title>Överlämning av lead | Vindkollen</title>
<style>
  body {{ font-family: -apple-system, Segoe UI, Arial, sans-serif; background:#030712;
         color:#e2e8f0; margin:0; padding:24px; }}
  .card {{ max-width:520px; margin:0 auto; background:#0f172a; border:1px solid #1e293b;
           border-radius:16px; padding:24px; }}
  h1 {{ font-size:20px; margin:0 0 4px; }}
  .sub {{ color:#94a3b8; font-size:14px; margin-bottom:20px; }}
  table {{ width:100%; border-collapse:collapse; font-size:14px; margin-bottom:20px; }}
  td {{ padding:6px 0; border-bottom:1px solid #1e293b; }}
  td:first-child {{ color:#94a3b8; width:45%; }}
  button {{ width:100%; background:#059669; color:#fff; border:0; border-radius:10px;
            padding:15px; font-size:16px; font-weight:700; }}
  .fine {{ color:#64748b; font-size:12px; margin-top:12px; }}
  .done {{ color:#34d399; font-weight:600; }}
</style></head>
<body><div class="card">
  <h1>Överlämna lead</h1>
  <div class="sub">{vk_leads.segment_label(lead.segment)} · {lead.county or '—'} ·
      {lead.lead_tier or '?'}·{lead.lead_score or 0}</div>
  <table>
    <tr><td>Namn</td><td>{lead.name or '—'}</td></tr>
    <tr><td>E-post</td><td>{lead.email}</td></tr>
    <tr><td>Telefon</td><td>{lead.phone or '—'}</td></tr>
    <tr><td>Fastighet</td><td>{lead.property_address or '—'}</td></tr>
    <tr><td>Areal (ha)</td><td>{lead.land_hectares or '—'}</td></tr>
    <tr><td>Status</td><td>{stage}</td></tr>
    <tr><td>Samtycke</td><td>{'Ja' if lead.consent_partner_share else 'NEJ'}</td></tr>
  </table>
  {body}
</div></body></html>"""
