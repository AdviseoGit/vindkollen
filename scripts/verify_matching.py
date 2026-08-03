"""
Verifierar matchning och överlämning end-to-end mot en riktig Postgres.

Kör den efter ändringar i matching.py eller lead-flödet. Mailern byts mot en
attrapp, så inget lämnar maskinen — men databasen, endpointsen och signeringen
är på riktigt.

    DATABASE_URL=postgresql://... python scripts/verify_matching.py

Skapar och städar bort sina egna testpartners och testleads.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("INTERNAL_API_KEY", "verify-key")
os.environ.setdefault("PUBLIC_BASE_URL", "http://testserver")
if not os.environ.get("DATABASE_URL"):
    sys.exit("DATABASE_URL måste vara satt (en databas du får skriva testdata i).")

import mailer  # noqa: E402

SENT = []
mailer.send_email = lambda to, subj, html, **kw: (SENT.append((to, subj, html)), (True, "sent"))[1]
mailer.notify_owner = lambda subj, html, **kw: (SENT.append(("OWNER", subj, html)), (True, "sent"))[1]

import main  # noqa: E402

main.mailer = mailer
from fastapi.testclient import TestClient  # noqa: E402

KEY = {"X-API-KEY": os.environ["INTERNAL_API_KEY"]}
PREFIX = "ZZ-verify"
ok_count = 0


def check(label, condition, detail=""):
    global ok_count
    status = "OK  " if condition else "FEL "
    print(f"  {status} {label}{(' — ' + str(detail)) if detail else ''}")
    if not condition:
        sys.exit(f"\nVerifieringen misslyckades: {label}")
    ok_count += 1


with TestClient(main.app) as c:
    print("\nLägger upp testpartners")
    for spec in [
        {"name": f"{PREFIX} Projektör Norr", "kind": "projektor",
         "email": "zz-projektor@zz-verify.example.se", "elareas": "SE1,SE2", "min_score": 50},
        {"name": f"{PREFIX} Jurist BD", "kind": "jurist",
         "email": "zz-jurist@zz-verify.example.se", "counties": "Norrbotten", "min_score": 40},
        {"name": f"{PREFIX} Projektör Syd", "kind": "projektor",
         "email": "zz-syd@zz-verify.example.se", "elareas": "SE4"},
    ]:
        r = c.post("/api/partners", headers=KEY, json=spec)
        check(f"partner {spec['name']}", r.status_code == 200)
    check("okänd partnertyp avvisas",
          c.post("/api/partners", headers=KEY,
                 json={"name": "x", "kind": "astrolog", "email": "a@b.se"}).status_code == 422)

    print("\nLead med samtycke, både juridik- och projektörsintresse")
    r = c.post("/api/lead/qualify", json={
        "email": "zz-verify-markagare@zz-verify.example.se", "segment": "markagare",
        "name": "Verify", "phone": "070", "county": "Norrbotten", "municipality": "Piteå",
        "property_address": "Granliden 1:29", "land_hectares": 300,
        "project_stage": "forhandlar", "timeframe": "nu", "wants_legal_help": True,
        "wants_projector_contact": True, "consent_partner_share": True,
        "source": f"{PREFIX}"})
    check("lead sparat", r.status_code == 200, r.text[:120])

    owner = [s for s in SENT if s[0] == "OWNER"][-1][2]
    links = re.findall(r'href="http://testserver/handover/([^"]+)"', owner)
    check("ägarmejlet föreslår en mottagare per partnertyp", len(links) == 2, f"{len(links)} länkar")

    before = len(SENT)
    check("GET på godkännandelänken svarar", c.get(f"/handover/{links[0]}").status_code == 200)
    check("GET skickar INGET mejl (mejlskannrar förhandshämtar länkar)", len(SENT) == before)
    check("manipulerad token avvisas",
          c.get("/handover/1-2-deadbeefdeadbeefdeadbeefdeadbeef").status_code == 404)

    print("\nÖverlämning")
    for token in links:
        check("POST skickar", c.post(f"/api/handover/{token}/send").status_code == 200,
              SENT[-1][0])
    handover = SENT[-1][2]
    check("mejlet bär fastighet, areal och samtyckesrad",
          all(x in handover for x in ("Granliden 1:29", "300", "samtyckt")))
    check("samma länk igen ger 409",
          c.post(f"/api/handover/{links[0]}/send").status_code == 409)

    print("\nSpärrar")
    c.post("/api/lead/qualify", json={
        "email": "zz-verify-utan@zz-verify.example.se", "segment": "markagare",
        "county": "Norrbotten", "land_hectares": 200, "wants_projector_contact": True,
        "consent_partner_share": False, "source": PREFIX})
    lead_id = [a for a in c.get("/api/assignments", headers=KEY).json()["assignments"]][0]["lead_id"]
    matches = c.get(f"/api/leads/{lead_id + 1}/matches", headers=KEY).json()
    check("lead utan samtycke matchar ingen", matches["matches"] == [],
          matches["rejected"][0]["reasons"][0] if matches["rejected"] else "")

    print(f"\n{ok_count} kontroller OK")
    print("Städa testdata med:")
    print("  DELETE FROM vindkollen_lead_assignments WHERE partner_id IN "
          f"(SELECT id FROM vindkollen_partners WHERE name LIKE '{PREFIX}%');")
    print(f"  DELETE FROM vindkollen_partners WHERE name LIKE '{PREFIX}%';")
    print("  DELETE FROM vindkollen_leads WHERE email LIKE 'zz-verify-%';")
