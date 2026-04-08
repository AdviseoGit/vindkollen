import os
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

# Get Database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# For Railway/Postgres, ensure the driver is asyncpg
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# SQLAlchemy Async Setup
if DATABASE_URL:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
else:
    engine = None
    async_session = None

class Base(DeclarativeBase):
    pass

class Lead(Base):
    __tablename__ = "vindkollen_leads"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=True)
    municipality = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

@asynccontextmanager
async def lifespan(app: FastAPI):
    if engine:
        async with engine.begin() as conn:
            # Create table if not exists
            await conn.run_sync(Base.metadata.create_all)
    yield
    if engine:
        await engine.dispose()

app = FastAPI(title="Vindkollen", lifespan=lifespan)

# Lead model
class LeadIn(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    municipality: Optional[str] = None

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/kalkylator", response_class=HTMLResponse)
async def calculator():
    try:
        with open("static/kalkylator.html", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Kalkylator missing.</h1>", status_code=404)

@app.get("/robots.txt")
async def robots():
    from fastapi.responses import FileResponse
    return FileResponse("static/robots.txt", media_type="text/plain")

@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import FileResponse
    return FileResponse("static/favicon.svg")

@app.get("/", response_class=HTMLResponse)
async def index():
    try:
        with open("static/index.html", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Vindkollen MVP</h1><p>Static files missing.</p>", status_code=404)

@app.post("/api/lead")
async def capture_lead(lead: LeadIn):
    if not async_session:
        # Fallback if DB is not configured
        print(f"LEAD CAPTURED (No DB): {lead}")
        return JSONResponse(content={"status": "ok", "message": "Tack! Vi har sparat din intresseanmälan."})

    async with async_session() as session:
        try:
            # Simple upsert/ignore logic
            db_lead = Lead(
                email=lead.email,
                name=lead.name,
                municipality=lead.municipality
            )
            session.add(db_lead)
            await session.commit()
            return {"status": "ok", "message": "Tack! Vi hör av oss snart."}
        except Exception as e:
            await session.rollback()
            # If email already exists, just return ok
            return {"status": "ok", "message": "Du är redan registrerad. Vi hör av oss!"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
