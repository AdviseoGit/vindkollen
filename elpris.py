"""Elpris per elområde från ENTSO-E Transparency Platform.

Kalkylatorerna ska räkna på ett pris vi kan visa källan till, inte på ett
tal besökaren skriver in själv. Här hämtas dagen-före-priserna (A44) för
SE1–SE4, räknas om från EUR/MWh till öre/kWh med Riksbankens dagskurs och
slås ihop till snitt för de tre senaste tolvmånadersperioderna.

Går hämtningen inte att göra (ingen nyckel, ENTSO-E nere) gäller FALLBACK:
2024 års snittpris, samma tal som regeringen räknar med i prop. 2025/26:239.
"""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone

ENTSOE_URL = "https://web-api.tp.entsoe.eu/api"
RIKSBANK_URL = "https://api.riksbank.se/swea/v1/Observations/SEKEURPMI/{start}/{end}"

ZONES = {
    "SE1": "10Y1001A1001A44P",
    "SE2": "10Y1001A1001A45N",
    "SE3": "10Y1001A1001A46L",
    "SE4": "10Y1001A1001A47J",
}

YEARS = 3
MONTHS_SV = ["jan", "feb", "mar", "apr", "maj", "jun",
             "jul", "aug", "sep", "okt", "nov", "dec"]

FALLBACK = {
    "source": "fallback",
    "source_label": "2024 års snittpris per elområde (prop. 2025/26:239)",
    "period_label": "2024",
    "updated_at": None,
    "areas": {
        "SE1": {"price": 28.7, "low": 28.7, "high": 28.7},
        "SE2": {"price": 28.0, "low": 28.0, "high": 28.0},
        "SE3": {"price": 41.0, "low": 41.0, "high": 41.0},
        "SE4": {"price": 57.0, "low": 57.0, "high": 57.0},
    },
}

_state = {"data": None, "error": None, "attempt_at": None}


def current() -> dict:
    """Det som kalkylatorerna ska räkna på just nu."""
    return _state["data"] or FALLBACK


def status() -> dict:
    return {"error": _state["error"], "attempt_at": _state["attempt_at"]}


