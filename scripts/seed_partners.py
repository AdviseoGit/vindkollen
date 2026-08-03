"""
Laddar partners_seed.json in i partnerregistret.

    python scripts/seed_partners.py --key $INTERNAL_API_KEY
    python scripts/seed_partners.py --key ... --base-url http://127.0.0.1:8099 --dry-run

Rader utan e-postadress hoppas över och listas på slutet — fyll i dem i
partners_seed.json och kör om. Skriptet är idempotent: /api/partners matchar på
namn, så en andra körning uppdaterar i stället för att skapa dubletter.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEED = os.path.join(ROOT, "partners_seed.json")

# Fält som /api/partners tar emot. Allt annat i seed-filen (email_kalla m.m.)
# är anteckningar till dig och skickas inte.
API_FIELDS = {
    "name", "kind", "email", "contact_name", "segments", "counties", "elareas",
    "min_score", "monthly_cap", "priority", "exclusive", "requires_consent",
    "auto_send", "active", "notes",
}


def post(base_url, key, payload):
    req = urllib.request.Request(
        f"{base_url}/api/partners",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "X-API-KEY": key},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return True, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.read().decode('utf-8', 'ignore')[:200]}"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", default=os.environ.get("INTERNAL_API_KEY"),
                    help="INTERNAL_API_KEY (annars från miljön)")
    ap.add_argument("--base-url", default="https://vindkoll.se")
    ap.add_argument("--dry-run", action="store_true",
                    help="visa vad som skulle skickas, rör inte registret")
    ap.add_argument("--no-auto-send", action="store_true",
                    help="tvinga auto_send=false på alla, oavsett seed-filen")
    args = ap.parse_args()

    if not args.key and not args.dry_run:
        sys.exit("Ingen API-nyckel. Ange --key eller sätt INTERNAL_API_KEY.")

    with open(SEED, encoding="utf-8") as f:
        rows = json.load(f)["partners"]

    created, skipped, failed = [], [], []
    for row in rows:
        payload = {k: v for k, v in row.items() if k in API_FIELDS}
        if not payload.get("email"):
            skipped.append((row["name"], row.get("email_kalla", "")))
            continue
        if args.no_auto_send:
            payload["auto_send"] = False

        auto = "AUTO" if payload.get("auto_send") else "manuell"
        region = payload.get("counties") or payload.get("elareas") or "hela landet"
        if args.dry_run:
            print(f"  [torrkörning] {row['name']:26} {payload['kind']:8} {region:14} {auto}")
            created.append(row["name"])
            continue

        ok, res = post(args.base_url, args.key, payload)
        if ok:
            print(f"  OK   {row['name']:26} {payload['kind']:8} {region:14} {auto}")
            created.append(row["name"])
        else:
            print(f"  FEL  {row['name']:26} {res}")
            failed.append((row["name"], res))

    print(f"\n{len(created)} partners {'skulle laddas' if args.dry_run else 'i registret'}.")

    if skipped:
        print(f"\n{len(skipped)} hoppades över — saknar e-postadress:")
        for name, source in skipped:
            print(f"  · {name}")
            if source:
                print(f"      {source}")
        print("\n  Fyll i 'email' i partners_seed.json och kör om.")

    if failed:
        sys.exit(f"\n{len(failed)} misslyckades.")


if __name__ == "__main__":
    main()
