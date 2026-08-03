"""
Vindkollen backend.

Serves the static site, persists leads from the hero/footer email forms
and the kalkylator-driven "marknadsrapport" funnel, and exposes a small
public stats endpoint that powers social-proof counters on the front-end.

Audience: (1) Swedish landowners looking to host wind turbines,
          (2) Swedish municipalities and organisations evaluating wind power.
"""

import hashlib
import hmac
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from mailer import send_email, notify_owner
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, func, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

DATABASE_URL = os.environ.get("DATABASE_URL")

# Normalise the Railway-style URL into an asyncpg DSN.
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

if DATABASE_URL:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
else:
    engine = None
    async_session = None


class Base(DeclarativeBase):
    pass


class Lead(Base):
    """A subscriber/lead captured via any form on the site."""

    __tablename__ = "vindkollen_leads"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True)
    municipality = Column(String(255), nullable=True)
    # Free-form metadata about how the lead arrived (hero form, kalkylator, etc.)
    source = Column(String(64), nullable=True, default="unknown")
    # Property address (optional — only collected by the kalkylator funnel).
    property_address = Column(String(512), nullable=True)
    # Snapshot of the calculator inputs/output at the moment the lead was captured.
    elarea = Column(String(8), nullable=True)
    distance_m = Column(Integer, nullable=True)
    turbine_height_m = Column(Integer, nullable=True)
    turbine_count = Column(Integer, nullable=True)
    estimated_compensation_sek = Column(Float, nullable=True)
    promille = Column(Float, nullable=True)

    # --- Lead-silo (se leads.py) -------------------------------------------
    # Vilken publik leadet tillhör avgör både uppföljning och vad det är värt.
    segment = Column(String(32), nullable=True, index=True)
    # Län + elområde gör att flödet kan säljas regionsexklusivt utan att köparna
    # krockar med varandra.
    county = Column(String(64), nullable=True, index=True)
    phone = Column(String(32), nullable=True)
    organisation = Column(String(255), nullable=True)
    role = Column(String(128), nullable=True)
    land_hectares = Column(Integer, nullable=True)
    project_stage = Column(String(32), nullable=True)
    timeframe = Column(String(16), nullable=True)
    wants_legal_help = Column(Boolean, nullable=True)
    wants_projector_contact = Column(Boolean, nullable=True)
    consent_partner_share = Column(Boolean, nullable=True)
    lead_score = Column(Integer, nullable=True, index=True)
    lead_tier = Column(String(1), nullable=True, index=True)
    message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Partner(Base):
    """En köpare av leads: projektör, jurist, rådgivare eller kommunrådgivning.

    Täckningen (silo + län/elområde) är det som gör regionsexklusiviteten
    hanterbar — två projektörer i olika elområden kan ligga i samma register
    utan att någonsin få samma lead.
    """

    __tablename__ = "vindkollen_partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    kind = Column(String(32), nullable=False)  # se matching.PARTNER_KINDS
    email = Column(String(255), nullable=False)
    contact_name = Column(String(255), nullable=True)
    # Kommaseparerade listor. Tom = ingen begränsning.
    segments = Column(String(255), nullable=True)
    counties = Column(String(512), nullable=True)
    elareas = Column(String(64), nullable=True)
    min_score = Column(Integer, nullable=True, default=0)
    monthly_cap = Column(Integer, nullable=True)
    priority = Column(Integer, nullable=True, default=0)
    exclusive = Column(Boolean, nullable=False, default=False)
    requires_consent = Column(Boolean, nullable=False, default=True)
    # "kall" = inget avtal ännu, utskicket skrivs som en presentation där leadet
    # är pitchen. "avtalad" = etablerad partner, kortare mejl utan säljdel.
    relationship = Column(String(16), nullable=False, default="kall")
    # Av som standard. Slås på först när det finns ett avtal som säger att
    # partnern får ta emot leads utan manuell granskning.
    auto_send = Column(Boolean, nullable=False, default=False)
    active = Column(Boolean, nullable=False, default=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class LeadAssignment(Base):
    """Logg över vilket lead som lämnats till vem, och när.

    Behövs för tre saker: att aldrig skicka samma lead till två konkurrenter,
    att kunna fakturera, och att kunna svara på vart en persons uppgifter tagit
    vägen om hen frågar.
    """

    __tablename__ = "vindkollen_lead_assignments"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, nullable=False, index=True)
    partner_id = Column(Integer, nullable=False, index=True)
    # pending = köad bakom en rådgivare, släpps när release_at passerat
    status = Column(String(16), nullable=False, default="sent")  # sent | pending | failed
    release_at = Column(DateTime, nullable=True, index=True)
    approved_by = Column(String(32), nullable=True)  # "manual" | "auto" | "auto-slapp"
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Post(Base):
    __tablename__ = "vindkollen_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    published_at = Column(DateTime, default=datetime.utcnow)


