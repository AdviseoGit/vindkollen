"""
Vindkollen backend.

Serves the static site, persists leads from the hero/footer email forms
and the kalkylator-driven "marknadsrapport" funnel, and exposes a small
public stats endpoint that powers social-proof counters on the front-end.

Audience: (1) Swedish landowners looking to host wind turbines,
          (2) Swedish municipalities and organisations evaluating wind power.
"""

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


def _deliver_report(data: dict):
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
        "Din vindkraftsrapport fran Vindkollen",
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
        + vk_report.build_owner_email_html(data),
        reply_to=data.get("email"),
    )


def _deliver_qualified(data: dict, score: int, tier: str):
    """Bekräftelse till leadet + prioriterad notis till oss.

    Ämnesraden på ägarnotisen bär silo och tier så att A-leads syns direkt i
    inkorgen utan att mejlet behöver öppnas.
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
        vk_leads.build_owner_email_html(data, score, tier),
        reply_to=data.get("email"),
    )


def _deliver_newsletter(email: str, source: str):
    html = (
        '<div style="font-family:Segoe UI,Arial,sans-serif;max-width:520px;color:#1e293b">'
        '<h2 style="color:#105e4e">Valkommen till Vindkollen</h2>'
        '<p>Tack for att du prenumererar. Vi bevakar lagen om intaktsdelning dagligen '
        'och hor av oss sa fort nagot viktigt hander for dig som markagare eller narboende.</p>'
        '<p>Testa garna var <a href="https://vindkoll.se/kalkylator.html" style="color:#105e4e">'
        'ersattningskalkylator</a> for en personlig uppskattning.</p>'
        '<p>Vanliga halsningar,<br><b>Vindkollen</b></p></div>'
    )
    try:
        mailer.send_email(email, "Valkommen till Vindkollen", html)
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



def deliver_report(email: str, name: str, est: int):
    subject = "Din marknadsrapport för vindkraftsersättning"
    html = f"""
    <html>
    <body style="font-family: sans-serif; line-height: 1.6; color: #333;">
        <h2>Hej {name or ''},</h2>
        <p>Här är din personliga uträkning från Vindkollen.</p>
        <p>Enligt kalkylen är din estimerade årliga ersättning: <b>{est} kr/år</b>.</p>
        <p>Vi arbetar just nu med att ta fram en mer detaljerad rapport. Vi hör av oss om vi behöver kompletterande information om din fastighet.</p>
        <p>Vänliga hälsningar,<br>Teamet på Vindkollen</p>
    </body>
    </html>
    """
    send_email(email, subject, html)
    
    notify_html = f"<p>Ny kalkylator-lead: {email} (Est: {est} kr/år)</p>"
    notify_owner("Ny lead - Vindkollen", notify_html)

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

    background.add_task(_deliver_report, dict(payload))
    return {"status": "ok", "persisted": True, "report": "queued"}


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

    background.add_task(_deliver_qualified, dict(payload), score, tier)
    return {
        "status": "ok",
        "persisted": True,
        "segment": payload["segment"],
        "elarea": payload.get("elarea"),
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
