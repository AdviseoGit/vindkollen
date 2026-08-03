"""
Hämtar publicerade kontaktadresser från aktörernas egna sidor.

Katalogen känner till bolagen men saknar adress till de flesta. Att leta upp
dem för hand är det sista manuella steget i kedjan — det här gör det i stället.

Två principer:

1. Bara adresser som bolaget själv publicerat på sin egen sida, och bara om
   domänen stämmer. Vi gissar aldrig, och vi plockar aldrig upp en adress som
   råkar ligga i en tredjepartswidget.
2. En hittad adress är ett *förslag*, inte ett faktum. Den måste bekräftas
   innan ett lead skickas dit, eftersom det som skickas är en markägares namn,
   telefon och fastighetsbeteckning.

Ren stdlib — ingen ny dependency för något som körs en gång per aktör.
"""

import gzip
import io
import re
import urllib.error
import urllib.request
from typing import List, Optional, Tuple
from urllib.parse import urljoin, urlparse

MAX_BYTES = 600_000
TIMEOUT = 12
UA = "Mozilla/5.0 (compatible; VindkollenBot/1.0; +https://vindkoll.se/om-sajten)"

# Sidor som brukar bära kontaktuppgifter, om huvudsidan inte gör det.
KONTAKTVAGAR = ("", "/kontakt", "/kontakta-oss", "/kontakt/", "/om-oss/kontakt",
                "/contact", "/contact-us")

_MAILTO = re.compile(r'mailto:([^"\'>?\s]+)', re.I)
_EPOST = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')

# Adresser som aldrig ska ta emot ett lead även om de står på sidan.
SKRAP = ("noreply", "no-reply", "donotreply", "webmaster", "postmaster", "abuse",
         "sentry", "wixpress", "example.", "@2x", ".png", ".jpg", ".webp", ".svg")

# Lägre är bättre. Styr vilken adress som föreslås när sidan har flera.
ROLLVIKT = [
    (("markagare", "mark@", "arrende"), 0),   # bäst: någon som faktiskt ska ha detta
    (("info@", "kontakt@", "hej@", "kontakta@"), 1),
    (("kansli", "reception", "office@"), 2),
    (("press", "media", "jobb", "job", "rekrytering", "karriar"), 8),
    (("faktura", "ekonomi", "invoice", "gdpr", "dataskydd", "kundservice"), 9),
]


def _hamta(url: str) -> Optional[str]:
    """Hämta en sida som text. Returnerar None vid fel — aldrig ett undantag."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": UA,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "sv,en;q=0.8",
            "Accept-Encoding": "gzip",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            rå = r.read(MAX_BYTES)
            if r.headers.get("Content-Encoding") == "gzip":
                try:
                    rå = gzip.GzipFile(fileobj=io.BytesIO(rå)).read()
                except Exception:  # noqa: BLE001 — trunkerad gzip, ta det vi har
                    pass
            return rå.decode("utf-8", "ignore")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError, ValueError) as e:
        print(f"[contacts] {url}: {e}")
        return None


def _registrerbar_domän(värd: str) -> str:
    """example.co.uk -> co.uk är fel, men för svenska sajter räcker två nivåer."""
    delar = (värd or "").lower().replace("www.", "").split(".")
    return ".".join(delar[-2:]) if len(delar) >= 2 else värd


def _rollvikt(epost: str) -> int:
    e = epost.lower()
    for nycklar, vikt in ROLLVIKT:
        if any(n in e for n in nycklar):
            return vikt
    return 5  # namngiven person: användbar, men generella adressen är stabilare


def extrahera(html: str, sid_url: str) -> List[str]:
    """Adresser på sidan, rankade. Bara sådana som hör till sidans egen domän."""
    if not html:
        return []
    hittade = set()
    for m in _MAILTO.findall(html):
        hittade.add(m.split("?")[0].strip())
    hittade.update(_EPOST.findall(html))

    domän = _registrerbar_domän(urlparse(sid_url).netloc)
    rena = []
    for e in hittade:
        e = e.strip().strip(".,;:").lower()
        if not e or len(e) > 120 or any(s in e for s in SKRAP):
            continue
        if _registrerbar_domän(e.split("@")[-1]) != domän:
            continue  # tredjepartsadress eller byråns egen — inte bolagets
        rena.append(e)

    rena = sorted(set(rena), key=lambda e: (_rollvikt(e), len(e)))
    return rena


def hitta_adress(url: str) -> Tuple[Optional[str], Optional[str], List[str]]:
    """Leta upp bästa kontaktadress för en aktör.

    Returnerar (bästa adress, sidan den hittades på, alla kandidater).
    Provar först den angivna sidan, sedan vanliga kontaktsökvägar på samma domän.
    """
    if not url:
        return None, None, []

    bas = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    provade = []
    for väg in KONTAKTVAGAR:
        sida = url if väg == "" else urljoin(bas, väg)
        if sida in provade:
            continue
        provade.append(sida)
        kandidater = extrahera(_hamta(sida) or "", sida)
        if kandidater:
            return kandidater[0], sida, kandidater
    return None, None, []