def _get(url: str, timeout: int = 60) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "vindkoll.se"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _parse_dt(value: str) -> datetime:
    return datetime.strptime(value.strip(), "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)


def _resolution_minutes(value: str) -> int:
    return {"PT15M": 15, "PT30M": 30, "PT60M": 60, "P1D": 1440}.get(value.strip(), 60)


def parse_periods(xml_bytes: bytes) -> dict:
    """{periodstart: (snittpris EUR/MWh, timmar)} ur ett A44-svar.

    Saknade positioner betyder att föregående pris gäller (curveType A03).
    Samma period kan komma i flera upplösningar; då tas snittet av dem.
    """
    root = ET.fromstring(xml_bytes)
    if _local(root.tag).startswith("Acknowledgement"):
        reason = " ".join(
            (el.text or "").strip() for el in root.iter() if _local(el.tag) == "text"
        )
        raise ValueError(f"ENTSO-E: {reason[:200] or 'inget svar'}")

    found = {}
    for period in root.iter():
        if _local(period.tag) != "Period":
            continue
        start = end = None
        minutes = 60
        points = {}
        for el in period:
            name = _local(el.tag)
            if name == "timeInterval":
                for part in el:
                    if _local(part.tag) == "start":
                        start = _parse_dt(part.text)
                    elif _local(part.tag) == "end":
                        end = _parse_dt(part.text)
            elif name == "resolution":
                minutes = _resolution_minutes(el.text)
            elif name == "Point":
                pos = price = None
                for part in el:
                    if _local(part.tag) == "position":
                        pos = int(part.text)
                    elif _local(part.tag) == "price.amount":
                        price = float(part.text)
                if pos is not None and price is not None:
                    points[pos] = price
        if not (start and end and points):
            continue
        slots = int((end - start).total_seconds() // (minutes * 60))
        total, last = 0.0, None
        counted = 0
        for pos in range(1, slots + 1):
            last = points.get(pos, last)
            if last is None:
                continue
            total += last
            counted += 1
        if not counted:
            continue
        hours = (end - start).total_seconds() / 3600
        found.setdefault(start, []).append((total / counted, hours))

    return {
        start: (sum(a for a, _ in vals) / len(vals), vals[0][1])
        for start, vals in found.items()
    }


def _fetch_zone(token: str, eic: str, start: datetime, end: datetime) -> dict:
    query = urllib.parse.urlencode({
        "securityToken": token,
        "documentType": "A44",
        "in_Domain": eic,
        "out_Domain": eic,
        "periodStart": start.strftime("%Y%m%d%H%M"),
        "periodEnd": end.strftime("%Y%m%d%H%M"),
    })
    try:
        return parse_periods(_get(f"{ENTSOE_URL}?{query}"))
    except urllib.error.HTTPError as exc:
        # Aldrig str(exc) eller adressen i felet: nyckeln står i adressen.
        body = b""
        try:
            body = exc.read()
        except Exception:  # noqa: BLE001
            pass
        reason = ""
        try:
            parse_periods(body)
        except ValueError as inner:
            reason = str(inner)
        except Exception:  # noqa: BLE001
            pass
        raise ValueError(reason or f"ENTSO-E svarade {exc.code}") from None
    except urllib.error.URLError:
        raise ValueError("ENTSO-E gick inte att nå") from None


def _fetch_rates(start: date, end: date) -> dict:
    url = RIKSBANK_URL.format(start=start.isoformat(), end=end.isoformat())
    try:
        rows = json.loads(_get(url))
    except Exception:  # noqa: BLE001
        raise ValueError("Riksbankens växelkurs gick inte att hämta") from None
    rates = {date.fromisoformat(r["date"]): float(r["value"]) for r in rows}
    if not rates:
        raise ValueError("Riksbanken gav inga växelkurser")
    return rates


def _rate_for(day: date, rates: dict, first: date) -> float:
    """Dagens kurs, annars närmast föregående bankdag."""
    probe = day
    while probe >= first:
        if probe in rates:
            return rates[probe]
        probe -= timedelta(days=1)
    return rates[min(rates)]


def _shift_years(d: datetime, years: int) -> datetime:
    return d.replace(year=d.year - years)


def _label(start: datetime, end: datetime) -> str:
    last = end - timedelta(days=1)
    return (f"{MONTHS_SV[start.month - 1]} {start.year}–"
            f"{MONTHS_SV[last.month - 1]} {last.year}")


def refresh() -> dict:
    """Hämta nya priser. Blockerande; körs i trådpool. Kastar aldrig."""
    _state["attempt_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    token = os.environ.get("ENTSOE_TOKEN", "").strip()
    if not token:
        _state["error"] = "ENTSOE_TOKEN saknas"
        return current()
    try:
        now = datetime.now(timezone.utc)
        end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        windows = [(_shift_years(end, k + 1), _shift_years(end, k)) for k in range(YEARS)]
        first_day = (windows[-1][0] - timedelta(days=10)).date()
        rates = _fetch_rates(first_day, end.date())

        areas = {}
        for zone, eic in ZONES.items():
            yearly = []
            for w_start, w_end in windows:
                periods = _fetch_zone(token, eic, w_start, w_end)
                weighted = hours = 0.0
                for p_start, (eur, h) in periods.items():
                    if not (w_start <= p_start < w_end):
                        continue
                    # Leveransdygnet börjar 22:00 eller 23:00 UTC dagen före.
                    day = (p_start + timedelta(hours=3)).date()
                    weighted += eur * _rate_for(day, rates, first_day) * h
                    hours += h
                # Under 90 % av årets timmar är inget årssnitt.
                if hours < 0.9 * (w_end - w_start).total_seconds() / 3600:
                    raise ValueError(f"För lite prisdata för {zone} {_label(w_start, w_end)}")
                yearly.append(weighted / hours / 10)  # SEK/MWh → öre/kWh
            areas[zone] = {
                "price": round(yearly[0], 1),
                "low": round(min(yearly), 1),
                "high": round(max(yearly), 1),
            }

        _state["data"] = {
            "source": "entsoe",
            "source_label": "ENTSO-E Transparency Platform, dagen-före-pris, "
                            "omräknat med Riksbankens kurs",
            "period_label": _label(*windows[0]),
            "span_label": _label(windows[-1][0], windows[0][1]),
            "updated_at": _state["attempt_at"],
            "areas": areas,
        }
        _state["error"] = None
    except ValueError as exc:
        _state["error"] = str(exc)[:300]
    except Exception as exc:  # noqa: BLE001 — får aldrig fälla appen
        _state["error"] = type(exc).__name__
    return current()
