"""
Branschkatalogen: vilka aktörer som finns i ett område.

Skild från partnerregistret med flit. Registret säger vem som *får ta emot*
leads; katalogen säger vem som *finns* i regionen. När ett lead kommer in och
registret är tunt för just det området plockar ägarnotisen kandidater härifrån
— så fylls listan på i takt med att leads kommer, i stället för att någon ska
lägga in hela branschen i förväg.

Katalogen skickar aldrig något själv. Den föreslår.
"""

import json
import os
from typing import List, Optional

import leads as vk_leads
import matching as vk_matching

_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "directory.json")
_CACHE: Optional[list] = None


def load() -> list:
    """Läs katalogen. Cachas — filen ändras bara vid deploy."""
    global _CACHE
    if _CACHE is None:
        try:
            with open(_PATH, encoding="utf-8") as f:
                _CACHE = json.load(f).get("aktorer", [])
        except Exception as exc:  # noqa: BLE001
            print(f"[directory] kunde inte läsa katalogen: {exc}")
            _CACHE = []
    return _CACHE


def _covers(entry: dict, lead) -> bool:
    """Täcker aktören leadets område? Tom täckning = hela landet."""
    counties = vk_matching._csv_set(entry.get("counties"))
    elareas = vk_matching._csv_set(entry.get("elareas"))
    if not counties and not elareas:
        return True
    if lead.county and lead.county in counties:
        return True
    return bool(lead.elarea and lead.elarea in elareas)


def _relevant_kinds(lead) -> set:
    """Vilka sorters aktörer är relevanta för just det här leadet?

    Utgår från vad personen faktiskt bett om — en projektör föreslås inte för
    någon som bara vill ha juridisk hjälp, och tvärtom.
    """
    segment = vk_leads.normalise_segment(lead.segment)
    kinds = set()
    if segment == "markagare":
        if getattr(lead, "wants_projector_contact", False):
            kinds.add("projektor")
        if getattr(lead, "wants_legal_help", False):
            kinds.update(("jurist", "radgivare"))
    elif segment == "narboende":
        if getattr(lead, "wants_legal_help", False):
            kinds.update(("jurist", "radgivare"))
    elif segment == "kommun":
        kinds.add("kommunradgivning")
    return kinds


def candidates_for(lead, known_names: set, limit: int = 6) -> List[dict]:
    """Aktörer i leadets område som ännu inte finns i partnerregistret.

    Sorteras med de regionalt specifika först — en aktör med tyngdpunkt i
    leadets elområde är en bättre första kontakt än en rikstäckande — och
    därefter de vi har en belagd adress till, eftersom de går att aktivera direkt.
    """
    kinds = _relevant_kinds(lead)
    if not kinds:
        return []

    träffar = [
        e for e in load()
        if e.get("kind") in kinds
        and e.get("name") not in known_names
        and _covers(e, lead)
    ]

    def specificitet(e):
        if vk_matching._csv_set(e.get("counties")):
            return 2
        if vk_matching._csv_set(e.get("elareas")):
            return 1
        return 0

    segment = vk_leads.normalise_segment(lead.segment)

    def profilerad(e):
        """Aktörer som uttryckligen passar leadets silo går före de generella.
        En jurist som arbetar med inlösen är rätt för en närboende; en
        arrendejurist är det inte."""
        segments = vk_matching._csv_set(e.get("segments"))
        return 0 if segment in segments else 1

    träffar.sort(key=lambda e: (
        -specificitet(e),
        profilerad(e),
        0 if e.get("email") else 1,
        0 if e.get("sakerhet") == "bekraftad" else 1,
        e.get("name", ""),
    ))
    return träffar[:limit]


def build_suggestions_html(lead, kandidater: List[dict], base_url: str,
                           token_for=None) -> str:
    """Blocket i ägarnotisen: vilka i området som går att kontakta.

    Har vi en belagd adress följer en knapp som lägger till aktören i registret
    och skickar leadet direkt. Saknas adressen får du länken till deras sida —
    då är nästa steg att hämta adressen, inte att gissa den.
    """
    if not kandidater:
        return ""

    region = lead.county or lead.elarea or "området"
    rader = []
    for e in kandidater:
        etikett = vk_matching.PARTNER_KINDS.get(e["kind"], {}).get("label", e["kind"])
        tackning = e.get("counties") or e.get("elareas") or "hela landet"
        osaker = ('<span style="color:#b45309"> · uppgiften bör stämmas av</span>'
                  if e.get("sakerhet") != "bekraftad" else "")

        if e.get("email") and token_for:
            token = token_for(e)
            handling = (
                f'<a href="{base_url}/katalog/{token}" style="display:inline-block;'
                f'margin-top:8px;background:#0f766e;color:#fff;text-decoration:none;'
                f'padding:8px 14px;border-radius:7px;font-weight:700;font-size:13px">'
                f'Lägg till och skicka →</a>'
            ) if token else ""
        else:
            handling = (
                f'<a href="{e.get("url", "#")}" style="font-size:13px;color:#0f766e">'
                f'Hämta kontaktuppgift →</a>'
            )

        rader.append(f"""
    <div style="border-top:1px solid #e2e8f0;padding:12px 0">
      <div style="font-weight:700">{e['name']}</div>
      <div style="font-size:12px;color:#64748b">{etikett} · {tackning}{osaker}</div>
      <div style="font-size:13px;color:#475569;margin-top:4px">{e.get('note', '')}</div>
      {handling}
    </div>""")

    return f"""
<div style="font-family:Segoe UI,Arial,sans-serif;max-width:600px;background:#f8fafc;
            border:1px solid #cbd5e1;border-radius:10px;padding:16px 18px;margin-top:14px">
  <div style="font-size:15px;font-weight:800;color:#0f172a">
    Aktörer i {region} att kontakta
  </div>
  <div style="font-size:12px;color:#64748b;margin-top:4px">
    Ur branschkatalogen — de finns inte i registret ännu och har inte fått det här
    leadet. Lägger du till någon här får de framtida leads i samma område automatiskt.
  </div>
  {''.join(rader)}
</div>"""