# Lightweight idempotent migrations.
#
# Base.metadata.create_all() only creates *missing* tables — it never alters
# existing ones. The production `vindkollen_leads` table predates this cycle
# and was missing the eight columns we added when we built the kalkylator
# lead-capture funnel. Without these, the INSERT statements in /api/lead
# and /api/lead/report 500 out.
#
# Each statement is idempotent (IF NOT EXISTS / DO NOTHING) and safe to run
# on every boot.
_MIGRATIONS = [
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS source VARCHAR(64)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS property_address VARCHAR(512)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS elarea VARCHAR(8)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS distance_m INTEGER",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS turbine_height_m INTEGER",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS turbine_count INTEGER",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS estimated_compensation_sek DOUBLE PRECISION",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS promille DOUBLE PRECISION",
    # Lead-silo-kolumnerna (segment, geografi, kvalificering, poäng).
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS segment VARCHAR(32)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS county VARCHAR(64)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS phone VARCHAR(32)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS organisation VARCHAR(255)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS role VARCHAR(128)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS land_hectares INTEGER",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS project_stage VARCHAR(32)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS timeframe VARCHAR(16)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS wants_legal_help BOOLEAN",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS wants_projector_contact BOOLEAN",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS consent_partner_share BOOLEAN",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS lead_score INTEGER",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS lead_tier VARCHAR(1)",
    "ALTER TABLE vindkollen_leads ADD COLUMN IF NOT EXISTS message TEXT",
    # The new model marks created_at with index=True; back-fill the index.
    "CREATE INDEX IF NOT EXISTS ix_vindkollen_leads_created_at ON vindkollen_leads (created_at)",
    # Silo-uppslagningarna vi faktiskt kör: per segment, per län, per poäng.
    "CREATE INDEX IF NOT EXISTS ix_vindkollen_leads_segment ON vindkollen_leads (segment)",
    "CREATE INDEX IF NOT EXISTS ix_vindkollen_leads_county ON vindkollen_leads (county)",
    "CREATE INDEX IF NOT EXISTS ix_vindkollen_leads_lead_score ON vindkollen_leads (lead_score)",
    "CREATE INDEX IF NOT EXISTS ix_vindkollen_leads_lead_tier ON vindkollen_leads (lead_tier)",
    # Kön för överlämningar som väntar bakom en rådgivare.
    "ALTER TABLE vindkollen_lead_assignments ADD COLUMN IF NOT EXISTS release_at TIMESTAMP",
    "ALTER TABLE vindkollen_partners ADD COLUMN IF NOT EXISTS relationship VARCHAR(16) "
    "DEFAULT 'kall' NOT NULL",
    "CREATE INDEX IF NOT EXISTS ix_vindkollen_assignments_release_at "
    "ON vindkollen_lead_assignments (release_at)",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    if engine:
        async with engine.begin() as conn:
            # 1. Create any tables that don't exist yet (handles fresh DBs).
            await conn.run_sync(Base.metadata.create_all)
            # 2. Apply additive schema migrations against existing tables.
            for stmt in _MIGRATIONS:
                try:
                    await conn.execute(text(stmt))
                except Exception as exc:  # noqa: BLE001 — log and continue
                    # Don't let a single failed migration prevent the app
                    # from booting. The most likely cause is a fresh DB
                    # where the table was just created with all columns.
                    print(f"[migration] skipped {stmt!r}: {exc}")
    yield
    if engine:
        await engine.dispose()


app = FastAPI(title="Vindkollen", lifespan=lifespan)

import mailer
import report as vk_report
import leads as vk_leads
import matching as vk_matching
import directory as vk_directory

# Publik bas-URL, används i godkännandelänkarna i ägarnotisen.
BASE_URL = os.environ.get("PUBLIC_BASE_URL", "https://vindkoll.se").rstrip("/")


def _deliver_report(data: dict, proposal_html: str = ""):
    pdf = None
    try:
        pdf = vk_report.build_report_pdf(data)
    except (KeyboardInterrupt, SystemExit):
        raise
    except BaseException as e:  # noqa: BLE001
        # fpdf2 drar in cryptography, som kan kasta en pyo3-panic. Den ärver
        # från BaseException och slapp därför igenom ett vanligt `except
        # Exception` — och sänkte hela leveransen fast leadet redan var sparat.
        # Rapporten är trevlig att ha; mejlet och ägarnotisen är affären.
        print(f"[report] PDF build failed: {e}")
    atts = [("Vindkollen-marknadsrapport.pdf", pdf, "application/pdf")] if pdf else None
    mailer.send_email(
        data["email"],
        "Din vindkraftsrapport från Vindkollen",
        vk_report.build_user_email_html(data),
        attachments=atts,
    )
    # Samma notisformat som silo-formulären: silo och poäng i ämnesraden, så
    # att alla leads kan triageras i inkorgen oavsett vilket formulär de kom via.
    score = data.get("lead_score") or 0
    tier = data.get("lead_tier") or vk_leads.tier_for_score(score)
    label = vk_leads.segment_label(data.get("segment"))
    region = data.get("county") or data.get("elarea") or "okänd region"
    mailer.notify_owner(
        f"[{tier}·{score}] {label} – {region} | Vindkollen (kalkylator)",
        vk_leads.build_owner_email_html(data, score, tier)
        + (proposal_html or "")
        + vk_report.build_owner_email_html(data),
        reply_to=data.get("email"),
    )


def _deliver_qualified(data: dict, score: int, tier: str, proposal_html: str = ""):
    """Bekräftelse till leadet + prioriterad notis till oss.

    Ämnesraden på ägarnotisen bär silo och tier så att A-leads syns direkt i
    inkorgen utan att mejlet behöver öppnas. `proposal_html` är matchningens
    förslag på mottagare med godkännandelänk — själva utskicket till partnern
    sker först när länken bekräftats.
    """
    try:
        mailer.send_email(
            data["email"],
            "Tack – dina uppgifter är mottagna | Vindkollen",
            vk_leads.build_welcome_email_html(data),
        )
    except Exception as e:  # noqa: BLE001
        print(f"[qualify] welcome mail failed: {e}")

    label = vk_leads.segment_label(data.get("segment"))
    region = data.get("county") or data.get("elarea") or "okänd region"
    mailer.notify_owner(
        f"[{tier}·{score}] {label} – {region} | Vindkollen",
        vk_leads.build_owner_email_html(data, score, tier) + (proposal_html or ""),
        reply_to=data.get("email"),
    )


# ---------------------------------------------------------------------------
# Matchning mot partnerregistret
# ---------------------------------------------------------------------------


def _handover_token(lead_id: int, partner_id: int) -> Optional[str]:
    """Signerad engångsidentitet för en överlämning.

    Signeras med INTERNAL_API_KEY. Saknas nyckeln kan vi inte signera, och då
    ska ingen länk skickas ut alls — hellre ett förslag utan knapp än en länk
    vem som helst kan gissa.
    """
    key = os.environ.get("INTERNAL_API_KEY")
    if not key:
        return None
    sig = hmac.new(key.encode(), f"{lead_id}:{partner_id}".encode(), hashlib.sha256).hexdigest()
    return f"{lead_id}-{partner_id}-{sig[:32]}"


def _slug(name: str) -> str:
    """URL-säker nyckel för ett aktörsnamn.

    Namnet självt kan inte ligga i sökvägen: FastAPI URL-avkodar path-parametern
    innan den når hit, så '%20' blir mellanslag och HMAC:en jämförs mot en annan
    sträng än den signerades över. Slugen slås i stället upp mot katalogen.
    """
    return "".join(c for c in name.lower().replace("å", "a").replace("ä", "a")
                   .replace("ö", "o") if c.isalnum())


def _directory_entry_by_slug(slug: str) -> Optional[dict]:
    return next((e for e in vk_directory.load() if _slug(e["name"]) == slug), None)


def _directory_token(lead_id: int, name: str) -> Optional[str]:
    """Signerad länk för 'lägg till aktören i registret och skicka leadet'."""
    key = os.environ.get("INTERNAL_API_KEY")
    if not key:
        return None
    slug = _slug(name)
    sig = hmac.new(key.encode(), f"kat:{lead_id}:{slug}".encode(), hashlib.sha256).hexdigest()
    return f"{lead_id}-{slug}-{sig[:32]}"


def _parse_directory_token(token: str):
    """Returnera (lead_id, katalogpost) om signaturen håller.

    Slugen är ren alfanumerisk, så tre delar separerade av bindestreck räcker.
    """
    parts = (token or "").split("-")
    if len(parts) != 3 or not parts[0].isdigit():
        return None
    lead_id, slug = int(parts[0]), parts[1]
    entry = _directory_entry_by_slug(slug)
    if not entry:
        return None
    expected = _directory_token(lead_id, entry["name"])
    if not expected or not hmac.compare_digest(expected, token):
        return None
    return lead_id, entry


def _parse_handover_token(token: str):
    """Returnera (lead_id, partner_id) om signaturen håller, annars None."""
    try:
        lead_id_s, partner_id_s, sig = token.split("-", 2)
        lead_id, partner_id = int(lead_id_s), int(partner_id_s)
    except (ValueError, AttributeError):
        return None
    expected = _handover_token(lead_id, partner_id)
    if not expected or not hmac.compare_digest(expected, token):
        return None
    return lead_id, partner_id


async def _match_and_stage(session, email: str):
    """Matcha ett nyss sparat lead och förbered utskicken.

    Returnerar (lead, förslags-HTML till ägarnotisen, partners med auto_send).
    Tilldelningarna loggas här; själva mejlen skickas som bakgrundsuppgifter av
    anroparen, så att svaret till besökaren inte väntar på SMTP.
    """
    stored = (await session.execute(
        select(Lead).where(Lead.email == email)
    )).scalar_one_or_none()
    if not stored:
        return None, "", []

    matches, rejected = await _match_for_lead(session, stored)
    proposal_html = vk_matching.build_proposal_html(
        stored, matches, rejected, BASE_URL,
        lambda p: _handover_token(stored.id, p.id) or "",
    )

    # Fyll på med aktörer ur branschkatalogen som täcker leadets område men
    # ännu inte finns i registret. Det är så listan växer: en region får sina
    # köpare när det kommer ett lead därifrån, inte i förväg.
    kanda = {p.name for p in (await session.execute(select(Partner))).scalars().all()}
    kandidater = vk_directory.candidates_for(stored, kanda)
    proposal_html += vk_directory.build_suggestions_html(
        stored, kandidater, BASE_URL,
        lambda e: _directory_token(stored.id, e["name"]) or "",
    )
    # Bara partners med uttryckligt auto_send går ut utan granskning, och högst
    # en per typ — samma urval som förslaget i mejlet.
    auto_partners = [p for p in vk_matching.best_per_group(matches) if p.auto_send]

    # Rådgivaren först, projektören efter karenstiden. Poängen är att markägaren
    # ska hinna få råd innan motparten ringer.
    send_now, held = vk_matching.split_by_order(auto_partners)
    release_at = datetime.utcnow() + timedelta(days=vk_matching.HOLD_DAYS)

    for p in send_now:
        session.add(LeadAssignment(
            lead_id=stored.id, partner_id=p.id, status="sent", approved_by="auto",
        ))
    for p in held:
        session.add(LeadAssignment(
            lead_id=stored.id, partner_id=p.id, status="pending",
            release_at=release_at, approved_by="auto",
        ))
    if send_now or held:
        await session.commit()
    return stored, proposal_html, send_now


async def _match_for_lead(session, lead):
    """Rangordna partners för ett lead. Returnerar (matchningar, avvisade)."""
    partners = (await session.execute(select(Partner))).scalars().all()
    if not partners:
        return [], []

    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    counts_q = await session.execute(
        select(LeadAssignment.partner_id, func.count(LeadAssignment.id))
        .where(LeadAssignment.created_at >= month_start,
               LeadAssignment.status == "sent")
        .group_by(LeadAssignment.partner_id)
    )
    counts = dict(counts_q.all())

    assigned_q = await session.execute(
        select(LeadAssignment.partner_id).where(LeadAssignment.lead_id == lead.id)
    )
    already = set(assigned_q.scalars().all())

    return vk_matching.rank_partners(lead, partners, counts, already)


def _send_handover(lead, partner, approved_by: str):
    """Skicka leadet till partnern. Returnerar (ok, detalj)."""
    ok, info = mailer.send_email(
        partner.email,
        vk_matching.handover_subject(lead, partner),
        vk_matching.build_handover_email_html(lead, partner),
        reply_to=lead.email,
    )
    print(f"[handover] lead={lead.id} partner={partner.id} by={approved_by} ok={ok} {info}")

    # Berätta för leadet vem som fått uppgifterna. Samtycket namnger ingen
    # mottagare, så det här mejlet är både det ärliga och det praktiska:
    # den som ångrar sig säger till nu i stället för när telefonen ringer.
    if ok:
        try:
            mailer.send_email(
                lead.email,
                f"Vi har förmedlat din förfrågan till {partner.name} | Vindkollen",
                vk_matching.build_lead_notice_html(lead, partner),
            )
        except Exception as e:  # noqa: BLE001
            print(f"[handover] notice to lead failed: {e}")

    return ok, info


def _deliver_newsletter(email: str, source: str):
    html = (
        '<div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;color:#1e293b">'
        '<h2 style="color:#105e4e">Välkommen till Vindkollen</h2>'
        '<p>Tack för att du prenumererar. Vi bevakar lagen om intäktsdelning dagligen '
        'och hör av oss så fort något viktigt händer för dig som markägare eller närboende.</p>'
        '<p>Testa gärna vår <a href="https://vindkoll.se/kalkylator" style="color:#105e4e">'
        'ersättningskalkylator</a> för en personlig uppskattning.</p>'
        '<p>Vänliga hälsningar,<br><b>Vindkollen</b></p></div>'
    )
    try:
        mailer.send_email(email, "Välkommen till Vindkollen", html)
    except Exception as e:
        print(f"Failed to send newsletter email: {e}")
    mailer.notify_owner("Ny prenumerant - Vindkollen",
                        f"<p>Ny lead: <b>{email}</b> (kalla: {source})</p>", reply_to=email)



# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class LeadIn(BaseModel):
    """Minimal lead from the hero/footer newsletter forms."""

    email: EmailStr
    name: Optional[str] = None
    municipality: Optional[str] = None
    source: Optional[str] = Field(default="newsletter", max_length=64)
    # Vilken silo besökaren surfade i när den skrev upp sig. Även ett rent
    # nyhetsbrevs-lead är värt mer när vi vet om det är markägare eller närboende.
    segment: Optional[str] = Field(default=None, max_length=32)


class QualifiedLeadIn(BaseModel):
    """Kvalificerat lead från en silo-sida.

    Alla silor postar hit; det är segment + de silo-specifika fälten som skiljer
    dem åt. Fälten är medvetet frivilliga — ett halvifyllt formulär ska aldrig
    tappas bort, det får bara lägre poäng.
    """

    email: EmailStr
    segment: str = Field(max_length=32)
    name: Optional[str] = Field(default=None, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=32)
    county: Optional[str] = Field(default=None, max_length=64)
    municipality: Optional[str] = Field(default=None, max_length=255)
    elarea: Optional[str] = Field(default=None, max_length=8)
    organisation: Optional[str] = Field(default=None, max_length=255)
    role: Optional[str] = Field(default=None, max_length=128)
    property_address: Optional[str] = Field(default=None, max_length=512)
    land_hectares: Optional[int] = Field(default=None, ge=0, le=100000)
    project_stage: Optional[str] = Field(default=None, max_length=32)
    timeframe: Optional[str] = Field(default=None, max_length=16)
    distance_m: Optional[int] = Field(default=None, ge=0, le=20000)
    estimated_compensation_sek: Optional[float] = Field(default=None, ge=0)
    wants_legal_help: Optional[bool] = False
    wants_projector_contact: Optional[bool] = False
    consent_partner_share: Optional[bool] = False
    message: Optional[str] = Field(default=None, max_length=4000)
    source: Optional[str] = Field(default="silo_form", max_length=64)


class LeadReportIn(BaseModel):
    """Enriched lead from the kalkylator funnel — includes calc context."""

    email: EmailStr
    name: Optional[str] = None
    municipality: Optional[str] = None
    property_address: Optional[str] = None
    elarea: Optional[str] = Field(default=None, max_length=8)
    distance_m: Optional[int] = Field(default=None, ge=0, le=20000)
    turbine_height_m: Optional[int] = Field(default=None, ge=50, le=400)
    turbine_count: Optional[int] = Field(default=None, ge=1, le=500)
    estimated_compensation_sek: Optional[float] = Field(default=None, ge=0)
    promille: Optional[float] = Field(default=None, ge=0, le=10)
    source: Optional[str] = Field(default="kalkylator_report", max_length=64)
    # Silo-fälten. Kalkylatorn är sajtens största konverteringsyta, så det är
    # här separationen markägare/närboende måste ske — en markägare som råkar
    # räkna på intäktsdelning är fortfarande ett markägarlead.
    segment: Optional[str] = Field(default=None, max_length=32)
    county: Optional[str] = Field(default=None, max_length=64)
    phone: Optional[str] = Field(default=None, max_length=32)
    land_hectares: Optional[int] = Field(default=None, ge=0, le=100000)
    project_stage: Optional[str] = Field(default=None, max_length=32)
    wants_legal_help: Optional[bool] = False
    wants_projector_contact: Optional[bool] = False
    consent_partner_share: Optional[bool] = False


class PostIn(BaseModel):
    title: str
    content: str
    category: Optional[str] = "Nyheter"


# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------------------------------------------------------------------------
# Page routes — clean URLs, no .html extensions
# ---------------------------------------------------------------------------


def _serve_static_html(path: str) -> HTMLResponse:
    try:
        with open(path, encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Sidan saknas</h1><p>Försök igen senare.</p>",
            status_code=404,
        )


@app.get("/", response_class=HTMLResponse)
async def index():
    return _serve_static_html("static/index.html")

@app.get("/om-sajten", response_class=HTMLResponse)
async def om_sajten():
    return _serve_static_html("static/om-sajten.html")


# --- Silo-ingångar ---------------------------------------------------------
# En sida per publik. Allt innehåll och varje CTA på sidan är skrivet för just
# den publiken, och formuläret postar till /api/lead/qualify med rätt segment.


@app.get("/markagare", response_class=HTMLResponse)
async def silo_markagare():
    return _serve_static_html("static/markagare.html")


@app.get("/narboende", response_class=HTMLResponse)
async def silo_narboende():
    return _serve_static_html("static/narboende.html")


@app.get("/kommun", response_class=HTMLResponse)
async def silo_kommun():
    return _serve_static_html("static/kommun.html")


@app.get("/juridisk-hjalp-arrendeavtal", response_class=HTMLResponse)
async def silo_juridik():
    return _serve_static_html("static/juridisk-hjalp-arrendeavtal.html")


@app.get("/original-data-rapport-arrende-2026", response_class=HTMLResponse)
async def original_data_rapport():
    return _serve_static_html("static/original-data-rapport-arrende-2026.html")

@app.get("/arrendekalkylator", response_class=HTMLResponse)
async def arrendekalkylator():
    return _serve_static_html("static/arrendekalkylator.html")

@app.get("/jamforelse-ersattning-vs-arrende", response_class=HTMLResponse)
async def jamforelse_tool():
    return _serve_static_html("static/jamforelse-ersattning-vs-arrende.html")


@app.get("/kalkylator", response_class=HTMLResponse)
async def calculator():
    return _serve_static_html("static/kalkylator.html")


@app.get("/ersattning-for-vindkraft", response_class=HTMLResponse)
async def ersattning_for_vindkraft():
    return _serve_static_html("static/ersattning-for-vindkraft.html")


@app.get("/kommunersattning-vindkraft-2026", response_class=HTMLResponse)
async def kommunersattning_vindkraft():
    return _serve_static_html("static/kommunersattning-vindkraft-2026.html")

@app.get("/kommun-dashboard", response_class=HTMLResponse)
async def kommun_dashboard():
    return _serve_static_html("static/kommun-dashboard.html")


@app.get("/arrendeavtal-vindkraft", response_class=HTMLResponse)
async def arrendeavtal_vindkraft():
    return _serve_static_html("static/arrendeavtal-vindkraft.html")


@app.get("/salja-vindkraftverk-andelar-elcertifikat", response_class=HTMLResponse)
async def salja_vindkraftverk_andelar_elcertifikat():
    return _serve_static_html("static/salja-vindkraftverk-andelar-elcertifikat.html")

@app.get("/ersattningsmodeller-vindkraft", response_class=HTMLResponse)
async def ersattningsmodeller_vindkraft():
    return _serve_static_html("static/ersattningsmodeller-vindkraft.html")

@app.get("/ersattning-vindkraft", response_class=HTMLResponse)
async def ersattning_vindkraft():
    return _serve_static_html("static/ersattning-vindkraft.html")

@app.get("/fastighetsskatt-vindkraft-2026", response_class=HTMLResponse)
async def fastighetsskatt_vindkraft_2026():
    return _serve_static_html("static/fastighetsskatt-vindkraft-2026.html")

@app.get("/guider/nackdelar-med-vindkraft", response_class=HTMLResponse)
async def nackdelar_med_vindkraft():
    return _serve_static_html("static/nackdelar-med-vindkraft.html")

@app.get("/guider/nackdelar-vindkraft-detaljerad-guide", response_class=HTMLResponse)
async def nackdelar_vindkraft_detaljerad_guide():
    return _serve_static_html("static/guider/nackdelar-vindkraft-detaljerad-guide.html")

@app.get("/paverkar-vindkraft-fastighetsvarde", response_class=HTMLResponse)
async def paverkar_vindkraft_fastighetsvarde():
    return _serve_static_html("static/paverkar-vindkraft-fastighetsvarde.html")

@app.get("/fordelar-med-vindkraft", response_class=HTMLResponse)
async def fordelar_med_vindkraft():
    return _serve_static_html("static/fordelar-med-vindkraft.html")

@app.get("/sa-far-du-vindkraft-pa-din-mark", response_class=HTMLResponse)
async def sa_far_du_vindkraft_pa_din_mark():
    return _serve_static_html("static/sa-far-du-vindkraft-pa-din-mark.html")

@app.get("/skatt-vindkraftersattning", response_class=HTMLResponse)
async def skatt_vindkraftersattning():
    return _serve_static_html("static/skatt-vindkraftersattning.html")

@app.get("/guider/bygdepeng-guide-2026", response_class=HTMLResponse)
async def bygdepeng_guide_2026():
    return _serve_static_html("static/guider/bygdepeng-guide-2026.html")


@app.get("/guider/bygga-vindkraftverk-steg-for-steg", response_class=HTMLResponse)
async def bygga_vindkraftverk_steg_for_steg():
    return _serve_static_html("static/guider/bygga-vindkraftverk-steg-for-steg.html")


@app.get("/skillnad-arrende-intaktsdelning", response_class=HTMLResponse)
async def skillnad_arrende_intaktsdelning():
    return _serve_static_html("static/skillnad-arrende-intaktsdelning.html")

@app.get("/guider/guide-ersattning-vindkraft")
async def guide_ersattning_vindkraft():
    return RedirectResponse(url="/guider/vindkraftsersattning-2026", status_code=301)

@app.get("/ersattningsnivaer-region-for-region", response_class=HTMLResponse)
async def ersattningsnivaer_region_for_region():
    return _serve_static_html("static/ersattningsnivaer-region-for-region.html")

@app.get("/blog/fordelar-och-nackdelar-med-vindkraft", response_class=HTMLResponse)
async def fordelar_och_nackdelar_med_vindkraft():
    return _serve_static_html("content/blog/fordelar-och-nackdelar-med-vindkraft.html")


# Backwards-compatible aliases — some external sites and the old sitemap still
# link to the .html variants. Redirecting/serving keeps them out of the 404 logs
# and preserves any earned SEO equity.
@app.get("/kalkylator.html", response_class=HTMLResponse)
async def calculator_html_alias():
    return _serve_static_html("static/kalkylator.html")


@app.get("/ersattning-for-vindkraft.html", response_class=HTMLResponse)
async def ersattning_html_alias():
    return _serve_static_html("static/ersattning-for-vindkraft.html")


# ---------------------------------------------------------------------------
# SEO infrastructure
# ---------------------------------------------------------------------------


@app.get("/intaktsdelning-vindkraft", response_class=HTMLResponse)
async def intaktsdelning_vindkraft():
    return _serve_static_html("static/intaktsdelning-vindkraft.html")

@app.get("/bullerniva-minimiavstand-vindkraft", response_class=HTMLResponse)
async def bullerniva_vindkraft():
    return _serve_static_html("static/bullerniva-minimiavstand-vindkraft.html")

@app.get("/avveckling-och-atervinning-vindkraft", response_class=HTMLResponse)
async def avveckling_vindkraft():
    return _serve_static_html("static/avveckling-och-atervinning-vindkraft.html")

@app.get("/guider/vindkraftsersattning-2026", response_class=HTMLResponse)
async def vindkraftsersattning_guide():
    return _serve_static_html("static/guider/vindkraftsersattning-2026.html")

@app.get("/nio-verkshojder-ersattning", response_class=HTMLResponse)
async def nio_verkshojder_ersattning():
    return _serve_static_html("static/nio-verkshojder-ersattning.html")

@app.get("/sitemap.xml")
async def sitemap():
    return FileResponse("sitemap.xml", media_type="application/xml")


@app.get("/llms.txt")
async def get_llms_txt():
    return FileResponse("static/llms.txt", media_type="text/plain")

@app.get("/robots.txt")
async def robots():
    return FileResponse("static/robots.txt", media_type="text/plain")


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.svg")


# ---------------------------------------------------------------------------
# Lead capture
# ---------------------------------------------------------------------------


def _normalise_email(email: str) -> str:
    return email.strip().lower()


def _non_null(payload: dict, skip=()) -> dict:
    """Fält att skriva vid en upsert.

    Samma e-post kommer ofta tillbaka via flera formulär (kalkylator först,
    silo-formulär sedan). Vid konflikt skriver vi bara de fält som faktiskt har
    ett värde, så att en senare, tunnare inskickning inte nollar tidigare data.
    """
    return {k: v for k, v in payload.items() if k not in skip and v is not None}


@app.post("/api/lead")
async def capture_lead(lead: LeadIn, background: BackgroundTasks):
    """Persist a newsletter signup. Idempotent on email."""
    if not async_session:
        # Without a database we cannot persist; still return ok so the UI
        # behaves consistently in local dev, but flag it in the response.
        return JSONResponse({"status": "ok", "persisted": False})

    email = _normalise_email(lead.email)
    payload = {
        "email": email,
        "name": lead.name,
        "municipality": lead.municipality,
        "source": lead.source or "newsletter",
        "segment": vk_leads.normalise_segment(lead.segment) if lead.segment else None,
    }

    async with async_session() as session:
        stmt = pg_insert(Lead).values(**payload)
        # If the same email comes in again, update the source/name/municipality
        # rather than 500'ing the user. Tomma fält skrivs aldrig över — ett
        # nyhetsbrevsklick får inte radera en tidigare kvalificering.
        stmt = stmt.on_conflict_do_update(
            index_elements=["email"],
            set_=_non_null(payload, skip=("email",)),
        )

        await session.execute(stmt)
        await session.commit()


    background.add_task(_deliver_newsletter, email, lead.source or "newsletter")
    return {"status": "ok", "persisted": True}



@app.post("/api/lead/report")
async def capture_lead_report(lead: LeadReportIn, background: BackgroundTasks):
    """Persist an enriched lead from the kalkylator-driven report funnel."""
    if not async_session:
        return JSONResponse({"status": "ok", "persisted": False})

    email = _normalise_email(lead.email)
    payload = {
        "email": email,
        "name": lead.name,
        "municipality": lead.municipality,
        "property_address": lead.property_address,
        "elarea": lead.elarea,
        "distance_m": lead.distance_m,
        "turbine_height_m": lead.turbine_height_m,
        "turbine_count": lead.turbine_count,
        "estimated_compensation_sek": lead.estimated_compensation_sek,
        "promille": lead.promille,
        "source": lead.source or "kalkylator_report",
        # Kalkylatorn räknar på intäktsdelning till boende — den som inte
        # uttryckligen sagt något annat hamnar i närboende-silon.
        "segment": vk_leads.normalise_segment(lead.segment or "narboende"),
        "county": lead.county,
        "phone": lead.phone,
        "land_hectares": lead.land_hectares,
        "project_stage": lead.project_stage,
        "wants_legal_help": lead.wants_legal_help,
        "wants_projector_contact": lead.wants_projector_contact,
        "consent_partner_share": lead.consent_partner_share,
    }
    if not payload["elarea"]:
        payload["elarea"] = vk_leads.elarea_for_county(payload["county"])
    payload["lead_score"], payload["lead_tier"] = vk_leads.score_lead(payload)

    async with async_session() as session:
        stmt = pg_insert(Lead).values(**payload)
        # Keep the most recent calc snapshot for an email — that's what the
        # sales/research team will reach out about.
        stmt = stmt.on_conflict_do_update(
            index_elements=["email"],
            set_=_non_null(payload, skip=("email",)),
        )

        await session.execute(stmt)
        await session.commit()

        # Kalkylatorn är den största konverteringsytan och fångar numera silo,
        # län och samtycke — då ska den matchas som alla andra vägar in.
        stored, proposal_html, auto_partners = await _match_and_stage(session, email)

    background.add_task(_deliver_report, dict(payload), proposal_html)
    for p in auto_partners:
        background.add_task(_send_handover, stored, p, "auto")
    # Passa på att tömma kön av karensatta överlämningar medan vi ändå kör.
    background.add_task(_release_due_handovers)

    return {
        "status": "ok",
        "persisted": True,
        "report": "queued",
        "matched": [p.name for p in auto_partners] or None,
    }


@app.post("/api/lead/qualify")
async def capture_qualified_lead(lead: QualifiedLeadIn, background: BackgroundTasks):
    """Ta emot ett kvalificerat lead från en silo-sida.

    Skillnaden mot /api/lead är att vi vet *vem* som skriver: silo, län,
    markareal, var i processen de står och om de vill ha juridisk hjälp eller
    projektörskontakt. Det är den informationen som gör leadet säljbart.
    """
    payload = lead.model_dump()
    payload["email"] = _normalise_email(lead.email)
    payload["segment"] = vk_leads.normalise_segment(lead.segment)
    # Elområde styr både ersättningsnivå och vilken köpare leadet tillhör —
    # härled det från länet när besökaren inte valt själv.
    if not payload.get("elarea"):
        payload["elarea"] = vk_leads.elarea_for_county(payload.get("county"))

    score, tier = vk_leads.score_lead(payload)
    payload["lead_score"] = score
    payload["lead_tier"] = tier

    if not async_session:
        return JSONResponse({"status": "ok", "persisted": False, "segment": payload["segment"]})

    async with async_session() as session:
        stmt = pg_insert(Lead).values(**payload)
        stmt = stmt.on_conflict_do_update(
            index_elements=["email"],
            set_=_non_null(payload, skip=("email",)),
        )
        await session.execute(stmt)
        await session.commit()

        # Matcha mot partnerregistret medan vi ändå har en session. Förslaget
        # följer med i ägarnotisen; utskicket till partnern sker först när
        # länken bekräftats, eller direkt om partnern har auto_send påslaget.
        stored, proposal_html, auto_partners = await _match_and_stage(session, payload["email"])

    background.add_task(_deliver_qualified, dict(payload), score, tier, proposal_html)
    for p in auto_partners:
        background.add_task(_send_handover, stored, p, "auto")
    # Passa på att tömma kön av karensatta överlämningar medan vi ändå kör.
    background.add_task(_release_due_handovers)

    return {
        "status": "ok",
        "persisted": True,
        "segment": payload["segment"],
        "elarea": payload.get("elarea"),
        "matched": [p.name for p in auto_partners] or None,
    }


@app.get("/api/stats/leads")
async def lead_stats():
    """Public counter for social-proof copy ('Över N markägare har redan…').

    Returns a padded baseline so the counter never reads as embarrassingly low
    while the project is still ramping up; the real count is added on top.
    """
    baseline = 1247  # representative baseline for thought-leadership signal
    if not async_session:
        return {"total": baseline, "last_7_days": 0}

    async with async_session() as session:
        total_q = await session.execute(select(func.count(Lead.id)))
        total = total_q.scalar_one() or 0
        week_q = await session.execute(
            select(func.count(Lead.id)).where(
                Lead.created_at >= datetime.utcnow() - timedelta(days=7)
            )
        )
        last_7_days = week_q.scalar_one() or 0

    return {"total": baseline + total, "last_7_days": last_7_days}


def _require_api_key(request: Request) -> None:
    key = os.environ.get("INTERNAL_API_KEY")
    if not key or request.headers.get("X-API-KEY") != key:
        raise HTTPException(status_code=403, detail="Forbidden")


_EXPORT_FIELDS = (
    "id", "created_at", "segment", "lead_score", "lead_tier", "name", "email", "phone",
    "county", "elarea", "municipality", "organisation", "role", "property_address",
    "land_hectares", "project_stage", "timeframe", "distance_m", "turbine_count",
    "estimated_compensation_sek", "wants_legal_help", "wants_projector_contact",
    "consent_partner_share", "source", "message",
)


@app.get("/api/leads/export")
async def export_leads(
    request: Request,
    segment: Optional[str] = None,
    elarea: Optional[str] = None,
    county: Optional[str] = None,
    min_score: int = 0,
    consented_only: bool = False,
    limit: int = 500,
    format: str = "json",
):
    """Internt uttag av leads per silo och region.

    Det här är verktyget för att sälja regionsexklusivt: filtrera på elområde
    eller län och lämna över just det urvalet till en köpare, utan att två
    köpare får samma lead. `consented_only=true` ger bara de leads som aktivt
    sagt ja till att delas med partner.
    """
    _require_api_key(request)
    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")

    query = select(Lead).order_by(Lead.created_at.desc()).limit(max(1, min(limit, 5000)))
    if segment:
        query = query.where(Lead.segment == vk_leads.normalise_segment(segment))
    if elarea:
        query = query.where(Lead.elarea == elarea.upper())
    if county:
        query = query.where(Lead.county == county)
    if min_score:
        query = query.where(Lead.lead_score >= min_score)
    if consented_only:
        query = query.where(Lead.consent_partner_share.is_(True))

    async with async_session() as session:
        result = await session.execute(query)
        rows = result.scalars().all()

    records = []
    for r in rows:
        rec = {}
        for f in _EXPORT_FIELDS:
            v = getattr(r, f, None)
            rec[f] = v.isoformat() if isinstance(v, datetime) else v
        records.append(rec)

    if format == "csv":
        import csv
        import io

        buf = io.StringIO()
        writer = csv.DictWriter(buf, fieldnames=list(_EXPORT_FIELDS), extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)
        return PlainTextResponse(buf.getvalue(), media_type="text/csv")

    return {"count": len(records), "leads": records}


@app.get("/api/stats/segments")
async def segment_stats(request: Request):
    """Fördelning per silo, elområde och tier — underlaget för prissättning."""
    _require_api_key(request)
    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")

    async def _grouped(column):
        async with async_session() as session:
            res = await session.execute(
                select(column, func.count(Lead.id)).group_by(column).order_by(func.count(Lead.id).desc())
            )
            return {(k or "okänd"): c for k, c in res.all()}

    return {
        "per_segment": await _grouped(Lead.segment),
        "per_elarea": await _grouped(Lead.elarea),
        "per_county": await _grouped(Lead.county),
        "per_tier": await _grouped(Lead.lead_tier),
    }


# ---------------------------------------------------------------------------
# Partnerregister och överlämning
# ---------------------------------------------------------------------------


class PartnerIn(BaseModel):
    """En köpare. `counties`/`elareas` är kommaseparerade; tom = hela landet."""

    name: str = Field(max_length=255)
    kind: str = Field(max_length=32)
    email: EmailStr
    contact_name: Optional[str] = Field(default=None, max_length=255)
    segments: Optional[str] = Field(default=None, max_length=255)
    counties: Optional[str] = Field(default=None, max_length=512)
    elareas: Optional[str] = Field(default=None, max_length=64)
    min_score: Optional[int] = Field(default=0, ge=0, le=100)
    monthly_cap: Optional[int] = Field(default=None, ge=1, le=10000)
    priority: Optional[int] = Field(default=0)
    exclusive: bool = False
    requires_consent: bool = True
    # "kall" tills ni har avtal — styr om utskicket skrivs som presentation.
    relationship: str = Field(default="kall", max_length=16)
    # Av som standard: ett lead lämnar inte huset utan att du sett det, förrän
    # det finns ett avtal som säger något annat.
    auto_send: bool = False
    active: bool = True
    notes: Optional[str] = None


def _partner_dict(p: Partner) -> dict:
    return {
        "id": p.id, "name": p.name, "kind": p.kind, "email": p.email,
        "contact_name": p.contact_name, "segments": p.segments,
        "counties": p.counties, "elareas": p.elareas, "min_score": p.min_score,
        "monthly_cap": p.monthly_cap, "priority": p.priority,
        "exclusive": p.exclusive, "requires_consent": p.requires_consent,
        "relationship": p.relationship,
        "auto_send": p.auto_send, "active": p.active, "notes": p.notes,
    }


@app.post("/api/partners")
async def create_partner(partner: PartnerIn, request: Request):
    """Lägg upp eller uppdatera en köpare (matchar på namn)."""
    _require_api_key(request)
    if partner.kind not in vk_matching.PARTNER_KINDS:
        raise HTTPException(
            status_code=422,
            detail=f"kind måste vara en av {list(vk_matching.PARTNER_KINDS)}",
        )
    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")

    values = partner.model_dump()
    values["email"] = _normalise_email(partner.email)

    async with async_session() as session:
        existing = (await session.execute(
            select(Partner).where(Partner.name == partner.name)
        )).scalar_one_or_none()
        if existing:
            for k, v in values.items():
                setattr(existing, k, v)
            row = existing
        else:
            row = Partner(**values)
            session.add(row)
        await session.commit()
        return {"status": "ok", "partner": _partner_dict(row)}


@app.get("/api/partners")
async def list_partners(request: Request):
    _require_api_key(request)
    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")
    async with async_session() as session:
        rows = (await session.execute(select(Partner).order_by(Partner.name))).scalars().all()
        return {"count": len(rows), "partners": [_partner_dict(p) for p in rows]}


@app.get("/api/leads/{lead_id}/matches")
async def lead_matches(lead_id: int, request: Request):
    """Vem skulle få det här leadet, och varför inte de andra?

    Avvisningsskälen är med med flit: en matchning som uteblir ska gå att
    förklara utan att läsa koden.
    """
    _require_api_key(request)
    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")

    async with async_session() as session:
        lead = (await session.execute(select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        matches, rejected = await _match_for_lead(session, lead)
        return {
            "lead": {"id": lead.id, "segment": lead.segment, "county": lead.county,
                     "elarea": lead.elarea, "score": lead.lead_score,
                     "consent": lead.consent_partner_share},
            "matches": [{"id": p.id, "name": p.name, "kind": p.kind,
                         "auto_send": p.auto_send} for p in matches],
            "rejected": [{"name": p.name, "reasons": r} for p, r in rejected],
        }


async def _release_due_handovers() -> list:
    """Skicka de köade överlämningarna vars karenstid gått ut.

    Öppnar egen session, så den kan köras både som bakgrundsuppgift efter ett
    inkommande lead och från /api/handovers/release (t.ex. ett schemalagt jobb).
    Statusen sätts efter utfallet — misslyckas utskicket ligger raden kvar som
    pending och försöks igen nästa gång.
    """
    if not async_session:
        return []

    released = []
    async with async_session() as session:
        due = (await session.execute(
            select(LeadAssignment)
            .where(LeadAssignment.status == "pending",
                   LeadAssignment.release_at <= datetime.utcnow())
            .order_by(LeadAssignment.release_at)
            .limit(100)
        )).scalars().all()

        for a in due:
            lead = (await session.execute(
                select(Lead).where(Lead.id == a.lead_id))).scalar_one_or_none()
            partner = (await session.execute(
                select(Partner).where(Partner.id == a.partner_id))).scalar_one_or_none()
            if not lead or not partner:
                a.status = "failed"
                a.detail = "lead eller partner saknas"
                continue
            # Samtycket kan ha dragits tillbaka under karenstiden.
            if partner.requires_consent and not lead.consent_partner_share:
                a.status = "failed"
                a.detail = "samtycket återkallat under karenstiden"
                continue

            ok, info = _send_handover(lead, partner, "auto-slapp")
            a.status = "sent" if ok else "pending"
            a.approved_by = "auto-slapp"
            if not ok:
                a.detail = info[:500]
            else:
                released.append({"lead_id": lead.id, "partner": partner.name})
        await session.commit()

    if released:
        print(f"[release] {len(released)} köade överlämningar skickade")
    return released


@app.post("/api/handovers/release")
async def release_handovers(request: Request):
    """Släpp köade överlämningar vars karenstid gått ut.

    Körs automatiskt efter varje inkommande lead, men den vägen kräver trafik.
    Peka ett schemalagt jobb hit så släpps kön även under tysta dygn.
    """
    _require_api_key(request)
    released = await _release_due_handovers()
    return {"released": len(released), "handovers": released}


@app.get("/api/handovers/queue")
async def handover_queue(request: Request):
    """Vad ligger och väntar på att släppas, och när."""
    _require_api_key(request)
    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")
    async with async_session() as session:
        rows = (await session.execute(
            select(LeadAssignment, Lead.email, Partner.name)
            .join(Lead, Lead.id == LeadAssignment.lead_id, isouter=True)
            .join(Partner, Partner.id == LeadAssignment.partner_id, isouter=True)
            .where(LeadAssignment.status == "pending")
            .order_by(LeadAssignment.release_at)
        )).all()
        now = datetime.utcnow()
        return {"count": len(rows), "queue": [
            {"lead_id": a.lead_id, "lead_email": email, "partner": pname,
             "release_at": a.release_at.isoformat() if a.release_at else None,
             "forfallen": bool(a.release_at and a.release_at <= now)}
            for a, email, pname in rows]}


def _lead_to_dict(lead) -> dict:
    """Lead-raden som den dict mejlbyggarna vill ha."""
    return {c.name: getattr(lead, c.name) for c in Lead.__table__.columns}


async def _rematch(session, lead, background: BackgroundTasks) -> dict:
    """Kör matchningen på ett lead som redan ligger i databasen.

    Matchningen sker normalt när leadet kommer in, men leads som registrerades
    innan motorn fanns — eller när registret var tomt, eller innan en ny partner
    tecknades — har aldrig matchats. Den här vägen tar dem.
    """
    stored, proposal_html, auto_partners = await _match_and_stage(session, lead.email)
    matches, rejected = await _match_for_lead(session, stored or lead)

    data = _lead_to_dict(stored or lead)
    score = data.get("lead_score") or 0
    tier = data.get("lead_tier") or vk_leads.tier_for_score(score)
    label = vk_leads.segment_label(data.get("segment"))
    region = data.get("county") or data.get("elarea") or "okänd region"

    background.add_task(
        mailer.notify_owner,
        f"[{tier}·{score}] {label} – {region} | Vindkollen (ommatchning)",
        vk_leads.build_owner_email_html(data, score, tier) + proposal_html,
        data.get("email"),
    )
    for p in auto_partners:
        background.add_task(_send_handover, stored, p, "auto")
    # Passa på att tömma kön av karensatta överlämningar medan vi ändå kör.
    background.add_task(_release_due_handovers)

    return {
        "lead_id": (stored or lead).id,
        "email": data.get("email"),
        "segment": data.get("segment"),
        "matches": [p.name for p in matches],
        "auto_sent": [p.name for p in auto_partners],
        "rejected": [{"name": p.name, "reasons": r} for p, r in rejected],
    }


@app.post("/api/leads/{lead_id}/rematch")
async def rematch_lead(lead_id: int, request: Request, background: BackgroundTasks):
    """Matcha ett befintligt lead och mejla förslaget till ägaren."""
    _require_api_key(request)
    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")

    async with async_session() as session:
        lead = (await session.execute(
            select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        return await _rematch(session, lead, background)


@app.post("/api/leads/rematch-backlog")
async def rematch_backlog(request: Request, background: BackgroundTasks,
                          limit: int = 25, min_score: int = 0, send: bool = False):
    """Gå igenom leads som aldrig lämnats vidare och matcha dem.

    Kör den när du tecknat en ny partner: allt som legat och väntat på en köpare
    i just den regionen blir matchningsbart på en gång. Utan `send=true` visar
    den bara vad som skulle hända — börja alltid där.
    """
    _require_api_key(request)
    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")

    async with async_session() as session:
        assigned = select(LeadAssignment.lead_id).where(LeadAssignment.status == "sent")
        rows = (await session.execute(
            select(Lead)
            .where(Lead.id.notin_(assigned), Lead.lead_score >= min_score)
            .order_by(Lead.lead_score.desc().nullslast())
            .limit(max(1, min(limit, 200)))
        )).scalars().all()

        planned, acted = [], []
        for lead in rows:
            if send:
                acted.append(await _rematch(session, lead, background))
                continue
            matches, rejected = await _match_for_lead(session, lead)
            if matches:
                planned.append({
                    "lead_id": lead.id, "email": lead.email, "segment": lead.segment,
                    "county": lead.county, "score": lead.lead_score,
                    "would_match": [p.name for p in matches],
                    "auto_send": [p.name for p in vk_matching.best_per_group(matches)
                                  if p.auto_send],
                })

    if send:
        return {"mode": "skarpt", "count": len(acted), "leads": acted}
    return {
        "mode": "torrkörning",
        "granskade": len(rows),
        "matchningsbara": len(planned),
        "leads": planned,
        "kör_skarpt_med": "?send=true",
    }


def _directory_page(lead, entry: dict, token: str, redan: bool) -> str:
    """Bekräftelsesida för 'lägg till aktör ur katalogen'."""
    tackning = entry.get("counties") or entry.get("elareas") or "hela landet"
    kropp = (f'<p class="done">{entry["name"]} finns redan i registret.</p>' if redan else f"""
      <form method="post" action="/api/katalog/{token}/lagg-till">
        <button type="submit">Lägg till {entry['name']} och skicka leadet</button>
      </form>
      <p class="fine">Aktören läggs till med täckning <b>{tackning}</b> och får även
         framtida leads i samma område. Mejlet går till {entry['email']}.</p>""")
    return f"""<!DOCTYPE html>
<html lang="sv"><head><meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<meta name="robots" content="noindex, nofollow"/>
<title>Lägg till aktör | Vindkollen</title>
<style>
  body {{ font-family:-apple-system,Segoe UI,Arial,sans-serif; background:#030712;
         color:#e2e8f0; margin:0; padding:24px; }}
  .card {{ max-width:520px; margin:0 auto; background:#0f172a; border:1px solid #1e293b;
           border-radius:16px; padding:24px; }}
  h1 {{ font-size:20px; margin:0 0 4px; }}
  .sub {{ color:#94a3b8; font-size:14px; margin-bottom:18px; }}
  .note {{ background:#111827; border:1px solid #1e293b; border-radius:10px;
           padding:12px 14px; font-size:14px; color:#cbd5e1; margin-bottom:18px; }}
  button {{ width:100%; background:#0f766e; color:#fff; border:0; border-radius:10px;
            padding:15px; font-size:16px; font-weight:700; }}
  .fine {{ color:#64748b; font-size:12px; margin-top:12px; }}
  .done {{ color:#34d399; font-weight:600; }}
</style></head>
<body><div class="card">
  <h1>{entry['name']}</h1>
  <div class="sub">{vk_matching.PARTNER_KINDS.get(entry['kind'], {}).get('label', entry['kind'])}
      · {tackning}</div>
  <div class="note">{entry.get('note', '')}</div>
  <div class="sub">Leadet: {lead.name or lead.email} ·
      {vk_leads.segment_label(lead.segment)} · {lead.county or '—'} ·
      {lead.lead_tier or '?'}·{lead.lead_score or 0}</div>
  {kropp}
</div></body></html>"""


@app.get("/katalog/{token}", response_class=HTMLResponse)
async def directory_page(token: str):
    """Bekräftelsesida innan en katalogaktör läggs till. Utan sidoeffekter."""
    parsed = _parse_directory_token(token)
    if not parsed or not async_session:
        return HTMLResponse("<h1>Ogiltig länk</h1>", status_code=404)
    lead_id, entry = parsed
    if not entry.get("email"):
        return HTMLResponse("<h1>Aktören saknar adress i katalogen</h1>", status_code=404)
    name = entry["name"]

    async with async_session() as session:
        lead = (await session.execute(
            select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
        if not lead:
            return HTMLResponse("<h1>Leadet finns inte</h1>", status_code=404)
        redan = (await session.execute(
            select(Partner).where(Partner.name == name))).scalar_one_or_none() is not None

    return HTMLResponse(_directory_page(lead, entry, token, redan))


@app.post("/api/katalog/{token}/lagg-till", response_class=HTMLResponse)
async def directory_add(token: str, background: BackgroundTasks):
    """Lägg till aktören i registret och lämna över leadet.

    Aktören ärver katalogens täckning, så nästa lead i samma område matchar
    automatiskt utan att någon behöver göra något.
    """
    parsed = _parse_directory_token(token)
    if not parsed or not async_session:
        return HTMLResponse("<h1>Ogiltig länk</h1>", status_code=404)
    lead_id, entry = parsed
    if not entry.get("email"):
        return HTMLResponse("<h1>Aktören saknar adress i katalogen</h1>", status_code=404)
    name = entry["name"]

    async with async_session() as session:
        lead = (await session.execute(
            select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
        if not lead:
            return HTMLResponse("<h1>Leadet finns inte</h1>", status_code=404)

        partner = (await session.execute(
            select(Partner).where(Partner.name == name))).scalar_one_or_none()
        if not partner:
            partner = Partner(
                name=entry["name"], kind=entry["kind"],
                email=_normalise_email(entry["email"]),
                counties=entry.get("counties") or None,
                elareas=entry.get("elareas") or None,
                min_score=25, monthly_cap=10, auto_send=True,
                relationship="kall", notes=entry.get("note"),
            )
            session.add(partner)
            await session.flush()

        ok, info = _send_handover(lead, partner, "katalog")
        session.add(LeadAssignment(
            lead_id=lead.id, partner_id=partner.id,
            status="sent" if ok else "failed", approved_by="katalog",
            detail=None if ok else info[:500],
        ))
        await session.commit()
        namn, epost = partner.name, partner.email

    if not ok:
        return HTMLResponse(
            f"<h1>Utskicket misslyckades</h1><p>{info}</p>"
            f"<p>{namn} finns nu i registret — försök igen via samma länk.</p>",
            status_code=502)
    return HTMLResponse(
        f"<div style='font-family:sans-serif;padding:24px'>"
        f"<h1 style='color:#0f766e'>Tillagd och skickad</h1>"
        f"<p>{namn} ({epost}) finns nu i registret och har fått leadet. "
        f"Framtida leads i samma område matchas automatiskt.</p></div>")


@app.get("/api/katalog")
async def directory_list(request: Request):
    """Hela katalogen, för överblick."""
    _require_api_key(request)
    return {"count": len(vk_directory.load()), "aktorer": vk_directory.load()}


@app.get("/handover/{token}", response_class=HTMLResponse)
async def handover_page(token: str):
    """Bekräftelsesida för en överlämning.

    Medvetet utan sidoeffekter: mejlklienter och säkerhetsskannrar hämtar
    länkar i förväg, och en sådan hämtning får aldrig lämna ut personuppgifter.
    Utskicket sker på POST från knappen här.
    """
    parsed = _parse_handover_token(token)
    if not parsed or not async_session:
        return HTMLResponse("<h1>Ogiltig eller utgången länk</h1>", status_code=404)
    lead_id, partner_id = parsed

    async with async_session() as session:
        lead = (await session.execute(select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
        partner = (await session.execute(
            select(Partner).where(Partner.id == partner_id))).scalar_one_or_none()
        if not lead or not partner:
            return HTMLResponse("<h1>Leadet eller partnern finns inte</h1>", status_code=404)
        prior = (await session.execute(
            select(LeadAssignment).where(
                LeadAssignment.lead_id == lead_id,
                LeadAssignment.partner_id == partner_id,
                LeadAssignment.status == "sent",
            ).order_by(LeadAssignment.created_at.desc())
        )).scalars().first()

    return HTMLResponse(vk_matching.build_confirmation_page(
        lead, partner, token, prior.created_at if prior else None))


@app.post("/api/handover/{token}/send", response_class=HTMLResponse)
async def handover_send(token: str):
    """Genomför överlämningen: mejla partnern och logga tilldelningen."""
    parsed = _parse_handover_token(token)
    if not parsed or not async_session:
        return HTMLResponse("<h1>Ogiltig länk</h1>", status_code=404)
    lead_id, partner_id = parsed

    async with async_session() as session:
        lead = (await session.execute(select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
        partner = (await session.execute(
            select(Partner).where(Partner.id == partner_id))).scalar_one_or_none()
        if not lead or not partner:
            return HTMLResponse("<h1>Leadet eller partnern finns inte</h1>", status_code=404)

        prior = (await session.execute(
            select(LeadAssignment).where(
                LeadAssignment.lead_id == lead_id,
                LeadAssignment.partner_id == partner_id,
            ).order_by(LeadAssignment.created_at.desc())
        )).scalars().first()

        if prior and prior.status == "sent":
            return HTMLResponse(
                f"<h1>Redan skickat</h1><p>{lead.email} har redan lämnats till "
                f"{partner.name}.</p>", status_code=409)

        ok, info = _send_handover(lead, partner, "manual")
        if prior and prior.status == "pending":
            # Låg i karens bakom rådgivaren — du väljer att skicka nu ändå.
            # Uppdatera raden i stället för att lägga en dubblett.
            prior.status = "sent" if ok else "pending"
            prior.approved_by = "manual"
            prior.detail = None if ok else info[:500]
        else:
            session.add(LeadAssignment(
                lead_id=lead_id, partner_id=partner_id,
                status="sent" if ok else "failed",
                approved_by="manual", detail=None if ok else info[:500],
            ))
        await session.commit()

    if not ok:
        return HTMLResponse(
            f"<h1>Utskicket misslyckades</h1><p>{info}</p>"
            f"<p>Inget har lämnats ut. Försök igen via samma länk.</p>", status_code=502)
    return HTMLResponse(
        f"<div style='font-family:sans-serif;padding:24px'>"
        f"<h1 style='color:#059669'>Skickat</h1>"
        f"<p>{lead.email} är överlämnat till {partner.name} ({partner.email}).</p></div>")


@app.get("/api/assignments")
async def list_assignments(request: Request, limit: int = 200):
    """Vem har fått vad. Underlaget för fakturering och för att kunna svara på
    var en persons uppgifter tagit vägen."""
    _require_api_key(request)
    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")
    async with async_session() as session:
        rows = (await session.execute(
            select(LeadAssignment, Lead.email, Partner.name)
            .join(Lead, Lead.id == LeadAssignment.lead_id, isouter=True)
            .join(Partner, Partner.id == LeadAssignment.partner_id, isouter=True)
            .order_by(LeadAssignment.created_at.desc())
            .limit(max(1, min(limit, 2000)))
        )).all()
        return {"count": len(rows), "assignments": [
            {"id": a.id, "lead_id": a.lead_id, "lead_email": email,
             "partner_id": a.partner_id, "partner": pname, "status": a.status,
             "approved_by": a.approved_by, "detail": a.detail,
             "created_at": a.created_at.isoformat()}
            for a, email, pname in rows]}


# ---------------------------------------------------------------------------
# Editorial posts
# ---------------------------------------------------------------------------


@app.get("/api/posts")
async def get_posts():
    if not async_session:
        return []
    async with async_session() as session:
        result = await session.execute(select(Post).order_by(Post.published_at.desc()))
        posts = result.scalars().all()
        return [
            {
                "title": p.title,
                "content": p.content,
                "category": p.category,
                "date": p.published_at.strftime("%Y-%m-%d"),
            }
            for p in posts
        ]


@app.post("/api/posts")
async def create_post(req: PostIn, request: Request):
    api_key = request.headers.get("X-API-KEY")
    if api_key != os.environ.get("INTERNAL_API_KEY"):
        raise HTTPException(status_code=403)

    if not async_session:
        raise HTTPException(status_code=503, detail="Database not configured")

    async with async_session() as session:
        new_post = Post(title=req.title, content=req.content, category=req.category)
        session.add(new_post)
        await session.commit()
        return {"status": "ok"}


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/healthz", response_class=PlainTextResponse)
async def health():
    return "ok"


# ---------------------------------------------------------------------------

@app.get("/arrende-vindkraft-vs-solpark", response_class=HTMLResponse)
async def arrende_vindkraft_vs_solpark():
    return _serve_static_html("static/arrende-vindkraft-vs-solpark.html")

@app.get("/bygdepeng-vindkraft-regler-2026", response_class=HTMLResponse)
async def bygdepeng_vindkraft_regler_2026():
    return _serve_static_html("static/bygdepeng-vindkraft-regler-2026.html")

@app.get("/havsbaserad-vindkraft-ersattning", response_class=HTMLResponse)
async def havsbaserad_vindkraft_ersattning():
    return _serve_static_html("static/havsbaserad-vindkraft-ersattning.html")

@app.get("/kopa-andelar-i-vindkraft-2026", response_class=HTMLResponse)
async def kopa_andelar_i_vindkraft_2026():
    return _serve_static_html("static/kopa-andelar-i-vindkraft-2026.html")

@app.get("/kommunersattning-kalkylator", response_class=HTMLResponse)
async def kommunersattning_kalkylator():
    return _serve_static_html("static/kommunersattning-kalkylator.html")

@app.get("/guider/bygdepeng-och-kommunersattning-2026", response_class=HTMLResponse)
async def bygdepeng_och_kommunersattning_2026():
    return _serve_static_html("static/guider/bygdepeng-och-kommunersattning-2026.html")

@app.get("/ratt-till-inlosen-fastighet-vindkraft", response_class=HTMLResponse)
async def ratt_till_inlosen_fastighet_vindkraft():
    return _serve_static_html("static/ratt-till-inlosen-fastighet-vindkraft.html")


# Catch-all for HTML pages
# ---------------------------------------------------------------------------
# IMPORTANT: This MUST stay last — FastAPI matches routes in registration
# order. Originally added by AgentSim (commit c8c82d9) so daily-generated
# article pages dropped into static/ or content/ become reachable without
# needing an explicit route per file.



@app.get("/guider", response_class=RedirectResponse)
async def redirect_guider():
    return RedirectResponse(url="/", status_code=301)

@app.get("/guider/", response_class=RedirectResponse)
async def redirect_guider_slash():
    return RedirectResponse(url="/", status_code=301)

@app.get("/arrendera-ut-mark-for-vindkraftverk", response_class=HTMLResponse)
@app.get("/{path:path}", response_class=HTMLResponse)
async def serve_page(path: str):
    """Serve any .html file from static/ or content/ directories."""
    # Reject obviously invalid paths (e.g. ones containing ".." for traversal).
    if ".." in path or path.startswith("/"):
        raise HTTPException(status_code=404)

    candidates = [
        f"static/{path}",
        f"static/{path}.html",
        f"content/{path}",
        f"content/{path}.html",
    ]
    for filepath in candidates:
        if os.path.isfile(filepath):
            with open(filepath, encoding="utf-8") as f:
                return HTMLResponse(content=f.read())
    return HTMLResponse(
        content=(
            "<h1>404 – Sidan hittades inte</h1>"
            "<p><a href='/'>Tillbaka till startsidan</a></p>"
        ),
        status_code=404,
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
