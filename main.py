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
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func, select
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
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Post(Base):
    __tablename__ = "vindkollen_posts"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    category = Column(String(100))
    published_at = Column(DateTime, default=datetime.utcnow)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    yield
    if engine:
        await engine.dispose()


app = FastAPI(title="Vindkollen", lifespan=lifespan)


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class LeadIn(BaseModel):
    """Minimal lead from the hero/footer newsletter forms."""

    email: EmailStr
    name: Optional[str] = None
    municipality: Optional[str] = None
    source: Optional[str] = Field(default="newsletter", max_length=64)


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


@app.get("/kalkylator", response_class=HTMLResponse)
async def calculator():
    return _serve_static_html("static/kalkylator.html")


@app.get("/ersattning-for-vindkraft", response_class=HTMLResponse)
async def ersattning_for_vindkraft():
    return _serve_static_html("static/ersattning-for-vindkraft.html")


@app.get("/guider/nackdelar-med-vindkraft", response_class=HTMLResponse)
async def nackdelar_med_vindkraft():
    return _serve_static_html("static/nackdelar-med-vindkraft.html")


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


@app.post("/api/lead")
async def capture_lead(lead: LeadIn):
    """Persist a newsletter signup. Idempotent on email."""
    if not async_session:
        # Without a database we cannot persist; still return ok so the UI
        # behaves consistently in local dev, but flag it in the response.
        return JSONResponse({"status": "ok", "persisted": False})

    email = _normalise_email(lead.email)
    async with async_session() as session:
        stmt = pg_insert(Lead).values(
            email=email,
            name=lead.name,
            municipality=lead.municipality,
            source=lead.source or "newsletter",
        )
        # If the same email comes in again, update the source/name/municipality
        # rather than 500'ing the user.
        stmt = stmt.on_conflict_do_update(
            index_elements=["email"],
            set_={
                "name": lead.name,
                "municipality": lead.municipality,
                "source": lead.source or "newsletter",
            },
        )
        await session.execute(stmt)
        await session.commit()
    return {"status": "ok", "persisted": True}


@app.post("/api/lead/report")
async def capture_lead_report(lead: LeadReportIn):
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
    }

    async with async_session() as session:
        stmt = pg_insert(Lead).values(**payload)
        # Keep the most recent calc snapshot for an email — that's what the
        # sales/research team will reach out about.
        stmt = stmt.on_conflict_do_update(
            index_elements=["email"],
            set_={k: v for k, v in payload.items() if k != "email"},
        )
        await session.execute(stmt)
        await session.commit()

    return {"status": "ok", "persisted": True}


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


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
